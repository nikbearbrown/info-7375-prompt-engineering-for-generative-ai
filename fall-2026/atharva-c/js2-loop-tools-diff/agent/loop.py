"""The bounded watch loop (GATE.md: Exits, Budgets, Repeat Rule, Error Policy).

Usage (run from the js2-loop-tools-diff/ folder):
    python3 -m agent.loop                         # live run on boards.json
    python3 -m agent.loop --replay out/run-<id>   # re-run from saved raw responses

Every run writes out/<run-id>/: report.json, trace.jsonl, raw/ and seen-before.json.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from agent.policy import Policy, PolicyViolation, guarded_write

FINISHED = "finished"
INCOMPLETE = "incomplete"
BUDGET_EXHAUSTED = "budget-exhausted"
ERROR = "error"
EXIT_CODES = {FINISHED: 0, INCOMPLETE: 1, BUDGET_EXHAUSTED: 2, ERROR: 3}

USER_AGENT = "js2-job-watch/0.1 (course project; read-only)"


@dataclass
class Response:
    status: int
    body: str


class BudgetStop(Exception):
    """Internal: a budget limit was hit; the loop stops with budget-exhausted."""


# ---- repeat rule ------------------------------------------------------------

def normalize(url: str) -> str:
    """GATE.md > Repeat Rule: lowercase host and path, strip trailing slash."""
    p = urlsplit(url)
    path = p.path.lower().rstrip("/")
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, p.query, ""))


# ---- parsing ----------------------------------------------------------------

def extract_jobs(ats: str, data) -> list[dict] | None:
    """Return a list of jobs, or None if the JSON is not the expected shape."""
    if ats == "greenhouse":
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            return None
        return [
            {
                "id": str(j.get("id")),
                "title": j.get("title"),
                "location": (j.get("location") or {}).get("name"),
                "url": j.get("absolute_url"),
            }
            for j in data["jobs"]
        ]
    if ats == "lever":
        if not isinstance(data, list):
            return None
        return [
            {
                "id": str(j.get("id")),
                "title": j.get("text"),
                "location": (j.get("categories") or {}).get("location"),
                "url": j.get("hostedUrl"),
            }
            for j in data
        ]
    return None


# ---- the loop ---------------------------------------------------------------

class Loop:
    def __init__(self, boards, budget, policy, fetch, clock=time.monotonic,
                 sleep=time.sleep, seen=None):
        self.boards = boards
        self.budget = budget
        self.policy = policy
        self.fetch = fetch
        self.clock = clock
        self.sleep = sleep
        self.seen = seen            # {board_name: [job ids]} or None
        self.trace: list[dict] = []
        self.raw: list[dict] = []
        self.results: list[dict] = []
        self.requests = 0
        self.boards_fetched = 0
        self.current = None

    def _t(self) -> float:
        return round(self.clock() - self.start, 3)

    def _log(self, event: str, **fields) -> None:
        self.trace.append({"t": self._t(), "event": event, **fields})

    def _remaining(self) -> float:
        return self.budget["max_seconds"] - (self.clock() - self.start)

    def run(self) -> dict:
        self.start = self.clock()
        self._log("start", boards=len(self.boards), budget=self.budget)
        status, reason = None, None
        done: set[str] = set()
        try:
            for i, board in enumerate(self.boards):
                name, url = board["name"], board["url"]
                key = normalize(url)
                if key in done:
                    self._log("repeat-skipped", board=name, url=url)
                    self.results.append({"board": name, "status": "repeat-skipped",
                                         "reason": "same normalized URL already fetched this run"})
                    continue
                if self._remaining() <= 0:
                    raise BudgetStop(f"time budget of {self.budget['max_seconds']} s used")
                if self.boards_fetched >= self.budget["max_boards"]:
                    raise BudgetStop(f"board budget of {self.budget['max_boards']} used")
                # Check requests before counting the board, so a board that never
                # got a request is "not reached", not "stopped mid-board".
                if self.requests >= self.budget["max_requests"]:
                    raise BudgetStop(f"request budget of {self.budget['max_requests']} used")
                done.add(key)
                self.boards_fetched += 1
                self.results.append(self._visit(board))
            status = self._final_status()
            reason = self._final_reason(status)
        except BudgetStop as e:
            status, reason = BUDGET_EXHAUSTED, str(e)
            self._log("budget-exhausted", reason=reason)
            listed = {r["board"] for r in self.results}
            for b in self.boards:
                if b["name"] not in listed:
                    started = b["name"] == self.current
                    self.results.append({"board": b["name"], "status": "skipped",
                                         "reason": ("stopped mid-board: " if started else "not reached: ") + reason})
                    listed.add(b["name"])
        except PolicyViolation as e:
            status, reason = ERROR, f"policy violation: {e}"
            self._log("policy-violation", kind=e.kind, target=e.target, reason=e.reason)
        except Exception as e:  # crash: report it, never hide it
            status, reason = ERROR, f"crash: {type(e).__name__}: {e}"
            self._log("crash", error=reason)

        self._log("exit", status=status, reason=reason)
        return {
            "exit": status,
            "reason": reason,
            "budget": {
                "limits": {k: self.budget[k] for k in ("max_boards", "max_requests", "max_seconds")},
                "used": {"boards": self.boards_fetched, "requests": self.requests,
                         "seconds": round(self.clock() - self.start, 1)},
            },
            "boards": self.results,
        }

    def _final_status(self) -> str:
        if any(r["status"] in ("flagged", "failed") for r in self.results):
            return INCOMPLETE
        return FINISHED

    def _final_reason(self, status: str) -> str:
        if status == FINISHED:
            return "every board returned at least one job; nothing flagged or failed"
        bad = [f"{r['board']} {r['status']}" for r in self.results
               if r["status"] in ("flagged", "failed")]
        return "; ".join(bad)

    def _visit(self, board: dict) -> dict:
        name, url, ats = board["name"], board["url"], board["ats"]
        self.current = name
        attempt = 0
        while True:
            if self.requests >= self.budget["max_requests"]:
                raise BudgetStop(f"request budget of {self.budget['max_requests']} used")
            remaining = self._remaining()
            if remaining <= 0:
                raise BudgetStop(f"time budget of {self.budget['max_seconds']} s used")
            self.policy.check_request("GET", url)   # PolicyViolation -> exit error
            attempt += 1
            self.requests += 1
            timeout = min(self.budget["request_timeout_seconds"], remaining)
            self._log("request", board=name, url=url, attempt=attempt, request_no=self.requests)
            try:
                resp = self.fetch(url, timeout)
                self.raw.append({"board": name, "url": url, "attempt": attempt,
                                 "status": resp.status, "body": resp.body})
            except TimeoutError:
                resp = None
                self.raw.append({"board": name, "url": url, "attempt": attempt,
                                 "timeout": True})

            retryable = resp is None or 500 <= resp.status <= 599
            what = "timeout" if resp is None else f"HTTP {resp.status}"
            self._log("response", board=name, attempt=attempt, result=what)
            if retryable:
                if attempt == 1:
                    wait = self.budget["retry_wait_seconds"]
                    self._log("retry-wait", board=name, seconds=wait)
                    self.sleep(wait)
                    continue
                return self._failed(name, f"{what} after 1 retry")
            if resp.status == 404:
                return self._failed(name, "HTTP 404 (not retried)")
            if 400 <= resp.status <= 499:
                return self._failed(name, f"HTTP {resp.status} (not retried)")
            if not 200 <= resp.status <= 299:
                return self._failed(name, f"unexpected HTTP {resp.status}")
            try:
                data = json.loads(resp.body)
            except ValueError:
                return self._failed(name, "response was not JSON")
            jobs = extract_jobs(ats, data)
            if jobs is None:
                return self._failed(name, f"JSON did not match the {ats} format")
            if not jobs:
                self._log("flagged", board=name, reason="empty-response")
                return {"board": name, "status": "flagged", "reason": "empty-response: 200 OK with zero jobs"}
            result = {"board": name, "status": "ok", "jobs": len(jobs)}
            if self.seen is not None:
                before = set(self.seen.get(name, []))
                new = [j for j in jobs if j["id"] not in before]
                result["new"] = len(new)
                result["new_titles"] = sorted(j["title"] for j in new)[:10]
                self.seen[name] = sorted(before | {j["id"] for j in jobs})
            self._log("ok", board=name, jobs=len(jobs), new=result.get("new"))
            return result

    def _failed(self, name: str, reason: str) -> dict:
        # GATE.md > Data integrity: a failed board gets no job count.
        self._log("failed", board=name, reason=reason)
        return {"board": name, "status": "failed", "reason": reason}


# ---- fetchers -----------------------------------------------------------------

def live_fetch(url: str, timeout: float) -> Response:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return Response(r.status, r.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return Response(e.code, e.read().decode("utf-8", errors="replace"))
    except (socket.timeout, TimeoutError):
        raise TimeoutError(url)
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise TimeoutError(url)
        raise


def replay_fetch_from(run_dir: Path):
    """Serve recorded responses in the order they were recorded, per URL."""
    queues: dict[str, list[dict]] = {}
    for f in sorted((run_dir / "raw").glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        queues.setdefault(normalize(rec["url"]), []).append(rec)

    def fetch(url: str, timeout: float) -> Response:
        q = queues.get(normalize(url))
        if not q:
            raise RuntimeError(f"replay has no recorded response for {url}")
        rec = q.pop(0)
        if rec.get("timeout"):
            raise TimeoutError(url)
        return Response(rec["status"], rec["body"])

    return fetch


# ---- CLI ----------------------------------------------------------------------

def main(argv=None, root: Path | None = None, loop_cls=None, run_prefix: str = "") -> int:
    ap = argparse.ArgumentParser(prog="python3 -m agent.loop")
    ap.add_argument("--boards", default="boards.json")
    ap.add_argument("--budget", default="budget.json")
    ap.add_argument("--replay", metavar="RUN_DIR", help="re-run from a saved run folder")
    ap.add_argument("--approve", action="store_true", help="allow writes to protected files")
    args = ap.parse_args(argv)

    root = Path(root or Path.cwd()).resolve()
    policy = Policy(root, approve=args.approve)
    boards = json.loads(policy.check_read(args.boards).read_text(encoding="utf-8"))["boards"]
    budget = json.loads(policy.check_read(args.budget).read_text(encoding="utf-8"))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    seen_path = Path("out/seen.json")
    if args.replay:
        src = policy.check_read(args.replay)
        fetch = replay_fetch_from(src)
        before_file = src / "seen-before.json"
        seen = json.loads(before_file.read_text()) if before_file.exists() else {}
        run_id, sleep = f"replay-{stamp}-of-{src.name}", (lambda s: None)
    else:
        fetch = live_fetch
        real_seen = root / seen_path
        seen = json.loads(real_seen.read_text()) if real_seen.exists() else {}
        run_id, sleep = f"run-{stamp}", time.sleep
    seen_before = json.loads(json.dumps(seen))
    run_id = run_prefix + run_id

    loop = (loop_cls or Loop)(boards, budget, policy, fetch, sleep=sleep, seen=seen)
    report = loop.run()
    report = {"run_id": run_id, "mode": "replay" if args.replay else "live", **report}

    out = Path("out") / run_id
    try:
        guarded_write(policy, out / "report.json", json.dumps(report, indent=2) + "\n")
        guarded_write(policy, out / "trace.jsonl",
                      "".join(json.dumps(e) + "\n" for e in loop.trace))
        guarded_write(policy, out / "seen-before.json", json.dumps(seen_before, indent=2) + "\n")
        for n, rec in enumerate(loop.raw, 1):
            guarded_write(policy, out / "raw" / f"{n:02d}-{rec['board']}-a{rec['attempt']}.json",
                          json.dumps(rec, indent=2) + "\n")
        if not args.replay and report["exit"] != ERROR:
            guarded_write(policy, seen_path, json.dumps(seen, indent=2) + "\n")
    except PolicyViolation as e:
        report["exit"], report["reason"] = ERROR, f"policy violation while saving: {e}"

    print(f"{report['run_id']}: {report['exit']} | {report['reason']}")
    for r in report["boards"]:
        extra = f"{r['jobs']} jobs, {r.get('new', '?')} new" if r["status"] == "ok" else r["reason"]
        print(f"  {r['board']:<22} {r['status']:<15} {extra}")
    u = report["budget"]["used"]
    print(f"  used: {u['boards']} boards, {u['requests']} requests, {u['seconds']} s  ->  {out}/")
    return EXIT_CODES[report["exit"]]


if __name__ == "__main__":
    sys.exit(main())
