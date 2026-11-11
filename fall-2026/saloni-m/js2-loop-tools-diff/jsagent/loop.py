"""The bounded loop (GATE.md sections 1-4 and 8).

One pass over the planned boards. Every observation goes into the trace. The run ends with
exactly one status: finished | incomplete | budget-exhausted | error (most serious wins).

Method hooks (classify, exit_status, job_key) exist so the wrong versions in
tests/wrong_versions.py can each change exactly one behaviour.
"""
import copy
import datetime as dt
import gzip
import hashlib
import json
import os
import time
import urllib.parse

from jsagent.policy import ALLOW, NEEDS_APPROVAL, PolicyError
from jsagent.providers import PROVIDERS, BadData

SEVERITY = ["finished", "incomplete", "budget-exhausted", "error"]


def empty_state():
    return {"schema": 1, "boards": {}, "seen": [], "runs": []}


class Loop:
    def __init__(self, cfg, policy, fetch, out_dir, run_id, label="live",
                 clock=time.monotonic, expected_empty=()):
        self.cfg = cfg
        self.b = cfg["budgets"]
        self.policy = policy
        self.fetch = fetch
        self.out_dir = out_dir
        self.run_id = run_id
        self.label = label
        self.clock = clock
        self.expected_empty = set(expected_empty)
        self.run_dir = os.path.join(out_dir, "runs", run_id)
        self.trace = []

    # -- hooks ---------------------------------------------------------------------------
    def job_key(self, system, board, job_id):
        """The identity of a job in saved state. (JS1 stored the bare posting id.)"""
        return job_id

    def classify(self, board, result):
        """-> ("ok", jobs) | ("suspicious_empty", []) | ("failed", reason, retryable)"""
        if result.error == "timeout":
            return ("failed", "timeout", True)
        if result.error:
            return ("failed", result.error, False)
        if 500 <= result.status <= 599:
            return ("failed", f"HTTP {result.status}", True)
        if result.status != 200:
            return ("failed", f"HTTP {result.status}", False)
        try:
            jobs = PROVIDERS[board["system"]].parse(result.body)
        except BadData as e:
            return ("failed", f"bad data: {e}", False)
        if not jobs and f"{board['system']}:{board['board']}" not in self.expected_empty:
            return ("suspicious_empty", [])
        return ("ok", jobs)

    def exit_status(self, flags, boards):
        if any(b["result"] in ("failed", "suspicious_empty") for b in boards):
            flags.add("incomplete")
        return max(flags | {"finished"}, key=SEVERITY.index)

    # -- helpers -------------------------------------------------------------------------
    def log(self, event, **kw):
        rec = {"t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"), "event": event, **kw}
        self.trace.append(rec)
        return rec

    def save_raw(self, board, attempt, result):
        body = result.body or b""
        name = f"{board['system']}-{board['board']}-a{attempt}.json.gz"
        path = os.path.join(self.run_dir, "raw", name)
        self.policy.write_bytes(path, gzip.compress(body, mtime=0))
        return os.path.relpath(path, self.out_dir), hashlib.sha256(body).hexdigest(), len(body)

    # -- the loop ------------------------------------------------------------------------
    def run(self, state):
        t0 = self.clock()
        used = 0
        flags = set()
        done = set()
        boards = []
        stop = None
        plan = list(self.cfg["boards"])
        self.log("start", run_id=self.run_id, label=self.label, budgets=self.b,
                 planned=[f"{p['system']}:{p['board']}" for p in plan])
        if len(plan) > self.b["max_boards"]:
            flags.add("budget-exhausted")
            self.log("budget_stop", reason=f"{len(plan)} boards planned > max_boards {self.b['max_boards']}",
                     never_tried=[f"{p['system']}:{p['board']}" for p in plan[self.b["max_boards"]:]])
            for p in plan[self.b["max_boards"]:]:
                boards.append(self._board(p, None, "not_tried", "max_boards budget"))
            plan = plan[: self.b["max_boards"]]
        seen = set(state["seen"])

        for p in plan:
            if stop:
                boards.append(self._board(p, None, "not_tried", stop))
                continue
            url = PROVIDERS[p["system"]].url(p["board"])
            parts = urllib.parse.urlsplit(url)
            action = ("GET", parts.hostname, parts.path)
            if action in done:
                self.log("repeat_skipped", board=f"{p['system']}:{p['board']}", action=list(action))
                boards.append(self._board(p, url, "repeat_skipped", "same method+host+path already done this run"))
                continue
            done.add(action)
            d = self.policy.check_request("GET", url)
            if d.outcome != ALLOW:
                self.log("policy_refused", url=url, reason=d.reason)
                flags.add("error")
                stop = "policy refused a request"
                boards.append(self._board(p, url, "refused", d.reason))
                continue

            attempt, outcome = 0, None
            while True:
                if used >= self.b["max_requests"]:
                    stop = f"max_requests {self.b['max_requests']} reached"
                elif self.clock() - t0 >= self.b["max_seconds"]:
                    stop = f"max_seconds {self.b['max_seconds']} reached"
                if stop:
                    flags.add("budget-exhausted")
                    self.log("budget_stop", reason=stop, board=f"{p['system']}:{p['board']}")
                    break
                attempt += 1
                used += 1
                self.log("request", n=used, attempt=attempt, method="GET", url=url)
                r0 = self.clock()
                try:
                    res = self.fetch(url, self.b["request_timeout_seconds"])
                except PolicyError as e:
                    self.log("policy_refused", url=url, reason=e.decision.reason)
                    flags.add("error")
                    stop = "policy refused a redirect"
                    outcome = ("failed", e.decision.reason, False)
                    break
                raw, sha, nbytes = self.save_raw(p, attempt, res)
                outcome = self.classify(p, res)
                self.log("response", url=url, attempt=attempt, status=res.status, error=res.error,
                         bytes=nbytes, sha256=sha, raw=raw, seconds=round(self.clock() - r0, 3),
                         outcome=outcome[0], reason=(outcome[1] if outcome[0] == "failed" else None))
                if outcome[0] == "failed" and outcome[2] and attempt == 1:
                    self.log("retry", url=url, reason=outcome[1], why="timeout/5xx: one retry, a GET changes nothing")
                    continue
                break

            if outcome is None:
                boards.append(self._board(p, url, "not_tried", stop, attempts=attempt))
            elif outcome[0] == "ok":
                boards.append(self._ok(p, url, outcome[1], state, seen, attempt))
            else:
                reason = outcome[1] if outcome[0] == "failed" else "valid response with zero jobs"
                boards.append(self._board(p, url, outcome[0], reason, attempts=attempt))
            self.log("board_result", **{k: v for k, v in boards[-1].items() if k not in ("new", "_keys")})

        status = self.exit_status(flags, boards)
        report = {
            "run_id": self.run_id, "label": self.label, "status": status,
            "requests_used": used, "seconds": round(self.clock() - t0, 3), "budgets": self.b,
            "total_new": sum(len(b["new"]) for b in boards if b.get("new") is not None),
            "boards": [{k: v for k, v in b.items() if k != "_keys"} for b in boards],
        }
        self.log("exit", status=status, requests_used=used, total_new=report["total_new"])
        new_state = None if status == "error" else self.next_state(state, boards, status)
        return report, new_state

    def _board(self, p, url, result, reason, attempts=0):
        return {"system": p["system"], "board": p["board"], "url": url, "result": result, "reason": reason,
                "attempts": attempts, "count_seen": None, "count_new": None, "baseline": None, "new": None}

    def _ok(self, p, url, jobs, state, seen, attempts):
        bkey = f"{p['system']}:{p['board']}"
        keyed = {}
        for j in jobs:
            keyed.setdefault(self.job_key(p["system"], p["board"], j["id"]), j)
        baseline = bkey not in state["boards"]
        new = [] if baseline else [
            {"key": k, "id": j["id"], "title": j["title"]} for k, j in keyed.items() if k not in seen]
        b = self._board(p, url, "ok", "baseline: recorded, nothing reported new" if baseline else "compared with saved state",
                        attempts)
        b.update(count_seen=len(keyed), count_new=len(new), baseline=baseline, new=new, _keys=sorted(keyed))
        return b

    def next_state(self, state, boards, status):
        s = copy.deepcopy(state)
        seen = set(s["seen"])
        for b in boards:
            if b["result"] != "ok":
                continue  # failed or suspicious boards never add or remove history
            seen.update(b["_keys"])
            entry = s["boards"].setdefault(f"{b['system']}:{b['board']}", {"first_run": self.run_id})
            entry.update(last_ok_run=self.run_id, count=b["count_seen"])
        s["seen"] = sorted(seen)
        s["runs"].append({"run_id": self.run_id, "label": self.label, "status": status})
        return s


def write_run(loop, report, new_state, state_path, approve_state=False):
    """Write trace, report and state through the policy. Returns where the state went."""
    pol = loop.policy
    where = None
    if new_state is not None:
        data = json.dumps(new_state, indent=1).encode()
        d = pol.check_write(state_path, approved=approve_state)
        if d.outcome == ALLOW:
            pol.write_bytes(state_path, data, approved=approve_state)
            where = {"state": os.path.relpath(state_path, loop.out_dir), "approved": approve_state}
        elif d.outcome == NEEDS_APPROVAL:
            pending = state_path.replace(".json", ".pending.json")
            pol.write_bytes(pending, data)
            where = {"state": os.path.relpath(pending, loop.out_dir), "approved": False,
                     "note": "saved history NOT overwritten: rerun with --approve-state to apply"}
            loop.log("state_pending", reason=d.reason, pending=where["state"])
        else:
            raise PolicyError(d)
    else:
        loop.log("state_not_written", reason="run ended in error")
    report["state_written"] = where
    pol.write_bytes(os.path.join(loop.run_dir, "report.json"), json.dumps(report, indent=1).encode())
    pol.write_bytes(os.path.join(loop.run_dir, "trace.jsonl"),
                    "".join(json.dumps(r) + "\n" for r in loop.trace).encode())
    return where
