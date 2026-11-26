"""Build the deduplicated corpus from every capture in raw/CAPTURES.json.

  .venv/bin/python -m js3.corpus          -> build/corpus.jsonl (derived, not committed)
                                             corpus/PROVENANCE.json (committed)

Identity is (provider, board, id); the latest capture's text wins (FILTER.md §4).
Content duplicates = same board + same normalized title + same normalized description.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from inherited.board import decode_body
from inherited.providers import PROVIDERS
from inherited.rules import html_to_text, normalize

from .text import readable

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build" / "corpus.jsonl"
PROVENANCE = ROOT / "corpus" / "PROVENANCE.json"


def load_captures():
    return json.loads((ROOT / "raw" / "CAPTURES.json").read_text())["captures"]


def read_capture(cap):
    body = gzip.decompress((ROOT / cap["file"]).read_bytes())
    sha = hashlib.sha256(body).hexdigest()
    if sha != cap["body_sha256"]:
        raise SystemExit(f"REFUSED: {cap['file']} body sha256 {sha} != recorded {cap['body_sha256']}")
    return body


def build(write=True):
    """write=False builds in memory only (used by the read-only tool server)."""
    caps = sorted(load_captures(), key=lambda c: c["captured_utc"])
    records, per_capture, unavailable = {}, [], []
    cross_dups = 0
    for cap in caps:
        body = read_capture(cap)
        if cap["status"] != 200:
            unavailable.append({"board": f"{cap['provider']}:{cap['board']}", "status": cap["status"],
                                "file": cap["file"], "answer": "I cannot tell what is on this board (FILTER.md §4)",
                                "body": decode_body(body)})
            per_capture.append({"file": cap["file"], "status": cap["status"], "postings": 0})
            continue
        jobs = PROVIDERS[cap["provider"]].parse(body)
        n_dup_here = 0
        for jid, job in jobs:
            key = f"{cap['provider']}:{cap['board']}:{jid}"
            rec = {
                "key": key, "provider": cap["provider"], "board": cap["board"], "id": jid,
                "title": job.get("title") or "",
                "text": job.get("content") or "",
                "location": (job.get("location") or {}).get("name"),
                "departments": [d.get("name") for d in job.get("departments") or [] if d.get("name")],
                "url": job.get("absolute_url"),
            }
            if key in records:
                n_dup_here += 1
                prev = records[key]
                rec["first_seen"] = prev["first_seen"]
                rec["seen_in"] = prev["seen_in"] + [cap["file"]]
                rec["text_changed_since_first_seen"] = prev["text_changed_since_first_seen"] or (
                    prev["title"] != rec["title"] or prev["text"] != rec["text"])
            else:
                rec["first_seen"] = cap["captured_utc"]
                rec["seen_in"] = [cap["file"]]
                rec["text_changed_since_first_seen"] = False
            rec["last_seen"] = cap["captured_utc"]
            records[key] = rec
        cross_dups += n_dup_here
        per_capture.append({"file": cap["file"], "status": 200, "board": f"{cap['provider']}:{cap['board']}",
                            "captured_utc": cap["captured_utc"], "postings": len(jobs),
                            "already_seen_in_earlier_capture": n_dup_here})

    # Content-duplicate groups, and the readable-text equivalence check.
    groups = defaultdict(list)
    missing_desc, missing_title, mismatch = [], [], []
    for key, rec in sorted(records.items()):
        rd = readable(rec["text"])
        if normalize(rd) != normalize(html_to_text(rec["text"])):
            mismatch.append(key)
        nt, nd = normalize(rec["title"]), normalize(rd)
        if not nt:
            missing_title.append(key)
        if not nd:
            missing_desc.append(key)
        h = hashlib.sha1(f"{rec['board']}\x00{nt}\x00{nd}".encode()).hexdigest()[:12]
        groups[h].append(key)
    if mismatch:
        raise SystemExit(f"readable() disagrees with inherited html_to_text on {len(mismatch)} postings: {mismatch[:3]}")
    for h, keys in groups.items():
        for k in keys:
            records[k]["dup_group"] = h
            records[k]["dup_group_size"] = len(keys)

    if not write:
        return records, None
    BUILD.parent.mkdir(exist_ok=True)
    with BUILD.open("w", encoding="utf-8") as f:
        for key in sorted(records):
            f.write(json.dumps(records[key], ensure_ascii=False, sort_keys=True) + "\n")

    by_board = Counter(r["board"] for r in records.values())
    multi = {h: k for h, k in groups.items() if len(k) > 1}
    prov = {
        "built_from": "raw/CAPTURES.json (every body sha256 re-verified at build time)",
        "captures": per_capture,
        "unavailable_boards": unavailable,
        "unique_postings": len(records),
        "unique_postings_by_board": dict(sorted(by_board.items())),
        "same_identity_in_two_captures": cross_dups,
        "only_in_2026-10-30_capture (closed by 2026-11-10)": sum(
            1 for r in records.values() if r["last_seen"].startswith("2026-10-30")),
        "text_changed_between_captures": sum(r["text_changed_since_first_seen"] for r in records.values()),
        "content_duplicate_groups": len(groups),
        "groups_with_more_than_one_posting": len(multi),
        "postings_in_multi_posting_groups": sum(len(k) for k in multi.values()),
        "largest_group_size": max((len(k) for k in groups.values()), default=0),
        "missing_title_after_normalization": missing_title,
        "missing_description_after_normalization": missing_desc,
    }
    PROVENANCE.parent.mkdir(exist_ok=True)
    PROVENANCE.write_text(json.dumps(prov, indent=1, ensure_ascii=False) + "\n")
    return records, prov


def load_corpus():
    if not BUILD.exists():
        build()
    with BUILD.open(encoding="utf-8") as f:
        return {r["key"]: r for r in map(json.loads, f)}


if __name__ == "__main__":
    _, p = build()
    print(json.dumps({k: v for k, v in p.items() if k != "unavailable_boards"}, indent=1)[:3000])
    sys.exit(0)
