"""The loop (GATE.md sections 0-4): walk the boards once, within budget, and end with exactly one exit.

    python3 -m agent.loop                                  # live run of config/boards.json
    python3 -m agent.loop --fixture KEY=FILE ...           # seeded run: saved responses, no network
    python3 -m agent.loop --max-requests 2                 # lower a budget (a budget is never raised)
    python3 -m agent.loop --approve-state-reset KEY        # my approval for one state reset, this run only

Exit codes: finished 0, error 1, incomplete 2, budget_exhausted 3.
"""

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from agent import tools
from agent.boards import board_url, normalize, parse_postings, BadShape
from agent.policy import Policy, refuse
from agent.resume import ResumeRefused, check_resume
from agent.rule import judge

GATE = "GATE.md of 2026-11-10"
LIMITS = {"boards": 5, "requests": 8, "seconds": 120, "seconds_per_request": 30, "bytes_per_response": 20000000}
LOWERABLE = ("boards", "requests", "seconds")
RETRY_WAITS = [2, 4]
MAX_RETRY_AFTER = 10
REPEAT_LIMIT = 3
MAX_REDIRECTS = 2
TRANSIENT_STATUS = {429, 500, 502, 503, 504}
TRANSIENT_ERRORS = {"timeout", "connection"}
EXIT_CODES = {"finished": 0, "error": 1, "incomplete": 2, "budget_exhausted": 3}
CONFIG = Path("config") / "boards.json"
PERSONA = Path("persona") / "aarav-patel.resume.example.json"
MEANING = {
    "finished": "Every board was attempted within budget and every response looked usable. This is not proof "
                "that the boards have no other new jobs: `check_run.py` checks the run from the outside.",
    "incomplete": "Every board was attempted within budget, but at least one board failed or is suspect. "
                  "Those boards have no counts (not 0) and their state was not changed.",
    "budget_exhausted": "A budget ran out before every board was attempted. The boards not attempted are listed.",
    "error": "The run stopped because going on was not safe. Nothing was written after the error except "
             "this record and the last trace line.",
}


class OutOfBudget(Exception):
    def __init__(self, which):
        super().__init__(which)
        self.which = which


class RepeatLimit(Exception):
    pass


class Stop(Exception):
    def __init__(self, reason, detail):
        super().__init__("%s: %s" % (reason, detail))
        self.reason, self.detail = reason, detail


def classify(system, http_status, body):
    """(status, reason, postings) for one HTTP answer (GATE.md section 4)."""
    if http_status in (404, 410):
        return "failed", "not_found", None
    if http_status in (401, 403):
        return "failed", "forbidden", None
    if http_status in TRANSIENT_STATUS:
        return "failed", "transient", None
    if 300 <= http_status < 400:
        return "redirect", None, None
    if 400 <= http_status < 500:
        return "failed", "http_4xx", None
    if http_status != 200:
        return "failed", "http_%d" % http_status, None
    try:
        postings = parse_postings(system, body)
    except BadShape:
        return "failed", "bad_shape", None
    if not postings:
        return "suspect", "empty", None
    return "ok", None, postings


def should_retry(reason, headers, retries_done):
    """Seconds to wait before trying again, or None for no retry (GATE.md section 4)."""
    if reason != "transient" or retries_done >= len(RETRY_WAITS):
        return None
    retry_after = (headers or {}).get("retry-after")
    if retry_after is None:
        return RETRY_WAITS[retries_done]
    try:
        seconds = float(retry_after)
    except ValueError:
        return None
    return None if seconds > MAX_RETRY_AFTER else max(RETRY_WAITS[retries_done], seconds)


def request_timeout(seconds_left):
    """A request never gets more seconds than are left in the run (GATE.md W12)."""
    return min(LIMITS["seconds_per_request"], seconds_left)


def decide_exit(boards, not_attempted, stop):
    if stop and stop[0] == "error":
        return "error", stop[1]
    if stop and stop[0] == "budget":
        return "budget_exhausted", stop[1]
    bad = ["%s %s %s" % (b["key"], b["status"], b["reason"]) for b in boards if b["status"] in ("failed", "suspect")]
    if bad:
        return "incomplete", "; ".join(bad)
    return "finished", None


def checked_limits(limits):
    """GATE.md section 2: a flag may lower a budget, never raise it."""
    result = dict(LIMITS)
    for name, value in (limits or {}).items():
        if name not in LOWERABLE:
            raise ValueError("refused: %r is not a budget that can be changed per run" % name)
        if not isinstance(value, (int, float)) or math.isnan(value) or value < 0:  # NaN compares False to all
            raise ValueError("refused: budget %s must be a non-negative number" % name)
        if value > LIMITS[name]:
            raise ValueError("refused: GATE.md allows at most %s %s per run; raising it needs a new written "
                             "decision in GATE.md" % (LIMITS[name], name))
        result[name] = value
    return result


class Loop:
    def __init__(self, root, transport=None, clock=time.monotonic, sleep=time.sleep, now=None, limits=None,
                 approvals=(), fixtures=None, note=None, run_id=None):
        self.root = Path(os.path.realpath(root))
        self.limits = checked_limits(limits)
        self.policy = Policy(self.root, approvals)
        self.approvals = sorted(a.lower() for a in approvals)
        self.fixtures = dict(fixtures or {})
        self.transport = self.seeded_transport if self.fixtures else (transport or tools.http_transport)
        self.fixture_urls = {}
        self.clock, self.sleep = clock, sleep
        self.start = clock()
        self.now = now or datetime.now(timezone.utc)
        self.run_id = run_id or self.now.strftime("%Y-%m-%dT%H%M%SZ")
        self.note = note
        self.requests = 0
        self.attempted = 0
        self.fetched_ok = set()
        self.refused_repeats = 0
        self.step = 0
        self.resume = None
        self.runs_dir = self.root / "jobs" / "runs"
        self.trace_path = self.runs_dir / (self.run_id + ".trace.jsonl")
        self.trace_started = False

    # --- bookkeeping -------------------------------------------------------------------------------
    def seconds_left(self):
        return self.limits["seconds"] - (self.clock() - self.start)

    def rel(self, path):
        return Path(os.path.relpath(path, self.root)).as_posix()

    def trace(self, action, **fields):
        self.step += 1
        line = {"step": self.step, "t": round(self.clock() - self.start, 3), "action": action}
        line.update(fields)
        line["budget"] = {"boards_attempted": self.attempted, "requests_used": self.requests,
                          "requests_left": self.limits["requests"] - self.requests,
                          "seconds_left": round(self.seconds_left(), 3)}
        text = json.dumps(line, ensure_ascii=False) + "\n"
        if self.trace_started:
            tools.append_text(self.policy, self.trace_path, text)
        else:
            tools.write_new(self.policy, self.trace_path, text.encode("utf-8"))
            self.trace_started = True

    def seeded_transport(self, url, timeout, max_bytes):
        """A seeded run reads saved responses through the policy and never touches the network."""
        path = self.fixture_urls.get(url)
        if path is None:
            raise tools.FetchError("connection", "seeded run: no saved response for this board")
        data = tools.read_file(self.policy, path)
        body = gzip.decompress(data) if str(path).endswith(".gz") else data
        if len(body) > max_bytes:
            raise tools.FetchError("too_large", "over %d bytes" % max_bytes)
        return tools.Response(200, {"x-seeded-from": self.rel(path)}, body)

    # --- one request --------------------------------------------------------------------------------
    def request(self, key, url):
        """One GET, after the repeat rule, the budgets and the policy. Returns (attempt, response or None).

        Returns None for a refused repeat; the third refused repeat raises RepeatLimit.
        """
        if tools.normalize_url(url) in self.fetched_ok:
            self.refused_repeats += 1
            self.trace("refused_repeat", board=key, url=url, refused_repeats=self.refused_repeats)
            if self.refused_repeats >= REPEAT_LIMIT:
                raise RepeatLimit("%d refused repeats in one run" % self.refused_repeats)
            return None
        if self.requests >= self.limits["requests"]:
            raise OutOfBudget("requests")
        left = self.seconds_left()
        if left <= 0:
            raise OutOfBudget("seconds")
        timeout = request_timeout(left)
        decision = self.policy.check_fetch("GET", url)
        if not decision.allowed:
            self.trace("policy_refused", board=key, url=url, decision=decision.as_dict())
            raise tools.Refused(decision)
        self.requests += 1
        attempt = {"n": self.requests, "url": url, "timeout": round(timeout, 3)}
        started = self.clock()
        try:
            response = tools.fetch(self.policy, url, self.transport, timeout=timeout,
                                   max_bytes=self.limits["bytes_per_response"])
        except tools.FetchError as error:
            attempt.update(error=error.kind, detail=error.detail, seconds=round(self.clock() - started, 3))
            self.trace("fetch", board=key, url=url, policy="allow", timeout=attempt["timeout"],
                       result={"error": error.kind, "detail": error.detail}, seconds=attempt["seconds"])
            return attempt, None
        raw_path = self.root / "jobs" / "raw" / ("%s--%s--r%d.body.gz" % (self.run_id, key.replace("/", "-"),
                                                                          self.requests))
        tools.write_new(self.policy, raw_path, gzip.compress(response.body, mtime=0))  # saved before parsing
        attempt.update(http_status=response.status, bytes=len(response.body), raw_file=self.rel(raw_path),
                       raw_sha256=hashlib.sha256(response.body).hexdigest(), seconds=round(self.clock() - started, 3))
        if "x-seeded-from" in response.headers:
            attempt["seeded_from"] = response.headers["x-seeded-from"]
        self.trace("fetch", board=key, url=url, policy="allow", timeout=attempt["timeout"],
                   result={k: attempt[k] for k in ("http_status", "bytes", "raw_file", "raw_sha256")},
                   seconds=attempt["seconds"])
        if response.status == 200:
            self.fetched_ok.add(tools.normalize_url(url))
        return attempt, response

    # --- one board ----------------------------------------------------------------------------------
    def watch_board(self, entry, key):
        system, name = key.split("/", 1)
        url = board_url(system, entry["board"])
        result = {"key": key, "system": system, "board": entry["board"], "company": entry.get("company"),
                  "url": url, "status": None, "reason": None, "http_status": None, "requests": 0,
                  "attempts": [], "counts": None, "run_kind": None}
        retries = redirects = 0
        requested = {tools.normalize_url(url)}
        while True:
            got = self.request(key, url)
            if got is None:
                result.update(status="failed", reason="refused_repeat")
                return result
            attempt, response = got
            result["attempts"].append(attempt)
            result["requests"] += 1
            headers = {}
            if response is None:
                kind = attempt["error"]
                status, reason, postings = "failed", ("transient" if kind in TRANSIENT_ERRORS else kind), None
            else:
                headers = response.headers
                result["http_status"] = response.status
                status, reason, postings = classify(system, response.status, response.body)
            self.trace("classify", board=key, status=status, reason=reason,
                       postings=None if postings is None else len(postings))

            if status == "redirect":
                target = tools.join_url(url, headers.get("location"))
                decision = self.policy.check_fetch("GET", target)
                if not headers.get("location") or tools.normalize_url(target) in requested:
                    decision = refuse("a redirect with no new Location would repeat the same fetch",
                                     target)
                if redirects >= MAX_REDIRECTS or not decision.allowed:
                    self.trace("redirect_refused", board=key, url=target, decision=decision.as_dict())
                    result.update(status="failed", reason="refused_redirect", redirect_to=target)
                    return result
                if self.requests >= self.limits["requests"] or self.seconds_left() <= 0:
                    result.update(status="failed", reason="out_of_budget", redirect_to=target)
                    return result
                redirects += 1
                requested.add(tools.normalize_url(target))
                self.trace("redirect_followed", board=key, url=target)
                url = target
                continue

            if status == "failed":
                wait = should_retry(reason, headers, retries)
                if wait is None:
                    result.update(status="failed", reason=reason)
                    return result
                if self.requests >= self.limits["requests"] or self.seconds_left() <= wait:
                    self.trace("retry_not_affordable", board=key, wait=wait)
                    result.update(status="failed", reason=reason, retry_not_affordable=True)
                    return result
                retries += 1
                self.trace("retry_wait", board=key, seconds=wait, retry=retries)
                self.sleep(wait)
                continue

            if status == "suspect":
                result.update(status="suspect", reason=reason)
                return result

            return self.compare(result, entry, postings, attempt)

    def read_state(self, path):
        if not tools.exists(self.policy, path):
            return None
        try:
            state = json.loads(tools.read_file(self.policy, path).decode("utf-8"))
            if not isinstance(state.get("seen_ids"), list):
                raise ValueError("no seen_ids list")
        except ValueError as error:
            raise Stop("state_unreadable", "%s cannot be read (%s); not starting over" % (self.rel(path), error))
        return state

    def compare(self, result, entry, postings, attempt):
        key, system = result["key"], result["system"]
        state_path = self.root / "jobs" / "state" / ("%s.json" % key.replace("/", "-"))
        state = self.read_state(state_path)
        unique, duplicates = {}, 0
        for job in postings:
            posting = normalize(system, job, entry.get("company"))
            if posting["id"] in unique:
                duplicates += 1
            else:
                unique[posting["id"]] = posting
        seen = set(state["seen_ids"]) if state else set()
        new_ids = [i for i in unique if i not in seen] if state else []
        new_postings = []
        for i in new_ids:
            p = unique[i]
            new_postings.append({"job_id": i, "title": p["title"], "location": p["location"]["name"],
                                 "absolute_url": p["absolute_url"], "company_name": p["company_name"],
                                 "first_published": p.get("first_published"),
                                 "rule_verdict": judge(p, self.resume)})
        # Gone since the last good run. A state imported from JS1 has no last_ids; its seen ids are JS1's last run.
        last = set(state.get("last_ids", state["seen_ids"])) if state else set()
        counts = {"postings": len(unique), "new": len(new_postings), "gone": len(last - set(unique)),
                  "duplicate_ids": duplicates}
        new_state = dict(state or {"system": system, "board": key.split("/", 1)[1]})
        new_state["seen_ids"] = sorted(seen | set(unique))
        new_state["last_ids"] = sorted(unique)
        new_state["runs"] = list((state or {}).get("runs", [])) + [{
            "run_id": self.run_id, "source": "seeded" if self.fixtures else "live",
            "postings": len(unique), "new": len(new_postings), "raw_file": attempt["raw_file"]}]
        try:
            decision = tools.write_state(self.policy, state_path, new_state, key)
        except tools.Refused as refused:
            self.trace("policy_refused", board=key, path=self.rel(state_path), decision=refused.decision.as_dict())
            raise
        self.trace("compare", board=key, run_kind="watch" if state else "baseline", counts=counts,
                   new_ids=new_ids, state_file=self.rel(state_path), policy=decision.as_dict())
        result.update(status="ok", run_kind="watch" if state else "baseline", counts=counts,
                      new_postings=new_postings)
        return result

    # --- the run --------------------------------------------------------------------------------------
    def run(self):
        boards, not_attempted, stop, error_detail = [], [], None, None
        entries, keys, index = [], [], 0
        try:
            config = json.loads(tools.read_file(self.policy, self.root / CONFIG).decode("utf-8"))
            entries = config["boards"]
            keys = ["%s/%s" % (e["system"].lower(), e["board"].lower()) for e in entries]
            try:
                self.resume = check_resume(tools.read_file(self.policy, self.root / PERSONA).decode("utf-8"))
            except ResumeRefused as refused:
                raise Stop("persona_refused", str(refused))
            for key, entry in zip(keys, entries):
                if key in self.fixtures:
                    self.fixture_urls[board_url(key.split("/")[0], entry["board"])] = self.root / self.fixtures[key]
            self.trace("start", run_id=self.run_id, gate=GATE, source="seeded" if self.fixtures else "live",
                       boards=keys, limits=self.limits, approvals=self.approvals,
                       fixtures={k: str(v) for k, v in self.fixtures.items()})
            watched = set()
            for index, (key, entry) in enumerate(zip(keys, entries)):
                if key in watched:
                    boards.append({"key": key, "system": key.split("/")[0], "board": entry["board"],
                                   "company": entry.get("company"), "status": "skipped_repeat",
                                   "reason": "same board as an earlier entry", "requests": 0, "counts": None})
                    self.trace("skipped_repeat", board=key)
                    continue
                if self.attempted >= self.limits["boards"]:
                    raise OutOfBudget("boards")
                if self.requests >= self.limits["requests"]:
                    raise OutOfBudget("requests")
                if self.seconds_left() <= 0:
                    raise OutOfBudget("seconds")
                watched.add(key)
                self.attempted += 1
                if key.split("/")[0] not in ("greenhouse", "lever", "ashby"):
                    raise Stop("unknown_system", "%s: the config names a system the agent has no reader for" % key)
                boards.append(self.watch_board(entry, key))
            index = len(entries)
        except OutOfBudget as out:
            stop = ("budget", out.which)
        except RepeatLimit as repeat:
            stop, error_detail = ("error", "repeat_limit"), str(repeat)
        except tools.Refused as refused:
            stop, error_detail = ("error", "policy_refused"), str(refused)
        except Stop as stopped:
            stop, error_detail = ("error", stopped.reason), stopped.detail
        except Exception as unexpected:  # an error exit, never a crash without a record
            stop, error_detail = ("error", "unexpected"), "%s: %s" % (type(unexpected).__name__, unexpected)
        done = {b["key"] for b in boards}
        not_attempted = []
        for key in keys[index:]:
            if key not in done and key not in not_attempted:
                not_attempted.append(key)
        exit_, reason = decide_exit(boards, not_attempted, stop)
        return self.finish(boards, not_attempted, exit_, reason, error_detail)

    def finish(self, boards, not_attempted, exit_, reason, error_detail):
        record = {
            "run_id": self.run_id, "gate": GATE, "source": "seeded" if self.fixtures else "live",
            "fixtures": {k: str(v) for k, v in self.fixtures.items()}, "note": self.note,
            "started_at": self.now.isoformat(timespec="seconds"),
            "exit": exit_, "exit_code": EXIT_CODES[exit_], "exit_reason": reason, "error_detail": error_detail,
            "meaning": MEANING[exit_],
            "budget": {"limits": self.limits, "used": {"boards": self.attempted, "requests": self.requests,
                                                       "seconds": round(self.clock() - self.start, 3)}},
            "boards": boards, "not_attempted": not_attempted, "approvals": self.approvals,
            "files": {"record": self.rel(self.runs_dir / (self.run_id + ".json")),
                      "report": self.rel(self.runs_dir / (self.run_id + ".md")),
                      "trace": self.rel(self.trace_path)},
        }
        tools.write_new(self.policy, self.root / record["files"]["record"],
                        (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        tools.write_new(self.policy, self.root / record["files"]["report"], report(record).encode("utf-8"))
        self.trace("exit", exit=exit_, exit_code=EXIT_CODES[exit_], reason=reason, not_attempted=not_attempted)
        return record


def run(root, transport=None, clock=time.monotonic, sleep=time.sleep, now=None, limits=None, approvals=(),
        fixtures=None, note=None, run_id=None):
    checked_limits(limits)  # refuse a raised budget before anything is read, sent or written
    return Loop(root, transport=transport, clock=clock, sleep=sleep, now=now, limits=limits, approvals=approvals,
                fixtures=fixtures, note=note, run_id=run_id).run()


def report(record):
    used, limits = record["budget"]["used"], record["budget"]["limits"]
    source = "SEEDED from saved responses (no network)" if record["source"] == "seeded" else "LIVE"
    lines = ["# Run %s" % record["run_id"], "",
             "- **Source:** %s" % source,
             "- **Exit:** `%s` (code %d)%s" % (record["exit"], record["exit_code"],
                                              (": " + record["exit_reason"]) if record["exit_reason"] else ""),
             "- **What that means:** %s" % record["meaning"],
             "- **Budget used:** %d of %d boards, %d of %d requests, %.1f of %d seconds"
             % (used["boards"], limits["boards"], used["requests"], limits["requests"], used["seconds"],
                limits["seconds"]),
             "- **Rules:** %s" % record["gate"]]
    if record["error_detail"]:
        lines.append("- **Error:** %s" % record["error_detail"])
    if record.get("note"):
        lines.append("- **Note:** %s" % record["note"])
    lines += ["", "| Board | Status | HTTP | Requests | Postings | New | Gone |", "|---|---|---:|---:|---:|---:|---:|"]
    for b in record["boards"]:
        c = b.get("counts")
        status = b["status"] + ((": " + b["reason"]) if b.get("reason") else "")
        lines.append("| %s | %s | %s | %d | %s | %s | %s |" % (
            b["key"], status, b.get("http_status") or "—", b["requests"],
            c["postings"] if c else "—", c["new"] if c else "—", c["gone"] if c else "—"))
    for key in record["not_attempted"]:
        lines.append("| %s | not attempted | — | 0 | — | — | — |" % key)
    lines.append("")
    lines.append("A dash means no value: a failed, suspect or skipped board has no counts, never 0.")
    for b in record["boards"]:
        if b["status"] in ("failed", "suspect"):
            lines += ["", "**%s: %s.** %s" % (b["key"], b["reason"], ESCALATE.get(b["reason"], ""))]
    for b in record["boards"]:
        if b["status"] != "ok":
            continue
        lines += ["", "## %s (%s)" % (b["key"], b["run_kind"]), ""]
        if b["run_kind"] == "baseline":
            lines.append("First run for this board: every id is recorded, none is reported as new.")
            continue
        if not b["new_postings"]:
            lines.append("No new ids since the last good run of this board.")
            continue
        matches = [p for p in b["new_postings"] if p["rule_verdict"]["verdict"] == "MATCH"]
        lines.append("%d new ids. JS1 rule (R1-R5): %d MATCH, %d NOT_MATCH." % (
            len(b["new_postings"]), len(matches), len(b["new_postings"]) - len(matches)))
        lines.append("")
        for p in b["new_postings"]:
            failed = [c["rule"] for c in p["rule_verdict"]["checks"] if not c["passed"]]
            lines.append("- %s · %s · %s · %s%s" % (p["rule_verdict"]["verdict"], p["job_id"], p["title"],
                                                   p["location"], (" · fails " + ", ".join(failed)) if failed else ""))
    lines.append("")
    return "\n".join(lines)


ESCALATE = {
    "not_found": "The board name is wrong or the board is gone. Check the name by hand; it was not retried.",
    "forbidden": "The board wants a login. The agent never logs in.",
    "empty": "A 200 with zero postings is not proof of no jobs. Check the board's public page by hand.",
    "transient": "The server or network failed, and the allowed retries did not help.",
    "bad_shape": "The board answered with something that is not a board. Nothing was guessed from it.",
    "refused_redirect": "The board redirected to a place the policy refuses. The redirect was not followed.",
    "too_large": "The response was larger than the byte budget and was not read to the end.",
}


def main(argv=None):
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Job-Search Agent 2: one bounded run over config/boards.json.")
    parser.add_argument("--root", type=Path, default=here, help="the folder with config/, persona/ and jobs/")
    parser.add_argument("--max-boards", type=int)
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--max-seconds", type=float)
    parser.add_argument("--approve-state-reset", action="append", default=[], metavar="KEY",
                        help="my approval, for this run only, to reset one board's state (e.g. lever/palantir)")
    parser.add_argument("--fixture", action="append", default=[], metavar="KEY=FILE",
                        help="seeded run: use this saved response (relative to --root) for that board")
    parser.add_argument("--note", help="a note written into the run record and report")
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)
    limits = {name: value for name, value in (("boards", args.max_boards), ("requests", args.max_requests),
                                               ("seconds", args.max_seconds)) if value is not None}
    fixtures = dict(item.split("=", 1) for item in args.fixture)
    try:
        record = run(args.root, limits=limits, approvals=args.approve_state_reset, fixtures=fixtures,
                     note=args.note, run_id=args.run_id)
    except ValueError as error:
        print(error, file=sys.stderr)
        return EXIT_CODES["error"]
    print("Run %s (%s): exit %s%s" % (record["run_id"], record["source"], record["exit"],
                                      (" — " + record["exit_reason"]) if record["exit_reason"] else ""))
    for b in record["boards"]:
        c = b.get("counts")
        print("  %-45s %-22s %s" % (b["key"], b["status"] + ((":" + b["reason"]) if b.get("reason") else ""),
                                    ("%d postings, %d new" % (c["postings"], c["new"])) if c else "no counts"))
    for key in record["not_attempted"]:
        print("  %-45s not attempted" % key)
    print("Record: %s\nReport: %s\nTrace:  %s" % (record["files"]["record"], record["files"]["report"],
                                                  record["files"]["trace"]))
    return record["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
