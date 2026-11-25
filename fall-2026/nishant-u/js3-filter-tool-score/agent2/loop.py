"""The bounded loop from GATE.md: several boards, budgets, a repeat rule, an error policy, and
exactly one exit status. Every network call and file write goes through agent2.policy.

    python -m agent2.loop --profile full          # boards 1-5, live; ends incomplete (board 5 fails)
    python -m agent2.loop --profile demo          # boards 1-4, live (the finished-wrong-answer run before
                                                  # the review-packet patch; now ends incomplete)
    python -m agent2.loop --profile demo --replay-dir out/runs/<run>   # no network
    python -m agent2.loop --profile demo --claude # also the optional Claude judge (JS1)

`finished` means every planned board returned a parsed response within budget. It does not
mean the answer is right: run `python -m agent2.check out/runs/<run>` for the outcome check.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path

from agent2 import ROOT, providers
from agent2.policy import Policy, PolicyRefused

SYSTEMS = ("greenhouse", "ashby")
DEFAULT_BUDGETS = {"boards": 5, "requests": 10, "seconds": 60}
RETRY_DELAY = 2
REQUEST_TIMEOUT = 20
STATE = "state/seen_ids.json"


def _board(system, board, company):
    return {"system": system, "board": board, "company": company, "url": providers.url_for(system, board)}


PROFILES = {
    "full": [
        _board("greenhouse", "faire", "faire"),
        _board("greenhouse", "instacart", "instacart"),
        _board("ashby", "poshmark", "poshmark"),
        _board("greenhouse", "poshmark", "poshmark"),
        _board("greenhouse", "no-such-board-js2-test", "no-such-board-js2-test"),
    ],
}
PROFILES["demo"] = PROFILES["full"][:4]


class ConfigError(ValueError):
    pass


class NotInReplay(Exception):
    """A --replay-dir run asked for a URL the saved run has no response for."""


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def rule_judge(postings):
    """The JS1 rule judge (agent.rules, CONTRACT.md R1-R4) on new postings; verdicts are records."""
    from agent import rules, validator
    from agent.resume import load_resume
    resume = load_resume(ROOT / "data" / "resume.example.json")
    requirements = json.loads((ROOT / "data" / "requirements.json").read_text(encoding="utf-8"))
    verdicts = []
    for posting in postings:
        view = providers.judge_view(posting)
        verdict = rules.evaluate(view, resume, requirements)
        for c in verdict["citations"]:
            c["support"] = validator.support_check(c, view)
        verdicts.append(verdict)
    return verdicts


class Loop:
    def __init__(self, boards, policy, client=None, clock=time.monotonic, sleep=time.sleep, budgets=None,
                 judge=None, mode="live", profile=None, claude=False, now=_utc_now):
        self.boards = boards
        self.policy = policy
        self.client = client or (lambda url, timeout: providers.http_get(url, policy, timeout=timeout)[:2])
        self.clock, self.sleep, self.now = clock, sleep, now
        self.budgets = dict(DEFAULT_BUDGETS, **(budgets or {}))
        self.judge = judge or rule_judge
        self.mode, self.profile, self.claude = mode, profile, claude

    # --- the pieces a wrong version would change (see tests/js2_mutants.py) ------------------
    def _count_request(self, kind):
        self.requests += 1

    def exit_status(self, stopped_by_budget):
        if stopped_by_budget:
            return "budget-exhausted"
        # GATE.md amendment (before the review-packet patch): an empty 200 board is not a clean result.
        if any(e["status"] in ("failed", "unverified-empty") for e in self.entries):
            return "incomplete"
        return "finished"

    def _fail(self, entry, reason, http_status=None):
        # No invented value: a failed board has no posting count and no new ids, never "0 new".
        entry.update(status="failed", reason=reason, http_status=http_status,
                     postings=None, new_ids=None, baseline=None)

    # --- budgets and records ----------------------------------------------------------------
    def _seconds(self):
        return round(self.clock() - self.started, 3)

    def _budget_block(self):
        """The name of the budget that forbids another request now, or None."""
        if self.requests >= self.budgets["requests"]:
            return "requests"
        if self._seconds() >= self.budgets["seconds"]:
            return "seconds"
        return None

    def _trace(self, action, b, decision, host=None, http_status=None, body=None):
        parts = urllib.parse.urlsplit(b["url"])
        line = {
            "step": len(self.trace) + 1, "action": action, "system": b["system"], "board": b["board"],
            "host": host, "path": parts.path + (f"?{parts.query}" if parts.query else ""),
            "http_status": http_status, "bytes": None if body is None else len(body),
            "sha256": None if body is None else hashlib.sha256(body).hexdigest(), "decision": decision,
            "requests_used": self.requests, "boards_attempted": self.boards_attempted,
            "seconds_used": self._seconds(),
        }
        self.trace.append(line)
        return line

    def _save_raw(self, step, b, status, body, attempt):
        stem = f"{step:02d}-{_safe(b['system'])}-{_safe(b['board'])}"
        self.policy.write_run_file(f"{self.run_path}/raw/{stem}.body", body)
        meta = {"step": step, "attempt": attempt, "system": b["system"], "board": b["board"],
                "company": b.get("company") or b["board"], "url": b["url"], "http_status": status,
                "file": f"{stem}.body", "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "fetched_at": self.now(), "mode": self.mode}
        self.policy.write_run_file(f"{self.run_path}/raw/{stem}.meta.json",
                                   (json.dumps(meta, indent=2) + "\n").encode("utf-8"))

    # --- configuration ----------------------------------------------------------------------
    def _validate(self):
        for name, value in self.budgets.items():
            if name not in DEFAULT_BUDGETS:
                raise ConfigError(f"unknown budget {name!r}")
            if type(value) is not int or value < 1:
                raise ConfigError(f"budget {name} must be a positive integer, got {value!r}")
        if not isinstance(self.boards, list) or not self.boards:
            raise ConfigError("the plan must be a non-empty list of boards")
        for b in self.boards:
            if not isinstance(b, dict) or b.get("system") not in SYSTEMS:
                raise ConfigError(f"board {b!r}: system must be one of {SYSTEMS}")
            if not isinstance(b.get("board"), str) or not b["board"] or not isinstance(b.get("url"), str):
                raise ConfigError(f"board {b!r}: needs a board name and a url")

    def _new_run_id(self):
        day = date.today().isoformat()
        n = 1
        while self.policy.exists(f"runs/{day}-{n}"):
            n += 1
        return f"{day}-{n}"

    # --- one board --------------------------------------------------------------------------
    def _do_board(self, b, entry):
        """Returns the budget name if a budget stopped the run, else None."""
        try:
            host = self.policy.authorize("fetch", b["url"])
        except PolicyRefused as exc:
            self.boards_attempted += 1
            self._fail(entry, "refused")
            self._trace("refuse", b, f"refused: policy ({exc})")
            return None
        parts = urllib.parse.urlsplit(b["url"])
        action = ("GET", host, parts.path, parts.query)
        if action in self.seen_actions:
            self.boards_attempted += 1
            self._fail(entry, "repeat")
            self._trace("refuse", b, "refused: repeat", host=host)
            return None
        self.seen_actions.add(action)

        attempt = 1
        while True:
            block = self._budget_block()
            if block:
                if attempt == 1:
                    entry.update(status="not-attempted", reason=f"budget: {block}")
                else:
                    self._fail(entry, f"budget: {block}")
                self._trace("stop", b, f"budget-exhausted: {block}", host=host)
                return block
            if attempt == 1:
                self.boards_attempted += 1
            kind = "request" if attempt == 1 else "retry"
            self._count_request(kind)
            timeout = max(0.1, min(REQUEST_TIMEOUT, self.budgets["seconds"] - self._seconds()))
            status = body = None
            transient = None
            try:
                status, body = self.client(b["url"], timeout)
            except providers.Transient as exc:
                transient = exc.reason
            except NotInReplay:
                self._fail(entry, "not-in-replay")
                self._trace("fetch" if attempt == 1 else "retry", b, "failed: not-in-replay (no retry)", host=host)
                return None
            except PolicyRefused as exc:  # a redirect to a host off the list
                self._fail(entry, "refused")
                self._trace("fetch" if attempt == 1 else "retry", b, f"refused: redirect ({exc})", host=host)
                return None
            step = len(self.trace) + 1
            if body is not None:
                self._save_raw(step, b, status, body, attempt)
            name = "fetch" if attempt == 1 else "retry"

            if transient or (status is not None and 500 <= status <= 599):
                reason = transient or "server-error"
                if attempt == 1:
                    self._trace(name, b, f"{reason}: retry once in {RETRY_DELAY}s", host, status, body)
                    self.sleep(RETRY_DELAY)
                    attempt = 2
                    continue
                self._fail(entry, reason, status)
                self._trace(name, b, f"failed: {reason} after one retry; escalated", host, status, body)
                return None
            if status in (404, 410):
                self._fail(entry, "not-found", status)
                self._trace(name, b, f"failed: not-found (HTTP {status}, no retry); escalated", host, status, body)
                return None
            if status != 200:
                self._fail(entry, f"http-{status}", status)
                self._trace(name, b, f"failed: HTTP {status} (no retry); escalated", host, status, body)
                return None
            try:
                postings = providers.parse(b["system"], b["board"], body)
            except providers.BadResponse as exc:
                self._fail(entry, "bad-response", status)
                self._trace(name, b, f"failed: bad-response ({exc}; no retry)", host, status, body)
                return None
            if not postings:
                # Not a clean result: no new ids (unknown, not []), nothing merged into state.
                entry.update(status="unverified-empty", reason="empty-200", http_status=status, postings=0,
                             new_ids=None, baseline=None)
                self._trace(name, b, "unverified-empty: HTTP 200 with 0 postings (not a clean result); escalated",
                            host, status, body)
                return None
            entry.update(status="parsed", reason=None, http_status=status, postings=len(postings))
            entry["_postings"] = postings
            self._trace(name, b, f"parsed: {len(postings)} postings", host, status, body)
            return None

    # --- the run ------------------------------------------------------------------------------
    def run(self):
        self.started = self.clock()
        self.trace, self.entries, self.seen_actions = [], [], set()
        self.requests = self.boards_attempted = 0
        self.run_id = self._new_run_id()
        self.run_path = f"runs/{self.run_id}"
        report = {"run": self.run_id, "mode": self.mode, "profile": self.profile, "started_at": self.now(),
                  "budgets": self.budgets, "exit": None, "error": None}
        try:
            self._validate()
        except ConfigError as exc:
            return self._write_error(report, f"bad configuration: {exc}")

        try:
            stopped = None
            for b in self.boards:
                entry = {"system": b["system"], "board": b["board"], "company": b.get("company") or b["board"],
                         "url": b["url"], "status": "not-attempted", "reason": None, "http_status": None,
                         "postings": None, "new_ids": None, "baseline": None}
                self.entries.append(entry)
                if stopped:
                    entry["reason"] = f"budget: {stopped}"
                    continue
                if self.boards_attempted >= self.budgets["boards"]:
                    stopped = "boards"
                    entry["reason"] = "budget: boards"
                    self._trace("stop", b, "budget-exhausted: boards")
                    continue
                stopped = self._do_board(b, entry)

            state = self.policy.read_state(STATE)
            seen, boards_seen = set(state["seen_ids"]), set(state["boards"])
            new_postings, all_ids, parsed_boards = [], [], []
            for entry in self.entries:
                postings = entry.pop("_postings", None)
                if entry["status"] != "parsed":
                    continue
                bkey = f"{entry['system']}:{entry['board']}"
                ids = [p["id"] for p in postings]
                all_ids += ids
                parsed_boards.append(bkey)
                if bkey not in boards_seen:
                    entry["baseline"], entry["new_ids"] = True, []
                else:
                    entry["baseline"] = False
                    entry["new_ids"] = sorted(set(ids) - seen)
                    new_postings += [p for p in postings if p["id"] in set(entry["new_ids"])]

            report["rule_verdicts"] = self.judge(new_postings) if new_postings else []
            report["claude"] = self._claude(new_postings)
            report.update(self._summary(stopped))
            self._write_report(report)
            # The state moves only after the report is written, and only for parsed boards.
            self.policy.update_state(STATE, all_ids, boards=parsed_boards)
            return report
        except Exception as exc:  # unexpected: exit error, nothing written to state
            return self._write_error(report, f"{exc.__class__.__name__}: {exc}")

    def _summary(self, stopped):
        return {
            "exit": self.exit_status(bool(stopped)),
            "stopped_by": stopped,
            "boards": self.entries,
            "not_attempted": [f"{e['system']}:{e['board']}" for e in self.entries if e["status"] == "not-attempted"],
            "failed": [f"{e['system']}:{e['board']}" for e in self.entries if e["status"] == "failed"],
            "unverified_empty": [f"{e['system']}:{e['board']}" for e in self.entries
                                 if e["status"] == "unverified-empty"],
            "new_ids": {f"{e['system']}:{e['board']}": e["new_ids"] for e in self.entries},
            "used": {"requests": self.requests, "boards": self.boards_attempted, "seconds": self._seconds()},
            "trace": self.trace,
        }

    def _claude(self, new_postings):
        if not self.claude:
            return {"status": "not requested", "judgments": []}
        from agent import claude_judge, validator
        from agent.resume import load_resume
        from agent.run import load_prompt
        resume = load_resume(ROOT / "data" / "resume.example.json")
        template, prompt = load_prompt("revision-1")  # JS1's frozen prompt and its schema
        judgments = []
        for p in new_postings:
            raw_id = p["id"].rsplit(":", 1)[1]
            if p["system"] != "greenhouse":
                judgments.append({"posting_id": p["id"], "label": "judgment", "status": "not run",
                                  "reason": "the JS1 validator requires an integer posting_id; Ashby ids are strings"})
                continue
            out_dir = self.policy.authorize("write_run_file", f"{self.run_path}/claude/{_safe(p['board'])}")
            view = dict(providers.judge_view(p), id=int(raw_id))
            outcome = claude_judge.judge(view, resume, out_dir, template=template)
            entry = {"posting_id": p["id"], "label": "judgment", "status": outcome["status"]}
            if outcome["status"] != "ran":
                entry["reason"] = outcome["reason"]
            else:
                entry["meta"] = outcome["meta"]
                entry["raw_result"] = outcome["result"]
                entry["validator_errors"] = validator.validate(outcome["result"], resume, {int(raw_id)},
                                                               schema=prompt["schema"])
            judgments.append(entry)
        return {"status": "ran" if any(j["status"] == "ran" for j in judgments) else "not run",
                "prompt": prompt, "judgments": judgments}

    def _write_report(self, report):
        lines = "".join(json.dumps(t) + "\n" for t in self.trace)
        self.policy.write_run_file(f"{self.run_path}/trace.jsonl", lines.encode("utf-8"))
        self.policy.write_run_file(f"{self.run_path}/report.json",
                                   (json.dumps(report, indent=2) + "\n").encode("utf-8"))
        self.policy.write_run_file(f"{self.run_path}/report.md", render_markdown(report).encode("utf-8"))

    def _write_error(self, report, message):
        report.update(self._summary(None), exit="error", error=message)
        for e in report["boards"]:
            e.pop("_postings", None)
        try:
            self._write_report(report)
        except Exception as exc:  # the report itself could not be written; say so, write nothing else
            report["error"] += f"; report not written: {exc}"
        return report


def render_markdown(report):
    used, budgets = report["used"], report["budgets"]
    lines = [f"# Run {report['run']}", "",
             f"- Exit (controller status): **{report['exit']}**"
             + (f" — stopped by the {report['stopped_by']} budget" if report.get("stopped_by") else ""),
             f"- Mode: {report['mode']}; profile: {report['profile']}; started (UTC): {report['started_at']}",
             f"- Used: {used['requests']}/{budgets['requests']} requests, {used['boards']}/{budgets['boards']} boards, "
             f"{used['seconds']}/{budgets['seconds']} s",
             "- `finished` only means every planned board returned a parsed response within budget. "
             f"It is not the outcome check: run `python -m agent2.check out/runs/{report['run']}`.", ""]
    if report.get("error"):
        lines += [f"**Error:** {report['error']}. Nothing was written to state.", ""]
    lines += ["## Boards", ""]
    for e in report["boards"]:
        name = f"{e['system']}:{e['board']}"
        if e["status"] == "parsed":
            new = "baseline (ids saved; none reported as new)" if e["baseline"] else f"{len(e['new_ids'])} new"
            lines.append(f"- `{name}` — parsed, HTTP {e['http_status']}, {e['postings']} postings, {new}")
        elif e["status"] == "failed":
            code = f", HTTP {e['http_status']}" if e["http_status"] else ""
            lines.append(f"- `{name}` — failed: {e['reason']}{code}. New postings: unknown (no value invented). "
                         "Escalated to me.")
        elif e["status"] == "unverified-empty":
            lines.append(f"- `{name}` — unverified-empty: HTTP {e['http_status']} with an empty jobs list. "
                         "Not a clean result; new postings: unknown, ids not saved. Escalated to me.")
        else:
            lines.append(f"- `{name}` — not attempted ({e['reason'] or 'run ended before it'})")
    lines += ["", "## New postings, rule verdicts [record]", ""]
    verdicts = report.get("rule_verdicts") or []
    if not verdicts:
        lines.append("None.")
    for v in verdicts:
        lines.append(f"- **{v['posting_id']}** {v['title']}: `{v['verdict']}` [record]. {v['justification']}")
    claude = report.get("claude") or {"status": "not requested", "judgments": []}
    lines += ["", "## Claude judge [judgment]", "", f"Status: {claude['status']}."]
    for j in claude["judgments"]:
        lines.append(f"- {j['posting_id']}: {j['status']}" + (f" ({j['reason']})" if j.get("reason") else ""))
    lines += ["", "## Trace", "", "| step | action | board | HTTP | bytes | decision | requests | seconds |",
              "|---:|---|---|---:|---:|---|---:|---:|"]
    for t in report["trace"]:
        lines.append(f"| {t['step']} | {t['action']} | {t['system']}:{t['board']} | {t['http_status'] or ''} | "
                     f"{'' if t['bytes'] is None else t['bytes']} | {t['decision']} | {t['requests_used']} | "
                     f"{t['seconds_used']} |")
    return "\n".join(lines) + "\n"


class ReplayClient:
    """Serves the responses a saved run recorded, in step order, with no network."""

    def __init__(self, run_dir):
        self.queues = {}
        for meta_path in sorted(Path(run_dir, "raw").glob("*.meta.json")):
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            body = (meta_path.parent / meta["file"]).read_bytes()
            if hashlib.sha256(body).hexdigest() != meta["sha256"]:
                raise ValueError(f"{meta['file']}: sha256 does not match its record")
            self.queues.setdefault(meta["url"], []).append((meta["http_status"], body))

    def __call__(self, url, timeout=None):
        queue = self.queues.get(url)
        if not queue:
            raise NotInReplay(url)
        return queue.pop(0) if len(queue) > 1 else queue[0]


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="python -m agent2.loop", description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--claude", action="store_true", help="also run the optional Claude judge (JS1)")
    parser.add_argument("--replay-dir", type=Path, help="re-run from a saved run folder; no network")
    parser.add_argument("--out", type=Path, default=ROOT / "out", help="the output root (default: out/)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    policy = Policy(args.out)
    client = ReplayClient(args.replay_dir) if args.replay_dir else None
    report = Loop(PROFILES[args.profile], policy, client=client, mode="replay" if args.replay_dir else "live",
                  profile=args.profile, claude=args.claude).run()
    run_dir = (args.out / "runs" / report["run"]).as_posix()
    print(f"{report['run']}: exit {report['exit']}; {report['used']['requests']} requests, "
          f"{report['used']['seconds']} s; report in {run_dir}/report.md")
    print(f"outcome check (separate): python -m agent2.check {run_dir}")
    return report


if __name__ == "__main__":
    sys.exit(0 if main()["exit"] != "error" else 1)
