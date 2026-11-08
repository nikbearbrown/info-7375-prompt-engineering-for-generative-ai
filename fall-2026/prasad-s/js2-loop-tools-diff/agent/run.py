"""The JS2 loop and its run report (GATE.md v0.2 §1-§4; CONTRACT.md v0.5, v0.6).

run() reads the config, checks the run's own instructions against §5 before
anything is fetched or written, visits each configured board in order, then
writes the new state to a temporary file, the report, and moves the state
into place. Every fetch, read and write goes through agent/tool_layer.py.
"""

import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from . import CONTRACT_VERSION
from .adapters import ADAPTERS, UnexpectedShape
from .config import parse_config
from .errors import Refusal, RunError
from .fetch import load_seed, save_evidence, utc_stamp
from .persona import check_persona
from .policy import Policy, PolicyRefusal
from .replies import CLAUDE_LABEL
from .rule import judge
from .state import board_ids, commit_state, compute_watch, load_state, write_state_tmp
from .tool_layer import FetchError, ToolLayer

GATE_VERSION = "v0.2"
# GATE.md §2. Budgets live there and here; never in the config (§5).
MAX_BOARDS = 5
MAX_REQUESTS = 10
MAX_SECONDS = 60
BUDGET_LIMITS = {"boards": MAX_BOARDS, "requests": MAX_REQUESTS, "seconds": MAX_SECONDS}
MAX_ATTEMPTS = 2  # GATE.md §4: one retry, for timeout, 5xx or connection error only

NOT_STATED = "not stated"
# CONTRACT v0.5 item 7: JS1's verdict for a missing reply. The Claude judge is not run.
JUDGE_LINE = "rejected — no saved reply (judge not run in JS2)"
REPEAT_LINE = "repeat — not re-run"  # GATE.md §3
DEFAULT_OUTPUT_DIR = "output"


def build_record(posting, persona):
    """One §2 record: the rule judge as in JS1, and the Claude line of v0.5 item 7."""
    rule_verdict, rule_justification = judge(posting, persona)
    location = posting.get("location")
    location_name = location.get("name") if isinstance(location, dict) else None
    return {
        "posting_id": posting["posting_id"],
        "title": posting.get("title"),
        "absolute_url": posting.get("absolute_url"),
        "location.name": location_name if isinstance(location_name, str) else NOT_STATED,
        "rule_verdict": rule_verdict,
        "rule_justification": rule_justification,
        "claude_verdict_label": CLAUDE_LABEL,
        "claude_verdict": "rejected",
        "claude_line": JUDGE_LINE,
        "claude_justification": {
            "reply": None,
            "reasons": ["no saved reply (judge not run in JS2)"],
            "note": "no saved reply was read",
        },
    }


def classify(result=None, error=None):
    """GATE.md §4 for one attempt: ("ok" | "retry" | "failed", reason)."""
    if error is not None:
        return "retry", "timeout" if error.kind == "timeout" else "connection error"
    status = result.status
    if status == 200:
        return "ok", "200"
    if status == 404:  # decided on the status; the body is never parsed as jobs
        return "failed", "not found (404)"
    if 300 <= status < 400:
        return "failed", "redirect refused"
    if 500 <= status < 600:
        return "retry", f"HTTP {status}"
    # Prasad, CP5b: every status §4 does not list fails, with no retry.
    return "failed", f"HTTP {status}"


def final_reason(last_reason):
    """§4's wording once the retry is spent, from the last attempt's failure."""
    if last_reason == "timeout":
        return f"timeout after {MAX_ATTEMPTS} attempts"
    return f"5xx / connection error after {MAX_ATTEMPTS} attempts"


@dataclass(frozen=True)
class Outcome:
    """One board's fetch action, after its retries."""

    status: str  # "ok", "failed", "not completed", "not attempted"
    reason: str = ""
    attempts: int = 0
    body: bytes = None
    budget: str = None
    repeat: bool = False


class Loop:
    """One run's boards, budgets, trace and repeat ledger."""

    def __init__(self, tools, config, persona, sections, seeded, clock, now, started):
        self.tools = tools
        self.config = config
        self.persona = persona
        self.sections_before = sections
        self.sections_after = dict(sections or {})
        self.seeded = seeded  # board key -> (raw, source)
        self.clock = clock
        self.now = now
        self.started = started
        self.requests = 0
        self.boards_started = 0
        self.trace = []
        self.ledger = {}  # GATE.md §3: fetch key -> recorded Outcome
        self.lines = []

    def elapsed(self):
        return self.clock() - self.started

    def budget_stop(self, live=True):
        """The budget that stops the next request (or seeded board), or None. §2: checked between requests."""
        if live and self.requests >= MAX_REQUESTS:
            return "requests"
        if self.elapsed() >= MAX_SECONDS:
            return "seconds"
        return None

    def fetch_board(self, board):
        """One fetch action and its §4 retries. A repeat returns the recorded outcome (§3).

        A retry is not a repeat: it happens inside this call, before any result
        is recorded, and it counts as a request.
        """
        key = ("GET", board.host, urlsplit(board.url).path, board.key)
        if key in self.ledger:
            self.trace.append({"board": board.key, "url": board.url, "note": REPEAT_LINE})
            return replace(self.ledger[key], repeat=True)
        attempt, last_reason = 0, None
        while True:
            stop = self.budget_stop()
            if stop:
                if attempt == 0:
                    return Outcome("not attempted", budget=stop)
                # Prasad, CP5b: the board in progress is not completed, not failed.
                return Outcome("not completed", attempts=attempt, budget=stop,
                               reason=f"{last_reason} on attempt {attempt}; retry not started: {stop} budget exhausted")
            attempt += 1
            self.requests += 1
            fetched_at, began = self.now(), self.clock()
            result = error = None
            try:
                result = self.tools.fetch(board.url)
            except FetchError as exc:
                error = exc
            entry = {"board": board.key, "attempt": attempt, "url": board.url,
                     "elapsed_s": round(self.clock() - began, 3)}
            if result is not None:
                entry["status"] = result.status
                if result.location:
                    entry["location"] = result.location
            else:
                entry["error"] = str(error)
            self.trace.append(entry)
            note = save_evidence(self.tools, self.config.evidence_dir, board, attempt, fetched_at, board.url,
                                 result=result, error=error)
            entry["saved"], entry["sidecar"] = note["file"], note["sidecar"]

            category, last_reason = classify(result, error)
            if category == "retry" and attempt < MAX_ATTEMPTS:
                continue
            if category == "ok":
                outcome = Outcome("ok", attempts=attempt, body=result.body)
            elif category == "failed":
                outcome = Outcome("failed", reason=last_reason, attempts=attempt)
            else:
                outcome = Outcome("failed", reason=final_reason(last_reason), attempts=attempt)
            self.ledger[key] = outcome
            return outcome

    def visit(self, board):
        """Fetch or seed one board and account for it (§1). Returns its line."""
        line = {"board": board.key, "mode": "seeded" if board.key in self.seeded else "live"}
        if board.key in self.seeded:
            raw, source = self.seeded[board.key]
            line["source"] = source
            outcome = Outcome("ok", attempts=0, body=raw)
        else:
            outcome = self.fetch_board(board)
        if outcome.repeat:
            line["repeat"] = REPEAT_LINE
        line["attempts"] = outcome.attempts

        if outcome.status in ("not completed", "not attempted"):
            line.update(status=outcome.status, reason=outcome.reason, budget=outcome.budget,
                        line=f"{outcome.status} — {outcome.reason}" if outcome.reason else outcome.status)
            return line
        if outcome.status == "failed":
            return self._failed(line, outcome.reason)
        try:
            postings = ADAPTERS[board.ats](outcome.body)
        except UnexpectedShape as exc:
            line["detail"] = str(exc)
            return self._failed(line, "unexpected shape")
        return self._ok(line, board, postings)

    def _failed(self, line, reason):
        """§4: the word failed, the reason and the attempts; never 0 jobs, never an empty list. Ids unchanged."""
        line.update(status="failed", reason=reason, line=f"failed — {reason}; attempts: {line['attempts']}")
        return line

    def _ok(self, line, board, postings):
        before = board_ids(self.sections_before, board.key)
        if not postings:
            if before:
                # GATE.md v0.3 §4: zero jobs on a board whose saved state holds ids is a failure,
                # not an empty board. No retry; saved ids unchanged; a live response is already
                # saved as evidence by fetch_board. W5 pins this exact line (no attempts suffix;
                # the attempts are in the line's "attempts" field).
                reason = f"empty board: 0 jobs, {len(before)} ids saved before"
                line.update(status="failed", reason=reason, line=f"failed — {reason}")
                return line
            # GATE.md v0.3 §4: no saved ids, so zero is a real answer; the board's saved ids are unchanged.
            line.update(status="ok", jobs_fetched=0, new_ids=[], already_seen=0, baseline=False,
                        new_postings=[], line="ok — 0 jobs, 0 new")
            return line
        by_id = {}
        for posting in postings:
            by_id.setdefault(posting["posting_id"], posting)  # JS1 v0.4 decision 11
        watch = compute_watch(before, [posting["posting_id"] for posting in postings])
        self.sections_after[board.key] = watch.state_after
        seen = set(before or [])
        line.update(
            status="ok",
            jobs_fetched=len(postings),
            new_ids=list(watch.new_ids),
            already_seen=sum(1 for posting_id in by_id if posting_id in seen),
            baseline=watch.baseline,
            new_postings=[build_record(by_id[posting_id], self.persona) for posting_id in watch.new_ids],
            line=f"ok — {len(postings)} jobs, {len(watch.new_ids)} new" + (" (baseline)" if watch.baseline else ""),
        )
        return line


def _preflight(tools, config, seeds):
    """§5 and §1 item 6 before any fetch or write. Raises Refusal or RunError; returns the seeds read."""
    for board in config.boards:
        tools.policy.check("fetch", board.url)
    tools.policy.check("read", config.resume_path)
    for folder in (config.state_dir, config.evidence_dir, config.output_dir):
        tools.policy.check("write", f"{folder}/.preflight")  # a new file there must be writable
    keys = {board.key for board in config.boards}
    seeded = {}
    for key, path in seeds.items():
        if key not in keys:
            raise RunError(f"--seed names board {key}, which is not in the config")
        seeded[key] = load_seed(tools, path, config.evidence_dir)
    return seeded


def _load_persona(tools, path):
    """The persona, read through the tool layer. Reasons never echo values (§3.2)."""
    try:
        persona = json.loads(tools.read(path))
    except (OSError, ValueError) as exc:
        raise RunError(f"cannot read résumé {Path(path).name}: {type(exc).__name__}") from exc
    check_persona(persona)
    return persona


def _exit(kind, line, **extra):
    return {"kind": kind, "line": line, **extra}


def run(config_path, seeds=None, approvals=(), clock=time.monotonic, now=None):
    """One run of the loop. Returns the report; writes it to output/ unless the run is refused.

    seeds maps a board key to a saved board response under evidence/.
    """
    now = now or (lambda: datetime.now(timezone.utc))
    started, started_at = clock(), now()
    stamp = utc_stamp(started_at)
    config_file = Path(config_path).resolve()
    root = config_file.parent
    seeds = dict(seeds or {})
    report = {
        "contract_version": CONTRACT_VERSION,
        "gate_version": GATE_VERSION,
        "run_at": started_at.isoformat(timespec="seconds"),
        "exit": None,
        "boards": [],
        "trace": [],
        "budgets": None,
        "approvals": [],
        "repeats": [],
        "state": {"read": None, "written": None},
        "report_file": None,
    }

    def finish_early(tools, output_dir, kind, message):
        """refused: no write at all (§1). error before the loop: the report only, no state."""
        report["exit"] = _exit(kind, f"{kind} — {message}")
        report["approvals"] = tools.policy.approval_record()
        if kind == "refused":
            return report
        _write_report(tools, report, f"{output_dir}/run_report_{stamp}.json")
        return report

    bootstrap = ToolLayer(Policy(root, (), approvals=approvals))
    try:
        config = parse_config(bootstrap.read(config_file), config_file.name)
    except Refusal as exc:
        return finish_early(bootstrap, DEFAULT_OUTPUT_DIR, "refused", str(exc))
    except (RunError, OSError) as exc:
        return finish_early(bootstrap, DEFAULT_OUTPUT_DIR, "error", str(exc))

    tools = ToolLayer(Policy(root, config.board_pairs, approvals=approvals))
    try:
        seeded = _preflight(tools, config, seeds)
        persona = _load_persona(tools, config.resume_path)
        state_read, sections = load_state(tools, config.state_dir)
    except Refusal as exc:
        return finish_early(tools, config.output_dir, "refused", str(exc))
    except (RunError, OSError) as exc:
        return finish_early(tools, config.output_dir, "error", str(exc))
    report["state"]["read"] = state_read

    loop = Loop(tools, config, persona, sections, seeded, clock, now, started)
    stopped = exhausted = None
    current = None
    try:
        for board in config.boards:
            live = board.key not in seeded
            stop = "boards" if loop.boards_started >= MAX_BOARDS else loop.budget_stop(live=live)
            if stop:
                exhausted = (stop, board)
                break
            loop.boards_started += 1
            current = board
            line = loop.visit(board)
            loop.lines.append(line)
            current = None
            if line["status"] in ("not completed", "not attempted"):
                exhausted = (line["budget"], board)
                break
    except KeyboardInterrupt:
        stopped = ("incomplete", "operator interrupt")
    except PolicyRefusal as exc:
        stopped = ("incomplete", f"a required write was refused: {exc}")
    except (RunError, OSError) as exc:
        stopped = ("error", str(exc))
    if stopped and current is not None:
        # The board in progress adds no ids: sections_after is only set once a board is accounted for.
        loop.lines.append({"board": current.key, "mode": "seeded" if current.key in seeded else "live",
                           "status": "not completed", "reason": stopped[1], "line": f"not completed — {stopped[1]}"})
    visited = {line["board"] for line in loop.lines}
    for board in config.boards:
        if board.key not in visited:
            loop.lines.append({"board": board.key, "mode": "seeded" if board.key in seeded else "live",
                               "status": "not attempted", "line": "not attempted"})

    # State: temporary file first (v0.6 item 2); moved into place only after the report is written.
    tmp = final = None
    try:
        tmp, final = write_state_tmp(tools, config.state_dir, stamp, loop.sections_after)
    except PolicyRefusal as exc:
        stopped = stopped or ("incomplete", f"a required write was refused: {exc}")
    except OSError as exc:
        stopped = stopped or ("error", f"state not written: {exc}")

    lines = loop.lines
    by_status = lambda *statuses: [line["board"] for line in lines if line["status"] in statuses]  # noqa: E731
    lists = {
        "completed_boards": by_status("ok", "failed"),
        "failed_boards": by_status("failed"),
        "not_completed_boards": by_status("not completed"),
        "not_attempted_boards": by_status("not attempted"),
    }
    if stopped:
        report["exit"] = _exit(stopped[0], f"{stopped[0]} — {stopped[1]}", **lists)
    elif exhausted:
        budget, board = exhausted
        report["exit"] = _exit("budget-exhausted",
                               f"budget-exhausted — {budget} budget ({BUDGET_LIMITS[budget]} per run) ran out on {board.key}",
                               budget=budget, budget_board=board.key, **lists)
    elif lists["failed_boards"]:
        report["exit"] = _exit("finished", "finished — with failures: " + ", ".join(lists["failed_boards"]), **lists)
    else:
        report["exit"] = _exit("finished", "finished", **lists)

    report["boards"] = lines
    report["trace"] = loop.trace
    report["budgets"] = {
        "boards": {"used": loop.boards_started, "max": MAX_BOARDS},
        "requests": {"used": loop.requests, "max": MAX_REQUESTS},
        "seconds": {"used": round(loop.elapsed(), 3), "max": MAX_SECONDS},
    }
    report["state"]["written"] = final if tmp else None
    report["approvals"] = tools.policy.approval_record()
    report["repeats"] = tools.repeats
    if not _write_report(tools, report, f"{config.output_dir}/run_report_{stamp}.json"):
        return report  # no report, so the state stays a temporary file and the next run re-reports
    if tmp:
        try:
            commit_state(tools, tmp, final)
        except (PolicyRefusal, OSError) as exc:
            report["state"]["written"] = None
            report["state_error"] = f"state left at {tmp}, not moved into place: {exc}"
    return report


def _write_report(tools, report, path):
    report["report_file"] = path
    try:
        tools.write(path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    except (PolicyRefusal, OSError) as exc:
        report["report_file"] = None
        report["report_error"] = str(exc)
        return False
    return True
