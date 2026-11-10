"""Independent check of one loop run (GATE.md: "finished is not correct").

It does not trust the loop's record. It recomputes every count from the saved raw files, flags boards
that look wrong even though the loop called them ok (too few postings, or a newest posting older than
max_newest_age_days), and for a flagged board makes ONE read-only cross-check request to the same
company on another allow-listed ATS (checks.json). It reads only through the permission policy
(a refused read stops the check before any verdict is written), writes only check.json / check.md in
the run folder through the same policy, and never touches state.

Usage: python3 check_run.py runs/<run-id>
"""
import datetime as dt
import json
import os
import pathlib
import re
import sys

from jobwatch2 import ats
from jobwatch2.net import http_get
from jobwatch2.policy import Policy

ROOT = pathlib.Path(__file__).resolve().parent


def _date(s):
    try:
        return dt.datetime.fromisoformat(s).date()
    except (TypeError, ValueError):
        return None


def _read(policy, path):
    """Every file the check reads is asked of the permission policy first (GATE.md: reads only
    inside the assignment folder). A refusal stops the check: no verdict is written."""
    d = policy.read(path)
    if not d.allowed:
        raise PermissionError(f"check refused to read {path}: {d.reason}")
    return pathlib.Path(path).read_bytes()


def _raw_for(run_dir, key, raw_path):
    """A record may only point a board at THIS run's raw response for THAT board:
    <run_dir>/raw/<ats>__<slug>.attempt<N>.json, judged on the resolved path. Anything else, even a
    file the policy may read (another run, another board, a persona), stops the check."""
    raw_dir = os.path.realpath(pathlib.Path(run_dir) / "raw")
    real = os.path.realpath(raw_path)
    name_ok = re.fullmatch(re.escape(key.replace("/", "__")) + r"\.attempt\d+\.json", os.path.basename(real))
    if os.path.dirname(real) != raw_dir or not name_ok:
        raise PermissionError(f"check refused raw_path {raw_path} for {key}: not this run's raw file for this board")
    return real


def check(root, run_dir, fetcher=http_get, today=None):
    root, run_dir = pathlib.Path(root), pathlib.Path(run_dir)
    today = today or dt.date.today()
    policy = Policy(root)
    cfg = json.loads(_read(policy, root / "checks.json"))
    record = json.loads(_read(policy, run_dir / "record.json"))
    raws = {b["key"]: _read(policy, _raw_for(run_dir, b["key"], b["raw_path"]))
            for b in record["boards"] if b["status"] == "ok"}
    flags, requests = [], 0
    for b in record["boards"]:
        if b["status"] != "ok":
            continue
        posts = ats.parse(b["ats"], raws[b["key"]])
        if len(posts) != b["fetched"]:
            flags.append({"board": b["key"], "kind": "count-mismatch",
                          "detail": f"record says {b['fetched']}, raw file has {len(posts)}"})
        dates = [d for d in (_date(p["published"]) for p in posts) if d]
        newest = max(dates) if dates else None
        age = (today - newest).days if newest else None
        small = len(posts) < cfg["min_postings"]
        stale = age is None or age > cfg["max_newest_age_days"]
        if not (small or stale):
            continue
        why = (f"{len(posts)} postings (< {cfg['min_postings']})" if small else "") + \
              ("; " if small and stale else "") + (f"newest posting {age} days old" if stale and age is not None
                                                   else "no dates" if stale else "")
        xc = cfg["cross_check"].get(b["key"])
        if not xc:
            flags.append({"board": b["key"], "kind": "suspect", "detail": why + "; no cross-check configured"})
            continue
        url = ats.url(xc["ats"], xc["slug"])
        d = policy.request("GET", url)
        if not d.allowed:
            flags.append({"board": b["key"], "kind": "suspect", "detail": f"{why}; cross-check refused: {d.reason}"})
            continue
        policy.record_request("GET", url)
        requests += 1
        try:
            status, body = fetcher(url, 20)
            n = len(ats.parse(xc["ats"], body)) if status == 200 else None
        except (TimeoutError, ConnectionError, OSError, ats.ShapeError) as ex:
            status, n = None, None
        if n is not None and n >= cfg["min_postings"]:
            flags.append({"board": b["key"], "kind": "finished-wrong", "detail":
                          f"{why}; the same company on {xc['ats']}/{xc['slug']} lists {n} postings",
                          "cross_check": f"{xc['ats']}/{xc['slug']}", "cross_check_postings": n})
        else:
            flags.append({"board": b["key"], "kind": "suspect",
                          "detail": f"{why}; cross-check {xc['ats']}/{xc['slug']} gave HTTP {status}, {n} postings"})
    wrong = any(f["kind"] in ("finished-wrong", "count-mismatch") for f in flags)
    rep = {"run_dir": str(run_dir), "loop_exit": record["exit"], "checked_on": today.isoformat(),
           "verdict": "wrong" if wrong else ("suspect" if flags else "consistent"),
           "cross_check_requests": requests, "flags": flags}
    for name, data in (("check.json", json.dumps(rep, indent=1) + "\n"), ("check.md", _md(rep))):
        out = run_dir / name
        if not policy.write(out).allowed:
            raise PermissionError(f"check may not write {out}")
        out.write_text(data)
    return rep


def _md(rep):
    out = [f"# Independent check — loop said `{rep['loop_exit']}`, check says **{rep['verdict']}**", "",
           f"Checked {rep['checked_on']}; cross-check requests: {rep['cross_check_requests']}.", ""]
    out += [f"- **{f['board']}** — `{f['kind']}`: {f['detail']}" for f in rep["flags"]] or ["- no flags"]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    rep = check(ROOT, sys.argv[1])
    print(f"loop exit: {rep['loop_exit']} -> independent check: {rep['verdict']}")
    for f in rep["flags"]:
        print(f"  {f['board']}: {f['kind']} — {f['detail']}")
    sys.exit(1 if rep["verdict"] == "wrong" else 0)
