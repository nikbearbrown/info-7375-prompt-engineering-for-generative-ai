"""GATE.md boundary cases 1-15, each asserting exactly the result predicted in GATE.md
(predictions written 2026-11-10, before any agent2 code). Real temp folders, a real symlink."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from tests import helpers, js2_helpers as h


class BoundaryCases(helpers.ContractTest):
    modules = ("agent2.policy", "agent2.providers")

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        self.out = self.parent / "out"
        self.out.mkdir()
        self.p = self.policy.Policy(self.out)

    def refused(self):
        return self.assertRaises(self.policy.PolicyRefused)

    # --- fetch ---------------------------------------------------------------------------
    def test_case_01_greenhouse_fetch_allowed(self):
        self.assertEqual(self.p.authorize("fetch", h.URLS["faire"]), "boards-api.greenhouse.io")

    def test_case_02_ashby_fetch_allowed(self):
        self.assertEqual(self.p.authorize("fetch", h.URLS["ashby_poshmark"]), "api.ashbyhq.com")

    def test_case_03_lever_refused_before_any_request(self):
        spy = h.SpyOpener()
        with self.refused():
            self.providers.http_get("https://api.lever.co/v0/postings/gopuff?mode=json", self.p, opener=spy)
        self.assertEqual(spy.calls, [], "no request may be made to a host off the list")
        for url in ("https://boards-api.greenhouse.io.evil.example/v1/boards/faire/jobs",
                    "https://boards-api.greenhouse.io@evil.example/v1/boards/faire/jobs"):
            with self.subTest(url=url), self.refused():
                self.p.authorize("fetch", url)

    def test_case_04_redirect_to_evil_refused_without_requesting_it(self):
        spy = h.SpyOpener(redirects={h.URLS["faire"]: "https://evil.example/steal"})
        with self.refused():
            self.providers.http_get(h.URLS["faire"], self.p, opener=spy)
        self.assertEqual(spy.calls, [("GET", h.URLS["faire"])], "evil.example must never be requested")

    # --- files ---------------------------------------------------------------------------
    def test_case_05_write_inside_runs_allowed(self):
        path = self.p.write_run_file("runs/r1/raw.json", b"{}")
        self.assertEqual(path, (self.out / "runs" / "r1" / "raw.json").resolve())
        self.assertEqual(path.read_bytes(), b"{}")

    def test_case_06_traversal_refused(self):
        with self.refused():
            self.p.write_run_file("../escape.txt", b"x")
        self.assertFalse((self.parent / "escape.txt").exists())

    def test_case_07_sibling_prefix_refused(self):
        (self.parent / "out-evil").mkdir()
        for target in (str(self.parent / "out-evil" / "x.txt"), "../out-evil/x.txt"):
            with self.subTest(target=target), self.refused():
                self.p.write_run_file(target, b"x")
        self.assertFalse((self.parent / "out-evil" / "x.txt").exists())

    def test_case_08_outside_pointing_symlink_refused(self):
        outside = self.parent / "outside"
        outside.mkdir()
        try:
            os.symlink(outside, self.out / "link", target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"SKIPPED case 8: this OS refused to create a symlink ({exc.__class__.__name__}: {exc})")
        with self.refused():
            self.p.write_run_file("link/x.txt", b"x")
        self.assertFalse((outside / "x.txt").exists())

    def test_case_09_read_file_inside_allowed(self):
        state = self.out / "state" / "seen_ids.json"
        state.parent.mkdir()
        state.write_bytes(b'{"seen_ids": []}')
        self.assertEqual(self.p.authorize("read_file", "state/seen_ids.json"), state.resolve())
        self.assertEqual(self.p.read_file("state/seen_ids.json"), b'{"seen_ids": []}')

    def test_case_10_delete_not_in_vocabulary(self):
        with self.refused():
            self.p.authorize("delete", "state/seen_ids.json")
        with self.refused():
            self.p.authorize("delete", "state/seen_ids.json", approved=True)

    # --- approval ------------------------------------------------------------------------
    def test_case_11_reset_state_with_true_allowed(self):
        self.p.update_state("state/seen_ids.json", ["greenhouse:faire:1"])
        self.p.reset_state("state/seen_ids.json", ["greenhouse:faire:2"], approved=True)
        self.assertEqual(self.p.read_state("state/seen_ids.json")["seen_ids"], ["greenhouse:faire:2"])

    def test_case_12_reset_state_with_yes_refused(self):
        self.p.update_state("state/seen_ids.json", ["greenhouse:faire:1"])
        for value in ("yes", 1, None, False):
            with self.subTest(approved=value), self.refused():
                self.p.reset_state("state/seen_ids.json", [], approved=value)
        with self.refused():
            self.p.reset_state("state/seen_ids.json", [])
        self.assertEqual(self.p.read_state("state/seen_ids.json")["seen_ids"], ["greenhouse:faire:1"])

    def test_case_13_approval_cannot_override_containment(self):
        (self.parent / "outside").mkdir()
        with self.refused():
            self.p.reset_state("../outside/seen_ids.json", [], approved=True)
        self.assertFalse((self.parent / "outside" / "seen_ids.json").exists())

    def test_case_14_post_to_allowed_host_refused(self):
        with self.refused():
            self.p.authorize("fetch", h.URLS["faire"], method="POST")
        spy = h.SpyOpener()
        with self.refused():
            self.providers.http_get(h.URLS["faire"], self.p, opener=spy, method="POST")
        self.assertEqual(spy.calls, [])

    def test_case_15_update_that_would_drop_an_id_refused(self):
        with self.refused():
            self.p.authorize("update_state", "state/seen_ids.json",
                             old_ids={"greenhouse:faire:1", "greenhouse:faire:2"},
                             new_ids={"greenhouse:faire:2"})
        self.p.update_state("state/seen_ids.json", ["greenhouse:faire:1"])
        self.p.update_state("state/seen_ids.json", ["greenhouse:faire:2"])
        self.assertEqual(self.p.read_state("state/seen_ids.json")["seen_ids"],
                         ["greenhouse:faire:1", "greenhouse:faire:2"], "update_state merges, never drops")


class PolicyExtras(helpers.ContractTest):
    modules = ("agent2.policy",)

    def test_allow_list_is_exactly_the_two_gate_hosts(self):
        self.assertEqual(set(self.policy.ALLOWED_HOSTS), {"boards-api.greenhouse.io", "api.ashbyhq.com"})

    def test_vocabulary_is_exactly_the_gate_operations(self):
        self.assertEqual(set(self.policy.OPERATIONS),
                         {"fetch", "read_file", "write_run_file", "update_state", "reset_state"})

    def test_state_file_is_json_with_sorted_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.policy.Policy(tmp)
            p.update_state("state/seen_ids.json", ["b", "a"])
            data = json.loads((Path(tmp) / "state" / "seen_ids.json").read_text(encoding="utf-8"))
            self.assertEqual(data["seen_ids"], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
