"""tools/score_replies.py on constructed replies, labels and board (not real data)."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import JS1, persona

from agent.replies import validate_reply

_spec = importlib.util.spec_from_file_location("score_replies", JS1 / "tools" / "score_replies.py")
score_replies = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(score_replies)

SOURCE = "evidence/board.json"
BOARD = {"jobs": [
    {"id": 71, "title": "Product Manager", "location": {"name": "New York"}, "content": "&lt;p&gt;SQL and Python&lt;/p&gt;"},
    {"id": 72, "title": "Designer", "location": {"name": "London"}, "content": "Sketching"},
]}
RELEVANT_SQL = ("VERDICT: relevant\nRESUME_FIELD: target_titles=Product Manager\nRESUME_FIELD: skills=SQL\n"
                "POSTING_FIELD: title=Product Manager\nPOSTING_FIELD: content=SQL\nREASON: C1, C2 and C3 pass.\n")
RELEVANT_PYTHON = RELEVANT_SQL.replace("=SQL", "=Python")
NOT_RELEVANT = ("VERDICT: not_relevant\nRESUME_FIELD: target_titles=Product Manager\n"
                "POSTING_FIELD: title=Designer\nREASON: C1 fails: no target title in the title.\n")
WRAPPED = "Here is my answer:\n" + NOT_RELEVANT  # a sentence before the reply: rejected
SAMPLING = {"71_r1": RELEVANT_SQL, "71_r2": RELEVANT_PYTHON, "72_r1": NOT_RELEVANT, "72_r2": WRAPPED}
LABELS = {"source": SOURCE, "labels": [{"id": "71", "verdict": "relevant"}, {"id": "72", "verdict": "relevant"}]}


def entry(key, posting_id=None):
    data = {"file": f"{key}.txt", "collected": "2026-10-29T00:00:00Z", "model": "test model",
            "prompt_version": "baseline-v1"}
    if posting_id:
        data["posting_id"] = posting_id
    return data


def wrapped_reasons():
    """The agent's own reasons; the format check fails, so the posting is never read."""
    return validate_reply(WRAPPED, persona(), {}).reasons


EXPECTED_SAMPLING = [
    "71_r1.txt  accepted  judgment (Claude): relevant  hand: relevant  PASS",
    "71_r2.txt  accepted  judgment (Claude): relevant  hand: relevant  PASS",
    "72_r1.txt  accepted  judgment (Claude): not_relevant  hand: relevant  FAIL",
    "72_r2.txt  rejected  judgment (Claude): rejected  hand: relevant  FAIL",
    *(f"    - {reason}" for reason in wrapped_reasons()),
    "replies: 4  accepted: 3  rejected: 1  PASS: 2  pass rate: 2/4 = 50%",
    "",
    "per posting (sampling repeats):",
    "71  verdicts: relevant, relevant  accepted: 2/2  "
    "RESUME_FIELD lines identical: no  POSTING_FIELD lines identical: no",
    "72  verdicts: not_relevant, rejected  accepted: 1/2  "
    "RESUME_FIELD lines identical: yes  POSTING_FIELD lines identical: yes",
]


def run_tool(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = score_replies.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ScoreReplies(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "evidence").mkdir()
        (self.root / SOURCE).write_text(json.dumps(BOARD), encoding="utf-8")
        (self.root / "experiments").mkdir()
        selected = self.root / "experiments" / "selected_ids.json"
        selected.write_text(json.dumps({"source": SOURCE}), encoding="utf-8")
        patcher = mock.patch.object(score_replies, "SELECTED_IDS", selected)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.labels = self.write_json("labels.json", LABELS)
        self.sampling = self.write_folder("sampling", SAMPLING, {key: entry(key, key.split("_")[0]) for key in SAMPLING})

    def write_json(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def write_folder(self, name, replies, metadata):
        folder = self.root / name
        folder.mkdir()
        for key, text in replies.items():
            (folder / f"{key}.txt").write_text(text, encoding="utf-8")
        (folder / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        return folder

    def test_sampling_folder_with_labels(self):
        code, out, err = run_tool(str(self.sampling), "--labels", str(self.labels))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines(), EXPECTED_SAMPLING)

    def test_without_labels_there_is_no_pass_or_fail(self):
        code, out, _ = run_tool(str(self.sampling))
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertEqual(lines[0], "71_r1.txt  accepted  judgment (Claude): relevant")
        self.assertEqual([line for line in lines if line.endswith(("PASS", "FAIL"))], [])
        self.assertIn("replies: 4  accepted: 3  rejected: 1  PASS: n/a (no --labels)", lines)

    def test_dev_folder_metadata_problems_are_rejections_and_no_sampling_section(self):
        metadata = {"71": entry("71"), "72": dict(entry("72"), model="")}
        folder = self.write_folder("baseline", {"72": NOT_RELEVANT}, metadata)  # 71.txt is not saved
        code, out, _ = run_tool(str(folder), "--labels", str(self.labels))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "71.txt  rejected  judgment (Claude): rejected  hand: relevant  FAIL",
            "    - 71.txt is listed in metadata.json but was not saved",
            "72.txt  rejected  judgment (Claude): rejected  hand: relevant  FAIL",
            "    - metadata.json entry for 72 has no model",
            "replies: 2  accepted: 0  rejected: 2  PASS: 0  pass rate: 0/2 = 0%",
        ])

    def test_split_scores_only_that_split(self):
        metadata = {"71": dict(entry("71"), split="development"), "72": dict(entry("72"), split="held_out")}
        folder = self.write_folder("baseline", {"71": RELEVANT_SQL, "72": NOT_RELEVANT}, metadata)
        heldout_labels = self.write_json("heldout.json", dict(LABELS, labels=LABELS["labels"][1:]))
        code, out, err = run_tool(str(folder), "--split", "held_out", "--labels", str(heldout_labels))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines(), [
            "split: held_out (1 of 2 replies in metadata.json)",
            "72.txt  accepted  judgment (Claude): not_relevant  hand: relevant  FAIL",
            "replies: 1  accepted: 1  rejected: 0  PASS: 0  pass rate: 0/1 = 0%",
        ])
        code, out, _ = run_tool(str(folder), "--split", "development", "--labels", str(self.labels))
        self.assertEqual(out.splitlines(), [
            "split: development (1 of 2 replies in metadata.json)",
            "71.txt  accepted  judgment (Claude): relevant  hand: relevant  PASS",
            "replies: 1  accepted: 1  rejected: 0  PASS: 1  pass rate: 1/1 = 100%",
        ])
        code, out, _ = run_tool(str(folder), "--labels", str(self.labels))  # no --split: as before
        self.assertEqual(out.splitlines()[-1], "replies: 2  accepted: 2  rejected: 0  PASS: 1  pass rate: 1/2 = 50%")

    def test_split_is_refused_for_sampling(self):
        sampling_metadata = {key: dict(entry(key, key.split("_")[0]), set="sampling") for key in SAMPLING}
        folder = self.write_folder("sampling_set", SAMPLING, sampling_metadata)
        for split in ("development", "held_out"):
            with self.subTest(split):
                code, out, err = run_tool(str(folder), "--split", split, "--labels", str(self.labels))
                self.assertNotEqual(code, 0)
                self.assertEqual(out, "")
                self.assertIn("sampling replies have no split", err)

    def test_unscoreable_input_is_an_error_with_no_output(self):
        other_source = self.write_json("other.json", dict(LABELS, source="evidence/other.json"))
        one_label = self.write_json("one.json", dict(LABELS, labels=LABELS["labels"][:1]))
        unknown = self.write_folder("unknown", {"99": NOT_RELEVANT}, {"99": entry("99")})
        cases = {
            "no metadata.json": [str(self.root / "evidence")],
            "labels from another source": [str(self.sampling), "--labels", str(other_source)],
            "posting without a hand label": [str(self.sampling), "--labels", str(one_label)],
            "posting not in the source": [str(unknown)],
        }
        for name, argv in cases.items():
            with self.subTest(name):
                code, out, err = run_tool(*argv)
                self.assertNotEqual(code, 0)
                self.assertEqual(out, "")
                self.assertIn("error", err)

    def test_writes_no_files(self):
        before = sorted(self.root.rglob("*"))
        run_tool(str(self.sampling), "--labels", str(self.labels))
        self.assertEqual(sorted(self.root.rglob("*")), before)


if __name__ == "__main__":
    unittest.main()
