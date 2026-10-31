"""Run the contract tests against three deliberately broken versions
(CONTRACT.md > Wrong versions). Each mutant must make at least one test fail."""
import re
import sys
import unittest
from unittest import mock

from agent import rule, watch


def substring_word(token, any_case=True):
    # Wrong version 2: substring matching, no word boundaries.
    return re.compile(re.escape(token), re.IGNORECASE)


_orig_run_once = watch.run_once


def forgetful_run_once(raw, resume_data, out_dir, run_label, seeded_from=None):
    # Wrong version 1: only remembers the previous run's ids, so a posting that
    # drops out and comes back is reported as new again.
    import json
    from pathlib import Path
    rep = _orig_run_once(raw, resume_data, out_dir, run_label, seeded_from)
    p = Path(out_dir) / "state" / "seen_ids.json"
    s = json.loads(p.read_text())
    s["seen_ids"] = sorted(str(j["id"]) for j in json.loads(raw)["jobs"])
    p.write_text(json.dumps(s))
    return rep


_orig_judge_all = rule.judge_all


def shifted_judge_all(postings, resume_data):
    # Wrong version 3: verdicts paired with the wrong postings (shifted by one).
    out = _orig_judge_all(postings, resume_data)
    ids = [v["posting_id"] for v in out]
    for v, pid in zip(out, ids[1:] + ids[:1]):
        v["posting_id"] = pid
    return out


MUTANTS = {
    "wrong version 1: seen posting reported new again": mock.patch.object(watch, "run_once", forgetful_run_once),
    "wrong version 2: substring matching": mock.patch.object(rule, "_word", substring_word),
    "wrong version 3: verdicts on wrong posting": mock.patch.object(rule, "judge_all", shifted_judge_all),
}

ok = True
for name, patch in MUTANTS.items():
    with patch:
        suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
        res = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
    failed = [t.id().split(".")[-1] for t, _ in res.failures + res.errors]
    caught = bool(failed)
    ok &= caught
    print(f"{'CAUGHT' if caught else 'MISSED'}  {name}: {len(failed)} failing test(s): {', '.join(failed)}")
sys.exit(0 if ok else 1)
