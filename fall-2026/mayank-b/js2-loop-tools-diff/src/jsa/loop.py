"""The bounded loop (GATE.md §1–§4). Policy = the plan (a list of boards); controller = run().

The controller proposes nothing itself: it walks the plan, checks budgets *before* acting,
applies the repeat rule, sends one GET per attempt, records every observation, and stops
with exactly one exit status. It never decides that an answer is right.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field

from . import boards, policy, rule
from .net import NetError, Timeout

EXITS = ("finished", "incomplete", "budget-exhausted", "error")


class RunError(Exception):
    """A run-level fault (GATE §1 `error`): stop, touch no state."""


# ---- the rules, one small function each (wrong_versions.py swaps these) -------------------

def repeat_key(ats: str, slug: str) -> str:
    return boards.board_key(ats, slug)


def classify_response(ats: str, status: int, body: bytes):
    """-> (kind, jobs). kind: ok | http-4xx | http-5xx | malformed. Never turns a failure into []."""
    if status == 200:
        try:
            return "ok", boards.parse(ats, body)
        except boards.Malformed as e:
            return "malformed", str(e)
    if 500 <= status < 600:
        return "http-5xx", f"HTTP {status}"
    return "http-4xx", f"HTTP {status}"


def should_retry(kind: str) -> bool:
    """Retry once only for transient failures (GATE §4)."""
    return kind in ("timeout", "network", "http-5xx")


def final_status(planned: int, attempted: int, skipped_repeats: int, budget_hit: str | None) -> str:
    if budget_hit and attempted + skipped_repeats < planned:
        return "budget-exhausted"
    if skipped_repeats:
        return "incomplete"
    return "finished"


def merge_seen(old_ids: list[str] | None, result: dict) -> list[str] | None:
    """Proposed seen-ids for one board. A failed board keeps exactly what it had (W9)."""
    if result["result"] != "ok":
        return old_ids
    return sorted(set(old_ids or []) | set(result["ids"]))


# ---- the controller ---------------------------------------------------------------------

@dataclass
class Budget:
    max_boards: int
    max_requests: int
    max_seconds: float
    request_timeout_seconds: float

    @classmethod
    def load(cls, d: dict) -> "Budget":
        try:
            b = cls(**{k: d[k] for k in ("max_boards", "max_requests", "max_seconds", "request_timeout_seconds")})
        except (KeyError, TypeError) as e:
            raise RunError(f"invalid budget config: {e}") from e
        for k, v in vars(b).items():
            if type(v) not in (int, float) or v <= 0:
                raise RunError(f"invalid budget {k}={v!r}")
        return b


@dataclass
class Run:
    root: str
    run_id: str
    trace: list = field(default_factory=list)
    requests: int = 0

    def log(self, **event):
        event["step"] = len(self.trace) + 1
        self.trace.append(event)

    def write(self, rel: str, text: str):
        policy.write_text(self.root, f"runs/{self.run_id}/{rel}", text, run_id=self.run_id)


RUN_ID_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z(-[a-z0-9-]+)?$")


def validate_plan(plan) -> list[dict]:
    if not isinstance(plan, list) or not plan:
        raise RunError("plan must be a non-empty list")
    for e in plan:
        if not isinstance(e, dict) or e.get("ats") not in boards.ATS or not isinstance(e.get("slug"), str) or not e["slug"].strip():
            raise RunError(f"invalid plan entry {e!r}")
        policy.check_url(boards.board_url(e["ats"], e["slug"]))  # an off-list host stops the run before any request
    return plan


def validate_persona(p: dict) -> dict:
    try:
        email = p["personal"]["email"]
        p["search"]["target_titles"], p["search"]["exclude_titles"], p["personal"]["location"]
    except (KeyError, TypeError) as e:
        raise RunError(f"invalid persona: missing {e}") from e
    if not str(email).endswith("@example.com"):
        raise RunError("persona must be fictional (email @example.com)")
    return p


def run(root: str, run_id: str, plan, budget_cfg: dict, persona: dict, seen: dict, *,
        fetch, clock=time.monotonic) -> dict:
    if not RUN_ID_RE.match(run_id):
        raise RunError(f"invalid run id {run_id!r}")
    budget = Budget.load(budget_cfg)
    plan = validate_plan(plan)
    persona = validate_persona(persona)
    r = Run(root, run_id)
    start = clock()
    done, results, skipped, budget_hit = set(), [], [], None
    attempted = 0
    r.log(event="start", run_id=run_id, planned=len(plan), budget=vars(budget))

    for i, entry in enumerate(plan):
        ats, slug = entry["ats"], entry["slug"]
        key = repeat_key(ats, slug)
        if key in done:
            skipped.append({"ats": ats, "slug": slug, "reason": "repeat", "same_as": key})
            r.log(event="skipped", reason="repeat", board=f"{ats}/{slug}", key=key)
            continue
        if attempted >= budget.max_boards:
            budget_hit = "max_boards"
            r.log(event="budget", cap="max_boards", value=budget.max_boards)
            break
        done.add(key)
        url = boards.board_url(ats, slug)
        res = {"board": key, "ats": ats, "slug": slug, "url": url, "attempts": []}
        kind = detail = None
        attempt = 0
        while True:
            if r.requests >= budget.max_requests:
                budget_hit = "max_requests"
            elif clock() - start >= budget.max_seconds:
                budget_hit = "max_seconds"
            if budget_hit:
                r.log(event="budget", cap=budget_hit, board=key, before_attempt=attempt + 1)
                break
            attempt += 1
            r.requests += 1
            t0 = clock()
            status, body = None, None
            try:
                status, body = fetch(url, budget.request_timeout_seconds)
                kind, detail = classify_response(ats, status, body)
            except Timeout as e:
                kind, detail = "timeout", str(e)
            except NetError as e:
                kind, detail = "network", str(e)
            except policy.PolicyError as e:
                kind, detail = e.reason, str(e)
            obs = {"attempt": attempt, "status": status, "kind": kind, "seconds": round(clock() - t0, 3)}
            if body is not None:
                safe = re.sub(r"[^a-z0-9-]+", "-", key.split("/", 1)[1])
                raw_rel = f"raw/{ats}__{safe}__a{attempt}__{status}.json"
                policy.write_bytes(root, f"runs/{run_id}/{raw_rel}", body, run_id=run_id)
                obs.update(raw=raw_rel, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            if kind == "ok":
                obs["postings"] = len(detail)
            else:
                obs["error"] = detail
            res["attempts"].append(obs)
            r.log(event="observation", board=key, url=url, **obs)
            if kind == "ok":
                break
            if attempt == 1 and should_retry(kind):
                r.log(event="retry", board=key, because=kind)
                continue
            break
        if not res["attempts"]:  # budget hit before the first request: never attempted
            done.discard(key)
            break
        attempted += 1
        if kind == "ok":
            ids = [j["id"] for j in detail]
            old = seen.get(key)
            new = [] if old is None else [j for j in detail if j["id"] not in set(old)]
            relevant = [dict(j, rule=rule.judge(j, persona)) for j in new]
            res.update(result="ok", postings=len(ids), ids=ids, baseline=old is None,
                       new=[{k: j[k] for k in ("id", "title", "location", "url")} for j in new],
                       relevant_new=[{"id": j["id"], "title": j["title"], "rule": j["rule"]} for j in relevant if j["rule"]["verdict"] == "relevant"])
        else:
            res.update(result="error", error_kind=kind, error=detail, postings=None, ids=None)
        results.append(res)

    status = final_status(len(plan), attempted, len(skipped), budget_hit)
    never = [f"{e['ats']}/{e['slug']}" for e in plan
             if repeat_key(e["ats"], e["slug"]) not in done and not any(s["slug"] == e["slug"] and s["ats"] == e["ats"] for s in skipped)]
    needs = [x["board"] for x in results if x["result"] == "error"]
    proposed = {k: v for k, v in seen.items()}
    for x in results:
        merged = merge_seen(seen.get(x["board"]), x)
        if merged is not None:
            proposed[x["board"]] = merged
    summary = {"run_id": run_id, "exit": status, "budget_hit": budget_hit, "requests": r.requests,
               "seconds": round(clock() - start, 3), "boards_attempted": attempted, "skipped": skipped,
               "never_attempted": never, "needs_mayank": needs, "results": results,
               "note": "exit describes how the loop ended, not whether any answer is right (GATE §1)"}
    r.log(event="stop", exit=status, budget_hit=budget_hit, requests=r.requests, needs_mayank=needs)
    r.write("trace.jsonl", "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in r.trace))
    r.write("report.json", json.dumps({k: v for k, v in summary.items()}, indent=1, ensure_ascii=False))
    r.write("proposed-seen-ids.json", json.dumps(proposed, indent=1))
    r.write("report.md", render_report(summary))
    return summary


def render_report(s: dict) -> str:
    lines = [f"NEEDS MAYANK: {', '.join(s['needs_mayank']) if s['needs_mayank'] else 'none from the loop (run checker/check.py next)'}", "",
             f"# Run {s['run_id']}", "",
             f"**Exit: `{s['exit']}`.** This says how the loop ended, not whether any answer is right. "
             "The independent check is `checker/check.py`.", "",
             f"Requests {s['requests']} · seconds {s['seconds']} · boards attempted {s['boards_attempted']} · budget hit: {s['budget_hit'] or 'none'}", "",
             "| Board | Result | Postings | New | Relevant new | Note |", "|---|---|---|---|---|---|"]
    for x in s["results"]:
        if x["result"] == "ok":
            note = "baseline (first time seen: nothing reported as new)" if x["baseline"] else ""
            lines.append(f"| {x['board']} | ok | {x['postings']} | {len(x['new'])} | {len(x['relevant_new'])} | {note} |")
        else:
            lines.append(f"| {x['board']} | **error** | — (not 0) | — | — | {x['error_kind']}: {x['error']}; state left untouched |")
    for k in s["skipped"]:
        lines.append(f"| {k['ats']}/{k['slug']} | skipped | — | — | — | repeat of {k['same_as']}, no request sent |")
    for k in s["never_attempted"]:
        lines.append(f"| {k} | never attempted | — | — | — | budget |")
    return "\n".join(lines) + "\n"
