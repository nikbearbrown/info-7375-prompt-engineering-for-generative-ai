"""One-off probe for the pitch film (2026-10-14). Not the Early Bird agent.

Fetches five public job boards once, saves each raw response, and counts
titles that match a naive SWE/AI keyword rule. Standard library only.
Usage: python probe.py
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

BOARDS = {
    "ashby:commure": "https://api.ashbyhq.com/posting-api/job-board/commure",
    "greenhouse:stripe": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs",
    "greenhouse:figma": "https://boards-api.greenhouse.io/v1/boards/figma/jobs",
    "greenhouse:databricks": "https://boards-api.greenhouse.io/v1/boards/databricks/jobs",
    "lever:palantir": "https://api.lever.co/v0/postings/palantir?mode=json",
}
ALLOWED_HOSTS = {"api.ashbyhq.com", "boards-api.greenhouse.io", "api.lever.co"}

# Naive on purpose: the film shows why keyword matching alone is not enough.
ROLE = re.compile(r"\b(software|engineer|full[- ]?stack|backend|frontend|ai|ml|machine learning)\b", re.I)


def titles(platform, data):
    if platform in ("greenhouse", "ashby"):
        return [j["title"] for j in data["jobs"]]
    return [j["text"] for j in data]  # lever


def main():
    out = Path(__file__).parent / date.today().isoformat()
    out.mkdir(exist_ok=True)
    summary = {}
    for key, url in BOARDS.items():
        host = url.split("/")[2]
        if host not in ALLOWED_HOSTS:
            raise SystemExit(f"refused: {host} not on allow-list")
        # Ashby answered 403 to urllib's default User-Agent; identify ourselves honestly.
        req = urllib.request.Request(url, headers={"User-Agent": "earlybird-probe/0.1 (INFO 7375 student project)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
        (out / f"{key.replace(':', '_')}.json").write_bytes(body)
        names = titles(key.split(":")[0], json.loads(body))
        matched = [t for t in names if ROLE.search(t)]
        summary[key] = {"postings": len(names), "keyword_matches": len(matched), "sample": matched[:5]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for key, s in summary.items():
        print(f"{key:24} {s['postings']:5} postings  {s['keyword_matches']:4} keyword matches")


if __name__ == "__main__":
    main()
