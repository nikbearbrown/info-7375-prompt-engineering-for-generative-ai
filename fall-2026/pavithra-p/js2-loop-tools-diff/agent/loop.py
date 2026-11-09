"""The bounded loop from GATE.md: one request at a time, budgets checked before each one, one exit status per run.

Every attempt is an observation in the trace, every response body is saved as raw evidence, and a failed board is
reported as failed, never as "0 jobs". The wrong versions in agent/wrong_versions.py reuse this loop with one hook
changed; the real watcher never sets them.
"""
import json
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import ats, rule, tools
from .policy import PolicyRefused

TRANSIENT_STATUSES = {429, 500, 502, 503, 504}


class RepeatedAction(Exception):
    """The same GET a second time in one run, other than the one allowed retry (GATE.md, repeat rule)."""


class BudgetExhausted(Exception):
    def __init__(self, limit, detail):
        super().__init__(f"{limit} budget reached: {detail}")
        self.limit = limit


def action_key(method, url):
    parts = urllib.parse.urlsplit(url)
    return (method, parts.hostname, parts.path, tuple(sorted(urllib.parse.parse_qsl(parts.query))))


def classify(outcome):
    """'ok', 'transient' (retry once) or 'permanent' (no retry): GATE.md, error policy."""
    if outcome == "timeout":
        return "transient"
    if isinstance(outcome, int):
        if outcome == 200:
            return "ok"
        return "transient" if outcome in TRANSIENT_STATUSES else "permanent"
    return "permanent"


@dataclass
class Hooks:
    """The behaviour GATE.md fixes. Only agent/wrong_versions.py changes these, to build the versions the tests must catch."""
    classify: object = classify
    max_attempts: int = 2
    check_budgets: bool = True
    check_hosts: bool = True
    failed_as_empty: bool = False


@dataclass
class RunResult:
    status: str
    reason: str
    started_at: str
    boards: list = field(default_factory=list)
    requests: int = 0
    seconds: float = 0.0
    last_action: str = ""
    new_jobs: list = field(default_factory=list)
    all_jobs: int = 0
    relevant_all: int = 0
    trace: list = field(default_factory=list)


class _Run:
    def __init__(self, budgets, policy, persona, state, raw_dir, stamp, get, clock, sleep, hooks):
        self.budgets, self.policy, self.persona, self.state = budgets, policy, persona, state
        self.raw_dir, self.stamp, self.get, self.clock, self.sleep, self.hooks = raw_dir, stamp, get, clock, sleep, hooks
        self.t0 = clock()
        self.requests = 0
        self.done = set()
        self.trace = []
        self.last_action = "nothing yet"

    def elapsed(self):
        return self.clock() - self.t0

    def observe(self, **event):
        event = {"t": round(self.elapsed(), 3), "step": len(self.trace) + 1, **event}
        self.trace.append(event)
        return event

    def check_budgets(self, boards_started):
        if not self.hooks.check_budgets:
            return
        b = self.budgets
        if boards_started > b["max_boards"]:
            raise BudgetExhausted("boards", f"{b['max_boards']} boards per run")
        if self.requests >= b["max_requests"]:
            raise BudgetExhausted("requests", f"{self.requests} of {b['max_requests']} requests used")
        if self.elapsed() >= b["max_seconds"]:
            raise BudgetExhausted("seconds", f"{self.elapsed():.1f} of {b['max_seconds']} s used")

    def fetch_board(self, board, boards_started):
        """One board: at most one retry, and only after a transient failure."""
        system, name = board["system"], board["name"]
        key_name = f"{system}:{name}"
        url = ats.board_url(system, name)
        result = {"board": key_name, "system": system, "url": url, "result": "failed", "attempts": [],
                  "jobs": None, "new": [], "reason": ""}
        retry_allowed = False
        for attempt in range(1, self.hooks.max_attempts + 1):
            self.check_budgets(boards_started)
            key = action_key("GET", url)
            if key in self.done and not retry_allowed:
                raise RepeatedAction(f"GET {url} was already made in this run")
            if self.hooks.check_hosts:
                self.policy.check_request("GET", url)
            self.done.add(key)
            self.requests += 1
            started = self.elapsed()
            try:
                response = self.get(url, self.budgets["request_timeout_seconds"])
                outcome, body = response.status, response.body
            except tools.Timeout:
                outcome, body = "timeout", None
            except tools.NetworkError as e:
                outcome, body = f"network error: {e}", None
            raw = None
            if body is not None:
                raw = self.policy.write_bytes(self.raw_dir / f"{self.stamp}-{system}-{name}-a{attempt}.json", body)
            kind = self.hooks.classify(outcome)
            step = {"attempt": attempt, "outcome": f"HTTP {outcome}" if isinstance(outcome, int) else outcome,
                    "bytes": len(body) if body is not None else 0,
                    "raw": str(raw.relative_to(self.policy.root)) if raw else None,
                    "seconds": round(self.elapsed() - started, 3)}
            result["attempts"].append(step)
            self.last_action = f"GET {url} (attempt {attempt}): {step['outcome']}"
            if kind == "ok":
                try:
                    jobs = ats.parse(system, body)
                except ats.BadData as e:
                    result["reason"] = f"invalid data: {e}"
                    self.observe(action=f"GET {url}", board=key_name, **step, decision=f"failed, no retry: {result['reason']}")
                    break
                result.update(result="checked", jobs=jobs)
                self.observe(action=f"GET {url}", board=key_name, **step, jobs=len(jobs), decision="checked")
                break
            if kind == "transient" and attempt < self.hooks.max_attempts:
                retry_allowed = True
                self.observe(action=f"GET {url}", board=key_name, **step,
                             decision=f"transient, retry once after {self.budgets['retry_wait_seconds']} s")
                self.sleep(self.budgets["retry_wait_seconds"])
                continue
            result["reason"] = (f"{step['outcome']} after one retry" if kind == "transient"
                                else f"{step['outcome']}, not retried (permanent)")
            self.observe(action=f"GET {url}", board=key_name, **step, decision=f"failed: {result['reason']}")
            break
        if result["result"] == "failed" and self.hooks.failed_as_empty:
            result.update(result="checked", jobs=[], reason="")
        return result


def run(boards, budgets, policy, persona, state, raw_dir, now=None, get=None, clock=time.monotonic,
        sleep=time.sleep, hooks=None, tag=""):
    """One run over the board list. Returns a RunResult; never raises for a board failure or a budget.

    tag (for example "-WRONG-V3") goes into every saved file name, so a demonstration run is never mistaken for a real one.
    """
    hooks = hooks or Hooks()
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    stamp = now.strftime("%Y%m%dT%H%M%SZ") + tag
    get = get or (lambda url, timeout: tools.http_get(url, policy, timeout))
    r = _Run(budgets, policy, persona, state, raw_dir, stamp, get, clock, sleep, hooks)
    result = RunResult(status="", reason="", started_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    seen = state.setdefault("boards", {})
    try:
        for i, board in enumerate(boards, start=1):
            board_result = r.fetch_board(board, i)
            if board_result["result"] == "checked":
                before = set(seen.get(board_result["board"], []))
                ids = [j["id"] for j in board_result["jobs"]]
                baseline = board_result["board"] not in seen
                board_result["baseline"] = baseline
                board_result["new"] = [] if baseline else [j for j in board_result["jobs"] if j["id"] not in before]
                seen[board_result["board"]] = sorted(before | set(ids))
            result.boards.append(board_result)
        failed = [b for b in result.boards if b["result"] == "failed"]
        result.status = "incomplete" if failed else "finished"
        result.reason = (f"{len(failed)} of {len(result.boards)} boards failed: "
                         + "; ".join(f"{b['board']} ({b['reason']})" for b in failed)) if failed else \
            f"all {len(result.boards)} boards checked"
    except BudgetExhausted as e:
        result.status, result.reason = "budget-exhausted", str(e)
    except (RepeatedAction, PolicyRefused) as e:
        result.status, result.reason = "error", str(e)
    except Exception as e:  # the loop itself broke: report it, do not hide it
        result.status, result.reason = "error", f"{type(e).__name__}: {e}"
    r.observe(action="exit", status=result.status, reason=result.reason)
    result.requests, result.seconds, result.last_action, result.trace = r.requests, round(r.elapsed(), 3), r.last_action, r.trace
    for b in result.boards:
        new_ids = {j["id"] for j in b["new"]}
        for job in b.get("jobs") or []:
            verdict = rule.judge(job, persona)
            result.all_jobs += 1
            result.relevant_all += verdict.verdict == "Relevant"
            if job["id"] in new_ids:
                result.new_jobs.append({"board": b["board"], "id": job["id"], "title": job["title"],
                                        "location": job["location"]["name"], "url": job["url"],
                                        "rule": verdict.verdict, "reason": verdict.reason})
    return result


def summary(result):
    """The machine-readable report: what agent/check.py compares with the raw evidence."""
    return {"status": result.status, "reason": result.reason, "started_at": result.started_at,
            "requests": result.requests, "seconds": result.seconds, "last_action": result.last_action,
            "all_jobs": result.all_jobs, "relevant_all": result.relevant_all,
            "new_jobs": result.new_jobs,
            "boards": [{k: v for k, v in b.items() if k not in ("jobs", "new")}
                       | {"jobs": None if b.get("jobs") is None else len(b["jobs"]),
                          "new_ids": [j["id"] for j in b.get("new", [])]} for b in result.boards]}


def report_markdown(result, label=""):
    s = summary(result)
    relevant_new = sum(j["rule"] == "Relevant" for j in result.new_jobs)
    lines = [f"# Watch run {s['started_at']}{label}", "",
             f"- Exit status: **{s['status']}** ({s['reason']})",
             f"- Requests: {s['requests']} · seconds: {s['seconds']} · last action: {s['last_action']}",
             f"- Jobs found: {s['all_jobs']} · new since the last run: {len(result.new_jobs)} · "
             f"relevant by my rule (record): {relevant_new} of the new, {s['relevant_all']} of all found", "",
             "| Board | Result | Attempts | Jobs | New | Reason |", "|---|---|---|---|---|---|"]
    for b in s["boards"]:
        attempts = ", ".join(a["outcome"] for a in b["attempts"])
        jobs = "—" if b["jobs"] is None else b["jobs"]
        new = "baseline" if b.get("baseline") else len(b["new_ids"])
        lines.append(f"| {b['board']} | {b['result']} | {attempts} | {jobs} | {new if b['result'] == 'checked' else '—'} | {b['reason']} |")
    if result.new_jobs:
        lines += ["", "## New jobs and the rule's verdict (a record: anyone can recompute it)", "",
                  "| Board | Job ID | Title | Location | Rule |", "|---|---|---|---|---|"]
        lines += [f"| {j['board']} | {j['id']} | {j['title']} | {j['location']} | {j['rule']} |" for j in result.new_jobs]
    return "\n".join(lines) + "\n"


def trace_jsonl(result):
    return "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in result.trace)
