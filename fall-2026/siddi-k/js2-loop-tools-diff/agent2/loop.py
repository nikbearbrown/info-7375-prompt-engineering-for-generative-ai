"""The loop (GATE.md §1-§4): visit each board within budget, record every observation, end with a named exit."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlparse

from . import http, policy, providers

EXITS = ("finished", "incomplete", "budget-exhausted", "error")
MAX_ATTEMPTS = 3                  # GATE §4: the initial attempt plus at most two retries, timeouts only
PER_REQUEST_TIMEOUT = 20.0


class ConfigError(Exception):
    pass


class BudgetExhausted(Exception):
    def __init__(self, which: str):
        super().__init__(which)
        self.which = which


@dataclass(frozen=True)
class Budget:
    boards: int
    requests: int
    seconds: float


def load_config(path) -> dict:
    cfg = json.loads(policy.read_bytes(path).decode("utf-8"))
    b = cfg.get("budgets") or {}
    if not all(isinstance(b.get(k), (int, float)) and b.get(k) > 0 for k in ("boards", "requests", "seconds")):
        raise ConfigError("budgets must give positive boards, requests and seconds")
    boards = cfg.get("boards")
    if not isinstance(boards, list) or not boards:
        raise ConfigError("boards must be a non-empty list")
    for x in boards:
        if x.get("provider") not in providers.PROVIDERS or not isinstance(x.get("slug"), str) or not x["slug"]:
            raise ConfigError(f"bad board entry: {x}")
    return cfg


def action_key(method: str, url: str) -> tuple:
    """GATE §3: the same method, normalised host, path, query parameters (incl. the pagination cursor)."""
    p = urlparse(url)
    return (method.upper(), (p.hostname or "").lower(), p.path, tuple(sorted(parse_qsl(p.query))))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)


def new_run_id() -> str:
    while True:
        rid = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        if not (policy.WRITE_ROOT / rid).exists():
            return rid
        time.sleep(1)


class _Run:
    def __init__(self, cfg, fetch, clock, sleep, run_id, log):
        self.cfg, self.fetch, self.clock, self.sleep, self.log = cfg, fetch, clock, sleep, log
        self.run_id = run_id
        self.dir = f"evidence/runs/{run_id}"
        self.budget = Budget(**{k: cfg["budgets"][k] for k in ("boards", "requests", "seconds")})
        self.t0 = clock()
        self.requests = 0
        self.seen: set = set()
        self.trace: list = []
        self.last_action = None

    def elapsed(self) -> float:
        return self.clock() - self.t0

    def emit(self, **event):
        event = {"t": round(self.elapsed(), 3), **event}
        self.trace.append(event)
        self.log("  " + " ".join(f"{k}={v}" for k, v in event.items() if k != "t"))

    def check_budget(self):
        if self.requests >= self.budget.requests:
            raise BudgetExhausted("requests")
        if self.elapsed() >= self.budget.seconds:
            raise BudgetExhausted("seconds")

    def attempt(self, board: dict, url: str, offset: int):
        """One action, retried only on timeout (GATE §4). Returns ('ok', status, body, raw) or (kind, detail)."""
        for attempt in range(MAX_ATTEMPTS):
            self.check_budget()
            self.requests += 1
            self.emit(event="request", board=board["slug"], url=url, attempt=attempt + 1, requests_used=self.requests)
            try:
                status, body = self.fetch(url, timeout=min(PER_REQUEST_TIMEOUT, max(0.1, self.budget.seconds - self.elapsed())))
            except TimeoutError as e:
                self.emit(event="timeout", board=board["slug"], attempt=attempt + 1, detail=str(e))
                if attempt + 1 < MAX_ATTEMPTS:
                    self.sleep(min(2 ** attempt, max(0.0, self.budget.seconds - self.elapsed())))
                    continue
                return ("timeout", f"{MAX_ATTEMPTS} attempts timed out")
            except policy.Refused as e:
                self.emit(event="refused", board=board["slug"], detail=str(e))
                return ("refused", str(e))
            except OSError as e:
                self.emit(event="network_error", board=board["slug"], detail=str(e))
                return ("network_error", str(e))
            raw = f"{self.dir}/raw/{_safe(board['provider'])}-{_safe(board['slug'])}-o{offset}-a{attempt + 1}.json"
            policy.write_bytes(raw, body)
            self.emit(event="response", board=board["slug"], status=status, bytes=len(body), raw=raw)
            self.last_action = f"GET {url} -> {status}"
            return ("ok", status, body, raw)

    def board(self, b: dict) -> dict:
        out = {"company": b.get("company", b["slug"]), "provider": b["provider"], "slug": b["slug"],
               "status": "failed", "reason": None, "postings": None, "board_total": None,
               "new_since_previous": None, "raw_paths": []}
        found, offset = [], 0

        def fail(reason: str) -> dict:
            out["reason"] = reason
            self.emit(event="board_done", board=b["slug"], status="failed", reason=reason)
            return out

        try:
            while True:
                url = providers.url(b["provider"], b["slug"], offset)
                key = action_key("GET", url)
                if key in self.seen:               # GATE §3: skip, record, and the board cannot finish
                    self.emit(event="repeat_guard", board=b["slug"], url=url)
                    return fail("repeat_guard")
                self.seen.add(key)
                res = self.attempt(b, url, offset)
                if res[0] != "ok":
                    return fail(res[0])
                _, status, body, raw = res
                out["raw_paths"].append(raw)
                if status == 404:
                    return fail("not_found")
                if status != 200:
                    return fail(f"http_{status}")
                try:
                    page, total = providers.parse(b["provider"], body)
                except providers.Malformed as e:
                    self.emit(event="malformed", board=b["slug"], detail=str(e))
                    return fail("malformed")
                found += page
                out["board_total"] = total
                if total is not None and len(found) < total:       # SmartRecruiters pages by offset
                    if not page:
                        return fail("truncated")
                    offset += len(page)
                    continue
                break
        except BudgetExhausted as e:
            self.emit(event="board_done", board=b["slug"], status="not_finished", reason=f"budget_exhausted:{e.which}")
            raise
        # NOTE: GATE §4 also asks that an empty 200 be accepted only once the board's identity is confirmed.
        # This first build checks structure only; the identity check is the change reviewed in REVIEW-PACKET.md.
        out["status"], out["postings"] = "success", len(found)
        out["new_since_previous"] = self.new_since_previous(b, found)
        policy.write_bytes(f"{self.dir}/postings/{_safe(b['provider'])}-{_safe(b['slug'])}.json",
                           json.dumps(found, ensure_ascii=False, indent=1).encode("utf-8"))
        self.emit(event="board_done", board=b["slug"], status="success", postings=len(found))
        return out

    def previous_postings(self, b: dict):
        """The most recent earlier run's saved postings for this board (read-only), or None."""
        name = f"{_safe(b['provider'])}-{_safe(b['slug'])}.json"
        if not policy.WRITE_ROOT.exists():
            return None
        for d in sorted((p for p in policy.WRITE_ROOT.iterdir() if p.is_dir() and p.name < self.run_id), reverse=True):
            f = d / "postings" / name
            if f.exists():
                return json.loads(policy.read_bytes(f.relative_to(policy.ROOT)).decode("utf-8"))
        return None

    def new_since_previous(self, b: dict, found: list):
        prev = self.previous_postings(b)
        if prev is None:
            return None
        seen = {p["id"] for p in prev}
        return sum(1 for p in found if p["id"] not in seen)


def run(cfg: dict, *, fetch=http.fetch, clock=time.monotonic, sleep=time.sleep, run_id=None, log=print) -> dict:
    started = _now()
    rid = run_id or new_run_id()
    r = None
    boards_out, status, budget_reached, error = [], None, None, None
    try:
        r = _Run(cfg, fetch, clock, sleep, rid, log)
        log(f"run {rid}: {len(cfg['boards'])} boards configured; budgets {r.budget}")
        for i, b in enumerate(cfg["boards"]):
            if i >= r.budget.boards:
                raise BudgetExhausted("boards")
            try:
                boards_out.append(r.board(b))
            except BudgetExhausted:
                boards_out.append({"company": b.get("company", b["slug"]), "provider": b["provider"], "slug": b["slug"],
                                   "status": "not_finished", "reason": "budget_exhausted", "postings": None,
                                   "board_total": None, "new_since_previous": None, "raw_paths": []})
                raise
        status = "finished" if all(x["status"] == "success" for x in boards_out) else "incomplete"
    except BudgetExhausted as e:
        status, budget_reached = "budget-exhausted", e.which
    except Exception as e:          # invalid config, unsafe condition, or a bug: never dressed up as success
        status, error = "error", f"{type(e).__name__}: {e}"
    done = {(x["provider"], x["slug"]) for x in boards_out if x["status"] != "not_finished"}
    summary = {
        "run_id": rid, "exit": status, "started_at": started, "finished_at": _now(),
        "budgets": cfg.get("budgets"), "budget_reached": budget_reached,
        "used": {"requests": r.requests if r else 0, "seconds": round(r.elapsed(), 2) if r else 0,
                 "boards": len(boards_out)},
        "boards": boards_out,
        "successful": [x["slug"] for x in boards_out if x["status"] == "success"],
        "failed": [{"slug": x["slug"], "reason": x["reason"]} for x in boards_out if x["status"] != "success"],
        "remaining": [b["slug"] for b in cfg.get("boards", []) if (b.get("provider"), b.get("slug")) not in done
                      and status == "budget-exhausted"],
        "total_postings_successful_boards": sum(x["postings"] for x in boards_out if x["status"] == "success"),
        "error": error, "last_completed_action": r.last_action if r else None,
        "outputs": {"trace": f"evidence/runs/{rid}/trace.jsonl", "summary": f"evidence/runs/{rid}/summary.json"},
    }
    try:
        if r:
            policy.write_bytes(summary["outputs"]["trace"],
                               "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in r.trace).encode("utf-8"))
        policy.write_bytes(summary["outputs"]["summary"], json.dumps(summary, indent=2, ensure_ascii=False).encode("utf-8"))
    except Exception as e:
        summary["exit"], summary["error"] = "error", f"could not persist outputs: {type(e).__name__}: {e}"
    return summary
