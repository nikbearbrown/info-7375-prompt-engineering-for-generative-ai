"""The bounded loop (GATE.md): one GET per selected board, four exits, state only after a clean approved run."""
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone

from jsagent.resume import ResumeError, load_resume
from jsagent.rule import judge_posting

from .budget import PRODUCTION_BUDGET
from .fetch import http_get
from .policy import BY_NAME, RESUME_PATH, STATE_DIR, PolicyDenied, Workspace, check_request
from .providers import PARSERS, BoardInvalid

EXIT_CODES = {"finished": 0, "incomplete": 10, "budget-exhausted": 11, "error": 12}
STATE_PATH = f"{STATE_DIR}/seen_ids.json"
UNKNOWN = "unknown"


class Ledger:
    """Every action, in order. The repeat rule lives here: one (method, URL) per run."""

    def __init__(self, elapsed=None):
        self.entries = []
        self._taken = set()
        self._elapsed = elapsed or (lambda: None)

    def note(self, event, **fields):
        self.entries.append({"seq": len(self.entries) + 1, "t": self._elapsed(), "event": event, **fields})

    def claim(self, method, url, board):
        key = (method, url)
        if key in self._taken:
            self.note("suppressed", method=method, url=url, board=board,
                      reason="same method and URL already taken in this run; not sent again")
            return False
        self._taken.add(key)
        return True


class _Stop(Exception):
    """A budget limit stopped the loop before its next action."""

    def __init__(self, limit, detail):
        super().__init__(detail)
        self.limit, self.detail = limit, detail


def _observation(board, seeded_path):
    return {
        "order": board.order, "board": board.name, "provider": board.provider, "url": board.url,
        "mode": "seeded" if seeded_path else "live", "source": seeded_path or board.url,
        "deliberate_failure": board.demo_only,
        "outcome": "not_attempted", "reason": None,
        "http_status": None, "error": None, "raw_path": None, "raw_bytes": None, "raw_note": None,
        "postings_in_response": UNKNOWN, "baseline": None, "new_count": UNKNOWN, "new_postings": [],
        "seconds": None,
    }


def _new_posting_record(resume, posting):
    rule = judge_posting(resume, posting)
    return {
        "posting_id": posting["id"], "title": posting["title"], "location": posting["location"]["name"],
        "workplace_type": posting.get("workplace_type"), "url": posting.get("url"),
        "rule_verdict": rule["rule_verdict"],
        "rule_failed_conditions": [e["condition"] for e in rule["rule_justification"] if not e["passed"]],
        "rule_justification": rule["rule_justification"],
    }


def _preflight(ws, selection, demo, seeded):
    """Everything that can be refused before the first request. Returns the boards, or raises ValueError."""
    problem = ws.roots_problem()
    if problem:
        raise ValueError(f"permission roots unsound: {problem}")
    if not selection:
        raise ValueError("no boards selected")
    unknown = [name for name in selection if name not in BY_NAME]
    if unknown:
        raise ValueError(f"not on GATE.md's allow-list: {unknown}")
    boards = [BY_NAME[name] for name in selection]
    urls = [b.url for b in boards]
    duplicates = sorted({u for u in urls if urls.count(u) > 1})
    if duplicates:
        raise ValueError(f"duplicate URL selected (the selection itself is wrong): {duplicates}")
    for board in boards:
        check_request("GET", board.url, demo=demo)  # raises PolicyDenied, e.g. demo-only without --demo-failure
    stray = sorted(set(seeded) - set(selection))
    if stray:
        raise ValueError(f"seeded response given for an unselected board: {stray}")
    for name, path in seeded.items():
        if not ws.check_read(path).is_file():
            raise ValueError(f"seeded response for {name} not found: {path}")
    ws.check_read(RESUME_PATH)
    return boards


def _load_state(ws):
    real = ws.check_read(STATE_PATH)
    if not real.exists():
        return {"boards": {}}
    try:
        state = json.loads(real.read_bytes())
        assert isinstance(state.get("boards"), dict)
        return state
    except (ValueError, AssertionError, AttributeError):
        raise ValueError(f"{STATE_PATH} is not a valid JS2 state file") from None


def run_watch(selection, *, base_dir, demo=False, approve_state_write=False, seeded=None,
              fetcher=http_get, clock=time.monotonic, budget=PRODUCTION_BUDGET, now=None):
    started = clock()
    deadline = started + budget.max_seconds
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    ws = Workspace(base_dir)
    seeded = dict(seeded or {})
    ledger = Ledger(elapsed=lambda: round(clock() - started, 3))
    selection = list(selection)

    seeded_names = [n for n in selection if n in seeded]
    run_mode = ("live" if not seeded_names else "seeded" if len(seeded_names) == len(selection)
                else f"mixed (seeded: {', '.join(seeded_names)})")
    trace = {
        "agent": "jsloop — Job-Search Agent 2", "policy": "GATE.md",
        "started_at": now.isoformat(timespec="seconds"),
        "selection": selection, "demo": demo, "approve_state_write": approve_state_write,
        "run_mode": run_mode,
        "budget": asdict(budget), "budget_label": "production" if budget == PRODUCTION_BUDGET else "test",
        "status": None, "exit_code": None, "stop_reason": None, "error": None,
        "requests_made": 0, "elapsed_seconds": None,
        "boards": [_observation(BY_NAME[n], seeded.get(n)) if n in BY_NAME else {"board": n,
                   "outcome": "not_attempted", "reason": "not on the allow-list",
                   "postings_in_response": UNKNOWN, "new_count": UNKNOWN} for n in selection],
        "state_path": STATE_PATH, "state_updated": False, "state_note": None,
        "trace_path": None, "actions": ledger.entries,
    }

    status = None
    try:
        boards = _preflight(ws, selection, demo, seeded)
        resume = load_resume(ws.check_read(RESUME_PATH))
        prior = _load_state(ws)
    except (ValueError, PolicyDenied, ResumeError, OSError) as exc:
        status, trace["error"] = "error", f"preflight: {exc}"
        for obs in trace["boards"]:
            obs["reason"] = "not attempted: the run stopped at preflight"
        ledger.note("preflight_refused", error=str(exc))
        return _finish(ws, trace, status, stamp, clock, started, deadline, budget, prior=None,
                       current=None, ledger=ledger)

    ledger.note("preflight_ok", boards=selection, demo=demo, approve_state_write=approve_state_write)
    current = {}
    attempted = 0
    try:
        for board, obs in zip(boards, trace["boards"]):
            if attempted >= budget.max_boards:
                raise _Stop("boards", f"board limit {budget.max_boards} reached before {board.name}")
            if board.demo_only:
                ledger.note("label", board=board.name, url=board.url,
                            note="deliberately failing board, selected for the labeled demonstration run")
            if obs["mode"] == "seeded":
                ledger.note("read_seeded", board=board.name, path=obs["source"])
                result_status, result_error = None, None
                body = ws.read_bytes(obs["source"])
                obs["raw_path"], obs["raw_bytes"] = obs["source"], len(body)
            else:
                if trace["requests_made"] >= budget.max_requests:
                    raise _Stop("requests", f"request limit {budget.max_requests} reached before {board.name}")
                remaining = deadline - clock()
                if remaining < budget.min_seconds_to_start_request:
                    raise _Stop("seconds", f"{remaining:.1f} s left before {board.name}; a request needs "
                                           f"{budget.min_seconds_to_start_request:.0f} s")
                check_request("GET", board.url, demo=demo)  # again, at the moment of use
                if not ledger.claim("GET", board.url, board.name):
                    obs["outcome"], obs["reason"] = "suppressed", "repeat of an action already taken"
                    continue
                timeout = min(budget.request_timeout, remaining - budget.finalize_reserve)
                ledger.note("request", method="GET", url=board.url, board=board.name, timeout=timeout)
                trace["requests_made"] += 1
                t0 = clock()
                result = fetcher(board.url, timeout)
                obs["seconds"] = round(clock() - t0, 3)
                ledger.note("response", board=board.name, http_status=result.status, error=result.error,
                            bytes=None if result.body is None else len(result.body))
                obs["http_status"] = result.status
                result_status, result_error, body = result.status, result.error, result.body
                if body is not None:
                    # Saved before parsing, exactly as received.
                    path = ws.write_new(ws.unique_path("evidence/js2", f"{stamp}_{board.name}", ".body"), body)
                    obs["raw_path"], obs["raw_bytes"] = path, len(body)
                    ledger.note("write_raw", board=board.name, path=path)
                else:
                    obs["raw_note"] = "no response body was received, so none was saved"
            attempted += 1

            failure = result_error or (f"HTTP {result_status}"
                                       if result_status is not None and result_status != 200 else None)
            if failure is None:
                try:
                    postings = PARSERS[board.provider](body)
                except BoardInvalid as exc:
                    failure = str(exc)
            if failure is not None:
                obs["outcome"], obs["error"] = "failed", failure
            else:
                obs["outcome"], obs["postings_in_response"] = "ok", len(postings)
                current[board.name] = [p["id"] for p in postings]
                previous = prior["boards"].get(board.name)
                if previous is None:
                    obs["baseline"], obs["new_count"] = True, "baseline"
                else:
                    seen = set(previous["seen_ids"])
                    new = [p for p in postings if p["id"] not in seen]
                    obs["baseline"], obs["new_count"] = False, len(new)
                    obs["new_postings"] = [_new_posting_record(resume, p) for p in new]
            ledger.note("observed", board=board.name, outcome=obs["outcome"], error=obs["error"],
                        postings=obs["postings_in_response"], new=obs["new_count"])

            if clock() > deadline:
                raise _Stop("seconds", f"deadline passed during {board.name} ({clock() - started:.1f} s elapsed)")
    except _Stop as stop:
        status = "budget-exhausted"
        trace["stop_reason"] = {"limit": stop.limit, "detail": stop.detail}
        ledger.note("budget_exhausted", limit=stop.limit, detail=stop.detail)
        for obs in trace["boards"]:
            if obs["outcome"] == "not_attempted":
                obs["reason"] = f"not attempted: {stop.limit} budget exhausted"
    except (PolicyDenied, OSError) as exc:
        status, trace["error"] = "error", f"{exc.__class__.__name__}: {exc}"
        ledger.note("error", error=trace["error"])
        for obs in trace["boards"]:
            if obs["outcome"] == "not_attempted":
                obs["reason"] = "not attempted: the run stopped on a local error"

    if status is None:
        status = "finished" if all(o["outcome"] == "ok" for o in trace["boards"]) else "incomplete"
    return _finish(ws, trace, status, stamp, clock, started, deadline, budget, prior, current, ledger)


def _set_status(trace, status, started, clock):
    trace["status"], trace["exit_code"] = status, EXIT_CODES[status]
    trace["elapsed_seconds"] = round(clock() - started, 3)


def _dump(trace):
    return (json.dumps(trace, indent=2, ensure_ascii=False) + "\n").encode()


def _finish(ws, trace, status, stamp, clock, started, deadline, budget, prior, current, ledger):
    if status == "finished" and clock() > deadline:
        status = "budget-exhausted"
        trace["stop_reason"] = {"limit": "seconds", "detail": "deadline passed before the trace was saved"}
    wants_state = status == "finished" and trace["approve_state_write"]
    if status == "finished" and not wants_state:
        trace["state_note"] = "observation-only run: state not written (no --approve-state-write)"
    elif wants_state:
        trace["state_note"] = "approved state write pending: attempted after this trace was first saved"
    else:
        trace["state_note"] = f"state not written: run status is {status}"
    _set_status(trace, status, started, clock)

    kind = "demo" if trace["demo"] else "normal"
    try:
        trace["trace_path"] = ws.unique_path("runs/js2", f"{stamp}_{kind}", ".json")
        ledger.note("write_trace", path=trace["trace_path"])
        ws.write_new(trace["trace_path"], _dump(trace))
    except (PolicyDenied, OSError) as exc:
        trace["trace_path"] = None
        if status != "error":
            trace["error"] = f"could not save the trace: {exc}"
        _set_status(trace, "error", started, clock)
        return trace
    if not wants_state:
        return trace

    boards = dict(prior["boards"])
    for name, ids in current.items():
        old = set(boards.get(name, {}).get("seen_ids", []))
        boards[name] = {"seen_ids": sorted(old | set(ids)), "updated_at": trace["started_at"],
                        "source": next(o["raw_path"] for o in trace["boards"] if o["board"] == name)}
    state = {"boards": boards, "updated_at": trace["started_at"], "trace": trace["trace_path"]}
    try:
        ledger.note("write_state", path=STATE_PATH)
        ws.replace(STATE_PATH, _dump(state), approve_state_write=trace["approve_state_write"])
        trace["state_updated"] = True
        trace["state_note"] = "approved state write saved"
        _set_status(trace, "finished", started, clock)
    except (PolicyDenied, OSError) as exc:
        trace["error"] = f"state write failed: {exc.__class__.__name__}: {exc}"
        trace["state_note"] = "state not written: the state write failed"
        ledger.note("error", error=trace["error"])
        _set_status(trace, "error", started, clock)
    ws.replace(trace["trace_path"], _dump(trace))
    return trace
