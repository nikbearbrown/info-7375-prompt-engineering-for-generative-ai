"""Prompt experiment (brief Step 4.2, R24-R26): run one prompt file on the dev or held-out labels and score it.

Why a script: the pass rate has to be recomputable from saved data, and the held-out set must not
be looked at before the revision is fixed. So held-out runs refuse to start unless both prompt
files exist and the caller says --final; dev runs are free (dev is where we are allowed to look).

Same judge as the agent (claude.judge + validator, claude -p). "Pass" = the Claude verdict
equals Isaac's hand label; a rejected or failed answer counts as a fail, because the agent
would have recorded it as not_relevant with an error.

Run:  .venv/bin/python reports/experiment.py claude_judge.v1 dev
      .venv/bin/python reports/experiment.py claude_judge.v2 held_out --final
"""

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs                     # noqa: E402
from job_agent.common.paths import Paths         # noqa: E402
from job_agent.judges import claude, claude_cli  # noqa: E402
from job_agent.watch.boards import greenhouse    # noqa: E402

RAW = ROOT / "evidence/raw/2026-10-31T214118Z/stripe_content.json"   # where the labeled postings came from
OUT = ROOT / "reports" / "experiment"
PROMPTS = ("claude_judge.v1", "claude_judge.v2")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", choices=PROMPTS)
    ap.add_argument("split", choices=("dev", "held_out"))
    ap.add_argument("--final", action="store_true", help="required for held_out: the revision is fixed")
    args = ap.parse_args()
    paths = Paths()
    if args.split == "held_out":
        # The held-out set is the exam: only after v2 exists and is no longer being tuned.
        missing = [p for p in PROMPTS if not paths.prompt(p).exists()]
        if missing or not args.final:
            sys.exit(f"refusing held_out: {'missing ' + ', '.join(missing) if missing else 'pass --final once v2 is fixed'}")

    ids = json.loads((ROOT / "labels/split.json").read_text())[args.split]
    labels = {int(r["posting_id"]): r for r in csv.DictReader(open(ROOT / "labels/labels.csv", newline=""))}
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    prompt = claude.Prompt.load(paths.prompt(args.prompt))
    posts = {p.id: p for p in greenhouse.parse(RAW.read_bytes())}
    ask = claude_cli.make_ask()

    rows, raws = [], []
    for pid in ids:
        r = claude.judge(posts[pid], criteria, ask, prompt)
        hand = labels[pid]["label"]
        ok = r.verdict["status"] == "ok" and r.verdict["verdict"] == hand
        rows.append({"posting_id": pid, "title": posts[pid].title, "hand_label": hand,
                     "claude": r.verdict["verdict"] if r.verdict["status"] == "ok" else "error",
                     "pass": ok, "verdict": r.verdict})
        raws.append(r.raw)
        print(pid, hand, "->", rows[-1]["claude"], "PASS" if ok else "FAIL", flush=True)
    passed = sum(r["pass"] for r in rows)
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"{args.prompt}.{args.split}"
    (OUT / f"{name}.json").write_text(json.dumps(
        {"prompt": args.prompt, "split": args.split, "model": claude.MODEL, "via": "cli",
         "passed": passed, "total": len(rows), "rows": rows}, indent=1, ensure_ascii=False) + "\n")
    (OUT / f"{name}.raw.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in raws))
    print(f"{name}: {passed}/{len(rows)} match the hand labels")


if __name__ == "__main__":
    main()
