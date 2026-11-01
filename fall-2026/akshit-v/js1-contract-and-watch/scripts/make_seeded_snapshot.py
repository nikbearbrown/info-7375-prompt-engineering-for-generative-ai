"""Build a SEEDED "earlier" snapshot from a real saved response.

Removes the N most recently created postings (highest Greenhouse ids) and saves the
rest as a new file labeled kind=seeded. Nothing is invented: every posting left in the
seeded file is a real posting copied from the source response.

    python scripts/make_seeded_snapshot.py evidence/raw/<stamp>_figma_live.json --remove 10
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.config import EVIDENCE_DIR  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("--remove", type=int, default=10)
    args = ap.parse_args()

    data = json.loads(args.source.read_text(encoding="utf-8"))
    removed = sorted((j["id"] for j in data["jobs"]), reverse=True)[:args.remove]
    data["jobs"] = [j for j in data["jobs"] if j["id"] not in set(removed)]
    if "meta" in data and isinstance(data["meta"], dict) and "total" in data["meta"]:
        data["meta"]["total"] = len(data["jobs"])

    out = EVIDENCE_DIR / args.source.name.replace("_live.json", "_SEEDED_earlier.json")
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    out.write_bytes(body)
    meta = {
        "kind": "seeded",
        "note": f"SEEDED earlier snapshot: real response {args.source.name} minus its "
                f"{args.remove} highest-id (most recently created) postings",
        "derived_from": args.source.as_posix(),
        "removed_ids": removed,
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"saved SEEDED snapshot: {out} ({len(data['jobs'])} postings, removed {removed})")


if __name__ == "__main__":
    main()
