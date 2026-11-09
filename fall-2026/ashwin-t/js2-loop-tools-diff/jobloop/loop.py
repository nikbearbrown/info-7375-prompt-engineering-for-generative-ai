"""The bounded multi-board loop (GATE.md sections 1-4).

Usage (from this folder):
    python3 -m jobloop                          # live run of config/boards.json, state not written
    python3 -m jobloop --approve-state-write    # same; a FINISHED run may then write state/seen.json
    python3 -m jobloop --replay seeded/NAME     # SEEDED REPLAY from saved files, no network, no state write
    python3 -m jobloop --max-attempts 4         # a smaller budget (ceilings can only be lowered)

Exit codes: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error.

Every attempt, response, retry decision and outcome is appended to runs/<run-id>/trace.jsonl
as it happens; report.json and report.md summarize the run. Small module-level functions
(classify_response, retry_allowed, ...) are the decisions the tests pin down; the files in
wrong_versions/ replace them one at a time to show the tests catch each wrong version.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from . import fetch, policy, providers, rule, state
from .persona import PersonaError, validate_resume

FINISHED, INCOMPLETE, BUDGET_EXHAUSTED, ERROR = "finished", "incomplete", "budget-exhausted", "error"
EXIT_CODES = {FINISHED: 0, INCOMPLETE: 1, BUDGET_EXHAUSTED: 2, ERROR: 3}
OBSERVED, EMPTY, FAILED, NOT_OBSERVED = "observed", "empty-needs-review", "failed", "not-observed"
LIVE, SEEDED = "LIVE", "SEEDED REPLAY"

CONFIG_PATH = "config/boards.json"
RESUME_PATH = "data/supriya-sharma.resume.json"
TRANSIENT_STATUSES = {500, 502, 503, 504}
TRANSIENT_FAILURES = {"timeout", "connection-reset"}
PURPOSES = {"watch", "deliberate-failure"}


@dataclass(frozen=True)
class Budget:
    """GATE.md section 2. These defaults are the ceilings. Raising one needs a new written
    decision in GATE.md, committed with a reason before the next run."""
    max_boards: int = 6
    max_attempts: int = 12
    max_seconds: float = 120.0
    request_timeout: float = 10.0
    max_retries_per_board: int = 1
    retry_delay: float = 1.0


CEILINGS = Budget()


class ConfigError(ValueError):
    """Invalid configuration or budget. Stops with `error` before any network access."""


class RepeatViolation(RuntimeError):
    """The same action was attempted again without being the one allowed retry (GATE.md section 3)."""


# ------------------------------------------------------------------ decisions


def check_budget(b: Budget) -> Budget:
    for f in fields(Budget):
        value, ceiling = getattr(b, f.name), getattr(CEILINGS, f.name)
        minimum = 0 if f.name in ("max_retries_per_board", "retry_delay") else 1e-9
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < minimum:
            raise ConfigError(f"budget {f.name}={value!r} is not a positive number")
        if value > ceiling:
            raise ConfigError(f"budget {f.name}={value} is above the GATE.md ceiling {ceiling}; "
                              "only a new written decision in GATE.md can raise it")
    return b


def validate_config(cfg, budget: Budget) -> list:
    """Return the board list, or raise ConfigError. Runs before any network access."""
    if not isinstance(cfg, dict) or set(cfg) != {"schema_version", "boards"}:
        raise ConfigError("config must have exactly the keys ['boards', 'schema_version']")
    if cfg["schema_version"] != 1:
        raise ConfigError(f"unsupported config schema_version {cfg['schema_version']!r}")
    boards = cfg["boards"]
    if not isinstance(boards, list) or not boards:
        raise ConfigError("config must list at least one board")
    if len(boards) > budget.max_boards:
        raise ConfigError(f"{len(boards)} boards configured; the budget allows {budget.max_boards}")
    seen = set()
    for i, b in enumerate(boards):
        if not isinstance(b, dict) or set(b) != {"provider", "board", "purpose"}:
            raise ConfigError(f"boards[{i}] must have exactly the keys ['board', 'provider', 'purpose']")
        if b["purpose"] not in PURPOSES:
            raise ConfigError(f"boards[{i}].purpose {b['purpose']!r} must be one of {sorted(PURPOSES)}")
        try:
            url = providers.endpoint(b["provider"], b["board"])
        except ValueError as exc:
            raise ConfigError(f"boards[{i}]: {exc}") from None
        key = (b["provider"], b["board"])
        if key in seen:
            raise ConfigError(f"boards[{i}] repeats {b['provider']}/{b['board']}; duplicates are not allowed")
        seen.add(key)
        b["url"] = url
    return boards


def request_timeout(budget: Budget, remaining: float) -> float:
    """Per-request timeout, reduced to the remaining run time."""
    return min(budget.request_timeout, remaining)


def classify_failure(failure: "fetch.TransportFailure") -> tuple:
    kind = "transient" if failure.kind in TRANSIENT_FAILURES else "failed"
    return kind, f"no response received ({failure})", None


def classify_response(provider: str, board: str, resp: "fetch.Response") -> tuple:
    """(kind, detail, postings). kind: ok, empty, transient, failed. Never turns a failure into []."""
    s = resp.status
    if s in TRANSIENT_STATUSES:
        return "transient", f"HTTP {s} (server error)", None
    if 300 <= s < 400:
        return "failed", f"HTTP {s} redirect to {resp.headers.get('location')!r} refused (redirects are never followed)", None
    if s == 404:
        return "failed", "HTTP 404: board not found (bad board name?)", None
    if s in (401, 403):
        return "failed", f"HTTP {s}: access refused; the agent never logs in", None
    if s == 429:
        return "failed", "HTTP 429: rate limited; not retried, check manually later", None
    if s != 200:
        return "failed", f"HTTP {s}: unexpected status", None
    if not resp.body.strip():
        return "failed", "HTTP 200 with an empty body", None
    try:
        postings = providers.parse(provider, board, resp.body)
    except providers.ParseError as exc:
        return "failed", f"{exc.kind}: {exc}", None
    if not postings:
        return "empty", "HTTP 200 with a valid listing of zero postings; needs review, not 'no new jobs'", []
    return "ok", f"HTTP 200, {len(postings)} postings", postings


def retry_allowed(kind: str, retries_used: int, budget: Budget) -> bool:
    return kind == "transient" and retries_used < budget.max_retries_per_board


def count_attempt(run: "Run", got_response: bool) -> None:
    """Every attempt counts against the request budget, failed or not."""
    run.attempts_used += 1


def fetch_once(method: str, url: str, allowed: set, transport: Callable, timeout: float):
    """Check the policy, then send exactly one request. A redirect is returned, never followed."""
    decision = policy.check_request(method, url, allowed)
    if not decision.allowed:
        raise policy.PolicyViolation(decision, f"{method} {url}")
    return transport(url, timeout)


def not_observed_outcome(b: dict, reason: str) -> dict:
    return {"outcome": NOT_OBSERVED, "reason": reason, "postings": None}


def overall_status(outcomes: list, budget_hit: bool, interrupted: bool) -> str:
    if budget_hit:
        return BUDGET_EXHAUSTED
    if interrupted or any(o["outcome"] != OBSERVED for o in outcomes):
        return INCOMPLETE
    return FINISHED


def state_update_allowed(status: str) -> bool:
    return status == FINISHED


def board_key(provider: str, board: str) -> str:
    return state.board_key(provider, board)


def mode_label(replay: bool) -> str:
    return SEEDED if replay else LIVE


# ------------------------------------------------------------------ the run


class Ledger:
    """Repeat rule: an action is (provider, board, method, url). A second attempt is allowed
    only as the single retry of a transient failure; anything else is a RepeatViolation."""

    def __init__(self):
        self.kinds = {}

    def authorize(self, action: tuple, is_retry: bool) -> None:
        prev = self.kinds.get(action, [])
        if not prev:
            return
        if is_retry and len(prev) == 1 and prev[0] == "transient":
            return
        raise RepeatViolation(f"repeated action {action} after {prev}; only one retry of a transient failure is allowed")

    def record(self, action: tuple, kind: str) -> None:
        self.kinds.setdefault(action, []).append(kind)


class Run:
    def __init__(self, root: Path, run_rel: str, budget: Budget, clock: Callable, wall: Callable):
        self.root, self.run_rel, self.budget = root, run_rel, budget
        self.clock, self.wall = clock, wall
        self.start = clock()
        self.deadline = self.start + budget.max_seconds
        self.attempts_used = 0
        self.budget_hit = False
        self.trace = policy.open_new_file(f"{run_rel}/trace.jsonl", root=root)

    def remaining(self) -> float:
        return self.deadline - self.clock()

    def elapsed(self) -> float:
        return self.clock() - self.start

    def event(self, event_name: str, /, **data) -> None:
        line = {"t": round(self.elapsed(), 3), "utc": _utc(self.wall()), **data, "event": event_name}
        self.trace.write((json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
        self.trace.flush()

    def save(self, name: str, data: bytes) -> str:
        rel = f"{self.run_rel}/{name}"
        policy.write_new_file(rel, data, root=self.root)
        return rel


def _utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_run_dir(root: Path, stamp: str, suffix: str) -> str:
    for n in range(1, 100):
        rel = f"runs/{stamp}-{suffix}" + (f"-{n}" if n > 1 else "")
        try:
            policy.make_new_dir(rel, root=root)
            return rel
        except FileExistsError:
            continue
    raise OSError("could not create a unique run folder")


def observe_board(run: Run, b: dict, allowed: set, transport: Callable, sleep: Callable,
                  ledger: Ledger) -> dict:
    budget = run.budget
    action = (b["provider"], b["board"], "GET", b["url"])
    attempts, retries = [], 0
    while True:
        why = None
        if run.attempts_used >= budget.max_attempts:
            why = f"request budget exhausted ({run.attempts_used}/{budget.max_attempts} attempts used)"
        elif run.remaining() <= 0:
            why = f"time budget exhausted ({budget.max_seconds:.0f}s)"
        if why:
            run.budget_hit = True
            run.event("budget-stop", board=f"{b['provider']}/{b['board']}", reason=why)
            if not attempts:
                return {**not_observed_outcome(b, why), "attempts": attempts}
            return {"outcome": FAILED, "postings": None, "attempts": attempts,
                    "reason": f"{attempts[-1]['detail']}; retry not attempted: {why}"}

        ledger.authorize(action, is_retry=bool(attempts))
        timeout = request_timeout(budget, run.remaining())
        n = len(attempts) + 1
        run.event("attempt", board=f"{b['provider']}/{b['board']}", attempt=n, method="GET", url=b["url"],
                  timeout=round(timeout, 3), attempts_used_before=run.attempts_used,
                  seconds_remaining=round(run.remaining(), 3))
        resp = failure = None
        try:
            resp = fetch_once("GET", b["url"], allowed, transport, timeout)
        except fetch.TransportFailure as exc:
            failure = exc
        count_attempt(run, got_response=resp is not None)

        record = {"attempt": n, "url": b["url"]}
        if resp is not None:
            ext = "json" if "json" in (resp.headers.get("content-type") or "") else "txt"
            record.update({
                "status": resp.status,
                "raw_file": run.save(f"raw/{b['provider']}__{b['board']}__attempt-{n}.{ext}", resp.body),
                "sha256": hashlib.sha256(resp.body).hexdigest(), "bytes": len(resp.body),
                "headers": {k: resp.headers.get(k) for k in ("date", "content-type", "location") if resp.headers.get(k)},
                "elapsed": round(resp.elapsed, 3)})
            if resp.note:
                record["source_note"] = resp.note
            kind, detail, postings = classify_response(b["provider"], b["board"], resp)
        else:
            record.update({"status": None, "raw_file": None, "response": "no response received",
                           "failure": failure.kind, "elapsed": round(failure.elapsed, 3)})
            kind, detail, postings = classify_failure(failure)
        record.update({"kind": kind, "detail": detail})
        attempts.append(record)
        ledger.record(action, kind)
        run.event("result", board=f"{b['provider']}/{b['board']}", attempts_used_after=run.attempts_used,
                  **{k: v for k, v in record.items() if k != "url"})

        if kind == "ok":
            if run.remaining() <= 0:
                run.budget_hit = True
                return {**not_observed_outcome(b, "time budget ran out while processing the response"),
                        "attempts": attempts}
            return {"outcome": OBSERVED, "reason": detail, "postings": postings, "attempts": attempts}
        if kind == "empty":
            return {"outcome": EMPTY, "reason": detail, "postings": [], "attempts": attempts}
        if retry_allowed(kind, retries, budget):
            if run.attempts_used >= budget.max_attempts or run.remaining() <= budget.retry_delay:
                run.budget_hit = True
                why = "request budget" if run.attempts_used >= budget.max_attempts else "time budget"
                run.event("retry-skipped", board=f"{b['provider']}/{b['board']}", reason=f"{why} cannot fit a retry")
                return {"outcome": FAILED, "postings": None, "attempts": attempts,
                        "reason": f"{detail}; retry not attempted: {why} cannot fit it"}
            run.event("retry-scheduled", board=f"{b['provider']}/{b['board']}", delay=budget.retry_delay,
                      why="transient failure on a read-only GET; one retry allowed by GATE.md section 4")
            sleep(budget.retry_delay)
            retries += 1
            continue
        suffix = " after 1 retry" if retries else ""
        return {"outcome": FAILED, "reason": f"{detail}{suffix}", "postings": None, "attempts": attempts}


def _next_check(b: dict, outcome: dict) -> str:
    if outcome["outcome"] == EMPTY:
        return f"Open {b['url']} by hand: is the board really empty, or is the name wrong?"
    if outcome["outcome"] == NOT_OBSERVED:
        return "Not visited. Run again (budget allowing) before saying anything about this board."
    if b["purpose"] == "deliberate-failure":
        return "Expected: this board is the deliberate failure. Confirm the reason matches GATE.md section 4."
    return f"Check {b['url']} by hand and the raw file for this attempt before retrying."


def run(root: Path = policy.PROJECT_ROOT, *, config_path: str = CONFIG_PATH, state_path: str = state.STATE_PATH,
        transport: Callable = fetch.https_get, budget: Budget = CEILINGS, approve_state_write: bool = False,
        replay: Optional[str] = None, label: str = "", clock: Callable = time.monotonic,
        sleep: Callable = time.sleep, wall: Callable = lambda: datetime.now(timezone.utc)) -> dict:
    """One run. Returns the report dict (also saved). Raises only if no run folder can be made."""
    root = Path(root)
    started = wall()
    mode = mode_label(replay is not None)
    suffix = "seeded" if replay is not None else "live"
    run_rel = _new_run_dir(root, started.strftime("%Y-%m-%dT%H-%M-%SZ"), suffix + (f"-{label}" if label else ""))
    r = Run(root, run_rel, budget, clock, wall)
    r.event("start", mode=mode, label=label or None, config=config_path, state=state_path,
            approve_state_write=approve_state_write, budget=asdict(budget))

    reasons, outcomes, boards, prev_state, status = [], [], [], None, None
    interrupted = False
    try:
        check_budget(budget)
        if replay is not None and approve_state_write:
            raise ConfigError("a SEEDED REPLAY never writes state; --approve-state-write is refused")
        cfg = json.loads(policy.read_bytes(config_path, root=root).decode("utf-8"))
        boards = validate_config(cfg, budget)
        resume = validate_resume(json.loads(policy.read_bytes(RESUME_PATH, root=root).decode("utf-8")))
        prev_state = state.load(state_path, root=root)
        r.event("preflight-ok", boards=[f"{b['provider']}/{b['board']}" for b in boards],
                state_boards=sorted((prev_state or {}).get("boards", {})))
        allowed = {b["url"] for b in boards}
        ledger = Ledger()
        for i, b in enumerate(boards):
            if r.budget_hit:
                out = {**not_observed_outcome(b, "not visited: the run budget was exhausted earlier"), "attempts": []}
            else:
                try:
                    out = observe_board(r, b, allowed, transport, sleep, ledger)
                except KeyboardInterrupt:
                    interrupted = True
                    out = {**not_observed_outcome(b, "interrupted by the user"), "attempts": []}
                    r.event("interrupted", board=f"{b['provider']}/{b['board']}")
            outcomes.append(out)
            if interrupted:
                for rest in boards[i + 1:]:
                    outcomes.append({**not_observed_outcome(rest, "not visited: the run was interrupted"),
                                     "attempts": []})
                break
            r.event("board-outcome", board=f"{b['provider']}/{b['board']}", outcome=out["outcome"],
                    reason=out["reason"])
    except (ConfigError, state.StateError, PersonaError, policy.PolicyViolation, RepeatViolation,
            json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        status = ERROR
        reasons.append(f"{type(exc).__name__}: {exc}")
        r.event("error", error=reasons[-1])
    for b in boards[len(outcomes):]:
        outcomes.append({**not_observed_outcome(b, "no outcome: the run stopped with an error at or before this "
                                                   "board (see trace.jsonl)"), "attempts": []})

    # Comparisons and the rule, only for boards actually observed.
    board_reports, observed_ids = [], {}
    for b, out in zip(boards, outcomes):
        key = board_key(b["provider"], b["board"])
        entry = {"provider": b["provider"], "board": b["board"], "purpose": b["purpose"], "url": b["url"],
                 "outcome": out["outcome"], "reason": out["reason"], "attempts": out["attempts"],
                 "postings_observed": None, "baseline": None, "previously_seen": None, "new": None,
                 "rule_relevant": None}
        if out["outcome"] in (OBSERVED, EMPTY):
            entry["postings_observed"] = len(out["postings"])
        if out["outcome"] == OBSERVED:
            prior = ((prev_state or {}).get("boards", {})).get(key)
            entry["baseline"] = prior is None
            ids = [p["id"] for p in out["postings"]]
            observed_ids[key] = set(ids)
            if prior is not None:
                seen = set(prior["seen_ids"])
                entry["previously_seen"] = len(seen)
                entry["previous_observation"] = prior["last_observed"]
                new = [p for p in out["postings"] if p["id"] not in seen]
                entry["new"] = []
                for p in new:
                    rec = rule.classify(p, resume)
                    entry["new"].append({"key": p["key"], "title": p["title"], "location": p["location"]["name"],
                                         "url": p["absolute_url"], "rule_verdict": rec["verdict"],
                                         "rule_checks": rec["checks"], "rule_justification": rec["justification"]})
                entry["rule_relevant"] = sum(n["rule_verdict"] == rule.RELEVANT for n in entry["new"])
        board_reports.append(entry)

    if status is None:
        status = overall_status(outcomes, r.budget_hit, interrupted)
        for e in board_reports:
            if e["outcome"] != OBSERVED:
                reasons.append(f"{e['provider']}/{e['board']}: {e['outcome']} ({e['reason']})")
        if interrupted:
            reasons.append("interrupted by the user")

    deliberate = []
    for e in board_reports:
        if e["purpose"] == "deliberate-failure":
            if e["outcome"] == FAILED:
                deliberate.append(f"{e['provider']}/{e['board']}: deliberate failure observed and handled: {e['reason']}")
            else:
                deliberate.append(f"{e['provider']}/{e['board']}: the deliberate-failure demonstration was NOT "
                                  f"achieved (outcome {e['outcome']}: {e['reason']})")

    # The one state write: only after a finished run, only with the command-line approval.
    if not state_update_allowed(status):
        state_update = f"not-allowed: run status is {status}"
    elif not approve_state_write:
        d = policy.check_write(state_path, root=root, approve_state_write=False, run_status=status)
        state_update = f"not-approved ({d.outcome}: {d.reason}); state unchanged"
    else:
        try:
            state.save(state.merged(prev_state, observed_ids, _utc(started)),
                       approve_state_write=approve_state_write, run_status=status, root=root)
            state_update = "updated"
        except (policy.PolicyViolation, state.StateError, OSError) as exc:
            status = ERROR
            reasons.append(f"state write failed: {type(exc).__name__}: {exc}")
            state_update = f"write-failed: {exc}"
    r.event("state", state_update=state_update)

    attention = []
    for b, e in zip(boards, board_reports):
        if e["outcome"] != OBSERVED:
            last = e["attempts"][-1] if e["attempts"] else None
            attention.append({"board": f"{e['provider']}/{e['board']}",
                              "attempt": last["attempt"] if last else None,
                              "failure": f"{e['outcome']}: {e['reason']}",
                              "next_check": _next_check(b, e)})
    if status == ERROR and not attention:
        attention.append({"board": None, "attempt": None, "failure": "; ".join(reasons),
                          "next_check": "Fix the configuration, state or permission problem; nothing was observed after it."})

    report = {
        "run": {"run_id": run_rel.split("/", 1)[1], "run_dir": run_rel, "mode": mode, "label": label or None,
                "status": status, "exit_code": EXIT_CODES[status], "reasons": reasons,
                "started_utc": _utc(started), "ended_utc": _utc(wall()), "elapsed_seconds": round(r.elapsed(), 3),
                "budget": asdict(budget), "attempts_used": r.attempts_used,
                "boards_configured": len(boards), "state_update": state_update,
                "deliberate_failure": deliberate,
                "replay_source": replay},
        "boards": board_reports,
        "attention_required": attention,
    }
    r.event("end", status=status, exit_code=EXIT_CODES[status], attempts_used=r.attempts_used)
    r.trace.close()
    r.save("report.json", (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    from .report import render_markdown
    r.save("report.md", render_markdown(report).encode("utf-8"))
    return report


# ------------------------------------------------------------------ seeded replay


def replay_transport(replay_dir: str, root: Path = policy.PROJECT_ROOT) -> tuple:
    """Return (transport, config_path, state_path) for a seeded folder. No network."""
    manifest = json.loads(policy.read_bytes(f"{replay_dir}/manifest.json", root=root).decode("utf-8"))
    responses = manifest["responses"]

    def transport(url: str, timeout: float):
        if url not in responses:
            raise fetch.TransportFailure("connection-error", f"SEEDED REPLAY has no saved response for {url}")
        item = responses[url]
        body = policy.read_bytes(f"{replay_dir}/{item['body']}", root=root)
        return fetch.Response(item["status"], {"content-type": item.get("content_type", "application/json")},
                              body, 0.0, note=f"SEEDED REPLAY: {item['provenance']}")

    return transport, f"{replay_dir}/{manifest['config']}", f"{replay_dir}/{manifest['state']}"


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m jobloop", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=CONFIG_PATH)
    ap.add_argument("--replay", help="seeded folder (e.g. seeded/finished-wrong-answer); no network, no state write")
    ap.add_argument("--approve-state-write", action="store_true",
                    help="Ashwin's approval for this run only to write state/seen.json, if the run finishes")
    ap.add_argument("--max-boards", type=int, default=CEILINGS.max_boards)
    ap.add_argument("--max-attempts", type=int, default=CEILINGS.max_attempts)
    ap.add_argument("--max-seconds", type=float, default=CEILINGS.max_seconds)
    args = ap.parse_args(argv)
    budget = replace(CEILINGS, max_boards=args.max_boards, max_attempts=args.max_attempts,
                     max_seconds=args.max_seconds)
    kwargs = {}
    if args.replay:
        try:
            transport, config_path, state_path = replay_transport(args.replay.rstrip("/"))
        except (policy.PolicyViolation, OSError, KeyError, json.JSONDecodeError) as exc:
            print(f"RUN FAILED before starting: cannot load replay {args.replay}: {exc}", file=sys.stderr)
            return EXIT_CODES[ERROR]
        kwargs = {"transport": transport, "config_path": config_path, "state_path": state_path,
                  "replay": args.replay.rstrip("/")}
    else:
        kwargs = {"config_path": args.config}
    try:
        report = run(budget=budget, approve_state_write=args.approve_state_write, **kwargs)
    except (policy.PolicyViolation, OSError) as exc:
        print(f"RUN FAILED: no run folder could be created: {exc}", file=sys.stderr)
        return EXIT_CODES[ERROR]
    print_summary(report)
    return report["run"]["exit_code"]


def print_summary(report: dict) -> None:
    run_ = report["run"]
    print(f"{run_['mode']} run {run_['run_id']}: status {run_['status'].upper()} (exit {run_['exit_code']}), "
          f"{run_['attempts_used']}/{run_['budget']['max_attempts']} attempts, {run_['elapsed_seconds']}s")
    for e in report["boards"]:
        extra = ""
        if e["outcome"] == OBSERVED:
            extra = (f", {e['postings_observed']} postings, baseline" if e["baseline"] else
                     f", {e['postings_observed']} postings, {len(e['new'])} new, {e['rule_relevant']} RELEVANT by rule")
        print(f"  {e['provider']}/{e['board']}: {e['outcome']}{extra}  [{e['reason']}]")
    print(f"  state: {run_['state_update']}")
    for line in run_["deliberate_failure"]:
        print(f"  {line}")
    print(f"Report: {run_['run_dir']}/report.md")
