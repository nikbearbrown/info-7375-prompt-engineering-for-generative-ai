"""Collect: one public GET per board, allow-listed, no redirects, raw responses saved untouched.

    python3 src/collect.py --run-id live-YYYYMMDD

Writes runs/<run-id>/raw/<board>.json and runs/<run-id>/manifest.json. Never logs in, never
posts, never follows a redirect. The endpoints are the ones listed in FILTER.md section 4.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"}
BOARDS = [
    {"board": "airbnb", "ats": "greenhouse", "url": "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true"},
    {"board": "figma", "ats": "greenhouse", "url": "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true"},
    {"board": "spotify", "ats": "lever", "url": "https://api.lever.co/v0/postings/spotify?mode=json"},
    {"board": "linear", "ats": "ashby", "url": "https://api.ashbyhq.com/posting-api/job-board/linear"},
]
USER_AGENT = "INFO7375-JS3-student-project (read-only; one request per board per run)"


class Refused(Exception):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refused(f"redirect to {newurl} refused")


def check_url(url):
    p = urllib.parse.urlparse(url)
    if p.scheme != "https" or p.hostname not in ALLOWED_HOSTS:
        raise Refused(f"{url} is not on the allow-list")


def fetch(url, timeout=30):
    check_url(url)
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with opener.open(req, timeout=timeout) as r:
        return r.status, r.read()


def collect(run_id, boards=BOARDS, fetcher=fetch, gap_s=1.0):
    out_dir = os.path.join(ROOT, "runs", run_id)
    if os.path.exists(out_dir):
        raise SystemExit(f"{out_dir} exists; use a new run id")
    os.makedirs(os.path.join(out_dir, "raw"))
    manifest = {"run_id": run_id, "started": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "boards": []}
    for i, b in enumerate(boards):
        if i:
            time.sleep(gap_s)
        entry = {"board": b["board"], "ats": b["ats"], "url": b["url"]}
        try:
            status, body = fetcher(b["url"])
            json.loads(body)  # a body that is not JSON is a failed collection, not data
            path = os.path.join("raw", f"{b['board']}.json")
            with open(os.path.join(out_dir, path), "wb") as f:
                f.write(body)
            entry.update(status="collected", http=status, bytes=len(body),
                         sha256=hashlib.sha256(body).hexdigest(), raw=path)
        except (Refused, urllib.error.URLError, OSError, ValueError) as e:
            entry.update(status="not collected", error=f"{type(e).__name__}: {e}")
        entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        manifest["boards"].append(entry)
    manifest["finished"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    m = collect(ap.parse_args().run_id)
    for b in m["boards"]:
        print(f"{b['board']:8} {b['status']:14} {b.get('bytes', '')} {b.get('error', '')}")
    return 0 if all(b["status"] == "collected" for b in m["boards"]) else 2


if __name__ == "__main__":
    sys.exit(main())
