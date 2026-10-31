"""The watch end to end, with a constructed board and a scripted stand-in for the model.
Nothing here touches the network, and no reply here is Claude output."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jobwatch import judge, net, run, state, transports
from jobwatch.errors import FetchError, InputError, JudgeError, StateError
from tests.helpers import NOT_RELEVANT_202, OTHER_1, RELEVANT_101, ScriptedModel, board_bytes, persona

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"


class Board:
    """A constructed board: serves whatever jobs the test sets, one fetch per run."""

    def __init__(self):
        self.calls = 0
        self.body = None
        self.fail = False

    def serve(self, *jobs):
        self.body = board_bytes(*jobs)

    def __call__(self):
        self.calls += 1
        if self.fail:
            raise FetchError("constructed network failure")
        return net.FetchResult(
            body=self.body,
            url=BOARD_URL,
            status=200,
            content_type="application/json; charset=utf-8",
            retrieved_at=f"2026-10-28T10:00:{self.calls:02d}Z",
        )


class AgentCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state_path = self.root / "state.json"
        self.out = self.root / "runs"
        self.board = Board()
        self.model = ScriptedModel(verdicts={101: "relevant", 202: "not_relevant"})

    def tearDown(self):
        self.tmp.cleanup()

    def run_agent(self, resume=None, mode="live"):
        return run.run_once(
            fetch=self.board,
            resume=persona() if resume is None else resume,
            state_path=self.state_path,
            out_dir=self.out,
            send=self.model,
            mode=mode,
            source="constructed test board",
        )

    def results(self, summary):
        return json.loads((Path(summary["run_dir"]) / "results.json").read_text(encoding="utf-8"))

    def by_id(self, summary):
        return {p["posting_id"]: p for p in self.results(summary)["postings"]}

    def run_dirs(self):
        return sorted(self.out.iterdir())


class WatchTest(AgentCase):
    def test_first_run_is_a_baseline_that_reports_nothing_new(self):
        self.board.serve(RELEVANT_101, NOT_RELEVANT_202)
        summary = self.run_agent()
        self.assertTrue(summary["baseline"])
        self.assertEqual(summary["new_ids"], [])
        self.assertEqual(self.results(summary)["postings"], [])
        self.assertEqual(self.model.calls, [])
        self.assertEqual(state.load_state(self.state_path)["seen_ids"], [101, 202])

    def test_raw_response_is_saved_unchanged_with_its_retrieval_time(self):
        self.board.serve(RELEVANT_101)
        run_dir = Path(self.run_agent()["run_dir"])
        self.assertEqual((run_dir / "raw_response.json").read_bytes(), self.board.body)
        retrieval = json.loads((run_dir / "retrieval.json").read_text(encoding="utf-8"))
        self.assertEqual(retrieval["retrieved_at"], "2026-10-28T10:00:01Z")
        self.assertEqual(retrieval["url"], BOARD_URL)
        self.assertEqual(retrieval["sha256"], hashlib.sha256(self.board.body).hexdigest())

    def test_later_run_reports_only_ids_not_seen_before(self):
        self.board.serve(OTHER_1)
        self.run_agent()
        self.board.serve(OTHER_1, RELEVANT_101, NOT_RELEVANT_202)
        summary = self.run_agent()
        self.assertFalse(summary["baseline"])
        self.assertEqual(summary["new_ids"], [101, 202])
        self.assertEqual(sorted(self.by_id(summary)), [101, 202])
        self.assertEqual(state.load_state(self.state_path)["seen_ids"], [1, 101, 202])

    def test_an_edited_title_does_not_make_a_posting_new(self):
        self.board.serve(RELEVANT_101)
        self.run_agent()
        self.board.serve(dict(RELEVANT_101, title="Software Engineer, Inference Platform"))
        self.assertEqual(self.run_agent()["new_ids"], [])
        self.assertEqual(self.model.calls, [])

    def test_an_id_that_disappears_and_returns_is_not_new(self):
        self.board.serve(OTHER_1, RELEVANT_101)
        self.run_agent()
        self.board.serve(OTHER_1)
        self.run_agent()
        self.board.serve(OTHER_1, RELEVANT_101)
        self.assertEqual(self.run_agent()["new_ids"], [])


class FailureLeavesStateTest(AgentCase):
    def test_raw_response_is_saved_before_it_is_interpreted(self):
        self.board.body = b'{"meta": {}}'
        with self.assertRaises(InputError):
            self.run_agent()
        self.assertFalse(self.state_path.exists())
        [run_dir] = self.run_dirs()
        self.assertEqual((run_dir / "raw_response.json").read_bytes(), b'{"meta": {}}')
        self.assertTrue((run_dir / "error.json").exists())
        self.assertFalse((run_dir / "results.json").exists())

    def test_invalid_board_on_a_later_run_leaves_state_unchanged(self):
        self.board.serve(OTHER_1)
        self.run_agent()
        before = self.state_path.read_bytes()
        self.board.body = b'{"jobs": [{"id": -1}]}'
        with self.assertRaises(InputError):
            self.run_agent()
        self.assertEqual(self.state_path.read_bytes(), before)

    def test_fetch_failure_leaves_state_unchanged(self):
        self.board.serve(OTHER_1)
        self.run_agent()
        before = self.state_path.read_bytes()
        self.board.fail = True
        with self.assertRaises(FetchError):
            self.run_agent()
        self.assertEqual(self.state_path.read_bytes(), before)

    def test_damaged_state_is_an_error_not_a_new_baseline(self):
        self.state_path.write_text("{", encoding="utf-8")
        self.board.serve(OTHER_1)
        with self.assertRaises(StateError):
            self.run_agent()
        self.assertEqual(self.board.calls, 0)
        self.assertEqual(self.state_path.read_text(encoding="utf-8"), "{")

    def test_invalid_resume_stops_before_any_request(self):
        resume = persona()
        resume["email"] = "alex.morgan@gmail.com"
        self.board.serve(OTHER_1)
        with self.assertRaises(InputError):
            self.run_agent(resume=resume)
        self.assertEqual(self.board.calls, 0)


class VerdictAttachmentTest(unittest.TestCase):
    """CONTRACT.md wrong version 1: two postings with different ids and opposite rule
    outcomes, in both orders. Each verdict and its evidence must stay with its own id."""

    def assess(self, order):
        with tempfile.TemporaryDirectory() as tmp:
            board = Board()
            model = ScriptedModel(verdicts={101: "relevant", 202: "not_relevant"})
            kwargs = dict(fetch=board, resume=persona(), state_path=Path(tmp) / "state.json",
                          out_dir=Path(tmp) / "runs", send=model, mode="live", source="constructed")
            board.serve(OTHER_1)
            run.run_once(**kwargs)
            board.serve(OTHER_1, *order)
            summary = run.run_once(**kwargs)
            results = json.loads((Path(summary["run_dir"]) / "results.json").read_text(encoding="utf-8"))
            return {p["posting_id"]: p for p in results["postings"]}

    def test_verdicts_and_evidence_stay_with_their_posting_in_either_order(self):
        for order in ([RELEVANT_101, NOT_RELEVANT_202], [NOT_RELEVANT_202, RELEVANT_101]):
            with self.subTest(order=[j["id"] for j in order]):
                by_id = self.assess(order)
                first, second = by_id[101], by_id[202]

                self.assertEqual(first["title"], "Software Engineer, Inference")
                self.assertEqual(first["rule_verdict"]["verdict"], "relevant")
                self.assertEqual(first["rule_verdict"]["conditions"][0]["posting_value"], "Software Engineer, Inference")
                self.assertEqual(first["claude_verdict"]["verdict"], "relevant")
                self.assertEqual(first["claude_verdict"]["posting_evidence"],
                                 [{"field": "posting.title", "quote": "Software Engineer, Inference"}])

                self.assertEqual(second["title"], "Senior Software Engineer, Inference")
                self.assertEqual(second["rule_verdict"]["verdict"], "not_relevant")
                self.assertEqual(second["rule_verdict"]["failed_conditions"], ["title_seniority"])
                self.assertEqual(second["rule_verdict"]["conditions"][1]["posting_value"],
                                 "Senior Software Engineer, Inference")
                self.assertEqual(second["claude_verdict"]["verdict"], "not_relevant")
                self.assertEqual(second["claude_verdict"]["posting_evidence"],
                                 [{"field": "posting.title", "quote": "Senior Software Engineer, Inference"}])


INVENTED_QUOTE = json.dumps({
    "posting_id": "101",
    "verdict": "relevant",
    "justification": "Strong match on systems experience.",
    "resume_evidence": [{"field": "resume.skills", "quote": "python"}],
    "posting_evidence": [{"field": "posting.content", "quote": "10+ years of Rust"}],
})

CITES_NOTHING = json.dumps({
    "posting_id": "101",
    "verdict": "relevant",
    "justification": "This looks like a good fit.",
    "resume_evidence": [],
    "posting_evidence": [],
})


class RejectedResponseTest(AgentCase):
    """CONTRACT.md wrong version 2, second half: a rejected reply is an error. It must not
    become a not_relevant verdict and must not advance the state."""

    def check_rejected(self, reply):
        self.board.serve(OTHER_1)
        self.run_agent()
        before = self.state_path.read_bytes()
        self.model.replies = {101: reply}
        self.board.serve(OTHER_1, RELEVANT_101)
        with self.assertRaises(JudgeError):
            self.run_agent()
        self.assertEqual(self.state_path.read_bytes(), before)
        failed_run = self.run_dirs()[-1]
        self.assertFalse((failed_run / "results.json").exists())
        self.assertTrue((failed_run / "error.json").exists())

    def test_an_invented_quotation_fails_the_run(self):
        self.check_rejected(INVENTED_QUOTE)

    def test_a_reply_that_cites_nothing_fails_the_run(self):
        self.check_rejected(CITES_NOTHING)


class OutputTest(AgentCase):
    def new_101(self):
        self.board.serve(OTHER_1)
        self.run_agent()
        self.board.serve(OTHER_1, RELEVANT_101)
        return self.run_agent()

    def test_disagreement_between_the_judges_is_preserved(self):
        self.model.verdicts[101] = "not_relevant"
        result = self.by_id(self.new_101())[101]
        self.assertEqual(result["rule_verdict"]["verdict"], "relevant")
        self.assertEqual(result["claude_verdict"]["verdict"], "not_relevant")
        self.assertFalse(result["verdicts_agree"])

    def test_each_verdict_is_labelled_record_or_model_judgment(self):
        result = self.by_id(self.new_101())[101]
        self.assertEqual(result["rule_verdict"]["kind"], "record")
        self.assertEqual(result["claude_verdict"]["kind"], "model_judgment")

    def test_the_call_metadata_is_kept_with_the_verdict(self):
        scripted = self.model

        def send_with_meta(system, user):
            return transports.Reply(scripted(system, user), {"transport": "constructed", "model": "m-1"})
        self.model = send_with_meta
        result = self.by_id(self.new_101())[101]
        self.assertEqual(result["claude_verdict"]["call"], {"transport": "constructed", "model": "m-1"})

    def test_the_prompt_recorded_is_the_prompt_sent_and_it_is_v2(self):
        # 2026-10-31: the student switched future runs to judge_v2; runs 1 and 2 used judge_v1.
        result = self.by_id(self.new_101())[101]
        [(system, _user)] = self.model.calls
        self.assertEqual(result["claude_verdict"]["prompt"], "judge_v2")
        self.assertEqual(system, judge.load_prompt(result["claude_verdict"]["prompt"]))

    def test_the_model_reply_is_saved_verbatim(self):
        summary = self.new_101()
        reply = (Path(summary["run_dir"]) / "claude" / "101.txt").read_text(encoding="utf-8")
        self.assertEqual(json.loads(reply)["posting_id"], "101")

    def test_the_model_receives_only_the_instructions_resume_and_posting(self):
        self.new_101()
        [(system, user)] = self.model.calls
        payload = json.loads(user)
        self.assertEqual(set(payload), {"resume", "posting"})
        self.assertEqual(payload["resume"], persona())
        self.assertEqual(payload["posting"], {
            "id": 101,
            "title": "Software Engineer, Inference",
            "location": {"name": "San Francisco, CA"},
            "content": "You write Python and PyTorch daily.",
        })
        self.assertNotIn("greenhouse", system + user)

    def test_a_seeded_run_is_labelled_seeded(self):
        self.board.serve(OTHER_1)
        summary = self.run_agent(mode="seeded")
        self.assertEqual(self.results(summary)["mode"], "seeded")
        self.assertIn("SEEDED", (Path(summary["run_dir"]) / "results.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
