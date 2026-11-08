"""The bounded watch loop. Exits, budgets, repeat rule, and error policy follow GATE.md."""

import json
import os
import time
from datetime import datetime, timezone

from agent import adapters, policy

FINISHED = "finished"
INCOMPLETE = "incomplete"
BUDGET_EXHAUSTED = "budget_exhausted"
ERROR = "error"
EXIT_CODES = {FINISHED: 0, ERROR: 1, INCOMPLETE: 2, BUDGET_EXHAUSTED: 3}

RETRY_WAIT_S = 2.0
MAX_IDENTICAL_REQUESTS = 2  # the first try plus the one retry the error policy allows


class Trace:
    def __init__(self, base, path):
        self.base, self.path, self.seq, self.lines = base, path, 0, []

    def log(self, event, **fields):
        self.seq += 1
        rec = {"seq": self.seq, "ts": _now(), "event": event, **fields}
        self.lines.append(json.dumps(rec, sort_keys=True))
        policy.guarded_write(self.base, self.path, "\n".join(self.lines) + "\n")
        return rec


class Budget:
    def __init__(self, limits, clock):
        self.limits = limits
        self.clock = clock
        self.start = clock()
        self.requests = 0

    def elapsed(self):
        return self.clock() - self.start

    def blocked(self):
        """Name of the budget that stops the next request, or None."""
        if self.requests >= self.limits["max_requests"]:
            return "max_requests"
        if self.elapsed() >= self.limits["max_seconds"]:
            return "max_seconds"
        return None


def validate_config(boards, budgets):
    problems = []
    if not isinstance(boards, list) or not boards:
        problems.append("boards must be a non-empty list")
    else:
        for i, b in enumerate(boards):
            if not isinstance(b, dict) or not {"name", "ats", "slug"} <= set(b):
                problems.append(f"board {i} needs name, ats, slug")
            elif b["ats"] not in adapters.PARSERS:
                problems.append(f"board {b['name']}: unknown ats {b['ats']!r}")
    for key in ("max_boards", "max_requests", "max_seconds", "retries_per_board"):
        if not isinstance(budgets.get(key), (int, float)) or budgets[key] < 0:
            problems.append(f"budget {key} missing or negative")
    return problems


def run(base, boards, budgets, fetcher, run_id, clock=time.monotonic, sleep=time.sleep,
        seeded=False):
    run_dir = os.path.join("jobs", "runs", run_id)
    state_dir = state_dir_for(run_id, seeded)
    trace = Trace(base, os.path.join(run_dir, "trace.jsonl"))
    trace.log("run_start", run_id=run_id, seeded=seeded, budgets=budgets,
              boards=[b.get("name") for b in boards] if isinstance(boards, list) else None)

    problems = validate_config(boards, budgets)
    if problems:
        return _finish(base, trace, run_dir, run_id, ERROR, [], {}, seeded,
                       error={"step": "config", "problems": problems})

    unique, seen_keys = [], set()
    for b in boards:
        key = (b["ats"], b["slug"].lower())
        if key in seen_keys:
            trace.log("config_duplicate_removed", board=b["name"], ats=b["ats"], slug=b["slug"])
            continue
        seen_keys.add(key)
        unique.append(b)

    budget = Budget(budgets, clock)
    identical = {}
    results, stop = [], None

    for index, board in enumerate(unique):
        if index >= budgets["max_boards"]:
            stop = {"budget": "max_boards", "limit": budgets["max_boards"]}
        elif budget.blocked():
            name = budget.blocked()
            stop = {"budget": name, "limit": budgets[name]}
        if stop:
            stop["not_attempted"] = [b["name"] for b in unique[index:]]
            trace.log("budget_stop", **stop)
            break
        try:
            result = _watch_board(base, board, budgets, budget, fetcher, trace, identical,
                                  run_dir, sleep, state_dir)
        except policy.PolicyDenied as e:
            trace.log("policy_denied", board=board["name"], reason=str(e))
            return _finish(base, trace, run_dir, run_id, ERROR, results, {}, seeded,
                           error={"step": f"board {board['name']}", "policy": str(e)})
        results.append(result)
        if result.get("stopped_by_budget"):
            stop = {"budget": result["stopped_by_budget"],
                    "limit": budgets[result["stopped_by_budget"]],
                    "not_attempted": [b["name"] for b in unique[index + 1:]]}
            trace.log("budget_stop", **stop)
            break

    if stop:
        status = BUDGET_EXHAUSTED
    elif results and all(r["status"] != "ok" for r in results):
        status = ERROR
    elif any(r["status"] != "ok" for r in results):
        status = INCOMPLETE
    else:
        status = FINISHED

    new_by_board = {}
    if status != ERROR:
        for r in results:
            if r["status"] == "ok":
                new_by_board[r["name"]] = _update_state(base, state_dir, r, run_id, trace)
    error = {"step": "all boards", "problems": ["every board failed"]} if status == ERROR else None
    return _finish(base, trace, run_dir, run_id, status, results, new_by_board, seeded,
                   budget=budget, stop=stop, error=error)


def _watch_board(base, board, budgets, budget, fetcher, trace, identical, run_dir, sleep,
                 state_dir):
    url = adapters.board_url(board["ats"], board["slug"])
    key = ("GET", policy.normalize_url(url))
    result = {"name": board["name"], "ats": board["ats"], "slug": board["slug"], "url": url,
              "attempts": 0, "count": None, "raw_files": []}
    retries_left = budgets["retries_per_board"]

    while True:
        blocked = budget.blocked()
        if blocked:
            result.update(status="failed:budget", stopped_by_budget=blocked)
            trace.log("board_result", **_public(result))
            return result
        if identical.get(key, 0) >= MAX_IDENTICAL_REQUESTS:
            trace.log("repeat_blocked", board=board["name"], url=url, times=identical[key])
            result.update(status="failed:repeat_blocked")
            trace.log("board_result", **_public(result))
            return result

        identical[key] = identical.get(key, 0) + 1
        budget.requests += 1
        result["attempts"] += 1
        trace.log("request", board=board["name"], method="GET", url=url,
                  attempt=result["attempts"], request_no=budget.requests)
        resp = fetcher.get(url)

        raw_path = None
        if resp.http_status is not None:
            raw_path = os.path.join(run_dir, "raw", f"{board['name']}-{result['attempts']}.json")
            policy.guarded_write(base, raw_path, resp.body)
            result["raw_files"].append(raw_path)
        trace.log("response", board=board["name"], attempt=result["attempts"],
                  http_status=resp.http_status, error=resp.error, bytes=len(resp.body),
                  elapsed_ms=resp.elapsed_ms, seeded=resp.seeded, raw_file=raw_path,
                  host_gap_wait_s=getattr(fetcher, "last_wait_s", 0.0))
        result["http_status"] = resp.http_status

        transient = resp.error is not None or (resp.http_status or 0) >= 500
        if transient:
            if retries_left > 0:
                retries_left -= 1
                trace.log("retry_wait", board=board["name"], seconds=RETRY_WAIT_S,
                          reason=resp.error or f"http {resp.http_status}")
                sleep(RETRY_WAIT_S)
                continue
            result.update(status="failed:unreachable", reason=resp.error or f"http {resp.http_status}")
            break
        if resp.http_status == 404:
            result.update(status="failed:not_found", reason="board name not found (404)")
            break
        if resp.http_status != 200:
            result.update(status=f"failed:http_{resp.http_status}",
                          reason=f"server refused with {resp.http_status}")
            break
        try:
            postings = adapters.PARSERS[board["ats"]](json.loads(resp.body))
        except (ValueError, adapters.BadResponse) as e:
            result.update(status="failed:bad_response", reason=str(e))
            break
        ids, dups = [], 0
        for p in postings:
            if p["id"] in ids:
                dups += 1
            else:
                ids.append(p["id"])
        previous = load_state(base, board["name"], state_dir)
        if not ids and previous and previous["count"] > 0:
            # GATE.md error policy: empty after a non-empty baseline is not "no news".
            result.update(status="suspect:empty_after_nonempty", count=None, observed_count=0,
                          duplicate_ids=0, previous_count=previous["count"],
                          reason=f"0 postings now, {previous['count']} in the baseline")
            break
        result.update(status="ok", count=len(ids), ids=ids, duplicate_ids=dups,
                      titles={p["id"]: p["title"] for p in postings})
        break

    trace.log("board_result", **_public(result))
    return result


def state_dir_for(run_id, seeded):
    """Live runs share jobs/state. A seeded run never touches it: each scenario family
    (the run id without its last "-part") keeps its own baseline under jobs/seeded-state."""
    if not seeded:
        return os.path.join("jobs", "state")
    return os.path.join("jobs", "seeded-state", run_id.rsplit("-", 1)[0])


def _state_path(state_dir, name):
    return os.path.join(state_dir, f"{name}.state.json")


def load_state(base, name, state_dir=os.path.join("jobs", "state")):
    path = _state_path(state_dir, name)
    if not os.path.exists(os.path.join(base, path)):
        return None
    return json.loads(policy.guarded_read(base, path))


def _update_state(base, state_dir, result, run_id, trace):
    previous = load_state(base, result["name"], state_dir)
    if previous is None:
        new_ids, baseline = [], True
    else:
        known = set(previous["ids"])
        new_ids, baseline = [i for i in result["ids"] if i not in known], False
    state = {"board": result["name"], "ats": result["ats"], "slug": result["slug"],
             "count": result["count"], "ids": result["ids"], "updated_by_run": run_id}
    policy.guarded_write(base, _state_path(state_dir, result["name"]),
                         json.dumps(state, indent=2) + "\n")
    trace.log("state_write", board=result["name"], baseline=baseline,
              previous_count=None if previous is None else previous["count"],
              count=result["count"], new=len(new_ids))
    return {"baseline": baseline, "new_ids": new_ids,
            "new": [{"id": i, "title": result["titles"].get(i)} for i in new_ids]}


def _public(result):
    return {k: v for k, v in result.items() if k not in ("ids", "titles")}


def _finish(base, trace, run_dir, run_id, status, results, new_by_board, seeded,
            budget=None, stop=None, error=None):
    needs_human = []
    for r in results:
        if r["status"] != "ok":
            needs_human.append(f"{r['name']}: {r['status']} ({r.get('reason', '')})".strip())
    if stop:
        needs_human.append(f"budget {stop['budget']} hit; not attempted: {stop['not_attempted']}")
    if error:
        needs_human.append(f"error at {error['step']}")
    summary = {
        "run_id": run_id,
        "seeded": seeded,
        "exit": status,
        "exit_code": EXIT_CODES[status],
        "requests": budget.requests if budget else 0,
        "elapsed_s": round(budget.elapsed(), 2) if budget else 0,
        "boards": [{**_public(r), **new_by_board.get(r["name"], {})} for r in results],
        "budget_stop": stop,
        "error": error,
        "needs_human": needs_human,
    }
    policy.guarded_write(base, os.path.join(run_dir, "summary.json"),
                         json.dumps(summary, indent=2) + "\n")
    trace.log("run_end", exit=status, exit_code=EXIT_CODES[status], needs_human=needs_human)
    return summary


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
