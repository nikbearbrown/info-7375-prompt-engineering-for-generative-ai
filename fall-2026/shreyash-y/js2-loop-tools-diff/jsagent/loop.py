"""The bounded loop (GATE.md sections 2-5, read as GATE-NOTES.md says): one pass over the boards,
under budgets it cannot raise, with one exit status and a trace line for every observation."""
import datetime
import hashlib
import json
import pathlib
import re
import time

from jsagent import policy, providers, rule

SEVERITY = ["finished", "incomplete", "budget-exhausted", "error"]
BUDGET_KEYS = ("max_boards", "max_requests", "max_seconds")


def load_budgets(budgets_path, gate_path):
    """budgets.json may not exceed the latest dated row of GATE.md's budget table."""
    b = json.loads(pathlib.Path(budgets_path).read_text())
    rows = re.findall(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", pathlib.Path(gate_path).read_text(), re.M)
    if not rows:
        raise ValueError("GATE.md has no dated budget row")
    date, *limits = max(rows)
    for key, gate_value in zip(BUDGET_KEYS, map(int, limits)):
        if not isinstance(b.get(key), int) or b[key] > gate_value:
            raise ValueError(f"budgets.json {key}={b.get(key)} exceeds GATE.md ({gate_value}, decided {date})")
    return {k: b[k] for k in BUDGET_KEYS}


def latest_state(runs_dir):
    states = []
    for f in (pathlib.Path(runs_dir) / "state").glob("state-*.json"):
        s = json.loads(f.read_text())
        states.append((s["sequence"], s))
    return max(states)[1] if states else {"sequence": 0, "boards": {}, "last_counts": {}}


def run(boards, budgets, transport, files, run_id, resume, clock=time.monotonic, judge=rule.judge):
    start = clock()
    run_dir = files.runs / run_id
    rel = lambda p: str(pathlib.Path(p).relative_to(files.project))

    def trace(event, **kw):
        line = {"event": event, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), **kw}
        files.append(run_dir / "trace.jsonl", (json.dumps(line) + "\n").encode())

    prev = latest_state(files.runs)
    seen = {k: set(v) for k, v in prev["boards"].items()}
    last_counts = dict(prev.get("last_counts", {}))
    trace("start", run_id=run_id, budgets=budgets, boards=[b["name"] for b in boards], previous_state_sequence=prev["sequence"])
    results, requests, done_urls, exhausted, fatal = [], 0, set(), False, None

    for b in boards:
        if b.get("ats") not in providers.ATS:
            fatal = f"board {b.get('name')!r}: unknown applicant-tracking system {b.get('ats')!r}"
    if fatal:
        trace("fatal", reason=fatal)

    for i, b in enumerate(boards):
        r = {"name": b["name"], "ats": b["ats"], "token": b["token"], "status": None, "fetched": None, "new": None,
             "baseline": None, "requests": 0, "error": None, "needs_review": False, "raw_files": [], "new_postings": []}
        results.append(r)
        if fatal:
            r["status"] = "not-run"
            continue
        if i >= budgets["max_boards"]:
            exhausted = True
        if exhausted:
            r["status"] = "skipped-budget"
            trace("skip", board=b["name"], reason="budget")
            continue
        url = providers.board_url(b["ats"], b["token"])
        if url in done_urls:
            r["status"] = "skipped-duplicate"
            trace("skip", board=b["name"], reason="duplicate", url=url)
            continue
        done_urls.add(url)
        attempt = 0
        while True:
            used = clock() - start
            if requests >= budgets["max_requests"] or used > budgets["max_seconds"]:
                exhausted = True
                r["status"] = "skipped-budget" if attempt == 0 else "failed"
                r["error"] = None if attempt == 0 else "budget ran out before the allowed retry"
                trace("budget", board=b["name"], requests=requests, seconds=round(used, 1))
                break
            attempt += 1
            requests += 1
            r["requests"] += 1
            trace("request", board=b["name"], url=url, attempt=attempt)
            status, body, kind = None, None, None
            try:
                status, body = transport.get(url)
            except TimeoutError as e:
                kind = "timeout"
            except policy.PolicyViolation as e:
                fatal = f"policy refused a request the loop built: {e}"
                trace("fatal", reason=fatal)
                r["status"], r["error"] = "failed", "policy"
                break
            except ConnectionError as e:
                kind = "network"
            if body is not None:
                raw = files.write(run_dir / "raw" / f"{b['ats']}-{b['token']}-attempt{attempt}.json", body)
                r["raw_files"].append(rel(raw))
                trace("response", board=b["name"], status=status, bytes=len(body),
                      sha256=hashlib.sha256(body).hexdigest(), raw_file=rel(raw))
            else:
                trace("no-response", board=b["name"], kind=kind)
            if kind is None:
                try:
                    postings, info = providers.parse(b["ats"], b["token"], status, body)
                except providers.BadResponse as e:
                    kind = e.kind
            if kind in ("timeout", "server-error") and attempt == 1:
                trace("retry", board=b["name"], reason=kind)
                continue
            if kind:
                r["status"], r["error"], r["needs_review"] = "failed", kind, True
                trace("board", board=b["name"], status="failed", error=kind)
                break
            key = f"{b['ats']}:{b['token']}"
            r["fetched"] = len(postings)
            r["meta_total"] = info.get("meta_total")
            if not postings:
                r["status"], r["needs_review"] = "empty", True
                trace("board", board=b["name"], status="empty", fetched=0,
                      note="valid response with no postings; not counted as 'no new jobs'")
                break
            ids = {p["id"] for p in postings}
            r["baseline"] = key not in seen
            new = [] if r["baseline"] else [p for p in postings if p["id"] not in seen[key]]
            seen[key] = seen.get(key, set()) | ids
            last_counts[key] = len(postings)
            r["new"] = len(new)
            for p in new:
                rec = judge(p, resume)
                r["new_postings"].append({"posting_id": p["id"], "title": p["title"], "location": p["location"],
                                          "url": p.get("absolute_url"), "verdict": rec["verdict"],
                                          "failed_conditions": rec["failed_conditions"], "justification": rec["justification"],
                                          "judge": rec["judge"]})
            r["status"] = "ok"
            trace("board", board=b["name"], status="ok", fetched=len(postings), new=len(new), baseline=r["baseline"],
                  meta_total=r["meta_total"])
            break
        if fatal:
            break

    for r in results:
        if r["status"] is None:
            r["status"] = "not-run"
    statuses = [r["status"] for r in results]
    if fatal:
        exit_status = "error"
    elif exhausted:
        exit_status = "budget-exhausted"
    elif any(s in ("failed", "empty") for s in statuses):
        exit_status = "incomplete"
    else:
        exit_status = "finished"
    seconds = round(clock() - start, 2)
    sequence = prev["sequence"] + 1
    if exit_status != "error":
        files.write(files.runs / "state" / f"state-{run_id}.json", json.dumps(
            {"sequence": sequence, "run_id": run_id, "boards": {k: sorted(v) for k, v in seen.items()},
             "last_counts": last_counts}, indent=1, sort_keys=True).encode())
    report = {"run_id": run_id, "exit": exit_status, "fatal": fatal, "state_sequence": sequence,
              "previous_state_sequence": prev["sequence"], "budgets": budgets, "requests_used": requests,
              "seconds_used": seconds, "boards": results,
              "verified_postings": sum(r["fetched"] for r in results if r["status"] == "ok"),
              "needs_review": [r["name"] for r in results if r["needs_review"]]}
    files.write(run_dir / "summary.json", (json.dumps(report, indent=1) + "\n").encode())
    files.write(run_dir / "summary.md", markdown(report).encode())
    trace("exit", exit=exit_status, requests=requests, seconds=seconds, needs_review=report["needs_review"])
    return report


def markdown(rep):
    out = [f"# Run {rep['run_id']}: exit `{rep['exit']}`", "",
           f"Requests {rep['requests_used']} of {rep['budgets']['max_requests']}; seconds {rep['seconds_used']} of "
           f"{rep['budgets']['max_seconds']}; boards {len(rep['boards'])} (limit {rep['budgets']['max_boards']}).",
           f"Verified postings (ok boards only): {rep['verified_postings']}. Needs review: {', '.join(rep['needs_review']) or 'none'}.",
           "" if not rep["fatal"] else f"**Fatal:** {rep['fatal']}", "",
           "| Board | System | Status | Fetched | New | Baseline | Requests | Error |", "|---|---|---|---|---|---|---|---|"]
    for r in rep["boards"]:
        show = lambda v: "—" if v is None else str(v)
        out.append(f"| {r['name']} | {r['ats']} | {r['status']} | {show(r['fetched'])} | {show(r['new'])} | "
                   f"{show(r['baseline'])} | {r['requests']} | {show(r['error'])} |")
    for r in rep["boards"]:
        for p in r["new_postings"]:
            out += ["", f"**{r['name']} {p['posting_id']}**: {p['title']} ({p['location']}). Rule (record): "
                        f"{p['verdict']}" + (f", failed {p['failed_conditions']}" if p["failed_conditions"] else "")]
    return "\n".join(out) + "\n"
