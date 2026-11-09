"""The bounded loop (GATE.md, every section).

One run: check the plan against the configured boards; then, for each board and within
the budgets, ask the policy, GET the board once, save the raw bytes, and only then read
them. The exit is computed from what happened, never assumed:

  finished          every normal board usable, results saved, approved state written
  incomplete        a normal board usable but another board failed (the failure
                    control's expected 404 included), or the approval is missing or names
                    another run or file; usable results are provisional, state untouched
  budget-exhausted  a board, request or time limit stopped required work
  error             no normal board usable, the failure control did not fail as
                    expected, a policy denial, a damaged state, or a required write failed

When two apply, the earlier one in this order wins: error, budget-exhausted, incomplete.
Only a finished run replaces the state. Every run that has a folder gets results.json,
results.md, trace.json and trace.md, whatever its exit."""

import datetime as dt
import gzip
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass

from jobwatch import ats, boards, net, report, rule, state
from jobwatch.errors import InputError, PolicyDenied, StateError
from jobwatch.files import Files
from jobwatch.policy import PERSONA_FILE, STATE_FILE, Policy
from jobwatch.resume import validate_resume

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


@dataclass(frozen=True)
class Budget:
    """GATE.md 'Budgets'. Changed only by a dated change to GATE.md before the next run."""

    max_boards: int = 4
    max_requests: int = 4
    max_seconds: float = 30.0
    max_request_seconds: float = 5.0


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Small pieces, named so each GATE.md rule has one place in the code ---------------------

def unique_boards(requested):
    """Repeat rule: the same ATS and slug (trimmed, lowercased) is one board; later
    copies are logged and never fetched."""
    unique, duplicates = [], []
    for name in requested:
        key = boards.normalize_name(name)
        if key in unique:
            duplicates.append((name, key))
        else:
            unique.append(key)
    return unique, duplicates


def budget_stop(used, budget, now, run_deadline):
    """The limit that forbids starting another board, or None."""
    if used["boards"] >= budget.max_boards:
        return "boards"
    if used["requests"] >= budget.max_requests:
        return "requests"
    if now >= run_deadline:
        return "seconds"
    return None


def request_deadline(now, run_deadline, budget):
    return min(now + budget.max_request_seconds, run_deadline)


def classify_response(board, response):
    """(outcome, postings, reason) for one response, read only after it was saved."""
    if board.role == "failure-control":
        if response.status == 404:
            return "failed-as-expected", None, "HTTP 404, as expected for the failure control"
        return "failure-control-broke", None, f"the failure control answered HTTP {response.status}, not the expected 404"
    if 300 <= response.status < 400:
        return "unverified", None, f"HTTP {response.status} redirect to {response.location!r} was not followed"
    if response.status != 200:
        return "unverified", None, f"HTTP {response.status}"
    try:
        postings = ats.parse(board.ats, response.body)
    except InputError as error:
        return "unverified", None, f"malformed payload: {error}"
    if not postings:
        return "unverified", None, "empty jobs list: the board answered 200 with no postings, so it could not be verified"
    return "usable", postings, None


def may_advance_state(status):
    return status == "finished"


# The run ---------------------------------------------------------------------------------

class _Run:
    """What one run has recorded so far: the trace events and one row per board."""

    def __init__(self, run_id, requested, budget, approval, clock, wall):
        self.run_id, self.requested, self.budget, self.approval = run_id, list(requested), budget, approval
        self.clock, self.wall = clock, wall
        self.started = clock()
        self.started_at = wall()
        self.run_deadline = self.started + budget.max_seconds
        self.events, self.rows, self.plan = [], {}, []
        self.used = {"boards": 0, "requests": 0}

    def event(self, kind, **fields):
        self.events.append({"seq": len(self.events) + 1, "at": self.wall(), "event": kind, **fields})

    def add_board(self, board):
        self.plan.append(board)
        self.rows[board.name] = {"board": board.name, "role": board.role, "url": board.url,
                                 "outcome": "not-checked", "jobs": None, "baseline": None,
                                 "new_keys": None, "new_postings": None, "reason": None, "provisional": True}

    def not_checked(self, boards_left, why):
        for board in boards_left:
            self.rows[board.name]["reason"] = why
            self.event("not-checked", board=board.name, reason=why)

    def result(self, status, reason, state_advanced, approval_problem):
        for row in self.rows.values():
            row["provisional"] = not state_advanced
        used = dict(self.used, seconds=round(self.clock() - self.started, 3))
        return {
            "run_id": self.run_id,
            "status": status,
            "reason": reason,
            "state_advanced": state_advanced,
            "started_at": self.started_at,
            "ended_at": self.wall(),
            "requested": self.requested,
            "plan": [b.name for b in self.plan],
            "budget": asdict(self.budget),
            "used": used,
            "approval": {"given": str(self.approval) if self.approval is not None else None,
                         "problem": approval_problem},
            "boards": [self.rows[b.name] for b in self.plan],
            "trace": "trace.json",
        }

    def trace(self, result):
        return {"run_id": self.run_id, "status": result["status"], "reason": result["reason"],
                "state_advanced": result["state_advanced"], "budget": result["budget"], "used": result["used"],
                "events": self.events + [{"seq": len(self.events) + 1, "at": result["ended_at"], "event": "exit",
                                          "status": result["status"], "reason": result["reason"]}]}


def _write_outputs(files, run_rel, record, result):
    trace = record.trace(result)
    files.write_bytes(f"{run_rel}/results.json", _json(result))
    files.write_bytes(f"{run_rel}/results.md", report.results_md(result).encode("utf-8"))
    files.write_bytes(f"{run_rel}/trace.json", _json(trace))
    files.write_bytes(f"{run_rel}/trace.md", report.trace_md(trace).encode("utf-8"))


def _json(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def run(*, root, run_id, requested, approval=None, configured=boards.CONFIGURED, budget=Budget(),
        fetch=net.https_get, clock=time.monotonic, wall=utc_now):
    record = _Run(run_id, requested, budget, approval, clock, wall)

    # Setup. Before the run folder exists there is nowhere to write evidence.
    if not isinstance(run_id, str) or not RUN_ID.match(run_id):
        return record.result("error", f"invalid run id {run_id!r}: use letters, digits, '.', '_' or '-'", False, None)
    policy = Policy(root, run_id, boards.approved_urls(configured), approval)
    files = Files(policy)
    run_rel = f"runs/{run_id}"
    try:
        if files.exists(run_rel):
            return record.result("error", f"{run_rel} already exists; a run never overwrites another run's evidence",
                                 False, policy.approval_problem())
        files.mkdir(run_rel)
    except (OSError, PolicyDenied) as error:
        return record.result("error", f"could not create {run_rel}: {error}", False, policy.approval_problem())

    def finish(status, reason, state_advanced=False):
        result = record.result(status, reason, state_advanced, policy.approval_problem())
        try:
            _write_outputs(files, run_rel, record, result)
        except (OSError, PolicyDenied) as error:
            result = record.result("error", f"required write failed: the run's results: {error}", False,
                                   policy.approval_problem())
        return result

    try:
        persona = json.loads(files.read_bytes(PERSONA_FILE).decode("utf-8"))
        validate_resume(persona)
    except (OSError, ValueError, InputError, PolicyDenied) as error:
        return finish("error", f"the persona could not be used: {error}")
    try:
        before = state.load_state(files)
    except (StateError, PolicyDenied, OSError) as error:
        return finish("error", f"the state could not be used: {error}")

    # The plan: every board must be configured before anything is requested.
    names, duplicates = unique_boards(requested)
    for original, key in duplicates:
        record.event("duplicate", board=key, detail=f"{original!r} repeats {key}; it is fetched once")
    for name in names:
        board = boards.lookup(name, configured)
        if board is None:
            record.event("policy-denied", board=name, rule="endpoint", detail="not a configured board")
            return finish("error", f"policy denial: {name} is not a configured board; nothing was requested")
        record.add_board(board)

    # The loop.
    postings_of, stopped_by, hard_error, control_broke = {}, None, None, False
    for index, board in enumerate(record.plan):
        limit = budget_stop(record.used, budget, clock(), record.run_deadline)
        if limit:
            stopped_by = limit
            record.not_checked(record.plan[index:], f"budget: {limit} limit reached before this board")
            break
        record.used["boards"] += 1
        try:
            policy.check_request("GET", board.url)
        except PolicyDenied as error:
            record.event("policy-denied", board=board.name, rule=error.rule, detail=error.detail)
            hard_error = f"policy denial for {board.name}: {error}"
            break
        row = record.rows[board.name]
        start = clock()
        deadline = request_deadline(start, record.run_deadline, budget)
        cut_by_run = deadline < start + budget.max_request_seconds
        record.used["requests"] += 1
        at = wall()
        try:
            response = fetch(board.url, deadline)
        except (net.Timeout, net.ConnectionFailed) as error:
            if isinstance(error, net.Timeout) and cut_by_run:
                why = "timeout: stopped at the run's time limit"
            elif isinstance(error, net.Timeout):
                why = f"timeout: no complete response within {budget.max_request_seconds:g} s"
            else:
                why = f"connection failed: {error}"
            row.update(outcome="unverified", reason=why)
            record.events.append({"seq": len(record.events) + 1, "at": at, "event": "request", "board": board.name,
                                  "url": board.url, "elapsed_s": round(clock() - start, 3), "status": None,
                                  "bytes": None, "sha256": None, "raw": None, "outcome": "unverified",
                                  "jobs": None, "reason": why})
            if isinstance(error, net.Timeout) and cut_by_run:
                stopped_by = "seconds"
                record.not_checked(record.plan[index + 1:], "budget: seconds limit reached before this board")
                break
            continue
        elapsed = round(clock() - start, 3)
        raw_rel = f"raw/{board.ats}-{board.slug}.body.gz"
        try:
            files.write_bytes(f"{run_rel}/{raw_rel}", gzip.compress(response.body, mtime=0))
        except (OSError, PolicyDenied) as error:
            hard_error = f"required write failed: {raw_rel}: {error}"
            break
        outcome, postings, why = classify_response(board, response)
        row.update(outcome=outcome, reason=why, jobs=len(postings) if postings is not None else None)
        if postings is not None:
            postings_of[board.name] = postings
        if outcome == "failure-control-broke":
            control_broke = True
        record.events.append({"seq": len(record.events) + 1, "at": at, "event": "request", "board": board.name,
                              "url": board.url, "elapsed_s": elapsed, "status": response.status,
                              "content_type": response.content_type, "bytes": len(response.body),
                              "sha256": hashlib.sha256(response.body).hexdigest(), "raw": raw_rel,
                              "outcome": outcome, "jobs": row["jobs"], "reason": why})

    # What the usable boards show, compared with the saved state.
    normal = [b for b in record.plan if b.role == "normal"]
    usable = [b for b in normal if record.rows[b.name]["outcome"] == "usable"]
    for board in usable:
        postings = postings_of[board.name]
        keys = [p.key for p in postings]
        fresh = state.new_keys(before, board.name, keys)
        row = record.rows[board.name]
        if fresh is None:
            row.update(baseline=True, new_keys=[], new_postings=[])
        else:
            by_key = {p.key: p for p in postings}
            row.update(baseline=False, new_keys=fresh,
                       new_postings=[rule.rule_verdict(persona, by_key[key]) for key in fresh])

    # The exit.
    failed = [b.name for b in record.plan if record.rows[b.name]["outcome"] != "usable"]
    if hard_error:
        status, reason = "error", hard_error
    elif control_broke:
        status, reason = "error", "the failure control did not fail as expected, so this run cannot show the error policy"
    elif stopped_by:
        status, reason = "budget-exhausted", f"budget: the {stopped_by} limit stopped the run; not finished: {failed}"
    elif not usable:
        status, reason = "error", "no normal board was usable"
    elif failed:
        status, reason = "incomplete", f"not every board could be verified: {failed}; results are provisional"
    else:
        status, reason = "finished", "every board was usable"

    if not may_advance_state(status):
        return finish(status, reason)
    if clock() >= record.run_deadline:
        return finish("budget-exhausted", "budget: the seconds limit was reached before the state could be saved")
    problem = policy.approval_problem()
    if problem:
        return finish("incomplete", f"the state was not saved: {problem}; results are provisional")

    snapshots = {b.name: (b.ats, b.slug, [p.key for p in postings_of[b.name]]) for b in usable}
    after = state.advanced(before, run_id, wall(), snapshots)
    # Evidence and results are saved before the state is replaced (GATE.md 'Error policy').
    result = finish(status, reason, state_advanced=True)
    if result["status"] != status:
        return result
    try:
        state.save_state(files, after)
    except (OSError, PolicyDenied, StateError) as error:
        record.event("state-not-saved", detail=str(error))
        return finish("error", f"required write failed: {STATE_FILE}: {error}")
    return result
