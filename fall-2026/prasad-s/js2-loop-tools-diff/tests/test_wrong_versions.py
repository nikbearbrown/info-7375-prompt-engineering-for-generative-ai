"""CONTRACT.md §5: the W1 and W2 checks, in both directions.

Each check is a function that returns a list of failures. On the real agent
code it must return none; on every deliberately wrong variant in
tests/wrong_versions/ it must return at least one. A wrong variant that
raises makes the test error, never pass.

Inputs: rule cases R01 (relevant) and R14 (not_relevant) from
tests/expected/rule_cases.json, and the §1 persona. Everything runs offline
in a temporary folder; the real agent runs in seeded mode there.
"""

import json
import tempfile
import unittest
from pathlib import Path

from support import JS1, load_table, persona

from agent.rule import judge, posting_field
from agent.run import run
from agent.state import parse_board_response
from wrong_versions import w1_pairing, w2_justification

ROWS = {row["id"]: row for row in load_table("rule_cases.json")["cases"]}
CASES = ("R01", "R14")
# Made-up board ids, JSON numbers as on the real board. R01 gets the smaller id.
BOARD_IDS = {"R01": 4100001, "R14": 4100002}
# Constructed test replies in the §6 format, written for this test. NOT Claude output.
# Each one agrees with its case's hand label and cites its own posting's title.
CONSTRUCTED_REPLIES = {
    "R01": [
        "VERDICT: relevant",
        "RESUME_FIELD: target_titles=Product Manager",
        "RESUME_FIELD: locations=New York",
        "RESUME_FIELD: skills=Python",
        "RESUME_FIELD: skills=SQL",
        "POSTING_FIELD: title=Product Manager",
        "POSTING_FIELD: location.name=New York",
        "POSTING_FIELD: content=Python",
        "POSTING_FIELD: content=SQL",
        "REASON: Title, location and two skills match.",
    ],
    "R14": [
        "VERDICT: not_relevant",
        "RESUME_FIELD: target_titles=Product Manager",
        "POSTING_FIELD: title=Software Engineer",
        "REASON: The title contains no target title, so C1 fails.",
    ],
}
RESUME_LISTS = ("target_titles", "locations", "skills")
POSTING_FIELD_NAMES = ("title", "location.name", "content")
CONDITIONS = ("C1", "C2", "C3")


def board_job(case):
    row = ROWS[case]
    return {
        "id": BOARD_IDS[case],
        "title": row["title"],
        "location": {"name": row["location"]},
        "content": row["content"],
        "absolute_url": f"https://example.invalid/jobs/{BOARD_IDS[case]}",
    }


def parsed_posting(case):
    """The posting exactly as the agent sees it after parse_board_response."""
    return parse_board_response(json.dumps({"jobs": [board_job(case)]}).encode())[0]


def write_workspace(tmp, order):
    """A seeded-run folder: config, empty-but-existing state, board, saved replies."""
    tmp = Path(tmp)
    (tmp / "evidence").mkdir()
    (tmp / "evidence" / "board.json").write_text(json.dumps({"jobs": [board_job(c) for c in order]}), encoding="utf-8")
    outputs = tmp / "claude_outputs"
    outputs.mkdir()
    metadata = {}
    for case in CASES:
        posting_id = str(BOARD_IDS[case])
        (outputs / f"{posting_id}.txt").write_text("\n".join(CONSTRUCTED_REPLIES[case]) + "\n", encoding="utf-8")
        metadata[posting_id] = {
            "file": f"{posting_id}.txt",
            "collected": "2026-10-27",
            "model": "none: constructed test reply",
            "prompt_version": "test",
        }
    (outputs / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    # An existing [] is not a baseline (v0.3), so both postings are new.
    (tmp / "state.json").write_text("[]", encoding="utf-8")
    config = {
        "board_token": "stripe",
        "allow_list": ["boards-api.greenhouse.io"],
        "resume_path": str(JS1 / "resume_persona.json"),
        "state_path": "state.json",
        "evidence_dir": "evidence",
        "claude_outputs_dir": "claude_outputs",
    }
    (tmp / "config.json").write_text(json.dumps(config), encoding="utf-8")
    return tmp


def real_agent(workspace):
    report = run(workspace / "config.json", seed_path=workspace / "evidence" / "board.json",
                 report_path=workspace / "run_report.json")
    return report["new_postings"]


def wrong_pipeline(variant):
    def pipeline(workspace):
        postings = parse_board_response((workspace / "evidence" / "board.json").read_bytes())
        return variant(postings, persona(), workspace / "claude_outputs")
    return pipeline


# ---- W1: each id carries its own verdict and cites its own title, in any input order.

def w1_record_failures(records):
    expected = {str(BOARD_IDS[case]): ROWS[case] for case in CASES}
    failures = []
    ids = [record["posting_id"] for record in records]
    if sorted(ids) != sorted(expected):
        failures.append(f"records cover ids {ids}, expected {sorted(expected)}")
    for record in records:
        posting_id = record["posting_id"]
        row = expected.get(posting_id)
        if row is None:
            continue
        own_title = row["title"]
        if record["title"] != own_title:
            failures.append(f"{posting_id}: title {record['title']!r}, not its own {own_title!r}")
        if record["rule_verdict"] != row["expect_verdict"]:
            failures.append(f"{posting_id}: rule_verdict {record['rule_verdict']}, its hand label is {row['expect_verdict']}")
        rule_justification = record.get("rule_justification") or {}
        c1 = (rule_justification.get("conditions") or {}).get("C1") or {}
        if c1.get("posting_value") != own_title:
            failures.append(f"{posting_id}: rule justification compares title {c1.get('posting_value')!r}, not its own {own_title!r}")
        for entry in rule_justification.get("posting_fields") or []:
            if entry.get("field") == "title" and str(entry.get("matched")).lower() not in own_title.lower():
                failures.append(f"{posting_id}: rule justification cites title {entry.get('matched')!r}, not in its own title")
        # The constructed replies agree with the hand labels, so Claude's expected verdict is the hand label.
        if record["claude_verdict"] != row["expect_verdict"]:
            failures.append(f"{posting_id}: judgment (Claude) {record['claude_verdict']}, its own saved reply says {row['expect_verdict']}")
            continue
        parsed = (record.get("claude_justification") or {}).get("parsed") or {}
        for entry in parsed.get("posting_fields") or []:
            if entry.get("field") == "title" and str(entry.get("value")).lower() not in own_title.lower():
                failures.append(f"{posting_id}: Claude's reply cites title {entry.get('value')!r}, not in its own title")
    return failures


def check_w1(pipeline):
    failures, pairings = [], []
    for order in (CASES, tuple(reversed(CASES))):
        with tempfile.TemporaryDirectory() as tmp:
            records = pipeline(write_workspace(tmp, order))
        label = " then ".join(order)
        failures += [f"[{label}] {failure}" for failure in w1_record_failures(records)]
        pairings.append({r["posting_id"]: (r["rule_verdict"], r["claude_verdict"]) for r in records})
    if pairings[0] != pairings[1]:
        failures.append(f"reordering the input changed which verdict belongs to which id: {pairings}")
    return failures


# ---- W2: every citation exists, a relevant record cites its matches, all conditions are marked.

def w2_failures(verdict, justification, posting, resume, row):
    justification = justification if isinstance(justification, dict) else {}
    resume_fields = justification.get("resume_fields") or []
    posting_fields = justification.get("posting_fields") or []
    conditions = justification.get("conditions") or {}
    failures = []
    for entry in resume_fields:
        field, value = entry.get("field"), entry.get("value")
        if field not in RESUME_LISTS or value not in resume[field]:
            failures.append(f"resume_fields cites {field}={value!r}, which is not in the résumé under {field}")
    for entry in posting_fields:
        field, matched = entry.get("field"), entry.get("matched")
        text = posting_field(posting, field) if field in POSTING_FIELD_NAMES else None
        if not isinstance(matched, str) or not matched or text is None or matched.lower() not in text.lower():
            failures.append(f"posting_fields cites {field}={matched!r}, which is not in this posting's {field}")
    if verdict == "relevant":
        for field, minimum, posting_name in (("target_titles", 1, "title"), ("skills", 2, "content")):
            named = {entry.get("value") for entry in resume_fields if entry.get("field") == field}
            matched = {
                term for term in resume[field]
                for entry in posting_fields
                if entry.get("field") == posting_name and str(entry.get("matched")).lower() == term.lower()
            }
            if len(named) < minimum or len(matched) < minimum:
                failures.append(
                    f"relevant record must cite at least {minimum} {field}: names {len(named)} "
                    f"in resume_fields, {len(matched)} matched in the posting's {posting_name}"
                )
    if set(conditions) != set(CONDITIONS):
        failures.append(f"conditions cover {sorted(conditions)}, not all of C1, C2, C3")
    hand_failing = [c for c in CONDITIONS if not row[f"expect_{c}"]]
    marked = [c for c in CONDITIONS if isinstance(conditions.get(c), dict) and conditions[c].get("result") is False]
    if marked != hand_failing:
        failures.append(f"failing conditions marked {marked}, hand-computed {hand_failing}")
    return failures


def check_w2(judge_fn):
    resume = persona()
    failures = []
    for case in CASES:
        verdict, justification = judge_fn(parsed_posting(case), resume)
        failures += [f"[{case}] {failure}" for failure in w2_failures(verdict, justification, parsed_posting(case), resume, ROWS[case])]
    return failures


class Inputs(unittest.TestCase):
    def test_r01_and_r14_have_opposite_hand_labels(self):
        self.assertEqual(ROWS["R01"]["expect_verdict"], "relevant")
        self.assertEqual(ROWS["R14"]["expect_verdict"], "not_relevant")
        self.assertNotEqual(ROWS["R01"]["title"], ROWS["R14"]["title"])


class W1Pairing(unittest.TestCase):
    def test_check_passes_on_real_agent(self):
        self.assertEqual(check_w1(real_agent), [])

    def test_check_fails_on_every_wrong_variant(self):
        for name, variant in w1_pairing.VARIANTS.items():
            with self.subTest(variant=name):
                self.assertTrue(check_w1(wrong_pipeline(variant)), f"W1 check did not catch {name}")

    def test_rule_variant_verdicts_are_correct_only_misattached(self):
        with tempfile.TemporaryDirectory() as tmp:
            records = wrong_pipeline(w1_pairing.build_records_sorted_independently)(write_workspace(tmp, CASES))
        self.assertCountEqual([r["rule_verdict"] for r in records], [ROWS[c]["expect_verdict"] for c in CASES])


class W2Justification(unittest.TestCase):
    def test_check_passes_on_real_agent(self):
        self.assertEqual(check_w2(judge), [])

    def test_check_passes_on_real_run_records(self):
        resume = persona()
        by_id = {str(BOARD_IDS[case]): case for case in CASES}
        with tempfile.TemporaryDirectory() as tmp:
            records = real_agent(write_workspace(tmp, CASES))
        self.assertEqual(len(records), len(CASES))
        for record in records:
            case = by_id[record["posting_id"]]
            with self.subTest(case=case):
                self.assertEqual(w2_failures(record["rule_verdict"], record["rule_justification"],
                                             parsed_posting(case), resume, ROWS[case]), [])

    def test_check_fails_on_every_wrong_variant(self):
        for name, variant in w2_justification.VARIANTS.items():
            with self.subTest(variant=name):
                self.assertTrue(check_w2(variant), f"W2 check did not catch {name}")

    def test_wrong_variants_keep_the_right_label(self):
        resume = persona()
        for name, variant in w2_justification.VARIANTS.items():
            for case in CASES:
                with self.subTest(variant=name, case=case):
                    self.assertEqual(variant(parsed_posting(case), resume)[0], ROWS[case]["expect_verdict"])


if __name__ == "__main__":
    unittest.main()
