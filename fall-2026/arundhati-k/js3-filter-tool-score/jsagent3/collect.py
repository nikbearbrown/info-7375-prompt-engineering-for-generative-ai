"""Collect postings from the three FILTER.md section 6 boards. GET only, allow-listed hosts.

Raw responses are saved gzipped under data/raw/<date>/ so every later step can be re-run offline.
"""
import gzip
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.ashbyhq.com"}

BOARDS = {
    "stripe": ("greenhouse", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"),
    "figma": ("greenhouse", "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true"),
    "notion": ("ashby", "https://api.ashbyhq.com/posting-api/job-board/notion"),
}


def fetch(url, timeout=30):
    host = urllib.parse.urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise PermissionError(f"host not on allow-list: {host}")
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "info7375-js3-student-agent"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def html_to_text(s):
    """Greenhouse content is HTML-escaped HTML. Keep line breaks at block tags so headings survive."""
    s = html.unescape(s or "")
    s = re.sub(r"(?i)<\s*(br|/p|/li|/h[1-6]|/div|/ul|/ol)\s*/?>", "\n", s)
    s = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def normalise(board, kind, raw):
    out = []
    for j in raw.get("jobs", []):
        if kind == "greenhouse":
            body = html_to_text(j.get("content"))
            loc = (j.get("location") or {}).get("name") or ""
            url = j.get("absolute_url")
        else:
            body = (j.get("descriptionPlain") or "").strip()
            locs = [j.get("location") or ""] + [x.get("location", "") for x in (j.get("secondaryLocations") or [])]
            addr = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or ""
            loc = "; ".join(x for x in locs if x) + (f" ({addr})" if addr else "")
            url = j.get("jobUrl")
        out.append({
            "id": f"{board}:{j.get('id')}",
            "board": board,
            "title": (j.get("title") or "").strip(),
            "location": loc,
            "body": body,
            "url": url,
        })
    return out


def collect(raw_dir: Path, offline=False):
    raw_dir.mkdir(parents=True, exist_ok=True)
    postings, report = [], {}
    for board, (kind, url) in BOARDS.items():
        path = raw_dir / f"{board}.json.gz"
        try:
            if not offline:
                path.write_bytes(gzip.compress(fetch(url)))
            raw = json.loads(gzip.decompress(path.read_bytes()))
            items = normalise(board, kind, raw)
            report[board] = {"status": "ok", "postings": len(items),
                             "body_missing": sum(1 for p in items if not p["body"])}
            postings += items
        except Exception as e:  # FILTER.md s6: say which board failed and why, never "0 relevant"
            report[board] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
    return postings, report
