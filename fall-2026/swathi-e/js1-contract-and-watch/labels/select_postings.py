"""Choose the 20 postings to hand-label and split them, reproducibly (no Claude, no network).

    python3 labels/select_postings.py

Source: the saved Oct 26 board response. The 20 are all postings that pass the
written rule (Revision 2) plus 12 drawn with random.Random(7375) from the pool
of postings whose title contains a check 1(a) word but which do not pass the
rule. Split, decided before labeling: the already-read rule-passing postings
all go to development; held-out is 10 drawn with random.Random(20261026) from
the 12 random postings; the other 2 go to development.
"""
import csv
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import persona  # noqa: E402
import rule  # noqa: E402
import watch  # noqa: E402

SOURCE = ROOT / "runs" / "raw" / "databricks_2026-10-26T10-20-47-0400.json"
SELECT_SEED = 7375
SPLIT_SEED = 20261026
RANDOM_COUNT = 12
HELD_OUT_COUNT = 10
SHEET_COLUMNS = ["posting_id", "title", "location", "link", "my_label", "my_reason"]


def choose(postings, targets):
    by_id = sorted(postings, key=lambda p: p["id"])
    passing = [p["id"] for p in by_id if rule.judge(p["title"], p["location"], targets)["verdict"] == rule.RELEVANT]
    pool = [p["id"] for p in by_id if p["id"] not in passing and rule.find_terms(p["title"], rule.ROLE_TERMS)]
    drawn = sorted(random.Random(SELECT_SEED).sample(pool, RANDOM_COUNT))
    held_out = sorted(random.Random(SPLIT_SEED).sample(drawn, HELD_OUT_COUNT))
    development = sorted(passing + [i for i in drawn if i not in held_out])
    return {"passing_rule": passing, "pool_size": len(pool), "random_drawn": drawn,
            "development": development, "held_out": held_out}


def main():
    body = SOURCE.read_bytes()
    postings = watch.parse_postings(body)
    chosen = choose(postings, persona.load_persona()[1])
    selection = {
        "source": watch._relative(SOURCE), "source_sha256": hashlib.sha256(body).hexdigest(),
        "postings_in_source": len(postings), "rule": "rule.py, CONTRACT.md Revision 2",
        "method": ("all postings that pass the written rule, plus 12 drawn with random.Random(7375).sample "
                   "from postings (sorted by id) whose title contains a check 1(a) word (rule.ROLE_TERMS, "
                   "whole word, case-insensitive) but that do not pass the rule"),
        "split_method": ("decided before labeling: the rule-passing postings, whose descriptions were already "
                         "read, all go to development; held_out is 10 drawn with random.Random(20261026).sample "
                         "from the 12 random postings; the remaining 2 go to development"),
        "select_seed": SELECT_SEED, "split_seed": SPLIT_SEED, **chosen,
    }
    (HERE / "selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    sheet = HERE / "LABELS.csv"
    if sheet.exists():
        print(f"{watch._relative(sheet)} already exists; not overwriting your labels.")
        return
    by_id = {p["id"]: p for p in postings}
    with sheet.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(SHEET_COLUMNS)
        for posting_id in sorted(chosen["development"] + chosen["held_out"]):
            p = by_id[posting_id]
            writer.writerow([p["id"], p["title"].strip(), p["location"], p["absolute_url"], "", ""])
    print(f"wrote {watch._relative(HERE / 'selection.json')} and {watch._relative(sheet)}")


if __name__ == "__main__":
    main()
