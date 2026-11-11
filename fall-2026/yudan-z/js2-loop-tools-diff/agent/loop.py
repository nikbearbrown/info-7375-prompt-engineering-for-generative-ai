"""GATE §2-§5: the bounded loop. Walks the board list once, ends with exactly one exit status."""
import json
import os
import time

from agent import ats, rule
from agent.policy import Refused
from agent.tools import FetchFailed, Tools, http_get

EXIT_CODES = {"finished": 0, "error": 2, "incomplete": 3, "budget-exhausted": 4}
LIMITS = {"max_boards": 6, "max_requests": 12, "max_seconds": 120}     # GATE §3, changed only by a dated revision


class BudgetExhausted(Exception):
    pass


class Budget:
    def __init__(self, clock=time.monotonic, **limits):
        for k, v in limits.items():
            if k not in LIMITS:
                raise ValueError(f"unknown budget {k}")
            if v > LIMITS[k]:
                raise ValueError(f"{k}={v} is above GATE's {LIMITS[k]}: a budget may be lowered, never raised")
        self.lim = dict(LIMITS, **limits)
        self.clock, self.start = clock, clock()
        self.boards = self.requests = 0
        self._now = self.start

    def elapsed(self):
        return self._now - self.start

    def _tick(self):
        self._now = self.clock()
        if self.elapsed() > self.lim["max_seconds"]:
            raise BudgetExhausted(f"seconds: {self.elapsed():.1f} > {self.lim['max_seconds']}")

    def take_board(self):
        self._tick()
        if self.boards + 1 > self.lim["max_boards"]:
            raise BudgetExhausted(f"boards: next would be {self.boards + 1} > {self.lim['max_boards']}")
        self.boards += 1

    def take_request(self):
        self._tick()
        if self.requests + 1 > self.lim["max_requests"]:
            raise BudgetExhausted(f"requests: next would be {self.requests + 1} > {self.lim['max_requests']}")
        self.requests += 1


def _fetch_with_policy(tools, url):
    """GATE §5: one retry for a transient failure, none for 404/4xx."""
    try:
        return tools.fetch(url)
    except FetchFailed as e:
        if not e.transient:
            raise
        return tools.fetch(url, retry=True)


def run(boards, workdir, policy, fetcher=http_get, clock=time.monotonic, stamp=None, resume=None,
        on_board=None, **limits):
    stamp = stamp or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    base, n = stamp, 1           # two runs in the same second get distinct names; evidence is never overwritten
    while os.path.exists(os.path.join(workdir, f"trace-{stamp}.jsonl")):
        n += 1
        stamp = f"{base}-{n}"
    trace, results = [], []
    budget = Budget(clock=clock, **limits)
    tools = Tools(policy, budget, trace, fetcher=fetcher)
    exit_status, stop_reason, not_reached = None, None, []
    seen_boards = set()

    for i, (system, board) in enumerate(boards):
        if (system, board) in seen_boards:          # GATE §4: listed twice -> fetched once
            trace.append({"t": round(budget.elapsed(), 3), "tool": "fetch", "target": f"{system}/{board}",
                          "outcome": "repeat-refused", "reason": "board listed twice"})
            continue
        seen_boards.add((system, board))
        entry = {"system": system, "board": board}
        try:
            budget.take_board()
            url = ats.url(system, board)
            raw = _fetch_with_policy(tools, url)
            postings = ats.parse(system, raw)
            ev = os.path.join(workdir, "evidence", f"{stamp}-{system}-{board}.json")
            tools.write_new(ev, raw)
            state_path = os.path.join(workdir, "state", f"{system}-{board}.json")
            baseline = not os.path.exists(state_path)
            seen = set() if baseline else set(json.loads(tools.read_bytes(state_path))["seen_ids"])
            new, reported = [], set()
            for p in postings:
                if not baseline and p["id"] not in seen and p["id"] not in reported:
                    new.append(p)
                    reported.add(p["id"])
            seen.update(p["id"] for p in postings)
            tools.write_state(state_path, json.dumps(
                {"system": system, "board": board, "last_run": stamp, "seen_ids": sorted(seen, key=str)},
                indent=1).encode())
            entry.update(status="ok", baseline=baseline, postings=len(postings), new=len(new),
                         evidence=os.path.relpath(ev, workdir).replace(os.sep, "/"),
                         new_postings=[{"id": p["id"], "title": p["title"], "location": p["location"].get("name", ""),
                                        "url": p["absolute_url"],
                                        **({"rule": rule.judge(p, resume)} if resume else {})} for p in new])
        except BudgetExhausted as e:
            exit_status, stop_reason = "budget-exhausted", str(e)
            entry.update(status="not-reached")
            not_reached = [b for _, b in boards[i:]]
            trace.append({"t": round(budget.elapsed(), 3), "tool": "loop", "target": board,
                          "outcome": "budget-exhausted", "reason": str(e)})
            break
        except FetchFailed as e:                     # W1/W5: no count, no "0 new", state untouched
            entry.update(status="failed", error=str(e), attempts=sum(
                1 for o in trace if o["tool"] == "fetch" and o["target"] == e.url and o["outcome"] != "repeat-refused"))
        except (Refused, ats.BadShape, ValueError, KeyError) as e:
            exit_status, stop_reason = "error", f"{type(e).__name__}: {e}"
            entry.update(status="error", error=str(e))
            results.append(entry)
            not_reached = [b for _, b in boards[i + 1:]]
            trace.append({"t": round(budget.elapsed(), 3), "tool": "loop", "target": board,
                          "outcome": "error", "reason": stop_reason})
            break
        results.append(entry)
        if on_board:
            on_board(entry)

    if exit_status is None:
        exit_status = "incomplete" if any(r["status"] == "failed" for r in results) else "finished"
    res = {"run": stamp, "exit": exit_status, "exit_code": EXIT_CODES[exit_status], "stop_reason": stop_reason,
           "budget": {"limits": budget.lim, "boards": budget.boards, "requests": budget.requests,
                      "seconds": round(budget.elapsed(), 3)},
           "boards": results, "not_reached": not_reached, "trace": trace}
    trace_path = os.path.join(workdir, f"trace-{stamp}.jsonl")
    try:
        tools.write_new(trace_path, "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in trace).encode())
        res["trace_path"] = trace_path
    except Refused as e:
        res["trace_path"] = None
        res["stop_reason"] = (stop_reason or "") + f" | trace not saved: {e}"
    return res
