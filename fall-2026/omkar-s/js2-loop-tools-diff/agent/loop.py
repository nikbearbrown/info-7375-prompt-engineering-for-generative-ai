"""The bounded watch loop (GATE.md sections 1-4).

    python3 -m agent.loop --watchlist config/watchlist.json [--budgets config/budgets.json]
                          [--out runs] [--persona persona/aarav-patel.example.json] [--label NAME]

One run: for each board on the watch list, within budget, fetch it (through the policy), save the
raw response, record an observation in trace.jsonl, diff against that board's state, and apply the
JS1 rule to each new posting. Ends in exactly one exit status: finished | incomplete |
budget_exhausted | error. Only `finished` exits 0.
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import time

from . import ats, persona, policy, rule, store, transport

EXIT_CODES = {"finished": 0, "incomplete": 3, "budget_exhausted": 4, "error": 5}
BUDGET_KEYS = ("max_boards", "max_requests", "max_seconds", "max_retries_per_board",
               "request_timeout_seconds", "max_response_bytes")
BACKOFF_SECONDS = (1, 2)
# Omkar's drop rule (GATE.md change log, 2026-11-10): flag "more than 50% fewer" postings than the
# last run (now < previous * 0.5), but only when the last run had at least 10 postings.
DROP_KEEP_FRACTION = 0.5
DROP_MIN_PREVIOUS = 10
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigError(Exception):
    pass


def _read_json(pol, path):
    d = pol.check_read(path)
    if d["decision"] != policy.ALLOW:
        raise policy.PolicyDenied(d)
    with open(pol._resolve(path), encoding="utf-8") as f:
        return json.load(f)


def load_budgets(pol, path):
    b = _read_json(pol, path)
    for k in BUDGET_KEYS:
        if not isinstance(b.get(k), (int, float)) or isinstance(b.get(k), bool) or b[k] < 0:
            raise ConfigError(f"budgets: {k} must be a non-negative number")
    return b


def load_watchlist(pol, path):
    w = _read_json(pol, path)
    boards = w.get("boards") if isinstance(w, dict) else None
    if not isinstance(boards, list) or not boards:
        raise ConfigError("watchlist: 'boards' must be a non-empty list")
    for b in boards:
        if not isinstance(b, dict) or not isinstance(b.get("ats"), str) or not isinstance(b.get("slug"), str):
            raise ConfigError(f"watchlist: each board needs 'ats' and 'slug' strings, got {b!r}")
    return boards


def classify(resp):
    """-> (outcome, reason). outcome: ok | transient | permanent."""
    if resp.error_kind in ("timeout", "network"):
        return "transient", resp.error_kind
    if resp.error_kind == "too_large":
        return "permanent", "too_large"
    s = resp.status
    if s == 429:
        return "transient", "rate_limited"
    if s is not None and s >= 500:
        return "transient", f"http_{s}"
    if s in (404, 410):
        return "permanent", "not_found"
    if s != 200:
        return "permanent", f"http_{s}"
    return "ok", "http_200"


class Run:
    def __init__(self, base, out, budgets, boards, resume, label=None, get=None, clock=None,
                 sleep=None, now=None, approver=None):
        self.base, self.budgets, self.boards, self.resume = base, budgets, boards, resume
        self.get = get or transport.get
        self.clock = clock or time.monotonic
        self.sleep = sleep or time.sleep
        now = now or _dt.datetime.now(_dt.timezone.utc)
        self.run_id = now.strftime("%Y-%m-%dT%H-%M-%SZ") + (f"-{label}" if label else "")
        self.started_at = now.isoformat(timespec="seconds")
        self.policy = policy.Policy(base, out, approver=approver)
        self.out = self.policy.out
        self.run_dir = os.path.join(self.out, self.run_id)
        n = 1
        while os.path.lexists(self.run_dir):  # two runs in the same second: new folder, never reuse one
            n += 1
            self.run_dir = os.path.join(self.out, f"{self.run_id}-{n}")
        self.run_id = os.path.basename(self.run_dir)
        self.raw_dir = os.path.join(self.run_dir, "raw")
        self.state_dir = os.path.join(self.out, "state")
        self.trace_path = os.path.join(self.run_dir, "trace.jsonl")
        self.store = store.Store(self.policy, on_decision=self._policy_event)
        self.requests_used = 0
        self.boards_attempted = 0
        self.budget_hit = None
        self._pending = []

    # ---- trace -------------------------------------------------------------------------------
    def _rel(self, target):
        """Paths in the trace are relative to the assignment folder (no local user paths)."""
        if isinstance(target, str) and os.path.isabs(target):
            return os.path.relpath(target, self.policy.base)
        return target

    def _policy_event(self, decision):
        ev = {"event": "policy", **decision, "target": self._rel(decision.get("target"))}
        if os.path.realpath(self.trace_path) in self.store.created:
            self.trace(ev)
        else:
            self._pending.append(ev)

    def trace(self, ev):
        ev = {"t": round(self.clock() - self.t0, 3), **ev}
        self.store.append(self.trace_path, json.dumps(ev, sort_keys=True) + "\n")

    # ---- budget ------------------------------------------------------------------------------
    def seconds_left(self):
        return self.budgets["max_seconds"] - (self.clock() - self.t0)

    def budget_blocks_request(self):
        """Checked BEFORE every request (GATE section 2)."""
        if self.requests_used >= self.budgets["max_requests"]:
            return "max_requests"
        if self.seconds_left() <= 0:
            return "max_seconds"
        return None

    # ---- one board -----------------------------------------------------------------------------
    def fetch_board(self, b):
        rec = {"key": ats.board_key(b["ats"], b["slug"]), "ats": b["ats"], "slug": b["slug"],
               "company": b.get("company", ""), "purpose": b.get("purpose", ""), "url": None,
               "status": None, "reason": None, "attempts": [], "postings": None, "new": None,
               "removed": None, "baseline": None, "new_postings": []}
        try:
            rec["url"] = ats.board_url(b["ats"], b["slug"])
        except ats.BadSlug as e:
            rec.update(status="error", reason=f"bad_slug: {e}")
            return rec, None
        retries = int(self.budgets["max_retries_per_board"])
        for attempt in range(1, retries + 2):
            blocked = self.budget_blocks_request()
            if blocked:
                self.budget_hit = self.budget_hit or blocked
                rec.update(status="error", reason=f"budget {blocked} ran out before attempt {attempt}")
                return rec, None
            timeout = max(0.1, min(self.budgets["request_timeout_seconds"], self.seconds_left()))
            # decided (and recorded) here as well as inside transport.get, so the trace shows it
            req_d = policy.check_request("GET", rec["url"], {"User-Agent": transport.USER_AGENT})
            try:
                resp = self.get(rec["url"], timeout, int(self.budgets["max_response_bytes"]))
            except policy.PolicyDenied as e:
                self.trace({"event": "policy", **e.decision, "board": rec["key"]})
                rec.update(status="refused", reason=e.decision["reason"])
                return rec, None
            self.requests_used += 1
            raw_name = f"{b['ats']}-{b['slug'].replace(' ', '_')}-a{attempt}.json"
            self.store.write_new(os.path.join(self.raw_dir, raw_name), resp.body or b"")
            outcome, why = classify(resp)
            parsed = None
            if outcome == "ok":
                try:
                    parsed = ats.parse(b["ats"], resp.body)
                except ats.BadResponse as e:
                    outcome, why = "permanent", f"bad_response: {e}"
                if outcome == "ok" and not parsed:
                    # GATE section 4: a valid but empty board is evidence of nothing (moved board,
                    # wrong slug, or a real lull). Classified BEFORE tracing, so trace and report agree.
                    outcome, why = "empty", "HTTP 200 with zero postings; not reported as 'no new jobs'"
            obs = {"event": "observation", "board": rec["key"], "attempt": attempt, "url": rec["url"],
                   "http_status": resp.status, "error_kind": resp.error_kind, "error": resp.error,
                   "bytes": len(resp.body or b""), "sha256": hashlib.sha256(resp.body or b"").hexdigest(),
                   "elapsed_s": round(resp.elapsed, 3), "raw": f"raw/{raw_name}", "outcome": outcome,
                   "request_policy": req_d["decision"], "request_policy_reason": req_d["reason"],
                   "why": why, "postings_parsed": None if parsed is None else len(parsed),
                   "requests_used": self.requests_used}
            self.trace(obs)
            rec["attempts"].append({k: obs[k] for k in ("attempt", "http_status", "error_kind", "outcome",
                                                         "why", "raw", "bytes", "elapsed_s")})
            if outcome == "empty":
                # Record what was observed (0), claim nothing new, leave the state untouched,
                # and keep the run from reporting `finished`. Not retried: same request, same body.
                rec.update(status="empty_unverified", postings=0, reason=why)
                return rec, None
            if outcome == "ok":
                rec.update(status="ok", reason=why)
                return rec, parsed
            if outcome == "permanent":
                rec.update(status="error", reason=why)
                return rec, None
            # transient
            if attempt > retries:
                rec.update(status="error", reason=f"{why} on all {attempt} attempts")
                return rec, None
            wait = BACKOFF_SECONDS[min(attempt - 1, len(BACKOFF_SECONDS) - 1)]
            if self.seconds_left() <= wait:
                self.budget_hit = self.budget_hit or "max_seconds"
                rec.update(status="error", reason=f"{why}; no time left in max_seconds to retry")
                return rec, None
            self.trace({"event": "retry_wait", "board": rec["key"], "after_attempt": attempt,
                        "wait_s": wait, "why": why})
            self.sleep(wait)
        raise AssertionError("unreachable")

    def diff_and_judge(self, rec, postings):
        safe = rec["key"].replace(":", "-").replace(" ", "_")
        state_path = os.path.join(self.state_dir, f"{safe}.state.json")
        state = None
        if os.path.exists(state_path):
            self._policy_event(self.policy.check_read(state_path))  # the read decision is traced too
            state = _read_json(self.policy, state_path)  # reads go through the policy too
        ids = [p["id"] for p in postings]
        prev = set(state["seen_ids"]) if state else set()
        new = [p for p in postings if p["id"] not in prev] if state else []
        rec.update(postings=len(postings), new=len(new), removed=len(prev - set(ids)) if state else 0,
                   baseline=state is None)
        self.check_drop(rec, state, len(postings))
        for p in new:
            v = rule.judge(p, self.resume)
            rec["new_postings"].append({"id": p["id"], "title": p["title"], "location": p["location"]["name"],
                                        "url": p["absolute_url"], "rule_verdict": v["verdict"],
                                        "justification": v["justification"]})
        state = state or {"board": rec["key"], "seen_ids": [], "runs": []}
        state["seen_ids"] = sorted(prev | set(ids))
        state["runs"].append({"run_id": self.run_id, "postings": len(postings), "new": len(new)})
        self.store.write_state(state_path, state)

    def check_drop(self, rec, state, now):
        """Omkar's drop rule (GATE.md change log, 2026-11-10). A warning only: it never changes
        the board's status or the run's exit."""
        runs = (state or {}).get("runs") or []
        if not runs:
            w = {"code": "no_baseline", "previous": None, "now": now,
                 "message": "first run for this board; no earlier count to compare against"}
        else:
            previous = runs[-1]["postings"]
            if previous < DROP_MIN_PREVIOUS or now >= previous * DROP_KEEP_FRACTION:
                return
            w = {"code": "suspicious_drop", "previous": previous, "now": now,
                 "message": f"postings fell from {previous} to {now} (more than 50% fewer than the last run); "
                            "the board may have moved or broken"}
        rec.setdefault("warnings", []).append(w)
        self.trace(dict({"event": "warning", "board": rec["key"]}, **w))

    # ---- the loop ------------------------------------------------------------------------------
    def execute(self):
        self.t0 = self.clock()
        self.store.makedirs(self.out)
        self.store.makedirs(self.run_dir)
        self.store.makedirs(self.raw_dir)
        self.store.makedirs(self.state_dir)
        self.trace({"event": "run_start", "run_id": self.run_id, "started_at": self.started_at,
                    "budgets": self.budgets, "watchlist": [ats.board_key(b["ats"], b["slug"]) for b in self.boards]})
        for ev in self._pending:
            self.trace(ev)
        self._pending = []
        seen, records = set(), []
        for i, b in enumerate(self.boards):
            key = ats.board_key(b["ats"], b["slug"])
            if key in seen:
                rec = {"key": key, "ats": b["ats"], "slug": b["slug"], "company": b.get("company", ""),
                       "status": "repeat_skipped", "reason": "same action already taken this run (GATE section 3)",
                       "postings": None, "new": None, "attempts": [], "new_postings": []}
                self.trace({"event": "repeat_skipped", "board": key, "index": i})
                records.append(rec)
                continue
            if self.boards_attempted >= self.budgets["max_boards"]:
                self.budget_hit = self.budget_hit or "max_boards"
            blocked = self.budget_hit or self.budget_blocks_request()
            if blocked:
                self.budget_hit = self.budget_hit or blocked
                for rest in self.boards[i:]:
                    records.append({"key": ats.board_key(rest["ats"], rest["slug"]), "ats": rest["ats"],
                                    "slug": rest["slug"], "company": rest.get("company", ""),
                                    "status": "not_attempted", "reason": f"budget {self.budget_hit} exhausted",
                                    "postings": None, "new": None, "attempts": [], "new_postings": []})
                self.trace({"event": "budget_exhausted", "budget": self.budget_hit,
                            "value": self.budgets[self.budget_hit], "requests_used": self.requests_used,
                            "not_attempted": [r["key"] for r in records if r["status"] == "not_attempted"]})
                break
            seen.add(key)
            self.boards_attempted += 1
            rec, postings = self.fetch_board(b)
            if rec["status"] == "ok":
                self.diff_and_judge(rec, postings)
            self.trace({"event": "board_done", "board": key, "status": rec["status"], "reason": rec["reason"],
                        "postings": rec["postings"], "new": rec["new"]})
            records.append(rec)
        return self.finish(records)

    def exit_status(self, records):
        statuses = [r["status"] for r in records]
        if self.budget_hit:
            left = [r["key"] for r in records if r["status"] == "not_attempted"]
            return "budget_exhausted", (f"budget {self.budget_hit} ({self.budgets[self.budget_hit]}) ran out; "
                                        f"not attempted: {', '.join(left) or 'none (ran out during retries)'}")
        attempted = [r for r in records if r["status"] not in ("repeat_skipped", "not_attempted")]
        if attempted and all(r["status"] in ("error", "refused") for r in attempted):
            return "error", "ESCALATE: every board failed; nothing was observed. Omkar must look."
        if all(s == "ok" for s in statuses):
            return "finished", "every board returned postings"
        bad = [f"{r['key']} ({r['status']})" for r in records if r["status"] != "ok"]
        return "incomplete", "no answer from: " + ", ".join(bad)

    def finish(self, records):
        status, why = self.exit_status(records)
        result = {"run_id": self.run_id, "started_at": self.started_at, "source": "live",
                  "exit": {"status": status, "code": EXIT_CODES[status], "why": why},
                  "budgets": self.budgets, "requests_used": self.requests_used,
                  "boards_attempted": self.boards_attempted, "seconds": round(self.clock() - self.t0, 3),
                  "persona": "Aarav Patel (fictional)", "boards": records}
        self.store.write_new(os.path.join(self.run_dir, "report.json"), json.dumps(result, indent=1))
        self.store.write_new(os.path.join(self.run_dir, "report.md"), render(result))
        self.trace({"event": "run_end", "exit": result["exit"], "requests_used": self.requests_used,
                    "seconds": result["seconds"]})
        return result


def _fmt(v):
    return "null" if v is None else str(v)


def render(result):
    ex = result["exit"]
    L = [f"# Run {result['run_id']}: **{ex['status'].upper()}** (exit code {ex['code']})", "",
         f"> {ex['why']}", "",
         f"Requests used {result['requests_used']}/{result['budgets']['max_requests']} · boards attempted "
         f"{result['boards_attempted']}/{result['budgets']['max_boards']} · {result['seconds']} s of "
         f"{result['budgets']['max_seconds']} s · persona {result['persona']}", "",
         "| Board | Status | Why | Postings | New | Removed | Attempts |", "|---|---|---|---:|---:|---:|---:|"]
    for r in result["boards"]:
        new = _fmt(r.get("new")) + (" (baseline)" if r.get("baseline") else "")
        L.append(f"| `{r['key']}` | {r['status']} | {r.get('reason') or ''} | {_fmt(r.get('postings'))} | {new} "
                 f"| {_fmt(r.get('removed'))} | {len(r.get('attempts') or [])} |")
    L.append("")
    failed = [r for r in result["boards"] if r["status"] != "ok"]
    if failed:
        L += ["## Boards with no answer", ""]
        L += [f"- `{r['key']}`: **{r['status']}**, {r.get('reason')}. "
              + ("Postings: 0 observed; new: null (an empty board is not evidence of 'no new jobs')."
                 if r["status"] == "empty_unverified" else
                 f"Postings: {_fmt(r.get('postings'))} (null = not observed; no value invented).")
              for r in failed]
        L.append("")
    warns = [(r, w) for r in result["boards"] for w in r.get("warnings") or []]
    if warns:
        L += ["## Warnings", "", "These do not change the exit code (Omkar's drop rule, GATE.md change log 2026-11-10).", ""]
        L += [f"- `{r['key']}`: **{w['code']}**, {w['message']}." for r, w in warns]
        L.append("")
    news = [(r, p) for r in result["boards"] for p in r.get("new_postings") or []]
    L += ["## New postings since the last run", ""]
    if not news:
        L.append("None among boards that answered.")
    for r, p in news:
        L += [f"### {p['title']} ({r['key']}, `{p['id']}`)", f"<{p['url']}> · {p['location']}", "",
              f"**Record (JS1 rule, recomputable): {p['rule_verdict']}**", ""] + [f"- {j}" for j in p["justification"]] + [""]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--watchlist", default="config/watchlist.json")
    ap.add_argument("--budgets", default="config/budgets.json")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--persona", default="persona/aarav-patel.example.json")
    ap.add_argument("--label", help="suffix for the run folder name")
    ap.add_argument("--base", default=HERE, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    base = os.path.realpath(a.base)
    out = a.out if os.path.isabs(a.out) else os.path.join(base, a.out)
    try:
        pol = policy.Policy(base, out)
        budgets = load_budgets(pol, a.budgets)
        boards = load_watchlist(pol, a.watchlist)
        d = pol.check_read(a.persona)
        if d["decision"] != policy.ALLOW:
            raise policy.PolicyDenied(d)
        resume = persona.load(pol._resolve(a.persona))
        run = Run(base, out, budgets, boards, resume, label=a.label)
        result = run.execute()
    except (ConfigError, persona.RefusedResume, policy.PolicyDenied, ValueError, OSError) as e:
        print(f"EXIT error (code 5): ESCALATE: {e}", file=sys.stderr)
        return EXIT_CODES["error"]
    print(render(result))
    print(f"trace: {os.path.relpath(run.trace_path, base)}")
    return result["exit"]["code"]


if __name__ == "__main__":
    sys.exit(main())
