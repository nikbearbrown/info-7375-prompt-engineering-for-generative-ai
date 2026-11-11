"""The bounded loop (GATE.md sections 1-4): watch several boards, under a
budget, with a repeat rule and an error policy, and end in exactly one exit.

    python3 -m agent.loop                          # live, config/boards.json
    python3 -m agent.loop --approve-state          # I approve state overwrites
    python3 -m agent.loop --fixtures F.json --seeded   # from saved responses

Every observation goes to runs/<stamp>-<kind>/trace.jsonl; the raw body of
every response goes to runs/<stamp>-<kind>/raw/. All writes go through the
policy.
"""

import argparse
import datetime
import gzip
import hashlib
import json
import pathlib
import sys
import time

from agent import net, providers
from agent.policy import (NeedsApproval, Policy, Refused, ask_on_terminal,
                          always_approve, no_approval)

EXIT_CODES = {"finished": 0, "error": 1, "incomplete": 2,
              "budget_exhausted": 3}
RETRYABLE = {"timeout", "server_error"}       # GATE 4: one retry, these only
ROOT = pathlib.Path(__file__).resolve().parent.parent


class BudgetExhausted(Exception):
    def __init__(self, which, used, limit):
        super().__init__(f"{which} budget exhausted ({used}/{limit})")
        self.which, self.used, self.limit = which, used, limit


class Budget:
    """Checked BEFORE each board and each request. Retries are requests."""

    def __init__(self, limits, clock=time.monotonic):
        self.limits, self.clock = limits, clock
        self.t0 = clock()
        self.boards = self.requests = 0

    def elapsed(self):
        return self.clock() - self.t0

    def _time(self):
        if self.elapsed() >= self.limits["seconds"]:
            raise BudgetExhausted("seconds", round(self.elapsed(), 1),
                                  self.limits["seconds"])

    def start_board(self):
        self._time()
        if self.boards >= self.limits["boards"]:
            raise BudgetExhausted("boards", self.boards,
                                  self.limits["boards"])
        self.boards += 1

    def take_request(self):
        self._time()
        if self.requests >= self.limits["requests"]:
            raise BudgetExhausted("requests", self.requests,
                                  self.limits["requests"])
        self.requests += 1


GATE_ROWS = [("boards", r"Boards"), ("requests", r"Requests"),
             ("seconds", r"Seconds \(wall clock")]


def budget_mismatches(gate_text, limits):
    """GATE 2: the budgets the code uses must equal GATE.md's table. Returns
    a list of problems; empty means they match."""
    import re
    bad = []
    for key, label in GATE_ROWS:
        m = re.search(rf"^\| {label}[^|]*\| \*\*(\d+)\*\*", gate_text, re.M)
        if not m:
            bad.append(f"GATE.md has no '{key}' row")
        elif limits.get(key) != int(m.group(1)):
            bad.append(f"{key}: config {limits.get(key)} != GATE.md "
                       f"{m.group(1)}")
    m = re.search(r"Seconds per single request \(timeout\) \| (\d+)",
                  gate_text)
    if not m or limits.get("request_timeout_seconds") != int(m.group(1)):
        bad.append("request_timeout_seconds does not match GATE.md")
    return bad


def repeat_key(ats, board):
    """GATE 3: same ATS host + same board name, ignoring capitals."""
    return (ats, board.lower())


def classify(ats, resp):
    """(status, reason, postings or None) for one HTTP answer."""
    if resp.status == 200:
        try:
            postings = providers.parse(ats, resp.body)
        except providers.BadBody as e:
            return "bad_body", str(e), None
        if not postings:
            return ("suspicious_empty",
                    "HTTP 200 with 0 jobs: not reported as 'no new jobs'",
                    postings)
        return "ok", f"{len(postings)} jobs", postings
    if resp.status == 404:
        return "not_found", "HTTP 404: board name not found", None
    if 500 <= resp.status < 600:
        return "server_error", f"HTTP {resp.status}", None
    return f"http_{resp.status}", f"HTTP {resp.status}", None


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H%M%SZ")


def run(boards, *, policy, get, limits, kind="live", approver=no_approval,
        clock=time.monotonic, sleep=time.sleep, stamp=None, source=None):
    stamp = stamp or utc_stamp()
    run_dir = f"runs/{stamp}-{kind}"
    budget = Budget(limits, clock)
    trace, results, seen = [], [], set()
    stop, fatal = None, None

    def observe(**event):
        event = {"seq": len(trace) + 1, "t": round(budget.elapsed(), 3),
                 **event}
        trace.append(event)
        return event

    observe(event="run_start", kind=kind, boards_planned=len(boards),
            limits=limits, source=source)

    for i, entry in enumerate(boards):
        ats, board = entry["ats"], entry["board"]
        res = {"ats": ats, "board": board, "status": None, "reason": None,
               "jobs": None, "new_count": None, "new": None,
               "baseline": None, "state_written": None, "attempts": 0,
               "raw": []}
        results.append(res)

        if stop or fatal:
            res.update(status="not_visited",
                       reason=f"run stopped: {stop or fatal}")
            observe(event="board_not_visited", ats=ats, board=board,
                    reason=res["reason"])
            continue

        key = repeat_key(ats, board)
        if key in seen:
            res.update(status="skipped_repeat",
                       reason=f"same action as an earlier board {key}")
            observe(event="skipped_repeat", ats=ats, board=board, key=key)
            continue
        seen.add(key)

        try:
            budget.start_board()
        except BudgetExhausted as e:
            stop = str(e)
            res.update(status="not_visited", reason=stop)
            observe(event="budget_exhausted", which=e.which, ats=ats,
                    board=board)
            continue

        try:
            url = policy.check_url(providers.url_for(ats, board))
        except (ValueError, Refused) as e:
            fatal = f"config/permission error on {ats}/{board}: {e}"
            res.update(status="refused", reason=str(e))
            observe(event="refused", ats=ats, board=board, reason=str(e))
            continue
        res["url"] = url

        postings = None
        for attempt in (1, 2):
            try:
                budget.take_request()
            except BudgetExhausted as e:
                stop = str(e)
                if attempt == 1:
                    res.update(status="not_visited", reason=stop)
                else:
                    res["reason"] += f"; retry skipped: {stop}"
                observe(event="budget_exhausted", which=e.which, ats=ats,
                        board=board, attempt=attempt)
                break
            res["attempts"] = attempt
            t_req = clock()
            try:
                resp = get(url, limits["request_timeout_seconds"])
            except net.Timeout as e:
                status, reason, postings, resp = "timeout", str(e), None, None
            except Refused as e:
                fatal = f"permission refused: {e}"
                res.update(status="refused", reason=str(e))
                observe(event="refused", ats=ats, board=board, url=url,
                        reason=str(e))
                break
            else:
                status, reason, postings = classify(ats, resp)
            ev = {"event": "request", "ats": ats, "board": board, "url": url,
                  "attempt": attempt, "outcome": status, "reason": reason,
                  "seconds": round(clock() - t_req, 3)}
            if resp is not None:
                raw_path = (f"{run_dir}/raw/{ats}-{board}-attempt{attempt}"
                            f"-http{resp.status}.body.gz")
                policy.write_bytes(raw_path, gzip.compress(resp.body,
                                                           mtime=0))
                ev.update(http_status=resp.status, bytes=len(resp.body),
                          sha256=hashlib.sha256(resp.body).hexdigest(),
                          raw=raw_path)
                res["raw"].append(raw_path)
            if postings is not None:
                ev["jobs"] = len(postings)
            observe(**ev)
            res.update(status=status, reason=reason)
            if status in RETRYABLE and attempt == 1:
                observe(event="retry", ats=ats, board=board,
                        why=f"{status} can be temporary; one retry (GATE 4)")
                sleep(limits["retry_wait_seconds"])
                continue
            break

        if res["status"] == "suspicious_empty":
            res["jobs"] = 0                 # what the board said; new = None
        if res["status"] == "ok":
            res["jobs"] = len(postings)
            _update_state(res, postings, policy, approver, stamp, kind,
                          observe)

    exit_ = _exit(results, stop, fatal)
    report = _report(stamp, kind, source, limits, budget, results, exit_,
                     stop, fatal)
    observe(event="run_end", exit=exit_["exit"], reason=exit_["reason"])
    policy.write_bytes(f"{run_dir}/trace.jsonl", "".join(
        json.dumps(e, ensure_ascii=False) + "\n" for e in trace).encode())
    policy.write_bytes(f"{run_dir}/report.json", (json.dumps(
        report, indent=2, ensure_ascii=False) + "\n").encode())
    policy.write_bytes(f"{run_dir}/report.md", render(report).encode())
    report["run_dir"] = run_dir
    return report, trace


def _update_state(res, postings, policy, approver, stamp, kind, observe):
    path = f"state/{res['ats']}-{res['board'].lower()}.json"
    try:
        prev = json.loads(policy.read_bytes(path))
    except FileNotFoundError:
        prev = None
    ids = {p["id"]: p for p in postings}
    if prev is None:
        res.update(baseline=True, new_count=0, new=[])
    else:
        seen = set(prev["seen_ids"])
        fresh = sorted(i for i in ids if i not in seen)
        res.update(baseline=False, new_count=len(fresh),
                   new=[ids[i] for i in fresh])
    new_state = {
        "ats": res["ats"], "board": res["board"].lower(),
        "seen_ids": sorted(set(prev["seen_ids"] if prev else []) | set(ids)),
        "runs": (prev["runs"] if prev else []) + [
            {"stamp": stamp, "kind": kind, "jobs": len(ids),
             "new": res["new_count"]}],
    }
    if prev and prev.get("imported_from"):
        new_state["imported_from"] = prev["imported_from"]
    try:
        policy.write_bytes(path, (json.dumps(new_state, indent=1) + "\n")
                           .encode(), approver=approver)
        res["state_written"] = True
        observe(event="state_written", path=path,
                overwrite=prev is not None)
    except NeedsApproval as e:
        res["state_written"] = False
        res["reason"] += "; state NOT updated (no approval)"
        observe(event="state_not_written", path=path, reason=str(e))


def _exit(results, stop, fatal):
    if fatal:
        return {"exit": "error", "reason": fatal}
    if stop:
        return {"exit": "budget_exhausted", "reason": stop}
    visited = [r for r in results
               if r["status"] not in ("skipped_repeat", "not_visited")]
    if visited and not any(r["status"] in ("ok", "suspicious_empty")
                           for r in visited):
        return {"exit": "error", "reason": "every board failed"}
    problems = [f"{r['ats']}/{r['board']}: {r['status']}" for r in visited
                if r["status"] != "ok" or r["state_written"] is False]
    if problems:
        return {"exit": "incomplete", "reason": "; ".join(problems)}
    return {"exit": "finished", "reason": "every board fetched, parsed, "
                                          "non-empty, state saved"}


def _report(stamp, kind, source, limits, budget, results, exit_, stop,
            fatal):
    ok = [r for r in results if r["status"] == "ok"]
    return {
        "stamp": stamp, "kind": kind, "source": source,
        "exit": exit_["exit"], "exit_code": EXIT_CODES[exit_["exit"]],
        "exit_reason": exit_["reason"],
        "escalate": [f"{r['ats']}/{r['board']}: {r['status']} ({r['reason']})"
                     for r in results
                     if r["status"] not in ("ok", "skipped_repeat")
                     or r["state_written"] is False],
        "budget_used": {"boards": budget.boards, "requests": budget.requests,
                        "seconds": round(budget.elapsed(), 2)},
        "limits": limits,
        # totals count ok boards only: a failed board is never a 0
        "jobs_total_ok_boards": sum(r["jobs"] for r in ok),
        "boards_counted": [f"{r['ats']}/{r['board']}" for r in ok],
        "boards": results,
    }


def render(r):
    lines = [f"# JS2 run {r['stamp']} ({r['kind'].upper()})", "",
             f"- **Exit:** `{r['exit']}` (code {r['exit_code']}): "
             f"{r['exit_reason']}",
             f"- **Budget used:** {r['budget_used']['boards']}/"
             f"{r['limits']['boards']} boards, {r['budget_used']['requests']}/"
             f"{r['limits']['requests']} requests, "
             f"{r['budget_used']['seconds']}/{r['limits']['seconds']} s"]
    if r["source"]:
        lines.append(f"- **Source:** {r['source']}")
    if r["escalate"]:
        lines += ["", "## For me to look at", ""]
        lines += [f"- {e}" for e in r["escalate"]]
    lines += ["", "## Boards", "",
              "| # | ATS | board | status | attempts | jobs | new | state saved |",
              "|---|---|---|---|---|---|---|---|"]
    for i, b in enumerate(r["boards"], 1):
        def show(v):
            return "—" if v is None else v
        new = ("baseline" if b["baseline"] else show(b["new_count"]))
        lines.append(f"| {i} | {b['ats']} | {b['board']} | {b['status']} | "
                     f"{b['attempts']} | {show(b['jobs'])} | {new} | "
                     f"{show(b['state_written'])} |")
    lines += ["", f"Jobs on boards that worked: {r['jobs_total_ok_boards']} "
                  f"({', '.join(r['boards_counted']) or 'none'}). "
                  "Failed boards are not counted as 0.", ""]
    for b in r["boards"]:
        if b["new"]:
            lines += [f"### New on {b['ats']}/{b['board']} "
                      f"({len(b['new'])})", ""]
            lines += [f"- {p['title']} — {p['location']} (`{p['id']}`)"
                      for p in b["new"]]
            lines.append("")
    return "\n".join(lines) + "\n"


def fixture_get(policy, manifest_path):
    """A seeded `get`: answers from saved files, still through the policy."""
    man = json.loads(policy.read_bytes(manifest_path))

    def get(url, timeout):
        policy.check_action("fetch_board")
        policy.check_url(url)
        spec = man["responses"].get(url)
        if spec is None:
            raise net.Timeout(f"seeded: no saved response for {url}")
        if spec.get("timeout"):
            raise net.Timeout("seeded timeout")
        body = policy.read_bytes(spec["file"]) if spec.get("file") else b""
        if spec.get("file", "").endswith(".gz"):
            body = gzip.decompress(body)
        return net.Response(spec.get("status", 200), body)
    return get


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--boards", default="config/boards.json")
    ap.add_argument("--budgets", default="config/budgets.json")
    ap.add_argument("--approve-state", action="store_true",
                    help="I approve overwriting files in state/ for this run")
    ap.add_argument("--fixtures", help="seeded run from a manifest of saved "
                                       "responses")
    ap.add_argument("--seeded", action="store_true",
                    help="required with --fixtures; labels the run seeded")
    a = ap.parse_args(argv)
    if a.fixtures and not a.seeded:
        ap.error("--fixtures needs --seeded: a run from saved responses must "
                 "be labeled as seeded")
    policy = Policy(ROOT)   # all paths below are relative to the JS2 folder
    limits = json.loads(policy.read_bytes(a.budgets))
    limits = {k: v for k, v in limits.items() if not k.startswith("_")}
    bad = budget_mismatches(policy.read_bytes("GATE.md").decode(), limits)
    if bad:
        print("REFUSING TO RUN: config/budgets.json does not match GATE.md "
              "section 2 (a budget changes only by a written decision):\n  "
              + "\n  ".join(bad))
        return EXIT_CODES["error"]
    boards = json.loads(policy.read_bytes(a.boards))["boards"]
    approver = always_approve if a.approve_state else ask_on_terminal
    if a.fixtures:
        get, kind, source = fixture_get(policy, a.fixtures), "seeded", \
            a.fixtures
    else:
        get, kind, source = net.make_get(policy), "live", None
    report, _ = run(boards, policy=policy, get=get, limits=limits, kind=kind,
                    approver=approver, source=source)
    print(render(report))
    print(f"Saved in {report['run_dir']}/ (trace.jsonl, report.json, raw/)")
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
