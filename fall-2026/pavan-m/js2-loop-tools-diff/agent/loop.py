"""Bounded multi-board loop (GATE.md sections 2-5).

One run: validate config and state, then for each board fetch (or replay) once, with at most
one retry on a transient failure, inside fixed request/time/board budgets. Every observation
goes to out/runs/<stamp>/trace.jsonl; raw responses to raw/; the result to summary.json.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

from agent import adapters
from agent.policy import (
    PolicyError,
    append_line,
    check_read,
    check_url,
    make_client,
    make_dir,
    reset_state,
    safe_key,
    state_path,
    write_atomic,
    write_new,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# GATE.md section 3. Callers may lower these, never raise them.
DEFAULT_BUDGETS = {
    "max_boards": 4,
    "max_requests": 10,
    "max_seconds": 60,
    "request_timeout": 10,
    "retry_wait": 2,
}

EXIT_CODES = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}


class ConfigError(Exception):
    pass


class _BudgetStop(Exception):
    def __init__(self, which, detail):
        super().__init__(detail)
        self.which = which
        self.detail = detail


def _merge_budgets(budgets):
    merged = dict(DEFAULT_BUDGETS)
    for name, value in (budgets or {}).items():
        if name not in DEFAULT_BUDGETS:
            raise ConfigError(f"unknown budget: {name!r}")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ConfigError(f"budget {name} must be a non-negative number, got {value!r}")
        if value > DEFAULT_BUDGETS[name]:
            raise ConfigError(
                f"budget {name}={value} exceeds GATE.md limit {DEFAULT_BUDGETS[name]}; "
                "budgets change only by a dated GATE.md decision"
            )
        merged[name] = value
    return merged


def _validate_boards(boards):
    if not isinstance(boards, list):
        raise ConfigError("boards must be a list")
    for i, b in enumerate(boards):
        if not isinstance(b, dict):
            raise ConfigError(f"board {i} is not an object")
        for field in ("key", "system", "url"):
            if not isinstance(b.get(field), str):
                raise ConfigError(f"board {i} needs a string {field!r}")
        if b["system"] not in adapters.SYSTEMS:
            raise ConfigError(f"board {i}: unknown system {b['system']!r}")
        try:
            safe_key(b["key"])
        except PolicyError as e:
            raise ConfigError(f"board {i}: {e}") from None
        if not b["key"].startswith(b["system"] + ":"):
            raise ConfigError(f"board {i}: key {b['key']!r} must start with {b['system']!r}:")
        try:
            check_url(b["url"])
        except PolicyError as e:
            raise ConfigError(f"board {i}: configured url refused: {e}") from None
        if "replay" in b and not isinstance(b["replay"], str):
            raise ConfigError(f"board {i}: replay must be a path string")


def _make_run_dir(root):
    runs = make_dir(Path(root) / "out" / "runs", root)
    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    n = 0
    while True:
        name = stamp if n == 0 else f"{stamp}-{n}"
        candidate = runs / name
        try:
            make_dir(runs, root)  # re-check the parent before creating
            os.mkdir(candidate)  # exclusive: fails if another run took this name
        except FileExistsError:
            n += 1
            continue
        make_dir(candidate / "raw", root)
        return candidate


class _Run:
    def __init__(self, root, client, budgets, sleep, approvals):
        self.root = Path(root)
        self.client = client
        self.budgets = budgets
        self.sleep = sleep
        self.approvals = set(approvals or ())
        self.start = time.monotonic()
        self.requests_used = 0
        self.sent = set()  # (method, url) actually sent this run
        self.run_dir = None
        self.boards = {}
        self.duplicates = []
        self.seen = {}  # board key -> set of composite ids, or None for baseline

    # ---------- recording ----------

    def elapsed(self):
        return time.monotonic() - self.start

    def trace(self, event, **fields):
        if self.run_dir is None:
            return
        line = {"t": round(self.elapsed(), 3), "event": event, **fields}
        append_line(self.run_dir / "trace.jsonl", json.dumps(line, ensure_ascii=False), self.root)

    def save_raw(self, key, content, suffix=""):
        name = f"{safe_key(key)}{suffix}.json"
        write_new(self.run_dir / "raw" / name, content, self.root)
        return f"raw/{name}"

    def result(self, key, status, reason, postings=None, new=None, **extra):
        self.boards[key] = {"status": status, "reason": reason, "postings": postings, "new": new, **extra}
        self.trace("board_result", board=key, status=status, reason=reason,
                   postings=postings, new=None if new is None else len(new))

    # ---------- setup ----------

    def load_states(self, keys):
        for key in keys:
            p = state_path(key, self.root)
            if not p.exists():
                self.seen[key] = None
                continue
            try:
                state = json.loads(check_read(p, self.root).read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise ConfigError(f"state for {key} is unreadable: {e}") from None
            ids = state.get("seen_ids") if isinstance(state, dict) else None
            if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
                raise ConfigError(f"state for {key} is malformed: {p}")
            self.seen[key] = set(ids)

    def apply_resets(self, keys):
        for approval in sorted(self.approvals):
            if not approval.startswith("reset:") or approval[len("reset:"):] not in keys:
                raise ConfigError(f"approval {approval!r} does not match a configured board")
        for key in keys:
            if f"reset:{key}" in self.approvals:
                reset_state(key, self.root, self.approvals)
                self.seen[key] = set()
                self.trace("state_reset", board=key, approval=f"reset:{key}")

    # ---------- budgets ----------

    def check_request_budget(self):
        if self.requests_used >= self.budgets["max_requests"]:
            raise _BudgetStop("max_requests",
                              f"request budget reached ({self.requests_used}/{self.budgets['max_requests']})")
        if self.elapsed() >= self.budgets["max_seconds"]:
            raise _BudgetStop("max_seconds",
                              f"time budget reached ({self.elapsed():.1f}s/{self.budgets['max_seconds']}s)")

    def request_timeout(self):
        # Never let one request run past the end of the run's time budget.
        return min(self.budgets["request_timeout"], self.budgets["max_seconds"] - self.elapsed())

    # ---------- one board ----------

    def send(self, key, url, attempt):
        """One GET. Returns (kind, info): ok/http/transient/refused/bad."""
        self.check_request_budget()
        self.sent.add(("GET", url))
        self.trace("request", board=key, method="GET", url=url, attempt=attempt)
        try:
            response = self.client.get(url, follow_redirects=True, timeout=self.request_timeout())
        except PolicyError as e:
            # The configured URL passed the static check, so this came from a redirect.
            self.requests_used += 1
            self.trace("response", board=key, attempt=attempt, error="policy_refused", detail=str(e))
            return "refused", {"detail": str(e)}
        except httpx.TimeoutException as e:
            self.requests_used += 1
            self.trace("response", board=key, attempt=attempt, error="timeout", detail=repr(e))
            return "transient", {"detail": f"timeout: {e!r}"}
        except httpx.TooManyRedirects as e:
            self.requests_used += 1
            self.trace("response", board=key, attempt=attempt, error="too_many_redirects", detail=str(e))
            return "bad", {"detail": f"too many redirects: {e}"}
        except httpx.TransportError as e:
            self.requests_used += 1
            self.trace("response", board=key, attempt=attempt, error="connection_error", detail=repr(e))
            return "transient", {"detail": f"connection error: {e!r}"}

        self.requests_used += 1 + len(response.history)
        raw = self.save_raw(key, response.content, "" if attempt == 1 else f".attempt{attempt}")
        status = response.status_code
        self.trace("response", board=key, attempt=attempt, status=status,
                   bytes=len(response.content), redirects=len(response.history),
                   final_url=str(response.url), raw_file=raw)
        info = {"http_status": status, "raw_file": raw, "content": response.content}
        if 200 <= status < 300:
            return "ok", info
        if status >= 500:
            info["detail"] = f"HTTP {status}"
            return "transient", info
        return "http", info

    def fetch(self, b):
        key, url = b["key"], b["url"]
        kind, info = self.send(key, url, attempt=1)
        if kind == "transient":
            # GATE.md section 5: exactly one retry, after retry_wait, if the budgets allow it.
            wait = self.budgets["retry_wait"]
            try:
                self.check_request_budget()
                if self.elapsed() + wait >= self.budgets["max_seconds"]:
                    raise _BudgetStop("max_seconds", "no time left for the retry wait")
            except _BudgetStop as stop:
                self.trace("budget_stop", board=key, budget=stop.which, detail=stop.detail, during="retry")
                self.result(key, "failed", "retry_not_sent_budget", detail=info.get("detail"),
                            http_status=info.get("http_status"), raw_file=info.get("raw_file"))
                raise
            self.trace("retry", board=key, wait_seconds=wait, after=info.get("detail"))
            self.sleep(wait)
            try:
                kind, info = self.send(key, url, attempt=2)
            except _BudgetStop as stop:
                self.trace("budget_stop", board=key, budget=stop.which, detail=stop.detail, during="retry")
                self.result(key, "failed", "retry_not_sent_budget", detail=info.get("detail"),
                            http_status=info.get("http_status"), raw_file=info.get("raw_file"))
                raise
        self.finish_board(b, kind, info, source="live")

    def replay(self, b):
        key = b["key"]
        src = check_read(self.root / b["replay"], self.root)
        if not src.is_relative_to((self.root / "evidence").resolve()):
            raise PolicyError(f"replay file must be under evidence/: {b['replay']}")
        content = src.read_bytes()
        raw = self.save_raw(key, content)
        self.trace("replay", board=key, source=str(src.relative_to(self.root.resolve())),
                   bytes=len(content), raw_file=raw)
        self.finish_board(b, "ok", {"raw_file": raw, "content": content}, source="replay")

    def finish_board(self, b, kind, info, source):
        key = b["key"]
        common = {"source": source, "http_status": info.get("http_status"), "raw_file": info.get("raw_file")}
        if kind == "refused":
            return self.result(key, "failed", "policy_refused", detail=info["detail"], **common)
        if kind == "bad":
            return self.result(key, "failed", "bad_response", detail=info["detail"], **common)
        if kind == "transient":
            return self.result(key, "failed", "unreachable", detail=info["detail"], **common)
        if kind == "http":
            status = info["http_status"]
            reason = "rate_limited" if status == 429 else "bad_board" if status == 404 else "client_error"
            return self.result(key, "failed", reason, detail=f"HTTP {status}", **common)

        try:
            postings = adapters.parse(b["system"], json.loads(info["content"]))
        except ValueError as e:  # invalid JSON, wrong shape (BadResponse), or bad encoding
            return self.result(key, "failed", "bad_response", detail=f"{type(e).__name__}: {e}", **common)

        current, unusable = [], []
        for i, p in enumerate(postings):
            pk = adapters.posting_key(key, p)
            if pk is None:
                unusable.append({"index": i, "id": p.get("id")})
            elif pk not in current:
                current.append(pk)

        seen = self.seen[key]
        baseline = seen is None
        new = [] if baseline else [pk for pk in current if pk not in seen]

        state_written = False
        if source == "live":
            merged = sorted((seen or set()) | set(current))
            write_atomic(state_path(key, self.root), json.dumps({"seen_ids": merged}), self.root)
            self.seen[key] = set(merged)
            state_written = True
            self.trace("state_write", board=key, seen_ids=len(merged), baseline=baseline)

        self.result(key, "ok", "baseline" if baseline else "compared", postings=len(postings), new=new,
                    baseline=baseline, usable_ids=len(current), unusable_ids=len(unusable),
                    unusable_examples=unusable[:5], state_written=state_written, **common)

    # ---------- whole run ----------

    def run(self, boards):
        status, reason = None, None
        try:
            self.run_dir = _make_run_dir(self.root)
        except (PolicyError, OSError) as e:
            return self.summary("error", f"could not create run folder: {e}")
        self.trace("run_start", budgets=self.budgets, boards=len(boards) if isinstance(boards, list) else None)

        try:
            _validate_boards(boards)
            unique = list(dict.fromkeys(b["key"] for b in boards))
            self.load_states(unique)
            self.apply_resets(unique)
        except (ConfigError, PolicyError, OSError) as e:
            self.trace("error", detail=str(e))
            return self.summary("error", str(e))

        stopped = None
        attempted = set()
        try:
            for index, b in enumerate(boards):
                key = b["key"]
                if key in attempted or key in self.boards:
                    self.duplicates.append({"index": index, "key": key})
                    self.trace("repeat_blocked", board=key, index=index, why="duplicate board key")
                    continue
                if stopped:
                    self.result(key, "not_attempted", f"stopped: {stopped.which}")
                    continue
                try:
                    if len(attempted) >= self.budgets["max_boards"]:
                        raise _BudgetStop("max_boards", f"board budget reached ({self.budgets['max_boards']})")
                    if "replay" in b:
                        attempted.add(key)
                        self.replay(b)
                    elif ("GET", b["url"]) in self.sent:
                        attempted.add(key)
                        self.trace("repeat_blocked", board=key, index=index, why="identical GET already sent",
                                   url=b["url"])
                        self.result(key, "repeat_blocked", "identical GET already sent this run")
                    else:
                        attempted.add(key)
                        self.fetch(b)
                except _BudgetStop as stop:
                    stopped = stop
                    if key not in self.boards:
                        self.trace("budget_stop", board=key, budget=stop.which, detail=stop.detail)
                        attempted.discard(key)
                        self.result(key, "not_attempted", f"stopped: {stop.which}")
        except PolicyError as e:
            # The agent's own code tried something the policy refuses: stop the whole run.
            self.trace("error", detail=f"policy violation by agent: {e}")
            status, reason = "error", f"policy violation by agent: {e}"
        except Exception as e:
            self.trace("error", detail=f"{type(e).__name__}: {e}")
            status, reason = "error", f"{type(e).__name__}: {e}"

        if status is None:
            failed = [k for k, v in self.boards.items() if v["status"] not in ("ok", "not_attempted")]
            if stopped:
                status, reason = "budget-exhausted", stopped.detail
            elif failed:
                status, reason = "incomplete", f"{len(failed)} board(s) did not succeed: {', '.join(failed)}"
            else:
                status, reason = "finished", f"all {len(self.boards)} board(s) succeeded"
        return self.summary(status, reason)

    def summary(self, status, reason):
        by = lambda s: [k for k, v in self.boards.items() if v["status"] == s]
        summary = {
            "status": status,
            "exit_code": EXIT_CODES[status],
            "reason": reason,
            "requests_used": self.requests_used,
            "elapsed_seconds": round(self.elapsed(), 3),
            "budgets": self.budgets,
            "boards_attempted": [k for k, v in self.boards.items() if v["status"] != "not_attempted"],
            "boards_succeeded": by("ok"),
            "boards_failed": by("failed"),
            "boards_repeat_blocked": by("repeat_blocked"),
            "boards_not_attempted": by("not_attempted"),
            "new_counts": {k: len(v["new"]) for k, v in self.boards.items() if v["status"] == "ok"},
            "failures": {k: {"reason": v["reason"], "detail": v.get("detail")}
                         for k, v in self.boards.items() if v["status"] == "failed"},
            "duplicate_entries": self.duplicates,
            "replayed": [k for k, v in self.boards.items() if v.get("source") == "replay"],
            "run_dir": str(self.run_dir) if self.run_dir else None,
            "trace": str(self.run_dir / "trace.jsonl") if self.run_dir else None,
            "raw_dir": str(self.run_dir / "raw") if self.run_dir else None,
            "boards": self.boards,
        }
        if self.run_dir is not None:
            self.trace("run_end", status=status, exit_code=summary["exit_code"], reason=reason,
                       requests_used=self.requests_used)
            write_new(self.run_dir / "summary.json",
                      json.dumps(summary, indent=2, ensure_ascii=False) + "\n", self.root)
        summary["run_dir"] = self.run_dir
        return summary


def run_loop(boards, root, client, budgets=None, sleep=time.sleep, approvals=None):
    try:
        merged = _merge_budgets(budgets)
    except ConfigError as e:
        run = _Run(root, client, dict(DEFAULT_BUDGETS), sleep, approvals)
        try:
            run.run_dir = _make_run_dir(root)
            run.trace("error", detail=str(e))
        except (PolicyError, OSError):
            pass
        return run.summary("error", str(e))
    return _Run(root, client, merged, sleep, approvals).run(boards)


def main(argv=None, root=None, client=None):
    parser = argparse.ArgumentParser(prog="python -m agent.loop")
    parser.add_argument("--config", required=True, help="board config under config/")
    parser.add_argument("--approve", action="append", default=[], metavar="reset:<board-key>",
                        help="explicit approval, e.g. reset:lever:palantir (repeatable)")
    args = parser.parse_args(argv)
    root = Path(root) if root else PROJECT_ROOT

    try:
        cfg = json.loads(check_read(Path(args.config).absolute(), root).read_text(encoding="utf-8"))
        boards = cfg["boards"] if isinstance(cfg, dict) else cfg
    except (PolicyError, OSError, ValueError, KeyError) as e:
        print(json.dumps({"status": "error", "exit_code": 3, "reason": f"config unreadable: {e}"}, indent=2))
        return 3

    own_client = client is None
    client = client or make_client()
    try:
        summary = run_loop(boards, root, client, approvals=args.approve)
    finally:
        if own_client:
            client.close()
    printable = dict(summary, run_dir=str(summary["run_dir"]) if summary["run_dir"] else None)
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    return summary["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
