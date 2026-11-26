"""Checks which shortlisted postings are still open (JS3, optional live check).

One GET per board to its public list endpoint (the same allow-listed hosts as JS2,
without content), then a membership check for each shortlisted posting. Writes only
data/js3/liveness/<date>.json; the corpus, the board state and the audit are untouched.

Usage: uv run python scripts/js3_liveness.py
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
UA = "job-search-agent/0.1 (discovery only; INFO 7375 coursework)"
ENDPOINTS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{token}",
}
ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.ashbyhq.com"}


def open_ids(client: httpx.Client, board: str) -> tuple[set[str], dict[str, object]]:
    """The IDs currently listed on one board, and facts about the request."""
    provider, token = board.split("/")
    url = ENDPOINTS[provider].format(token=token)
    assert httpx.URL(url).host in ALLOWED_HOSTS  # noqa: S101 - fixed allow-list
    resp = client.get(url)
    resp.raise_for_status()
    jobs = resp.json()["jobs"]
    ids = {str(j["id"]) for j in jobs}
    facts = {
        "url": url,
        "status": resp.status_code,
        "jobs": len(jobs),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
    }
    return ids, facts


def main() -> int:
    """Checks every shortlisted posting and writes the result."""
    shortlist = json.loads(
        (ROOT / "data/js3/shortlist.json").read_text(encoding="utf-8")
    )
    keys = [p["key"] for p in shortlist["postings"]]
    boards = sorted({k.rsplit("/", 1)[0] for k in keys})
    checked_at = datetime.now(UTC).isoformat(timespec="seconds")
    with httpx.Client(
        timeout=30, headers={"User-Agent": UA}, follow_redirects=False
    ) as client:
        listing = {b: open_ids(client, b) for b in boards}
    rows = [
        {
            "key": k,
            "title": p["title"].strip(),
            "still_listed": k.rsplit("/", 1)[1] in listing[k.rsplit("/", 1)[0]][0],
        }
        for k, p in zip(keys, shortlist["postings"], strict=True)
    ]
    out = {
        "checked_at_utc": checked_at,
        "filter_version": shortlist["filter_version"],
        "requests": {b: facts for b, (_, facts) in listing.items()},
        "still_listed": sum(r["still_listed"] for r in rows),
        "n": len(rows),
        "by_board": {
            b: dict(
                Counter(r["still_listed"] for r in rows if r["key"].startswith(b + "/"))
            )
            for b in boards
        },
        "postings": rows,
    }
    path = ROOT / "data/js3/liveness" / f"{checked_at[:10]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    rel = path.relative_to(ROOT)
    print(f"{out['still_listed']} of {out['n']} still listed; wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
