"""Sampling report data (Chapter 1): the same prompt, the same posting, several fresh calls.

Each call is a separate, stateless API request, so no call sees another's answer.
Held-out postings are refused. Every raw response is saved with its date.

Usage: .venv/bin/python -m experiment.sample --ids 1,2,3,4,5 [--n 4] [--prompt prompts/baseline.txt]
"""
import argparse
import collections
import pathlib

from jsagent.claude_judge import (DEFAULT_EFFORT, DEFAULT_MODEL, DEFAULT_PROMPT, MISSING_CREDENTIALS,
                                  credentials_present, make_claude_judge)
from jsagent.resume import load_resume

from .common import (EXP, RESUME, SNAPSHOT, ExperimentError, load_labels, load_postings, load_split,
                     new_run_dir, now_utc, prompt_fingerprint, stamp, write_json)

OUTCOMES = ("relevant", "not_relevant", "invalid", "unavailable")


def check_ids(ids, labels, split):
    heldout = set(split["heldout"])
    if leaked := [i for i in ids if i in heldout]:
        raise ExperimentError(f"refusing held-out ids {leaked}: sampling them would leak results")
    if unlabeled := [i for i in ids if i not in labels]:
        raise ExperimentError(f"ids without a hand label: {unlabeled}")


def summarize(ids, calls, labels):
    rows = []
    for pid in ids:
        verdicts = [c["claude_verdict"] for c in calls if c["posting_id"] == pid]
        counts = collections.Counter(verdicts)
        modal, modal_n = counts.most_common(1)[0]
        hand = labels[pid]["label"].strip()
        rows.append({
            "posting_id": pid,
            "title": labels[pid]["title"],
            "hand_label": hand,
            "n": len(verdicts),
            "counts": {o: counts.get(o, 0) for o in OUTCOMES},
            "modal_verdict": modal,
            "agreement": modal_n / len(verdicts),
            "matches_hand_label": counts.get(hand, 0),
        })
    return rows


def run_sampling(ids, n, judge, postings, resume, labels, split, out_dir, config):
    check_ids(ids, labels, split)
    calls = []
    for pid in ids:
        for k in range(1, n + 1):
            result = judge(resume, postings[pid])
            record = {"posting_id": pid, "call": k, **result}
            write_json(out_dir / "raw" / f"{pid}_{k}.json", record)
            calls.append(record)
    summary = {**config, "ids": ids, "calls_per_posting": n, "postings": summarize(ids, calls, labels)}
    write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(to_markdown(summary))
    return summary


def to_markdown(summary):
    lines = [
        f"# Sampling data — {summary['started_at']}",
        "",
        f"Prompt `{summary['prompt']['path']}` (sha256 `{summary['prompt']['sha256'][:12]}`), "
        f"model `{summary['model']}`, effort `{summary['effort']}`, "
        f"{summary['calls_per_posting']} fresh calls per posting. Verdicts are JUDGMENTS, not facts.",
        "",
        "| posting | title | hand label | relevant | not_relevant | invalid | unavailable | modal | agreement | match hand |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in summary["postings"]:
        c = r["counts"]
        lines.append(f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {c['relevant']} | "
                     f"{c['not_relevant']} | {c['invalid']} | {c['unavailable']} | {r['modal_verdict']} | "
                     f"{r['agreement']:.2f} | {r['matches_hand_label']}/{r['n']} |")
    lines += ["", "Same verdict every time shows repeatability, not correctness; compare with the hand label."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", required=True, help="comma-separated dev posting ids")
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--prompt", default=str(DEFAULT_PROMPT))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default=DEFAULT_EFFORT)
    args = parser.parse_args(argv)
    if args.n < 4:
        raise SystemExit("the assignment asks for at least 4 calls per posting")
    if not credentials_present():
        raise SystemExit(MISSING_CREDENTIALS)
    ids = [int(x) for x in args.ids.split(",")]
    started = now_utc()
    try:
        labels, split = load_labels(), load_split()
        check_ids(ids, labels, split)
    except ExperimentError as exc:
        raise SystemExit(str(exc))
    config = {"started_at": started.isoformat(timespec="seconds"), "model": args.model,
              "effort": args.effort, "prompt": prompt_fingerprint(args.prompt),
              "snapshot": SNAPSHOT.name}
    out_dir = new_run_dir(EXP / "sampling", f"{stamp(started)}_{pathlib.Path(args.prompt).stem}")
    judge = make_claude_judge(args.model, args.effort, args.prompt)
    summary = run_sampling(ids, args.n, judge, load_postings(), load_resume(RESUME), labels, split,
                           out_dir, config)
    print((out_dir / "summary.md").read_text())
    print(f"raw responses and summary in {out_dir}")
    if any(r["counts"]["unavailable"] for r in summary["postings"]):
        print("WARNING: some calls were unavailable; see claude_reason in the raw files")


if __name__ == "__main__":
    main()
