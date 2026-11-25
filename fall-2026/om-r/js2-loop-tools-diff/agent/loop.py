"""The JS2 loop: watch several boards across two ATS systems, implemented
against GATE.md.

Exits (exactly one, always printed): finished / incomplete / budget-exhausted
/ error. Budgets, repeat rule, error policy, and permissions are as GATE.md
states; the numbered comments below point at the clause each block enforces.

    python3 -m agent.loop --boards gitlab stripe palantir \\
        --approve-new-board gitlab --approve-new-board stripe --approve-new-board palantir

--approve-new-board is needed only the first time a board is watched (no
state file yet). Budgets are not settable from the command line: they change
only by editing GATE.md and the constants below together.
"""
import argparse
import json
import sys
import time
import traceback
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from agent import boards as boards_mod
from agent import fetch as fetch_mod
from agent.permissions import WritePolicy

ROOT = Path(__file__).resolve().parent.parent

# GATE.md "Budgets" - change only together with GATE.md.
MAX_BOARDS_PER_RUN = 5
MAX_REQUESTS_PER_RUN = 15
MAX_SECONDS_PER_RUN = 120
DEFAULT_BUDGETS = {"max_boards": MAX_BOARDS_PER_RUN,
                   "max_requests": MAX_REQUESTS_PER_RUN,
                   "max_seconds": MAX_SECONDS_PER_RUN}
_BUDGET_NAMES = {"max_boards": "boards", "max_requests": "requests", "max_seconds": "seconds"}

# GATE.md "Error policy".
MAX_RETRIES = 2
BACKOFF_S = 1.0

EXITS = ("finished", "incomplete", "budget-exhausted", "error")


class BudgetExhausted(Exception):
    def __init__(self, budget, limit):
        super().__init__(f"{budget} budget exhausted (limit {limit})")
        self.budget, self.limit = budget, limit


class BoardFailed(Exception):
    def __init__(self, error, attempts, retried):
        super().__init__(error)
        self.error, self.attempts, self.retried = error, attempts, retried


class StateCorrupt(Exception):
    pass


def is_transient(exc):
    """GATE.md: retry ONLY a timeout or a 5xx. Never a 404, never malformed."""
    if isinstance(exc, urllib.error.HTTPError):
        return 500 <= exc.code < 600
    if isinstance(exc, TimeoutError):  # socket.timeout is TimeoutError on 3.10+
        return True
    if isinstance(exc, urllib.error.URLError):
        return isinstance(exc.reason, TimeoutError)
    return False


def describe(exc):
    return f"{type(exc).__name__}: {exc}"


class _Meter:
    """Counts every request and enforces the request and seconds budgets
    BEFORE a request is made - a budget hit stops the request, it is not
    merely logged."""

    def __init__(self, fetch, budgets, clock):
        self.fetch, self.budgets, self.clock = fetch, budgets, clock
        self.start = clock()
        self.requests = 0

    def elapsed(self):
        return self.clock() - self.start

    def check(self):
        if self.elapsed() >= self.budgets["max_seconds"]:
            raise BudgetExhausted("seconds", self.budgets["max_seconds"])
        if self.requests >= self.budgets["max_requests"]:
            raise BudgetExhausted("requests", self.budgets["max_requests"])

    def request(self, url):
        self.check()
        self.requests += 1
        remaining = self.budgets["max_seconds"] - self.elapsed()
        return self.fetch(url, timeout=max(0.1, min(fetch_mod.TIMEOUT_S, remaining)))


def _fetch_page(meter, url, sleep):
    attempt = 0
    while True:
        try:
            return meter.request(url), attempt + 1
        except BudgetExhausted:
            raise
        except Exception as e:  # classified below; nothing is swallowed
            if not is_transient(e):
                raise BoardFailed(describe(e), attempt + 1, retried=attempt > 0) from e
            if attempt >= MAX_RETRIES:
                raise BoardFailed(f"{describe(e)} (gave up after {MAX_RETRIES} retries)",
                                  attempt + 1, retried=True) from e
            attempt += 1
            sleep(BACKOFF_S)


def _fetch_board(meter, board, sleep):
    """Return (pages of raw bytes, postings, request count)."""
    raws, postings, page, requests = [], [], 0, 0
    while True:
        url = boards_mod.page_url(board, page)
        try:
            raw, n = _fetch_page(meter, url, sleep)
        except BoardFailed as e:
            e.attempts += requests
            raise
        requests += n
        try:
            items, has_more = boards_mod.parse_page(board, raw)
        except boards_mod.MalformedResponse as e:
            raise BoardFailed(describe(e), requests, retried=False) from e
        raws.append(raw)
        postings.extend(items)
        if not has_more:
            return raws, postings, requests
        page += 1


def _load_state(policy, board):
    path = policy.state_path(board)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text())
        if not isinstance(state, dict) or state.get("board") != board or not isinstance(state.get("seen_ids"), list):
            raise ValueError(f"unexpected shape (board={state.get('board') if isinstance(state, dict) else '?'!r})")
        return state
    except (OSError, ValueError) as e:
        raise StateCorrupt(f"state file {path} is unreadable: {describe(e)}") from e


def _record_board(policy, board, raws, postings, state, stamp, at):
    """Save evidence, apply the repeat rule, update state. Returns the board
    entry for the report."""
    # Repeat rule: identity is (board, posting id). Duplicate ids inside one
    # response (e.g. across Lever pages) are collapsed, first one wins.
    unique, ids = [], set()
    for p in postings:
        if p["id"] not in ids:
            ids.add(p["id"])
            unique.append(p)

    evidence = []
    for i, raw in enumerate(raws):
        suffix = "" if len(raws) == 1 else f"_p{i}"
        path = policy.root / "evidence" / f"{board}_{stamp}{suffix}.json"
        policy.write_bytes(path, raw)  # exactly as received
        evidence.append(str(path.relative_to(policy.root)))

    baseline = state is None
    if baseline:
        state = {"board": board, "ats": boards_mod.ats_of(board), "seen_ids": [], "runs": []}
        new, removed = [], []
    else:
        seen = set(state["seen_ids"])
        new = [p for p in unique if p["id"] not in seen]
        # Removal: in the previous successful fetch, absent from this one.
        # State written before last_fetch_ids existed falls back to seen_ids.
        previous = set(state.get("last_fetch_ids", state["seen_ids"]))
        removed = sorted(previous - ids, key=str)

    state["seen_ids"] = sorted(set(state["seen_ids"]) | ids, key=str)
    state["last_fetch_ids"] = sorted(ids, key=str)
    state["runs"].append({"at": at, "baseline": baseline, "evidence_files": evidence,
                          "postings_in_response": len(unique), "new_ids": [p["id"] for p in new],
                          "removed_ids": removed})
    policy.write_bytes(policy.state_path(board), (json.dumps(state, indent=2) + "\n").encode())
    return {"board_status": "ok", "error": None, "baseline": baseline, "new": new, "removed": removed,
            "postings_in_response": len(unique), "evidence_files": evidence}


def run(boards, *, root=ROOT, fetch=fetch_mod.fetch, budgets=None, approved_new_boards=(),
        sleep=time.sleep, clock=time.monotonic, now=None):
    unknown = set(budgets or {}) - set(DEFAULT_BUDGETS)
    if unknown:
        raise ValueError(f"unknown budget(s) {sorted(unknown)}")
    budgets = {**DEFAULT_BUDGETS, **(budgets or {})}
    now = now or datetime.now(timezone.utc)
    stamp, at = now.strftime("%Y%m%dT%H%M%SZ"), now.isoformat(timespec="seconds")
    policy = WritePolicy(root, approved_new_boards)
    meter = _Meter(fetch, budgets, clock)
    report = {"started_at": at, "exit": None, "error": None, "budgets": budgets, "budget_hit": None,
              "requests_made": 0, "elapsed_s": 0.0, "boards": {}, "not_attempted": [],
              "duplicates_skipped": []}

    try:
        # Repeat rule, run level: a board is fetched at most once per run.
        plan = []
        for b in boards:
            boards_mod.ats_of(b)  # unknown board -> ValueError -> exit error
            (report["duplicates_skipped"] if b in plan else plan).append(b)

        # Pre-flight, before any request: corrupt state is a run-level error;
        # a new board without approval is refused without spending budget.
        states = {}
        for b in plan:
            states[b] = _load_state(policy, b)
            if states[b] is None and b not in policy.approved_new_boards:
                report["boards"][b] = {"board_status": "refused", "new": [], "removed": [],
                                       "error": f"new board: no state yet and not approved "
                                                f"(--approve-new-board {b})"}
        runnable = [b for b in plan if b not in report["boards"]]

        attempted = 0
        for i, b in enumerate(runnable):
            if attempted >= budgets["max_boards"]:
                report["budget_hit"] = {"budget": "boards", "limit": budgets["max_boards"]}
                report["not_attempted"] = runnable[i:]
                break
            before = meter.requests
            try:
                meter.check()
                attempted += 1
                raws, postings, n = _fetch_board(meter, b, sleep)
            except BudgetExhausted as e:
                report["budget_hit"] = {"budget": e.budget, "limit": e.limit}
                board_requests = meter.requests - before
                if board_requests:
                    # Started but cut off mid-board (pagination or retry):
                    # partial data is discarded, state untouched.
                    report["boards"][b] = {"board_status": "interrupted", "new": [], "removed": [],
                                           "error": f"{e} after {board_requests} request(s) for this board; "
                                                    f"partial data discarded, state unchanged"}
                    report["not_attempted"] = runnable[i + 1:]
                else:
                    attempted -= 1
                    report["not_attempted"] = runnable[i:]
                break
            except BoardFailed as e:
                report["boards"][b] = {"board_status": "failed", "new": [], "removed": [], "error": e.error,
                                       "attempts": e.attempts, "retried": e.retried}
                continue
            entry = _record_board(policy, b, raws, postings, states[b], stamp, at)
            entry["requests"] = n
            report["boards"][b] = entry

        statuses = [report["boards"][b]["board_status"] for b in runnable if b in report["boards"]]
        if report["budget_hit"]:
            report["exit"] = "budget-exhausted"
        elif statuses and all(s == "failed" for s in statuses):
            report["exit"] = "error"
            report["error"] = f"all {len(statuses)} attempted board(s) failed"
        elif any(report["boards"][b]["board_status"] == "refused" for b in plan):
            report["exit"] = "incomplete"
            report["not_attempted"] = [b for b in plan if report["boards"][b]["board_status"] == "refused"]
        else:
            report["exit"] = "finished"
    except Exception as e:
        report["exit"] = "error"
        report["error"] = describe(e)
        report["traceback"] = traceback.format_exc()

    report["requests_made"] = meter.requests
    report["elapsed_s"] = round(meter.elapsed(), 3)
    try:
        log_path = policy.root / "logs" / f"run_{stamp}.json"
        policy.write_bytes(log_path, (json.dumps(report, indent=2, default=str) + "\n").encode())
        report["log_file"] = str(log_path.relative_to(policy.root))
    except Exception as e:
        report["log_file"] = None
        report["log_error"] = describe(e)
    assert report["exit"] in EXITS
    return report


def format_report(report):
    b = report["budgets"]
    out = [f"JS2 loop run {report['started_at']}  EXIT: {report['exit']}"]
    if report["budget_hit"]:
        out.append(f"  budget hit: {report['budget_hit']['budget']} (limit {report['budget_hit']['limit']})")
    if report["error"]:
        out.append(f"  error: {report['error']}")
    out.append(f"  requests {report['requests_made']}/{b['max_requests']}  "
               f"elapsed {report['elapsed_s']}s/{b['max_seconds']}s  board limit {b['max_boards']}")
    for name, r in report["boards"].items():
        s = r["board_status"]
        if s == "ok":
            if r["baseline"]:
                detail = f"BASELINE: {r['postings_in_response']} postings recorded as seen, none reported as new"
            else:
                detail = (f"{r['postings_in_response']} postings in response, {len(r['new'])} new, "
                          f"{len(r['removed'])} removed")
            out.append(f"  {name:<20} ok           {detail}  ({r['requests']} request(s))")
        elif s == "failed":
            out.append(f"  {name:<20} FAILED       {r['error']}  "
                       f"({r['attempts']} attempt(s), {'retried' if r['retried'] else 'not retried'})")
        else:
            out.append(f"  {name:<20} {s.upper():<12} {r['error']}")
    for name in report["not_attempted"]:
        if name not in report["boards"]:
            out.append(f"  {name:<20} NOT ATTEMPTED (stopped by {report['budget_hit']['budget']} budget)")
    for name in report["duplicates_skipped"]:
        out.append(f"  {name:<20} duplicate in board list, fetched once")
    new = [(n, p) for n, r in report["boards"].items() for p in r["new"]]
    if new:
        out.append("  new postings:")
        out.extend(f"    - [{n}] id {p['id']}: {p['title']}\n      {p['url']}" for n, p in new)
    removed = [(n, i) for n, r in report["boards"].items() for i in r.get("removed", [])]
    if removed:
        out.append("  removed postings (in the previous fetch, absent from this one):")
        out.extend(f"    - [{n}] id {i}" for n, i in removed)
    if report.get("log_file"):
        out.append(f"  run log: {report['log_file']}")
    elif report.get("log_error"):
        out.append(f"  run log NOT written: {report['log_error']}")
    return "\n".join(out)


EXIT_CODES = {"finished": 0, "error": 1, "incomplete": 3, "budget-exhausted": 4}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boards", nargs="+", required=True, choices=sorted(boards_mod.BOARDS))
    ap.add_argument("--approve-new-board", action="append", default=[], metavar="NAME",
                    choices=sorted(boards_mod.BOARDS),
                    help="allow creating state for this board on its first run (repeatable)")
    args = ap.parse_args(argv)
    report = run(args.boards, approved_new_boards=set(args.approve_new_board))
    print(format_report(report))
    return EXIT_CODES[report["exit"]]


if __name__ == "__main__":
    sys.exit(main())
