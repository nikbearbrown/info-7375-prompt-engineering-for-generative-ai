"""Boundary tests B1-B21. The expected decision in each test is the one predicted in POLICY.md
BEFORE agent/policy.py existed (frozen copy: evidence/POLICY-predictions-2026-11-09.md)."""
import os
import re
import tempfile
import unittest
from unittest import mock

from agent import policy, store, transport
from tests.helpers import ROOT, TempBase, rd, wr

GH = "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true"


class Network(unittest.TestCase):
    def dec(self, method, url, headers=None):
        return policy.check_request(method, url, headers)["decision"]

    def test_B01_allowed_host_get(self):
        self.assertEqual(self.dec("GET", GH), policy.ALLOW)

    def test_B02_host_off_allow_list(self):
        self.assertEqual(self.dec("GET", "https://www.linkedin.com/jobs/view/1"), policy.DENY)

    def test_B03_suffix_trick_host(self):
        self.assertEqual(self.dec("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs"), policy.DENY)
        self.assertEqual(self.dec("GET", "https://evilboards-api.greenhouse.io/v1/boards/x/jobs"), policy.DENY)

    def test_B04_userinfo_trick(self):
        self.assertEqual(self.dec("GET", "https://boards-api.greenhouse.io@evil.example/v1/boards/x/jobs"), policy.DENY)

    def test_B05_plain_http(self):
        self.assertEqual(self.dec("GET", "http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs"), policy.DENY)

    def test_B06_non_443_port(self):
        self.assertEqual(self.dec("GET", "https://api.ashbyhq.com:8443/posting-api/job-board/linear"), policy.DENY)
        self.assertEqual(self.dec("GET", "https://api.ashbyhq.com:443/posting-api/job-board/linear"), policy.ALLOW)

    def test_B07_post_is_denied(self):
        for m in ("POST", "PUT", "DELETE", "PATCH"):
            self.assertEqual(self.dec(m, "https://api.lever.co/v0/postings/spotify/abc/apply"), policy.DENY, m)

    def test_B08_auth_header_denied(self):
        self.assertEqual(self.dec("GET", GH, {"Authorization": "Bearer x"}), policy.DENY)
        self.assertEqual(self.dec("GET", GH, {"cookie": "s=1"}), policy.DENY)

    def test_B09_redirect_refused(self):
        handler = transport._NoRedirect()
        with self.assertRaises(transport.Redirected):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example/")
        # and transport.get turns it into a policy refusal, never a followed request
        with mock.patch("urllib.request.OpenerDirector.open",
                        side_effect=transport.Redirected("redirect 302 to 'https://evil.example/' refused")):
            with self.assertRaises(policy.PolicyDenied) as cm:
                transport.get(GH, 5, 1000)
        self.assertEqual(cm.exception.decision["decision"], policy.DENY)

    def test_transport_refuses_before_any_io(self):
        with mock.patch("urllib.request.OpenerDirector.open") as op:
            with self.assertRaises(policy.PolicyDenied):
                transport.get("https://www.linkedin.com/jobs", 5, 1000)
            op.assert_not_called()


class Files(unittest.TestCase):
    def setUp(self):
        self.tb = TempBase().__enter__()
        self.pol = policy.Policy(self.tb.dir, self.tb.path("runs"))

    def tearDown(self):
        self.tb.__exit__()

    def test_B10_read_inside_folder(self):
        self.assertEqual(self.pol.check_read("config/watchlist.json")["decision"], policy.ALLOW)

    def test_B11_write_config_needs_approval(self):
        before = rd(self.tb.path("config", "watchlist.json"))
        d = self.pol.check_write("config/watchlist.json")
        self.assertEqual(d["decision"], policy.ASK)
        self.assertFalse(d["granted"])
        st = store.Store(self.pol)
        with self.assertRaises(policy.PolicyDenied):
            st.write_new(self.tb.path("config", "watchlist.json"), "{}")
        self.assertEqual(rd(self.tb.path("config", "watchlist.json")), before)  # not written

    def test_B12_write_config_approved(self):
        asked = []
        pol = policy.Policy(self.tb.dir, self.tb.path("runs"), approver=lambda p, r: asked.append(p) or True)
        d = pol.check_write("config/budgets.json")
        self.assertEqual(d["decision"], policy.ALLOW)
        self.assertTrue(d["granted"])
        self.assertEqual(asked, ["config/budgets.json"])

    def test_B13_new_file_in_runs(self):
        self.assertEqual(self.pol.check_write("runs/r1/raw/greenhouse-klaviyo-a1.json")["decision"], policy.ALLOW)

    def test_B14_dotdot_escape(self):
        self.assertEqual(self.pol.check_write("runs/../GATE.md")["decision"], policy.DENY)
        self.assertEqual(self.pol.check_write("runs/a/../../x.json")["decision"], policy.DENY)

    def test_B15_prefix_trick_sibling(self):
        os.makedirs(self.tb.path("runs-evil"))
        self.assertEqual(self.pol.check_write("runs-evil/x.json")["decision"], policy.DENY)

    def test_B16_symlink_escape(self):
        outside = os.path.realpath(tempfile.mkdtemp(prefix="js2-outside-"))
        try:
            os.symlink(outside, self.tb.path("runs", "link"))
            self.assertEqual(self.pol.check_write("runs/link/x.json")["decision"], policy.DENY)
            st = store.Store(self.pol)
            with self.assertRaises(policy.PolicyDenied):
                st.write_new(self.tb.path("runs", "link", "x.json"), "x")
            self.assertEqual(os.listdir(outside), [])  # nothing escaped
        finally:
            os.rmdir(outside)

    def test_B16b_symlink_file_planted_at_final_path(self):
        outside = os.path.realpath(tempfile.mkdtemp(prefix="js2-outside-"))
        try:
            target = os.path.join(outside, "victim.txt")
            os.symlink(target, self.tb.path("runs", "evil.json"))
            self.assertEqual(self.pol.check_write("runs/evil.json")["decision"], policy.DENY)
            self.assertFalse(os.path.exists(target))
        finally:
            os.rmdir(outside)

    def test_B17_overwrite_raw_needs_approval(self):
        os.makedirs(self.tb.path("runs", "r1", "raw"))
        p = self.tb.path("runs", "r1", "raw", "gh.json")
        wr(p, "original")
        d = self.pol.check_write(p)
        self.assertEqual(d["decision"], policy.ASK)
        with self.assertRaises(policy.PolicyDenied):
            store.Store(self.pol).write_new(p, "replaced")
        self.assertEqual(rd(p), "original")

    def test_B18_state_file_overwrite_allowed(self):
        os.makedirs(self.tb.path("runs", "state"))
        p = self.tb.path("runs", "state", "greenhouse-klaviyo.state.json")
        wr(p, "{}")
        self.assertEqual(self.pol.check_write(p)["decision"], policy.ALLOW)
        store.Store(self.pol).write_state(p, {"seen_ids": [1]})
        self.assertIn('"seen_ids"', rd(p))

    def test_B19_absolute_outside(self):
        self.assertEqual(self.pol.check_write("/tmp/x.json")["decision"], policy.DENY)

    def test_B20_read_outside_folder(self):
        self.assertEqual(self.pol.check_read(os.path.expanduser("~/.ssh/id_rsa"))["decision"], policy.DENY)
        self.assertEqual(self.pol.check_read("../../../../etc/passwd")["decision"], policy.DENY)

    def test_B21_forbidden_actions_never_allowed(self):
        for a in ("apply", "email", "message", "login", "APPLY"):
            self.assertEqual(policy.check_action(a, approver=lambda *x: True)["decision"], policy.DENY, a)


class OnlyTwoModulesTouchTheWorld(unittest.TestCase):
    def test_no_other_module_opens_network_or_writes(self):
        agent_dir = os.path.join(ROOT, "agent")
        net = re.compile(r"^\s*(import|from)\s+(urllib\.request|socket|http\.client|requests)\b", re.M)
        write = re.compile(r"open\([^)]*['\"](w|a|x|wb|ab|xb|r\+|w\+)['\"]")
        for name in sorted(os.listdir(agent_dir)):
            if not name.endswith(".py"):
                continue
            src = rd(os.path.join(agent_dir, name))
            if name != "transport.py":
                self.assertIsNone(net.search(src), f"{name} imports a network module")
            if name != "store.py":
                self.assertIsNone(write.search(src), f"{name} opens a file for writing")
                self.assertNotIn("os.replace(", src, f"{name} replaces files")


if __name__ == "__main__":
    unittest.main()
