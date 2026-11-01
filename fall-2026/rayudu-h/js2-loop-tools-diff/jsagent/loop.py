"""The bounded loop from GATE.md: several boards, budgets, a repeat rule, an error policy,
one exit status, and a trace of every observation.

Exits: finished | incomplete | budget-exhausted | error.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import claude_judge, net, rule
from .policy import Policy, Refused
from .providers import SYSTEMS, BadResponse

FINISHED, INCOMPLETE, BUDGET, ERROR = "finished", "incomplete", "budget-exhausted", "error"


@dataclass
class Budgets:
    max_boards: int = 6
    max_requests: int = 10
    max_seconds: float = 120.0
    request_timeout: float = 30.0
    max_claude: int = 25
    retry_delay: float = 2.0


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


class Trace:
    """Append-only record of every observation (runs/<id>/trace.jsonl)."""

    def __init__(self, policy: Policy, path: Path):
        self.path = policy.check_write(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.events = []

    def log(self, event: str, **detail):
        rec = {"t": now(), "event": event, **detail}
        self.events.append(rec)
        with open(self.path, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec


def load_state(policy: Policy, path: Path) -> dict:
    real = policy.check_read(path)
    if not real.exists():
        return {"boards": {}}
    data = json.loads(real.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("boards"), dict):
        raise ValueError(f"state file {path} has an unexpected shape")
    return data


def save_state(policy: Policy, path: Path, state: dict) -> None:
    real = policy.check_write(path)
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def run(boards: list, resume: dict, policy: Policy, state_path: Path, run_dir: Path,
        budgets: Budgets = Budgets(), use_claude: bool = True, prompt: str = "v2",
        fetch=net.fetch, judge_claude=claude_judge.judge, clock=time.monotonic, sleep=time.sleep) -> dict:
    trace = Trace(policy, run_dir / "trace.jsonl")
    started = clock()
    trace.log("run-start", boards=[f"{b['system']}:{b['board']}" for b in boards], budgets=budgets.__dict__)
    try:
        state = load_state(policy, state_path)
    except (Refused, ValueError, json.JSONDecodeError) as e:
        trace.log("exit", status=ERROR, reason=f"state unreadable: {e}")
        return {"status": ERROR, "reason": str(e), "boards": [], "trace": trace.events}

    results, requests_sent, sent = [], 0, set()
    claude_left = budgets.max_claude
    status = None

    for i, b in enumerate(boards):
        label = f"{b['system']}:{b['board']}"
        if i >= budgets.max_boards:
            status = BUDGET
            trace.log("budget-exhausted", budget="boards", at=label, untried=[f"{x['system']}:{x['board']}" for x in boards[i:]])
            break
        if clock() - started > budgets.max_seconds:
            status = BUDGET
            trace.log("budget-exhausted", budget="seconds", at=label, untried=[f"{x['system']}:{x['board']}" for x in boards[i:]])
            break
        res = {"board": label, "seeded": bool(b.get("from_file")), "status": None, "new": []}
        results.append(res)
        provider = SYSTEMS.get(b["system"])
        if provider is None:
            res.update(status="failed", reason=f"unknown system {b['system']!r}")
            trace.log("board-failed", board=label, reason=res["reason"])
            continue

        # ---- get the raw response: a live GET under the policy, or a saved (SEEDED) file ----
        raw = None
        if b.get("from_file"):
            try:
                raw = policy.check_read(b["from_file"]).read_bytes()
                if b["from_file"].endswith(".gz"):
                    raw = gzip.decompress(raw)
                trace.log("read-seeded", board=label, file=b["from_file"], bytes=len(raw))
            except (Refused, OSError) as e:
                res.update(status="failed", reason=f"seeded file: {e}")
                trace.log("board-failed", board=label, reason=res["reason"])
                continue
        else:
            try:
                url = provider.url(b["board"])
            except BadResponse as e:
                res.update(status="failed", reason=str(e))
                trace.log("board-failed", board=label, reason=str(e))
                continue
            if ("GET", url) in sent:                       # repeat rule
                res.update(status="failed", reason="repeat: same GET already made this run (not sent)")
                trace.log("refused-repeat", board=label, url=url)
                continue
            sent.add(("GET", url))
            timeout = b.get("timeout", budgets.request_timeout)
            for attempt in (1, 2):                         # error policy: at most one retry
                if requests_sent >= budgets.max_requests:
                    status = BUDGET
                    trace.log("budget-exhausted", budget="requests", at=label)
                    break
                requests_sent += 1
                trace.log("request", board=label, url=url, attempt=attempt, timeout=timeout)
                try:
                    raw = fetch(policy, url, timeout)
                    trace.log("response", board=label, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                    break
                except Refused as e:
                    res.update(status="failed", reason=f"refused: {e}")
                    trace.log("refused", board=label, reason=str(e))
                    break
                except net.Permanent as e:
                    res.update(status="failed", reason=f"{e} (permanent; not retried)")
                    trace.log("board-failed", board=label, reason=res["reason"], attempt=attempt)
                    break
                except net.Transient as e:
                    if attempt == 1:
                        trace.log("retry", board=label, reason=str(e), after_seconds=budgets.retry_delay)
                        sleep(budgets.retry_delay)
                        continue
                    res.update(status="failed", reason=f"{e} (transient; retried once)")
                    trace.log("board-failed", board=label, reason=res["reason"], attempt=attempt)
            if status == BUDGET:
                res.update(status="failed", reason="request budget used up")
                break
            if raw is None:
                continue

        # ---- evidence, parse, new-since-last ----------------------------------------------
        raw_path = policy.check_write(run_dir / "raw" / f"{b['system']}-{b['board']}.json.gz")
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(raw_path, "xb") as f:
            f.write(raw)
        res["raw"] = {"file": str(raw_path.relative_to(policy.root)), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        try:
            postings = provider.parse(b["board"], raw)
        except BadResponse as e:
            res.update(status="failed", reason=f"{e} (raw saved)")
            trace.log("board-failed", board=label, reason=res["reason"])
            continue

        keys = [p["key"] for p in postings]
        dupes = len(keys) - len(set(keys))
        if dupes:
            trace.log("duplicate-ids", board=label, count=dupes)
        board_state = state["boards"].get(label)
        last_good = (board_state or {}).get("last_good_count")
        if not postings and last_good:
            # GATE.md error policy: a board that suddenly returns nothing is more likely a broken
            # fetch than an empty board. No "0 new", no state update; the run is incomplete.
            res.update(status="unverified",
                       reason=f"empty response; the last good run had {last_good} postings (raw saved, state kept)")
            trace.log("board-unverified", board=label, postings=0, last_good_count=last_good)
            continue
        if board_state is None:
            new = []                                       # baseline: none reported as new
        else:
            seen = set(board_state["seen"])
            new, added = [], set()
            for p in postings:
                if p["key"] not in seen and p["key"] not in added:
                    new.append(p)
                    added.add(p["key"])
        res.update(status="ok", postings=len(postings), baseline=board_state is None,
                   last_good_count=None if board_state is None else board_state.get("last_good_count"))
        trace.log("board-ok", board=label, postings=len(postings), baseline=board_state is None, new=len(new))

        for p in new:
            row = {"record": rule.judge(p, resume)}
            if not use_claude:
                row["judgment"] = {"valid": False, "errors": ["Claude judge not requested (--no-claude)"]}
            elif claude_left <= 0:
                row["judgment"] = {"valid": False, "errors": ["Claude budget used up"]}
            else:
                claude_left -= 1
                row["judgment"] = judge_claude(p, resume, version=prompt)
                trace.log("claude-call", board=label, key=p["key"], valid=row["judgment"].get("valid"))
            res["new"].append(row)

        state["boards"][label] = {"seen": sorted(set(keys) | set((board_state or {}).get("seen", []))),
                                  "last_good_count": len(postings), "last_run": run_dir.name}

    if status is None:
        status = FINISHED if results and all(r["status"] == "ok" for r in results) else INCOMPLETE
    try:
        save_state(policy, state_path, state)
    except Refused as e:
        trace.log("exit", status=ERROR, reason=f"state write refused: {e}")
        return {"status": ERROR, "reason": str(e), "boards": results, "trace": trace.events}
    trace.log("exit", status=status, requests_sent=requests_sent, seconds=round(clock() - started, 2))
    return {"status": status, "boards": results, "requests_sent": requests_sent, "trace": trace.events}
