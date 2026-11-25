"""Finished-but-wrong demonstration (GATE.md). A DELIBERATE wrong version, not the agent's normal code.

Replays the saved 2026-10-23 responses with wrong version 1 (tests/wrong_versions.py: a parser that treats a
response without a 'jobs' key as an empty board) plugged into the real loop. The run ends `finished` and says
Palantir has 0 postings. Then the independent check (earlybird/check.py) re-reads the raw files and catches it.

    python experiments/finished_wrong.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from earlybird import boards, check, gate, loop, report, watch  # noqa: E402
from earlybird.policy import Policy  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402
from earlybird.tools import Tools, Trace  # noqa: E402
import wrong_versions  # noqa: E402

LABEL = "demo-finished-wrong"
KEYS = ["ashby:commure", "greenhouse:stripe", "greenhouse:figma", "greenhouse:databricks", "lever:palantir"]


def main():
    policy = Policy(ROOT)
    budget = gate.Budget()
    trace = Trace(budget)
    tools = Tools(policy, budget, trace, "2026-10-23", replay=True)
    board_list = [b for b in boards.load(tools.read_text("config/boards.json")) if b["key"] in KEYS]
    resume = load_resume(ROOT / "data/resume/rohan-desai.example.json")
    state = watch.empty_state()
    result = loop.run(board_list, tools, budget, trace, state, resume, "2026-10-23", LABEL,
                      parse=wrong_versions.parse_jobs_key_or_empty)
    tools.write_text(f"reports/{LABEL}-trace.jsonl", trace.jsonl())
    tools.write_text(f"reports/{LABEL}.md", "> DELIBERATE WRONG VERSION 1 plugged in (experiments/finished_wrong.py)."
                     " This report is wrong on purpose.\n\n" + report.markdown(result, "replay of data/raw/2026-10-23/"))
    print("--- the agent's own report (wrong version 1 plugged in) ---")
    for b in result["boards"]:
        print(f"  {b['key']:24} {b['status']}  {b['postings']} postings")
    print(f"  exit: {result['exit']}   <- looks clean")

    out = check.check(ROOT, ROOT / f"reports/{LABEL}-trace.jsonl")
    print("--- independent check (re-reads the raw files with its own counter) ---")
    for r in out["boards"]:
        print(f"  {'ok ' if r['claimed'] == r['recounted'] else 'BAD'} {r['board']:24} "
              f"trace {r['claimed']:>4} | raw file {r['recounted']}")
    for p in out["problems"]:
        print(f"  PROBLEM: {p}")
    print(f"  verdict: {out['verdict']}")
    tools.write_text(f"reports/{LABEL}-check.json", json.dumps(out, indent=2))
    return 0 if out["verdict"] == "FAIL" else 1  # success here means the check caught the wrong result


if __name__ == "__main__":
    raise SystemExit(main())
