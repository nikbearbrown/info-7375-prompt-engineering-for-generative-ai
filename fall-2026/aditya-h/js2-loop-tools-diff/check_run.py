"""Independent check of one loop run (GATE.md: "finished is not correct").

It does not trust the loop's record. It recomputes every count from the saved raw files, flags boards
that look wrong even though the loop called them ok (too few postings, or a newest posting older than
max_newest_age_days), and for a flagged board makes ONE read-only cross-check request to the same
company on another allow-listed ATS (checks.json). It writes only check.json / check.md in the run
folder, through the same permission policy, and never touches state.

Usage: python3 check_run.py runs/<run-id>
"""
import datetime as dt
import json
import pathlib
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


def check(root, run_dir, fetcher=http_get, today=None):
    root, run_dir = pathlib.Path(root), pathlib.Path(run_dir)
    today = today or dt.date.today()
    policy = Policy(root)
    cfg = json.loads((root / "checks.json").read_text())
    record = json.loads((run_dir / "record.json").read_text())
    flags, requests = [], 0
    for b in record["boards"]:
        if b["status"] != "ok":
            continue
        posts = ats.parse(b["ats"], pathlib.Path(b["raw_path"]).read_bytes())
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
