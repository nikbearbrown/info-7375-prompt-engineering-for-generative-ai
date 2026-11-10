"""Boundary tests for the permission policy (GATE.md section 5).

Each test's number matches a row of POLICY.md, where the predicted outcome was
written down before the tests were run. The first line of each docstring is
that prediction.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from agent.policy import Policy

GH = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"


class NetworkBoundary(unittest.TestCase):
    def setUp(self):
        self.root = Path(os.path.realpath(tempfile.mkdtemp(prefix="js2-policy-")))
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "jobs").mkdir()
        self.policy = Policy(self.root)

    def fetch(self, url, method="GET"):
        return self.policy.check_fetch(method, url)

    def test_B01_allowed_greenhouse_board(self):
        """allow: exact host, allowed path, GET, HTTPS."""
        self.assertEqual(self.fetch(GH).outcome, "allow")

    def test_B02_allowed_lever_board(self):
        """allow."""
        self.assertEqual(self.fetch("https://api.lever.co/v0/postings/palantir?mode=json").outcome, "allow")

    def test_B03_host_off_the_list_with_allowed_name_as_prefix(self):
        """refuse: api.lever.co.evil.example is a different host."""
        self.assertEqual(self.fetch("https://api.lever.co.evil.example/v0/postings/palantir").outcome, "refuse")

    def test_B04_subdomain_of_an_allowed_host(self):
        """refuse: evil.api.lever.co is not api.lever.co."""
        self.assertEqual(self.fetch("https://evil.api.lever.co/v0/postings/palantir").outcome, "refuse")

    def test_B05_allowed_name_hidden_in_the_query(self):
        """refuse: the host is evil.example."""
        self.assertEqual(self.fetch("https://evil.example/v0/postings/palantir?u=api.lever.co").outcome, "refuse")

    def test_B06_plain_http(self):
        """refuse: HTTPS only."""
        self.assertEqual(self.fetch("http://api.ashbyhq.com/posting-api/job-board/linear").outcome, "refuse")

    def test_B07_credentials_in_the_url(self):
        """refuse: no user name or password."""
        url = "https://user:secret@api.ashbyhq.com/posting-api/job-board/linear"
        self.assertEqual(self.fetch(url).outcome, "refuse")

    def test_B08_post_to_an_allowed_board(self):
        """refuse: GET only; a POST is how an application would be sent."""
        self.assertEqual(self.fetch("https://api.lever.co/v0/postings/palantir", method="POST").outcome, "refuse")

    def test_B09_apply_path_on_an_allowed_host(self):
        """refuse: the path is not a board listing."""
        url = "https://api.lever.co/v0/postings/palantir/0f0e-not-real/apply"
        self.assertEqual(self.fetch(url).outcome, "refuse")

    def test_B10_mailto_link(self):
        """refuse: the agent never sends email."""
        self.assertEqual(self.fetch("mailto:recruiter@example.com").outcome, "refuse")

    def test_B11_dot_dot_in_the_url_path(self):
        """refuse: the board name must be letters, digits and hyphens."""
        self.assertEqual(self.fetch("https://boards-api.greenhouse.io/v1/boards/../jobs").outcome, "refuse")
        self.assertEqual(self.fetch("https://boards-api.greenhouse.io/v1/boards/%2e%2e/jobs").outcome, "refuse")

    def test_B12_non_default_port(self):
        """refuse: port 443 only."""
        self.assertEqual(self.fetch("https://api.ashbyhq.com:8443/posting-api/job-board/linear").outcome, "refuse")

    def test_B12b_upper_case_host_is_the_same_host(self):
        """allow: host names are not case-sensitive."""
        self.assertEqual(self.fetch("https://API.LEVER.CO/v0/postings/palantir?mode=json").outcome, "allow")

    def test_B12c_unknown_query_parameter(self):
        """refuse: only the query parameters each board needs."""
        self.assertEqual(self.fetch("https://api.lever.co/v0/postings/palantir?mode=json&token=x").outcome,
                         "refuse")


class FileBoundary(unittest.TestCase):
    def setUp(self):
        base = Path(os.path.realpath(tempfile.mkdtemp(prefix="js2-policy-")))
        self.addCleanup(shutil.rmtree, base, True)
        self.root = base / "js2"
        self.outside = base / "outside"
        for folder in ("jobs/raw", "jobs/runs", "jobs/state", "jobs-evil", "config", "persona"):
            (self.root / folder).mkdir(parents=True)
        self.outside.mkdir()
        (self.outside / "secret.txt").write_text("not for the agent", encoding="utf-8")
        (self.root / "config" / "boards.json").write_text("{}", encoding="utf-8")
        (self.root / "persona" / "p.json").write_text("{}", encoding="utf-8")
        (self.root / "jobs" / "raw" / "old.body.gz").write_bytes(b"evidence")
        (self.root / "jobs" / "state" / "greenhouse-anthropic.json").write_text(
            json.dumps({"seen_ids": ["1", "2"]}), encoding="utf-8")
        os.symlink(self.outside, self.root / "jobs" / "link-out")
        os.symlink(self.root / "persona" / "p.json", self.root / "jobs" / "raw" / "sneaky.json")
        self.policy = Policy(self.root, approvals=["greenhouse/anthropic"])
        self.plain = Policy(self.root)

    def test_B13_new_file_inside_jobs(self):
        """allow."""
        self.assertEqual(self.plain.check_write(self.root / "jobs" / "raw" / "new.body.gz").outcome, "allow")

    def test_B14_dot_dot_escapes_jobs(self):
        """refuse: jobs/../config/boards.json resolves to config/."""
        path = Path(str(self.root / "jobs") + "/../config/boards.json")
        self.assertEqual(self.plain.check_write(path).outcome, "refuse")
        # Added 2026-11-10 after test_w3 failed: boards.json exists, so "written once" refused it
        # and the `..` check was never needed. A file that does not exist yet needs the `..` check.
        new = Path(str(self.root / "jobs") + "/../config/new.json")
        decision = self.plain.check_write(new)
        self.assertEqual(decision.outcome, "refuse")
        self.assertIn("inside jobs/ only", decision.reason)

    def test_B15_prefix_trick_jobs_evil(self):
        """refuse: jobs-evil/ starts with "jobs" but is not inside jobs/."""
        self.assertEqual(self.plain.check_write(self.root / "jobs-evil" / "x.json").outcome, "refuse")

    def test_B16_folder_symlink_inside_jobs_pointing_outside(self):
        """refuse: jobs/link-out/ is really ../outside/."""
        self.assertEqual(self.plain.check_write(self.root / "jobs" / "link-out" / "x.json").outcome, "refuse")

    def test_B17_file_symlink_inside_jobs_pointing_at_the_persona(self):
        """refuse: jobs/raw/sneaky.json is really persona/p.json."""
        self.assertEqual(self.plain.check_write(self.root / "jobs" / "raw" / "sneaky.json").outcome, "refuse")

    def test_B18_read_the_persona(self):
        """allow: a read inside persona/."""
        self.assertEqual(self.plain.check_read(self.root / "persona" / "p.json").outcome, "allow")

    def test_B19_write_the_persona(self):
        """refuse: the same file, but a write."""
        self.assertEqual(self.plain.check_write(self.root / "persona" / "p.json").outcome, "refuse")

    def test_B20_read_and_write_config(self):
        """read allow, write refuse: config/ is read-only to the agent."""
        self.assertEqual(self.plain.check_read(self.root / "config" / "boards.json").outcome, "allow")
        self.assertEqual(self.plain.check_write(self.root / "config" / "boards.json").outcome, "refuse")

    def test_B21_read_outside_the_folder(self):
        """refuse: reads stay inside this folder."""
        self.assertEqual(self.plain.check_read(self.outside / "secret.txt").outcome, "refuse")
        self.assertEqual(self.plain.check_read(self.root / "jobs" / "link-out" / "secret.txt").outcome, "refuse")
        self.assertEqual(self.plain.check_read(Path.home() / ".ssh" / "id_rsa").outcome, "refuse")

    def test_B22_overwrite_saved_evidence(self):
        """refuse: raw responses are written once."""
        self.assertEqual(self.plain.check_write(self.root / "jobs" / "raw" / "old.body.gz").outcome, "refuse")

    def test_B23_state_update_that_only_adds_ids(self):
        """allow."""
        path = self.root / "jobs" / "state" / "greenhouse-anthropic.json"
        self.assertEqual(self.plain.check_write(path, kind="state", board="greenhouse/anthropic",
                                                drops_ids=False).outcome, "allow")

    def test_B24_state_reset_without_approval(self):
        """needs_approval: dropping seen ids is a reset."""
        path = self.root / "jobs" / "state" / "greenhouse-anthropic.json"
        decision = self.plain.check_write(path, kind="state", board="greenhouse/anthropic", drops_ids=True)
        self.assertEqual(decision.outcome, "needs_approval")
        self.assertFalse(decision.allowed)

    def test_B25_state_reset_with_my_approval_for_that_board(self):
        """allow: I typed --approve-state-reset greenhouse/anthropic."""
        path = self.root / "jobs" / "state" / "greenhouse-anthropic.json"
        self.assertEqual(self.policy.check_write(path, kind="state", board="greenhouse/anthropic",
                                                 drops_ids=True).outcome, "allow")

    def test_B26_approval_for_a_different_board(self):
        """needs_approval: an approval covers only the board it names."""
        path = self.root / "jobs" / "state" / "lever-palantir.json"
        self.assertEqual(self.policy.check_write(path, kind="state", board="lever/palantir",
                                                 drops_ids=True).outcome, "needs_approval")

    def test_B27_append_only_to_a_file_this_run_created(self):
        """allow for the run's own trace; refuse for any other file."""
        trace = self.root / "jobs" / "runs" / "r.trace.jsonl"
        self.assertEqual(self.plain.check_write(trace).outcome, "allow")
        self.plain.note_created(trace)
        self.assertEqual(self.plain.check_write(trace, kind="append").outcome, "allow")
        other = self.root / "jobs" / "raw" / "old.body.gz"
        self.assertEqual(self.plain.check_write(other, kind="append").outcome, "refuse")

    def test_B28_state_write_outside_jobs_state(self):
        """refuse: state files live in jobs/state/ only."""
        self.assertEqual(self.plain.check_write(self.root / "jobs" / "raw" / "x.json", kind="state",
                                                board="greenhouse/anthropic").outcome, "refuse")


class ToolsGoThroughThePolicy(unittest.TestCase):
    """The tools refuse before acting: nothing is written and nothing is sent."""

    def setUp(self):
        base = Path(os.path.realpath(tempfile.mkdtemp(prefix="js2-policy-")))
        self.addCleanup(shutil.rmtree, base, True)
        self.root = base / "js2"
        (self.root / "jobs" / "state").mkdir(parents=True)
        (self.root / "jobs-evil").mkdir()
        self.policy = Policy(self.root)

    def test_refused_write_writes_nothing(self):
        from agent.tools import Refused, write_new
        with self.assertRaises(Refused):
            write_new(self.policy, self.root / "jobs-evil" / "x.json", b"data")
        self.assertEqual(list((self.root / "jobs-evil").iterdir()), [])

    def test_refused_fetch_sends_nothing(self):
        from agent.tools import Refused, fetch
        sent = []
        with self.assertRaises(Refused):
            fetch(self.policy, "https://evil.example/v0/postings/palantir",
                  lambda url, timeout, max_bytes: sent.append(url), timeout=5, max_bytes=10)
        self.assertEqual(sent, [])

    def test_state_reset_through_the_tool_needs_approval(self):
        from agent.tools import Refused, write_state
        path = self.root / "jobs" / "state" / "greenhouse-anthropic.json"
        path.write_text(json.dumps({"seen_ids": ["1", "2"]}), encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaises(Refused) as caught:
            write_state(self.policy, path, {"seen_ids": ["1"]}, "greenhouse/anthropic")
        self.assertEqual(caught.exception.decision.outcome, "needs_approval")
        self.assertEqual(path.read_bytes(), before)
        write_state(self.policy, path, {"seen_ids": ["1", "2", "3"]}, "greenhouse/anthropic")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["seen_ids"], ["1", "2", "3"])


if __name__ == "__main__":
    unittest.main()
