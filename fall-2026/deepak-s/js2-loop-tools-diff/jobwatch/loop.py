"""The bounded loop: GATE.md sections 0 to 4.

    run_loop(config_path, ...) -> exit code

Plans from config/boards.json, reads budgets only from config/budgets.json, fetches each board
through jobwatch/tools.py, applies the error policy and the repeat rule, records one trace line per
action in runs/<run-id>/trace.jsonl, and ends in exactly one exit. Every disk and network access
goes through Tools.
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone

from jobwatch import providers
from jobwatch.errors import Stop
from jobwatch.persona import check_resume
from jobwatch.policy import HOST_SYSTEM, Policy
from jobwatch.rule import apply_rule
from jobwatch.tools import ApprovalDenied, PolicyDenied, RepeatRefused, Tools

FINISHED, INCOMPLETE, BUDGET_EXHAUSTED, ERROR = "FINISHED", "INCOMPLETE", "BUDGET_EXHAUSTED", "ERROR"
EXIT_CODES = {FINISHED: 0, ERROR: 1, INCOMPLETE: 3, BUDGET_EXHAUSTED: 4}
BUDGETS_PATH = "config/budgets.json"
STATE_PATH = "state/seen.json"
RESUME_PATH = "examples/persona_resume.json"
SCHEMA_PATH = "schema/resume.schema.json"
BUDGET_KEYS = ("max_boards", "max_requests", "max_seconds", "request_timeout_seconds",
               "min_seconds_between_same_host", "max_retries_per_action", "retry_backoff_seconds")
STATE_SCHEMA_VERSION = 1


class LoopError(Exception):
    """Ends the run with ERROR (GATE.md section 1)."""


def run_id_for(now):
    return now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def board_key(board):
    """GATE.md section 0: identity is (system, slug); the host is not part of it (W12)."""
    return f"{board['system']}:{board['slug']}"


def _json(data, what):
    try:
        return json.loads(data)
    except ValueError:
        raise LoopError(f"{what} is not valid JSON") from None


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


# --- config (GATE.md section 0) ------------------------------------------------------------
def check_host_system(board):
    """The host must be on the allow-list and belong to the board's system (W14)."""
    if HOST_SYSTEM.get(board["host"]) != board["system"]:
        raise LoopError(f"config: host {board['host']!r} does not belong to system {board['system']!r}")


def check_duplicates(boards):
    """No (system, slug) twice (W13)."""
    seen = set()
    for b in boards:
        k = board_key(b)
        if k in seen:
            raise LoopError(f"config: board {k} appears twice")
        seen.add(k)


def validate_config(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("boards"), list):
        raise LoopError('config: expected an object with a "boards" list')
    boards = []
    for i, b in enumerate(doc["boards"]):
        if not isinstance(b, dict):
            raise LoopError(f"config: boards[{i}] is not an object")
        for field in ("system", "slug", "host"):
            if not isinstance(b.get(field), str) or not b[field]:
                raise LoopError(f"config: boards[{i}].{field} is missing")
        if b["system"] not in ("greenhouse", "lever", "ashby"):
            raise LoopError(f"config: boards[{i}].system {b['system']!r} is not greenhouse, lever or ashby")
        if b["host"] not in HOST_SYSTEM:
            raise LoopError(f"config: boards[{i}].host {b['host']!r} is not on the allow-list")
        check_host_system(b)
        # "deliberate_failure" and any other extra field are labels only; they are not copied.
        boards.append({"system": b["system"], "slug": b["slug"], "host": b["host"]})
    check_duplicates(boards)
    return boards


def validate_budgets(doc):
    if not isinstance(doc, dict):
        raise LoopError("budgets: not an object")
    out = {}
    for k in BUDGET_KEYS:
        v = doc.get(k)
        if type(v) not in (int, float) or v < 0:
            raise LoopError(f"budgets: {k} is missing or not a non-negative number")
        out[k] = v
    return out


def validate_state(raw):
    """GATE.md section 0: corrupt state is ERROR, not baseline."""
    if not raw.strip():
        raise LoopError("corrupt state: empty")
    doc = _json(raw, "corrupt state: state/seen.json")
    if not isinstance(doc, dict) or doc.get("schema_version") != STATE_SCHEMA_VERSION:
        raise LoopError("corrupt state: unknown schema_version")
    boards = doc.get("boards")
    if not isinstance(boards, dict):
        raise LoopError("corrupt state: boards is not an object")
    for k, v in boards.items():
        seen = v.get("seen_ids") if isinstance(v, dict) else None
        if not isinstance(seen, list) or not all(isinstance(s, str) for s in seen) or len(set(seen)) != len(seen):
            raise LoopError(f"corrupt state: {k}.seen_ids is not a list of unique strings")
    return doc


# --- budget (GATE.md section 2) ------------------------------------------------------------
class Budget:
    def __init__(self, limits, clock):
        self.limits = limits
        self.clock = clock
        self.start = clock()
        self.requests = 0

    def elapsed(self):
        return self.clock() - self.start

    def exhausted(self):
        """Checked before every request, retries included. Returns (budget, value) or None."""
        if self.requests >= self.limits["max_requests"]:
            return "max_requests", self.requests
        if self.elapsed() >= self.limits["max_seconds"]:
            return "max_seconds", round(self.elapsed(), 3)
        return None

    def note_request(self, is_retry):
        """Every request counts, retries included (W08)."""
        self.requests += 1


# --- per-board results ---------------------------------------------------------------------
def failed_result(base, reason, err, retries):
    """A failed board is never "0 new": count and new_ids are null (GATE.md section 1, W06)."""
    return {**base, "status": "FAILED", "count": None, "new_ids": None, "baseline": None,
            "reason": reason, "http_status": err.http_status if err else None,
            "detail": err.detail if err else None, "retry_after": err.retry_after if err else None,
            "retries_used": retries}


def decide_exit(results, budget_hit, error):
    """GATE.md section 1 order: ERROR, BUDGET_EXHAUSTED, INCOMPLETE, FINISHED (W07)."""
    if error is not None:
        return ERROR
    if budget_hit is not None:
        return BUDGET_EXHAUSTED
    if any(r["status"] != "OK" for r in results):
        return INCOMPLETE
    return FINISHED


class Loop:
    def __init__(self, config_path, *, root=".", transport=None, now=None, clock=time.monotonic,
                 sleep=time.sleep, approver=None, label="live", wall_clock=None):
        self.config_path = config_path
        self.now = now or datetime.now(timezone.utc)
        self.run_id = run_id_for(self.now)
        self.run_dir = f"runs/{self.run_id}"
        self.clock, self.sleep = clock, sleep
        self.label = label
        self.policy = Policy(root, run_id=self.run_id)
        self.step = 0
        self.trace_ok = False
        kw = {"wall_clock": wall_clock} if wall_clock else {}
        self.tools = Tools(self.policy, transport=transport, approver=approver, on_event=self._trace, **kw)
        self.manifest = []
        self.results = []
        self.context = {}
        self.lines = []

    # --- trace (GATE.md section 3 bookkeeping) ---------------------------------------------
    def _trace(self, ev):
        self.step += 1
        line = {"ts": ev["ts"], "step": self.step, **self.context, "tool": ev["tool"], "args": ev["args"],
                "policy": ev["policy"], "policy_reason": ev.get("policy_reason"),
                "http_status": ev.get("http_status"), "bytes": ev.get("bytes"),
                "sha256": ev.get("sha256"), "outcome": ev["outcome"], "label": self.label}
        self._append(line)

    def note(self, outcome, **fields):
        """A loop decision (retry, budget stop, board result, exit) as a trace line with no tool."""
        self.step += 1
        self._append({"ts": self.tools.wall_clock(), "step": self.step, **self.context, "tool": None,
                      "args": None, "policy": None, "policy_reason": None, "http_status": None,
                      "bytes": None, "sha256": None, "outcome": outcome, "label": self.label, **fields})

    def _append(self, line):
        self.lines.append(line)
        self.tools.write_file(f"{self.run_dir}/trace.jsonl",
                              json.dumps(line, ensure_ascii=False) + "\n", mode="append")

    # --- the run ---------------------------------------------------------------------------
    def run(self):
        try:
            self.tools.read_file(f"{self.run_dir}/summary.json")
        except FileNotFoundError:
            pass
        else:
            print(f"jobwatch: ERROR: {self.run_dir} already holds a run; nothing written", file=sys.stderr)
            return EXIT_CODES[ERROR]
        error, budget_hit, unvisited, state_doc, state_raw = None, None, [], None, None
        step_name = "start"
        budgets = None
        try:
            step_name = "read budgets"
            budgets = validate_budgets(_json(self.tools.read_file(BUDGETS_PATH), "budgets"))
            self.tools.timeout = budgets["request_timeout_seconds"]
            self.tools.max_retries = int(budgets["max_retries_per_action"])
            step_name = "read config"
            config_raw = self.tools.read_file(self.config_path)
            boards = validate_config(_json(config_raw, "config"))
            step_name = "read state"
            try:
                state_raw = self.tools.read_file(STATE_PATH)
            except FileNotFoundError:
                state_raw = None
            except OSError:
                raise LoopError("corrupt state: unreadable") from None
            state_doc = validate_state(state_raw) if state_raw is not None else None
            if state_raw is not None:
                self.tools.write_file(f"{self.run_dir}/state_before.json", state_raw)
            step_name = "read resume"
            schema = _json(self.tools.read_file(SCHEMA_PATH), "schema")
            resume = check_resume(self.tools.read_file(RESUME_PATH), schema)

            planned = boards[: int(budgets["max_boards"])]
            unvisited = [board_key(b) for b in boards[len(planned):]]
            if unvisited:
                budget_hit = {"budget": "max_boards", "value": len(boards), "board_in_progress": None}
            budget = Budget(budgets, self.clock)
            last_at = {}
            for i, board in enumerate(planned):
                step_name = f"board {board_key(board)}"
                self.context = {"board": board_key(board)}
                result, hit = self._visit(board, budgets, budget, last_at, state_doc, resume)
                self.results.append(result)
                if hit is not None:
                    budget_hit = {"budget": hit[0], "value": hit[1], "board_in_progress": board_key(board)}
                    unvisited = [board_key(b) for b in planned[i + 1:]] + unvisited
                    break
            self.context = {}
        except (LoopError, PolicyDenied, ApprovalDenied, Stop) as e:
            error = {"error": f"{type(e).__name__}: {e}", "step": step_name}
        except Exception as e:  # GATE.md section 1: an unexpected exception is ERROR
            error = {"error": f"unexpected {type(e).__name__}: {e}", "step": step_name}
        self.context = {}

        status = decide_exit(self.results, budget_hit, error)
        return self._finish(status, error, budget_hit, unvisited, budgets, state_raw, state_doc)

    def _visit(self, board, budgets, budget, last_at, state_doc, resume):
        key = board_key(board)
        provider = providers.get(board["system"])
        url = provider.url(board["host"], board["slug"])
        base = {"key": key, "system": board["system"], "slug": board["slug"], "host": board["host"], "url": url}
        attempt, retries, err = 0, 0, None
        while True:
            if attempt > 0:
                self.note("retry scheduled", wait_seconds=budgets["retry_backoff_seconds"])
                self.sleep(budgets["retry_backoff_seconds"])
            wait = last_at.get(board["host"], -1e18) + budgets["min_seconds_between_same_host"] - self.clock()
            if wait > 0:
                self.sleep(wait)
            hit = budget.exhausted()
            if hit is not None:
                self.note("budget exhausted", budget=hit[0], value=hit[1])
                return failed_result(base, "budget", err, retries), hit
            attempt += 1
            budget.note_request(is_retry=attempt > 1)
            try:
                result = self.tools.fetch_json(url)
            except RepeatRefused:
                r = failed_result(base, "repeat", err, retries)
                self.note("board FAILED", reason="repeat")
                return r, None
            last_at[board["host"]] = self.clock()
            raw_file = self._save_raw(board, attempt, result)
            parsed = provider.parse(result, key)
            if isinstance(parsed, providers.BoardError):
                err = parsed
                if parsed.retryable and retries < int(budgets["max_retries_per_action"]):
                    retries += 1
                    continue
                r = failed_result(base, parsed.kind, parsed, retries)
                r["raw_file"] = raw_file
                self.note("board FAILED", reason=parsed.kind, http_status=parsed.http_status)
                return r, None
            return self._ok_result(base, parsed, result, raw_file, retries, state_doc, resume), None

    def _save_raw(self, board, attempt, result):
        if result.error is not None:
            return None
        name = f"raw/{board['system']}_{board['slug']}_attempt{attempt}.body"
        self.tools.write_file(f"{self.run_dir}/{name}", result.body)
        self.manifest.append({"path": name, "board": board_key(board), "attempt": attempt,
                              "http_status": result.status, "content_type": result.content_type,
                              "bytes": len(result.body), "sha256": result.sha256})
        return name

    def _ok_result(self, base, postings, result, raw_file, retries, state_doc, resume):
        key = base["key"]
        known = (state_doc or {}).get("boards", {}).get(key)
        ids = [p.id for p in postings]
        baseline = known is None
        new_ids = [] if baseline else [i for i in ids if i not in set(known["seen_ids"])]
        new_set = set(new_ids)
        record = []
        for p in postings:
            if p.id in new_set:
                verdict = apply_rule(resume, {"title": p.title, "location": {"name": p.location}})
                record.append({"id": p.id, "title": p.title, "location": p.location, "url": p.url, **verdict})
        self.note("board OK", count=len(ids), new=len(new_ids), baseline=baseline)
        return {**base, "status": "OK", "count": len(ids), "new_ids": new_ids, "baseline": baseline,
                "ids": ids, "sha256": result.sha256, "raw_file": raw_file, "http_status": result.status,
                "retries_used": retries, "reason": None, "record": record}

    def _commit_state(self, state_doc, status):
        """GATE.md section 1: only boards that succeeded, one atomic replace at the end."""
        boards = dict((state_doc or {}).get("boards", {}))
        for r in self.results:
            if r["status"] != "OK":
                continue
            prior = set(boards.get(r["key"], {}).get("seen_ids", []))
            boards[r["key"]] = {"seen_ids": sorted(prior | set(r["ids"])), "last_run_id": self.run_id,
                                "last_count": r["count"]}
        doc = {"schema_version": STATE_SCHEMA_VERSION, "boards": boards,
               "updated_at": self.now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "last_run_id": self.run_id}
        self.policy.arm_state_commit(status)
        self.tools.write_file(STATE_PATH, json_bytes(doc))

    def _finish(self, status, error, budget_hit, unvisited, budgets, state_raw, state_doc):
        code = EXIT_CODES[status]
        # GATE.md section 1: state changes only on FINISHED or INCOMPLETE. The replace runs below,
        # only after the run record is written, so a failed record write leaves state untouched.
        state_updated = status in (FINISHED, INCOMPLETE)
        failed = [r["key"] for r in self.results if r["status"] != "OK"]
        if error is not None:
            cause = f"{error['error']} (step: {error['step']})"
        elif budget_hit is not None:
            cause = f"budget {budget_hit['budget']} reached; unvisited: {', '.join(unvisited) or 'none'}"
        elif failed:
            cause = "failed boards: " + ", ".join(
                f"{r['key']} ({r['reason']})" for r in self.results if r["status"] != "OK")
        else:
            cause = "every planned board fetched, validated and diffed"
        boards_out = [{k: v for k, v in r.items() if k != "ids"} for r in self.results]
        boards_out += [{"key": k, "status": "UNVISITED", "count": None, "new_ids": None, "baseline": None,
                        "reason": "budget" if budget_hit else "not reached"} for k in unvisited]
        summary = {
            "run_id": self.run_id, "label": self.label, "exit": status, "exit_code": code, "cause": cause,
            "needs_deepak": status == ERROR or self.tools.needs_deepak,
            "started_at": self.now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "config": self.config_path, "budgets": budgets,
            "requests_used": len(self.tools.requests_sent),
            "budget_exhausted": ({**budget_hit, "unvisited": unvisited} if budget_hit else None),
            "error": error, "boards": boards_out,
            "state_before_sha256": hashlib.sha256(state_raw).hexdigest() if state_raw is not None else None,
            "state_updated": state_updated,
        }
        try:
            self.note("exit", exit=status, exit_code=code)
            self.tools.write_file(f"{self.run_dir}/manifest.json",
                                  json_bytes({"run_id": self.run_id, "label": self.label, "files": self.manifest}))
            self.tools.write_file(f"{self.run_dir}/summary.json", json_bytes(summary))
            self.tools.write_file(f"{self.run_dir}/trace.md",
                                  render_trace_md(self.lines, summary))
        except Exception as e:
            print(f"jobwatch: ERROR: could not write the run record: {type(e).__name__}: {e}", file=sys.stderr)
            return EXIT_CODES[ERROR]
        if state_updated:
            try:
                self._commit_state(state_doc, status)
            except Exception as e:
                error = {"error": f"state write failed: {type(e).__name__}: {e}", "step": "state replace"}
                summary.update(exit=ERROR, exit_code=EXIT_CODES[ERROR], needs_deepak=True, state_updated=False,
                               error=error, cause=f"{error['error']} (step: state replace)")
                self.tools.write_file(f"{self.run_dir}/summary.json", json_bytes(summary))
                print(f"jobwatch: ERROR: {summary['cause']}", file=sys.stderr)
                return EXIT_CODES[ERROR]
        if code != 0:
            print(f"jobwatch: {status}: {cause}", file=sys.stderr)
        else:
            print(f"jobwatch: {status}: run {self.run_id}")
        return code


def render_trace_md(trace_lines, summary):
    """runs/<id>/trace.md: the trace.jsonl lines written up to this point, and summary.json."""
    lines = [f"# Trace of run {summary['run_id']} ({summary['label']})", "",
             f"Exit: **{summary['exit']}** (code {summary['exit_code']}). {summary['cause']}", "",
             "Generated by jobwatch at the end of the run from the lines it wrote to trace.jsonl "
             "(the write of this file is the last trace.jsonl line and is not listed here).", "",
             "| step | ts | board | tool | args | policy | HTTP | bytes | sha256 | outcome |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for t in trace_lines:
        args = t["args"] or {}
        arg = args.get("url") or args.get("path") or ""
        extra = {k: v for k, v in t.items() if k not in (
            "ts", "step", "board", "tool", "args", "policy", "policy_reason", "http_status", "bytes",
            "sha256", "outcome", "label")}
        outcome = t["outcome"] + (" " + json.dumps(extra) if extra else "")
        sha = (t["sha256"] or "")[:12]
        lines.append(f"| {t['step']} | {t['ts']} | {t.get('board') or ''} | {t['tool'] or 'loop'} | {arg} | "
                     f"{t['policy'] or ''} | {t['http_status'] or ''} | {t['bytes'] if t['bytes'] is not None else ''} | "
                     f"{sha} | {outcome} |")
    lines += ["", "## Boards", "", "| board | status | count | new | baseline | reason | retries |",
              "|---|---|---|---|---|---|---|"]
    for b in summary["boards"]:
        new = len(b["new_ids"]) if b.get("new_ids") is not None else "null"
        lines.append(f"| {b['key']} | {b['status']} | {b['count'] if b['count'] is not None else 'null'} | {new} | "
                     f"{b.get('baseline')} | {b.get('reason') or ''} | {b.get('retries_used', '')} |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def run_loop(config_path, **kw):
    loop = Loop(config_path, **kw)
    return loop.run()
