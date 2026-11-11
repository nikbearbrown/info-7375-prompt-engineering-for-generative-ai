"""The bounded loop (GATE.md sections 1-4). One pass over the board list; it never invents a value for a failed board."""
import json
from dataclasses import dataclass, asdict
from watcher.fetch import FetchTimeout, FetchError
from watcher.policy import Blocked

@dataclass
class Budget:                 # GATE 2: my numbers. Only I change them, before a run, by a written decision.
    boards: int = 5
    requests: int = 15
    seconds: float = 60.0
    per_request_timeout: float = 20.0

URLS = {"greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
        "lever": "https://api.lever.co/v0/postings/{slug}?mode=json"}

def board_key(b): return f"{b['ats']}:{b['slug']}"

def parse_jobs(ats, body):
    """Return a list of (id, title). Raises ValueError if the body is not the shape this ATS returns."""
    data = json.loads(body)
    if ats == "greenhouse":
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list): raise ValueError("no 'jobs' list")
        return [(str(j["id"]), j.get("title", "")) for j in data["jobs"]]
    if ats == "lever":
        if not isinstance(data, list): raise ValueError("Lever response is not a list")
        return [(str(j["id"]), j.get("text", "")) for j in data]
    raise ValueError(f"unknown ATS {ats}")

def run(boards, fetch, budget=None, clock=None, seen=None, on_raw=None):
    budget = budget or Budget(); seen = seen or {}
    import time; clock = clock or time.monotonic
    t0 = clock(); used = 0; notes = []; observations = []; results = []; limit_hit = None

    def time_left(): return budget.seconds - (clock() - t0)
    def can_request():
        nonlocal limit_hit
        if used >= budget.requests: limit_hit = limit_hit or "requests"; return False
        if time_left() <= 0: limit_hit = limit_hit or "seconds"; return False
        return True

    # GATE 3: duplicates are skipped and noted, before anything is fetched
    order, keys = [], set()
    for b in boards:
        k = board_key(b)
        if k in keys: notes.append(f"duplicate board {k} skipped (listed more than once)"); continue
        keys.add(k); order.append(b)

    for i, b in enumerate(order):
        k = board_key(b); rec = {"board": k, "status": None, "jobs": None, "new": None, "baseline": None, "error": "", "attempts": []}
        results.append(rec)
        if i >= budget.boards:                                   # GATE 2: at most 5 distinct boards
            limit_hit = limit_hit or "boards"; rec["status"] = "not-reached"; continue
        if limit_hit or not can_request():
            rec["status"] = "not-reached"; continue
        url = URLS[b["ats"]].format(slug=b["slug"])
        for attempt in (1, 2):                                   # GATE 4: at most one retry
            if attempt == 2 and not can_request():
                rec["error"] += "; retry not made: no budget left"; break
            used += 1; t = round(clock() - t0, 3)
            obs = {"t": t, "board": k, "url": url, "attempt": attempt, "outcome": None, "http_status": None, "n_jobs": None, "bytes": None}
            observations.append(obs)
            try:
                r = fetch(k, url, max(1.0, min(budget.per_request_timeout, time_left())))
            except FetchTimeout as e:
                obs["outcome"] = "timeout"; rec["status"] = "failed"; rec["error"] = f"timeout ({e})"; rec["attempts"].append(obs)
                continue                                             # retry once (temporary glitch)
            except Blocked as e:
                obs["outcome"] = "blocked"; rec["status"] = "failed"; rec["error"] = f"blocked by policy: {e}"; rec["attempts"].append(obs)
                break                                                # a policy refusal is never retried
            except FetchError as e:
                obs["outcome"] = "network-error"; rec["status"] = "failed"; rec["error"] = f"network error: {e}"; rec["attempts"].append(obs)
                break
            obs["http_status"] = r.status; obs["bytes"] = len(r.body); rec["attempts"].append(obs)
            if on_raw: obs["raw_file"] = on_raw(k, attempt, r)
            if r.status == 404:                                      # GATE 4: wrong board name -> report, move on, no retry
                obs["outcome"] = "not-found"; rec["status"] = "failed"; rec["error"] = "HTTP 404: board name not found"; break
            if r.status != 200:
                obs["outcome"] = f"http-{r.status}"; rec["status"] = "failed"; rec["error"] = f"HTTP {r.status}"; break
            if not r.body.strip():                                   # GATE 4: blank body -> retry once
                obs["outcome"] = "blank-body"; rec["status"] = "failed"; rec["error"] = "blank body"; continue
            try:
                jobs = parse_jobs(b["ats"], r.body)
            except (ValueError, KeyError, TypeError) as e:
                obs["outcome"] = "bad-json"; rec["status"] = "failed"; rec["error"] = f"unreadable response: {e}"; break
            obs["outcome"] = "ok"; obs["n_jobs"] = len(jobs)          # GATE 4: a valid empty list is a successful check
            rec.update(status="ok", jobs=len(jobs), error="", all_ids=[j[0] for j in jobs])
            if k not in seen:
                rec["baseline"] = True; rec["new"] = []
            else:
                rec["baseline"] = False; rec["new"] = [{"id": i_, "title": t_} for i_, t_ in jobs if i_ not in seen[k]]
            break

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "failed"]
    left = [r for r in results if r["status"] == "not-reached"]
    if not order:
        exit_, why = "error", "no boards to check: the run could not start"
    elif limit_hit and (left or any("retry not made" in r["error"] for r in failed)):
        exit_, why = "budget-exhausted", f"{limit_hit} limit hit with work left"
    elif not ok:
        exit_, why = "error", "no board was checked successfully"
    elif failed:
        exit_, why = "incomplete", f"{len(failed)} board(s) failed"
    else:
        exit_, why = "finished", "every board was checked"
    return {"exit": exit_, "why": why, "limit_hit": limit_hit, "budget": asdict(budget),
            "used": {"requests": used, "seconds": round(clock() - t0, 3), "boards": min(len(order), budget.boards)},
            "boards_checked": len(ok), "new_count": sum(len(r["new"] or []) for r in ok),
            "boards": results, "observations": observations, "notes": notes,
            "new_jobs": [dict(j, board=r["board"]) for r in ok for j in (r["new"] or [])]}
