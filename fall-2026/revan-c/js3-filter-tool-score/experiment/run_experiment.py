"""Prompt experiment (Chapter 2): score one prompt on the dev or held-out set against hand labels.

Pass = Claude's verdict equals the hand label. An invalid or unavailable output is a fail,
counted separately. Held-out runs need --final, a committed and unedited prompt, and an
earlier dev run of the same prompt.

Usage:
  .venv/bin/python -m experiment.run_experiment --set dev --prompt prompts/baseline.txt
  .venv/bin/python -m experiment.run_experiment --set heldout --prompt prompts/revision-1.txt --final
"""
import argparse
import json
import pathlib

from jsagent.claude_judge import (DEFAULT_EFFORT, DEFAULT_MODEL, MISSING_CREDENTIALS, credentials_present,
                                  make_claude_judge)
from jsagent.resume import load_resume

from .common import (EXP, RESUME, SNAPSHOT, ExperimentError, load_labels, load_postings, load_split,
                     new_run_dir, now_utc, prompt_fingerprint, stamp, wilson, write_json)

RESULTS = EXP / "results"


def check_heldout_allowed(prompt_fp, final, results_dir=RESULTS):
    if not final:
        raise ExperimentError("held-out runs need --final: freeze the revision first")
    if prompt_fp["uncommitted_changes"] or not prompt_fp["last_commit"]:
        raise ExperimentError(f"{prompt_fp['path']} must be committed and unedited before a held-out run")
    stem = pathlib.Path(prompt_fp["path"]).stem
    dev_runs = [json.loads(p.read_text()) for p in pathlib.Path(results_dir).glob(f"*_dev_{stem}*/summary.json")]
    if not any(r["prompt"]["sha256"] == prompt_fp["sha256"] for r in dev_runs):
        raise ExperimentError(f"no dev run of this exact {stem} prompt yet; run --set dev first")


def score(ids, results, labels):
    rows, passes, invalid = [], 0, 0
    confusion = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for pid in ids:
        verdict, hand = results[pid]["claude_verdict"], labels[pid]["label"].strip()
        ok = verdict == hand
        passes += ok
        if verdict in ("invalid", "unavailable"):
            invalid += 1
        else:
            key = ("t" if ok else "f") + ("p" if verdict == "relevant" else "n")
            confusion[key] += 1
        rows.append({"posting_id": pid, "title": labels[pid]["title"], "hand_label": hand,
                     "claude_verdict": verdict, "pass": ok,
                     "claude_reason": results[pid].get("claude_reason", "")})
    n = len(ids)
    low, high = wilson(passes, n)
    return {"n": n, "passes": passes, "pass_rate": passes / n if n else 0.0,
            "wilson_95": [round(low, 3), round(high, 3)], "invalid_or_unavailable": invalid,
            "confusion_relevant_positive": confusion, "rows": rows}


def run_experiment(set_name, ids, judge, postings, resume, labels, out_dir, config):
    results = {}
    for pid in ids:
        result = judge(resume, postings[pid])
        results[pid] = result
        write_json(out_dir / "raw" / f"{pid}.json", {"posting_id": pid, **result})
    summary = {**config, "set": set_name, "ids": ids, **score(ids, results, labels)}
    write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(to_markdown(summary))
    return summary


def to_markdown(s):
    lines = [
        f"# {s['set']} set — prompt `{s['prompt']['path']}` — {s['started_at']}",
        "",
        f"sha256 `{s['prompt']['sha256'][:12]}`, model `{s['model']}`, effort `{s['effort']}`. "
        "Claude verdicts are JUDGMENTS, not facts.",
        "",
        f"**Pass rate: {s['passes']}/{s['n']}** (95% Wilson interval {s['wilson_95'][0]:.2f}–{s['wilson_95'][1]:.2f}); "
        f"invalid or unavailable: {s['invalid_or_unavailable']}; "
        f"confusion with relevant as positive: {s['confusion_relevant_positive']}",
        "",
        "| posting | title | hand label | Claude | pass |",
        "|---|---|---|---|---|",
    ]
    for r in s["rows"]:
        lines.append(f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {r['claude_verdict']} | "
                     f"{'yes' if r['pass'] else 'no'} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", choices=("dev", "heldout"), required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--final", action="store_true", help="required for the held-out set")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default=DEFAULT_EFFORT)
    args = parser.parse_args(argv)
    if not credentials_present():
        raise SystemExit(MISSING_CREDENTIALS)
    started = now_utc()
    fp = prompt_fingerprint(args.prompt)
    try:
        labels, split = load_labels(), load_split()
        if args.set == "heldout":
            check_heldout_allowed(fp, args.final)
    except ExperimentError as exc:
        raise SystemExit(str(exc))
    config = {"started_at": started.isoformat(timespec="seconds"), "model": args.model,
              "effort": args.effort, "prompt": fp, "snapshot": SNAPSHOT.name}
    out_dir = new_run_dir(RESULTS, f"{stamp(started)}_{args.set}_{pathlib.Path(args.prompt).stem}")
    judge = make_claude_judge(args.model, args.effort, args.prompt)
    run_experiment(args.set, split[args.set], judge, load_postings(), load_resume(RESUME), labels,
                   out_dir, config)
    print((out_dir / "summary.md").read_text())
    print(f"raw responses and summary in {out_dir}")


if __name__ == "__main__":
    main()
