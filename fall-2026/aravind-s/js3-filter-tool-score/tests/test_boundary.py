"""The 19 boundary cases of the permission policy (GATE.md v1.0, Permission policy; BOUNDARY-TESTS.md).

My predictions were committed (21f33b7) before this file was written. Each test asserts what GATE.md
says should happen, not what I predicted: BOUNDARY-TESTS.md puts the two side by side, and
tools/boundary_table.py runs these same cases to fill its Actual column.

Requests go through the real network door (fetch.get_board) with a stand-in opener that records
every connection it is asked to open, so a refused request shows that no connection opened. Files go
through policy.Files on a temporary repo that has runs/, state/, persona/, a runs-evil/ folder beside
runs/, and a symlink runs/out-link that points to a folder outside the repo.
"""

from __future__ import annotations

import io
import os
import shutil
import tempfile
import unittest
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path

from job_agent import board_state, fetch, policy
from job_agent.errors import NeedsApproval, Redirected, Refused

REPO = Path(__file__).resolve().parent.parent
ALLOW, REFUSE, APPROVAL = "allow", "refuse", "approval"
VERKADA = "https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true"
PALANTIR = "https://api.lever.co/v0/postings/palantir?mode=json"

# What GATE.md v1.0 says for each case (not my prediction; BOUNDARY-TESTS.md has both).
EXPECTED = {1: REFUSE, 2: REFUSE, 3: REFUSE, 4: REFUSE, 5: REFUSE, 6: REFUSE, 7: ALLOW, 8: REFUSE, 9: REFUSE,
            10: REFUSE, 11: REFUSE, 12: REFUSE, 13: ALLOW, 14: REFUSE, 15: ALLOW, 16: ALLOW, 17: APPROVAL,
            18: ALLOW, 19: APPROVAL}


class Recorder:
    """A stand-in opener: records every connection it is asked to open and answers 200 with an empty list."""

    def __init__(self):
        self.opened = []

    def open(self, request, timeout=None):
        self.opened.append(request.full_url)
        reply = urllib.response.addinfourl(io.BytesIO(b'{"jobs": []}'), Message(), request.full_url, 200)
        reply.msg = "OK"
        return reply


class RedirectingServer(urllib.request.BaseHandler):
    """Stands in for api.lever.co answering 302 with a Location on another host. Records each request."""

    handler_order = 100  # ahead of urllib's own HTTPS handler, so nothing reaches the network

    def __init__(self):
        self.asked = []

    def https_open(self, request):
        self.asked.append(request.full_url)
        headers = Message()
        headers["Location"] = "https://evil.example/v0/postings/palantir?mode=json"
        reply = urllib.response.addinfourl(io.BytesIO(b""), headers, request.full_url, 302)
        reply.msg = "Found"
        return reply


class Sandbox:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-boundary-"))
        self.outside = Path(tempfile.mkdtemp(prefix="job-agent-outside-"))
        for folder in ("runs", "state", "persona", "prompts", "runs-evil"):
            (self.root / folder).mkdir()
        shutil.copy(REPO / "persona" / "jane-doe.json", self.root / "persona" / "jane-doe.json")
        os.symlink(self.outside, self.root / "runs" / "out-link")
        self.files = policy.Files(self.root, write_roots=["runs", "state"],
                                  read_roots=["persona", "prompts", "boards.json", "boards", "state", "runs"])
        self.recorder = Recorder()
        self.server = RedirectingServer()

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.outside, ignore_errors=True)

    def get(self, url):
        return fetch.get_board(url, opener=self.recorder)

    def redirected(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), fetch.RefuseRedirects(), self.server)
        return fetch.get_board(PALANTIR, opener=opener)

    def state(self, ids, runs):
        state = None
        for run in runs:
            state = board_state.next_state(state, "greenhouse", "verkada", VERKADA,
                                           [{"id": i, "title": "Software Engineer"} for i in ids], {"run_id": run}, [])
        return state


def actions(box: Sandbox) -> dict:
    """Case number -> (what it does, a call that returns when allowed and raises when not)."""
    old = box.state(["101", "102"], ["r1"])
    added = board_state.next_state(old, "greenhouse", "verkada", VERKADA,
                                   [{"id": i, "title": "Software Engineer"} for i in ("101", "102", "103")],
                                   {"run_id": "r2"}, [])
    dropped = dict(added, seen_ids=["102", "103"])
    path = "state/greenhouse-verkada.json"

    def delete():
        board_state.save(box.root / path, old)
        return box.files.check_state_delete(path, approval=None)

    return {
        1: ("GET a host not on the list", lambda: box.get("https://evil.example/posting-api/job-board/openai")),
        2: ("GET a look-alike host", lambda: box.get("https://api.lever.co.evil.example/v0/postings/palantir?mode=json")),
        3: ("GET with a user name before @", lambda: box.get("https://api.lever.co@evil.example/v0/postings/palantir?mode=json")),
        4: ("GET over plain http", lambda: box.get("http://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true")),
        5: ("GET an apply-like path on an allowed host", lambda: box.get("https://api.lever.co/v0/postings/palantir/abc123/apply")),
        6: ("POST to a board URL", lambda: policy.check_request("POST", VERKADA)),
        7: ("GET the real Verkada board URL", lambda: box.get(VERKADA)),
        8: ("a redirect from api.lever.co to another host", box.redirected),
        9: ("write through ..", lambda: box.files.check_write("runs/../persona/jane-doe.json")),
        10: ("write in runs-evil/ beside runs/", lambda: box.files.check_write("runs-evil/report.md")),
        11: ("write through a symlink in runs/", lambda: box.files.check_write("runs/out-link/report.md")),
        12: ("write an absolute path outside the repo", lambda: box.files.check_write("/tmp/report.md")),
        13: ("read Jane's résumé", lambda: box.files.check_read("persona/jane-doe.json")),
        14: ("write Jane's résumé", lambda: box.files.check_write("persona/jane-doe.json")),
        15: ("a board's first state", lambda: box.files.check_state_write(path, None, old)),
        16: ("a normal update that only adds ids", lambda: box.files.check_state_write(path, old, added)),
        17: ("a replacement that drops ids, no --approve", lambda: box.files.check_state_write(path, added, dropped)),
        18: ("the same replacement with --approve", lambda: box.files.check_state_write(path, added, dropped,
                                                                                            approval="reason")),
        19: ("delete a board's state, no --approve", delete),
    }


def outcome(action, root=None) -> tuple:
    """(allow | refuse | approval, what the program said)."""
    try:
        result = action()
    except NeedsApproval as exc:  # a Refused that --approve would allow
        return APPROVAL, str(exc)
    except (Refused, Redirected) as exc:
        return REFUSE, str(exc)
    if isinstance(result, fetch.Response):
        return ALLOW, f"sent once through the network door; the stand-in opener answered HTTP {result.status}"
    if isinstance(result, Path) and root is not None:
        return ALLOW, f"allowed: {result.relative_to(root)}"
    return ALLOW, str(result)


class BoundaryTest(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox()
        self.addCleanup(self.box.cleanup)
        self.cases = actions(self.box)

    def check(self, number):
        word, detail = outcome(self.cases[number][1])
        self.assertEqual(word, EXPECTED[number], f"case {number} ({self.cases[number][0]}): {detail}")
        return detail

    def test_case_01_a_host_not_on_the_list_is_refused_before_any_connection(self):
        self.check(1)
        self.assertEqual(self.box.recorder.opened, [])

    def test_case_02_a_look_alike_host_is_refused(self):
        self.assertIn("not on the allow-list", self.check(2))
        self.assertEqual(self.box.recorder.opened, [])

    def test_case_03_a_user_name_before_the_at_sign_is_refused(self):
        self.assertIn("names a user", self.check(3))
        self.assertEqual(self.box.recorder.opened, [])

    def test_case_04_plain_http_is_refused(self):
        self.assertIn("not https", self.check(4))

    def test_case_05_a_path_that_is_not_a_board_path_is_refused(self):
        self.assertIn("not a board path", self.check(5))
        self.assertEqual(self.box.recorder.opened, [])

    def test_case_06_post_is_refused(self):
        self.assertIn("GET requests only", self.check(6))

    def test_case_07_the_real_board_url_is_allowed_and_opened_once(self):
        self.check(7)
        self.assertEqual(self.box.recorder.opened, [VERKADA])

    def test_case_08_a_redirect_is_not_followed(self):
        self.assertIn("redirects are not followed", self.check(8))
        self.assertEqual(self.box.server.asked, [PALANTIR])  # nothing was asked of evil.example

    def test_case_09_a_path_with_dot_dot_is_refused(self):
        self.assertIn("'..'", self.check(9))

    def test_case_10_a_folder_beside_runs_with_the_same_start_is_refused(self):
        self.assertIn("outside the folders", self.check(10))

    def test_case_11_a_symlink_inside_runs_is_refused(self):
        self.assertIn("symlink", self.check(11))
        self.assertEqual(list(self.box.outside.iterdir()), [])

    def test_case_12_an_absolute_path_outside_the_repo_is_refused(self):
        self.check(12)

    def test_case_13_reading_the_resume_is_allowed(self):
        self.check(13)

    def test_case_14_writing_the_resume_is_refused(self):
        self.check(14)

    def test_case_15_a_boards_first_state_is_allowed(self):
        self.assertEqual(self.check(15), "first")

    def test_case_16_an_update_that_only_adds_ids_is_allowed(self):
        self.assertEqual(self.check(16), "append")

    def test_case_17_a_replacement_that_drops_ids_needs_approval(self):
        self.assertIn("1 seen id would be dropped", self.check(17))

    def test_case_18_the_same_replacement_with_approval_is_allowed(self):
        self.assertEqual(self.check(18), "approved")

    def test_case_19_deleting_a_state_needs_approval(self):
        self.assertIn("needs --approve", self.check(19))
        self.assertTrue((self.box.root / "state" / "greenhouse-verkada.json").exists())

    def test_there_are_19_cases_and_each_has_an_expected_result(self):
        self.assertEqual(sorted(self.cases), list(range(1, 20)))
        self.assertEqual(sorted(EXPECTED), list(range(1, 20)))


if __name__ == "__main__":
    unittest.main()
