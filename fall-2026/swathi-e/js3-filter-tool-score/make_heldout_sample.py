"""Draw the JS3 held-out sample from the 2026-11-19 baseline run (offline, reproducible).

    python3 make_heldout_sample.py

Follows HELDOUT-PLAN.md (commit 4cbb88c). Reads the raw responses of the saved
runs 2026-11-17 (to know which postings are not new) and 2026-11-19 (checked
against its trace). It never imports or runs the filter or the JS1 rule. With
the fixed seeds below it writes, once (never overwriting):
  heldout/selection.json  groups, seeds, pool sizes and method (open only after labeling)
  heldout/HELDOUT.csv     the blind sheet: row, board, posting id, title, location, reading
                          file; my_verdict, my_reason and how_judged left blank; rows shuffled
  heldout/read/*.txt      one reading file per posting: title, location and the full
                          description as plain text, from the exact saved raw response
If fewer than 5 new postings are eligible for Group A, it writes nothing and stops.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import re
import sys

import descriptions
import parsers

HERE = Path(__file__).resolve().parent
OLD_RUN = Path("runs/2026-11-17T21-47-06-167440-0500")
NEW_RUN = Path("runs/2026-11-19T17-31-47-142253-0500")
SEED_A, SEED_B, SHUFFLE_SEED = 20261119, 20261120, 20261121
GROUP_A_SIZE, GROUP_B_SIZE, GROUP_A_MIN = 10, 10, 5
GROUP_A_TERMS = ("new grad", "graduate", "early career", "entry level", "junior", "AI", "machine learning", "ML",
                 "data")
OUT = HERE / "heldout"


def _whole(term):
    body = r"[\s-]+".join(re.escape(w) for w in term.split())
    return re.compile(r"(?<!\w)" + body + r"(?!\w)", re.I)


GROUP_A = [_whole(t) for t in GROUP_A_TERMS]
INTERN = re.compile(r"(?<!\w)intern(?:s|ships?)?(?!\w)", re.I)


def in_group_a(title):
    return any(p.search(title) for p in GROUP_A) and not INTERN.search(title)


def load_run(run):
    """{(board, posting id): (posting, raw file, raw sha256)} for every ok board, checked against the trace."""
    trace = json.loads((HERE / run / "trace.json").read_text(encoding="utf-8"))
    out = {}
    for name, board in trace["boards"].items():
        if board["status"] != "ok":
            continue
        obs = [o for o in trace["trace"] if o["board"] == name and o["action"] in ("request", "retry")
               and o.get("status") == 200 and o.get("raw_file")][-1]
        raw = (HERE / obs["raw_file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == obs["sha256"], obs["raw_file"]
        for p in parsers.PARSERS[board["system"]](raw, include_description=True)[0]:
            out[(name, str(p["id"]))] = (p, obs["raw_file"], obs["sha256"])
    return out


def reading_text(board, posting, raw_file, raw_sha):
    return "\n".join([
        f"Title: {posting['title']}",
        f"Location: {posting['location']}",
        f"Board: {board}",
        f"Posting ID: {posting['id']}",
        f"Posting URL: {posting['url']}",
        f"Source: {raw_file} (sha256 {raw_sha}), saved LIVE run 2026-11-19 17:31 EST",
        "Description: the full description from that raw response, HTML converted to plain text",
        "(one line per paragraph, heading or list item); nothing removed or summarized.",
        "-" * 70,
        descriptions.html_to_text(posting["description_html"]),
        "",
    ])


def main():
    old, new_run = load_run(OLD_RUN), load_run(NEW_RUN)
    new = sorted(k for k in new_run if k not in old)
    per_board = {b: sum(k[0] == b for k in new) for b in sorted({k[0] for k in new_run})}
    eligible_a = [k for k in new if in_group_a(new_run[k][0]["title"])]
    print("new postings per board:", per_board, "| total:", len(new))
    print("eligible for Group A:", len(eligible_a))
    if len(eligible_a) < GROUP_A_MIN:
        print(f"fewer than {GROUP_A_MIN} eligible for Group A: stopping, nothing written")
        return 1

    group_a = (eligible_a if len(eligible_a) <= GROUP_A_SIZE
               else random.Random(SEED_A).sample(eligible_a, GROUP_A_SIZE))
    rest = [k for k in new if k not in set(group_a)]
    group_b = random.Random(SEED_B).sample(rest, GROUP_B_SIZE)
    chosen = [("A", k) for k in group_a] + [("B", k) for k in group_b]
    assert len({k for _, k in chosen}) == len(chosen)

    (OUT / "read").mkdir(parents=True, exist_ok=False)
    rows = []
    for _, (board, pid) in chosen:
        p, raw_file, raw_sha = new_run[(board, pid)]
        path = Path("heldout") / "read" / f"{board}-{pid}.txt"
        with open(HERE / path, "x", encoding="utf-8") as f:
            f.write(reading_text(board, p, raw_file, raw_sha))
        rows.append([board, pid, p["title"], p["location"], path.as_posix()])
    random.Random(SHUFFLE_SEED).shuffle(rows)

    sheet = io.StringIO()
    writer = csv.writer(sheet, lineterminator="\n")
    writer.writerow(["row", "board", "posting_id", "title", "location", "reading_file", "my_verdict", "my_reason",
                     "how_judged"])
    for i, row in enumerate(rows, 1):
        writer.writerow([i] + row + ["", "", ""])
    with open(OUT / "HELDOUT.csv", "x", encoding="utf-8") as f:
        f.write(sheet.getvalue())

    selection = {
        "note": "Group assignment for HELDOUT.csv. Open only after my labels are committed.",
        "plan": "HELDOUT-PLAN.md (commit 4cbb88c)",
        "runs": {"new": NEW_RUN.as_posix(), "not new if in": OLD_RUN.as_posix()},
        "seeds": {"group_a": SEED_A, "group_b": SEED_B, "shuffle": SHUFFLE_SEED},
        "group_a_rule": {"terms (whole word or phrase, case-insensitive)": list(GROUP_A_TERMS),
                         "excluded": "titles with intern, interns, internship or internships"},
        "method": ("New = (board, posting id) absent from the Nov 17 raw responses. Pools sorted by (board, posting "
                   "id). Group A: all eligible if 10 or fewer, else random.Random(20261119).sample(eligible, 10). "
                   "Group B: random.Random(20261120).sample(new postings not in Group A, 10). Rows A then B, "
                   "shuffled with random.Random(20261121). Script: make_heldout_sample.py."),
        "pool_sizes": {"new per board": per_board, "new total": len(new), "eligible for Group A": len(eligible_a),
                       "Group B pool": len(rest)},
        "groups": {"A": [{"board": b, "posting_id": i} for b, i in group_a],
                   "B": [{"board": b, "posting_id": i} for b, i in group_b]},
        "total": len(chosen),
    }
    with open(OUT / "selection.json", "x", encoding="utf-8") as f:
        json.dump(selection, f, indent=2)
    print(f"wrote {len(chosen)} reading files, heldout/HELDOUT.csv and heldout/selection.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
