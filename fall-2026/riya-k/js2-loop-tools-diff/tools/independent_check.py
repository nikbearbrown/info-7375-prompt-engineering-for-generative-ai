"""Independent check of a loop report. It does NOT trust the agent's own summary.

    python3 tools/independent_check.py runs/report-<run_id>.json [--config boards.json] [--offline]

Three checks, none of them using the loop's parsing or exit logic:
  1. Recount: for every board, count postings straight from the saved raw response (own JSON reading)
     and compare with the count the report claims.
  2. Second source: for every board the report says has 0 postings, ask a DIFFERENT source named in the
     config's "cross_check" (for HubSpot: Greenhouse hubspotjobs). If that source has postings, the
     report's "0" is contradicted. Own budget: 1 request per board checked. Same host allow-list.
  3. Exit consistency: a report that says "finished" must have every board ok with > 0 postings.

Writes only to <out>/checks/. Exit code 0 = no contradiction found, 1 = contradiction found.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from jsagent.policy import Policy, PolicyError  # noqa: E402  (shared allow-list and path rules only)

LIST_KEY = {"greenhouse": "jobs", "ashby": "jobs", "smartrecruiters": "content"}
URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{}",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{}/postings",
}


def count_raw(system, raw):
    obj = json.loads(raw)
    if system == "smartrecruiters":
        return len(obj["content"]), obj.get("totalFound")
    return len(obj[LIST_KEY[system]]), None


def check(report_path, config_path, offline=False):
    report_path = Path(report_path)
    out = report_path.parent
    policy = Policy(out, [HERE])
    report = json.loads(policy.read_bytes(report_path))
    cfg = json.loads(policy.read_bytes(Path(config_path)))
    findings, requests = [], 0

    for b in report["boards"]:
        claimed = b["postings"]
        if b["raw_responses"] and b["http_status"] == 200:
            try:
                n, total = count_raw(b["system"], policy.read_bytes(HERE / b["raw_responses"][-1]))
            except (ValueError, KeyError) as e:
                n, total = None, None
                findings.append({"check": "recount", "board": b["board"], "result": "UNREADABLE", "detail": str(e)})
            if n is not None and n != claimed:
                findings.append({"check": "recount", "board": b["board"], "result": "CONTRADICTED",
                                 "detail": f"report says {claimed}, raw response has {n}"})
            elif n is not None:
                findings.append({"check": "recount", "board": b["board"], "result": "agrees",
                                 "detail": f"{n} postings in raw" + (f" (totalFound {total})" if total is not None else "")})
        if claimed == 0:
            alt = cfg.get("cross_check", {}).get(b["board"])
            if not alt:
                findings.append({"check": "second_source", "board": b["board"], "result": "NO_SECOND_SOURCE",
                                 "detail": "0 postings and no second source configured; cannot confirm"})
                continue
            url = URLS[alt["system"]].format(alt["board"])
            if offline:
                findings.append({"check": "second_source", "board": b["board"], "result": "SKIPPED_OFFLINE",
                                 "detail": url})
                continue
            policy.check_request("GET", url)
            requests += 1
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        url, headers={"User-Agent": "INFO7375-js2-independent-check/1.0"}), timeout=20) as r:
                    raw = r.read()
                status = 200
            except urllib.error.HTTPError as e:
                raw, status = e.read(), e.code
            raw_path = out / "checks" / "raw" / f"{report['run_id']}-{alt['system']}-{alt['board']}.json"
            policy.write_bytes(raw_path, raw)
            n = count_raw(alt["system"], raw)[0] if status == 200 else None
            result = "CONTRADICTED" if n else "agrees"
            findings.append({"check": "second_source", "board": b["board"], "result": result,
                             "detail": f"report says 0; {alt['system']}:{alt['board']} has {n} postings (HTTP {status})",
                             "raw": str(raw_path)})

    if report["exit"] == "finished":
        bad = [b["board"] for b in report["boards"] if b["status"] != "ok" or not b["postings"]]
        if bad:
            findings.append({"check": "exit", "board": ",".join(bad), "result": "CONTRADICTED",
                             "detail": "report says finished, but these boards have 0 or no postings"})

    contradicted = [f for f in findings if f["result"] in ("CONTRADICTED", "UNREADABLE")]
    result = {"report": str(report_path), "report_exit": report["exit"], "requests_made": requests,
              "verdict": "CONTRADICTED" if contradicted else "no contradiction found", "findings": findings}
    policy.write_text(out / "checks" / f"check-{report['run_id']}.json", json.dumps(result, indent=2) + "\n")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--config", default=str(HERE / "boards.json"))
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    try:
        r = check(a.report, a.config, a.offline)
    except PolicyError as e:
        sys.exit(f"REFUSED: {e}")
    print(f"Independent check of {r['report']} (agent said: {r['report_exit']})")
    for f in r["findings"]:
        print(f"  [{f['result']}] {f['check']} {f['board']}: {f['detail']}")
    print(f"VERDICT: {r['verdict']}  ({r['requests_made']} request(s))")
    sys.exit(1 if r["verdict"] == "CONTRADICTED" else 0)


if __name__ == "__main__":
    main()
