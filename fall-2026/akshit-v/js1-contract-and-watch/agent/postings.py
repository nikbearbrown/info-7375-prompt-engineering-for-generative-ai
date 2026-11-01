"""Turn a saved Greenhouse response into plain posting records."""
import html
import json
import re
from pathlib import Path


def html_to_text(s: str) -> str:
    # Greenhouse escapes the HTML once (&lt;p&gt;), and the HTML itself holds entities (&nbsp;).
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_jobs(data: dict) -> list[dict]:
    jobs = data.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("response has no 'jobs' list")
    out = []
    for j in jobs:
        out.append({
            "id": int(j["id"]),
            "title": (j.get("title") or "").strip(),
            "location_name": ((j.get("location") or {}).get("name") or "").strip(),
            "absolute_url": j.get("absolute_url") or "",
            "updated_at": j.get("updated_at") or "",
            "content_text": html_to_text(j.get("content") or ""),
        })
    return out


def load_postings(raw_path: Path) -> list[dict]:
    return parse_jobs(json.loads(Path(raw_path).read_text(encoding="utf-8")))
