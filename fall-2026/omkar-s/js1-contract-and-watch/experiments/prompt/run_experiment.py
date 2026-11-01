"""Run one prompt contract over one split, one fresh `claude -p` call per posting.

    python3 -m experiments.prompt.run_experiment --prompt prompts/baseline.txt --split dev
    python3 -m experiments.prompt.lock          # freeze prompts + labels, then:
    python3 -m experiments.prompt.run_experiment --prompt prompts/baseline.txt --split heldout

Held-out runs refuse to start unless lock.json exists and the prompt and label files
still hash to what was locked, so nothing can be tuned after the held-out set is seen."""
import argparse
import json
import os
import sys

from experiments.common import EXP, LABELS, RESUME, ROOT, append_jsonl, load_labels, load_postings, sha256
from jsagent import claude_judge, persona, rule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--split", choices=["dev", "heldout"], required=True)
    a = ap.parse_args()
    labels = load_labels()
    ids = [i for i, r in labels.items() if r["split"] == a.split]
    missing = [i for i, r in labels.items() if r["omkar_label"].strip() not in ("relevant", "not_relevant")]
    if missing:
        sys.exit(f"refusing: {len(missing)} postings have no hand label yet (labels must come first)")
    if a.split == "heldout":
        lock_path = os.path.join(EXP, "lock.json")
        if not os.path.exists(lock_path):
            sys.exit("refusing: run `python3 -m experiments.prompt.lock` after the dev runs first")
        with open(lock_path) as f:
            lock = json.load(f)
        for path, digest in lock["sha256"].items():
            if sha256(os.path.join(ROOT, path)) != digest:
                sys.exit(f"refusing: {path} changed since it was locked")
    name = os.path.splitext(os.path.basename(a.prompt))[0]
    out = os.path.join(EXP, "results", f"{name}-{a.split}.jsonl")
    if os.path.exists(out):
        sys.exit(f"refusing: {out} exists; one run per prompt per split")
    with open(a.prompt, encoding="utf-8") as f:
        template = f.read()
    postings, resume = load_postings(), persona.load(RESUME)
    raw_dir = os.path.join(EXP, "results", "claude-raw")
    for pid in ids:
        j = claude_judge.judge(postings[pid], resume, template, raw_dir=raw_dir, tag=f"{name}-{a.split}-")
        row = {"posting_id": pid, "prompt": name, "prompt_sha256": sha256(a.prompt), "split": a.split,
               "hand_label": labels[pid]["omkar_label"].strip(),
               "rule_verdict": rule.judge(postings[pid], resume)["verdict"], **j}
        row["pass"] = j["status"] == "valid" and j["verdict"] == row["hand_label"]
        append_jsonl(out, row)
        print(f"{pid} {j['status']:8} claude={j['verdict']} hand={row['hand_label']} pass={row['pass']}")


if __name__ == "__main__":
    main()
