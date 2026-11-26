"""Collect every posting, with its text, from the boards in config/sources.json (FILTER.md §4).

    python3 -m js3.collect            # writes out/snapshots/<UTC time>/

One GET per board, through the JS2 policy (https, GET, two hosts). The raw bytes are saved
gzip'd before parsing, with their SHA-256. A board that fails or returns no jobs is reported as
not seen; it is never reported as "nothing relevant".
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import sys

from js3.fetch import make_fetcher
from js3.policy import Policy
from js3.text import plain_text

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BadData(ValueError):
    pass


def greenhouse_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def ashby_url(board):
    return f"https://api.ashbyhq.com/posting-api/job-board/{board}"


def parse_greenhouse(board, data):
    out, dropped = [], 0
    for j in data["jobs"]:
        if not j.get("id") or not isinstance(j.get("title"), str):
            dropped += 1
            continue
        out.append({
            "uid": f"greenhouse:{board}:{j['id']}",
            "system": "greenhouse", "board": board, "id": str(j["id"]),
            "title": j["title"],
            "location": (j.get("location") or {}).get("name"),
            "department": ", ".join(d.get("name", "") for d in j.get("departments") or []) or None,
            "text": plain_text(j.get("content")),
            "url": j.get("absolute_url"),
            "updated_at": j.get("updated_at"),
        })
    return out, dropped, 0


def parse_ashby(board, data):
    out, dropped, unlisted = [], 0, 0
    for j in data["jobs"]:
        if j.get("isListed") is False:
            unlisted += 1
            continue
        if not j.get("id") or not isinstance(j.get("title"), str):
            dropped += 1
            continue
        text = j.get("descriptionPlain") or plain_text(j.get("descriptionHtml"))
        out.append({
            "uid": f"ashby:{board}:{j['id']}",
            "system": "ashby", "board": board, "id": str(j["id"]),
            "title": j["title"],
            "location": j.get("location"),
            "department": j.get("department"),
            "text": (text or "").strip(),
            "url": j.get("jobUrl"),
            "updated_at": j.get("publishedAt"),
        })
    return out, dropped, unlisted


SYSTEMS = {"greenhouse": (greenhouse_url, parse_greenhouse), "ashby": (ashby_url, parse_ashby)}


def collect(config, out_root, fetch=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    snap = os.path.join(out_root, "snapshots", now.strftime("%Y%m%dT%H%M%SZ"))
    policy = Policy(HERE, os.path.join(HERE, "out"), config["allowed_hosts"])
    fetch = fetch or make_fetcher(policy)
    postings, boards = [], []
    for b in config["boards"]:
        system, board = b["system"], b["board"]
        url_for, parse = SYSTEMS[system]
        url = url_for(board)
        rec = {"system": system, "board": board, "url": url, "status": None, "seen": False}
        res = fetch(url, config["request_timeout_seconds"])
        rec["http_status"] = res.status
        if res.error or res.status != 200:
            rec["status"] = f"failed: {res.error or 'HTTP ' + str(res.status)}"
            boards.append(rec)
            continue
        raw_path = os.path.join(snap, "raw", f"{system}-{board}.json.gz")
        policy.write_bytes(raw_path, gzip.compress(res.body, mtime=0))
        rec["raw_sha256"] = hashlib.sha256(res.body).hexdigest()
        rec["raw_bytes"] = len(res.body)
        try:
            data = json.loads(res.body)
            if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
                raise BadData("no 'jobs' list")
            parsed = parse(board, data)
        except (ValueError, BadData) as e:
            rec["status"] = f"failed: bad data ({e})"
            boards.append(rec)
            continue
        items, rec["dropped"], rec["unlisted_skipped"] = parsed
        if not items:
            rec["status"] = "suspicious: 0 jobs"
            boards.append(rec)
            continue
        rec.update(status="ok", seen=True, postings=len(items),
                   text_missing=sum(len(p["text"]) < 300 for p in items))
        postings.extend(items)
        boards.append(rec)

    report = {
        "collected_at": now.isoformat(timespec="seconds"),
        "complete": all(b["seen"] for b in boards),
        "boards": boards,
        "postings": len(postings),
        "not_seen": [f"{b['system']}:{b['board']}" for b in boards if not b["seen"]],
    }
    body = "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in postings).encode()
    policy.write_bytes(os.path.join(snap, "postings.jsonl.gz"), gzip.compress(body, mtime=0))
    policy.write_bytes(os.path.join(snap, "collect_report.json"), json.dumps(report, indent=2).encode())
    return snap, report


def load_postings(snap):
    with gzip.open(os.path.join(snap, "postings.jsonl.gz"), "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def latest_snapshot(out_root=os.path.join(HERE, "out")):
    d = os.path.join(out_root, "snapshots")
    snaps = sorted(x for x in os.listdir(d) if not x.startswith("."))
    if not snaps:
        raise FileNotFoundError("no snapshot; run python3 -m js3.collect")
    return os.path.join(d, snaps[-1])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config", "sources.json"))
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    snap, report = collect(config, os.path.join(HERE, "out"))
    print(json.dumps(report, indent=2))
    print(f"snapshot: {os.path.relpath(snap, HERE)}")
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
