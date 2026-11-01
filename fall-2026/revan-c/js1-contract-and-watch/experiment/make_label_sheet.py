"""Create experiment/labels.csv for hand labeling. Shows no agent or Claude verdicts.

Default selection: every snapshot posting whose title contains a résumé target_titles phrase
(the same lowercase substring test as rule condition 1). Pass --ids to use your own selection.

Usage: .venv/bin/python -m experiment.make_label_sheet [--ids 1,2,3]
"""
import argparse
import csv
import json

from .common import LABEL_COLUMNS, LABELS, RESUME, SNAPSHOT, ExperimentError, load_postings


def select_title_matches(postings, target_titles):
    targets = [t.lower() for t in target_titles]
    return sorted(pid for pid, p in postings.items() if any(t in p["title"].lower() for t in targets))


def write_sheet(path, postings, ids, source):
    if path.exists():
        raise ExperimentError(f"{path} already exists; refusing to overwrite labels")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_COLUMNS)
        writer.writeheader()
        for pid in ids:
            p = postings[pid]
            writer.writerow({"posting_id": pid, "title": p["title"].strip(),
                             "location": p["location"]["name"], "source": source})


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="comma-separated posting ids (default: title-match selection)")
    args = parser.parse_args(argv)
    postings = load_postings()
    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
        missing = [i for i in ids if i not in postings]
        if missing:
            raise SystemExit(f"ids not in snapshot: {missing}")
    else:
        ids = select_title_matches(postings, json.loads(RESUME.read_text())["target_titles"])
    try:
        write_sheet(LABELS, postings, ids, SNAPSHOT.name)
    except ExperimentError as exc:
        raise SystemExit(str(exc))
    print(f"wrote {LABELS} with {len(ids)} postings and empty label columns")


if __name__ == "__main__":
    main()
