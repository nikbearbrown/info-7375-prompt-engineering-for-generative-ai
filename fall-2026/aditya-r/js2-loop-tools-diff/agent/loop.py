"""The JS2 bounded loop: several boards, budgets, exits, a trace of every action (GATE.md, Addendum 1).

    python -m agent.loop --label live                       # watch the configured boards
    python -m agent.loop --label live --propose-export      # also propose a shortlist export
    python -m agent.loop --export <run-id>                  # export-only: needs approvals/<run-id>.json

Exit codes: 0 finished, 2 error, 3 incomplete, 4 budget-exhausted (1 is reserved for a crash).
"""
import argparse
import copy
import datetime as dt
import gzip
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from . import judge as judge_mod
from .board import BoardError, BoardInconsistentError
from .net import TransportError, https_get
from .policy import PathPolicy, PolicyError, check_request
from .providers import PROVIDERS, SuspectEmpty
from .resume import ResumeError, load_resume
from .rules import evaluate
from .state import StateError, load_state as load_js1_state
from .validate import validate_judgment

ROOT = Path(__file__).resolve().parent.parent
LIMITS = {"boards": 4, "http_attempts": 8, "seconds": 180, "model_calls": 10}  # GATE.md §2 — maxima
ATTEMPT_TIMEOUT = MODEL_TIMEOUT = 20.0
RESERVE = 10.0      # Addendum §4
RETRY_WAIT = 0.5    # GATE.md §4
EXIT = {"finished": 0, "error": 2, "incomplete": 3, "budget-exhausted": 4}
LABEL_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
STATE_PATH = "out/state/seen.json"
JUDGMENT_LABEL = "Claude's judgment under a prompt contract — an opinion, validated for format and cited evidence, NOT for correctness"


class ConfigError(ValueError):
    pass


def _utc():
    return dt.datetime.now(dt.timezone.utc)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _dumps(obj):
    return (json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


class Trace:
    """Append-only JSONL record of every observation and action, in order."""

    def __init__(self, policy, path, clock, t0):
        self.f, self.clock, self.t0, self.seq = policy.open_new_stream(path), clock, t0, 0

    def __call__(self, event, **fields):
        self.seq += 1
        rec = {"seq": self.seq, "t": round(self.clock() - self.t0, 3),
               "utc": _utc().isoformat(timespec="milliseconds"), "event": event, **fields}
        self.f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
        self.f.flush()

    def close(self):
        self.f.close()


class Budget:
    def __init__(self, limits, clock, t0):
        self.limits, self.clock, self.t0 = limits, clock, t0
        self.http_used = self.model_used = 0

    def elapsed(self):
        return self.clock() - self.t0

    def allowance(self):  # Addendum §4: 180 − elapsed − 10
        return self.limits["seconds"] - self.elapsed() - RESERVE

    def consumption(self):
        return {"http_attempts": {"used": self.http_used, "limit": self.limits["http_attempts"]},
                "model_calls": {"used": self.model_used, "limit": self.limits["model_calls"]},
                "elapsed_seconds": {"used": round(self.elapsed(), 3), "limit": self.limits["seconds"],
                                    "finalization_reserve": RESERVE}}


def resolve_limits(overrides):
    limits = dict(LIMITS)
    for k, v in (overrides or {}).items():
        if v is None:
            continue
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0 or v > LIMITS[k]:
            raise ConfigError(f"limit {k}={v!r}: options may lower limits but never raise them (max {LIMITS[k]})")
        limits[k] = v
    return limits


def load_config(policy, path, limits):
    raw = policy.check_read(path).read_bytes()
    try:
        cfg = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ConfigError(f"config is not valid JSON: {e}") from None
    boards = cfg.get("boards") if isinstance(cfg, dict) else None
    if not isinstance(boards, list) or not boards:
        raise ConfigError("config needs a nonempty 'boards' list")
    if len(boards) > limits["boards"]:
        raise ConfigError(f"{len(boards)} boards configured; the limit is {limits['boards']} (no board is dropped silently)")
    out, keys = [], set()
    for i, b in enumerate(boards):
        if not isinstance(b, dict) or set(b) - {"provider", "board", "seed_from_js1_state", "purpose"}:
            raise ConfigError(f"boards[{i}] has unknown or missing fields")
        prov = PROVIDERS.get(b.get("provider"))
        if prov is None:
            raise ConfigError(f"boards[{i}]: provider {b.get('provider')!r} is not supported")
        if not isinstance(b.get("board"), str) or not prov.token_re.fullmatch(b["board"]):
            raise ConfigError(f"boards[{i}]: invalid board token {b.get('board')!r}")
        key = f"{prov.name}:{b['board']}"
        if key in keys:
            raise ConfigError(f"duplicate board {key} (the repeat rule rejects it; nothing fetched twice)")
        keys.add(key)
        out.append({"key": key, "provider": prov.name, "board": b["board"], "adapter": prov,
                    "seed": b.get("seed_from_js1_state"), "purpose": b.get("purpose")})
    return out, _sha(raw)


def load_working_state(policy, path):
    p = policy.check_read(path)
    if not p.exists():
        return {"version": 2, "boards": {}, "runs": []}, None
    raw = p.read_bytes()
    try:
        st = json.loads(raw)
    except json.JSONDecodeError as e:
        raise StateError(f"working state {path} is not valid JSON ({e.msg}); refusing to start over") from None
    ok = (isinstance(st, dict) and st.get("version") == 2 and isinstance(st.get("boards"), dict)
          and isinstance(st.get("runs"), list))
    for k, v in (st.get("boards") or {}).items() if ok else ():
        ok = ok and isinstance(v, dict) and isinstance(v.get("ids"), dict) and all(
            isinstance(i, str) and s in ("baseline", "completed", "pending") for i, s in v["ids"].items())
    if not ok:
        raise StateError(f"working state {path} is malformed; refusing to start over")
    return st, raw


def seed_from_js1(policy, board, path):
    """GATE.md §2: Databricks starts from a validated, documented copy of the JS1 state."""
    p = policy.check_read(path)
    st = load_js1_state(p)
    if st is None:
        raise StateError(f"inherited state {path} does not exist")
    if st["board"] != board:
        raise StateError(f"inherited state {path} belongs to {st['board']!r}, not {board!r}")
    raw = p.read_bytes()
    return dict(st["ids"]), {"path": str(path), "sha256": _sha(raw), "ids": len(st["ids"]),
                             "js1_runs": len(st["runs"]), "kind": "INHERITED JS1 state (not captured by JS2)"}


def fetch_board(b, ctx):
    """Attempts for one board under the error policy. Returns (outcome dict, jobs or None)."""
    url = b["adapter"].url(b["board"])
    check_request("GET", url)  # PolicyError -> run-level error (no attempt consumed)
    budget, trace, transport, clock = ctx["budget"], ctx["trace"], ctx["transport"], ctx["clock"]
    attempts, first_seq = [], None
    for attempt in (1, 2):
        if budget.http_used >= budget.limits["http_attempts"]:
            return _blocked(b, "http_attempts", attempts, after_failure=bool(attempts)), None
        allowance = budget.allowance()
        if allowance <= 0:
            return _blocked(b, "seconds", attempts, after_failure=bool(attempts)), None
        action = ("GET", url)
        if action in ctx["dispatched"] and attempt == 1:
            raise PolicyError(f"refused: repeated action {action} outside the single-retry rule")
        ctx["dispatched"].add(action)
        budget.http_used += 1  # counted immediately before dispatch (GATE.md §2)
        timeout = min(ATTEMPT_TIMEOUT, allowance)
        trace("http_attempt", board=b["key"], url=url, attempt=attempt, retry_of=first_seq if attempt == 2 else None,
              http_attempts_used=budget.http_used, timeout_s=round(timeout, 3))
        seq = trace.seq
        first_seq = first_seq or seq
        rec = {"attempt": attempt, "trace_seq": seq}
        try:
            status, headers, body = transport(url, timeout, clock() + timeout)
        except TransportError as e:
            rec.update(outcome="transport-error", kind=e.kind, detail=str(e))
            trace("http_result", board=b["key"], attempt=attempt, outcome="transport-error", kind=e.kind, detail=str(e))
            attempts.append(rec)
            if e.kind in ("timeout", "connection") and attempt == 1:
                blocked = _retry_wait(ctx, b)
                if blocked:
                    return _blocked(b, blocked, attempts, after_failure=True), None
                continue
            return _failed(b, f"transport failure ({e.kind}): {e}", attempts), None
        raw_name = f"raw/{ctx['n_raw']:02d}_{b['provider']}_{b['board']}_a{attempt}.json.gz"
        ctx["n_raw"] += 1
        ctx["policy"].write_new(ctx["run_dir"] / raw_name, gzip.compress(body, mtime=0))
        rec.update(status=status, bytes=len(body), sha256=_sha(body), raw=raw_name,
                   content_type=headers.get("content-type"))
        trace("http_result", board=b["key"], attempt=attempt, status=status, bytes=len(body), sha256=_sha(body),
              raw=raw_name, content_type=headers.get("content-type"))
        attempts.append(rec)
        if 300 <= status < 400:
            trace("redirect_refused", board=b["key"], status=status, location=headers.get("location"))
            raise PolicyError(f"refused: HTTP {status} redirect from {url} (redirects are never followed)")
        if status == 200:
            try:
                jobs = b["adapter"].parse(body)
            except SuspectEmpty as e:
                return _failed(b, str(e), attempts, kind="suspect-empty"), None
            except BoardInconsistentError as e:
                return _failed(b, str(e), attempts, kind="inconsistent"), None
            except BoardError as e:
                return _failed(b, f"invalid response: {e}", attempts, kind="invalid"), None
            return {"key": b["key"], "status": "succeeded", "attempts": attempts}, jobs
        if 500 <= status < 600 and attempt == 1:
            blocked = _retry_wait(ctx, b)
            if blocked:
                return _blocked(b, blocked, attempts, after_failure=True), None
            continue
        reason = f"HTTP {status}" + (" (no retry: 4xx is not transient)" if 400 <= status < 500 else "")
        out = _failed(b, reason, attempts, kind=f"http-{status}")
        if status == 429:
            out["retry_after"] = headers.get("retry-after")
        return out, None
    raise AssertionError("unreachable")


def _retry_wait(ctx, b):
    """Returns the name of the budget that blocks the retry, or None after waiting."""
    budget = ctx["budget"]
    if budget.http_used >= budget.limits["http_attempts"]:
        return "http_attempts"
    if budget.allowance() <= RETRY_WAIT:
        return "seconds"
    ctx["trace"]("retry_wait", board=b["key"], seconds=RETRY_WAIT)
    ctx["sleep"](RETRY_WAIT)
    return None


def _failed(b, reason, attempts, kind="failed"):
    return {"key": b["key"], "status": "failed", "kind": kind, "reason": reason, "attempts": attempts}


def _blocked(b, which, attempts, after_failure=False):
    status = "failed" if after_failure else "unattempted"
    reason = (f"{which} budget prevented " + ("a permitted retry" if after_failure else "any attempt"))
    return {"key": b["key"], "status": status, "kind": "budget", "budget": which, "reason": reason,
            "attempts": attempts}


def default_judge():
    system, prompt_sha = judge_mod.load_prompt("v1")

    def judge(posting, resume, timeout):
        rec = judge_mod.call_claude(system, judge_mod.build_user_message(posting, resume), timeout=timeout)
        rec["prompt_version"], rec["prompt_sha256"] = "v1", prompt_sha
        return rec

    return judge


def run_loop(root=ROOT, *, config="config/boards.json", resume="resume/priya-nair.resume.example.json",
             label="run", transport=https_get, judge_fn=None, clock=time.monotonic, sleep=time.sleep,
             limits=None, propose_export=False, now=_utc):
    t0 = clock()
    started = now()
    if not LABEL_RE.fullmatch(label or ""):
        print(f"ERROR: invalid label {label!r}", file=sys.stderr)
        return EXIT["error"], None
    policy = PathPolicy(root)
    run_id = f"{started.strftime('%Y%m%dT%H%M%S')}{started.microsecond // 1000:03d}Z_{label}"
    try:
        run_dir = policy.mkdir_new(policy.out / "runs" / run_id)
    except (PolicyError, OSError) as e:
        print(f"ERROR: cannot create a unique run directory: {e}", file=sys.stderr)
        return EXIT["error"], None
    trace = Trace(policy, run_dir / "trace.jsonl", clock, t0)
    trace("run_start", run_id=run_id, started_utc=started.isoformat(timespec="seconds"))
    report = {"run_id": run_id, "started_utc": started.isoformat(timespec="seconds"), "boards": [],
              "postings": [], "approval_request": None, "errors": []}
    budget = None
    boards = []
    run_error = None
    staged = state_raw = None
    try:
        lim = resolve_limits(limits)
        budget = Budget(lim, clock, t0)
        boards, cfg_sha = load_config(policy, config, lim)
        trace("config_validated", config=str(config), sha256=cfg_sha, boards=[b["key"] for b in boards], limits=lim)
        res = load_resume(policy.check_read(resume))
        state, state_raw = load_working_state(policy, STATE_PATH)
        staged = copy.deepcopy(state)
        policy.write_new(run_dir / "state_before.json", state_raw if state_raw is not None else b"null\n")
        trace("state_loaded", path=STATE_PATH, sha256=_sha(state_raw) if state_raw else None,
              boards=sorted(state["boards"]))
        for b in boards:
            if b["seed"] and b["key"] not in staged["boards"]:
                ids, prov = seed_from_js1(policy, b["board"], b["seed"])
                staged["boards"][b["key"]] = {"ids": ids, "seeded_from": prov}
                trace("state_seeded", board=b["key"], **prov)
    except (ConfigError, ResumeError, StateError, PolicyError, OSError) as e:
        run_error = f"{type(e).__name__}: {e}"
        trace("run_error", stage="validation", error=run_error)

    ctx = {"budget": budget, "trace": trace, "transport": transport, "clock": clock, "sleep": sleep,
           "policy": policy, "run_dir": run_dir, "dispatched": set(), "n_raw": 1}
    fetched = {}
    for b in boards:  # fetch every board before spending budget on judgments (GATE.md §2)
        if run_error:
            break
        try:
            outcome, jobs = fetch_board(b, ctx)
        except (PolicyError, OSError) as e:
            run_error = f"{type(e).__name__}: {e}"
            trace("run_error", stage="fetch", board=b["key"], error=run_error)
            report["boards"].append({"key": b["key"], "status": "failed", "kind": "policy", "reason": run_error})
            break
        trace("board_outcome", board=b["key"], status=outcome["status"], reason=outcome.get("reason"))
        if jobs is not None:
            fetched[b["key"]] = jobs
        report["boards"].append(outcome)
    attempted = {o["key"] for o in report["boards"]}
    for b in boards:
        if b["key"] not in attempted:
            report["boards"].append({"key": b["key"], "status": "unattempted", "kind": "stopped",
                                     "reason": "run stopped by a run-level error" if run_error else "not reached",
                                     "attempts": []})

    targets = []
    if not run_error:
        for o in report["boards"]:
            jobs = fetched.get(o["key"])
            if jobs is None:
                o.update(observed=None, new=None, new_ids=None, retried=None)
                continue
            ids = [i for i, _ in jobs]
            entry = staged["boards"].get(o["key"])
            o["observed"] = len(ids)
            if entry is None:
                staged["boards"][o["key"]] = {"ids": {i: "baseline" for i in ids}}
                o.update(status="succeeded", kind="baseline", new=0, new_ids=[], retried=0,
                         note="first successful run: baseline recorded, nothing judged")
                trace("baseline_recorded", board=o["key"], ids=len(ids))
                continue
            new = [i for i in ids if i not in entry["ids"]]
            retry = [i for i in ids if entry["ids"].get(i) == "pending"]
            gone_pending = sorted(i for i, s in entry["ids"].items() if s == "pending" and i not in set(ids))
            for i in new:
                entry["ids"][i] = "pending"
            o.update(kind="watch", new=len(new), new_ids=new, retried=len(retry),
                     pending_not_on_board=gone_pending)
            trace("new_ids", board=o["key"], new=len(new), retried=len(retry), new_ids=new)
            by_id = dict(jobs)
            targets += [(o, i, by_id[i]) for i in new + retry]

        judge_fn = judge_fn or (default_judge() if targets else None)
        for o, pid, posting in targets:
            row = {"provider": o["key"].split(":")[0], "board": o["key"].split(":", 1)[1], "posting_id": pid,
                   "title": posting.get("title"), "url": posting.get("absolute_url"),
                   "location": (posting.get("location") or {}).get("name"),
                   "RECORD": None, "JUDGMENT": {"label": JUDGMENT_LABEL}}
            rec = evaluate(posting, res)
            row["RECORD"] = {k: rec[k] for k in ("verdict", "checks", "missing", "explanation")}
            allowance = budget.allowance()
            if budget.model_used >= budget.limits["model_calls"]:
                row["JUDGMENT"].update(status="not-run", budget="model_calls")
            elif allowance <= 0:
                row["JUDGMENT"].update(status="not-run", budget="seconds")
            else:
                budget.model_used += 1  # counted before the invocation starts
                timeout = min(MODEL_TIMEOUT, allowance)
                trace("model_call", board=o["key"], posting_id=pid, model_calls_used=budget.model_used,
                      timeout_s=round(timeout, 3))
                jrec = judge_fn(posting, res, timeout)
                text = jrec.get("response_text")
                ok, errors, parsed = (validate_judgment(text, posting, res) if text is not None
                                      else (False, ["transport: no response text"], None))
                jrec.update(posting_id_requested=pid, board=o["key"], valid=ok, validation_errors=errors)
                jname = f"judgments/{row['provider']}_{row['board']}_{pid}.json"
                policy.write_new(run_dir / jname, _dumps(jrec))
                trace("model_result", board=o["key"], posting_id=pid, valid=ok, errors=errors[:3], file=jname,
                      wall_seconds=jrec.get("wall_seconds"))
                row["JUDGMENT"].update(status="valid" if ok else "invalid", verdict=(parsed or {}).get("verdict"),
                                       explanation=(parsed or {}).get("explanation"), errors=errors or None,
                                       file=jname, models_used=jrec.get("models_used"))
                if ok:
                    staged["boards"][o["key"]]["ids"][pid] = "completed"
            report["postings"].append(row)

    # ---- exit status, by precedence: error > budget-exhausted > incomplete > finished ----
    budget_reasons, incomplete_reasons = [], []
    for o in report["boards"]:
        if o.get("kind") == "budget":
            budget_reasons.append(f"{o['key']}: {o['reason']}")
        elif o["status"] in ("failed", "unattempted"):
            incomplete_reasons.append(f"{o['key']}: {o['status']} — {o.get('reason')}")
        if o["status"] != "succeeded":
            o.update(observed=None, new=None, new_ids=None, retried=None)  # unknown, never zero
        for i in o.get("pending_not_on_board") or []:
            incomplete_reasons.append(f"{o['key']}: posting {i} pending but no longer on the board")
    for r in report["postings"]:
        j = r["JUDGMENT"]
        if j.get("status") == "not-run":
            budget_reasons.append(f"{r['provider']}:{r['board']} {r['posting_id']}: judgment not run ({j['budget']} budget)")
        elif j.get("status") == "invalid":
            incomplete_reasons.append(f"{r['provider']}:{r['board']} {r['posting_id']}: judgment invalid, pending")
    if run_error is None and propose_export:
        try:
            report["approval_request"] = propose(policy, run_dir, run_id, report, budget_reasons, incomplete_reasons)
            incomplete_reasons.append(f"approval requested for {report['approval_request']['destination']}; not yet approved")
            trace("approval_proposed", **{k: report["approval_request"][k] for k in ("destination", "sha256")})
        except (PolicyError, OSError) as e:
            run_error = f"{type(e).__name__}: {e}"
    status = ("error" if run_error else "budget-exhausted" if budget_reasons
              else "incomplete" if incomplete_reasons else "finished")
    if run_error:
        report["errors"].append(run_error)
    report.update(status=status, exit_code=EXIT[status], budget_reasons=budget_reasons,
                  incomplete_reasons=incomplete_reasons,
                  budget=budget.consumption() if budget else None,
                  counts={"configured": len(boards) or None,
                          "attempted": sum(1 for o in report["boards"] if o.get("attempts")),
                          "succeeded": sum(1 for o in report["boards"] if o["status"] == "succeeded"),
                          "failed": sum(1 for o in report["boards"] if o["status"] == "failed"),
                          "unattempted": sum(1 for o in report["boards"] if o["status"] == "unattempted"),
                          "judgments_valid": sum(1 for r in report["postings"] if r["JUDGMENT"].get("status") == "valid"),
                          "pending": sum(1 for r in report["postings"] if r["JUDGMENT"].get("status") != "valid")})

    # ---- finalize: publish staged state unless run-level error ----
    if run_error is None and staged is not None:
        staged["runs"].append({"run_id": run_id, "status": status, "finished_utc": now().isoformat(timespec="seconds")})
        try:
            policy.replace_state(STATE_PATH, _dumps(staged))
            policy.write_new(run_dir / "state_after.json", _dumps(staged))
            report["state"] = {"published": True, "path": STATE_PATH, "sha256": _sha(_dumps(staged))}
        except (PolicyError, OSError) as e:
            report.update(status="error", exit_code=EXIT["error"])
            report["errors"].append(f"persistence failure: {e}")
            report["state"] = {"published": False}
    else:
        report["state"] = {"published": False, "reason": "run-level error: staged state not published"}
    report["finished_utc"] = now().isoformat(timespec="seconds")
    trace("run_end", status=report["status"], exit_code=report["exit_code"],
          budget=report["budget"], state_published=report["state"]["published"])
    trace.close()
    policy.write_new(run_dir / "report.json", _dumps(report))
    policy.write_new(run_dir / "report.md", render_md(report).encode("utf-8"))
    print(f"{report['status'].upper()} (exit {report['exit_code']}): run {run_id}. Report: {run_dir / 'report.md'}")
    return report["exit_code"], run_dir


def shortlist_bytes(run_id, report, unresolved):
    entries, withheld = [], 0
    for r in report["postings"]:
        if r["RECORD"]["verdict"] != "relevant":
            continue
        j = r["JUDGMENT"]
        if j.get("status") != "valid":
            withheld += 1
            continue
        entries.append({"provider": r["provider"], "board": r["board"], "posting_id": r["posting_id"],
                        "title": r["title"], "job_url": r["url"], "source_run": run_id,
                        "RECORD_verdict": r["RECORD"]["verdict"], "JUDGMENT_verdict": j.get("verdict"),
                        "verdicts_agree": j.get("verdict") == r["RECORD"]["verdict"],
                        "evidence": {"report": f"out/runs/{run_id}/report.json", "judgment": f"out/runs/{run_id}/{j['file']}"}})
    doc = {"kind": "shortlist export (local file; not an application or message)",
           "source_run": run_id, "partial": bool(unresolved),
           "partial_reason": "source run has unresolved work" if unresolved else None,
           "withheld_relevant_without_valid_judgment": withheld,
           "caution": "A validated JUDGMENT is an opinion checked for format and cited evidence; it does not prove suitability.",
           "entries": entries}
    return _dumps(doc)


def propose(policy, run_dir, run_id, report, budget_reasons, incomplete_reasons):
    data = shortlist_bytes(run_id, report, budget_reasons or incomplete_reasons)
    dest = f"out/approved-shortlists/{run_id}.json"
    pdir = policy.out / "pending_approval"
    policy.write_new(pdir / f"{run_id}.export.json", data)
    proposal = {"operation": "create-shortlist-export", "run_id": run_id, "destination": dest,
                "sha256": _sha(data), "bytes": len(data), "proposed_bytes_file": f"out/pending_approval/{run_id}.export.json",
                "approval_record_expected_at": f"approvals/{run_id}.json"}
    policy.write_new(pdir / f"{run_id}.json", _dumps(proposal))
    return {**proposal, "write_occurred": False}


def export_run(root=ROOT, run_id="", now=_utc):
    """Export-only invocation (Addendum §2): no board requests, no model calls, create-only."""
    policy = PathPolicy(root)
    if not re.fullmatch(r"\d{8}T\d{9}Z_[a-z0-9][a-z0-9-]{0,39}", run_id or ""):
        print(f"ERROR: invalid run id {run_id!r}", file=sys.stderr)
        return EXIT["error"]
    result = {"run_id": run_id, "at_utc": now().isoformat(timespec="seconds"), "write_occurred": False}

    def finish(status, reason):
        result.update(status=status, exit_code=EXIT[status], reason=reason)
        policy.write_new(policy.out / "exports" / f"{run_id}.{now().strftime('%Y%m%dT%H%M%S%fZ')}.result.json",
                         _dumps(result))
        print(f"EXPORT {status.upper()} (exit {EXIT[status]}): {reason}")
        return EXIT[status]

    try:
        prop_path = policy.check_read(f"out/pending_approval/{run_id}.json")
        proposal = json.loads(prop_path.read_bytes())
        data = policy.check_read(proposal["proposed_bytes_file"]).read_bytes()
    except (PolicyError, OSError, ValueError, KeyError) as e:
        return finish("error", f"no valid proposal for {run_id}: {e}")
    if proposal.get("run_id") != run_id or proposal.get("destination") != f"out/approved-shortlists/{run_id}.json":
        return finish("error", "proposal names a different run or a destination other than out/approved-shortlists/<run-id>.json")
    if _sha(data) != proposal["sha256"]:
        return finish("error", "proposed bytes no longer match the proposal's sha256")
    appr_path = policy.check_read(f"approvals/{run_id}.json")
    if not appr_path.exists():
        return finish("incomplete", f"pending: no human approval record at approvals/{run_id}.json")
    try:
        approval = json.loads(appr_path.read_bytes())
    except ValueError as e:
        return finish("error", f"approval record is not valid JSON: {e}")
    result["approval_sha256"] = _sha(appr_path.read_bytes())
    bound = ("run_id", "operation", "destination", "sha256")
    if not isinstance(approval, dict) or any(approval.get(k) != proposal[k] for k in bound):
        return finish("error", f"approval does not match the proposal on {[k for k in bound if not isinstance(approval, dict) or approval.get(k) != proposal[k]]}")
    try:
        policy.write_new(proposal["destination"], data, approved_export=True)
    except PolicyError as e:
        return finish("error", str(e))
    result.update(write_occurred=True, destination=proposal["destination"], sha256=proposal["sha256"],
                  approved_by=approval.get("approved_by"), approved_at=approval.get("approved_at"))
    return finish("finished", f"created {proposal['destination']} under the matching approval")


def render_md(r):
    md = [f"# JS2 run `{r['run_id']}`", "",
          f"- **Status:** `{r['status']}` (exit {r['exit_code']})",
          f"- **Started / finished (UTC):** {r['started_utc']} / {r.get('finished_utc')}",
          f"- **Budget:** {json.dumps(r['budget'])}",
          f"- **Boards:** {json.dumps(r['counts'])}", ""]
    if r["errors"]:
        md += ["## Run-level errors", ""] + [f"- {e}" for e in r["errors"]] + [""]
    md += ["## Boards", "", "| board | status | kind | observed | new | reason |", "|---|---|---|---|---|---|"]
    for o in r["boards"]:
        md.append(f"| {o['key']} | {o['status']} | {o.get('kind')} | {o.get('observed')} | {o.get('new')} | "
                  f"{(o.get('reason') or o.get('note') or '').replace('|', '/')} |")
    md += ["", "Unknown counts are `None` (never an invented zero).", ""]
    if r["budget_reasons"] or r["incomplete_reasons"]:
        md += ["## Why not finished", ""] + [f"- budget: {x}" for x in r["budget_reasons"]] + \
              [f"- incomplete: {x}" for x in r["incomplete_reasons"]] + [""]
    if r["postings"]:
        md += ["## New / pending postings", "", "RECORD = deterministic rule. JUDGMENT = " + JUDGMENT_LABEL + ".", "",
               "| board | id | title | RECORD | JUDGMENT |", "|---|---|---|---|---|"]
        for p in r["postings"]:
            j = p["JUDGMENT"]
            jv = j.get("verdict") if j.get("status") == "valid" else f"{j.get('status')}" + (f" ({j['budget']} budget)" if j.get("budget") else "")
            md.append(f"| {p['board']} | {p['posting_id']} | {(p['title'] or '').replace('|', '/')} | {p['RECORD']['verdict']} | {jv} |")
    if r.get("approval_request"):
        a = r["approval_request"]
        md += ["", "## Approval request", "", f"- destination `{a['destination']}`, sha256 `{a['sha256']}`, write occurred: {a['write_occurred']}"]
    md += ["", f"State published: {r['state']}"]
    return "\n".join(md) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", default="run")
    ap.add_argument("--config", default="config/boards.json")
    ap.add_argument("--resume", default="resume/priya-nair.resume.example.json")
    ap.add_argument("--propose-export", action="store_true")
    ap.add_argument("--export", metavar="RUN_ID")
    for k in LIMITS:
        ap.add_argument(f"--max-{k.replace('_', '-')}", type=float, dest=k, help=f"lower only (max {LIMITS[k]})")
    a = ap.parse_args(argv)
    if a.export:
        return export_run(ROOT, a.export)
    code, _ = run_loop(ROOT, config=a.config, resume=a.resume, label=a.label, propose_export=a.propose_export,
                       limits={k: getattr(a, k) for k in LIMITS})
    return code


if __name__ == "__main__":
    sys.exit(main())
