"""The bounded agent loop from GATE.md: several boards, budgets, a repeat rule, an error policy.

Exits, in order of precedence: error > budget-exhausted > incomplete > finished.
Only `finished` means every configured board succeeded.
"""
import datetime as dt
import json
import re
import time

import adapters
from policy import PolicyViolation
from tools import TransientError

BUDGETS = {"boards": 5, "requests": 10, "seconds": 60}  # GATE.md; tests/test_gate.py keeps these equal
RETRY_DELAY = 2
REQUEST_TIMEOUT = 15
EXIT_CODES = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}


class BudgetExhausted(Exception):
    pass


class Run:
    def __init__(self, tools, budgets=None, clock=time.monotonic, sleep=time.sleep):
        self.tools, self.clock, self.sleep = tools, clock, sleep
        self.budgets = dict(BUDGETS, **(budgets or {}))
        self.start = clock()
        self.trace, self.requests, self.boards_started, self.sent = [], 0, 0, set()

    def observe(self, event, **fields):
        self.trace.append({"t": round(self.clock() - self.start, 3), "event": event, **fields})

    def remaining_seconds(self):
        return self.budgets["seconds"] - (self.clock() - self.start)

    def spend_request(self):
        """Checked before every request: the request budget, then the time budget."""
        if self.requests + 1 > self.budgets["requests"]:
            raise BudgetExhausted(f"requests: {self.requests} of {self.budgets['requests']} used")
        if self.remaining_seconds() <= 0:
            raise BudgetExhausted(f"seconds: {self.budgets['seconds']} s used")
        self.requests += 1

    def start_board(self):
        if self.boards_started + 1 > self.budgets["boards"]:
            raise BudgetExhausted(f"boards: {self.boards_started} of {self.budgets['boards']} used")
        self.boards_started += 1

    def get(self, url, retry=False):
        key = ("GET", url)
        if key in self.sent and not retry:
            return None  # the caller records `repeat refused`
        self.spend_request()
        self.sent.add(key)
        timeout = max(0.1, min(REQUEST_TIMEOUT, self.remaining_seconds()))
        self.observe("request", method="GET", url=url, attempt=2 if retry else 1, timeout=round(timeout, 1))
        return self.tools.http_get(url, timeout=timeout)

    def fetch_board(self, board, raw_dir):
        """Returns (postings, None) or (None, reason). Never returns an invented empty list.
        Where the system can name its own board (Greenhouse), that name must match the configured
        employer before the job list is fetched at all."""
        name = f"{board['system']}_{board['token']}"
        identity = adapters.identity_url(board)
        if identity:
            actual, reason = self.fetch(identity, f"{raw_dir}/{name}_board", adapters.parse_board_name)
            if actual is None:
                return None, reason if reason == "repeat refused" else f"identity check: {reason}"
            if not same_employer(actual, board["employer"]):
                self.observe("identity mismatch", board=board_key(board), board_name=actual, employer=board["employer"])
                return None, (f"identity mismatch: the board calls itself {actual!r}, "
                              f"but the config says {board['employer']!r}")
        return self.fetch(adapters.board_url(board), f"{raw_dir}/{name}", lambda body: adapters.parse(board, body))

    def fetch(self, url, save_as, parse):
        """Error policy: 4xx never retried; timeout, dropped connection, or 5xx retried once after 2 s.
        Returns (parsed, None) or (None, reason)."""
        saved_name = save_as.rsplit("/", 1)[-1]
        for attempt in (1, 2):
            try:
                response = self.get(url, retry=attempt == 2)
            except TransientError as e:
                self.observe("transient", url=url, attempt=attempt, error=str(e))
                reason = f"no response: {e}"
            else:
                if response is None:
                    self.observe("repeat refused", url=url)
                    return None, "repeat refused"
                ext = "json" if response.status == 200 else f"http{response.status}.txt"
                self.tools.write_bytes(f"{save_as}.{ext}", response.body)
                self.observe("response", url=url, status=response.status, bytes=len(response.body),
                             elapsed=round(response.elapsed, 3), saved=f"raw/{saved_name}.{ext}")
                if response.status == 200:
                    try:
                        return parse(response.body), None
                    except adapters.ParseError as e:
                        return None, f"unparseable response: {e}"
                if response.status < 500:
                    return None, f"HTTP {response.status} (not retried: a wrong name won't fix itself)"
                reason = f"HTTP {response.status}"
            if attempt == 1:
                if self.remaining_seconds() <= RETRY_DELAY:
                    raise BudgetExhausted(f"seconds: no time left for a retry of {url}")
                self.observe("retry", url=url, after_seconds=RETRY_DELAY, reason=reason)
                self.sleep(RETRY_DELAY)
        return None, f"{reason} (after one retry)"


def board_key(board):
    return f"{board['system']}/{board['token']}"


def same_employer(a, b):
    """Case and punctuation are ignored. Deliberately not shared with check_identity.py, so the
    independent check has no code in common with the loop it checks."""
    def squash(s):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split())
    return bool(squash(a)) and squash(a) == squash(b)


def load_json(tools, path, missing=None):
    try:
        return json.loads(tools.read_text(path))
    except FileNotFoundError:
        return missing


def run(tools, config_path="config/boards.json", state_path="state/seen.json", label=None,
        budgets=None, clock=time.monotonic, sleep=time.sleep, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%M%SZ") + (f"_{label}" if label else "")
    run_dir = f"runs/{stamp}"
    tools.make_run_dir(run_dir)
    loop = Run(tools, budgets, clock, sleep)
    loop.observe("start", run=stamp, budgets=loop.budgets, config=config_path, state=state_path)
    exit_status, stop_reason, results, new_state = None, None, {}, None
    boards = []
    try:
        config = load_json(tools, config_path)
        if not isinstance(config, dict) or not isinstance(config.get("boards"), list):
            raise ValueError(f"{config_path} has no 'boards' list")
        boards = config["boards"]
        for board in boards:
            adapters.board_url(board)  # validates system and token before anything is sent
        old_state = load_json(tools, state_path, missing={"boards": {}, "board_list": None})
        current_list = [board_key(b) for b in boards]
        tools.policy.check_board_list(old_state.get("board_list"), current_list)
        try:
            for board in boards:
                key = board_key(board)
                loop.start_board()
                postings, reason = loop.fetch_board(board, f"{run_dir}/raw")
                if postings is None:
                    results[key] = {"status": "repeat refused" if reason == "repeat refused" else "failed",
                                    "reason": reason}
                    loop.observe("board failed" if reason != "repeat refused" else "board skipped", board=key,
                                 reason=reason)
                    continue
                before = old_state["boards"].get(key)
                ids = [p["id"] for p in postings]
                if before is None:
                    new, closed = [], []
                else:
                    new = [p for p in postings if p["id"] not in set(before["seen"])]
                    closed = sorted(set(before["present"]) - set(ids))
                results[key] = {"status": "ok", "baseline": before is None, "count": len(postings),
                                "new": new, "closed": closed, "ids": ids}
                loop.observe("board ok", board=key, count=len(postings), baseline=before is None,
                             new=len(new), closed=len(closed))
        except BudgetExhausted as e:
            exit_status, stop_reason = "budget-exhausted", str(e)
            loop.observe("budget exhausted", reason=str(e))
        except KeyboardInterrupt:
            loop.observe("interrupted")
        unvisited = [board_key(b) for b in boards if board_key(b) not in results]
        if exit_status is None:
            failed = [k for k, r in results.items() if r["status"] == "failed"]
            exit_status = "incomplete" if failed or unvisited else "finished"
        new_state = {"board_list": current_list, "updated": stamp, "boards": dict(old_state["boards"])}
        for key, r in results.items():
            if r["status"] != "ok":
                continue  # a failed board's previous state is kept as it was
            before = old_state["boards"].get(key, {"seen": []})
            new_state["boards"][key] = {"seen": sorted(set(before["seen"]) | set(r["ids"])),
                                        "present": sorted(r["ids"]), "last_ok": stamp}
        tools.policy.check_state_update(old_state, new_state)
        tools.write_text(state_path, json.dumps(new_state, indent=2) + "\n", overwrite=True)
    except PolicyViolation as e:
        exit_status, stop_reason = "error", f"policy: {e}"
        loop.observe("refused", reason=str(e))
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        exit_status, stop_reason = "error", f"config or state: {e}"
        loop.observe("error", reason=str(e))
    unvisited = [board_key(b) for b in boards if board_key(b) not in results] if boards else []
    summary = {"run": stamp, "exit": exit_status, "reason": stop_reason, "requests": loop.requests,
               "boards_started": loop.boards_started, "seconds": round(clock() - loop.start, 3),
               "budgets": loop.budgets, "results": results, "unvisited": unvisited,
               "state_written": exit_status != "error", "approvals": tools.policy.decisions}
    loop.observe("exit", status=exit_status, reason=stop_reason)
    tools.write_text(f"{run_dir}/trace.jsonl", "".join(json.dumps(e) + "\n" for e in loop.trace))
    tools.write_text(f"{run_dir}/run.json", json.dumps(summary, indent=2) + "\n")
    tools.write_text(f"{run_dir}/report.md", report(summary))
    return run_dir, summary


def report(s):
    lines = [f"# Run {s['run']}", "", f"**Exit: `{s['exit']}`**" + (f" ({s['reason']})" if s["reason"] else ""), "",
             f"- Requests: {s['requests']} of {s['budgets']['requests']}; boards started: "
             f"{s['boards_started']} of {s['budgets']['boards']}; seconds: {s['seconds']} of {s['budgets']['seconds']}",
             f"- State written: {'yes' if s['state_written'] else 'no'}", ""]
    if s["results"] or s["unvisited"]:
        lines += ["| Board | Result | Postings | New | Closed |", "|---|---|---|---|---|"]
        for key, r in s["results"].items():
            if r["status"] == "ok":
                note = "ok (baseline: nothing reported as new)" if r["baseline"] else "ok"
                lines.append(f"| {key} | {note} | {r['count']} | {len(r['new'])} | {len(r['closed'])} |")
            else:
                lines.append(f"| {key} | {r['status']}: {r['reason']} | none | none | none |")
        for key in s["unvisited"]:
            lines.append(f"| {key} | not visited | none | none | none |")
        lines.append("")
    for key, r in s["results"].items():
        if r["status"] == "ok" and (r["new"] or r["closed"]):
            lines.append(f"## {key}")
            lines += [f"- new: {p['title']} ({p['location']}) {p['url']}" for p in r["new"]]
            lines += [f"- closed: id {i}" for i in r["closed"]]
            lines.append("")
    return "\n".join(lines) + "\n"
