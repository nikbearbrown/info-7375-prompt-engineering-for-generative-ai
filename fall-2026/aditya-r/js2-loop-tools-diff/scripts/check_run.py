"""Independent checker. It imports nothing from agent/ and never reuses the loop's decision logic:
it recomputes from raw responses, prior state and the trace, against limits and rules restated here
from GATE.md (and Addendum 1).

    .venv/bin/python scripts/check_run.py run out/runs/<run-id>
    .venv/bin/python scripts/check_run.py watch-pair <baseline-run-dir> <later-run-dir> <exit_codes.json> <expectation.json>

`run` checks a JS2 loop run. `watch-pair` checks two single-board agent.watch runs against a
predeclared expectation (the finished-wrong-answer demonstration). Exit 0 = no contradiction found,
1 = contradiction(s) found, 2 = could not check.
"""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Restated from GATE.md, deliberately not imported from agent/
LIMITS = {"http_attempts": 8, "model_calls": 10, "seconds": 180}
HOSTS = {"boards-api.greenhouse.io": r"/v1/boards/[a-z0-9][a-z0-9-]*/jobs\?content=true",
         "api.ashbyhq.com": r"/posting-api/job-board/[A-Za-z0-9][A-Za-z0-9._-]*"}
EXIT = {"finished": 0, "error": 2, "incomplete": 3, "budget-exhausted": 4}

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  — ' + str(detail)) if detail else ''}")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def jobs_and_ids(provider, body):
    data = json.loads(body)
    jobs = data["jobs"]
    ids = [str(j["id"]) for j in jobs]
    total = (data.get("meta") or {}).get("total") if provider == "greenhouse" else None
    return jobs, ids, total


def check_run(run_dir):
    run_dir = Path(run_dir)
    rep = json.loads((run_dir / "report.json").read_text())
    ev = [json.loads(line) for line in (run_dir / "trace.jsonl").read_text().splitlines()]
    print(f"# Independent check of {run_dir.name} (reported status: {rep['status']}, exit {rep['exit_code']})")
    check("trace sequence is contiguous from 1", [e["seq"] for e in ev] == list(range(1, len(ev) + 1)), f"{len(ev)} events")

    attempts = [e for e in ev if e["event"] == "http_attempt"]
    model_calls = [e for e in ev if e["event"] == "model_call"]
    check("HTTP attempts within the gate limit (8) and equal to the report",
          len(attempts) <= LIMITS["http_attempts"] and len(attempts) == rep["budget"]["http_attempts"]["used"], len(attempts))
    check("model calls within the gate limit (10) and equal to the report",
          len(model_calls) <= LIMITS["model_calls"] and len(model_calls) == rep["budget"]["model_calls"]["used"], len(model_calls))
    end_t = ev[-1]["t"]
    check("elapsed time within 180 s", end_t <= LIMITS["seconds"] and rep["budget"]["elapsed_seconds"]["used"] <= LIMITS["seconds"], f"{end_t} s")
    check("every attempt timeout ≤ 20 s and ≤ 180 − t − 10 at dispatch",
          all(a["timeout_s"] <= 20 and a["timeout_s"] <= LIMITS["seconds"] - a["t"] - 10 + 0.01 for a in attempts + model_calls))

    bad_urls = []
    for a in attempts:
        m = re.fullmatch(r"https://([^/:@]+)(/.*)", a["url"])
        if not m or m.group(1) not in HOSTS or not re.fullmatch(HOSTS[m.group(1)], m.group(2)):
            bad_urls.append(a["url"])
    check("every dispatched URL is an allow-listed board endpoint", not bad_urls, bad_urls)
    seen, repeat_ok = {}, True
    for a in attempts:
        if a["url"] in seen:
            repeat_ok &= a["attempt"] == 2 and a["retry_of"] == seen[a["url"]]
        else:
            seen[a["url"]] = a["seq"]
            repeat_ok &= a["attempt"] == 1
    check("no URL dispatched twice except one linked retry", repeat_ok)

    raw_by_board = {}
    raw_ok = True
    for r in (e for e in ev if e["event"] == "http_result" and e.get("raw")):
        body = gzip.decompress((run_dir / r["raw"]).read_bytes())
        raw_ok &= sha(body) == r["sha256"] and len(body) == r["bytes"]
        raw_by_board[r["board"]] = (r["status"], body)
    check("every saved raw response matches its recorded sha256 and size", raw_ok, f"{len(raw_by_board)} boards")

    before = json.loads((run_dir / "state_before.json").read_text()) or {"boards": {}}
    seeds = {e["board"]: e for e in ev if e["event"] == "state_seeded"}
    after = json.loads((run_dir / "state_after.json").read_text()) if (run_dir / "state_after.json").exists() else None

    for o in rep["boards"]:
        key, provider = o["key"], o["key"].split(":")[0]
        if o["status"] != "succeeded":
            check(f"{key}: failed/unattempted board reports unknown counts as null (not 0)",
                  o.get("observed") is None and o.get("new") is None, o.get("reason"))
            if after is not None:
                check(f"{key}: failed board state unchanged", after["boards"].get(key) == before["boards"].get(key))
            if key in raw_by_board:
                st, body = raw_by_board[key]
                check(f"{key}: raw response confirms the failure (HTTP {st})", st != 200 or not body.strip() or b'"jobs": []' in body or b'"jobs":[]' in body)
            continue
        st, body = raw_by_board[key]
        jobs, ids, total = jobs_and_ids(provider, body)
        check(f"{key}: raw HTTP 200, nonempty, unique ids, observed count recomputes",
              st == 200 and jobs and len(set(ids)) == len(ids) and o["observed"] == len(ids), f"{len(ids)} postings")
        if provider == "greenhouse":
            check(f"{key}: meta.total equals the jobs list length", total == len(ids), total)
        if key in seeds:
            src = ROOT / seeds[key]["path"]
            check(f"{key}: inherited seed file matches the sha256 in the trace", sha(src.read_bytes()) == seeds[key]["sha256"])
            prior = set(json.loads(src.read_text())["ids"])
        else:
            prior = set((before["boards"].get(key) or {}).get("ids", {}))
        if o["kind"] == "baseline":
            check(f"{key}: baseline only when no prior state, with 0 new", not prior and o["new"] == 0)
        else:
            expected_new = [i for i in ids if i not in prior]
            check(f"{key}: new ids recompute as (raw ids − prior ids)", o["new_ids"] == expected_new, f"{len(expected_new)} new")

    # Exit status recomputed from the reported facts with the gate's precedence
    any_budget = any(o.get("kind") == "budget" for o in rep["boards"]) or any(
        p["JUDGMENT"].get("status") == "not-run" for p in rep["postings"])
    any_incomplete = any(o["status"] != "succeeded" and o.get("kind") != "budget" for o in rep["boards"]) or any(
        p["JUDGMENT"].get("status") == "invalid" for p in rep["postings"]) or bool(rep.get("approval_request"))
    expect = "error" if rep["errors"] else "budget-exhausted" if any_budget else "incomplete" if any_incomplete else "finished"
    check("status recomputed by precedence matches the report, and the exit code matches the status",
          rep["status"] == expect and rep["exit_code"] == EXIT[expect], f"{expect}")

    if after is not None:
        valid = {(f"{p['provider']}:{p['board']}", p["posting_id"]) for p in rep["postings"] if p["JUDGMENT"].get("status") == "valid"}
        others = {(f"{p['provider']}:{p['board']}", p["posting_id"]) for p in rep["postings"] if p["JUDGMENT"].get("status") != "valid"}
        check("state: every valid judgment is 'completed' and every unjudged one is 'pending'",
              all(after["boards"][k]["ids"].get(i) == "completed" for k, i in valid)
              and all(after["boards"][k]["ids"].get(i) == "pending" for k, i in others), f"{len(valid)} completed, {len(others)} pending")
        jok = True
        for p in rep["postings"]:
            if p["JUDGMENT"].get("status") == "valid":
                j = json.loads((run_dir / p["JUDGMENT"]["file"]).read_text())
                parsed = json.loads(j["response_text"])
                jok &= j["valid"] and str(parsed["posting_id"]) == p["posting_id"] and parsed["verdict"] == p["JUDGMENT"]["verdict"]
        check("every reported valid JUDGMENT's saved response names its own posting and verdict", jok)
        live_state = ROOT / "out/state/seen.json"
        if live_state.exists() and json.loads(live_state.read_text())["runs"][-1]["run_id"] == rep["run_id"]:
            check("working state file equals this run's state_after", json.loads(live_state.read_text()) == after)
    else:
        check("no state published for a run-level error", rep["status"] == "error" and not rep["state"]["published"])


def check_watch_pair(base_dir, later_dir, exit_codes, expectation):
    exp = json.loads(Path(expectation).read_text())
    codes = json.loads(Path(exit_codes).read_text())
    print(f"# Independent check against predeclared expectation {Path(expectation).name}: {exp['rule']}")

    def raw(d):
        p = next(Path(d).glob("raw_response.json*"))
        b = p.read_bytes()
        return json.loads(gzip.decompress(b) if b[:2] == b"\x1f\x8b" else b)

    prior_ids = {str(j["id"]) for j in raw(base_dir)["jobs"]}
    later_ids = {str(j["id"]) for j in raw(later_dir)["jobs"]}
    rep = json.loads((Path(later_dir) / "report.json").read_text()) if (Path(later_dir) / "report.json").exists() else None
    reported_ok = codes["later"] == 0
    vanished = prior_ids - later_ids
    print(f"      prior response: {len(prior_ids)} ids; later response: {len(later_ids)} ids; "
          f"vanished: {len(vanished)}; later exit code: {codes['later']}; later report run entry: "
          f"{rep and {k: rep['run'].get(k) for k in ('kind', 'new', 'completed', 'pending')}}")
    contradiction = len(prior_ids) >= exp["min_prior_postings"] and len(later_ids) == 0 and reported_ok
    check("no finished-wrong answer: an emptied, previously nonempty board must not end with exit 0",
          not contradiction,
          f"CONTRADICTION: {len(vanished)} previously observed postings all vanished, yet the run exited 0 "
          f"and reported {rep['run'].get('new') if rep else '?'} new" if contradiction else "")


def main(argv):
    try:
        if argv[:1] == ["run"] and len(argv) == 2:
            check_run(argv[1])
        elif argv[:1] == ["watch-pair"] and len(argv) == 5:
            check_watch_pair(*argv[1:])
        else:
            print(__doc__)
            return 2
    except (OSError, ValueError, KeyError) as e:
        print(f"CANNOT CHECK: {type(e).__name__}: {e}")
        return 2
    n_fail = results.count(False)
    print(f"\n{'NO CONTRADICTION FOUND' if not n_fail else f'{n_fail} CONTRADICTION(S) FOUND'} ({len(results)} checks)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
