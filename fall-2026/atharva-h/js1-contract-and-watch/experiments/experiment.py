"""Sampling report and prompt experiment: write prompt files, then score raw Claude outputs.

    python3 experiments/experiment.py prepare --variant v1_baseline --set development
    python3 experiments/experiment.py prepare-sampling
    python3 experiments/experiment.py score --variant v1_baseline --set development
    python3 experiments/experiment.py sampling

Raw outputs are saved as experiments/.../raw/<id>.txt by whatever asked Claude (in this
submission, fresh Claude Code subagents). Scoring follows CONTRACT.md rule item 7.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import judge  # noqa: E402
import persona  # noqa: E402
import rule  # noqa: E402
from make_label_sheet import load_postings  # noqa: E402

RESUME = persona.load(os.path.join(ROOT, "persona", "resume.json"))
SAMPLING_IDS = (8275927, 4388567009, 8877421002, 5212408008, 8706824002)  # five development postings
SAMPLING_RUNS = 4
VERDICTS = ("relevant", "not_relevant", "needs_human")


def hand_labels():
    """Parse the Label column of LABELS.md; missing labels come back as None."""
    labels = {}
    with open(os.path.join(HERE, "label_pool", "LABELS.md"), encoding="utf-8") as f:
        for line in f:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6 and cells[2].isdigit():
                label = cells[4].strip("` ").lower() or None
                labels[int(cells[2])] = {"label": label, "check": cells[5] or None}
    return labels


def postings(subset=None):
    return [(s, job) for s, job in load_postings() if subset is None or s["set"] == subset]


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def prepare(variant, subset):
    base = os.path.join(HERE, "prompt", variant, subset)
    template = os.path.join(ROOT, "prompts", f"{variant}.txt")
    for s, job in postings(subset):
        _write(os.path.join(base, "prompts", f"{job['id']}.txt"), judge.build_prompt(template, job, RESUME))
    os.makedirs(os.path.join(base, "raw"), exist_ok=True)
    print(f"wrote {len(postings(subset))} prompts to {os.path.relpath(base, ROOT)}/prompts")


def prepare_sampling():
    jobs = {job["id"]: job for _, job in postings()}
    template = os.path.join(ROOT, "prompts", "v1_baseline.txt")
    for pid in SAMPLING_IDS:
        _write(os.path.join(HERE, "sampling", "prompts", f"{pid}.txt"), judge.build_prompt(template, jobs[pid], RESUME))
    os.makedirs(os.path.join(HERE, "sampling", "raw"), exist_ok=True)
    print(f"wrote {len(SAMPLING_IDS)} sampling prompts; save run k of posting p as sampling/raw/<p>_run<k>.txt")


def judged(path, job):
    """(verdict or 'invalid', errors) for one raw output file, or (None, ...) if it does not exist."""
    if not os.path.exists(path):
        return None, ["no output file"]
    with open(path, encoding="utf-8") as f:
        verdict, errors = judge.validate(f.read(), job, RESUME)
    return (verdict["verdict"] if verdict else "invalid"), errors


def outcome(claude, hand):
    """CONTRACT rule item 7. Returns 'pass', 'fail', or 'excluded' (counts toward coverage only)."""
    if claude in ("needs_human", "invalid", None):
        return "excluded"
    if hand == "needs_human":
        return "fail"
    return "pass" if claude == hand else "fail"


def score(variant, subset):
    labels = hand_labels()
    base = os.path.join(HERE, "prompt", variant, subset)
    rows, tally = [], collections.Counter()
    for s, job in postings(subset):
        hand = labels.get(job["id"], {}).get("label")
        claude, errors = judged(os.path.join(base, "raw", f"{job['id']}.txt"), job)
        record = rule.judge(job, RESUME)["verdict"]
        result = outcome(claude, hand) if hand else "unlabeled"
        tally[result] += 1
        rows.append({"id": job["id"], "title": job["title"], "hand": hand, "claude": claude, "rule": record,
                     "outcome": result, "errors": errors})
    committed = tally["pass"] + tally["fail"]
    summary = {
        "variant": variant, "set": subset, "total": len(rows), "committed": committed,
        "passes": tally["pass"], "fails": tally["fail"], "excluded": tally["excluded"], "unlabeled": tally["unlabeled"],
        "pass_rate": f"{tally['pass']}/{committed}" if committed else "n/a (nothing committed)",
        "coverage": f"{committed}/{len(rows)}",
        "invalid_outputs": sum(r["claude"] == "invalid" for r in rows),
        "claude_needs_human": sum(r["claude"] == "needs_human" for r in rows),
        "rule_agrees_with_hand": f"{sum(r['rule'] == r['hand'] for r in rows if r['hand'])}/{sum(1 for r in rows if r['hand'])}",
        "always_not_relevant_baseline": f"{sum(r['hand'] == 'not_relevant' for r in rows if r['hand'])}/"
                                        f"{sum(1 for r in rows if r['hand'])} (pass rate if every answer were not_relevant)",
    }
    _write(os.path.join(base, "score.json"), json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2))
    for r in rows:
        print(f"{r['id']:>12} hand={str(r['hand']):13} claude={str(r['claude']):13} rule={r['rule']:13} {r['outcome']:9} {r['title'][:45]}")


def sampling():
    labels = hand_labels()
    jobs = {job["id"]: job for _, job in postings()}
    rows = []
    for pid in SAMPLING_IDS:
        runs = [judged(os.path.join(HERE, "sampling", "raw", f"{pid}_run{k}.txt"), jobs[pid])
                for k in range(1, SAMPLING_RUNS + 1)]
        verdicts = [v for v, _ in runs]
        counts = collections.Counter(verdicts)
        modal, modal_n = counts.most_common(1)[0]
        rows.append({"id": pid, "title": jobs[pid]["title"], "runs": verdicts,
                     "errors": [e for _, e in runs if e],
                     "distinct": len(counts), "modal": modal, "modal_share": f"{modal_n}/{len(verdicts)}",
                     "hand": labels.get(pid, {}).get("label"), "rule": rule.judge(jobs[pid], RESUME)["verdict"]})
    _write(os.path.join(HERE, "sampling", "results.json"), json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    for r in rows:
        print(f"{r['id']:>12} runs={r['runs']} modal={r['modal']} {r['modal_share']} hand={r['hand']} rule={r['rule']}  {r['title'][:40]}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "score"):
        p = sub.add_parser(name)
        p.add_argument("--variant", required=True)
        p.add_argument("--set", required=True, choices=("development", "held_out"))
    sub.add_parser("prepare-sampling")
    sub.add_parser("sampling")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        prepare(args.variant, args.set)
    elif args.command == "score":
        score(args.variant, args.set)
    elif args.command == "prepare-sampling":
        prepare_sampling()
    else:
        sampling()


if __name__ == "__main__":
    main()
