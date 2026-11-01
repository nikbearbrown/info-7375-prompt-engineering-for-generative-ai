"""Prompt experiment: rule judge plus Claude judge (baseline and revised) on one frozen split.

    python3 -m experiments.run_experiment --split dev
    python3 -m experiments.run_experiment --split heldout   # refused until experiments/results_dev.md exists

The split comes from LABEL_SET.md, the postings from the saved live response, and the hand
labels from labels/HAND_LABELS.md. Every Claude call goes through js1.claude_judge (pinned
model, tools disabled). Evidence goes to evidence/experiment/<split>/<UTC stamp>/.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from js1 import claude_judge, rule_judge
from js1.persona import PersonaRefused, load_persona

ROOT = Path(__file__).resolve().parent.parent
LABEL_SET = ROOT / "LABEL_SET.md"
HAND_LABELS = ROOT / "labels" / "HAND_LABELS.md"
RAW = ROOT / "evidence" / "raw" / "2026-10-30T23-59-22Z.json"
EVIDENCE = ROOT / "evidence" / "experiment"
RESULTS_DIR = ROOT / "experiments"
SPLIT_NAMES = {"dev": "development", "heldout": "held-out"}
PROMPTS = ("baseline", "revised")

EXIT_OK = 0
EXIT_PERSONA = 1
EXIT_HELDOUT_BEFORE_DEV = 7


def read_split(label_set_path, split):
    """Posting ids in the frozen split, in LABEL_SET.md order (sorted by id).

    Table rows look like: | # | posting id | title | split |
    """
    wanted = SPLIT_NAMES[split]
    ids = []
    for line in Path(label_set_path).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 4 and re.fullmatch(r"\d+", cells[1]) and cells[3] == wanted:
            ids.append(int(cells[1]))
    return ids


def read_hand_labels(path):
    labels = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 4 and re.fullmatch(r"\d+", cells[0]):
            labels[int(cells[0])] = cells[1]
    return labels


def claude_verdict(result):
    return result["verdict"] if result.get("status") == "valid" else "invalid"


def passes(result, hand_label):
    """Pass = status valid AND verdict equals the hand label. An invalid result is a fail."""
    return result.get("status") == "valid" and result.get("verdict") == hand_label


def score_row(posting, hand_label, record, baseline, revised):
    return {
        "posting_id": posting["id"],
        "title": posting["title"].strip(),
        "hand_label": hand_label,
        "rule_verdict": record["verdict"],
        "rule_pass": record["verdict"] == hand_label,
        "baseline_verdict": claude_verdict(baseline),
        "baseline_pass": passes(baseline, hand_label),
        "revised_verdict": claude_verdict(revised),
        "revised_pass": passes(revised, hand_label),
    }


def summarize(rows, results):
    n = len(rows)
    invalid = {p: sum(1 for r in results[p] if r.get("status") != "valid") for p in PROMPTS}
    return {
        "n": n,
        "baseline": sum(r["baseline_pass"] for r in rows),
        "revised": sum(r["revised_pass"] for r in rows),
        "rule": sum(r["rule_pass"] for r in rows),
        "invalid_baseline": invalid["baseline"],
        "invalid_revised": invalid["revised"],
        "invalid_total": invalid["baseline"] + invalid["revised"],
    }


def summary_lines(split, s):
    return [
        f"split: {split} ({s['n']} postings)",
        f"baseline {s['baseline']}/{s['n']}, revised {s['revised']}/{s['n']}, rule {s['rule']}/{s['n']}",
        f"invalid results: {s['invalid_total']} (baseline {s['invalid_baseline']}, revised {s['invalid_revised']})",
    ]


def write_results_md(path, split, stamp, evidence_dir, rows, s):
    pf = lambda ok: "pass" if ok else "fail"
    table = "\n".join(
        f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {r['rule_verdict']} | {r['baseline_verdict']} "
        f"| {r['revised_verdict']} | {pf(r['baseline_pass'])} | {pf(r['revised_pass'])} |"
        for r in rows
    )
    rel = evidence_dir.relative_to(ROOT) if evidence_dir.is_relative_to(ROOT) else evidence_dir
    Path(path).write_text(f"""# Prompt experiment results: {SPLIT_NAMES[split]} split

- **Run:** {stamp} (UTC)
- **Model:** {claude_judge.MODEL}, one call per posting per prompt (plus at most one retry on an invalid reply)
- **Postings:** real postings from `{RAW.relative_to(ROOT)}`, split frozen in `LABEL_SET.md`
- **Hand labels:** `labels/HAND_LABELS.md`
- **Evidence:** `{rel}/`
- **Scoring:** a prompt passes on a posting when its result is valid and its verdict equals my hand label; an invalid result is a fail.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
{table}

- **Baseline:** {s['baseline']}/{s['n']}
- **Revised:** {s['revised']}/{s['n']}
- **Rule:** {s['rule']}/{s['n']}
- **Invalid results:** {s['invalid_total']} (baseline {s['invalid_baseline']}, revised {s['invalid_revised']})
""", encoding="utf-8")


def run(split, runner=claude_judge.run_claude, stamp=None, label_set=LABEL_SET, hand_labels=HAND_LABELS,
        raw=RAW, evidence_root=EVIDENCE, results_dir=RESULTS_DIR, resume=None, profile=None,
        out=sys.stdout, err=sys.stderr):
    results_dir = Path(results_dir)
    if split == "heldout" and not (results_dir / "results_dev.md").exists():
        print("refusing --split heldout: run the dev split first (experiments/results_dev.md does not exist).",
              file=err)
        return EXIT_HELDOUT_BEFORE_DEV
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    ids = read_split(label_set, split)
    labels = read_hand_labels(hand_labels)
    jobs = {j["id"]: j for j in json.loads(Path(raw).read_text(encoding="utf-8"))["jobs"]}
    missing = [i for i in ids if i not in jobs or i not in labels]
    if missing:
        raise ValueError(f"postings missing from the raw response or hand labels: {missing}")

    evidence_dir = Path(evidence_root) / split / stamp
    evidence_dir.mkdir(parents=True, exist_ok=True)
    records, results, rows = [], {p: [] for p in PROMPTS}, []
    for pid in ids:
        posting = jobs[pid]
        record = rule_judge.judge(posting, resume, profile)
        records.append(record)
        by_prompt = {}
        for prompt in PROMPTS:
            by_prompt[prompt] = claude_judge.judge(posting, resume, profile, prompt_name=prompt, runner=runner,
                                                   evidence_dir=evidence_dir, stamp=stamp)
            results[prompt].append(by_prompt[prompt])
        rows.append(score_row(posting, labels[pid], record, by_prompt["baseline"], by_prompt["revised"]))
        print(f"  {pid}  hand={labels[pid]}  rule={record['verdict']}  "
              f"baseline={rows[-1]['baseline_verdict']}  revised={rows[-1]['revised_verdict']}", file=out)

    (evidence_dir / "rule_records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    s = summarize(rows, results)
    (evidence_dir / "summary.json").write_text(json.dumps({"split": split, "stamp": stamp,
                                                           "model": claude_judge.MODEL, "rows": rows,
                                                           "summary": s}, indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    results_path = results_dir / f"results_{split}.md"
    write_results_md(results_path, split, stamp, evidence_dir, rows, s)
    for line in summary_lines(split, s):
        print(line, file=out)
    print(f"results: {results_path}", file=out)
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(prog="experiments.run_experiment")
    parser.add_argument("--split", choices=sorted(SPLIT_NAMES), required=True)
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(claude_judge.RESUME, claude_judge.PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return EXIT_PERSONA
    return run(args.split, resume=resume, profile=profile)


if __name__ == "__main__":
    sys.exit(main())
