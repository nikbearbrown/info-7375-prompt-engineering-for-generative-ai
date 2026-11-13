"""The watch end to end, offline (CONTRACT.md In, Out, Refuses 2 and 6, wrong version 1, the failure sentence).

The board answers are constructed fixtures handed out by FakeGet; nothing here touches the network.
"""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from job_agent import watch
from job_agent.errors import BrokenInput, NoAnswer, Refused

from .helpers import PERSONA, Clock, FakeGet, board_bytes, job, response, stub_judge

A = [job("a-1"), job("a-2", "Backend Software Engineer, Payments"), job("a-3", "Data Engineer")]
B = [job("a-1"), job("a-2", "Backend Software Engineer, Payments"), job("b-4", "Full Stack Software Engineer, Growth")]


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.state = self.dir / "state" / "seen.json"
        self.runs = self.dir / "runs"
        self.clock = Clock()
        self.screen = []

    def run_once(self, body, status=200, judge=stub_judge, resume_path=PERSONA):
        get = FakeGet(response(body, status))
        summary = watch.run(resume_path=resume_path, state_path=self.state, runs_root=self.runs, judge=judge,
                            get=get, now=self.clock, say=self.screen.append)
        return summary, get

    def run_dirs(self):
        return sorted(p for p in self.runs.iterdir()) if self.runs.exists() else []

    def test_the_baseline_records_every_id_and_reports_none_new(self):
        summary, get = self.run_once(board_bytes(A), judge=None)
        self.assertEqual(get.urls, ["https://api.ashbyhq.com/posting-api/job-board/openai"])
        self.assertTrue(summary["baseline"])
        self.assertEqual(summary["counts"], {"new": 0, "gone": 0, "new_relevant_rule": 0, "new_relevant_claude": 0})
        saved = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(saved["seen_ids"], ["a-1", "a-2", "a-3"])
        self.assertIn("baseline: 3 postings recorded, 0 new", self.screen[0])

    def test_the_second_run_reports_exactly_the_added_posting(self):
        # Wrong version 1 (state saved before comparing) reports 0 new here.
        self.run_once(board_bytes(A), judge=None)
        summary, _ = self.run_once(board_bytes(B))
        report = json.loads((self.run_dirs()[-1] / "report.json").read_text(encoding="utf-8"))
        self.assertFalse(summary["baseline"])
        self.assertEqual([n["id"] for n in report["new"]], ["b-4"])
        self.assertEqual(summary["counts"]["new"], 1)

    def test_new_ids_are_recomputable_from_the_two_saved_responses(self):
        # The failure sentence: run 2's new ids must be exactly (ids in run 2) - (ids in run 1).
        self.run_once(board_bytes(A), judge=None)
        self.run_once(board_bytes(B))
        first, second = self.run_dirs()
        ids = [{j["id"] for j in json.loads((d / "response.json").read_bytes())["jobs"]} for d in (first, second)]
        reported = {n["id"] for n in json.loads((second / "report.json").read_text(encoding="utf-8"))["new"]}
        self.assertEqual(reported, ids[1] - ids[0])

    def test_gone_postings_are_listed_by_id_and_title_and_not_judged(self):
        judged = []

        def judge(job_data, resume, run_dir):
            judged.append(job_data["id"])
            return stub_judge(job_data, resume)

        self.run_once(board_bytes(A), judge=None)
        summary, _ = self.run_once(board_bytes(B), judge=judge)
        report = json.loads((self.run_dirs()[-1] / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["gone"], [{"id": "a-3", "title": "Data Engineer"}])
        self.assertEqual(judged, ["b-4"])
        self.assertEqual(summary["counts"]["gone"], 1)

    def test_the_same_answer_again_reports_nothing_new_but_still_prints_counts(self):
        self.run_once(board_bytes(A), judge=None)
        summary, _ = self.run_once(board_bytes(A))
        self.assertEqual(summary["counts"]["new"], 0)
        self.assertIn("3 postings in the response, 0 new since the last run, 0 gone", self.screen[-1])

    def test_a_posting_that_leaves_and_comes_back_is_not_new(self):
        self.run_once(board_bytes(A), judge=None)
        self.run_once(board_bytes(A[:1]))
        summary, _ = self.run_once(board_bytes(A))
        self.assertEqual(summary["counts"]["new"], 0)

    def test_the_raw_response_is_saved_byte_for_byte_with_its_sha256(self):
        body = board_bytes(A) + b"\n  "  # trailing bytes a re-encoder would drop
        summary, _ = self.run_once(body, judge=None)
        folder = self.run_dirs()[0]
        self.assertEqual((folder / "response.json").read_bytes(), body)
        digest = hashlib.sha256(body).hexdigest()
        self.assertEqual((folder / "response.sha256").read_text(encoding="utf-8"), f"{digest}  response.json\n")
        self.assertEqual(summary["response_sha256"], digest)
        meta = json.loads((folder / "response.meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["status"], meta["bytes"], meta["source"]), (200, len(body), "live fetch"))

    def test_a_broken_answer_is_saved_as_evidence_and_the_state_is_unchanged(self):
        self.run_once(board_bytes(A), judge=None)
        before = self.state.read_bytes()
        for body, status in ((b"<html>down</html>", 200), (board_bytes(A), 503), (board_bytes([]), 200),
                             (board_bytes([{"title": "no id"}]), 200)):
            with self.subTest(status=status, body=body[:20]):
                with self.assertRaises(BrokenInput):
                    self.run_once(body, status)
                folder = self.run_dirs()[-1]
                self.assertEqual((folder / "response.json").read_bytes(), body)
                self.assertTrue((folder / "error.txt").exists())
                self.assertFalse((folder / "report.json").exists())
                self.assertEqual(self.state.read_bytes(), before)

    def test_a_judge_that_fails_leaves_the_state_unchanged(self):
        self.run_once(board_bytes(A), judge=None)
        before = self.state.read_bytes()

        def failing(job_data, resume, run_dir):
            raise RuntimeError("judge crashed")

        with self.assertRaises(RuntimeError):
            self.run_once(board_bytes(B), judge=failing)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertIn("judge crashed", (self.run_dirs()[-1] / "error.txt").read_text(encoding="utf-8"))

    def test_a_refused_resume_stops_before_any_fetch(self):
        real_looking = json.loads(PERSONA.read_text(encoding="utf-8"))
        real_looking["fictional"] = False
        path = self.dir / "resume.json"
        path.write_text(json.dumps(real_looking), encoding="utf-8")
        get = FakeGet(response(board_bytes(A)))
        with self.assertRaises(Refused):
            watch.run(resume_path=path, state_path=self.state, runs_root=self.runs, get=get, now=self.clock,
                      say=self.screen.append)
        self.assertEqual(get.urls, [])
        self.assertFalse(self.state.exists())
        self.assertEqual(self.run_dirs(), [])

    def test_an_unreadable_state_file_stops_before_any_fetch(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text("{broken", encoding="utf-8")
        get = FakeGet(response(board_bytes(A)))
        with self.assertRaises(BrokenInput):
            watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, judge=stub_judge, get=get,
                      now=self.clock, say=self.screen.append)
        self.assertEqual(get.urls, [])
        self.assertEqual(self.state.read_text(encoding="utf-8"), "{broken")

    def test_a_later_run_without_a_judge_stops_before_any_fetch(self):
        self.run_once(board_bytes(A), judge=None)
        get = FakeGet(response(board_bytes(B)))
        with self.assertRaises(BrokenInput):
            watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, judge=None, get=get,
                      now=self.clock, say=self.screen.append)
        self.assertEqual(get.urls, [])

    def test_a_saved_run_folder_is_never_overwritten(self):
        clock = Clock()
        watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, get=FakeGet(response(board_bytes(A))),
                  now=lambda: clock.t, say=self.screen.append)
        saved = (self.run_dirs()[0] / "response.json").read_bytes()
        with self.assertRaises(Refused):
            watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, judge=stub_judge,
                      get=FakeGet(response(board_bytes(B))), now=lambda: clock.t, say=self.screen.append)
        self.assertEqual((self.run_dirs()[0] / "response.json").read_bytes(), saved)

    def test_contact_fields_never_reach_the_screen_or_the_report(self):
        self.run_once(board_bytes(A), judge=None)
        self.run_once(board_bytes(B))
        jane = json.loads(PERSONA.read_text(encoding="utf-8"))
        written = "\n".join(self.screen)
        for folder in self.run_dirs():
            for name in ("report.md", "report.json", "response.meta.json"):
                written += (folder / name).read_text(encoding="utf-8")
        written += self.state.read_text(encoding="utf-8")
        for value in (jane["name"], jane["email"], jane["phone"], *jane["links"]):
            self.assertNotIn(value, written)

    def test_the_report_keeps_the_record_and_the_judgment_apart(self):
        self.run_once(board_bytes(A), judge=None)
        self.run_once(board_bytes(B))
        text = (self.run_dirs()[-1] / "report.md").read_text(encoding="utf-8")
        self.assertIn("**Rule verdict (record):** relevant", text)
        self.assertIn("**Claude's judgment (model output, not verified):** not_relevant", text)
        self.assertIn("Claude's judgment (model output, not verified): not_relevant", "\n".join(self.screen))

    def test_a_replay_is_labeled_as_one(self):
        self.run_once(board_bytes(A), judge=None)
        saved = self.run_dirs()[0] / "response.json"
        other_state, other_runs = self.dir / "replay" / "seen.json", self.dir / "replay" / "runs"
        summary = watch.run(resume_path=PERSONA, state_path=other_state, runs_root=other_runs, replay=saved,
                            now=self.clock, say=self.screen.append, get=FakeGet())
        self.assertIn("replay of a saved response", summary["source"])
        self.assertIn("not a live run", summary["source"])
        meta = json.loads(next(other_runs.iterdir()).joinpath("response.meta.json").read_text(encoding="utf-8"))
        self.assertIn("replay", meta["source"])

    def test_a_screen_that_fails_leaves_the_state_unchanged(self):
        self.run_once(board_bytes(A), judge=None)
        before = self.state.read_bytes()

        def broken_screen(text):
            raise BrokenPipeError("the screen went away")

        with self.assertRaises(BrokenPipeError):
            watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, judge=stub_judge,
                      get=FakeGet(response(board_bytes(B))), now=self.clock, say=broken_screen)
        self.assertEqual(self.state.read_bytes(), before)  # so error.txt's "the state was not changed" is true
        self.assertIn("not changed", (self.run_dirs()[-1] / "error.txt").read_text(encoding="utf-8"))

    def test_no_answer_from_the_board_saves_nothing(self):
        def unreachable(url):
            raise OSError("network is unreachable")

        with self.assertRaises(NoAnswer):
            watch.run(resume_path=PERSONA, state_path=self.state, runs_root=self.runs, get=unreachable,
                      now=self.clock, say=self.screen.append)
        self.assertEqual(self.run_dirs(), [])
        self.assertFalse(self.state.exists())

    def test_one_screen_line_per_new_posting_and_the_report_starts_with_the_counts_line(self):
        self.run_once(board_bytes(A), judge=None)
        self.screen.clear()
        self.run_once(board_bytes(B))
        self.assertEqual(len(self.screen), 2)  # the counts line, then one line for b-4; gone postings are in the report
        self.assertTrue(self.screen[1].startswith("NEW b-4 "))
        first = (self.run_dirs()[-1] / "report.md").read_text(encoding="utf-8").splitlines()[0]
        self.assertTrue(first.startswith("Run ") and "new since the last run" in first)

    def test_a_replay_never_records_an_absolute_path(self):
        saved = self.dir / "elsewhere" / "response.json"
        saved.parent.mkdir()
        saved.write_bytes(board_bytes(A))
        summary = watch.run(resume_path=PERSONA, state_path=self.dir / "r" / "s.json", runs_root=self.dir / "r",
                            replay=saved, now=self.clock, say=self.screen.append, get=FakeGet())
        self.assertNotIn(str(self.dir), summary["source"])
        self.assertIn("(response.json)", summary["source"])


if __name__ == "__main__":
    unittest.main()
