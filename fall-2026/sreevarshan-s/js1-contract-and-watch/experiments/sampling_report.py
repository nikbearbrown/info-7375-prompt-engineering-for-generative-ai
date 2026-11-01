"""Results table for the sampling check, computed from the saved reply files. No Claude call, no network.

    python3 -m experiments.sampling_report

Prints the markdown table and the valid/invalid counts used in experiments/SAMPLING_REPORT.md.
Each reply is checked with experiments.sampling.check (the judge's own validator).
"""

import json
import sys
from pathlib import Path

from experiments import sampling
from experiments.run_experiment import HAND_LABELS, read_hand_labels
from js1 import claude_judge
from js1.persona import PersonaRefused, load_persona

REPLIES = sampling.SAMPLING_DIR / "replies"
RUNS = (1, 2, 3, 4)


def skills_count(text):
    """Number of skills_cited entries, or None when the reply is not a JSON object with a list there."""
    try:
        data = json.loads(text.strip())
    except ValueError:
        return None
    cited = data.get("skills_cited") if isinstance(data, dict) else None
    return len(cited) if isinstance(cited, list) else None


def split_label(verdicts):
    valid = [v for v in verdicts if v in claude_judge.VERDICTS]
    rel, notrel = valid.count("relevant"), valid.count("not relevant")
    invalid = len(verdicts) - len(valid)
    return f"{notrel}-{rel} (not relevant-relevant)" + (f", {invalid} invalid" if invalid else "")


def table(resume, profile, replies=REPLIES, raw=sampling.RAW, hand_labels=HAND_LABELS):
    jobs = {j["id"]: j for j in json.loads(Path(raw).read_text(encoding="utf-8"))["jobs"]}
    labels = read_hand_labels(hand_labels)
    rows, invalid = [], []
    for pid in sampling.POSTING_IDS:
        verdicts, skills = [], []
        for n in RUNS:
            path = Path(replies) / f"{pid}-{n}.txt"
            status, detail = sampling.check(path, resume, profile)
            verdicts.append(detail if status == "valid" else "invalid")
            if status != "valid":
                invalid.append((path.name, detail))
            count = skills_count(path.read_text(encoding="utf-8"))
            skills.append("?" if count is None else str(count))
        valid = sum(v != "invalid" for v in verdicts)
        rows.append(f"| {pid} | {jobs[pid]['title'].strip()} | {labels[pid]} | {' / '.join(verdicts)} "
                    f"| {split_label(verdicts)} | {valid}/{len(RUNS)} | {' / '.join(skills)} |")
    total = len(sampling.POSTING_IDS) * len(RUNS)
    lines = ["| posting_id | title | my hand label | verdicts, runs 1-4 | split | valid | skills cited, runs 1-4 |",
             "|---|---|---|---|---|---|---|", *rows, "",
             f"- **Total valid:** {total - len(invalid)}/{total}",
             f"- **Total invalid:** {len(invalid)}/{total}"]
    lines += [f"  - `{name}`: {reason}" for name, reason in invalid]
    return "\n".join(lines)


def main():
    try:
        resume, profile = load_persona(claude_judge.RESUME, claude_judge.PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return 1
    print(table(resume, profile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
