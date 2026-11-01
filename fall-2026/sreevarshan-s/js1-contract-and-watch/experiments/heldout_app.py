"""Held-out split run by hand in the Claude app, because the CLI hit its usage limit.

    python3 -m experiments.heldout_app build
    python3 -m experiments.heldout_app score

No Claude call and no network. `build` writes, for each held-out posting in LABEL_SET.md,
experiments/heldout_app/prompts/<posting_id>-baseline.txt and <posting_id>-revised.txt, built with
js1.claude_judge.build_prompt exactly as the judge would send them. `score` reads the saved replies,
experiments/heldout_app/replies/<posting_id>-baseline.txt and <posting_id>-revised.txt, checks each with
js1.claude_judge.validate (the judge's own validator), and scores them against labels/HAND_LABELS.md with
the dev run's pass rule: valid and verdict equal to the hand label. An invalid or missing reply is a fail.
The rule judge is run on the same postings for comparison. Writes experiments/results_heldout_app.md.
"""

import argparse
import json
import sys
from pathlib import Path

from experiments.run_experiment import HAND_LABELS, LABEL_SET, PROMPTS, RAW, passes, read_hand_labels, read_split
from js1 import claude_judge, rule_judge
from js1.persona import PersonaRefused, load_persona

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "experiments" / "heldout_app"
RESULTS = ROOT / "experiments" / "results_heldout_app.md"

EXIT_OK = 0
EXIT_PERSONA = 1


def _postings(raw, label_set, ids=None):
    ids = list(ids) if ids is not None else read_split(label_set, "heldout")
    jobs = {j["id"]: j for j in json.loads(Path(raw).read_text(encoding="utf-8"))["jobs"]}
    missing = [i for i in ids if i not in jobs]
    if missing:
        raise ValueError(f"postings missing from {raw}: {missing}")
    return [jobs[i] for i in ids]


def build(resume, profile, raw=RAW, label_set=LABEL_SET, out_dir=APP_DIR / "prompts", ids=None,
          prompts_dir=claude_judge.PROMPTS_DIR):
    candidate = claude_judge.candidate_fields(resume, profile)
    texts = {p: (Path(prompts_dir) / f"{p}.txt").read_text(encoding="utf-8") for p in PROMPTS}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for posting in _postings(raw, label_set, ids):
        for prompt in PROMPTS:
            path = out_dir / f"{posting['id']}-{prompt}.txt"
            path.write_text(claude_judge.build_prompt(texts[prompt], posting, candidate), encoding="utf-8")
            written.append(path)
    return written


def check(reply_path, posting_id, allowed):
    """Return a result dict shaped like the judge's: status valid with verdict, invalid with error, or missing."""
    reply_path = Path(reply_path)
    if not reply_path.exists():
        return {"status": "missing", "error": f"{reply_path.name} not found"}
    try:
        parsed = claude_judge.validate(reply_path.read_text(encoding="utf-8"), posting_id, allowed)
    except claude_judge.InvalidReply as exc:
        return {"status": "invalid", "error": str(exc)}
    return {"status": "valid", "verdict": parsed["verdict"]}


def score(resume, profile, raw=RAW, label_set=LABEL_SET, hand_labels=HAND_LABELS, replies_dir=APP_DIR / "replies",
          results=RESULTS, ids=None):
    labels = read_hand_labels(hand_labels)
    allowed = claude_judge.citable_fields(claude_judge.candidate_fields(resume, profile))
    rows = []
    for posting in _postings(raw, label_set, ids):
        pid = posting["id"]
        if pid not in labels:
            raise ValueError(f"posting {pid} has no hand label in {hand_labels}")
        row = {"posting_id": pid, "title": posting["title"].strip(), "hand_label": labels[pid],
               "rule_verdict": rule_judge.judge(posting, resume, profile)["verdict"]}
        row["rule_pass"] = row["rule_verdict"] == labels[pid]
        for prompt in PROMPTS:
            result = check(Path(replies_dir) / f"{pid}-{prompt}.txt", pid, allowed)
            row[prompt] = result
            row[f"{prompt}_pass"] = passes(result, labels[pid])
        rows.append(row)
    write_results_md(results, rows, replies_dir)
    return rows


def _shown(result):
    return result["verdict"] if result["status"] == "valid" else result["status"]


def write_results_md(path, rows, replies_dir):
    n = len(rows)
    pf = lambda ok: "pass" if ok else "fail"
    table = "\n".join(
        f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {r['rule_verdict']} | {_shown(r['baseline'])} "
        f"| {_shown(r['revised'])} | {pf(r['baseline_pass'])} | {pf(r['revised_pass'])} |"
        for r in rows
    )
    problems = [f"- {r['posting_id']} {p}: {r[p]['status']} ({r[p]['error']})"
                for r in rows for p in PROMPTS if r[p]["status"] != "valid"]
    count = lambda p, status: sum(1 for r in rows if r[p]["status"] == status)
    replies_rel = Path(replies_dir).relative_to(ROOT) if Path(replies_dir).is_relative_to(ROOT) else replies_dir
    Path(path).write_text(f"""# Prompt experiment results: held-out split, run by hand in the Claude app

- **Run:** 2026-10-31, run by me in the Claude app (incognito, Sonnet 4.6, web search off), one reply per prompt per posting, no retry.
- **Why the app:** the CLI held-out run hit the usage limit (commit `4a46925`).
- **Prompts:** `experiments/heldout_app/prompts/`, built with `js1.claude_judge.build_prompt`, byte for byte what the judge would send.
- **Replies:** `{replies_rel}/`, one reply per posting per prompt, saved by hand. There is no automatic retry in the app.
- **Validator:** `js1.claude_judge.validate`, unchanged from the dev run.
- **Hand labels:** `labels/HAND_LABELS.md`
- **Scoring:** a prompt passes on a posting when its reply is valid and its verdict equals my hand label; an invalid or missing reply is a fail.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
{table}

- **Baseline:** {sum(r['baseline_pass'] for r in rows)}/{n}
- **Revised:** {sum(r['revised_pass'] for r in rows)}/{n}
- **Rule:** {sum(r['rule_pass'] for r in rows)}/{n}
- **Invalid replies:** baseline {count('baseline', 'invalid')}, revised {count('revised', 'invalid')}
- **Missing replies:** baseline {count('baseline', 'missing')}, revised {count('revised', 'missing')}

## Invalid or missing replies

{chr(10).join(problems) if problems else "None."}
""", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="experiments.heldout_app")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="write experiments/heldout_app/prompts/<posting_id>-<prompt>.txt")
    sub.add_parser("score", help="score experiments/heldout_app/replies/ and write experiments/results_heldout_app.md")
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(claude_judge.RESUME, claude_judge.PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return EXIT_PERSONA
    if args.cmd == "build":
        for path in build(resume, profile):
            print(path.relative_to(ROOT))
        return EXIT_OK
    rows = score(resume, profile)
    n = len(rows)
    for p in PROMPTS:
        print(f"{p}: {sum(r[f'{p}_pass'] for r in rows)}/{n}")
    print(f"rule: {sum(r['rule_pass'] for r in rows)}/{n}")
    print(f"results: {RESULTS.relative_to(ROOT)}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
