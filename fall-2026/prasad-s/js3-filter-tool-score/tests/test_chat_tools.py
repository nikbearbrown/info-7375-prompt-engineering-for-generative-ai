"""tools/prep_chat.py and tools/save_reply.py on constructed data only.

Each test builds a temporary JS1 root (board, selected ids, run 2 report,
prompts). Replies come from --from-file, never the clipboard, and prep_chat
is given a fake copy function, so no test touches pbcopy or pbpaste.
"""

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from support import JS1, persona

if str(JS1 / "tools") not in sys.path:
    sys.path.insert(0, str(JS1 / "tools"))

import prep_chat  # noqa: E402
import save_reply  # noqa: E402

from agent.replies import claude_judgment, load_metadata  # noqa: E402
from agent.state import parse_board_response  # noqa: E402

RUN2_IDS = ["101", "102"]
DEV_IDS = ["201", "202", "203", "204", "205", "206", "207"]  # first 5 are the sampling set
HELDOUT_IDS = ["301", "302"]
PLACEHOLDER = "(paste the --for-claude block from the viewer here)"
BASELINE_PROMPT = f"PROMPT_VERSION: baseline-v1\n\nApply the rule.\n\nPOSTING\n{PLACEHOLDER}\n"
REVISION_PROMPT = f"PROMPT_VERSION: revision-v1\n\nApply the rule, revised.\n\nPOSTING\n{PLACEHOLDER}\n"
# Constructed replies, not Claude output.
FENCED_REPLY = b"```\nVERDICT: relevant\nREASON: wrapped in fences.\n```\n"
VALID_REPLY = (b"VERDICT: relevant\nRESUME_FIELD: target_titles=Product Manager\nRESUME_FIELD: locations=New York\n"
               b"RESUME_FIELD: skills=Python\nRESUME_FIELD: skills=SQL\nPOSTING_FIELD: title=Product Manager\n"
               b"POSTING_FIELD: location.name=New York\nPOSTING_FIELD: content=Python\nPOSTING_FIELD: content=SQL\n"
               b"REASON: Title, location and two skills match.\n")
COLLECTED = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d \(UTC \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\)$")


def job(posting_id):
    return {"id": int(posting_id), "title": f"Product Manager, Constructed {posting_id}",
            "location": {"name": "New York"}, "content": "&lt;p&gt;Python and SQL&lt;/p&gt;"}


def make_root(tmp):
    root = Path(tmp)
    (root / "evidence").mkdir()
    (root / "experiments").mkdir()
    (root / "prompts").mkdir()
    ids = RUN2_IDS + DEV_IDS + HELDOUT_IDS
    (root / "evidence" / "board.json").write_text(json.dumps({"jobs": [job(i) for i in ids]}), encoding="utf-8")
    (root / "evidence" / "run_report_run2_2026-10-28.json").write_text(
        json.dumps({"summary": {"source": {"file": "board.json"}, "new_ids": RUN2_IDS}}), encoding="utf-8")
    (root / "experiments" / "selected_ids.json").write_text(json.dumps(
        {"source": "evidence/board.json", "development": DEV_IDS, "held_out": HELDOUT_IDS}), encoding="utf-8")
    (root / "prompts" / "claude_prompt_baseline.txt").write_text(BASELINE_PROMPT, encoding="utf-8")
    (root / "prompts" / "revision.txt").write_text(REVISION_PROMPT, encoding="utf-8")
    return root


def call(module, argv, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = module.main(argv, **kwargs)
    return code, out.getvalue(), err.getvalue()


def all_files(root):
    return sorted(p.relative_to(root).as_posix() for p in Path(root).rglob("*") if p.is_file())


class ChatToolsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = make_root(tmp.name)
        # Reply inputs live outside the root, so "nothing was written" checks see only the tools' writes.
        inbox = tempfile.TemporaryDirectory()
        self.addCleanup(inbox.cleanup)
        self.inbox = Path(inbox.name)
        self.copied = []

    def prep(self, *argv):
        return call(prep_chat, list(argv), root=self.root, copy=self.copied.append)

    def save(self, posting_id, set_name, data, *extra, model="Opus 5.5"):
        reply = self.inbox / "reply_in.txt"
        reply.write_bytes(data)
        return call(save_reply, [posting_id, "--set", set_name, "--model", model, "--from-file", str(reply), *extra],
                    root=self.root)


class PrepChat(ChatToolsTest):
    def test_copies_prompt_with_block_and_prints_no_posting_text(self):
        code, out, _ = self.prep("201", "--set", "dev")
        self.assertEqual(code, 0)
        [text] = self.copied
        self.assertNotIn(PLACEHOLDER, text)
        self.assertIn("TITLE: Product Manager, Constructed 201\nLOCATION: New York\nCONTENT:  Python and SQL \n", text)
        self.assertEqual(out.splitlines(), ["posting_id: 201", "set: dev", "prompt_version: baseline-v1",
                                            f"characters copied: {len(text)}"])
        for leak in ("Product Manager", "New York", "Python", "relevant", "verdict"):
            self.assertNotIn(leak.lower(), out.lower())

    def test_set_membership_refusals(self):
        for posting_id, set_name in (("101", "dev"), ("206", "sampling"), ("301", "dev"), ("201", "heldout"),
                                     ("201", "run2"), ("999", "dev")):
            with self.subTest(posting_id=posting_id, set=set_name):
                code, out, err = self.prep(posting_id, "--set", set_name)
                self.assertNotEqual(code, 0)
                self.assertIn("REFUSED", err)
                self.assertEqual(out, "")
        self.assertEqual(self.copied, [])

    def test_refuses_prompt_without_placeholder_line(self):
        prompt = self.root / "prompts" / "no_placeholder.txt"
        prompt.write_text("PROMPT_VERSION: baseline-v1\n\nPOSTING\n(paste here)\n", encoding="utf-8")
        code, _, err = self.prep("201", "--set", "dev", "--prompt", str(prompt))
        self.assertNotEqual(code, 0)
        self.assertIn("REFUSED", err)
        self.assertEqual(self.copied, [])

    def test_run2_and_sampling_refuse_a_revision_prompt(self):
        revision = str(self.root / "prompts" / "revision.txt")
        for posting_id, set_name in (("101", "run2"), ("201", "sampling")):
            with self.subTest(set=set_name):
                code, _, _ = self.prep(posting_id, "--set", set_name, "--prompt", revision)
                self.assertNotEqual(code, 0)
        self.assertEqual(self.prep("201", "--set", "dev", "--prompt", revision)[0], 0)


class SaveReply(ChatToolsTest):
    def test_saves_bytes_unchanged_fences_and_trailing_newline(self):
        code, out, _ = self.save("101", "run2", FENCED_REPLY)
        self.assertEqual(code, 0)
        self.assertEqual((self.root / "claude_outputs" / "101.txt").read_bytes(), FENCED_REPLY)
        self.assertIn(f"bytes: {len(FENCED_REPLY)}", out)
        self.assertIn("first line: '```'", out)

    def test_refuses_to_overwrite_reply_or_metadata_entry(self):
        self.assertEqual(self.save("101", "run2", FENCED_REPLY)[0], 0)
        before = (self.root / "claude_outputs" / "metadata.json").read_bytes()
        code, _, err = self.save("101", "run2", VALID_REPLY)
        self.assertNotEqual(code, 0)
        self.assertIn("not overwriting", err)
        self.assertEqual((self.root / "claude_outputs" / "101.txt").read_bytes(), FENCED_REPLY)
        self.assertEqual((self.root / "claude_outputs" / "metadata.json").read_bytes(), before)
        # Entry present but reply file gone: still refused.
        (self.root / "claude_outputs" / "101.txt").unlink()
        self.assertNotEqual(self.save("101", "run2", VALID_REPLY)[0], 0)
        self.assertFalse((self.root / "claude_outputs" / "101.txt").exists())

    def test_refuses_prompt_copied_and_empty_clipboard(self):
        before = all_files(self.root)
        for data in (BASELINE_PROMPT.encode(), b"", b" \n"):
            with self.subTest(data=data[:20]):
                code, _, err = self.save("101", "run2", data)
                self.assertNotEqual(code, 0)
                self.assertIn("REFUSED", err)
        self.assertEqual(all_files(self.root), before)

    def test_set_membership_and_repeat_refusals(self):
        before = all_files(self.root)
        for posting_id, set_name, extra in (("201", "run2", []), ("101", "dev", []), ("206", "sampling", ["--repeat", "1"]),
                                            ("201", "sampling", []), ("201", "sampling", ["--repeat", "5"]),
                                            ("101", "run2", ["--repeat", "1"])):
            with self.subTest(posting_id=posting_id, set=set_name, extra=extra):
                self.assertNotEqual(self.save(posting_id, set_name, VALID_REPLY, *extra)[0], 0)
        self.assertEqual(all_files(self.root), before)

    def test_run2_metadata_shape_is_readable_by_the_agent(self):
        self.assertEqual(self.save("101", "run2", VALID_REPLY)[0], 0)
        outputs = self.root / "claude_outputs"
        entry = json.loads((outputs / "metadata.json").read_text(encoding="utf-8"))["101"]
        self.assertEqual(set(entry), {"file", "collected", "model", "prompt_version", "set", "conversation"})
        self.assertEqual(entry["file"], "101.txt")
        self.assertRegex(entry["collected"], COLLECTED)
        self.assertEqual((entry["model"], entry["prompt_version"], entry["set"], entry["conversation"]),
                         ("Opus 5.5", "baseline-v1", "run2", "fresh Incognito chat"))
        posting = parse_board_response(json.dumps({"jobs": [job("101")]}).encode())[0]
        metadata, error = load_metadata(outputs)
        verdict, _ = claude_judgment("101", posting, persona(), outputs, metadata, error)
        self.assertEqual(verdict, "relevant")

    def test_sampling_r1_is_not_reused_as_the_dev_baseline_reply(self):
        # chat_plan.md: "Sampling reply #1 also counts as the development baseline reply: no".
        self.assertEqual(self.save("201", "sampling", FENCED_REPLY, "--repeat", "1")[0], 0)
        sampling = self.root / "experiments" / "sampling"
        experiment = self.root / "experiments" / "prompt_experiment"
        self.assertEqual((sampling / "201_r1.txt").read_bytes(), FENCED_REPLY)
        self.assertEqual(all_files(experiment) if experiment.exists() else [], [])
        entry = json.loads((sampling / "metadata.json").read_text(encoding="utf-8"))["201_r1"]
        self.assertEqual(set(entry), {"file", "posting_id", "collected", "model", "prompt_version", "set",
                                      "repeat", "conversation"})
        self.assertEqual((entry["file"], entry["posting_id"], entry["set"], entry["repeat"]),
                         ("201_r1.txt", "201", "sampling", 1))
        # A first-5 id gets its own dev baseline chat: the save is accepted, with its own bytes.
        self.assertEqual(self.save("201", "dev", VALID_REPLY)[0], 0)
        self.assertEqual((experiment / "baseline" / "201.txt").read_bytes(), VALID_REPLY)
        dev_entry = json.loads((experiment / "baseline" / "metadata.json").read_text(encoding="utf-8"))["201"]
        self.assertEqual(set(dev_entry), {"file", "collected", "model", "prompt_version", "set", "split",
                                          "conversation"})
        self.assertEqual((dev_entry["file"], dev_entry["set"], dev_entry["split"]), ("201.txt", "dev", "development"))
        self.assertEqual((sampling / "201_r1.txt").read_bytes(), FENCED_REPLY)

    def test_dev_and_heldout_folders_follow_prompt_version(self):
        revision = str(self.root / "prompts" / "revision.txt")
        self.assertEqual(self.save("206", "dev", VALID_REPLY)[0], 0)
        self.assertEqual(self.save("201", "dev", VALID_REPLY, "--prompt", revision)[0], 0)
        self.assertEqual(self.save("301", "heldout", VALID_REPLY, "--prompt", revision)[0], 0)
        experiment = self.root / "experiments" / "prompt_experiment"
        self.assertTrue((experiment / "baseline" / "206.txt").is_file())
        self.assertTrue((experiment / "revision" / "201.txt").is_file())
        revision_meta = json.loads((experiment / "revision" / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual({k: (v["split"], v["prompt_version"]) for k, v in revision_meta.items()},
                         {"201": ("development", "revision-v1"), "301": ("held_out", "revision-v1")})


if __name__ == "__main__":
    unittest.main()
