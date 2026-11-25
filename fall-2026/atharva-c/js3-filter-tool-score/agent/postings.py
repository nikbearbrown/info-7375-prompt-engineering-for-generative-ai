"""Load a saved run's raw responses into one uniform list of postings.

This is data plumbing only: no relevance rules live here (those are in
FILTER.md and agent/filter.py). Every field the filter reads comes from here,
so FILTER.md > Expected sources documents exactly these fields.

Usage:
    python3 -m agent.postings evidence/run-20261123-185425Z   # prints a summary
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

FIELDS = ("uid", "board", "ats", "id", "title", "location", "department", "text", "url", "updated")


def _strip_html(s: str) -> str:
    # Greenhouse sends content HTML-escaped once: unescape, drop tags, unescape again.
    s = html.unescape(s or "")
    s = re.sub(r"<(br|/p|/li|/h\d|/div)\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t ]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def _greenhouse(board: str, body: dict) -> list[dict]:
    out = []
    for j in body.get("jobs", []):
        depts = j.get("departments") or []
        out.append({
            "board": board,
            "ats": "greenhouse",
            "id": str(j.get("id")),
            "title": (j.get("title") or "").strip(),
            "location": ((j.get("location") or {}).get("name") or None),
            "department": depts[0].get("name") if depts else None,
            "text": _strip_html(j.get("content") or ""),
            "url": j.get("absolute_url"),
            "updated": j.get("updated_at"),
        })
    return out


def _lever(board: str, body: list) -> list[dict]:
    out = []
    for j in body:
        cats = j.get("categories") or {}
        parts = [j.get("descriptionPlain") or ""]
        for lst in j.get("lists") or []:
            parts.append(lst.get("text") or "")
            parts.append(_strip_html(lst.get("content") or ""))
        parts.append(j.get("additionalPlain") or "")
        out.append({
            "board": board,
            "ats": "lever",
            "id": str(j.get("id")),
            "title": (j.get("text") or "").strip(),
            "location": cats.get("location"),
            "department": cats.get("team"),
            "text": "\n".join(p for p in parts if p).strip(),
            "url": j.get("hostedUrl"),
            "updated": j.get("createdAt"),
        })
    return out


def load_run(run_dir: Path | str) -> list[dict]:
    """All postings in a saved run, in file order. uid = '<board>:<id>'."""
    rows: list[dict] = []
    for f in sorted(Path(run_dir, "raw").glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("status") != 200:
            continue
        body = rec["body"]
        if isinstance(body, str):
            body = json.loads(body)
        ats = "lever" if isinstance(body, list) else "greenhouse"
        rows.extend(_lever(rec["board"], body) if ats == "lever" else _greenhouse(rec["board"], body))
    for r in rows:
        r["uid"] = f"{r['board']}:{r['id']}"
    return rows


if __name__ == "__main__":
    run = sys.argv[1] if len(sys.argv) > 1 else "evidence/run-20261123-185425Z"
    ps = load_run(run)
    print(f"{len(ps)} postings from {run}")
    for field in ("title", "location", "department", "text"):
        missing = sum(1 for p in ps if not p.get(field))
        print(f"  missing {field}: {missing}")
