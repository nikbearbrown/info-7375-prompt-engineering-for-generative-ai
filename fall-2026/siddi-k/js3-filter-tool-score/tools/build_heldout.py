"""The held-out set H for brief Step 2.4 (never used to choose a change):
- the 20 sheet items whose role is held_out_A / held_out_B (labels/sheet-manifest.json), from today's collection;
- JS1's 10 held-out Stripe postings, labelled by Siddi on 2026-10-31 (../js1-contract-and-watch/labels/), with their
  text from JS1's committed board raw/2026-10-31T10-48-38Z/board.json.
Writes data/heldout/postings.jsonl.gz, data/heldout/manifest.json and labels/heldout_js1_labels.jsonl (a copy)."""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import collect, policy  # noqa: E402

JS1 = policy.ROOT.parent / "js1-contract-and-watch"
JS1_BOARD = JS1 / "raw" / "2026-10-31T10-48-38Z" / "board.json"
JS1_LABELS = JS1 / "labels" / "hand_labels.jsonl"


def main() -> int:
    manifest = json.loads(policy.check_read("labels/sheet-manifest.json").read_text(encoding="utf-8"))
    run = manifest["collection_run"]
    today = {f"{p['board']}:{p['id']}": p for p in collect.load_postings(policy.ROOT / "data" / "collections" / run)}
    keys = [it["key"] for it in manifest["items"] if any(r.startswith("held_out") for r in it["roles"])]
    postings = [dict(today[k], heldout_source=f"sheet:{run}") for k in keys]

    board_bytes = JS1_BOARD.read_bytes()                     # outside this folder on purpose: JS1's own evidence
    board = json.loads(board_bytes.decode("utf-8"))
    labels = [json.loads(x) for x in JS1_LABELS.read_text(encoding="utf-8").splitlines() if x.strip()]
    js1_held = [x for x in labels if x["split"] == "held_out"]
    jobs = {j["id"]: j for j in board["jobs"]}
    for lab in js1_held:
        j = jobs[lab["posting_id"]]
        postings.append({"board": "stripe", "system": "greenhouse", "id": str(j["id"]), "title": j["title"].strip(),
                         "location": {"name": j["location"]["name"], "country": None, "remote": None, "other": []},
                         "text_format": "html", "text": j.get("content") or None,
                         "text_missing": None if j.get("content") else "empty", "url": j.get("absolute_url"),
                         "updated_at": j.get("updated_at"), "heldout_source": "js1:2026-10-31T10-48-38Z"})
    lines = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in postings).encode("utf-8")
    policy.write_bytes("data/heldout/postings.jsonl.gz", collect.gz(lines))
    policy.write_bytes("labels/heldout_js1_labels.jsonl", "".join(
        json.dumps({**x, "copied_from": "js1-contract-and-watch/labels/hand_labels.jsonl"}, ensure_ascii=False) + "\n"
        for x in js1_held).encode("utf-8"))
    info = {"postings": len(postings), "from_sheet": len(keys), "from_js1": len(js1_held),
            "postings_sha256": hashlib.sha256(lines).hexdigest(),
            "js1_board_sha256": hashlib.sha256(board_bytes).hexdigest(), "sheet_collection_run": run,
            "keys": [f"{p['board']}:{p['id']}" for p in postings]}
    policy.write_bytes("data/heldout/manifest.json", (json.dumps(info, indent=1) + "\n").encode("utf-8"))
    print(json.dumps({k: v for k, v in info.items() if k != "keys"}, indent=1))
    return 0


def load() -> list[dict]:
    with gzip.open(policy.check_read("data/heldout/postings.jsonl.gz"), "rt", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


if __name__ == "__main__":
    sys.exit(main())
