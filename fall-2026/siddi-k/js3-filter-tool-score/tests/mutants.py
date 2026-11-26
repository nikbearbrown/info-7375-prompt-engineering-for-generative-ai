"""Put each FILTER.md wrong version (and two server lies) into the code, one at a time, and check its test fails.

Usage: python tests/mutants.py   (exit 0 only if every mutant is caught)"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from js3 import filter as flt  # noqa: E402
from js3 import mcp_server, textprep  # noqa: E402


def m1_substring():
    sub = lambda term: re.compile(re.escape(term))      # noqa: E731
    return [(flt, "whole_word", sub), (textprep, "whole_word", sub)]


def m2_boilerplate_kept():
    orig = flt.posting_sentences
    return [(flt, "posting_sentences", lambda p, bp: orig(p, {}))]


def m3_score_over_gates():
    orig = flt.evaluate

    def ev(cfg, p):
        r = orig(cfg, p)
        if r["verdict"] == "reject" and r["reasons"] != ["below_threshold"]:
            parts = flt.score_parts(cfg, p["title"], flt.posting_sentences(p, cfg["boilerplate"]))
            if parts["score"] >= cfg["keep_threshold"]:
                r.update(verdict="keep", score=parts["score"], parts=parts, reasons=[])
        return r
    return [(flt, "evaluate", ev)]


def m4_missing_is_reject():
    orig = flt.evaluate

    def ev(cfg, p):
        r = orig(cfg, p)
        if r["verdict"] == "cannot_tell":
            r["verdict"] = "reject"
        return r
    return [(flt, "evaluate", ev)]


def m5_count_repeats():
    orig = flt.score_parts

    def sp(cfg, title, sentences):
        parts = orig(cfg, title, sentences)
        text = "\n".join(sentences)
        n = sum(len(re.findall(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", text))
                for skill, aliases in cfg["skills"].items() for a in dict.fromkeys([skill, *aliases]))
        parts["score"] += n - parts["R2"]
        parts["R2"] = n
        parts["skills"] = [{"skill": "x"}] * n
        return parts
    return [(flt, "score_parts", sp)]


def m6_tool_writes():
    orig = mcp_server.Server.score

    def score(self, args):
        open(Path(__file__).resolve().parent / "_mutant_wrote_this.txt", "w").close()
        return orig(self, args)
    return [(mcp_server.Server, "score", score)]


def m7_schema_not_enforced():
    return [(mcp_server, "check_arguments", lambda args: None)]


MUTANTS = [
    ("WV1 substring matching", m1_substring, "test_filter.WV1Substring"),
    ("WV2 boilerplate counted", m2_boilerplate_kept, "test_filter.WV2Boilerplate"),
    ("WV3 score instead of gates", m3_score_over_gates, "test_filter.WV3GatesBeforeScore"),
    ("WV4 missing treated as an answer", m4_missing_is_reject, "test_filter.WV4MissingIsCannotTell"),
    ("WV5 ranking by repetition", m5_count_repeats, "test_filter.WV5Repetition"),
    ("server: readOnlyHint but it writes", m6_tool_writes, "test_mcp_server.ServerTests.test_call_is_actually_read_only_and_offline"),
    ("server: inputSchema declared, not enforced", m7_schema_not_enforced, "test_mcp_server.ServerTests.test_schema_is_enforced_not_just_declared"),
]


def main() -> int:
    caught = 0
    for name, make, target in MUTANTS:
        patches = make()
        saved = [(obj, attr, getattr(obj, attr)) for obj, attr, _ in patches]
        for obj, attr, new in patches:
            setattr(obj, attr, new)
        try:
            suite = unittest.defaultTestLoader.loadTestsFromName(target)
            result = unittest.TestResult()
            suite.run(result)
            failed = len(result.failures) + len(result.errors)
        finally:
            for obj, attr, old in saved:
                setattr(obj, attr, old)
        ok = failed > 0
        caught += ok
        print(f"{'CAUGHT ' if ok else 'MISSED '} {name}: {failed} of {result.testsRun} test(s) in {target} failed")
    leftover = Path(__file__).resolve().parent / "_mutant_wrote_this.txt"
    if leftover.exists():
        leftover.unlink()
    print(f"{caught}/{len(MUTANTS)} mutants caught")
    return 0 if caught == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
