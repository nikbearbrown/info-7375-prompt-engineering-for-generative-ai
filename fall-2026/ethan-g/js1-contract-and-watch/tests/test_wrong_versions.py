"""The plausible-but-wrong implementations named in CONTRACT.md, built on purpose.

Each test builds the wrong version and asserts that the audit (or the state
logic) catches it. If one of these tests ever fails, the safety net has a hole.
"""
import copy
import unittest
from pathlib import Path

from jsagent import audit, fetch, resume, rule, state

ROOT = Path(__file__).resolve().parent.parent
POSTINGS = fetch.parse_postings((ROOT / "tests" / "fixtures" / "board_small.json").read_bytes())
RESUME = resume.load_resume(ROOT / "persona" / "evan-gordon.resume.json")


def w1_shifted_labels(postings, r):
    """W1: verdicts computed correctly, then zipped against the list rotated by one."""
    verdicts = [rule.judge(p, r) for p in postings]
    rotated = postings[1:] + postings[:1]
    out = []
    for v, p in zip(verdicts, rotated):
        v = copy.deepcopy(v)
        v["posting_id"] = p["id"]
        out.append(v)
    return out


def w1_resorted_labels(postings, r):
    """W1 variant: verdicts sorted by verdict, ids re-attached in original order."""
    verdicts = sorted((rule.judge(p, r) for p in postings), key=lambda v: v["verdict"])
    out = []
    for v, p in zip(verdicts, postings):
        v = copy.deepcopy(v)
        v["posting_id"] = p["id"]
        out.append(v)
    return out


def w2_empty_justification(postings, r):
    """W2: right verdict, no citations."""
    out = []
    for p in postings:
        v = rule.judge(p, r)
        v["checks"] = []
        out.append(v)
    return out


def w2_invented_citation(postings, r):
    """W2 variant: cites a résumé value that is not in the résumé."""
    out = []
    for p in postings:
        v = rule.judge(p, r)
        v["checks"][3]["resume"][0]["value"] = ["Rust", "Elixir"]
        out.append(v)
    return out


def w2_unresolvable_path(postings, r):
    """W2 variant: cites a résumé path that does not exist."""
    out = []
    for p in postings:
        v = rule.judge(p, r)
        v["checks"][0]["resume"][0]["field"] = "search.dream_titles"
        out.append(v)
    return out


def w2_posting_value_not_in_posting(postings, r):
    """W2 variant: claims a skill appears in the posting that does not."""
    out = []
    for p in postings:
        v = rule.judge(p, r)
        v["checks"][3]["posting"]["value"] = ["Terraform", "Jenkins"]
        out.append(v)
    return out


def w3_baseline_reports_everything(prev_state, postings):
    """W3: forgets that the first run is a baseline."""
    seen = set() if prev_state is None else set(prev_state["seen_ids"])
    return False, [p for p in postings if p["id"] not in seen]


def w4_new_board_reports_everything(prev_state, postings):
    """W4: ignores which boards were seen before, so a board's first appearance floods 'new'."""
    seen = set() if prev_state is None else set(prev_state["seen_ids"])
    return prev_state is None, [] if prev_state is None else [p for p in postings if p["id"] not in seen]


class TestWrongVersionsAreCaught(unittest.TestCase):
    def assertCaught(self, verdicts):
        errors = audit.audit_verdicts(POSTINGS, RESUME, verdicts)
        self.assertTrue(errors, "audit accepted a wrong version")
        return errors

    def test_w1_shifted(self):
        self.assertCaught(w1_shifted_labels(POSTINGS, RESUME))

    def test_w1_resorted(self):
        self.assertCaught(w1_resorted_labels(POSTINGS, RESUME))

    def test_w1_missing_verdict(self):
        self.assertCaught([rule.judge(p, RESUME) for p in POSTINGS[:-1]])

    def test_w1_unknown_posting_id(self):
        vs = [rule.judge(p, RESUME) for p in POSTINGS]
        vs[0]["posting_id"] = "999999"
        self.assertCaught(vs)

    def test_w2_empty(self):
        self.assertCaught(w2_empty_justification(POSTINGS, RESUME))

    def test_w2_invented_resume_value(self):
        self.assertCaught(w2_invented_citation(POSTINGS, RESUME))

    def test_w2_unresolvable_path(self):
        self.assertCaught(w2_unresolvable_path(POSTINGS, RESUME))

    def test_w2_posting_value_not_in_posting(self):
        self.assertCaught(w2_posting_value_not_in_posting(POSTINGS, RESUME))

    def test_w2_flipped_verdict_same_checks(self):
        vs = [rule.judge(p, RESUME) for p in POSTINGS]
        vs[0]["verdict"] = "not_relevant"
        self.assertCaught(vs)

    def test_w3_baseline_reports_new(self):
        _, new = w3_baseline_reports_everything(None, POSTINGS)
        _, real_new = state.diff_new(None, POSTINGS)
        self.assertNotEqual(len(new), len(real_new))
        self.assertEqual(real_new, [])


class TestW4(unittest.TestCase):
    def test_w4_new_board_is_caught(self):
        alpha = [dict(p, board="alpha") for p in POSTINGS[:3]]
        beta = [dict(p, board="beta") for p in POSTINGS[3:]]
        st = state.update_state(None, alpha, {"run_id": "r1"})
        _, wrong = w4_new_board_reports_everything(st, alpha + beta)
        _, right = state.diff_new(st, alpha + beta)
        self.assertTrue(wrong)
        self.assertEqual(right, [])


if __name__ == "__main__":
    unittest.main()
