"""Collection run (FILTER.md §C): three boards, with posting text, inside a request and time budget.

Exits follow JS2's GATE: finished / incomplete / budget-exhausted / error. A failed board is never reported as
zero postings, and a posting whose text could not be collected says why."""
from __future__ import annotations

import gzip
import hashlib
import json
import time
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

from . import http, policy

PER_REQUEST_TIMEOUT = 20.0
MAX_ATTEMPTS = 3               # the first attempt plus at most two retries, and only after a timeout (JS2 GATE §4)
SR_SECTIONS = ("companyDescription", "jobDescription", "qualifications", "additionalInformation")


class BudgetExhausted(Exception):
    def __init__(self, which: str):
        super().__init__(which)
        self.which = which


class Malformed(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def gz(data: bytes) -> bytes:
    return gzip.compress(data, mtime=0)


class Run:
    def __init__(self, cfg: dict, out_dir, fetch=http.fetch, clock=time.monotonic):
        self.cfg, self.out, self.fetch, self.clock = cfg, out_dir, fetch, clock
        self.budget = cfg["budget"]
        self.requests = 0
        self.t0 = clock()
        self.trace: list[dict] = []
        self.raw_files: dict[str, str] = {}

    def get(self, url: str, raw_name: str) -> tuple[int, bytes]:
        """One budgeted GET (with timeout retries). Every attempt counts against the request budget."""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if self.requests >= self.budget["requests"]:
                raise BudgetExhausted("requests")
            if self.clock() - self.t0 > self.budget["seconds"]:
                raise BudgetExhausted("seconds")
            self.requests += 1
            try:
                status, body = self.fetch(url, PER_REQUEST_TIMEOUT)
            except TimeoutError as e:
                self.trace.append({"t": _now(), "url": url, "attempt": attempt, "error": f"timeout: {e}"})
                continue
            self.trace.append({"t": _now(), "url": url, "attempt": attempt, "status": status, "bytes": len(body)})
            policy.write_bytes(self.out / "raw" / f"{raw_name}.json.gz", gz(body))
            self.raw_files[f"raw/{raw_name}.json.gz"] = hashlib.sha256(body).hexdigest()
            return status, body
        raise TimeoutError(f"{MAX_ATTEMPTS} attempts timed out")


def _json(body: bytes):
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise Malformed(f"body is not UTF-8 JSON: {e}") from None


def _greenhouse(run: Run, slug: str) -> list[dict]:
    status, body = run.get(f"https://boards-api.greenhouse.io/v1/boards/{quote(slug, safe='')}/jobs?content=true",
                           f"{slug}-list")
    if status != 200:
        raise _BoardFailed("not_found" if status == 404 else f"http_{status}")
    d = _json(body)
    if not isinstance(d, dict) or not isinstance(d.get("jobs"), list):
        raise Malformed("Greenhouse body has no 'jobs' list")
    out = []
    for j in d["jobs"]:
        content = j.get("content") or ""
        out.append({"board": slug, "system": "greenhouse", "id": str(j["id"]), "title": (j.get("title") or "").strip(),
                    "location": {"name": ((j.get("location") or {}).get("name") or ""), "country": None,
                                 "remote": None, "other": []},
                    "text_format": "html", "text": content or None, "text_missing": None if content else "empty",
                    "url": j.get("absolute_url"), "updated_at": j.get("updated_at")})
    return out


def _ashby_country(addr) -> str | None:
    return (((addr or {}).get("postalAddress") or {}).get("addressCountry")) or None


def _ashby(run: Run, slug: str) -> list[dict]:
    status, body = run.get(f"https://api.ashbyhq.com/posting-api/job-board/{quote(slug, safe='')}", f"{slug}-list")
    if status != 200:
        raise _BoardFailed("not_found" if status == 404 else f"http_{status}")
    d = _json(body)
    if not isinstance(d, dict) or not isinstance(d.get("jobs"), list):
        raise Malformed("Ashby body has no 'jobs' list")
    out = []
    for j in d["jobs"]:
        text = j.get("descriptionPlain") or ""
        other = [{"name": s.get("location") or "", "country": _ashby_country(s.get("address"))}
                 for s in (j.get("secondaryLocations") or [])]
        out.append({"board": slug, "system": "ashby", "id": str(j["id"]), "title": (j.get("title") or "").strip(),
                    "location": {"name": j.get("location") or "", "country": _ashby_country(j.get("address")),
                                 "remote": j.get("isRemote"), "workplace_type": j.get("workplaceType"),
                                 "other": other},
                    "text_format": "plain", "text": text or None, "text_missing": None if text else "empty",
                    "url": j.get("jobUrl"), "updated_at": j.get("publishedAt")})
    return out


def _smartrecruiters(run: Run, slug: str) -> tuple[list[dict], str | None]:
    """Returns (postings, budget_reason or None). Text comes from one detail call per posting."""
    q = urlencode({"limit": 100, "offset": 0})
    status, body = run.get(f"https://api.smartrecruiters.com/v1/companies/{quote(slug, safe='')}/postings?{q}",
                           f"{slug}-list")
    if status != 200:
        raise _BoardFailed("not_found" if status == 404 else f"http_{status}")
    d = _json(body)
    if not isinstance(d, dict) or not isinstance(d.get("content"), list) or not isinstance(d.get("totalFound"), int):
        raise Malformed("SmartRecruiters body needs a 'content' list and an integer 'totalFound'")
    if d["totalFound"] > len(d["content"]):
        raise _BoardFailed(f"pagination_not_supported: totalFound {d['totalFound']} > {len(d['content'])}")
    out = []
    for j in sorted(d["content"], key=lambda x: str(x["id"])):
        loc = j.get("location") or {}
        out.append({"board": slug, "system": "smartrecruiters", "id": str(j["id"]),
                    "title": (j.get("name") or "").strip(),
                    "location": {"name": loc.get("fullLocation") or "", "country": loc.get("country"),
                                 "remote": loc.get("remote"), "other": []},
                    "text_format": "html", "text": None, "text_missing": "not_fetched",
                    "url": f"https://jobs.smartrecruiters.com/{slug}/{j['id']}", "updated_at": j.get("releasedDate")})
    budget_reason = None
    for p in out:
        url = f"https://api.smartrecruiters.com/v1/companies/{quote(slug, safe='')}/postings/{quote(p['id'], safe='')}"
        try:
            status, body = run.get(url, f"{slug}-detail-{p['id']}")
        except BudgetExhausted as e:
            budget_reason = e.which
            p["text_missing"] = f"budget_{e.which}"
            continue
        except TimeoutError:
            p["text_missing"] = "detail_timeout"
            continue
        if status != 200:
            p["text_missing"] = f"detail_http_{status}"
            continue
        try:
            det = _json(body)
            sections = (det.get("jobAd") or {}).get("sections") or {}
        except (Malformed, AttributeError):
            p["text_missing"] = "detail_malformed"
            continue
        parts = []
        for key in SR_SECTIONS:
            sec = sections.get(key) or {}
            if (sec.get("text") or "").strip():
                parts.append(f"<h3>{sec.get('title') or key}</h3>{sec['text']}")
        p["text"] = "\n".join(parts) or None
        p["text_missing"] = None if p["text"] else "empty"
    return out, budget_reason


class _BoardFailed(Exception):
    pass


SYSTEMS = {"greenhouse": _greenhouse, "ashby": _ashby, "smartrecruiters": _smartrecruiters}


def collect(cfg: dict, out_dir, fetch=http.fetch, clock=time.monotonic, run_id: str | None = None) -> dict:
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out = out_dir / run_id
    run = Run(cfg, out, fetch, clock)
    started = _now()
    postings: list[dict] = []
    boards: list[dict] = []
    budget_hit = None
    for b in cfg["boards"]:
        entry = {"board": b["board"], "system": b["system"]}
        if budget_hit:
            entry.update(status="not_attempted", reason=f"budget_{budget_hit}")
            boards.append(entry)
            continue
        try:
            result = SYSTEMS[b["system"]](run, b["board"])
            got, reason = result if isinstance(result, tuple) else (result, None)
            if reason:
                budget_hit = reason
            if not got:
                entry.update(status="failed", reason="empty_unconfirmed")   # JS2 ef6456a: an empty 200 is not proof
            else:
                entry.update(status="ok", postings=len(got))
            postings.extend(got)
        except BudgetExhausted as e:
            budget_hit = e.which
            entry.update(status="failed", reason=f"budget_{e.which}")
        except _BoardFailed as e:
            entry.update(status="failed", reason=str(e))
        except (Malformed, TimeoutError, KeyError, TypeError) as e:
            entry.update(status="failed", reason=f"{type(e).__name__}: {e}")
        mine = [p for p in postings if p["board"] == b["board"]]
        missing: dict[str, int] = {}
        for p in mine:
            if p["text_missing"]:
                missing[p["text_missing"]] = missing.get(p["text_missing"], 0) + 1
        entry.update(with_text=sum(1 for p in mine if p["text"]), without_text=missing)
        boards.append(entry)

    if budget_hit:
        exit_ = "budget-exhausted"
    elif any(x["status"] != "ok" for x in boards):
        exit_ = "incomplete"
    else:
        exit_ = "finished"
    lines = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in postings).encode("utf-8")
    policy.write_bytes(out / "postings.jsonl.gz", gz(lines))
    policy.write_bytes(out / "trace.jsonl",
                       "".join(json.dumps(t) + "\n" for t in run.trace).encode("utf-8"))
    summary = {"run_id": run_id, "sources_version": cfg["version"], "started_at": started, "finished_at": _now(),
               "exit": exit_, "budget": cfg["budget"], "requests_used": run.requests,
               "seconds_used": round(clock() - run.t0, 1), "boards": boards, "postings_total": len(postings),
               "postings_sha256": hashlib.sha256(lines).hexdigest(), "raw_sha256": run.raw_files}
    policy.write_bytes(out / "summary.json", (json.dumps(summary, indent=2) + "\n").encode("utf-8"))
    return summary


def load_postings(run_dir) -> list[dict]:
    with gzip.open(policy.check_read(run_dir / "postings.jsonl.gz"), "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
