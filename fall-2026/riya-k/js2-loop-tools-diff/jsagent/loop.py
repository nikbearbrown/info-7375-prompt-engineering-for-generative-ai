"""The bounded loop from GATE.md: several boards, a budget, a repeat rule, an error policy, one exit status.

    python3 -m jsagent.loop run   --config boards.json --out runs [--fixtures DIR --label seeded] [--no-empty-guard]
    python3 -m jsagent.loop reset --out runs --board greenhouse:databricks [--approve]

Every observation (request, response, retry, refusal, budget check) goes into the trace. A failed board is
recorded with postings = null and a reason; it is never turned into "0 postings" or "no new jobs".
"""

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import ats, rules
from .contract import validate_resume, validate_verdict
from .policy import Policy, PolicyError

ROOT = Path(__file__).resolve().parent.parent

# GATE.md "Budgets". Constants on purpose: no flag or config key can change them. Only a dated GATE.md amendment can.
MAX_BOARDS = 6
MAX_REQUESTS = 10
MAX_SECONDS = 60.0
RETRY_WAIT = 2.0
RETRIES_ALLOWED = 1
REQUEST_TIMEOUT = 20.0

EXITS = ("finished", "incomplete", "budget_exhausted", "error")
EXIT_CODES = {"finished": 0, "incomplete": 3, "budget_exhausted": 4, "error": 5}
CONFIG_KEYS = {"boards", "cross_check", "persona", "_comment"}


def rel(path):
    """Paths in reports are relative to the JS2 folder, so committed reports carry no home-directory paths."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


class Transient(Exception):
    """Timeout or connection failure: the error policy may retry it once."""


class BudgetExhausted(Exception):
    pass


def live_get(url, timeout):
    """One real HTTPS GET. Returns (status, body). Transport problems raise Transient."""
    req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-js2-student-watch/1.0 (read-only)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
        raise Transient(f"{type(e).__name__}: {getattr(e, 'reason', e)}") from None


class Session:
    """Owns the budget, the repeat rule and the trace for one run."""

    def __init__(self, policy, get, clock=time.monotonic, sleep=time.sleep):
        self.policy, self.get, self.clock, self.sleep = policy, get, clock, sleep
        self.trace = policy.log  # policy decisions and loop events share one ordered trace
        self.t0 = clock()
        self.requests = 0
        self.sent = {}  # (method, url) -> times sent; the repeat rule

    def elapsed(self):
        return round(self.clock() - self.t0, 3)

    def event(self, kind, **fields):
        self.trace.append({"t": self.elapsed(), "kind": kind, **fields})

    def ensure_budget(self, extra_seconds=0.0):
        if self.requests >= MAX_REQUESTS:
            raise BudgetExhausted(f"request budget used: {self.requests}/{MAX_REQUESTS}")
        if self.elapsed() + extra_seconds >= MAX_SECONDS:
            raise BudgetExhausted(f"time budget: {self.elapsed()}s used (+{extra_seconds}s needed) of {MAX_SECONDS}s")

    def request(self, url, retry=False):
        """GET url once. A repeat is allowed only as the single retry the error policy permits."""
        action = ("GET", url)
        n = self.sent.get(action, 0)
        if n and not (retry and n <= RETRIES_ALLOWED):
            self.event("repeat_blocked", url=url, times_sent=n)
            raise PolicyError(f"repeat blocked: GET {url} already sent {n} time(s)")
        self.policy.check_request("GET", url)  # before any connection
        self.ensure_budget()
        self.requests += 1
        self.sent[action] = n + 1
        self.event("request", url=url, n=self.requests, attempt=n + 1)
        timeout = max(0.1, min(REQUEST_TIMEOUT, MAX_SECONDS - self.elapsed()))
        try:
            status, body = self.get(url, timeout)
        except Transient as e:
            self.event("response", url=url, error=str(e))
            raise
        self.event("response", url=url, status=status, bytes=len(body))
        return status, body


def read_board(s, system, board, out, stamp, label, empty_guard=True):
    """Apply the GATE.md error policy to one board. Returns a board result; never invents a count."""
    url_fn, parse = ats.SYSTEMS[system]
    url = url_fn(board)
    res = {"board": f"{system}:{board}", "system": system, "url": url, "attempts": 0, "http_status": None,
           "postings": None, "status": None, "reason": None, "raw_responses": []}
    status = body = None
    for attempt in (1, 2):
        if attempt == 2:
            s.ensure_budget(extra_seconds=RETRY_WAIT)
            s.event("retry_wait", board=res["board"], seconds=RETRY_WAIT)
            s.sleep(RETRY_WAIT)
        res["attempts"] = attempt
        try:
            status, body = s.request(url, retry=attempt == 2)
        except Transient as e:
            res["reason"] = f"transient: {e}"
            if attempt == 1:
                continue  # GATE.md: timeouts and connection errors get one retry
            break
        res["http_status"] = status
        raw_path = out / "raw" / f"{system}-{board.replace(' ', '_')}-{stamp}-{label}-a{attempt}.json"
        s.policy.write_bytes(raw_path, body)
        res["raw_responses"].append(rel(raw_path))
        if 500 <= status < 600 and attempt == 1:
            res["reason"] = f"HTTP {status}"
            continue  # GATE.md: 5xx gets one retry
        break
    if status is None:
        res["status"] = "failed"
        return res, []
    if status != 200:
        res.update(status="failed", reason=f"HTTP {status}" + (" (4xx: not retried)" if 400 <= status < 500 else
                                                                 " after retry"))
        return res, []
    try:
        postings = parse(body, board)
    except ats.ParseError as e:
        res.update(status="failed", reason=f"bad body: {e}")
        return res, []
    res["postings"] = len(postings)
    if not postings and empty_guard:
        res.update(status="suspect_empty", reason="HTTP 200 with 0 postings: wrong slug or wrong system? escalated")
        return res, []
    res.update(status="ok", reason=None)
    return res, postings


def state_path(out, key):
    return out / "state" / (key.replace(":", "-").replace(" ", "_") + ".json")


def load_state(policy, path):
    if not path.exists():
        return None
    return json.loads(policy.read_bytes(path))


def load_config(policy, path):
    cfg = json.loads(policy.read_bytes(path))
    extra = set(cfg) - CONFIG_KEYS
    if extra:
        raise ValueError(f"unknown config key(s) {sorted(extra)}: budgets live in GATE.md, not in config")
    for b in cfg["boards"]:
        if b.get("system") not in ats.SYSTEMS or not b.get("board"):
            raise ValueError(f"bad board entry {b}: system must be one of {sorted(ats.SYSTEMS)}")
    return cfg


def run(config, out_dir, fixtures=None, label="live", empty_guard=True, approve=False,
        get=None, clock=time.monotonic, sleep=time.sleep, now=None, extra_read_roots=()):
    out = Path(out_dir)
    read_roots = [ROOT] + ([Path(fixtures)] if fixtures else []) + [Path(r) for r in extra_read_roots]
    policy = Policy(out, read_roots, approve=approve)
    s = Session(policy, get or live_get, clock, sleep)
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{stamp}-{label}"
    s.event("run_start", run_id=run_id, label=label, empty_guard=empty_guard,
            budget={"boards": MAX_BOARDS, "requests": MAX_REQUESTS, "seconds": MAX_SECONDS})
    results, never_ran, skipped, stop = [], [], [], None
    exit_status, current, boards = None, None, []
    try:
        cfg = load_config(policy, Path(config))
        resume = validate_resume(json.loads(policy.read_bytes(ROOT / cfg.get("persona", "persona/arya-sahni.json"))))
        if fixtures:
            s.get = fixture_get(policy, Path(fixtures), cfg)
        boards, seen_keys = [], set()
        for b in cfg["boards"]:
            key = f"{b['system']}:{b['board']}"
            if key in seen_keys:
                skipped.append(key)
                s.event("duplicate_skipped", board=key)
                continue
            seen_keys.add(key)
            boards.append(b)
        for i, b in enumerate(boards):
            key = f"{b['system']}:{b['board']}"
            if i >= MAX_BOARDS:
                raise BudgetExhausted(f"board budget: {MAX_BOARDS} boards")
            s.ensure_budget()
            current = key
            res, postings = read_board(s, b["system"], b["board"], out, stamp, label, empty_guard)
            if res["status"] == "ok":
                res.update(compare_and_judge(policy, out, key, postings, resume, run_id))
            s.event("board_result", **{k: v for k, v in res.items() if k != "new_postings"})
            results.append(res)
            current = None
    except BudgetExhausted as e:
        stop = str(e)
        done = {r["board"] for r in results}
        never_ran = [f"{b['system']}:{b['board']}" for b in boards if f"{b['system']}:{b['board']}" not in done]
        s.event("budget_exhausted", reason=stop, never_ran=never_ran, interrupted=current)
        exit_status = "budget_exhausted"
    except (PolicyError, ValueError, KeyError, OSError) as e:
        stop = f"{type(e).__name__}: {e}"
        s.event("error", reason=stop)
        exit_status = "error"
    if exit_status is None:
        bad = [r for r in results if r["status"] != "ok"]
        exit_status = "incomplete" if bad else "finished"
        stop = (f"{len(bad)} board(s) failed or flagged; escalated to Riya" if bad else "all boards read")
    escalations = [{"board": r["board"], "status": r["status"], "reason": r["reason"]}
                   for r in results if r["status"] != "ok"]
    report = {
        "run_id": run_id, "label": label, "run_at": now.isoformat(timespec="seconds"),
        "exit": exit_status, "stop_reason": stop, "empty_guard": empty_guard,
        "budget_used": {"boards": len(results), "requests": s.requests, "seconds": s.elapsed(),
                        "limits": {"boards": MAX_BOARDS, "requests": MAX_REQUESTS, "seconds": MAX_SECONDS}},
        "boards": results, "never_ran": never_ran, "interrupted_by_budget": current if exit_status == "budget_exhausted" else None, "duplicates_skipped": skipped, "escalations": escalations,
    }
    s.event("run_end", exit=exit_status, reason=stop)
    write_outputs(policy, out, run_id, report, s.trace)
    return report


def compare_and_judge(policy, out, key, postings, resume, run_id):
    """New = ids not in this board's state. First run on a board is a baseline. State only ever grows here."""
    path = state_path(out, key)
    state = load_state(policy, path)
    ids = [p["id"] for p in postings]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{key}: duplicate posting ids in one response")
    baseline = state is None
    old = [] if baseline else state["seen_ids"]
    seen = set(old)
    fresh = [] if baseline else [p for p in postings if p["id"] not in seen]
    verdicts = []
    for p in fresh:
        v = rules.judge(p, resume)
        validate_verdict(v, p["id"])
        verdicts.append(v)
    new_state = state or {"board": key, "seen_ids": [], "runs": []}
    new_state["seen_ids"] = sorted(seen | set(ids))
    new_state["runs"] = new_state.get("runs", []) + [{"run_id": run_id, "postings": len(ids),
                                                      "new": None if baseline else len(fresh)}]
    policy.write_state(path, old, new_state)
    return {"baseline": baseline, "new": None if baseline else len(fresh),
            "removed_since_last": len(seen - set(ids)), "new_postings": verdicts}


def fixture_get(policy, folder, cfg):
    """Seeded mode: answer each board URL from a saved response file. Still goes through the policy and budget."""
    files = {}
    for b in cfg["boards"]:
        url = ats.SYSTEMS[b["system"]][0](b["board"])
        files[url] = folder / f"{b['system']}-{b['board'].replace(' ', '_')}.json"

    def get(url, timeout):
        f = files.get(url)
        if f is None or not f.exists():
            raise Transient(f"no saved response for {url}")
        return 200, policy.read_bytes(f)
    return get


def write_outputs(policy, out, run_id, report, trace):
    policy.write_text(out / "trace" / f"{run_id}.jsonl", "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in trace))
    policy.write_text(out / f"report-{run_id}.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    policy.write_text(out / f"report-{run_id}.md", markdown(report))


def markdown(r):
    u = r["budget_used"]
    lines = [f"# Loop report {r['run_id']}", "",
             f"- **Exit: `{r['exit']}`** ({r['stop_reason']})",
             f"- Label: {r['label']}" + ("" if r["empty_guard"] else " · **empty guard OFF (naive demonstration mode)**"),
             f"- Budget used: {u['boards']}/{u['limits']['boards']} boards, {u['requests']}/{u['limits']['requests']} "
             f"requests, {u['seconds']}/{u['limits']['seconds']} s", ""]
    lines += ["| board | status | HTTP | attempts | postings | new | reason |", "|---|---|---|---|---|---|---|"]
    for b in r["boards"]:
        new = "baseline" if b.get("baseline") else b.get("new", "")
        pc = "null" if b["postings"] is None else b["postings"]
        lines.append(f"| {b['board']} | {b['status']} | {b['http_status']} | {b['attempts']} | {pc} | "
                     f"{'' if new is None else new} | {b['reason'] or ''} |")
    for k in r["never_ran"]:
        lines.append(f"| {k} | **never ran** (budget) | | 0 | null | | |")
    if r["escalations"]:
        lines += ["", "## Escalated to Riya", ""] + [f"- `{e['board']}`: {e['status']}: {e['reason']}"
                                                      for e in r["escalations"]]
    newp = [(b["board"], v) for b in r["boards"] for v in b.get("new_postings", [])]
    if newp:
        lines += ["", "## New postings (rule verdicts are records)", "", "| board | id | title | location | verdict |",
                  "|---|---|---|---|---|"]
        lines += [f"| {k} | {v['id']} | {v['title']} | {v['location']} | {v['verdict']} |" for k, v in newp]
    return "\n".join(lines) + "\n"


def reset(out_dir, key, approve):
    """Erase one board's memory. GATE.md: removing ids needs --approve; without it nothing is written."""
    out = Path(out_dir)
    policy = Policy(out, [ROOT], approve=approve)
    path = state_path(out, key)
    state = load_state(policy, path)
    if state is None:
        return f"no state for {key}; nothing to reset"
    old = state["seen_ids"]
    policy.write_state(path, old, {**state, "seen_ids": [], "reset_at": datetime.now(timezone.utc).isoformat(
        timespec="seconds"), "reset_approved": True})
    return f"reset {key}: removed {len(old)} ids (approved)"


def main(argv=None):
    ap = argparse.ArgumentParser(description="JS2 bounded job-board loop")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--config", default=str(ROOT / "boards.json"))
    r.add_argument("--out", default=str(ROOT / "runs"))
    r.add_argument("--fixtures", help="answer from saved responses instead of the network (label the run 'seeded')")
    r.add_argument("--label")
    r.add_argument("--no-empty-guard", action="store_true",
                   help="DEMONSTRATION ONLY: GATE.md wrong version 1, treat a 0-posting board as fine")
    x = sub.add_parser("reset")
    x.add_argument("--out", default=str(ROOT / "runs"))
    x.add_argument("--board", required=True)
    x.add_argument("--approve", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "reset":
        try:
            print(reset(a.out, a.board, a.approve))
        except PolicyError as e:
            sys.exit(f"REFUSED: {e}")
        return
    label = a.label or ("seeded" if a.fixtures else "live")
    if a.no_empty_guard:
        label += "-naive"
    rep = run(a.config, a.out, a.fixtures, label, empty_guard=not a.no_empty_guard)
    print(markdown(rep))
    sys.exit(EXIT_CODES[rep["exit"]])


if __name__ == "__main__":
    main()
