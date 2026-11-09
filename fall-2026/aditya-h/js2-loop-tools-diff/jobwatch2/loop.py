"""The bounded loop (GATE.md). One pass over the configured boards, under budgets, a repeat rule, an
error policy and the permission policy. Every step is appended to the run's trace."""
import datetime as dt
import json
import pathlib
import time
import uuid

from . import ats, persona, rule
from .net import http_get
from .policy import Policy

BUDGETS = {"boards": 10, "requests": 15, "seconds": 120}  # GATE.md "Budget changes" v1 — only Aditya changes it
RETRY_DELAY = 2
MAX_TIMEOUT = 20
PERSONA = "personas/maya-sehgal.resume.json"


class PolicyError(Exception):
    pass


class StateError(Exception):
    pass


def board_key(b):
    return f"{b.get('ats')}/{b.get('slug')}"


def state_path(root, key):
    return pathlib.Path(root) / "runs" / "state" / (key.replace("/", "__") + ".json")


class Run:
    def __init__(self, root, policy, now, run_id):
        self.root, self.policy, self.now, self.t0 = pathlib.Path(root), policy, now, now()
        self.dir = self.root / "runs" / run_id
        self.trace_path = self.dir / "trace.jsonl"
        self.check_write(self.trace_path)
        self.dir.mkdir(parents=True, exist_ok=True)

    def trace(self, step, board=None, decision=None, **detail):
        line = {"t": round(self.now() - self.t0, 3), "step": step, "board": board, "decision": decision, **detail}
        with self.trace_path.open("a") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def check_write(self, path):
        d = self.policy.write(path)
        if not d.allowed:
            raise PolicyError(d.reason)

    def write(self, path, data, board=None):
        d = self.policy.write(path)
        self.trace("write", board, "allow" if d.allowed else "deny", path=str(path), reason=d.reason)
        if not d.allowed:
            raise PolicyError(d.reason)
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(data if isinstance(data, bytes) else data.encode())
        tmp.replace(path)

    def read(self, path, board=None):
        d = self.policy.read(path)
        self.trace("read", board, "allow" if d.allowed else "deny", path=str(path), reason=d.reason)
        if not d.allowed:
            raise PolicyError(d.reason)
        return pathlib.Path(path).read_bytes()


def load_state(r, key):
    p = state_path(r.root, key)
    if not p.exists():
        return None
    try:
        data = json.loads(r.read(p, key))
    except ValueError as e:
        raise StateError(f"state for {key} is not valid JSON") from e
    if not isinstance(data, dict) or not isinstance(data.get("seen_ids"), list) \
            or not all(isinstance(i, str) for i in data["seen_ids"]):
        raise StateError(f"state for {key} is malformed")
    return data


def run(root, boards, fetcher=http_get, now=time.monotonic, sleep=time.sleep, approvals=(), budgets=BUDGETS,
        run_id=None):
    root = pathlib.Path(root)
    policy = Policy(root, approvals)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    r = Run(root, policy, now, run_id or f"{stamp}-{uuid.uuid4().hex[:6]}")
    entries = [{"key": board_key(b), "ats": b.get("ats"), "slug": b.get("slug"), "status": "not-attempted",
                "reason": None, "http_status": None, "attempts": 0, "fetched": None, "new": None,
                "relevant": None, "baseline": None, "raw_path": None, "new_postings": []} for b in boards]
    used = {"boards": 0, "requests": 0}
    exit_status, budget_hit, error = None, None, None
    r.trace("start", detail_budgets=budgets, boards=[e["key"] for e in entries])

    try:
        resume = json.loads(r.read(root / PERSONA))
        bad = persona.problems(resume)
        if bad:
            raise PolicyError("persona refused: " + "; ".join(bad))
        done = set()
        for e in entries:
            key = e["key"]
            if e["ats"] not in ats.ATS:
                raise PolicyError(f"unknown ATS {e['ats']!r} for {key}")
            if key in done:
                e.update(status="skipped-duplicate", reason="board listed twice; fetched once")
                r.trace("observation", key, None, status=e["status"])
                continue
            if used["boards"] >= budgets["boards"]:
                exit_status, budget_hit = "budget-exhausted", "boards"
                break
            url = ats.url(e["ats"], e["slug"])
            d = policy.request("GET", url)
            r.trace("plan", key, "allow" if d.allowed else "deny", url=url, reason=d.reason)
            if not d.allowed:
                raise PolicyError(d.reason)
            prev = load_state(r, key)
            done.add(key)
            used["boards"] += 1

            status, body, err = None, None, None
            while True:
                elapsed = now() - r.t0
                if used["requests"] >= budgets["requests"]:
                    exit_status, budget_hit = "budget-exhausted", "requests"
                elif elapsed >= budgets["seconds"]:
                    exit_status, budget_hit = "budget-exhausted", "seconds"
                if exit_status:
                    break
                retry = e["attempts"] > 0
                d = policy.request("GET", url, retry=retry)
                if not d.allowed:
                    r.trace("request", key, "deny", url=url, reason=d.reason)
                    err = d.reason
                    break
                timeout = max(0.1, min(MAX_TIMEOUT, budgets["seconds"] - elapsed))
                policy.record_request("GET", url)
                used["requests"] += 1
                e["attempts"] += 1
                status, body, err = None, None, None
                try:
                    status, body = fetcher(url, timeout)
                except (TimeoutError, ConnectionError, OSError) as ex:
                    err = f"{type(ex).__name__}: {ex}"
                r.trace("request", key, "allow", url=url, attempt=e["attempts"], retry=retry,
                        http_status=status, error=err, bytes=len(body) if body is not None else None)
                if body is not None:
                    raw = r.dir / "raw" / f"{key.replace('/', '__')}.attempt{e['attempts']}.json"
                    r.write(raw, body, key)
                    e["raw_path"] = str(raw)
                transient = err is not None or (status is not None and (status >= 500 or status == 429))
                if transient and e["attempts"] == 1:
                    r.trace("retry-wait", key, None, seconds=RETRY_DELAY, why=err or f"HTTP {status}")
                    sleep(RETRY_DELAY)
                    continue
                break

            e["http_status"] = status
            if exit_status and e["attempts"] == 0:
                e.update(status="not-attempted", reason=f"{budget_hit} budget exhausted before first request")
                done.discard(key)
                used["boards"] -= 1
                break
            if err is not None or status != 200:
                e.update(status="failed", reason=err or f"HTTP {status}")
            else:
                try:
                    posts = ats.parse(e["ats"], body)
                except ats.ShapeError as ex:
                    posts = None
                    e.update(status="failed", reason=f"bad shape: {ex}")
                if posts is not None:
                    if not posts and prev and prev["seen_ids"]:
                        e.update(status="failed", reason="suspect-empty: zero postings but state holds ids")
                    else:
                        ids = [f"{key}:{p['id']}" for p in posts]
                        seen = set(prev["seen_ids"]) if prev else set()
                        new = [p for p, i in zip(posts, ids) if i not in seen] if prev else []
                        judged = [{"id": f"{key}:{p['id']}", "title": p["title"], "url": p["url"],
                                   **rule.judge(p, resume)} for p in new]
                        e.update(status="ok", fetched=len(posts), new=len(new), baseline=prev is None,
                                 relevant=sum(j["verdict"] == "relevant" for j in judged), new_postings=judged)
                        r.write(state_path(root, key), json.dumps(
                            {"board": key, "last_run": dt.datetime.now(dt.timezone.utc).isoformat(),
                             "seen_ids": sorted(seen | set(ids))}, indent=1) + "\n", key)
            r.trace("observation", key, None, status=e["status"], reason=e["reason"], fetched=e["fetched"],
                    new=e["new"], relevant=e["relevant"], attempts=e["attempts"])
            if exit_status:
                break
    except (PolicyError, StateError) as ex:
        exit_status, error = "error", f"{type(ex).__name__}: {ex}"
        r.trace("escalate", None, "deny", reason=error)

    if exit_status is None:
        exit_status = "finished" if all(e["status"] == "ok" for e in entries) else "incomplete"
    res = {"exit": exit_status, "budget_hit": budget_hit, "error": error, "rule_id": rule.RULE_ID,
           "budgets": budgets, "budget_used": {**used, "seconds": round(now() - r.t0, 3)},
           "boards": entries, "run_dir": str(r.dir), "trace_path": str(r.trace_path),
           "record_path": str(r.dir / "record.json"), "report_path": str(r.dir / "report.md")}
    r.trace("exit", None, None, exit=exit_status, budget_hit=budget_hit, error=error, used=res["budget_used"])
    r.write(r.dir / "record.json", json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    r.write(r.dir / "report.md", report(res))
    return res


def report(res):
    out = [f"# Job watch — exit: **{res['exit']}**", ""]
    if res["exit"] != "finished":
        out += [f"> Not a clean finish: {res['error'] or (res['budget_hit'] and res['budget_hit'] + ' budget exhausted') or 'one or more boards failed or were skipped'}.", ""]
    out += ["> `finished` means every board was fetched and parsed. It does not mean the answer is right: "
            "run `python3 check_run.py <run_dir>` for the independent check.", "",
            f"Budget used: {res['budget_used']} of {res['budgets']}", "",
            "| board | status | HTTP | attempts | fetched | new | relevant (rule) | reason |",
            "|---|---|---|---|---|---|---|---|"]
    show = lambda v: "—" if v is None else v
    for e in res["boards"]:
        out.append(f"| {e['key']} | {e['status']} | {show(e['http_status'])} | {e['attempts']} | {show(e['fetched'])} | "
                   f"{show(e['new'])} | {show(e['relevant'])} | {e['reason'] or ''} |")
    out.append("")
    for e in res["boards"]:
        rel = [j for j in e["new_postings"] if j["verdict"] == "relevant"]
        if rel:
            out += [f"## {e['key']}: relevant new postings", ""]
            out += [f"- **{j['title']}** ({j['url']}) — {j['reason']}; résumé: {j['resume_fields']}" for j in rel]
            out.append("")
    return "\n".join(out) + "\n"


def reset_board(root, key, approvals=()):
    p = Policy(root, approvals)
    d = p.reset(key)
    if not d.allowed:
        raise PolicyError(d.reason)
    path = state_path(root, key)
    w = p.write(path)
    if not w.allowed:
        raise PolicyError(w.reason)
    if path.exists():
        path.unlink()
