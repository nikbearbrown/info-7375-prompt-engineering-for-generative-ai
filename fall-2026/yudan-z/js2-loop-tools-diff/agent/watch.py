"""Contract §1-§3: allow-listed fetch, raw response saved as evidence, new-since-last by posting id."""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


class NotAllowed(PermissionError):
    pass


def host_allowed(url, allowlist):
    return urllib.parse.urlparse(url).hostname in set(allowlist)


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "js1-contract-and-watch (course assignment)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch(url, allowlist, fetcher=http_get):
    """Refuse before any network call if the host is not allow-listed (§3 refuse 1)."""
    if not host_allowed(url, allowlist):
        raise NotAllowed(f"refused: {urllib.parse.urlparse(url).hostname} is not on the allow-list {allowlist}")
    return fetcher(url)


def run_watch(board, workdir, allowlist, fetcher=http_get, stamp=None):
    """Fetch the board, save the raw bytes, and return postings whose id was never seen before.
    No state file yet = baseline: store every id, report nothing (§2, failure 1).
    Only ids in THIS response can be reported (failure 3); each id at most once (failure 2)."""
    raw = fetch(BOARD_URL.format(board=board), allowlist, fetcher)
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(os.path.join(workdir, "evidence"), exist_ok=True)
    # never overwrite evidence: two runs started in the same second once shared a stamp and the
    # first run's raw response was lost (seeded run, 2026-10-30) — add a counter instead
    base, n = stamp, 1
    while os.path.exists(os.path.join(workdir, "evidence", f"{stamp}-{board}.json")):
        n += 1
        stamp = f"{base}-{n}"
    with open(os.path.join(workdir, "evidence", f"{stamp}-{board}.json"), "wb") as f:
        f.write(raw)

    jobs = json.loads(raw.decode("utf-8")).get("jobs", [])
    state_path = os.path.join(workdir, "state", "seen_ids.json")
    baseline = not os.path.exists(state_path)
    seen = set() if baseline else set(json.load(open(state_path, encoding="utf-8"))["seen_ids"])

    new, reported = [], set()
    for j in jobs:
        jid = j["id"]
        if not baseline and jid not in seen and jid not in reported:
            new.append(j)
            reported.add(jid)
    seen.update(j["id"] for j in jobs)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"board": board, "last_run": stamp, "baseline_run": baseline,
                   "seen_ids": sorted(seen)}, f, indent=1)
    return new
