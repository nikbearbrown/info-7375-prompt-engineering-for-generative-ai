"""The JS2 loop: several boards, bounded by GATE.md's exits, budgets, repeat
rule, error policy and permission policy.

Every request goes through policy.check_host first, every file read through
policy.check_read, and every write through policy.write_evidence or
policy.write_state. Transport, clock and sleep are passed in, so the tests run
offline with SIMULATED responses and a fake clock.

    python3 loop.py     # a live run of the four GATE.md boards (network)
"""
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import socket
import sys
import time
import urllib.error
import urllib.request

import parsers
import persona
import policy as policy_module
import rule

BOARDS = (
    {"name": "databricks", "system": "greenhouse", "slug": "databricks"},
    {"name": "stripe", "system": "greenhouse", "slug": "stripe"},
    {"name": "plaid", "system": "ashby", "slug": "plaid"},
    {"name": "deliberate-bad-name", "system": "greenhouse", "slug": "js2-nonexistent-board-swathi",
     "deliberate_failure": True},
)
URLS = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
        "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}"}
BUDGETS = {"boards": 5, "requests": 15, "seconds": 60}
TIMEOUT_SECONDS = 15
RETRY_WAIT_SECONDS = 2
PERSONA_FILES = (Path("persona") / "priya-nair.resume.example.json",
                 Path("persona") / "priya-nair.targets.json")
USER_AGENT = "js2-job-search-agent (INFO 7375 coursework; read-only)"


class Timeout(Exception):
    """The request did not answer in time (retried once, per GATE.md)."""


class TransportError(Exception):
    """A network failure that is not a timeout (failed, no retry)."""


class _BudgetStop(Exception):
    pass


@dataclass
class RunResult:
    exit: str
    boards: dict
    budgets: dict
    trace: list
    error: str = None
    run_dir: str = None
    run_id: str = None
    extra: dict = field(default_factory=dict)


def board_url(board, urls=URLS):
    return urls[board["system"]].format(slug=board["slug"])


def _empty_board(board, status, reason=None):
    return {"system": board["system"], "status": status, "reason": reason, "attempts": 0,
            "postings": [], "new_ids": [], "new": [], "baseline": None}


def _load_state(pol):
    path = pol.check_read(policy_module.STATE_FILE)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    boards = data.get("boards") if isinstance(data, dict) else None
    if not isinstance(boards, dict) or not all(
            isinstance(ids, list) and all(isinstance(i, str) for i in ids) for ids in boards.values()):
        raise ValueError("state file must be {\"boards\": {name: [id strings]}}")
    return boards


def run_loop(boards=BOARDS, budgets=BUDGETS, *, policy, transport, clock, sleep, urls=URLS, run_id=None):
    start = clock()
    trace = []
    results = {}
    used = {"boards_used": 0, "requests_used": 0, "seconds_used": 0.0, "exhausted": None}
    run_id = run_id or datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S-%f%z")
    run_rel = Path(policy_module.EVIDENCE_DIR) / run_id
    own_run_dir = False

    def elapsed():
        return clock() - start

    def observe(board, action, **fields):
        obs = {"seq": len(trace) + 1, "t": round(elapsed(), 6), "board": board, "action": action}
        obs.update(fields)
        trace.append(obs)
        return obs

    def budget_check(board_name):
        if used["requests_used"] >= budgets["requests"]:
            used["exhausted"] = "requests"
        elif budgets["seconds"] - elapsed() <= 0:
            used["exhausted"] = "seconds"
        if used["exhausted"]:
            observe(board_name, "budget stop", outcome=f"{used['exhausted']} budget exhausted")
            raise _BudgetStop()

    try:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id):
            raise ValueError(f"run id {run_id!r} is not a plain folder name")
        if policy.check_write(run_rel).exists():
            raise ValueError(f"{run_rel.as_posix()} already exists; evidence is never overwritten")
        own_run_dir = True
        resume_path, targets_path = (policy.check_read(p) for p in PERSONA_FILES)
        _, targets = persona.load_persona(resume_path, targets_path)
        previous = _load_state(policy)

        seen_urls = set()
        new_state = dict(previous)
        for board in boards:
            name = board["name"]
            if used["exhausted"]:
                results[name] = _empty_board(board, "not tried", f"{used['exhausted']} budget exhausted")
                continue
            url = board_url(board, urls)
            if url in seen_urls:
                observe(name, "skipped repeat", url=url, outcome="same URL already requested this run")
                results[name] = _empty_board(board, "skipped repeat", f"{url} already requested this run")
                continue
            try:
                policy.check_host(url)
            except policy_module.PolicyRefused as refused:
                observe(name, "refused by policy", url=url, outcome=str(refused))
                results[name] = _empty_board(board, "failed", f"refused by policy: {refused}")
                continue
            if used["boards_used"] >= budgets["boards"]:
                used["exhausted"] = "boards"
                observe(name, "budget stop", url=url, outcome="boards budget exhausted")
                results[name] = _empty_board(board, "not tried", "boards budget exhausted")
                continue
            try:
                budget_check(name)
            except _BudgetStop:
                results[name] = _empty_board(board, "not tried", f"{used['exhausted']} budget exhausted")
                continue
            used["boards_used"] += 1
            seen_urls.add(url)
            record = _empty_board(board, "failed")
            results[name] = record

            for attempt in (1, 2):
                if attempt == 2:
                    try:
                        budget_check(name)
                        sleep(RETRY_WAIT_SECONDS)
                        budget_check(name)
                    except _BudgetStop:
                        record["reason"] += f"; retry not sent ({used['exhausted']} budget exhausted)"
                        break
                timeout = min(TIMEOUT_SECONDS, budgets["seconds"] - elapsed())
                action = "request" if attempt == 1 else "retry"
                sent_at = round(elapsed(), 6)
                used["requests_used"] += 1
                record["attempts"] = attempt
                obs = {"seq": len(trace) + 1, "t": sent_at, "board": name, "action": action, "url": url,
                       "timeout": timeout, "status": None, "bytes": None, "sha256": None,
                       "raw_file": None, "outcome": None}
                trace.append(obs)
                try:
                    status, body = transport(url, timeout)
                except Timeout as exc:
                    obs.update(status="timeout", outcome=f"timeout: {exc}")
                    record["reason"] = "timeout"
                    continue
                except policy_module.PolicyRefused as refused:
                    obs.update(status="refused", outcome=str(refused))
                    record["reason"] = f"refused by policy: {refused}"
                    break
                except TransportError as exc:
                    obs.update(status="network error", outcome=str(exc))
                    record["reason"] = f"network error: {exc}"
                    break
                body = body or b""
                raw_rel = run_rel / f"{obs['seq']:03d}-{re.sub(r'[^A-Za-z0-9._-]', '_', name)}-{action}.json"
                policy.write_evidence(raw_rel, body)
                obs.update(status=status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                           raw_file=raw_rel.as_posix())
                if status == 404:
                    obs["outcome"] = record["reason"] = "HTTP 404 (board not found): no retry"
                    break
                if 500 <= status <= 599:
                    obs["outcome"] = record["reason"] = f"HTTP {status} (server error)"
                    continue
                if status != 200:
                    obs["outcome"] = record["reason"] = f"HTTP {status}: failed, no retry"
                    break
                if not body.strip():
                    obs["outcome"] = "empty body"
                    record.update(status="empty, unverified", reason="200 with no body")
                    break
                try:
                    postings, unlisted = parsers.PARSERS[board["system"]](body)
                except parsers.ParseError as exc:
                    obs["outcome"] = record["reason"] = f"parse failed: {exc}"
                    break
                observe(name, "parsed", postings=len(postings), unlisted_skipped=unlisted)
                if not postings:
                    obs["outcome"] = "0 postings"
                    record.update(status="empty, unverified", reason="200 with 0 postings")
                    break
                obs["outcome"] = f"{len(postings)} postings"
                baseline = name not in previous
                seen = set(previous.get(name, ()))
                new = [] if baseline else [p for p in postings if p["id"] not in seen]
                for posting in new:
                    posting["judgment"] = rule.judge(posting["title"], posting["location"], targets)
                record.update(status="ok", reason=None, postings=postings, baseline=baseline,
                              new_ids=[p["id"] for p in new], new=new)
                new_state[name] = sorted(p["id"] for p in postings)
                break

        if new_state != previous:
            policy.write_state(json.dumps({"boards": new_state}, indent=2, sort_keys=True).encode())
            observe(None, "state updated", outcome="boards ok this run: " + ", ".join(
                n for n, r in results.items() if r["status"] == "ok"))
        else:
            observe(None, "state left unchanged", outcome="no board was ok with changed ids")

        if used["exhausted"]:
            exit_status = "budget-exhausted"
        elif all(r["status"] == "ok" for r in results.values()):
            exit_status = "finished"
        else:
            exit_status = "incomplete"
        error = None
    except Exception as exc:  # the agent itself broke: GATE.md exit "error"
        exit_status, error = "error", f"{type(exc).__name__}: {exc}"
        observe(None, "error", outcome=error)

    used["seconds_used"] = round(elapsed(), 6)
    result = RunResult(exit=exit_status, boards=results, budgets=used, trace=trace, error=error,
                       run_dir=run_rel.as_posix() if own_run_dir else None, run_id=run_id)
    if own_run_dir:
        summary = {name: {k: v for k, v in r.items() if k != "postings"} | {"postings_count": len(r["postings"])}
                   for name, r in results.items()}
        saved = {"run_id": run_id, "exit": exit_status, "error": error, "budgets": used,
                 "boards": summary, "trace": trace}
        try:
            policy.write_evidence(run_rel / "trace.json", json.dumps(saved, indent=2).encode())
        except Exception as exc:
            if result.exit != "error":
                result.exit, result.error = "error", f"trace not saved: {type(exc).__name__}: {exc}"
    return result


def live_transport(pol):
    """urllib transport: host checked before sending, every redirect checked."""
    opener = urllib.request.build_opener(pol.redirect_handler())

    def transport(url, timeout):
        pol.check_host(url)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except (socket.timeout, TimeoutError) as exc:
            raise Timeout(str(exc)) from None
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                raise Timeout(str(exc.reason)) from None
            raise TransportError(str(exc.reason)) from None

    return transport


def print_summary(result, out=sys.stdout):
    print(f"exit: {result.exit}" + ("" if result.exit == "finished" else "  (escalated to Swathi)"), file=out)
    if result.error:
        print(f"error: {result.error}", file=out)
    b = result.budgets
    print(f"budgets used: {b['boards_used']} boards, {b['requests_used']} requests, "
          f"{b['seconds_used']:.1f} s" + (f"; {b['exhausted']} budget exhausted" if b["exhausted"] else ""), file=out)
    for name, r in result.boards.items():
        line = f"- {name}: {r['status']}"
        if r["status"] == "ok":
            line += " (baseline, 0 new)" if r["baseline"] else f", {len(r['new'])} new"
        if r["reason"]:
            line += f" ({r['reason']})"
        print(line, file=out)
        for p in r["new"]:
            print(f"    {p['id']} {p['title']} | {p['location']} -> {p['judgment']['verdict']} "
                  f"({p['judgment']['source']})", file=out)
    if result.run_dir:
        print(f"evidence: {result.run_dir}/", file=out)


def main(argv=None):
    pol = policy_module.Policy(Path(__file__).resolve().parent)
    result = run_loop(BOARDS, BUDGETS, policy=pol, transport=live_transport(pol),
                      clock=time.monotonic, sleep=time.sleep)
    print_summary(result)
    return 0 if result.exit == "finished" else 1


if __name__ == "__main__":
    sys.exit(main())
