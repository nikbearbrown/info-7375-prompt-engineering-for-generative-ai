#!/usr/bin/env python3
"""SponsorScout board resolver v0.1. See CONTRACT.md.

Finds CANDIDATE public job boards (Greenhouse, Lever, Ashby) for the sponsors that have none
in boards.json. It proposes; a person approves at gate G1 (`decide`); `coverage` counts only
approvals. Python 3 standard library only.

  python resolver.py probe    --fixture fixtures/demo-transport.json --out-dir runs/demo
  python resolver.py probe    --live --out-dir runs/live-YYYY-MM-DD        # real GETs
  python resolver.py decide   --run runs/demo --company "YEXT INC" --ats greenhouse --slug yext \
                              --decision approve --by "Your Name" --seen-sha256 <first 12+ chars>
  python resolver.py coverage --run runs/demo

Network: only with --live, only GET, only boards-api.greenhouse.io, api.lever.co, api.ashbyhq.com.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS_ROOT = os.path.join(HERE, "runs")
DEFAULT_CANDIDATES = os.path.join(HERE, "inputs", "run-2-candidates.json")
DEFAULT_BOARDS = os.path.join(HERE, "inputs", "boards.json")

ATS_ORDER = ("greenhouse", "lever", "ashby")
ENDPOINTS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}
HUMAN_URLS = {
    "greenhouse": "https://boards.greenhouse.io/{slug}",
    "lever": "https://jobs.lever.co/{slug}",
    "ashby": "https://jobs.ashbyhq.com/{slug}",
}
ALLOWED_METHODS = frozenset({"GET"})
ALLOWED_HOSTS = frozenset(urllib.parse.urlsplit(u).hostname for u in ENDPOINTS.values())
USER_AGENT = "sponsorscout-board-resolver/" + VERSION  # Ashby returns 403 without one
HTTP_TIMEOUT = 15
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
CANARY_SLUG = "zz-sponsorscout-canary-0"

LEGAL = {"inc", "llc", "corp", "corporation", "co", "ltd", "lp", "llp", "plc", "company"}
DESCRIPTORS = {"technologies", "technology", "labs", "holdings", "group", "solutions", "hq",
               "systems", "partners", "international", "global", "interactive", "media",
               "network", "integrated", "and"}

HITS = ("name-match", "exists-no-name", "name-partial", "exists-empty", "name-mismatch")  # best first
STRONG = {"name-match", "exists-no-name"}
EXIT = {"done": 0, "budget": 4, "upstream-errors": 5, "canary-failed": 6}


class PolicyError(Exception):
    """Refused by the permission policy (exit 3)."""


class InputError(Exception):
    """Bad input or usage (exit 2)."""


class GateRefused(Exception):
    """Gate G1 refused a decision (exit 7)."""


class BudgetExhausted(Exception):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise InputError(f"can't read {path}: {e}")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ── names and slugs ─────────────────────────────────────────────────────────
def core_tokens(name):
    toks = re.sub(r"[^a-z0-9]+", " ", (name or "").lower().replace("&", " and ")).split()
    while toks and toks[-1] in LEGAL:
        toks.pop()
    return toks


def slug_candidates(company, aliases=None):
    """[(slug, rule)], aliases first, then at most 4 slugs derived from the name."""
    out = []
    for a in (aliases or {}).get(company, []):
        if not isinstance(a, str) or not SLUG_RE.match(a):
            raise InputError(f"alias slug {a!r} for {company} is not a valid slug")
        out.append((a, "alias"))
    core = core_tokens(company)
    stripped = [t for t in core if t not in DESCRIPTORS]
    derived = [("".join(core), "full")]
    if len(core) > 1:
        derived.append(("-".join(core), "hyphenated"))
    if stripped and stripped != core:
        derived.append(("".join(stripped), "descriptor-stripped"))
    if len(core) > 1 and len(core[0]) >= 4:
        derived.append((core[0], "first-word"))
    seen = {s for s, _ in out}
    for s, rule in derived:
        if s and s not in seen and SLUG_RE.match(s):
            out.append((s, rule)); seen.add(s)
    return out


def name_match(company, board_name):
    a, b = core_tokens(company), core_tokens(board_name)
    if a and "".join(a) == "".join(b):
        return "name-match"
    if (set(a) - DESCRIPTORS) & (set(b) - DESCRIPTORS):
        return "name-partial"
    return "name-mismatch"


# ── the tool and its permission policy ──────────────────────────────────────
def check_policy(method, url):
    parts = urllib.parse.urlsplit(url)
    if method not in ALLOWED_METHODS:
        raise PolicyError(f"method {method} not allowed")
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise PolicyError(f"host not allowed: {url}")


def check_out_dir(path):
    real, root = os.path.realpath(path), os.path.realpath(RUNS_ROOT)
    if real == root or os.path.commonpath([real, root]) != root:
        raise PolicyError(f"out-dir must be inside {RUNS_ROOT}: {path}")
    return real


class FixtureTransport:
    """Answers from a JSON file. URLs not listed get `default`, else 404. Never touches the network."""
    def __init__(self, path):
        fx = load_json(path)
        self.responses, self.default, self.label = fx.get("responses", {}), fx.get("default"), f"fixture:{os.path.basename(path)}"

    def __call__(self, url):
        r = self.responses.get(url, self.default) or {"status": 404, "body": {"fixture": "no entry"}}
        body = r.get("body", "")
        text = body if isinstance(body, str) else json.dumps(body)
        return {"status": r.get("status"), "body": text.encode("utf-8"), "error": r.get("error")}


class LiveTransport:
    def __init__(self, delay):
        self.delay, self.calls, self.label = delay, 0, "live"

    def __call__(self, url):
        if self.calls and self.delay:
            time.sleep(self.delay)
        self.calls += 1
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                return {"status": r.status, "body": r.read(), "error": None}
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": e.read() or b"", "error": f"HTTP {e.code}"}
        except Exception as e:  # timeout, DNS, connection reset
            return {"status": None, "body": b"", "error": f"{type(e).__name__}: {e}"}


class HttpTool:
    """The only way the resolver touches the outside world: policy check, then budget, then GET."""
    def __init__(self, transport, budget):
        self.transport, self.budget, self.used = transport, budget, 0

    def get(self, url):
        check_policy("GET", url)
        if self.used >= self.budget:
            raise BudgetExhausted()
        self.used += 1
        return self.transport(url)


# ── classify one response ───────────────────────────────────────────────────
def classify(ats, company, resp):
    status = resp["status"]
    if status == 404:
        return {"outcome": "not-found"}
    if status != 200:
        return {"outcome": "error", "detail": resp.get("error") or f"HTTP {status}"}
    try:
        data = json.loads(resp["body"].decode("utf-8", errors="replace"))
    except ValueError:
        return {"outcome": "error", "detail": "malformed-json"}
    if ats == "greenhouse":
        name = data.get("name") if isinstance(data, dict) else None
        if not name:
            return {"outcome": "error", "detail": "malformed-json"}
        return {"outcome": name_match(company, name) if company else "exists-no-name", "board_reported_name": name}
    jobs = data if ats == "lever" else (data.get("jobs") if isinstance(data, dict) else None)
    if not isinstance(jobs, list):
        return {"outcome": "error", "detail": "malformed-json"}
    return {"outcome": "exists-no-name" if jobs else "exists-empty", "posting_count": len(jobs)}


# ── probe: the loop ─────────────────────────────────────────────────────────
class Run:
    def __init__(self, out_dir, tool, max_errors):
        self.out, self.tool, self.max_errors = out_dir, tool, max_errors
        self.error_streak, self.cache = 0, {}
        os.makedirs(out_dir, exist_ok=True)
        self.log_f = open(os.path.join(out_dir, "log.jsonl"), "w", encoding="utf-8")

    def log(self, kind, **kw):
        self.log_f.write(json.dumps({"t": now(), "kind": kind, **kw}, ensure_ascii=False) + "\n")

    def probe_one(self, ats, slug, company):
        """act + record. Raises BudgetExhausted. Reuses an earlier response for the same board."""
        if (ats, slug) in self.cache:
            hit = dict(self.cache[(ats, slug)], reused=True)
            hit.update(classify(ats, company, {"status": hit["http_status"], "body": hit["_body"], "error": None})
                       if hit["http_status"] == 200 else {})
            return hit
        url = ENDPOINTS[ats].format(slug=slug)
        self.log("act", method="GET", url=url, request_no=self.tool.used + 1)
        resp = self.tool.get(url)
        text = resp["body"].decode("utf-8", errors="replace")
        rel = f"raw/{ats}/{slug}.json"
        digest = sha256_text(text)
        write_json(os.path.join(self.out, rel), {
            "url": url, "fetched_at": now(), "transport": self.tool.transport.label,
            "http_status": resp["status"], "error": resp["error"], "body_sha256": digest, "body_text": text})
        hit = {"ats": ats, "slug": slug, "url": url, "human_url": HUMAN_URLS[ats].format(slug=slug),
               "http_status": resp["status"], "sha256": digest, "raw_path": rel, "reused": False,
               "_body": text.encode("utf-8")}
        hit.update(classify(ats, company, resp))
        self.cache[(ats, slug)] = hit
        self.log("record", url=url, outcome=hit["outcome"], sha256=digest, raw_path=rel)
        self.error_streak = self.error_streak + 1 if hit["outcome"] == "error" else 0
        return hit

    def close(self):
        self.log_f.close()


def public(hit):
    return {k: v for k, v in hit.items() if not k.startswith("_")}


def company_status(c):
    outcomes = [p["outcome"] for p in c["probes"]]
    if any(o in HITS and o != "name-mismatch" for o in outcomes):
        return "proposed"
    if c["finished"] and "error" not in outcomes:
        return "mismatch-only" if "name-mismatch" in outcomes else "not-found"
    return "incomplete"


def select_companies(candidates, boards, only, limit):
    mapped = {b["company_name"] for b in boards["boards"] if b.get("confirmed")}
    unmapped = [c["company_name"]["value"] for c in candidates["candidates"]
                if c["company_name"]["value"] not in mapped and "no-board" in c.get("g1", "")]
    if only:
        bad = [o for o in only if o not in unmapped]
        if bad:
            raise InputError(f"not an unmapped candidate: {bad}")
        unmapped = [u for u in unmapped if u in only]
    return unmapped[:limit] if limit else unmapped


def cmd_probe(a):
    if a.live and a.fixture:
        raise InputError("give --live or --fixture, not both")
    if not (a.live or a.fixture):
        raise PolicyError("offline by default: pass --fixture FILE, or --live to make real GETs")
    out = check_out_dir(a.out_dir)
    candidates, boards = load_json(a.candidates), load_json(a.boards)
    aliases = load_json(a.aliases) if a.aliases else {}
    names = select_companies(candidates, boards, a.only, a.limit)
    plans = {n: slug_candidates(n, aliases) for n in names}  # validates aliases before any request
    transport = LiveTransport(a.delay) if a.live else FixtureTransport(a.fixture)
    run = Run(out, HttpTool(transport, a.budget), a.max_errors)
    companies = [{"company_name": n, "slugs_planned": [s for s, _ in plans[n]], "probes": [], "finished": False}
                 for n in names]
    started, stop = now(), "done"
    try:
        for ats in ATS_ORDER:  # canary: a made-up slug must come back not-found
            hit = run.probe_one(ats, CANARY_SLUG, None)
            if hit["outcome"] != "not-found":
                stop = f"canary-failed:{ats}"
                break
        if stop == "done":
            for c in companies:
                run.log("observe", company=c["company_name"], slugs_planned=c["slugs_planned"])
                strong = False
                for slug, rule in plans[c["company_name"]]:
                    for ats in ATS_ORDER:
                        run.log("decide", company=c["company_name"], next={"ats": ats, "slug": slug, "rule": rule})
                        hit = run.probe_one(ats, slug, c["company_name"])
                        hit["rule"] = rule
                        c["probes"].append(public(hit))
                        if run.error_streak >= run.max_errors:
                            stop = "upstream-errors"
                            raise StopIteration
                        if hit["outcome"] in STRONG:
                            strong = True
                            break
                    if strong:
                        break
                c["finished"] = True
                run.log("decide", company=c["company_name"], action="stop-company",
                        reason="strong-hit" if strong else "plan-exhausted")
    except BudgetExhausted:
        stop = "budget"
    except StopIteration:
        pass
    run.log("stop", reason=stop, requests_used=run.tool.used)
    run.close()

    for c in companies:
        c["status"] = company_status(c)
        hits = [p for p in c["probes"] if p["outcome"] in HITS]
        c["best"] = min(hits, key=lambda p: HITS.index(p["outcome"])) if hits else None
    counts = {}
    for c in companies:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    exit_code = EXIT[stop.split(":")[0]]
    summary = {
        "tool": "sponsorscout-board-resolver", "version": VERSION, "started_at": started, "finished_at": now(),
        "transport": transport.label, "budget": a.budget, "requests_used": run.tool.used,
        "max_errors": a.max_errors, "stop_reason": stop, "exit_code": exit_code,
        "companies_selected": len(companies), "status_counts": counts,
        "inputs": {"candidates": file_sha(a.candidates), "boards": file_sha(a.boards),
                   "aliases": file_sha(a.aliases) if a.aliases else None},
        "labels": "every board here is PROPOSED (model-free, rule-based). None is confirmed until G1 `decide`.",
    }
    write_json(os.path.join(out, "proposals.json"), {"companies": companies})
    write_json(os.path.join(out, "summary.json"), summary)
    write_review(out, companies, summary)
    print(f"probe: {stop} | {run.tool.used}/{a.budget} requests | " +
          " | ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"review: {os.path.join(out, 'review.md')}")
    return exit_code


def write_review(out, companies, summary):
    lines = [f"# G1 review — {os.path.basename(out)}", "",
             f"Transport **{summary['transport']}** · stop **{summary['stop_reason']}** · "
             f"{summary['requests_used']}/{summary['budget']} requests · {summary['status_counts']}", "",
             "Every row is a **proposal**. Open the board by hand, compare it with the company, then run the",
             "`decide` command with the hash shown (that binds your decision to this exact saved response).",
             "Lever and Ashby give no company name, so a hit there is only a slug that exists.", "",
             "| Company | ATS | Slug (rule) | Evidence | Open by hand | SHA-256 |", "|---|---|---|---|---|---|"]
    for c in companies:
        for p in c["probes"]:
            if p["outcome"] not in HITS:
                continue
            ev = p["outcome"] + (f": “{p['board_reported_name']}”" if p.get("board_reported_name") else "") + \
                (f": {p['posting_count']} postings" if "posting_count" in p else "")
            lines.append(f"| {c['company_name']} | {p['ats']} | `{p['slug']}` ({p['rule']}) | {ev} | "
                         f"{p['human_url']} | `{p['sha256'][:12]}` |")
    lines += ["", "Decide (approve / refuse / defer):", "", "```",
              f'python resolver.py decide --run "{out}" --company "<COMPANY>" --ats <ats> --slug <slug> \\',
              '  --decision approve --by "<your name>" --seen-sha256 <sha from the table>', "```", ""]
    with open(os.path.join(out, "review.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── gate G1 ─────────────────────────────────────────────────────────────────
def cmd_decide(a):
    out = check_out_dir(a.run)
    props = load_json(os.path.join(out, "proposals.json"))
    c = next((c for c in props["companies"] if c["company_name"] == a.company), None)
    if c is None:
        raise GateRefused(f"{a.company} is not in this run")
    p = next((p for p in c["probes"] if p["ats"] == a.ats and p["slug"] == a.slug), None)
    if p is None or p["outcome"] not in HITS:
        raise GateRefused(f"{a.ats}/{a.slug} is not a recorded hit for {a.company}")
    raw = load_json(os.path.join(out, p["raw_path"]))
    if sha256_text(raw.get("body_text", "")) != p["sha256"]:
        raise GateRefused(f"saved response {p['raw_path']} changed since it was recorded")
    seen = (a.seen_sha256 or "").lower()
    if len(seen) < 12 or not p["sha256"].startswith(seen):
        raise GateRefused("--seen-sha256 does not match the response on record (need >= 12 matching characters)")
    path = os.path.join(out, "decisions.json")
    log = load_json(path) if os.path.exists(path) else {"decisions": []}
    log["decisions"].append({
        "company_name": a.company, "ats": a.ats, "slug": a.slug, "decision": a.decision, "by": a.by,
        "decided_at": now(), "seen_sha256": p["sha256"], "raw_path": p["raw_path"], "human_url": p["human_url"],
        "evidence": p["outcome"], "board_reported_name": p.get("board_reported_name"), "note": a.note})
    write_json(path, log)
    print(f"G1: {a.decision} recorded for {a.company} -> {a.ats}/{a.slug} by {a.by}")
    return 0


# ── coverage ────────────────────────────────────────────────────────────────
def cmd_coverage(a):
    out = check_out_dir(a.run)
    candidates, boards = load_json(a.candidates), load_json(a.boards)
    names = {c["company_name"]["value"] for c in candidates["candidates"]}
    existing = {b["company_name"] for b in boards["boards"] if b.get("confirmed") and b["company_name"] in names}
    props = load_json(os.path.join(out, "proposals.json"))["companies"]
    dpath = os.path.join(out, "decisions.json")
    last = {}
    for d in (load_json(dpath)["decisions"] if os.path.exists(dpath) else []):
        last[d["company_name"]] = d
    approved = [d for n, d in last.items() if d["decision"] == "approve" and n not in existing]
    status = {c["company_name"]: c["status"] for c in props}
    reviewable = [n for n, s in status.items() if s in ("proposed", "mismatch-only")]
    cov = {
        "covered": len(existing) + len(approved), "total": len(names),
        "existing_confirmed": len(existing), "approved_new": len(approved),
        "refused": sum(d["decision"] == "refuse" for d in last.values()),
        "deferred": sum(d["decision"] == "defer" for d in last.values()),
        "proposed_unreviewed": sum(n not in last for n in reviewable),
        "not_found": sum(s == "not-found" for s in status.values()),
        "incomplete": sum(s == "incomplete" for s in status.values()),
        "computed_at": now(), "rule": "covered = confirmed in boards.json ∪ last G1 decision is approve. Proposals never count.",
    }
    new = [{"company_name": d["company_name"], "ats": d["ats"], "slug": d["slug"],
            "board_reported_name": d["board_reported_name"], "confirmed": True,
            "confirmed_by": f"{d['by']} (G1, {d['decided_at'][:10]})", "seen_sha256": d["seen_sha256"],
            "raw_path": d["raw_path"], "source_run": os.path.basename(out)} for d in approved]
    write_json(os.path.join(out, "boards.resolved.json"),
               {"_about": "boards.json (unchanged) plus boards approved at G1 by the resolver run named in source_run.",
                "boards": boards["boards"] + new})
    write_json(os.path.join(out, "coverage.json"), cov)
    md = [f"# Board coverage — {os.path.basename(out)}", "",
          f"**{cov['covered']} / {cov['total']}** companies have a confirmed board "
          f"({cov['existing_confirmed']} from 2026-10-03 + {cov['approved_new']} approved at G1).", "",
          "| | count |", "|---|---|"] + [f"| {k} | {cov[k]} |" for k in
          ("approved_new", "refused", "deferred", "proposed_unreviewed", "not_found", "incomplete")] + \
         ["", cov["rule"], ""]
    with open(os.path.join(out, "coverage.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"coverage: {cov['covered']}/{cov['total']}  (proposed, not yet reviewed: {cov['proposed_unreviewed']})")
    return 0


def safe_console():
    """A console that can't encode a character must never crash a command after it has
    written state (2026-11-23: `decide` saved an approval, then died printing on cp1252)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    safe_console()
    p = argparse.ArgumentParser(prog="resolver.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("probe")
    pr.add_argument("--candidates", default=DEFAULT_CANDIDATES)
    pr.add_argument("--boards", default=DEFAULT_BOARDS)
    pr.add_argument("--aliases")
    pr.add_argument("--out-dir", required=True)
    pr.add_argument("--live", action="store_true")
    pr.add_argument("--fixture")
    pr.add_argument("--budget", type=int, default=1000)
    pr.add_argument("--max-errors", type=int, default=5)
    pr.add_argument("--delay", type=float, default=1.0, help="seconds between live requests")
    pr.add_argument("--only", action="append")
    pr.add_argument("--limit", type=int)
    de = sub.add_parser("decide")
    de.add_argument("--run", required=True)
    de.add_argument("--company", required=True)
    de.add_argument("--ats", required=True, choices=ATS_ORDER)
    de.add_argument("--slug", required=True)
    de.add_argument("--decision", required=True, choices=("approve", "refuse", "defer"))
    de.add_argument("--by", required=True)
    de.add_argument("--seen-sha256", required=True)
    de.add_argument("--note")
    co = sub.add_parser("coverage")
    co.add_argument("--run", required=True)
    co.add_argument("--candidates", default=DEFAULT_CANDIDATES)
    co.add_argument("--boards", default=DEFAULT_BOARDS)
    try:
        a = p.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        return {"probe": cmd_probe, "decide": cmd_decide, "coverage": cmd_coverage}[a.cmd](a)
    except PolicyError as e:
        print(f"refused by policy: {e}", file=sys.stderr); return 3
    except InputError as e:
        print(f"input error: {e}", file=sys.stderr); return 2
    except GateRefused as e:
        print(f"G1 refused: {e}", file=sys.stderr); return 7


if __name__ == "__main__":
    sys.exit(main())
