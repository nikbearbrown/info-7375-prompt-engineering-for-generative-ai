"""The permission policy, enforced in code (GATE.md 'Permission policy').

Cases N1-N7 and F1-F14 are the boundary cases the student predicted before any of
this code existed (policy/BOUNDARY-PREDICTIONS.md, commit f871ccb). N5, the redirect,
needs the loop, so it lives in tests/test_loop.py. Cases X1-X11 were added by Claude
Code; their expected results are written here, before the implementation.

Every file below is a stand-in inside a temporary folder. Every approval is a
SIMULATED approval fixture."""

import os
import unittest

from jobwatch.errors import PolicyDenied
from jobwatch.files import Files
from jobwatch.policy import Approval, Policy
from tests.fakes import ANTHROPIC_URL, BAD_SLUG_URL, DATABRICKS_URL, LINEAR_URL, Project

APPROVED = {ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL, BAD_SLUG_URL}
GOOD_APPROVAL = Approval("R2", "state/state.json")  # simulated fixture


class Tree(unittest.TestCase):
    """runs/R1 is an earlier run, runs/R2 the current one; runs/R2/link points inside,
    runs/R2/out points outside the project; runs-evil sits next to runs."""

    def setUp(self):
        self.project = Project()
        self.addCleanup(self.project.cleanup)
        root, base = self.project.root, self.project.base
        (root / "state").mkdir()
        (root / "state" / "state.json").write_text("{}\n", encoding="utf-8")
        (root / "runs" / "R1").mkdir(parents=True)
        (root / "runs" / "R1" / "trace.json").write_text("{}\n", encoding="utf-8")
        (root / "runs" / "R2" / "sub").mkdir(parents=True)
        (base / "outside").mkdir()
        (base / "outside" / "resume.pdf").write_bytes(b"stand-in, not a real resume")
        os.symlink(root / "runs" / "R2" / "sub", root / "runs" / "R2" / "link")
        os.symlink(base / "outside", root / "runs" / "R2" / "out")
        (root / "runs-evil" / "R2").mkdir(parents=True)
        self.root = root

    def policy(self, approval=None):
        return Policy(self.root, "R2", APPROVED, approval)

    def refused(self, rule, call):
        with self.assertRaises(PolicyDenied) as caught:
            call()
        self.assertEqual(caught.exception.rule, rule, str(caught.exception))
        return caught.exception


class RequestCasesTest(Tree):
    def test_N1_the_exact_configured_https_get_is_allowed(self):
        self.assertIsNone(self.policy().check_request("GET", ANTHROPIC_URL))

    def test_N2_a_post_to_the_same_address_is_refused(self):
        self.refused("method", lambda: self.policy().check_request("POST", ANTHROPIC_URL))

    def test_N3_a_host_off_the_allow_list_is_refused(self):
        self.refused("host", lambda: self.policy().check_request("GET", "https://example.com/jobs"))

    def test_N4_plain_http_is_refused(self):
        url = "http://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
        self.refused("scheme", lambda: self.policy().check_request("GET", url))

    def test_N6_a_link_found_inside_a_posting_is_refused(self):
        url = "https://jobs.ashbyhq.com/linear/d3bc1ced-3ce4-4086-a050-555055dbb1ff"
        self.refused("host", lambda: self.policy().check_request("GET", url))

    def test_N7_an_unconfigured_board_on_an_allowed_host_is_refused(self):
        url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
        self.refused("endpoint", lambda: self.policy().check_request("GET", url))

    # Added by Claude Code.
    def test_X9_the_right_board_without_its_query_is_refused(self):
        url = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"
        self.refused("endpoint", lambda: self.policy().check_request("GET", url))

    def test_X10_an_allowed_name_before_an_at_sign_is_not_the_host(self):
        url = "https://boards-api.greenhouse.io@example.com/v1/boards/anthropic/jobs?content=true"
        self.refused("host", lambda: self.policy().check_request("GET", url))

    def test_X11_an_allowed_name_as_a_prefix_of_another_host_is_refused(self):
        url = "https://boards-api.greenhouse.io.example.com/v1/boards/anthropic/jobs?content=true"
        self.refused("host", lambda: self.policy().check_request("GET", url))


class FileCasesTest(Tree):
    def test_F1_reading_the_persona_is_allowed(self):
        self.assertEqual(self.policy().check_file("read", "persona/alex_morgan.json"),
                         self.root / "persona" / "alex_morgan.json")

    def test_F2_reading_the_state_is_allowed(self):
        self.assertEqual(self.policy().check_file("read", "state/state.json"),
                         self.root / "state" / "state.json")

    def test_F3_reading_a_file_outside_the_project_is_refused(self):
        outside = str(self.project.base / "outside" / "resume.pdf")
        self.refused("outside-project", lambda: self.policy().check_file("read", outside))

    def test_F4_writing_in_the_current_run_folder_needs_no_approval(self):
        self.assertEqual(self.policy().check_file("write", "runs/R2/trace.json"),
                         self.root / "runs" / "R2" / "trace.json")

    def test_F5_writing_in_an_earlier_run_folder_is_refused(self):
        self.refused("not-writable", lambda: self.policy().check_file("write", "runs/R1/trace.json"))

    def test_F6_a_path_through_dot_dot_is_refused(self):
        self.refused("parent-traversal",
                     lambda: self.policy().check_file("write", "runs/R2/../R1/trace.json"))

    def test_F7_a_look_alike_folder_next_to_runs_is_refused(self):
        self.refused("not-writable", lambda: self.policy().check_file("write", "runs-evil/R2/trace.json"))

    def test_F8_a_symlink_that_leads_outside_is_refused(self):
        self.refused("symlink", lambda: self.policy().check_file("write", "runs/R2/out/trace.json"))

    def test_F9_a_symlink_is_refused_even_when_it_points_inside(self):
        self.refused("symlink", lambda: self.policy().check_file("write", "runs/R2/link/trace.json"))

    def test_F10_a_state_write_without_approval_is_refused(self):
        self.refused("approval", lambda: self.policy(None).check_file("write", "state/state.json"))

    def test_F11_an_approval_for_another_run_is_refused(self):
        wrong_run = Approval("R1", "state/state.json")
        self.refused("approval", lambda: self.policy(wrong_run).check_file("write", "state/state.json"))

    def test_F12_an_approval_that_names_another_file_is_refused(self):
        wrong_file = Approval("R2", "state/other.json")
        self.refused("approval", lambda: self.policy(wrong_file).check_file("write", "state/state.json"))

    def test_F13_the_matching_approval_allows_the_state_write(self):
        self.assertEqual(self.policy(GOOD_APPROVAL).check_file("write", "state/state.json"),
                         self.root / "state" / "state.json")

    def test_F14_the_matching_approval_covers_the_temporary_state_file(self):
        self.assertEqual(self.policy(GOOD_APPROVAL).check_file("write", "state/.state.json.tmp"),
                         self.root / "state" / ".state.json.tmp")

    # Added by Claude Code.
    def test_X1_dot_dot_is_refused_even_when_it_lands_in_the_current_run(self):
        self.refused("parent-traversal",
                     lambda: self.policy().check_file("write", "runs/R2/sub/../trace.json"))

    def test_X2_reading_a_file_does_not_allow_writing_it(self):
        policy = self.policy(GOOD_APPROVAL)
        policy.check_file("read", "persona/alex_morgan.json")
        self.refused("not-writable", lambda: policy.check_file("write", "persona/alex_morgan.json"))

    def test_X3_an_operation_outside_read_and_write_is_refused(self):
        self.refused("operation", lambda: self.policy(GOOD_APPROVAL).check_file("delete", "runs/R2/trace.json"))

    def test_X4_a_bare_true_is_not_an_approval(self):
        self.refused("approval", lambda: self.policy(True).check_file("write", "state/state.json"))

    def test_X5_the_state_approval_does_not_cover_other_files_in_state(self):
        self.refused("not-writable", lambda: self.policy(GOOD_APPROVAL).check_file("write", "state/notes.txt"))

    def test_X6_reading_an_earlier_runs_saved_evidence_is_allowed(self):
        self.assertEqual(self.policy().check_file("read", "runs/R1/trace.json"),
                         self.root / "runs" / "R1" / "trace.json")

    def test_X7_creating_the_current_run_folder_is_allowed(self):
        self.assertEqual(self.policy().check_file("write", "runs/R2"), self.root / "runs" / "R2")

    def test_X8_a_state_file_that_is_a_symlink_cannot_be_read(self):
        (self.root / "state" / "state.json").unlink()
        os.symlink(self.project.base / "outside" / "resume.pdf", self.root / "state" / "state.json")
        self.refused("symlink", lambda: self.policy().check_file("read", "state/state.json"))

    def test_X12_reading_an_unlisted_file_inside_the_project_is_refused(self):
        (self.root / "notes.txt").write_text("private", encoding="utf-8")
        self.refused("not-readable", lambda: self.policy().check_file("read", "notes.txt"))

    def test_X13_a_look_alike_of_the_current_run_folder_is_refused(self):
        # runs/R2-evil shares its first characters with runs/R2; only a path relation tells them apart.
        self.refused("not-writable", lambda: self.policy().check_file("write", "runs/R2-evil/trace.json"))

    def test_X14_reading_from_a_look_alike_of_runs_is_refused(self):
        (self.root / "runs-evil" / "R2" / "trace.json").write_text("{}", encoding="utf-8")
        self.refused("not-readable", lambda: self.policy().check_file("read", "runs-evil/R2/trace.json"))


class ApprovalTextTest(unittest.TestCase):
    def test_parses_run_and_file(self):
        self.assertEqual(Approval.parse("R2:state/state.json"), Approval("R2", "state/state.json"))

    def test_rejects_text_without_both_parts(self):
        for text in ("R2", ":state/state.json", "R2:", ""):
            with self.subTest(text=text), self.assertRaises(ValueError):
                Approval.parse(text)


class FilesTest(Tree):
    """The file tool asks the policy first, so a refused operation never touches disk."""

    def test_a_refused_write_creates_nothing(self):
        files = Files(self.policy(GOOD_APPROVAL))
        with self.assertRaises(PolicyDenied):
            files.write_bytes("runs-evil/R2/trace.json", b"x")
        self.assertFalse((self.root / "runs-evil" / "R2" / "trace.json").exists())

    def test_an_allowed_write_creates_its_folders(self):
        Files(self.policy()).write_bytes("runs/R2/raw/a.body.gz", b"abc")
        self.assertEqual((self.root / "runs" / "R2" / "raw" / "a.body.gz").read_bytes(), b"abc")

    def test_an_approved_atomic_state_write_leaves_no_temporary_file(self):
        Files(self.policy(GOOD_APPROVAL)).write_atomic("state/state.json", b'{"new": true}\n')
        self.assertEqual((self.root / "state" / "state.json").read_bytes(), b'{"new": true}\n')
        self.assertEqual(sorted(p.name for p in (self.root / "state").iterdir()), ["state.json"])

    def test_an_unapproved_atomic_state_write_changes_nothing(self):
        with self.assertRaises(PolicyDenied):
            Files(self.policy(None)).write_atomic("state/state.json", b'{"new": true}\n')
        self.assertEqual((self.root / "state" / "state.json").read_bytes(), b"{}\n")
        self.assertEqual(sorted(p.name for p in (self.root / "state").iterdir()), ["state.json"])

    def test_a_refused_read_raises_instead_of_returning_bytes(self):
        outside = str(self.project.base / "outside" / "resume.pdf")
        with self.assertRaises(PolicyDenied):
            Files(self.policy()).read_bytes(outside)


if __name__ == "__main__":
    unittest.main()
