"""Independent check of a run report. It does NOT import or call the loop.

It trusts nothing the agent concluded. For every board the report calls "ok" it compares the
reported job count with (1) the count saved for that board before the run, and (2) with --live,
a fresh count from its own GET of the same public board (allow-listed hosts only). It also
checks that a run reported "finished" has no board that was anything but ok.

    python3 scripts/independent_check.py REPORT.json --state-before STATE.json [--live]

Verdict per board: CONFIRMED | CONTRADICTED | DIFFERS (counts moved; a real board can change).
Exit code 1 if anything is CONTRADICTED.
"""
import argparse
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from jsagent.policy import ALLOW, Policy  # only the allow-list, not the loop  # noqa: E402

URLS = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{}/jobs",
        "ashby": "https://api.ashbyhq.com/posting-api/job-board/{}"}


def live_count(policy, system, board):
    url = URLS[system].format(board)
    if policy.check_request("GET", url).outcome != ALLOW:
        return None, "refused by allow-list"
    req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-JS2-independent-check/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return len(json.loads(r.read())["jobs"]), url


def check(report, state_before, live=False, policy=None):
    rows, contradicted = [], False
    before = (state_before or {}).get("boards", {})
    for b in report["boards"]:
        key = f"{b['system']}:{b['board']}"
        row = {"board": key, "agent_result": b["result"], "agent_count": b["count_seen"]}
        if b["result"] != "ok":
            row["verdict"] = "NOT_CHECKED (agent did not claim ok)"
            rows.append(row)
            continue
        prev = before.get(key, {}).get("count")
        row["count_before_run"] = prev
        problems = []
        if prev and b["count_seen"] == 0:
            problems.append(f"agent says 0 jobs; {prev} were saved before this run")
        if live:
            n, src = live_count(policy, b["system"], b["board"])
            row["live_count"], row["live_source"] = n, src
            if n and b["count_seen"] == 0:
                problems.append(f"agent says 0 jobs; a fresh GET counts {n}")
        if problems:
            row["verdict"], contradicted = "CONTRADICTED", True
            row["why"] = problems
        elif live and row.get("live_count") is not None and row["live_count"] != b["count_seen"]:
            row["verdict"] = f"DIFFERS by {row['live_count'] - b['count_seen']} (board may have changed)"
        else:
            row["verdict"] = "CONFIRMED"
        rows.append(row)
    status_ok = not (report["status"] == "finished" and any(b["result"] != "ok" for b in report["boards"]))
    if not status_ok:
        contradicted = True
    claimed_finished_but_wrong = report["status"] == "finished" and any(r["verdict"] == "CONTRADICTED" for r in rows)
    return {"report": report["run_id"], "agent_status": report["status"], "status_consistent": status_ok,
            "finished_but_wrong": claimed_finished_but_wrong, "boards": rows,
            "overall": "CONTRADICTED" if contradicted else "CONFIRMED"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--state-before")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--out", help="write the check result here (inside out/)")
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "config", "run.json")) as f:
        cfg = json.load(f)
    pol = Policy(HERE, os.path.join(HERE, "out"), cfg["allowed_hosts"])
    with open(a.report) as f:
        report = json.load(f)
    state = None
    if a.state_before:
        with open(a.state_before) as f:
            state = json.load(f)
    res = check(report, state, a.live, pol)
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        pol.write_bytes(a.out, text.encode())
    return 1 if res["overall"] == "CONTRADICTED" else 0


if __name__ == "__main__":
    sys.exit(main())
