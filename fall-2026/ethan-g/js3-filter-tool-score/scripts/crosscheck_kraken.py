"""My own cross-check for run B, outside the agent (GATE.md, Evidence and review choices).

Kraken's Lever board answers 200 with []. This one GET asks Kraken's Ashby board whether Kraken has postings, to show
that the loop's "finished, 0 new" for lever:kraken is wrong, not just suspicious. Ashby is not on the agent's allow-list;
this script is not part of the agent and the gate does not add Ashby.

    python3 scripts/crosscheck_kraken.py      # saves evidence/crosscheck/<time>_ashby_kraken.com.json
"""
import hashlib
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://api.ashbyhq.com/posting-api/job-board/kraken.com"
UA = "INFO7375-job-search-agent-2 cross-check (student coursework; read-only)"


def main():
    now = datetime.now().astimezone()
    req = urllib.request.Request(URL, method="GET", headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        status, body = resp.status, resp.read()
    out = ROOT / "evidence" / "crosscheck"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{now:%Y-%m-%dT%H%M%S}_ashby_kraken.com.json"
    with open(path, "xb") as f:
        f.write(body)
    jobs = json.loads(body).get("jobs", [])
    us = [j for j in jobs if "united states" in (j.get("location") or "").lower() or "remote" in (j.get("location") or "").lower()]
    print(f"{now.isoformat(timespec='seconds')}  GET {URL}  ->  HTTP {status}, {len(jobs)} postings ({len(us)} US or remote)")
    print(f"saved {path.relative_to(ROOT)}  sha256 {hashlib.sha256(body).hexdigest()}")
    for j in jobs[:5]:
        print(f"  - {j.get('title')} | {j.get('location')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
