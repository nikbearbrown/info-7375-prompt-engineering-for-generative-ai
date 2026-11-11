"""The outcome check from GATE.md, separate from the controller.

It reads only the saved raw responses (raw/*.body and the sidecar that records each body's url,
HTTP status and sha256). It never reads report.json or trace.jsonl, and it does its own JSON
counting instead of reusing agent2.providers, so a parsing bug there cannot hide here.

Flags (thresholds from GATE.md, amendment 2026-11-10):
  zero-postings    a board whose final HTTP 200 raw response has 0 postings
  cross-system     a company with 0 postings on one system and at least 1 on another
  sha256-mismatch  a saved body that no longer matches its recorded sha256
  unreadable       an HTTP 200 body this check cannot count (not JSON, no jobs list)
  total-mismatch   a Greenhouse body whose meta.total differs from its jobs list

    python -m agent2.check out/runs/<run>
"""
import hashlib
import json
import sys
from pathlib import Path


def count_postings(body):
    """(count, greenhouse meta.total or None); count is None if the body cannot be counted."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None, None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return None, None
    meta = data.get("meta")
    total = meta.get("total") if isinstance(meta, dict) else None
    return len(data["jobs"]), total


def check_run(run_dir):
    raw = Path(run_dir) / "raw"
    final = {}
    for meta_path in sorted(raw.glob("*.meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        key = (meta["system"], meta["board"])
        if key not in final or meta["step"] > final[key]["step"]:
            final[key] = meta

    flags, boards = [], []
    for (system, board), meta in sorted(final.items()):
        name = f"{system}:{board}"
        body = (raw / meta["file"]).read_bytes()
        sha_ok = hashlib.sha256(body).hexdigest() == meta["sha256"]
        if not sha_ok:
            flags.append({"kind": "sha256-mismatch", "board": name})
        postings = None
        if meta["http_status"] == 200:
            postings, total = count_postings(body)
            if postings is None:
                flags.append({"kind": "unreadable", "board": name})
            elif postings == 0:
                flags.append({"kind": "zero-postings", "board": name})
            if postings is not None and system == "greenhouse" and total is not None and total != postings:
                flags.append({"kind": "total-mismatch", "board": name, "total": total, "jobs": postings})
        boards.append({"system": system, "board": board, "company": meta.get("company") or board,
                       "http_status": meta["http_status"], "postings": postings, "sha256_ok": sha_ok,
                       "file": meta["file"]})

    by_company = {}
    for b in boards:
        if b["postings"] is not None:
            by_company.setdefault(b["company"], {})[b["system"]] = b["postings"]
    for company, counts in sorted(by_company.items()):
        if len(counts) > 1 and min(counts.values()) == 0 and max(counts.values()) >= 1:
            flags.append({"kind": "cross-system", "company": company, "counts": dict(sorted(counts.items()))})

    not_checked = [f"{b['system']}:{b['board']} (HTTP {b['http_status']})" for b in boards if b["postings"] is None
                   and b["http_status"] != 200]
    return {"run_dir": Path(run_dir).as_posix(), "verdict": "flags raised" if flags else "no flags",
            "flags": flags, "boards": boards, "not_counted": not_checked}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit("usage: python -m agent2.check out/runs/<run>")
    result = check_run(argv[0])
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
