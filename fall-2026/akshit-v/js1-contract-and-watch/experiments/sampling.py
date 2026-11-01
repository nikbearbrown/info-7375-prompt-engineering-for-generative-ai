"""Sampling report (Chapter 1): ask Claude the same contract about each posting N times,
each in a fresh conversation, and record every verdict.

Run the calls (results saved, no verdicts printed, so hand labels can stay blind):
    python experiments/sampling.py run --raw evidence/raw/<file>.json --ids ID1 ID2 ID3 ID4 ID5 --n 4
Build the report once experiments/sampling_hand_labels.csv is filled in:
    python experiments/sampling.py report experiments/results/sampling_<stamp>.json
"""
import argparse
import csv
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent import claude_judge, rule  # noqa: E402
from agent.config import JUDGE_PROMPT, ROOT  # noqa: E402
from agent.postings import load_postings  # noqa: E402
from agent.resume import load_resume  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
HAND_LABELS = HERE / "sampling_hand_labels.csv"


def run(args) -> None:
    resume = load_resume(ROOT / "data" / "resume_jack_spencer.json")
    by_id = {p["id"]: p for p in load_postings(args.raw)}
    postings = [by_id[i] for i in args.ids]
    template = Path(args.prompt).read_text(encoding="utf-8")
    jobs = [(p, k) for p in postings for k in range(args.n)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        replies = list(pool.map(lambda job: claude_judge.judge(job[0], resume, template), jobs))
    out = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "raw": Path(args.raw).as_posix(), "prompt": Path(args.prompt).as_posix(), "n": args.n,
        "postings": [{"id": p["id"], "title": p["title"],
                      "rule_verdict": rule.judge(p, resume)["verdict"],
                      "replies": [r for (q, _), r in zip(jobs, replies) if q["id"] == p["id"]]}
                     for p in postings],
    }
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"sampling_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"saved {len(replies)} replies to {path} (verdicts not printed; fill {HAND_LABELS.name} first)")


def report(args) -> None:
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    with HAND_LABELS.open(encoding="utf-8") as f:
        hand = {int(r["id"]): r["hand_label"].strip() for r in csv.DictReader(f)}
    if any(not hand.get(p["id"]) for p in data["postings"]):
        sys.exit(f"fill hand_label for every posting in {HAND_LABELS} first")
    lines = ["| id | title | hand label | rule | Claude verdicts (in call order) | relevant / not / invalid | majority = hand? |",
             "|---|---|---|---|---|---|---|"]
    for p in data["postings"]:
        vs = [r["verdict"] if r["valid"] else "INVALID" for r in p["replies"]]
        c = Counter(vs)
        top, top_n = c.most_common(1)[0]
        majority = top if top_n > len(vs) / 2 else "no majority"
        lines.append(f"| {p['id']} | {p['title']} | {hand[p['id']]} | {p['rule_verdict']} | {', '.join(vs)} | "
                     f"{c['relevant']} / {c['not_relevant']} / {c['INVALID']} | "
                     f"{'yes' if majority == hand[p['id']] else 'no'} |")
    print("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--raw", type=Path, required=True)
    r.add_argument("--ids", type=int, nargs="+", required=True)
    r.add_argument("--n", type=int, default=4)
    r.add_argument("--prompt", type=Path, default=JUDGE_PROMPT)
    rep = sub.add_parser("report")
    rep.add_argument("results", type=Path)
    args = ap.parse_args()
    run(args) if args.cmd == "run" else report(args)


if __name__ == "__main__":
    main()
