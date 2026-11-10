#!/usr/bin/env python3
"""Job-Search Agent 2: a bounded loop over several job boards (GATE.md sections 1-4).

usage (from this folder):
  python3 agent.py --config config/live.json
  python3 agent.py --config <file> --replay <folder>   SEEDED: read saved responses, fetch nothing
  python3 agent.py --reset-state greenhouse-anthropic --approve-reset
                                                       remove one board's state (needs approval)

Each run writes its evidence to a new folder runs/run-<UTC time>/: every raw response,
trace.jsonl (every action and observation), summary.json and report.md.
exit codes: 0 finished, 1 incomplete, 2 error, 3 budget-exhausted
Python 3.9 or newer, standard library only.
"""
import argparse
import hashlib
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import policy
import providers
import record

HERE = Path(__file__).resolve().parent
# GATE.md section 2. Only a new dated decision in GATE.md may change these; no config or flag can.
BUDGETS = {"boards": 4, "requests": 6, "seconds": 120.0, "retries_per_board": 1}
PER_REQUEST_TIMEOUT = 30.0
EXIT_CODES = {"finished": 0, "incomplete": 1, "error": 2, "budget-exhausted": 3}
CONFIG_KEYS = {"_comment", "label", "boards"}
USER_AGENT = "js2-loop-tools-diff (INFO 7375 coursework)"


class Temporary(Exception):
    """A timeout or a network failure that may pass: one retry is allowed (GATE.md section 4)."""


class StateError(Exception):
    """A state file that cannot be trusted: the run stops with 'error'."""


def http_get(url, timeout, board=None, pol=None):
    """The agent's one network tool: a policy-checked HTTPS GET that refuses every redirect."""
    policy.check_request("GET", url)
    opener = urllib.request.build_opener(policy.RefuseRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except policy.PolicyViolation:
        raise
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return e.code, body
    except (socket.timeout, TimeoutError) as e:
        raise Temporary(f"timeout after {timeout:.0f} s") from e
    except urllib.error.URLError as e:
        raise Temporary(f"network error: {e.reason}") from e


def replay_get(folder):
    """SEEDED runs: answer from saved files named <ats>-<slug>.json instead of the network.
    The URL is still checked by the policy. A missing file answers 404."""
    def get(url, timeout, board, pol):
        policy.check_request("GET", url)
        path = Path(folder) / f"{board['ats']}-{board['slug']}.json"
        return (200, pol.read_bytes(path)) if path.is_file() else (404, b"")
    return get


def load_config(pol, path):
    cfg = json.loads(pol.read_bytes(path))
    if not isinstance(cfg, dict) or not isinstance(cfg.get("boards"), list) or not cfg["boards"]:
        raise providers.ConfigError("the configuration needs a non-empty 'boards' list")
    extra = set(cfg) - CONFIG_KEYS
    if extra:
        raise providers.ConfigError(f"unknown configuration keys {sorted(extra)}: budgets and permissions cannot be set by a config file")
    for b in cfg["boards"]:
        if not isinstance(b, dict) or set(b) - {"name", "ats", "slug"}:
            raise providers.ConfigError(f"a board needs only name, ats and slug: {b!r}")
        providers.board_url(b.get("ats"), b.get("slug"))
    return cfg


def load_persona(pol, path):
    """The JS1 persona check: a fictional résumé only (@example.com, a 555-01xx phone)."""
    r = json.loads(pol.read_bytes(path))
    personal = r.get("personal") if isinstance(r, dict) else None
    if not isinstance(personal, dict) or not str(personal.get("email", "")).lower().endswith("@example.com") \
            or not re.search(r"55501\d\d$", re.sub(r"\D", "", str(personal.get("phone", "")))):
        raise providers.ConfigError("the résumé is not the fictional persona (@example.com, 555-01xx)")
    return r


def state_path(state_dir, board):
    return Path(state_dir) / f"{board['ats']}-{board['slug']}.state.json"


def load_state(pol, path, board):
    """None means no state yet: this board's run is a baseline. A bad state file is never overwritten."""
    if not Path(path).exists():
        return None
    try:
        s = json.loads(pol.read_bytes(path))
    except (OSError, ValueError) as e:
        raise StateError(f"state file {Path(path).name} is unreadable: {e}") from e
    ok = (isinstance(s, dict) and s.get("board") == board["slug"] and s.get("ats", board["ats"]) == board["ats"]
          and isinstance(s.get("seen_ids"), list)
          and all(type(i) is providers.ID_TYPE[board["ats"]] for i in s["seen_ids"]))
    if not ok:
        raise StateError(f"{Path(path).name} is not a valid state file for {board['ats']}/{board['slug']}")
    return s


def new_result(b):
    return {"name": b.get("name", b["slug"]), "ats": b["ats"], "slug": b["slug"],
            "url": providers.board_url(b["ats"], b["slug"]), "status": None, "error": None,
            "attempts": 0, "raw_files": [], "postings": None, "new": [], "baseline": False}


def fail(res, kind, reason):
    """A board that was not observed. It is never reported as '0 new' (GATE.md Wrong Version 1)."""
    res["status"] = kind
    res["error"] = reason


def decide(fatal, budget_hit, boards):
    """GATE.md section 1, exit decision: error, then budget-exhausted, then incomplete, then finished."""
    if fatal:
        return "error"
    if budget_hit:
        return "budget-exhausted"
    if any(b["status"] != "ok" for b in boards):
        return "incomplete"
    return "finished"


def run(config_path, runs_dir, state_dir, read_dirs, persona_path, get=http_get, clock=time.monotonic,
        now=None, seeded=None):
    now = now or datetime.now(timezone.utc)
    pol = policy.Policy(runs_dir, state_dir, read_dirs)
    run_dir = pol.make_run_dir(f"run-{now.strftime('%Y-%m-%dT%H%M%SZ')}")
    started = clock()
    events, boards, problems = [], [], []
    fatal, budget_hit, requests_used = None, None, 0

    def trace(event, **fields):
        events.append({"t": round(clock() - started, 3), "event": event, **fields})

    trace("start", run=run_dir.name, config=str(config_path), budgets=BUDGETS,
          source=seeded or "live: each listing is fetched from its board's public API")
    cfg = None
    try:
        cfg = load_config(pol, config_path)
        resume = load_persona(pol, persona_path)
        observed = {}
        for i, b in enumerate(cfg["boards"]):
            res = new_result(b)
            boards.append(res)
            if budget_hit or i >= BUDGETS["boards"]:
                budget_hit = budget_hit or "boards"
                res["status"] = "not checked"
                trace("not checked", board=res["name"], reason=f"{budget_hit} budget reached")
                continue
            key = ("GET", res["url"])                      # GATE.md section 3: the repeat rule
            if key in observed:
                earlier = observed[key]
                res.update(status=earlier["status"], error=earlier["error"], postings=earlier["postings"],
                           new=list(earlier["new"]), repeat_of=earlier["name"])
                trace("repeat", board=res["name"], url=res["url"], reused_observation_of=earlier["name"])
                continue
            observed[key] = res
            attempt = 0
            while res["status"] is None:
                elapsed = clock() - started
                if requests_used >= BUDGETS["requests"]:
                    budget_hit = "requests"
                    break
                if elapsed >= BUDGETS["seconds"]:
                    budget_hit = "seconds"
                    break
                attempt += 1
                requests_used += 1
                res["attempts"] = attempt
                trace("request", board=res["name"], method="GET", url=res["url"], attempt=attempt,
                      requests_used=requests_used)
                try:
                    status, body = get(res["url"], min(PER_REQUEST_TIMEOUT, BUDGETS["seconds"] - elapsed), b, pol)
                except Temporary as e:
                    trace("observation", board=res["name"], attempt=attempt, outcome="temporary failure", detail=str(e))
                    if attempt <= BUDGETS["retries_per_board"]:
                        trace("retry", board=res["name"], reason=str(e))
                        continue
                    fail(res, "unavailable", f"{e} (after {attempt} attempts)")
                    break
                raw_name = f"raw-{res['ats']}-{res['slug']}-attempt{attempt}-http{status}.json"
                pol.write_evidence(run_dir / raw_name, body)    # raw first, byte for byte, before parsing
                res["raw_files"].append(raw_name)
                trace("observation", board=res["name"], attempt=attempt, http_status=status, bytes=len(body),
                      sha256=hashlib.sha256(body).hexdigest(), raw_file=raw_name)
                if status == 200:
                    try:
                        postings = providers.parse(res["ats"], body)
                    except providers.ResponseError as e:
                        fail(res, "failed", f"unexpected response: {e}")
                        break
                    observe(pol, res, postings, state_path(state_dir, b), b, resume, now, run_dir.name, trace)
                elif status == 429 or 500 <= status < 600:
                    if attempt <= BUDGETS["retries_per_board"]:
                        trace("retry", board=res["name"], reason=f"HTTP {status}")
                        continue
                    fail(res, "unavailable", f"HTTP {status} (after {attempt} attempts)")
                else:
                    fail(res, "failed", f"HTTP {status}")    # 404 and every other 4xx: never retried
            if res["status"] is None:
                res["status"] = "not checked"
                trace("not checked", board=res["name"], reason=f"{budget_hit} budget reached")
            if res["status"] != "ok":
                problems.append(f"{res['name']}: {res['status']} ({res['error'] or budget_hit + ' budget'})")
    except (policy.PolicyViolation, StateError, providers.ConfigError, OSError, ValueError) as e:
        fatal = f"{type(e).__name__}: {e}"
        problems.append(fatal)
        trace("error", detail=fatal)
        for res in boards:
            if res["status"] is None:
                res["status"] = "stopped by error"
        for b in (cfg["boards"] if cfg else [])[len(boards):]:
            boards.append(new_result(b) | {"status": "not checked"})
    exit_status = decide(fatal, budget_hit, boards)
    elapsed = round(clock() - started, 3)
    trace("exit", status=exit_status, budget_hit=budget_hit, problems=problems)
    summary = {
        "agent": "agent.py", "gate": "GATE.md (2026-11-09)", "run": run_dir.name,
        "started_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": seeded or "live", "config": str(config_path),
        "exit_status": exit_status, "exit_code": EXIT_CODES[exit_status], "budget_hit": budget_hit,
        "problems": problems, "budgets": BUDGETS,
        "used": {"boards": sum(r["status"] != "not checked" for r in boards), "requests": requests_used,
                 "seconds": elapsed},
        "boards": [{k: v for k, v in r.items() if k != "new"} | {"new_count": len(r["new"]) if r["status"] == "ok" else None}
                   for r in boards],
        "new_postings": [dict(p, board=r["name"]) for r in boards if r["status"] == "ok" for p in r["new"]
                         if "repeat_of" not in r],
    }
    pol.write_evidence(run_dir / "trace.jsonl", "".join(json.dumps(e) + "\n" for e in events))
    pol.write_evidence(run_dir / "summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    pol.write_evidence(run_dir / "report.md", report(summary))
    return summary, run_dir


def observe(pol, res, postings, spath, board, resume, now, run_name, trace):
    """A validated response: compare with state, then update state (GATE.md: only after evidence is saved)."""
    state = load_state(pol, spath, board)
    ids = [p["id"] for p in postings]
    res.update(status="ok", postings=len(postings), baseline=state is None)
    if state is not None:
        seen = set(state["seen_ids"])
        res["new"] = [{"id": p["id"], "title": p["title"], "location": p["location"], "url": p["url"],
                       "record": record.record_verdict({"id": p["id"], "title": p["title"], "content": p["content"],
                                                        "location": {"name": p["location"]}}, resume)["verdict"]}
                      for p in postings if p["id"] not in seen]
    seen_after = sorted(set(ids) | (set(state["seen_ids"]) if state else set()), key=str)
    pol.update_state(spath, {"board": board["slug"], "ats": board["ats"], "updated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "last_run": run_name, "seen_ids": seen_after})
    trace("state updated", board=res["name"], postings=len(postings), new=len(res["new"]),
          baseline=res["baseline"], seen_after=len(seen_after))


def report(s):
    lines = [f"# Run {s['run']}: {s['exit_status'].upper()}", "",
             f"- Source: {s['source']}", f"- Configuration: `{s['config']}`",
             f"- Exit: **{s['exit_status']}** (code {s['exit_code']})" + (f", budget reached: {s['budget_hit']}" if s["budget_hit"] else ""),
             f"- Used: {s['used']['boards']} boards, {s['used']['requests']} of {s['budgets']['requests']} requests, "
             f"{s['used']['seconds']} of {s['budgets']['seconds']} s",
             "", "| board | ats | status | attempts | postings | new | detail |", "|---|---|---|---|---|---|---|"]
    for b in s["boards"]:
        new = "baseline" if b["baseline"] else ("-" if b["status"] != "ok" else b["new_count"])
        detail = b["error"] or (f"same request as {b['repeat_of']}" if b.get("repeat_of") else "")
        lines.append(f"| {b['name']} | {b['ats']} | **{b['status']}** | {b['attempts']} | "
                     f"{'-' if b['postings'] is None else b['postings']} | {new} | {detail} |")
    if s["problems"]:
        lines += ["", "Problems:", ""] + [f"- {p}" for p in s["problems"]]
    if s["new_postings"]:
        lines += ["", "New postings (RECORD is my JS1 rule, recomputable; the person decides):", "",
                  "| board | id | title | location | RECORD |", "|---|---|---|---|---|"]
        for p in s["new_postings"]:
            lines.append(f"| {p['board']} | {p['id']} | {p['title']} | {p['location']} | {p['record']} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Watch several job boards in one bounded loop.")
    ap.add_argument("--config", default="config/live.json")
    ap.add_argument("--runs-dir", default=str(HERE / "runs"))
    ap.add_argument("--state-dir", default=str(HERE / "state"))
    ap.add_argument("--persona", default=str(HERE / "persona" / "priya-nair.resume.example.json"))
    ap.add_argument("--replay", help="SEEDED: answer from saved files <ats>-<slug>.json in this folder")
    ap.add_argument("--reset-state", metavar="ATS-SLUG", help="remove one board's state; needs --approve-reset")
    ap.add_argument("--approve-reset", action="store_true", help="my explicit approval for --reset-state")
    a = ap.parse_args(argv)
    if a.reset_state:
        pol = policy.Policy(a.runs_dir, a.state_dir)
        try:
            print(f"reset: {pol.reset_state(Path(a.state_dir) / f'{a.reset_state}.state.json', approved=a.approve_reset)}")
            return 0
        except policy.PolicyViolation as e:
            print(f"REFUSED: {e}", file=sys.stderr)
            return 2
    read_dirs = [HERE / "persona", HERE / "config"]     # GATE.md: its own configuration, the persona
    get, seeded = http_get, None
    if a.replay:
        read_dirs.append(Path(a.replay).resolve())
        get, seeded = replay_get(a.replay), f"SEEDED: responses read from {a.replay}, not fetched"
    s, run_dir = run(a.config, a.runs_dir, a.state_dir, read_dirs, a.persona, get=get, seeded=seeded)
    print(f"{s['exit_status'].upper()}  ({s['used']['requests']} requests, {s['used']['seconds']} s)  evidence: {run_dir}")
    for b in s["boards"]:
        print(f"  {b['name']:24} {b['status']:12} postings={b['postings']}  new={'baseline' if b['baseline'] else ('unknown' if b['new_count'] is None else b['new_count'])}"
              + (f"  ({b['error']})" if b["error"] else ""))
    for p in s["problems"]:
        print(f"  problem: {p}")
    return s["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
