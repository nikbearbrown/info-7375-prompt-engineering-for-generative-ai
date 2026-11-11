"""How often each judge agrees with the labeling rule's explicit exclusions, from titles only.

    .venv/bin/python scripts/exclusion_agreement.py RESULTS_JSON ...

labels/LABELING_RULE.md says that, whatever the description, these are not relevant: Staff,
people managers, interns and PhD-required roles (Level), and sales, marketing and support roles
(Work). This script flags a posting as excluded when its TITLE alone contains one of the terms
below as a whole word (CONTRACT.md's matching). It reads no description, so it misses exclusions
stated only in the text and can wrongly flag a title.

For each excluded posting it reports the verdict of the hand label, the rule (record) and each
prompt in the given experiment results.json files, and counts how many are not_relevant, i.e.
agree with the exclusion. It writes nothing.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jobwatch.textmatch import whole_word_match  # noqa: E402

EXCLUSION_TERMS = {
    "level": ["Staff", "Manager", "Intern", "PhD"],
    "work": ["Account Executive", "Sales", "Marketing", "Support"],
}


def excluded_by(title):
    return [t for terms in EXCLUSION_TERMS.values() for t in terms if whole_word_match(t, title)]


def main(paths):
    labels = {r["posting_id"]: r for r in csv.DictReader(open("labels/labels.csv", encoding="utf-8"))}
    flagged = {pid: excluded_by(r["title"]) for pid, r in labels.items() if excluded_by(r["title"])}
    columns = {"hand label": {pid: labels[pid]["hand_label"] for pid in labels}}
    rule = {}
    for path in paths:
        results = json.loads(Path(path).read_bytes())
        name = f"{Path(results['prompt_path']).stem} ({results['set']})"
        columns[name] = {r["posting_id"]: (r["verdict"] if r["status"] == "accepted" else r["status"])
                         for r in results["postings"]}
        rule.update({r["posting_id"]: r["verdict"] for r in results["baseline_rule"]["postings"]})
    columns["rule (record)"] = rule

    print(f"Postings whose title alone hits an explicit exclusion: {len(flagged)} of {len(labels)}")
    print("| posting_id | title | terms | " + " | ".join(columns) + " |")
    print("|---" * (3 + len(columns)) + "|")
    for pid, terms in flagged.items():
        cells = [columns[c].get(pid, "—") for c in columns]
        print(f"| {pid} | {labels[pid]['title'].strip()} | {', '.join(terms)} | " + " | ".join(cells) + " |")
    print()
    for name, verdicts in columns.items():
        judged = [pid for pid in flagged if pid in verdicts]
        agree = sum(verdicts[pid] == "not_relevant" for pid in judged)
        print(f"{name}: not_relevant on {agree} of {len(judged)} title-excluded postings it judged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
