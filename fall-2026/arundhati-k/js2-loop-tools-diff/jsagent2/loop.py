"""The bounded loop (GATE.md sections 1-4): visit boards, record every observation, end with one exit."""

import gzip
import hashlib
import json
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jsagent2 import providers
from jsagent2.policy import STATE_FILE
from jsagent2.transport import PolicyRefused, TransientError

FAILED = {"not-found", "client-error", "transient-failed", "bad-shape", "policy-refused", "budget-cut"}


@dataclass
class RunResult:
    run_id: str
    exit: str
    boards: dict
    observations: list
    unvisited: list = field(default_factory=list)
    budget_hit: str = None
    state_write: str = None
    requests_used: int = 0
    reason: str = ""
    trace_file: str = None


def classify(status, body, ats):
    """One HTTP response -> (board status, postings or None)."""
    if status == 200:
        try:
            jobs = providers.parse(ats, body)
        except providers.BadShape:
            return "bad-shape", None
        return ("empty-unverified", jobs) if not jobs else ("ok", jobs)
    if status == 404:
        return "not-found", None
    if status >= 500:
        return "server-error", None
    return "client-error", None


def is_retryable(status):
    """GATE §4: only server errors (and transport timeouts/connection errors) get the one retry."""
    return status >= 500


def normalise_url(url):
    """GATE §3: the same action = same method + normalised URL (scheme, host, path, sorted query).
    Scheme and host are case-insensitive; the path is kept as is (Ashby board names are case-sensitive)."""
    p = urlsplit(url)
    query = urlencode(sorted(parse_qsl(p.query, keep_blank_values=True)))
    return urlunsplit((p.scheme.lower(), (p.hostname or "") + (f":{p.port}" if p.port else ""), p.path, query, ""))


def exit_for(boards, budget_hit):
    # GATE §1: a permission-policy violation means the run could not run safely -> error, whatever else happened
    if any(b["status"] == "policy-refused" for b in boards.values()):
        return "error"
    if budget_hit:
        return "budget-exhausted"
    statuses = [b["status"] for b in boards.values() if b["status"] != "repeat-skipped"]
    if not statuses or not any(s == "ok" for s in statuses):
        return "error"
    if all(s == "ok" for s in statuses):
        return "finished"
    return "incomplete"


def _key(board):
    return f"{board['ats']}:{board['slug']}"


def run_loop(boards, budgets, policy, transport, now=time.monotonic, sleep=time.sleep, run_id=None, clock_utc=None):
    run_id = run_id or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stamp = clock_utc or (lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    run_dir = f"out/runs/{run_id}"
    start = now()
    obs, report = [], {}

    def observe(**kw):
        kw.setdefault("t_utc", stamp())
        kw["t_run"] = round(now() - start, 3)
        obs.append(kw)

    def finish(result):
        _write_trace(policy, run_dir, result, budgets)
        return result

    # --- config check before any request (exit: error) ------------------------------------------
    urls = []
    for b in boards:
        try:
            urls.append(providers.url_for(b["ats"], b["slug"]))
        except (KeyError, ValueError) as e:
            observe(event="config-error", board=b.get("name"), reason=str(e))
            return finish(RunResult(run_id, "error", {}, obs, reason=f"bad config: {e}"))

    # --- the loop --------------------------------------------------------------------------------
    seen_urls, requests, visited, budget_hit, unvisited = {}, 0, 0, None, []
    for i, (b, url) in enumerate(zip(boards, urls)):
        name = b["name"]
        action = ("GET", normalise_url(url))
        if action in seen_urls:
            observe(event="repeat-skipped", board=name, url=url, same_as=seen_urls[action])
            report[name] = {"status": "repeat-skipped", "postings": None, "new": None, "same_as": seen_urls[action]}
            continue
        if visited >= budgets["max_boards"]:
            budget_hit = "boards"
        elif now() - start >= budgets["max_seconds"]:
            budget_hit = "seconds"
        if budget_hit:
            unvisited = [x["name"] for x in boards[i:] if x["name"] not in report]
            observe(event="budget-exhausted", budget=budget_hit, unvisited=unvisited)
            break
        d = policy.check_request("GET", url)
        observe(event="policy", board=name, url=url, verdict=d.verdict, reason=d.reason)
        if d.verdict != "allow":
            report[name] = {"status": "policy-refused", "postings": None, "new": None, "reason": d.reason}
            continue
        seen_urls[action] = name
        visited += 1

        status, jobs, reason = None, None, ""
        for attempt in (1, 2):
            if requests >= budgets["max_requests"]:
                budget_hit = "requests"
            elif now() - start >= budgets["max_seconds"]:
                budget_hit = "seconds"
            if budget_hit:
                break
            requests += 1
            try:
                code, body = transport(url, budgets["request_timeout_seconds"])
            except TransientError as e:
                observe(event="transport-error", board=name, url=url, attempt=attempt, kind=e.kind, detail=str(e))
                status, reason, retry = "transient-failed", str(e), True
            except PolicyRefused as e:
                observe(event="policy", board=name, url=url, verdict="refuse", reason=str(e))
                status, reason, retry = "policy-refused", str(e), False
            else:
                raw_rel = f"{run_dir}/raw/{i + 1:02d}-{b['slug']}-attempt{attempt}.json.gz"
                w = policy.write_bytes(raw_rel, gzip.compress(body, mtime=0))
                observe(event="response", board=name, ats=b["ats"], url=url, attempt=attempt, http_status=code,
                        bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                        raw_file=raw_rel if w.verdict == "allow" else None)
                status, jobs = classify(code, body, b["ats"])
                reason = f"HTTP {code}"
                retry = is_retryable(code)
                if status == "server-error":
                    status = "transient-failed"
            if retry and attempt == 1:
                observe(event="retry", board=name, after_seconds=budgets["retry_delay_seconds"], why=reason)
                sleep(budgets["retry_delay_seconds"])
                continue
            break

        if budget_hit:
            if status is None or (retry and attempt == 1):
                status = "budget-cut"
            report[name] = _board_entry(status, jobs, reason)
            unvisited = [x["name"] for x in boards[i + 1:] if x["name"] not in report]
            observe(event="budget-exhausted", budget=budget_hit, unvisited=unvisited)
            break
        report[name] = _board_entry(status, jobs, reason)

    # --- new since last run, and the state write (needs approval) -------------------------------
    state = {}
    try:
        state = json.loads(policy.read_bytes(STATE_FILE))
    except FileNotFoundError:
        pass
    new_state = dict(state)
    by_name = {b["name"]: b for b in boards}
    for name, entry in report.items():
        if entry["status"] != "ok":
            continue
        k = _key(by_name[name])
        ids = [j["id"] for j in entry.pop("_jobs")]
        if k not in state:
            entry["baseline"], entry["new"] = True, None
        else:
            prev = set(state[k])
            entry["baseline"], entry["new"] = False, [x for x in ids if x not in prev]
        new_state[k] = sorted(set(state.get(k, [])) | set(ids), key=str)
    for entry in report.values():
        entry.pop("_jobs", None)

    result = RunResult(run_id, exit_for(report, budget_hit), report, obs, unvisited, budget_hit,
                       requests_used=requests)
    refused = [n for n, e in report.items() if e["status"] == "policy-refused"]
    if refused:
        result.reason = f"permission-policy violation: {', '.join(refused)}"
    elif result.exit == "error":
        result.reason = "no board succeeded"
    if result.exit == "error":
        result.state_write = "skipped (exit error)"
    else:
        w = policy.write_bytes(STATE_FILE, json.dumps(new_state, indent=1, sort_keys=True).encode())
        result.state_write = {"allow": "written", "hold": "held-for-approval", "refuse": "refused"}[w.verdict]
        observe(event="state-write", verdict=w.verdict, reason=w.reason)
    observe(event="exit", exit=result.exit, budget_hit=budget_hit, requests_used=requests)
    return finish(result)


def _board_entry(status, jobs, reason):
    entry = {"status": status, "postings": len(jobs) if status in ("ok", "empty-unverified") else None,
             "new": None, "reason": reason}
    if status == "ok":
        entry["_jobs"] = jobs
    return entry


def _write_trace(policy, run_dir, r, budgets):
    trace = {"run_id": r.run_id, "exit": r.exit, "reason": r.reason, "budget_hit": r.budget_hit,
             "unvisited": r.unvisited, "requests_used": r.requests_used, "budgets": budgets,
             "state_write": r.state_write, "boards": r.boards, "observations": r.observations}
    w = policy.write_bytes(f"{run_dir}/trace.json", json.dumps(trace, indent=1, default=str).encode())
    r.trace_file = f"{run_dir}/trace.json" if w.verdict == "allow" else None
    policy.write_bytes(f"{run_dir}/report.md", render_report(trace).encode())


def render_report(t):
    lines = [f"# Run {t['run_id']}", "", f"**Exit: `{t['exit']}`**" + (f" — {t['reason']}" if t["reason"] else ""), ""]
    if t["budget_hit"]:
        lines += [f"Budget hit: **{t['budget_hit']}**. Never visited: {', '.join(t['unvisited']) or '(none)'}", ""]
    lines += ["| board | status | postings | new since last run |", "|---|---|---|---|"]
    for name, b in t["boards"].items():
        if b["status"] == "ok":
            new = "baseline (first run for this board)" if b.get("baseline") else str(len(b["new"]))
        elif b["status"] == "empty-unverified":
            new = "— (empty board, not verified; not reported as 0 new)"
        else:
            new = "—"
        postings = "—" if b["postings"] is None else str(b["postings"])
        lines.append(f"| {name} | {b['status']} ({b.get('reason', '')}) | {postings} | {new} |")
    lines += ["", f"Requests used: {t['requests_used']} / {t['budgets']['max_requests']} · state write: {t['state_write']}", ""]
    return "\n".join(lines)
