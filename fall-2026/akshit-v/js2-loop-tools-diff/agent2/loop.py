"""The bounded watch loop (GATE.md sections 2–5).

One pass over the planned boards. Every step is appended to a trace. The loop ends in
exactly one exit: finished, incomplete, budget_exhausted, or error.
"""
import json
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit

from agent2 import policy, providers

REQUEST_TIMEOUT = 20
RETRY_WAIT = 2


@dataclass(frozen=True)
class Board:
    ats: str
    board: str

    @property
    def key(self) -> str:
        return f"{self.ats}:{self.board}"

    @property
    def url(self) -> str:
        return providers.board_url(self.ats, self.board)


@dataclass(frozen=True)
class Budget:
    max_boards: int = 5
    max_requests: int = 10
    max_seconds: float = 60


@dataclass
class LoopResult:
    exit: str
    cause: str
    trace: list = field(default_factory=list)
    boards: dict = field(default_factory=dict)       # board key -> outcome record
    postings: dict = field(default_factory=dict)     # board key -> parsed postings (ok boards only)
    not_attempted: list = field(default_factory=list)
    requests_used: int = 0


def action_key(method: str, url: str) -> tuple:
    """Repeat rule: same method, host, and normalized URL (scheme/host lowercased, query sorted)."""
    p = urlsplit(url)
    return (method.upper(), p.scheme.lower(), (p.hostname or "").lower(), p.path, urlencode(sorted(parse_qsl(p.query))))


def classify(ats: str, board: str, response, last_count: int | None):
    """Error policy for one finished request. Returns (outcome, postings, detail)."""
    if response.kind == "transient":
        return "failed_transient", None, response.detail
    if response.status == 404:
        return "failed_not_found", None, "HTTP 404"
    if response.kind == "http_error":
        return "failed_http", None, response.detail
    try:
        postings = providers.parse(ats, json.loads(response.body), board)
    except (ValueError, providers.Malformed) as e:
        return "malformed", None, str(e)
    if not postings and last_count:
        return "suspicious_empty", None, f"0 jobs, but the board had {last_count} last time"
    return "ok", postings, f"{len(postings)} jobs"


def run_loop(boards, transport, last_counts: dict, budget: Budget, save_raw,
             clock=time.monotonic, sleep=time.sleep, classify=classify) -> LoopResult:
    """save_raw(board_key, attempt, bytes) -> saved path (must go through policy.write_bytes)."""
    res = LoopResult(exit="", cause="")
    t0 = clock()
    done_actions = set()

    def log(event, **fields):
        res.trace.append({"seq": len(res.trace) + 1, "t": round(clock() - t0, 3), "event": event, **fields})

    def stop_for_budget(i, reason):
        log("budget_stop", reason=reason)
        res.exit, res.cause = "budget_exhausted", reason
        res.not_attempted = [b.key for b in boards[i:]]

    log("start", boards=[b.key for b in boards], budget=vars(budget), transport=transport.label)
    try:
        for i, b in enumerate(boards):
            if i >= budget.max_boards:
                stop_for_budget(i, f"board budget ({budget.max_boards}) reached")
                break
            key = action_key("GET", b.url)
            if key in done_actions:
                log("repeat_refused", board=b.key, url=b.url)
                res.boards[b.key + "#repeat"] = {"outcome": "repeat_refused", "detail": "identical request already made this run"}
                continue
            done_actions.add(key)

            attempt, outcome = 0, None
            while outcome is None:
                if res.requests_used >= budget.max_requests:
                    stop_for_budget(i, f"request budget ({budget.max_requests}) reached")
                    break
                if clock() - t0 >= budget.max_seconds:
                    stop_for_budget(i, f"time budget ({budget.max_seconds}s) reached")
                    break
                attempt += 1
                res.requests_used += 1
                r = transport.get(b.url, timeout=REQUEST_TIMEOUT)
                raw = save_raw(b.key, attempt, r.body) if r.body is not None else None
                log("request", board=b.key, attempt=attempt, url=b.url, kind=r.kind, status=r.status,
                    bytes=len(r.body) if r.body is not None else 0, raw=raw, detail=r.detail)
                outcome, postings, detail = classify(b.ats, b.board, r, last_counts.get(b.key))
                if outcome == "failed_transient" and attempt == 1:
                    log("retry_scheduled", board=b.key, wait_s=RETRY_WAIT, why="transient failure; one retry allowed")
                    sleep(RETRY_WAIT)
                    outcome = None
            if res.exit == "budget_exhausted":
                break
            res.boards[b.key] = {"outcome": outcome, "detail": detail, "attempts": attempt}
            if outcome == "ok":
                res.postings[b.key] = postings
            log("board_result", board=b.key, outcome=outcome, detail=detail)
    except policy.PolicyViolation as e:
        log("policy_refused", detail=str(e))
        res.exit, res.cause = "error", f"permission violation: {e}"
        return res

    if not res.exit:
        real = {k: v for k, v in res.boards.items() if not k.endswith("#repeat")}
        ok = [k for k, v in real.items() if v["outcome"] == "ok"]
        if real and len(ok) == len(real):
            res.exit, res.cause = "finished", "every planned board was fetched and checked"
        elif not ok:
            res.exit, res.cause = "error", "every board failed: escalate to a person"
        else:
            failed = [k for k in real if k not in ok]
            res.exit, res.cause = "incomplete", f"failed boards: {', '.join(failed)}"
    log("exit", exit=res.exit, cause=res.cause, requests_used=res.requests_used)
    return res
