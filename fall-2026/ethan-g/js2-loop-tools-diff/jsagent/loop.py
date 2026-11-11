"""Job-Search Agent 2: a bounded loop over the boards in a board file (GATE.md v2.3).

    python3 -m jsagent.loop --boards config/boards.json --no-claude                       # run A
    python3 -m jsagent.loop --boards config/boards_seeded.json --out evidence/seeded/empty-samsara --no-claude \
        --replay greenhouse:samsara=tests/fixtures/seeded/empty-samsara.json --seeded "constructed empty Samsara"   # run C

Every request and file access goes through jsagent/policy.py. The exit is calculated from the observation records by
compute_exit(). The loop does not judge whether an answer is plausible: scripts/verify_run.py does that, independently.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from . import claude_judge, net, policy, providers, resume, rule

ROOT = policy.ROOT
PERSONA = ROOT / "persona" / "evan-gordon.resume.json"
BASELINES = {"greenhouse:samsara": ROOT / "baseline" / "2026-10-31" / "seen_ids.json"}
EXIT_CODES = {"finished": 0, "incomplete": 1, "budget-exhausted": 2, "error": 3}
BACKOFF_S = (2, 4)
RETRY_AFTER_MAX_S = 10
TRACE_FIELDS = ("action", "board", "url", "decision", "rule", "attempt", "http_status", "raw_path", "raw_sha256", "outcome")


class BudgetExhausted(Exception):
    pass


class NoProgress(Exception):
    pass


class PreflightError(Exception):
    pass


class Budget:
    def __init__(self, cfg, clock=time.monotonic):
        self.cfg, self.clock = cfg, clock
        self.start = clock()
        self.requests = 0
        self.steps = 0

    def elapsed(self):
        return self.clock() - self.start

    def remaining_s(self):
        return self.cfg["max_seconds"] - self.elapsed()

    def check_time(self, need=0.0):
        if self.elapsed() + need > self.cfg["max_seconds"]:
            raise BudgetExhausted(f"time limit of {self.cfg['max_seconds']} s reached")

    def charge_request(self, url=None):
        self.check_time()
        if self.requests >= self.cfg["max_requests"]:
            raise BudgetExhausted(f"request limit of {self.cfg['max_requests']} reached")
        self.requests += 1

    def step(self):
        self.steps += 1
        if self.steps > self.cfg["max_loop_steps"]:
            raise NoProgress(f"more than {self.cfg['max_loop_steps']} loop steps")

    def left(self):
        return {"requests": self.cfg["max_requests"] - self.requests, "seconds": round(self.remaining_s(), 1),
                "steps": self.cfg["max_loop_steps"] - self.steps}


class ActionLog:
    """The repeat rule (GATE.md section 3): one action per method + normalized URL per run; a recorded retry is the only re-send."""

    def __init__(self):
        self.seen = set()

    def allow(self, method, url, retry=False):
        key = (method.upper(), policy.normalize_url(url))
        if key in self.seen and not retry:
            return False
        self.seen.add(key)
        return True


class Trace:
    def __init__(self, files, path, budget):
        rp = files.check_write(path, "create")
        rp.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(rp, "x", encoding="utf-8")
        self.budget = budget

    def write(self, **fields):
        line = {"step": self.budget.steps, "time": datetime.now().astimezone().isoformat(timespec="seconds")}
        line.update({k: None for k in TRACE_FIELDS})
        line.update(fields)
        line["budget_left"] = self.budget.left()
        self.f.write(json.dumps(line) + "\n")
        self.f.flush()

    def close(self):
        self.f.close()


class Ctx:
    pass


def rel(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def classify(resp, attempt):
    """Error policy (GATE.md section 4) -> (verdict, retries allowed or None, wait seconds)."""
    backoff = BACKOFF_S[min(attempt - 1, len(BACKOFF_S) - 1)]
    if resp.status == 200:
        return "ok", None, 0
    if resp.status is None:
        if resp.kind in ("timeout", "connection"):
            return "transient", 2, backoff
        return resp.kind or "failed", None, 0  # tls, redirect_limit: not retried
    if resp.status in (502, 503, 504):
        return "transient", 2, backoff
    if resp.status == 500:
        return "server error", 1, BACKOFF_S[0]
    if resp.status == 429:
        if resp.retry_after is not None and resp.retry_after <= RETRY_AFTER_MAX_S:
            return "rate limited", 1, resp.retry_after
        return "rate limited", None, 0
    return "failed", None, 0


def describe(resp, verdict, attempt):
    if resp.status is None:
        return f"no response received ({resp.error}) after {attempt} attempt(s)"
    if resp.status == 429 and attempt == 1:
        return "HTTP 429 with no short Retry-After: not retried; check this board later by hand"
    if verdict == "failed":
        return f"HTTP {resp.status}: deterministic, not retried"
    return f"HTTP {resp.status} after {attempt} attempt(s)"


def fetch_with_policy(ctx, rec, url, action, raw_stem):
    """One action with its retries. Returns (status, body, failure reason or None, attempts)."""
    attempt = 0
    while True:
        attempt += 1
        ctx.budget.step()
        if not ctx.actions.allow("GET", url, retry=attempt > 1):
            ctx.trace.write(action=action, board=rec["key"], url=policy.normalize_url(url), decision="repeat_blocked",
                            rule="repeat", attempt=attempt, outcome="blocked: this action was already taken in this run")
            return None, None, "repeat_blocked", attempt
        policy.check_url(url, ctx.allow)
        ctx.budget.charge_request(url)
        resp = ctx.fetcher.get(url, timeout=max(0.1, min(ctx.cfg["request_timeout_s"], ctx.budget.remaining_s())))
        raw_rel = sha = None
        if resp.body is not None:  # saved before parsing, so a body that won't parse is still evidence
            name = raw_stem + ("" if attempt == 1 else f"_attempt{attempt}") + ".json"
            rp = policy.write_new(ctx.files, ctx.run_dir / "raw" / name, resp.body)
            raw_rel = rp.relative_to(ctx.run_dir).as_posix()
            sha = hashlib.sha256(resp.body).hexdigest()
            rec["raw_paths"].append(raw_rel)
        verdict, retries, wait = classify(resp, attempt)
        ctx.trace.write(action=action, board=rec["key"], url=policy.normalize_url(url), decision="allowed", rule="network",
                        attempt=attempt, http_status=resp.status, raw_path=raw_rel, raw_sha256=sha, hops=resp.hops,
                        outcome=verdict if resp.error is None else f"{verdict}: {resp.error}")
        if verdict == "ok":
            return resp.status, resp.body, None, attempt
        if retries is None or attempt > retries:
            return resp.status, resp.body, describe(resp, verdict, attempt), attempt
        if ctx.budget.requests >= ctx.cfg["max_requests"]:  # the retry must fit both budgets before we wait for it
            raise BudgetExhausted(f"request limit of {ctx.cfg['max_requests']} reached before a retry of {rec['key']}")
        ctx.budget.check_time(wait)
        ctx.sleep(wait)


def previous_ids(ctx, key):
    """(ids seen before or None, where they came from). State first; the Oct 31 baseline only for a board not yet in state."""
    b = ctx.state["boards"].get(key)
    if b is not None:
        return set(b["seen"]), "state"
    path = ctx.baselines.get(key)
    if path:
        data = json.loads(ctx.files.check_read(path).read_text())
        return {str(x) for x in data["seen_ids"]}, f"baseline {Path(path).parent.name}"
    return None, "none"


def judge_claude(ctx, posting):
    for _ in range(2):  # retried at most once (GATE.md section 4)
        j = claude_judge.judge(posting, ctx.resume, ctx.prompt, model=ctx.model)
        if j.get("status") == "valid":
            return {"status": "valid", "verdict": j.get("verdict"), "reason": j.get("reason")}
    return {"status": j.get("status"), "errors": j.get("errors")}


def observe_board(ctx, entry):
    provider, board, key = entry["provider"], entry["board"], entry["key"]
    rec = {"key": key, "provider": provider, "board": board, "status": "not_observed", "reason": "not attempted",
           "attempts": 0, "http_status": None, "count": None, "baseline": False, "history": None, "new_ids": [],
           "new_judged": [], "new_unjudged": [], "new_other_ids": [], "detail_failures": [], "raw_paths": []}
    ctx.records.append(rec)
    status, body, reason, attempts = fetch_with_policy(ctx, rec, providers.list_url(provider, board), "list",
                                                       f"{provider}_{board}_list")
    rec["attempts"], rec["http_status"] = attempts, status
    if reason:
        rec.update(status="failed", reason=reason)
        return
    try:
        postings = providers.parse_list(provider, body, board)
    except providers.ShapeError as e:
        rec.update(status="failed", reason=f"bad response, not retried: {e}")
        ctx.trace.write(action="parse", board=key, decision="allowed", rule="error_policy", outcome=rec["reason"])
        return
    ids = [p["id"] for p in postings]
    rec.update(status="ok", reason="observed", count=len(postings))
    prev, source = previous_ids(ctx, key)
    if prev is None:
        rec.update(baseline=True, history="none (first observation: baselined, nothing reported as new)")
        ctx.observed[key] = {"ids": ids, "unjudged": set(), "prev": set()}
        return
    rec["history"] = source
    new = [p for p in postings if p["id"] not in prev]
    new_data = [p for p in new if rule.check_r1(p, ctx.resume)["passed"]]
    data_ids = {p["id"] for p in new_data}
    rec["new_ids"] = [p["id"] for p in new]
    rec["new_other_ids"] = [p["id"] for p in new if p["id"] not in data_ids]
    rec["new_unjudged"] = [p["id"] for p in new_data]
    unjudged = set(data_ids)
    ctx.observed[key] = {"ids": ids, "unjudged": unjudged, "prev": prev}  # registered first: a budget stop keeps S3
    for p in new_data:
        full = p
        if providers.needs_detail(provider):
            _, dbody, why, _ = fetch_with_policy(ctx, rec, providers.detail_url(provider, board, p["id"]), "detail",
                                                 f"{provider}_{board}_{p['id']}")
            if why is None:
                try:
                    full = providers.parse_detail(provider, dbody, board)
                except providers.ShapeError as e:
                    why = f"bad detail response: {e}"
            if why:
                rec["detail_failures"].append({"id": p["id"], "reason": why})
                continue
        record = rule.judge(full, ctx.resume)
        item = {"id": p["id"], "title": p["title"], "location": p["location"]["name"], "url": p["absolute_url"],
                "rule_verdict": record["verdict"], "preferred_location": record["preferred_location"],
                "preferred_years": record["preferred_years"], "rule_record": record}
        if ctx.no_claude:
            item["claude"] = "off"
        else:
            item["claude"] = judge_claude(ctx, full)
            if item["claude"]["status"] != "valid":
                ctx.judgment_missing.append(f"{key} {p['id']}: Claude judge {item['claude']['status']}")
        rec["new_judged"].append(item)
        rec["new_unjudged"].remove(p["id"])
        unjudged.discard(p["id"])


def compute_exit(records, budget_reason=None, error_reason=None, approvals_refused=(), judgment_missing=()):
    """The one function that decides the exit (GATE.md section 1), from the observation records. Keeps every reason."""
    reasons = []
    if error_reason:
        reasons.append(f"error: {error_reason}")
    if budget_reason:
        reasons.append(f"budget: {budget_reason}")
    for r in records:
        if r["status"] == "failed":
            reasons.append(f"{r['key']} failed: {r['reason']} (count unknown, not zero)")
        elif r["status"] == "not_observed":
            reasons.append(f"{r['key']} not observed: {r['reason']} (count unknown, not zero)")
        if r.get("new_unjudged"):
            reasons.append(f"{r['key']}: {len(r['new_unjudged'])} new data-titled posting(s) not judged; they stay new")
        for f in r.get("detail_failures") or []:
            reasons.append(f"{r['key']} {f['id']}: detail request failed: {f['reason']}")
    reasons += [f"approval refused: {a}" for a in approvals_refused]
    reasons += [f"judgment missing: {j}" for j in judgment_missing]
    partial = any(r["status"] != "ok" or r.get("new_unjudged") or r.get("detail_failures") for r in records)
    if error_reason:
        status = "error"
    elif budget_reason:
        status = "budget-exhausted"
    elif partial or approvals_refused or judgment_missing:
        status = "incomplete"
    else:
        status = "finished"
    return status, reasons


def preflight(files, boards_path, budgets, resume_path):
    try:
        cfg = budgets if budgets is not None else json.loads(files.check_read(files.root / "config" / "budgets.json").read_text())
        allow = policy.load_allowlist(files.check_read(files.root / "config" / "allowlist.json"))
        data = json.loads(files.check_read(boards_path).read_text())
        r = resume.load_resume(files.check_read(resume_path))
    except (OSError, ValueError, KeyError, resume.ResumeRefused) as e:
        raise PreflightError(f"configuration could not be read: {e}") from None
    entries = data.get("boards") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise PreflightError("the board file lists no boards")
    plan, seen, dups = [], set(), []
    for e in entries:
        if not isinstance(e, dict):
            raise PreflightError(f"bad board entry: {e!r}")
        provider, board = e.get("provider"), e.get("board")
        try:
            url = providers.list_url(provider, board)
        except ValueError as err:
            raise PreflightError(str(err)) from None
        policy.check_url(url, allow)
        key = f"{provider}:{board.lower()}"
        if key in seen:
            dups.append(key)
            continue
        seen.add(key)
        plan.append({"provider": provider, "board": board, "key": key})
    if len(plan) > cfg["max_boards"]:
        raise PreflightError(f"{len(plan)} boards is more than the board cap of {cfg['max_boards']}")
    return cfg, allow, plan, dups, r


def load_state(files):
    path = files.out / "state" / "state.json"
    if not path.exists():
        return {"version": 2, "boards": {}}
    st = json.loads(files.check_read(path).read_text())
    if not isinstance(st, dict) or not isinstance(st.get("boards"), dict):
        raise ValueError("the state file is not a JSON object with a 'boards' object")
    return st


def save_state(ctx):
    boards = dict(ctx.state.get("boards", {}))
    for key, obs in ctx.observed.items():  # only boards observed successfully in this run (S2)
        seen = set(obs["prev"]) | (set(obs["ids"]) - obs["unjudged"])  # unjudged postings stay new (S3)
        boards[key] = {"seen": sorted(seen), "last_count": len(obs["ids"]), "last_run": ctx.run_id}
    path = ctx.files.out / "state" / "state.json"
    tmp = path.with_name(f"state.json.tmp-{os.getpid()}")
    ctx.files.check_write(tmp, "state")
    ctx.files.check_write(path, "state")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps({"version": 2, "boards": boards}, indent=1) + "\n")
    os.replace(tmp, path)  # atomic: a crash cannot leave half a state file
    return sorted(ctx.observed)


def new_run_dir(files, now, source):
    base = files.out / "runs" / f"{now:%Y-%m-%dT%H%M%S}_{source}"
    n = 1
    while True:
        candidate = base if n == 1 else base.with_name(f"{base.name}_{n}")
        files.check_write(candidate, "create") if not candidate.exists() else None
        try:
            candidate.mkdir(parents=True)
            return candidate
        except FileExistsError:
            n += 1


def run(boards_path, out_root="out", fetcher=None, fetcher_factory=None, budgets=None, sleep=time.sleep,
        clock=time.monotonic, no_claude=False, resume_path=PERSONA, stream=None, baselines=None, root=ROOT, seeded=None,
        approvals=(), reset_state=False, prompt=ROOT / "prompts" / "judge_v1_baseline.txt", model=None, now=None):
    out = stream or sys.stdout
    baselines = BASELINES if baselines is None else baselines
    try:
        files = policy.FilePolicy(out_root, root=root, approvals=approvals)
    except policy.PolicyViolation as e:
        print(f"preflight refused the output root before any fetch: {e}", file=out)
        print("loop exit: error (3)", file=out)
        return {"code": 3, "status": "error", "run_dir": None, "report": None}

    now = now or datetime.now().astimezone()
    source = "seeded" if seeded else "live"
    ctx = Ctx()
    ctx.files, ctx.sleep, ctx.no_claude, ctx.baselines = files, sleep, no_claude, baselines
    ctx.prompt, ctx.model = prompt, model or claude_judge.DEFAULT_MODEL
    ctx.records, ctx.observed, ctx.judgment_missing, ctx.actions = [], {}, [], ActionLog()
    ctx.run_dir = new_run_dir(files, now, source)
    ctx.run_id = ctx.run_dir.name
    error_reason = budget_reason = None
    approvals_refused, dups, plan = [], [], []

    try:
        ctx.cfg, ctx.allow, plan, dups, ctx.resume = preflight(files, boards_path, budgets, resume_path)
    except (PreflightError, policy.PolicyViolation) as e:
        error_reason = f"preflight: {e}"
        ctx.cfg = budgets or {"max_requests": 0, "max_seconds": 0, "max_loop_steps": 0, "request_timeout_s": 0}
    ctx.budget = Budget(ctx.cfg, clock=clock)
    ctx.trace = Trace(files, ctx.run_dir / "trace.jsonl", ctx.budget)
    ctx.trace.write(action="preflight", decision="allowed" if not error_reason else "denied", rule="preflight",
                    outcome=error_reason or f"{len(plan)} boards planned; duplicates removed: {dups or 'none'}")

    if not error_reason:
        try:
            ctx.state = load_state(files)
        except (OSError, ValueError) as e:
            error_reason = f"unreadable state: {e}"
    if not error_reason and reset_state:
        try:
            files.check_write(files.out / "state" / "state.json", "delete")
            ctx.state = {"version": 2, "boards": {}}
            ctx.trace.write(action="reset_state", decision="allowed", rule="files.approval", outcome="state reset (approved)")
        except policy.NeedsApproval as e:
            approvals_refused.append(str(e))
            ctx.trace.write(action="reset_state", decision="needs_approval", rule="files.approval", outcome=str(e))

    if not error_reason:
        if fetcher is None:
            factory = fetcher_factory or (lambda c: net.LiveFetcher(
                c.allow, c.cfg["max_redirect_hops"], c.budget.charge_request, c.budget.check_time, clock=clock, sleep=sleep))
            fetcher = factory(ctx)
        ctx.fetcher = fetcher
        try:
            for entry in plan:
                observe_board(ctx, entry)
        except BudgetExhausted as e:
            budget_reason = str(e)
        except NoProgress as e:
            error_reason = f"no progress: {e}"
        except policy.PolicyViolation as e:
            error_reason = f"permission violation, escalated: {e}"
        except Exception as e:  # an unexpected internal error must not look like a clean run
            error_reason = f"internal error: {type(e).__name__}: {e}"
        done = {r["key"] for r in ctx.records}
        for entry in plan:
            if entry["key"] not in done:
                ctx.records.append({"key": entry["key"], "provider": entry["provider"], "board": entry["board"],
                                    "status": "not_observed", "reason": "not attempted: the run stopped first",
                                    "attempts": 0, "http_status": None, "count": None, "baseline": False, "history": None,
                                    "new_ids": [], "new_judged": [], "new_unjudged": [], "new_other_ids": [],
                                    "detail_failures": [], "raw_paths": []})

    status, reasons = compute_exit(ctx.records, budget_reason, error_reason, approvals_refused, ctx.judgment_missing)
    code = EXIT_CODES[status]
    state_plan = "not updated (error exit)" if status == "error" else \
        f"after this report is written: {len(ctx.observed)} board(s) observed successfully"
    report = {
        "run_id": ctx.run_id, "started": now.isoformat(timespec="seconds"), "source": source, "seeded_note": seeded,
        "boards_file": rel(boards_path), "out_root": rel(files.out), "claude": "off" if no_claude else "on",
        "exit": {"status": status, "code": code, "reasons": reasons},
        "requests_used": ctx.budget.requests, "seconds_used": round(ctx.budget.elapsed(), 1), "steps_used": ctx.budget.steps,
        "budgets": {k: v for k, v in ctx.cfg.items() if k != "note"}, "plan": [e["key"] for e in plan],
        "duplicates_removed": dups, "approvals_refused": approvals_refused, "state_update": state_plan,
        "boards": ctx.records,
    }
    policy.write_new(files, ctx.run_dir / "report.json", (json.dumps(report, indent=1) + "\n").encode())
    ctx.trace.write(action="exit", decision="allowed", rule="exits", outcome=f"{status} ({code})")
    ctx.trace.close()

    if status == "error":
        state_msg = "not updated (error exit)"
    else:
        updated = save_state(ctx)
        state_msg = f"updated for {len(updated)} board(s) observed successfully; failed or unobserved boards unchanged"
    policy.write_new(files, ctx.run_dir / "state_update.json", (json.dumps({"state_update": state_msg}) + "\n").encode())

    print_summary(out, ctx, report, state_msg)
    return {"code": code, "status": status, "run_dir": str(ctx.run_dir), "report": report}


def print_summary(out, ctx, report, state_msg):
    label = f"SEEDED ({report['seeded_note']})" if report["source"] == "seeded" else "LIVE"
    print(f"Run {report['run_id']}  [{label}]  boards file: {report['boards_file']}  output root: {report['out_root']}  "
          f"claude: {report['claude']}", file=out)
    for r in report["boards"]:
        if r["status"] == "ok":
            hist = "baseline: first observation" if r["baseline"] else f"compared with {r['history']}"
            print(f"  {r['key']:36} ok           {r['count']:4} postings  {hist}; new: {len(r['new_ids'])} "
                  f"({len(r['new_judged'])} judged, {len(r['new_unjudged'])} not judged, {len(r['new_other_ids'])} other)",
                  file=out)
        else:
            word = "FAILED" if r["status"] == "failed" else "NOT OBSERVED"
            print(f"  {r['key']:36} {word:12} count unknown, not zero: {r['reason']}", file=out)
    for r in report["boards"]:
        for j in r["new_judged"]:
            print(f"    - [{r['key']} {j['id']}] {j['title']} | {j['location']} -> rule: {j['rule_verdict']}"
                  f"{'' if j['claude'] == 'off' else ', claude: ' + str(j['claude'].get('verdict'))}", file=out)
    b = report["budgets"]
    print(f"requests {report['requests_used']}/{b.get('max_requests')}  seconds {report['seconds_used']}/{b.get('max_seconds')}  "
          f"steps {report['steps_used']}/{b.get('max_loop_steps')}", file=out)
    print(f"state update: {state_msg}", file=out)
    print(f"run dir: {rel(ctx.run_dir)}", file=out)
    if report["exit"]["reasons"]:
        print("attention required:", file=out)
        for reason in report["exit"]["reasons"]:
            print(f"  - {reason}", file=out)
    print(f"loop exit: {report['exit']['status']} ({report['exit']['code']})", file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boards", required=True, help="board file, e.g. config/boards.json")
    ap.add_argument("--out", default="out", help="output root (default out/)")
    ap.add_argument("--resume", default=str(PERSONA), help="fictional persona (default Evan Gordon)")
    ap.add_argument("--no-claude", action="store_true", help="rule judge only (every graded run uses this)")
    ap.add_argument("--prompt", default=str(ROOT / "prompts" / "judge_v1_baseline.txt"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--approve", action="append", default=[], metavar="PATH", help="approve one named overwrite/delete")
    ap.add_argument("--reset-state", action="store_true", help="start from empty state (needs --approve <out>/state/state.json)")
    ap.add_argument("--replay", action="append", default=[], metavar="PROVIDER:BOARD=FILE", help="SEEDED: serve FILE for that board")
    ap.add_argument("--seeded", help="required with --replay: how the seeded input was made")
    args = ap.parse_args(argv)
    if args.replay and not args.seeded:
        ap.error("--replay needs --seeded '<how the input was made>' so the run is labeled SEEDED")
    factory = None
    if args.replay:
        mapping = {}
        for item in args.replay:
            key, _, path = item.partition("=")
            provider, _, board = key.partition(":")
            mapping[providers.list_url(provider, board)] = path
        factory = lambda c: net.ReplayFetcher(mapping, c.files, c.allow)
    res = run(args.boards, out_root=args.out, fetcher_factory=factory, no_claude=args.no_claude, resume_path=args.resume,
              seeded=args.seeded, approvals=args.approve, reset_state=args.reset_state, prompt=args.prompt, model=args.model)
    return res["code"]


if __name__ == "__main__":
    sys.exit(main())
