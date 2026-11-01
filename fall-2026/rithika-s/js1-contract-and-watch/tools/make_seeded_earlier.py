"""Build a SEEDED 'earlier' board response from a real saved response.

Removes a documented set of postings so a second run against the real
response reports exactly those postings as new. Everything written here is
labeled SEEDED: constructed from real data, not a real earlier fetch.

Usage:
    python3 tools/make_seeded_earlier.py <real_raw.json> <out_dir>
"""
import json
import re
import sys
from pathlib import Path


def title_hits(title, keywords):
    text = title.lower()
    return any(
        re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text)
        for k in keywords
    )


def main():
    real_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(real_path.read_text(encoding="utf-8"))
    target = json.loads(
        Path("data/target.example.json").read_text(encoding="utf-8"))
    keywords = target["target_title_keywords"]

    jobs = sorted(data["jobs"], key=lambda j: j["id"])
    gate = [j for j in jobs if title_hits(j["title"], keywords)][:4]
    other = [j for j in jobs if not title_hits(j["title"], keywords)][:3]
    removed = gate + other
    removed_ids = {j["id"] for j in removed}

    earlier = dict(data)
    earlier["jobs"] = [j for j in data["jobs"] if j["id"] not in removed_ids]
    (out_dir / "earlier_SEEDED.json").write_text(
        json.dumps(earlier), encoding="utf-8")

    manifest = {
        "label": "SEEDED - constructed from a real saved response; "
                 "not a real earlier fetch",
        "source_raw": str(real_path),
        "selection": "first 4 by id whose title passes the title gate, "
                     "plus first 3 by id that do not",
        "removed": [{"id": j["id"], "title": j["title"]} for j in removed],
    }
    (out_dir / "SEEDED_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    for j in removed:
        print(j["id"], j["title"])


if __name__ == "__main__":
    main()
