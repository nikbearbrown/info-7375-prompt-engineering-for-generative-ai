"""Write labels/read/<posting_id>.txt for the 20 labeling postings (no Claude, no network).

    python3 labels/make_reading_files.py

Each file holds the posting's title, location and description exactly as the
judge's user message gives them, from the 12:40 ET Oct 26 saved detail
responses in runs/postings/.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import judge  # noqa: E402

SNAPSHOT = "2026-10-26T12-4"


def posting_text(posting):
    return "\n".join([f"title: {posting['title']}", f"location: {posting['location']}",
                      "description:", posting["description"]]) + "\n"


def main():
    selection = json.loads((HERE / "selection.json").read_text(encoding="utf-8"))
    out = HERE / "read"
    out.mkdir(exist_ok=True)
    for posting_id in sorted(selection["development"] + selection["held_out"]):
        [raw] = sorted((ROOT / "runs" / "postings").glob(f"databricks_job_{posting_id}_{SNAPSHOT}*-0400.json"))
        (out / f"{posting_id}.txt").write_text(posting_text(judge.load_posting(raw)), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.txt')))} files to labels/read/")


if __name__ == "__main__":
    main()
