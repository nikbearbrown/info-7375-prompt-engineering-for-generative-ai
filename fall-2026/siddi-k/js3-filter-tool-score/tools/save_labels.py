"""Save Siddi's sheet labels exactly as the page produced them, mapped to postings through the manifest.

Usage: python tools/save_labels.py --raw labels/sheet-results.raw.json --labelled-at "2026-11-25 ~23:30 ET"
The raw JSON (the page's results box) is kept byte-for-byte next to the mapped file."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import policy  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--labelled-at", required=True)
    a = ap.parse_args()
    raw = policy.check_read(a.raw).read_bytes()
    rows = json.loads(raw.decode("utf-8"))
    manifest = json.loads(policy.check_read("labels/sheet-manifest.json").read_text(encoding="utf-8"))
    by_n = {it["n"]: it for it in manifest["items"]}
    if sorted(r["n"] for r in rows) != sorted(by_n):
        raise SystemExit("the results do not cover exactly the sheet's items")
    missing = [r["n"] for r in rows if r["label"] not in ("relevant", "not_relevant")]
    if missing:
        raise SystemExit(f"items without a label: {missing}")
    out = []
    for r in sorted(rows, key=lambda r: r["n"]):
        it = by_n[r["n"]]
        out.append({"n": r["n"], "key": it["key"], "label": r["label"], "reason": r["reason"],
                    "labelled_by": "Siddi Kommuri", "labelled_at": a.labelled_at, "blind": True,
                    "sheet_items_sha256": manifest["items_shown_sha256"]})
    policy.write_bytes("labels/hand_labels.jsonl",
                       "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out).encode("utf-8"))
    print(f"saved {len(out)} labels; raw sha256 {hashlib.sha256(raw).hexdigest()}")
    print(f"relevant: {sum(x['label'] == 'relevant' for x in out)}, not_relevant: {sum(x['label'] == 'not_relevant' for x in out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
