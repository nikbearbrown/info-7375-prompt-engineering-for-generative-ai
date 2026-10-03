#!/usr/bin/env python3
"""daily_check.py — daily check of my target companies' job boards for entry-level data roles.

One command, run each morning from the repo root:

    python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample
    python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py \
        --candidate <candidate.json> --targets <targets.json> --out-dir <folder>

Recipe: recipes/cases/2026fa/atharvahambir-reallocation-engine.md

What one run does:
  G0  Intake gate: the candidate's dates and limits are present and not already past, the target
      list parses, and the data, fetcher and scorer this run depends on exist. Fails → exit 2.
  1.  Per target company: resolve the board (Greenhouse or Ashby only), look the company up in the
      80 Days sponsorship CSV (exact name match — never fuzzy), read E-Verify and hiring time from
      the target list.
  2.  Fetch each board once through the greenhouse-watch skill's fetcher (host allow-list, no
      redirects) — or read a saved response with --boards-dir (offline runs and tests).
  3.  Filter postings: title family, excluded title words, US / US-remote, stated years of experience.
  4.  Diff against the state file: new today / still open / closed since the last run.
  5.  Write roles.json (sponsorship vote, fit vote, liveness gate, timeline gate — each with its
      source label) and run the EXISTING scorer, scripts/score/role-scorer.mjs. No copy of it here.
  6.  Apply the recipe's own gates the scorer doesn't model (E-Verify; sponsorship with no record →
      held for the person), then write daily-check.json (for an agent) and daily-check.md (for me).

Every value carries a source label: record | model-judgment | your-input. A missing value is
reported missing and the posting is held for the person — it is never filled in.

Stdlib only. Exit: 0 ran · 2 stopped at the intake gate · 3 scorer failed · 4 no company checked.
"""
import argparse
import ast
import csv
import datetime as dt
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
from pathlib import Path
from urllib.parse import unquote, urlparse

RECIPE_ID = "atharvahambir-reallocation-engine"
RECIPE_VERSION = "0.1.0"


def find_repo(start):
    """Walk up to the repo root, so a copy of this file (e.g. a break-attempt mutant) runs from anywhere inside it."""
    for p in (start, *start.parents):
        if (p / "SNICKERDOODLE.md").is_file() and (p / "scripts" / "score" / "role-scorer.mjs").is_file():
            return p
    sys.exit(f"daily_check: no repo root (SNICKERDOODLE.md + scripts/score/role-scorer.mjs) above {start}")


HERE = Path(__file__).resolve().parent
REPO = find_repo(HERE)
COMPONENT = REPO / "scripts" / "contrib" / "2026fa" / RECIPE_ID
SPONSOR_CSV = REPO / "data" / "80-days-to-stay" / "80-days-csv" / "mapped_student_employment_targets_v3.csv"
BLS_CSV = REPO / "data" / "bls" / "compact" / "soc_occupation_compact.csv"
SCORER = REPO / "scripts" / "score" / "role-scorer.mjs"
FETCHER = REPO / ".claude" / "skills" / "greenhouse-watch" / "scripts" / "greenhouse_watch.py"
FIXTURES = COMPONENT / "fixtures"
PERSONA = REPO / "search" / "examples" / "atharva"   # fictional persona the sample runs as
SAMPLE_TODAY = "2026-10-01"

RECORD, MODEL, INPUT = "record", "model-judgment", "your-input"
SOURCES = (RECORD, MODEL, INPUT)

# ── Recipe parameters. None of these is pinned by the book; each is a proposal, recorded in the
#    run log so a reader can see which rule produced which label. ────────────────────────────────
TIER_RULE = {"proven_min_approvals": 10, "proven_min_approval_rate": 90.0, "likely_min_approvals": 1}
TIER_P = {"Proven": 0.9, "Likely": 0.6, "Avoid": 0.0}  # Proven/Likely p = data/examples/ch11-roles.json
LOW_APPROVAL_RATE = 75.0   # flag only; does not change the tier
LONG_OPEN_DAYS = 60        # flag only ("posting open a long time — ask a contact if it is real")
TIMELINE_CURVE = ("expected start = today + hiring weeks; slack = cliff − expected start; "
                  "factor 0 if slack < 0, 1 if slack ≥ buffer days, else slack ÷ buffer days")
SPONSOR_COLS = {"company_name", "Total Approvals", "Total Denials", "Approval_Rate",
                "top_job_titles_sponsored", "median_salary_offered", "latest_funding_stage", "latest_funding_date"}
COMPANY_SUFFIXES = {"inc", "incorporated", "llc", "corp", "corporation", "co", "company", "ltd",
                    "limited", "lp", "llp", "plc", "pbc", "pc"}


class StopRun(Exception):
    """The intake gate failed: stop before anything is fetched or scored."""


class BoardError(Exception):
    """One board could not be read today; other companies still run."""


def val(value, source, **detail):
    """A value together with where it came from. Every reported value goes through here."""
    if source not in SOURCES:
        raise ValueError(f"unknown source label {source!r}")
    out = {"value": value, "source": source}
    out.update({k: v for k, v in detail.items() if v is not None})
    return out


def rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def plain(text):
    """HTML (or HTML-escaped HTML, as Greenhouse sends it) → plain text."""
    t = html.unescape(html.unescape(text or ""))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def norm_text(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower())).strip()


def has_phrase(phrase, normalized_text):
    p = re.escape(norm_text(phrase))
    return bool(p) and re.search(rf"(?<![a-z0-9]){p}(?![a-z0-9])", normalized_text) is not None


# ═══════════════════════════════════════════════════════════════ inputs + intake gate (G0)
def load_structured(path, what):
    p = Path(path)
    if not p.exists():
        raise StopRun(f"{what} not found: {path}")
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yml", ".yaml"):
        try:
            import yaml  # optional: only for people who keep their files in YAML
        except ImportError:
            raise StopRun(f"{what} is YAML but PyYAML is not installed — use the JSON form, or activate the repo .venv")
        data = yaml.safe_load(text)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise StopRun(f"{what} is not valid JSON ({path}): {e}")
    if not isinstance(data, dict):
        raise StopRun(f"{what} must be an object at the top level ({path})")
    return data


def need_date(v, field):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if not isinstance(v, str) or not v.strip():
        raise StopRun(f"{field} is missing — fill it in (YYYY-MM-DD); there is no default")
    try:
        return dt.date.fromisoformat(v.strip())
    except ValueError:
        raise StopRun(f"{field} is not a date: {v!r} (expected YYYY-MM-DD)")


def need_number(v, field, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise StopRun(f"{field} is missing or not a number — fill it in; there is no default")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise StopRun(f"{field} must be between {lo} and {hi} (got {v})")
    return v


def check_candidate(c, today):
    """G0 for the candidate file. Returns the parsed constraints; raises StopRun on any gap."""
    visa = c.get("visa")
    search = c.get("search")
    if not isinstance(visa, dict) or not isinstance(search, dict):
        raise StopRun("candidate file needs a 'visa' object and a 'search' object")
    auth = c.get("authorization")
    if not isinstance(auth, str) or not auth.strip():
        raise StopRun("authorization is missing (e.g. \"F-1 OPT — needs H-1B sponsorship\"); the scorer reads it")
    v = {
        "opt_end_date": need_date(visa.get("opt_end_date"), "visa.opt_end_date"),
        "unemployment_days_used": need_number(visa.get("unemployment_days_used"), "visa.unemployment_days_used", 0),
        "unemployment_days_as_of": need_date(visa.get("unemployment_days_as_of"), "visa.unemployment_days_as_of"),
        "unemployment_limit_days": need_number(visa.get("unemployment_limit_days"), "visa.unemployment_limit_days", 1),
        "buffer_days": need_number(visa.get("buffer_days"), "visa.buffer_days", 0),
    }
    if not isinstance(visa.get("needs_e_verify_employer"), bool):
        raise StopRun("visa.needs_e_verify_employer must be true or false (a DSO question — the recipe never decides it)")
    v["needs_e_verify_employer"] = visa["needs_e_verify_employer"]
    if v["opt_end_date"] <= today:
        raise StopRun(f"OPT end date {v['opt_end_date']} is not after today {today}: there is no runway to score against")
    if v["unemployment_days_as_of"] > today:
        raise StopRun(f"visa.unemployment_days_as_of {v['unemployment_days_as_of']} is after today {today}")

    titles = search.get("titles")
    if not isinstance(titles, list) or not titles:
        raise StopRun("search.titles is missing — list the title phrases to match, each with a fit value")
    fams = []
    for i, t in enumerate(titles):
        if not isinstance(t, dict) or not isinstance(t.get("phrase"), str) or not t["phrase"].strip():
            raise StopRun(f"search.titles[{i}] needs a 'phrase'")
        fams.append({"phrase": norm_text(t["phrase"]),
                     "fit": need_number(t.get("fit"), f"search.titles[{i}].fit ({t['phrase']})", 0, 1),
                     "soc": t.get("soc")})
    words = {}
    for key in ("exclude_title_words", "flag_title_words"):
        w = search.get(key, [])
        if not isinstance(w, list) or not all(isinstance(x, str) for x in w):
            raise StopRun(f"search.{key} must be a list of words")
        words[key] = [norm_text(x) for x in w if norm_text(x)]
    return {
        "authorization": auth.strip(),
        "visa": v,
        "families": sorted(fams, key=lambda f: -len(f["phrase"])),
        "exclude_title_words": words["exclude_title_words"],
        "flag_title_words": words["flag_title_words"],
        "max_years": need_number(search.get("max_years_experience"), "search.max_years_experience", 0, 30),
    }


def check_targets(t):
    comps = t.get("companies")
    if not isinstance(comps, list) or not comps:
        raise StopRun("targets file has no 'companies' list — add at least one company and its board link")
    default_weeks = need_number((t.get("defaults") or {}).get("hiring_weeks"), "targets.defaults.hiring_weeks", 0, 104)
    seen = set()
    for i, c in enumerate(comps):
        if not isinstance(c, dict) or not isinstance(c.get("name"), str) or not c["name"].strip():
            raise StopRun(f"targets.companies[{i}] needs a 'name'")
        if not isinstance(c.get("board"), str) or not c["board"].strip():
            raise StopRun(f"targets.companies[{i}] ({c['name']}) needs a 'board' link")
        if c["name"].strip().lower() in seen:
            raise StopRun(f"company listed twice in targets: {c['name']}")
        seen.add(c["name"].strip().lower())
        if "hiring_weeks" in c:
            need_number(c["hiring_weeks"], f"targets.companies[{i}].hiring_weeks ({c['name']})", 0, 104)
        ev = c.get("e_verify")
        if ev is not None and (not isinstance(ev, dict) or ev.get("enrolled") not in (True, False, None)):
            raise StopRun(f"targets.companies[{i}].e_verify must look like {{\"enrolled\": true|false|null, \"source\": \"...\"}}")
        so = c.get("sponsorship_override")
        if so is not None and (not isinstance(so, dict) or so.get("tier") not in TIER_P or not str(so.get("source") or "").strip()):
            raise StopRun(f"targets.companies[{i}].sponsorship_override needs a tier ({'/'.join(TIER_P)}) and a source")
    return default_weeks


# ═══════════════════════════════════════════════════════════════ visa timeline (a gate)
def runway(visa, today):
    """The last day a new job can start: the earlier of the OPT end date and the day the
    unemployment allowance runs out (assumes still unemployed since `as_of`)."""
    used_today = visa["unemployment_days_used"] + (today - visa["unemployment_days_as_of"]).days
    left = visa["unemployment_limit_days"] - used_today
    unemp_end = today + dt.timedelta(days=left)
    cliff = min(visa["opt_end_date"], unemp_end)
    return {
        "unemployment_days_used_today": used_today,
        "unemployment_days_left": left,
        "unemployment_runs_out": unemp_end,
        "opt_end_date": visa["opt_end_date"],
        "cliff": cliff,
        "binding": "OPT end date" if visa["opt_end_date"] <= unemp_end else "unemployment allowance",
    }


def timeline_factor(today, cliff, hiring_weeks, buffer_days):
    start = today + dt.timedelta(days=round(hiring_weeks * 7))
    slack = (cliff - start).days
    if slack < 0:
        f = 0.0
    elif buffer_days <= 0 or slack >= buffer_days:
        f = 1.0
    else:
        f = slack / buffer_days
    return round(f, 3), start, slack


# ═══════════════════════════════════════════════════════════════ posting filters
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_N = r"(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"
_PAREN = r"(?:\(\s*\d{1,2}\s*\)\s*)?"
YEARS_RE = re.compile(
    rf"(?<![\w.$]){_N}\s*{_PAREN}(\+|plus)?\s*(?:(?:-|–|—|to)\s*{_N}\s*{_PAREN}\+?\s*)?(?:or more\s+)?(?:years?|yrs?)\b",
    re.I)
NOT_EXPERIENCE = re.compile(r"^[\s-]*(degree|college|university|program|bachelor|master|of (college|university|school))", re.I)


def _num(s):
    s = s.lower()
    return int(s) if s.isdigit() else NUM_WORDS[s]


def parse_experience(text, max_years):
    """Years of experience the posting states. Returns (status, mentions).
    status: within (every stated number ≤ max) · above (every minimum > max) ·
            mixed (some of each, or a range crossing max) · not-stated."""
    t = plain(text)
    mentions = []
    for m in YEARS_RE.finditer(t):
        after, before = t[m.end():m.end() + 60], t[max(0, m.start() - 40):m.start()]
        if NOT_EXPERIENCE.match(after) or "experience" not in (before + " " + after).lower():
            continue
        lo = _num(m.group(1))
        hi = _num(m.group(3)) if m.group(3) else None
        if lo > 30 or (hi is not None and (hi > 30 or hi < lo)):
            continue
        mentions.append({"min": lo, "max": hi, "text": t[max(0, m.start() - 30):m.end() + 40].strip()})
    if not mentions:
        return "not-stated", mentions
    if min(x["min"] for x in mentions) > max_years:
        return "above", mentions
    if all(x["min"] <= max_years and (x["max"] is None or x["max"] <= max_years) for x in mentions):
        return "within", mentions
    return "mixed", mentions


US_STATES = ("alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|"
             "idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|"
             "minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|"
             "north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|"
             "tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming|district of columbia")
US_CITIES = ("san francisco|new york city|nyc|seattle|chicago|boston|austin|los angeles|denver|atlanta|"
             "bay area|silicon valley|palo alto|mountain view|menlo park|san jose|sunnyvale|san mateo|redwood city|"
             "oakland|miami|dallas|houston|philadelphia|pittsburgh|detroit|minneapolis|salt lake city|phoenix|"
             "san diego|raleigh|nashville|brooklyn|jersey city|washington dc|washington d c")
NON_US = ("canada|toronto|vancouver|montreal|ontario|mexico|mexico city|brazil|sao paulo|são paulo|argentina|"
          "united kingdom|uk|england|london|ireland|dublin|germany|berlin|munich|france|paris|netherlands|"
          "amsterdam|spain|madrid|barcelona|portugal|lisbon|poland|warsaw|krakow|sweden|stockholm|switzerland|"
          "zurich|israel|tel aviv|india|bengaluru|bangalore|hyderabad|pune|chennai|mumbai|delhi|gurgaon|"
          "singapore|japan|tokyo|korea|seoul|china|shanghai|beijing|hong kong|taiwan|australia|sydney|melbourne|"
          "new zealand|philippines|manila|emea|apac|latam")
_US_TOKEN = re.compile(r"(?<![A-Za-z])(US|USA|U\.S\.A?\.?)(?![A-Za-z])")
_US_WORDS = re.compile(rf"\bunited states\b|\b({US_STATES})\b|\b({US_CITIES})\b", re.I)
_US_STATE_CODE = re.compile(r",\s*(A[LKZR]|C[AOT]|D[EC]|FL|GA|HI|I[DLNA]|K[SY]|LA|M[EDAINSOT]|N[EVHJMYCD]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[TA]|W[AVIY])\b")
_NON_US = re.compile(rf"\b({NON_US})\b", re.I)
_REMOTE = re.compile(r"\bremote\b", re.I)


def classify_location(texts, is_remote=False, countries=()):
    """us · us-remote (kept) · remote-unverified · unverified (kept, flagged) · non-us (excluded)."""
    blob = " | ".join(x for x in texts if x)
    us = (any(norm_text(c) in ("united states", "usa", "us") for c in countries if c)
          or bool(_US_TOKEN.search(blob) or _US_WORDS.search(blob) or _US_STATE_CODE.search(blob)))
    remote = bool(is_remote) or bool(_REMOTE.search(blob))
    if us:
        return "us-remote" if remote else "us"
    if any(c for c in countries) or _NON_US.search(blob):
        return "non-us"
    return "remote-unverified" if remote else "unverified"


def match_title(title, cand):
    """(family or None, excluded words, flag words)."""
    nt = norm_text(title)
    fam = next((f for f in cand["families"] if has_phrase(f["phrase"], nt)), None)
    excl = [w for w in cand["exclude_title_words"] if has_phrase(w, nt)]
    flag = [w for w in cand["flag_title_words"] if has_phrase(w, nt)]
    return fam, excl, flag


# ═══════════════════════════════════════════════════════════════ sponsorship (80 Days CSV)
def norm_company(name):
    toks = re.sub(r"[^a-z0-9]+", " ", (name or "").lower().replace("&", " and ")).split()
    while toks and toks[-1] in COMPANY_SUFFIXES:
        toks.pop()
    if toks and toks[0] == "the":
        toks = toks[1:]
    return "".join(toks)


def _f(x):
    try:
        return float(str(x).strip())
    except ValueError:
        return None


def parse_title_list(s):
    s = (s or "").strip()
    if not s:
        return []
    try:
        v = ast.literal_eval(s)
        if isinstance(v, (list, tuple)):
            return [str(x).strip() for x in v if str(x).strip()]
    except (ValueError, SyntaxError):
        pass
    return [x.strip(" '\"") for x in s.strip("[]").split(",") if x.strip(" '\"")]


class SponsorIndex:
    """The 80 Days CSV, indexed by normalized company name. Exact matches only."""

    def __init__(self, path):
        if not path.exists():
            raise StopRun(f"sponsorship data not found: {rel(path)}")
        self.path = path
        self.by_norm, self.by_upper, self.sig = {}, {}, {}
        self.rows = 0
        self.rows_h1b = 0
        with open(path, encoding="utf-8", errors="replace", newline="") as f:
            r = csv.DictReader(f)
            missing = SPONSOR_COLS - set(r.fieldnames or [])
            if missing:
                raise StopRun(f"sponsorship CSV is missing columns {sorted(missing)} — its schema changed")
            for row in r:
                self.rows += 1
                name = (row.get("company_name") or "").strip()
                if not name:
                    continue
                self.by_norm.setdefault(norm_company(name), []).append(row)
                self.by_upper.setdefault(name.upper(), []).append(row)
                if _f(row["Total Approvals"]) is not None:
                    self.rows_h1b += 1
                    key = (row["Total Approvals"], row["Total Denials"], row["Approval_Rate"],
                           row["median_salary_offered"], row["top_job_titles_sponsored"])
                    self.sig.setdefault(key, set()).add(name)

    def _similar(self, key, exclude, h1b_only):
        """Rows whose normalized name starts with (or is a prefix of) this one. A hint for the person
        only — never used as a match."""
        if len(key) < 4:
            return []
        out = []
        for k, rows in self.by_norm.items():
            if k != key and (k.startswith(key) or key.startswith(k)) and len(k) >= 4:
                for row in rows:
                    a = _f(row["Total Approvals"])
                    if row["company_name"].strip() in exclude or (h1b_only and a is None):
                        continue
                    out.append((a if a is not None else -1, row["company_name"].strip()))
        return [f"{n} ({int(a)} approvals)" if a >= 0 else f"{n} (no H-1B fields)"
                for a, n in sorted(out, reverse=True)[:3]]

    def lookup(self, company, families):
        name, csv_name = company["name"].strip(), (company.get("csv_name") or "").strip()
        key = norm_company(name)
        if csv_name:
            rows = self.by_upper.get(csv_name.upper(), [])
            how = val(f"csv_name given in targets: {csv_name}", INPUT)
        else:
            rows = self.by_norm.get(key, [])
            how = val("exact match on normalized company name (no fuzzy matching)", RECORD)
        res = {"match_method": how}
        if not rows:
            res["did_you_mean"] = self._similar(norm_company(csv_name) if csv_name else key, set(), h1b_only=False)
            hint = (f" — the data has similar names: {'; '.join(res['did_you_mean'])}; if one is this company, "
                    "set csv_name in targets") if res["did_you_mean"] else ""
            res.update(status="no-row",
                       hold=f"no row named '{csv_name or name}' in the sponsorship data{hint} — unknown, not 'does not sponsor'")
            return res
        if len(rows) > 1:
            names = sorted({r["company_name"].strip() for r in rows})
            res.update(status="ambiguous", hold=f"{len(rows)} rows match ({'; '.join(names)}) — set csv_name in targets")
            return res
        row = rows[0]
        matched = row["company_name"].strip()
        res["csv_row"] = val(matched, RECORD)
        res["similar_names_with_h1b"] = self._similar(norm_company(matched), {matched}, h1b_only=True)
        res["latest_funding"] = val(
            {"stage": row["latest_funding_stage"] or None, "date": row["latest_funding_date"] or None}, RECORD,
            note="80 Days CSV column; its provenance is not documented — shown, not used")
        a, d, rate = _f(row["Total Approvals"]), _f(row["Total Denials"]), _f(row["Approval_Rate"])
        if a is None:
            res.update(status="no-h1b-fields",
                       hold=f"'{matched}' is in the data but has no H-1B history fields — unknown, not 'does not sponsor'")
            return res
        titles = parse_title_list(row["top_job_titles_sponsored"])
        res.update(
            approvals=val(a, RECORD), denials=val(d, RECORD),
            approval_rate=val(round(rate, 1) if rate is not None else None, RECORD),
            median_salary_offered=val(_f(row["median_salary_offered"]), RECORD, note="all sponsored roles, not role-specific"),
            top_titles=val(titles, RECORD, note="at most 5 titles are listed; absence of a title is weak evidence"),
        )
        nts = [norm_text(t) for t in titles]
        hits = [t for t, nt in zip(titles, nts) if any(has_phrase(f["phrase"], nt) for f in families)]
        res["sponsored_matching_title"] = val(hits, RECORD, note="titles in the ≤5 listed that contain one of your title phrases")
        twins = sorted(self.sig.get((row["Total Approvals"], row["Total Denials"], row["Approval_Rate"],
                                     row["median_salary_offered"], row["top_job_titles_sponsored"]), set()) - {matched})
        if twins:
            res.update(status="duplicate-record", twins=twins,
                       hold=f"H-1B fields identical to {', '.join(twins)} — likely a join artifact, not trusted as a record")
            return res
        if a >= TIER_RULE["proven_min_approvals"] and rate is not None and rate >= TIER_RULE["proven_min_approval_rate"]:
            tier = "Proven"
        elif a >= TIER_RULE["likely_min_approvals"]:
            tier = "Likely"
        else:
            res.update(status="no-h1b-fields", hold=f"'{matched}' shows 0 approvals — no record of sponsoring")
            return res
        flags = []
        if rate is not None and rate < LOW_APPROVAL_RATE:
            flags.append(f"approval rate {rate:.0f}% is below {LOW_APPROVAL_RATE:.0f}%")
        if res["similar_names_with_h1b"]:
            flags.append("other companies with a similar name have H-1B records — confirm this is the right row")
        if not hits:
            flags.append("none of the ≤5 listed sponsored titles is one of your title phrases")
        res.update(status="record", tier=val(tier, RECORD, rule=TIER_RULE), flags=flags,
                   p=val(TIER_P[tier], RECORD, note="p for the tier, as in data/examples/ch11-roles.json"))
        return res


def load_bls(path):
    out = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[row["onet_soc_code"]] = row
    return out


# ═══════════════════════════════════════════════════════════════ boards
def resolve_board(url):
    """(ats, board name) for a Greenhouse or Ashby board link; None for any other source."""
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return None
    host = (p.hostname or "").lower()
    parts = [x for x in p.path.split("/") if x]
    if host in ("job-boards.greenhouse.io", "boards.greenhouse.io", "job-boards.eu.greenhouse.io") and parts:
        return ("greenhouse", parts[0].lower())
    if host == "boards-api.greenhouse.io" and len(parts) >= 3 and parts[:2] == ["v1", "boards"]:
        return ("greenhouse", parts[2].lower())
    if host == "jobs.ashbyhq.com" and parts:
        return ("ashby", unquote(parts[0]))
    return None


def fixture_name(ats, board):
    return f"{ats}-{re.sub(r'[^a-z0-9]+', '-', board.lower()).strip('-')}.json"


def load_fetcher():
    if not FETCHER.exists():
        raise StopRun(f"board fetcher not found: {rel(FETCHER)} (this prototype reuses the greenhouse-watch skill's fetcher)")
    spec = importlib.util.spec_from_file_location("greenhouse_watch", FETCHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for fn in ("board_url", "fetch_board", "normalize_jobs"):
        if not hasattr(mod, fn):
            raise StopRun(f"{rel(FETCHER)} no longer provides {fn}() — the reused fetcher changed")
    return mod


def read_board(gw, ats, board, boards_dir, raw_dir):
    """Returns (jobs as [(normalized, raw)], evidence string). Raises BoardError."""
    if boards_dir:
        f = Path(boards_dir) / fixture_name(ats, board)
        if not f.exists():
            raise BoardError(f"no saved response at {rel(f)}")
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise BoardError(f"saved response is not JSON ({rel(f)}): {e}")
        evidence = f"saved {ats} board response {rel(f)}"
    else:
        if os.environ.get("DAILY_CHECK_OFFLINE") == "1":
            raise RuntimeError("network fetch attempted while DAILY_CHECK_OFFLINE=1")
        try:
            url = gw.board_url(board, content=True, ats=ats)
            raw = gw.fetch_board(url)
        except gw.InputError as e:
            raise BoardError(str(e))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            raise BoardError(f"{type(e).__name__}: {e}")
        evidence = f"{url} fetched {dt.datetime.now().astimezone().isoformat(timespec='seconds')}"
        if raw_dir:
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / fixture_name(ats, board)).write_text(json.dumps(raw), encoding="utf-8")
    jobs = raw.get("jobs") if isinstance(raw, dict) else None
    if not isinstance(jobs, list):
        raise BoardError("response has no 'jobs' list")
    jobs = [j for j in jobs if isinstance(j, dict) and j.get("id") is not None]
    return list(zip(gw.normalize_jobs(jobs, ats), jobs)), evidence


def posting_facts(ats, norm, raw):
    texts, countries, remote = [(norm.get("location") or {}).get("name") or ""], [], False
    if ats == "greenhouse":
        texts += [o.get("name") or "" for o in (raw.get("offices") or []) if isinstance(o, dict)]
        texts += [o.get("location") or "" for o in (raw.get("offices") or []) if isinstance(o, dict)]
    else:
        remote = bool(raw.get("isRemote")) or (raw.get("workplaceType") or "").lower() == "remote"
        for a in [raw.get("address")] + [s.get("address") for s in (raw.get("secondaryLocations") or []) if isinstance(s, dict)]:
            c = (((a or {}).get("postalAddress") or {}).get("addressCountry"))
            if c:
                countries.append(c)
    published = (norm.get("first_published") or norm.get("updated_at") or "")[:10]
    listed = raw.get("isListed", True) is not False
    return texts, countries, remote, published, listed


# ═══════════════════════════════════════════════════════════════ scorer (the existing one)
def run_scorer(roles, day_dir, authorization):
    node = shutil.which("node")
    roles_path, prof_path = day_dir / "roles.json", day_dir / "scorer-profile.json"
    roles_path.write_text(json.dumps(roles, indent=2), encoding="utf-8")
    prof_path.write_text(json.dumps({"authorization": authorization}, indent=2), encoding="utf-8")
    cmd = [node, str(SCORER), str(roles_path), "--profile", str(prof_path), "--out-dir", str(day_dir)]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    info = {"called": True, "command": ["node", rel(SCORER), rel(roles_path), "--profile", rel(prof_path), "--out-dir", rel(day_dir)],
            "exit": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    if p.returncode != 0:
        return info, None
    scores_path = day_dir / "role-scores.json"
    data = json.loads(scores_path.read_text(encoding="utf-8"))
    info.update(roles_json=rel(roles_path), scores_json=rel(scores_path), scores_md=rel(day_dir / "role-scores.md"),
                config_seen=data.get("config"), scorer_id=data.get("_scorer"))
    return info, {r["role_id"]: r for r in data.get("roles", [])}


# ═══════════════════════════════════════════════════════════════ one run
NEXT = {
    "Apply": "Tailor an application today (your 2 research-and-apply hours).",
    "Consider": "Tailor only after the Apply roles; ask a contact about it first.",
    "Skip": "Skip — spend the time elsewhere.",
    "Held": "Needs you before any decision — see the reason.",
}


def run(args):
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    out_dir = Path(args.out_dir)
    day_dir = out_dir / today.isoformat()
    log = {"_recipe": RECIPE_ID, "recipe_version": RECIPE_VERSION, "_prototype": rel(__file__),
           "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "today": today.isoformat(),
           "mode": "offline (saved board responses)" if args.boards_dir else "live (board APIs)",
           "stop": None}

    # ── G0: intake gate ────────────────────────────────────────────────────
    try:
        cand = check_candidate(load_structured(args.candidate, "candidate file"), today)
        targets = load_structured(args.targets, "targets file")
        default_weeks = check_targets(targets)
        if not SCORER.exists():
            raise StopRun(f"scorer not found: {rel(SCORER)}")
        if not shutil.which("node"):
            raise StopRun("node is not on PATH — the existing scorer (scripts/score/role-scorer.mjs) needs it")
        if args.boards_dir and not Path(args.boards_dir).is_dir():
            raise StopRun(f"--boards-dir is not a folder: {args.boards_dir}")
        rw = runway(cand["visa"], today)
        if rw["unemployment_days_left"] <= 0:
            raise StopRun(f"unemployment allowance is used up ({rw['unemployment_days_used_today']} of "
                          f"{cand['visa']['unemployment_limit_days']} days as of {today}) — talk to your DSO; nothing to score")
        gw = load_fetcher()
        sponsors = SponsorIndex(SPONSOR_CSV)
    except StopRun as e:
        log["stop"] = {"gate": "G0 intake", "reason": str(e)}
        day_dir.mkdir(parents=True, exist_ok=True)
        write_outputs(day_dir, log)
        print(f"✗ stopped at the intake gate: {e}", file=sys.stderr)
        print(f"  {rel(day_dir / 'daily-check.md')}")
        return 2

    bls = load_bls(BLS_CSV)
    visa = cand["visa"]
    log["inputs"] = {
        "candidate": rel(args.candidate), "targets": rel(args.targets),
        "boards_dir": rel(args.boards_dir) if args.boards_dir else None,
        "sponsorship_csv": {"path": rel(SPONSOR_CSV), "sha256": sha256(SPONSOR_CSV),
                            "rows": sponsors.rows, "rows_with_h1b_fields": sponsors.rows_h1b},
        "bls_compact": {"path": rel(BLS_CSV), "sha256": sha256(BLS_CSV) if BLS_CSV.exists() else None},
        "fetcher": rel(FETCHER), "scorer": rel(SCORER),
    }
    log["config"] = {"tier_rule": TIER_RULE, "tier_p": TIER_P, "low_approval_rate_flag": LOW_APPROVAL_RATE,
                     "long_open_days_flag": LONG_OPEN_DAYS, "timeline_curve": TIMELINE_CURVE,
                     "default_hiring_weeks": val(default_weeks, INPUT),
                     "max_years_experience": val(cand["max_years"], INPUT),
                     "title_phrases": val([f["phrase"] for f in cand["families"]], INPUT),
                     "exclude_title_words": val(cand["exclude_title_words"], INPUT),
                     "flag_title_words": val(cand["flag_title_words"], INPUT)}
    log["runway"] = {
        "opt_end_date": val(visa["opt_end_date"].isoformat(), INPUT),
        "unemployment_days_used_today": val(rw["unemployment_days_used_today"], INPUT,
                                            note=f"{visa['unemployment_days_used']} as of {visa['unemployment_days_as_of']} "
                                                 "+ days since, assuming still unemployed"),
        "unemployment_limit_days": val(visa["unemployment_limit_days"], INPUT, note="confirm with your DSO"),
        "unemployment_runs_out": val(rw["unemployment_runs_out"].isoformat(), INPUT),
        "cliff": val(rw["cliff"].isoformat(), INPUT, binding=rw["binding"]),
        "buffer_days": val(visa["buffer_days"], INPUT),
        "needs_e_verify_employer": val(visa["needs_e_verify_employer"], INPUT, note="DSO question; the recipe never decides it"),
    }
    log["gates"] = {"G0 intake": "passed"}

    # ── state (what was open at the last run) ──────────────────────────────
    state_path = out_dir / "state.json"
    state = {"postings": {}}
    if state_path.exists() and not args.fresh_state:
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert isinstance(state.get("postings"), dict)
        except (json.JSONDecodeError, AssertionError):
            log["stop"] = {"gate": "state", "reason": f"state file is corrupt: {rel(state_path)} — move it aside to start fresh"}
            day_dir.mkdir(parents=True, exist_ok=True)
            write_outputs(day_dir, log)
            print(f"✗ {log['stop']['reason']}", file=sys.stderr)
            return 2
    first_run = not state["postings"]

    companies, postings, roles, not_checked = [], [], [], []
    listed_keys = {}  # company name → keys of every posting listed today (for the closed check)
    raw_dir = day_dir / "raw" if not args.boards_dir else None
    for comp in targets["companies"]:
        name = comp["name"].strip()
        c = {"name": name, "board_link": comp["board"]}
        weeks = comp.get("hiring_weeks", default_weeks)
        c["hiring_weeks"] = val(weeks, INPUT, **{"from": "company override" if "hiring_weeks" in comp else "default"})
        f, start, slack = timeline_factor(today, rw["cliff"], weeks, visa["buffer_days"])
        c["timeline"] = val(f, INPUT, expected_start=start.isoformat(), cliff=rw["cliff"].isoformat(),
                            slack_days=slack, buffer_days=visa["buffer_days"], curve=TIMELINE_CURVE)
        ev = comp.get("e_verify") or {}
        c["e_verify"] = val(ev.get("enrolled"), INPUT, source_note=ev.get("source"), checked_on=ev.get("checked_on"))
        c["sponsorship"] = sponsors.lookup(comp, cand["families"])
        so = comp.get("sponsorship_override")
        if so:
            c["sponsorship"]["override"] = {"tier": val(so["tier"], INPUT, source_note=so["source"]),
                                            "p": val(TIER_P[so["tier"]], INPUT, note="p for the tier you set")}
        resolved = resolve_board(comp["board"])
        if not resolved:
            c["status"] = "not checkable"
            c["reason"] = "board link is not Greenhouse or Ashby — only those two sources are supported so far"
            not_checked.append({"company": name, "reason": c["reason"], "board_link": comp["board"]})
            companies.append(c)
            continue
        ats, board = resolved
        c.update(ats=ats, board=board)
        try:
            jobs, evidence = read_board(gw, ats, board, args.boards_dir, raw_dir)
        except BoardError as e:
            c["status"] = "not checked today"
            c["reason"] = str(e)
            not_checked.append({"company": name, "reason": f"board could not be read: {e}", "board_link": comp["board"]})
            companies.append(c)
            continue
        c["status"] = "checked"
        c["listing_evidence"] = evidence
        counts = {"listed": len(jobs), "not a target title": 0, "excluded title word": 0,
                  "outside the US": 0, "experience above limit": 0, "matching": 0}
        excluded = []
        listed_keys[name] = set()
        for norm, raw in jobs:
            key = f"{ats}:{board}:{norm['id']}"
            listed_keys[name].add(key)
            title = norm.get("title") or ""
            fam, excl, flagw = match_title(title, cand)
            if not fam:
                counts["not a target title"] += 1
                continue
            if excl:
                counts["excluded title word"] += 1
                excluded.append({"title": title, "why": f"title word: {', '.join(excl)}"})
                continue
            texts, countries, remote, published, listed = posting_facts(ats, norm, raw)
            loc = classify_location(texts, remote, countries)
            if loc == "non-us":
                counts["outside the US"] += 1
                excluded.append({"title": title, "why": f"location: {' / '.join(x for x in texts + countries if x)[:80]}"})
                continue
            exp, mentions = parse_experience(norm.get("content") or "", cand["max_years"])
            if exp == "above":
                counts["experience above limit"] += 1
                excluded.append({"title": title, "why": f"experience: {mentions[0]['text'][:90]}"})
                continue
            counts["matching"] += 1
            age = None
            if published:
                try:
                    age = (today - dt.date.fromisoformat(published)).days
                except ValueError:
                    age = None
            flags = []
            if flagw:
                flags.append(f"title word to check: {', '.join(flagw)}")
            if exp in ("mixed", "not-stated"):
                flags.append("experience not stated" if exp == "not-stated" else "experience statements cross your limit")
            if loc in ("remote-unverified", "unverified"):
                flags.append("location not confirmed as US")
            if age is not None and age > LONG_OPEN_DAYS:
                flags.append(f"open {age} days — ask a contact whether it is still being filled")
            prev = state["postings"].get(key)
            soc = fam.get("soc")
            wage = bls.get(soc or "", {})
            postings.append({
                "key": key, "company": name, "title": title, "url": norm.get("absolute_url") or "",
                "new": prev is None, "first_seen": prev["first_seen"] if prev else today.isoformat(),
                "title_family": val(fam["phrase"], INPUT),
                "location": val(loc, RECORD, text=" / ".join(x for x in texts + countries if x)[:160]),
                "experience": val(exp, RECORD, mentions=mentions, limit_years=cand["max_years"]),
                "published": val(published or None, RECORD, age_days=age),
                "liveness": val(1.0 if listed else 0.0, RECORD, evidence=f"listed on the {ats} board — {evidence}"),
                "fit": val(fam["fit"], INPUT, note=f"your fit value for '{fam['phrase']}'"),
                "timeline": c["timeline"],
                "role_quality_reference": val({"soc": soc, "occupation": wage.get("title"),
                                               "annual_median_wage": _f(wage.get("annual_median_wage") or ""),
                                               "oews_year": wage.get("oews_year")} if wage else None, RECORD,
                                              note="national BLS median for the occupation code you mapped this title "
                                                   "to (the mapping is your input) — shown only; role quality weighs 0 in the scorer"),
                "flags": flags,
            })
        c["counts"] = counts
        c["excluded_examples"] = excluded[:15]
        companies.append(c)

    if not any(c.get("status") == "checked" for c in companies):
        log.update(companies=companies, postings=[], not_checked=not_checked,
                   stop={"gate": "boards", "reason": "no company board could be read — nothing was checked"})
        day_dir.mkdir(parents=True, exist_ok=True)
        write_outputs(day_dir, log)
        print("✗ no company board could be read — see the report", file=sys.stderr)
        return 4

    # ── decisions: scorer for everything with a sponsorship value, then the recipe's own gates ──
    by_name = {c["name"]: c for c in companies}
    for p in postings:
        c = by_name[p["company"]]
        sp = c["sponsorship"]
        if "override" in sp:
            vote = {"p": sp["override"]["p"]["value"], "tier": sp["override"]["tier"]["value"], "source": INPUT}
        elif sp["status"] == "record":
            vote = {"p": sp["p"]["value"], "tier": sp["tier"]["value"], "source": RECORD}
        else:
            vote = None
        p["sponsorship_vote"] = vote
        p["sponsorship_status"] = "override" if "override" in sp else sp["status"]
        if vote:
            roles.append({"role_id": p["key"], "company": p["company"], "title": p["title"],
                          "sponsorship": vote,
                          "fit": {"p": p["fit"]["value"], "source": INPUT},
                          "liveness": {"factor": p["liveness"]["value"], "source": RECORD},
                          "timeline": {"factor": p["timeline"]["value"], "source": INPUT}})
    day_dir.mkdir(parents=True, exist_ok=True)
    scores = {}
    if roles:
        info, scores = run_scorer(roles, day_dir, cand["authorization"])
        log["scorer"] = info
        if scores is None:
            log["stop"] = {"gate": "scorer", "reason": f"the scorer exited {info['exit']}: {info['stderr'][-300:]}"}
            log.update(companies=companies, postings=postings, not_checked=not_checked)
            write_outputs(day_dir, log)
            print(f"✗ scorer failed (exit {info['exit']})", file=sys.stderr)
            return 3
    else:
        log["scorer"] = {"called": False, "why": "no posting had a sponsorship value to score"}

    for p in postings:
        c = by_name[p["company"]]
        s = scores.get(p["key"])
        reasons = []
        if s:
            p["scorer"] = {"recommendation": s["recommendation"], "composite": s["composite"],
                           "reason": s["reason"], "arithmetic": s["trace"]["arithmetic"]}
        ev_needed = visa["needs_e_verify_employer"]
        enrolled = c["e_verify"]["value"]
        if ev_needed and enrolled is False:
            final, by = "Skip", "recipe gate: E-Verify"
            reasons.append("employer is not E-Verify enrolled, so it cannot support the STEM extension (confirm with your DSO)")
        else:
            if not p["sponsorship_vote"]:
                reasons.append(c["sponsorship"]["hold"])
            if ev_needed and enrolled is None:
                reasons.append("E-Verify enrollment not checked — look it up and record it in the targets file")
            if p["sponsorship_vote"] and not s:
                reasons.append("the scorer returned no result for this posting")
            if reasons:
                final, by = "Held", "recipe gate: needs you"
            else:
                final, by = s["recommendation"], "scorer"
                reasons.append(s["reason"])
        p["decision"] = {"final": final, "decided_by": by, "reasons": reasons, "next_action": NEXT[final]}

    # ── closed since the last run (only for boards read successfully today) ──
    closed = []
    for key, prev in state["postings"].items():
        if prev.get("status") != "open" or prev.get("company") not in listed_keys:
            continue
        if key not in listed_keys[prev["company"]]:
            closed.append({"key": key, "company": prev["company"], "title": prev.get("title"), "url": prev.get("url"),
                           "first_seen": prev.get("first_seen"), "closed_on": today.isoformat()})

    # ── companies worth networking into: sponsor on record, not ruled out, nothing to apply to ──
    matching_by_company = {}
    for p in postings:
        matching_by_company[p["company"]] = matching_by_company.get(p["company"], 0) + 1
    network = []
    for c in companies:
        sp = c["sponsorship"]
        tier = (sp.get("override") or {}).get("tier", {}).get("value") or (sp.get("tier") or {}).get("value")
        if c.get("status") == "checked" and tier in ("Proven", "Likely") and c["e_verify"]["value"] is not False \
                and matching_by_company.get(c["name"], 0) == 0:
            network.append({"company": c["name"], "tier": val(tier, INPUT if sp.get("override") else RECORD),
                            "why": f"{tier} sponsor on record, no matching posting today",
                            "next_action": "Network into this company (3 networking hours): ask for an informational chat before a role opens."})

    decided = [p["decision"]["final"] for p in postings]
    funnel = {"listed": sum(c.get("counts", {}).get("listed", 0) for c in companies),
              "matching": len(postings)}
    log.update(companies=companies, postings=postings, closed_since_last_run=closed, network_targets=network,
               not_checked=not_checked, first_run=first_run,
               summary={"companies": len(companies),
                        "companies_checked": sum(1 for c in companies if c.get("status") == "checked"),
                        "postings_listed": funnel["listed"], "postings_matching": funnel["matching"],
                        "new_today": sum(1 for p in postings if p["new"]),
                        **{k: decided.count(k) for k in ("Apply", "Consider", "Skip", "Held")},
                        "closed_since_last_run": len(closed), "network_targets": len(network),
                        "not_checked": len(not_checked)},
               cannot_verify=CANNOT_VERIFY)
    write_outputs(day_dir, log)

    if not args.dry_run:
        new_state = {"updated": today.isoformat(), "postings": dict(state["postings"])}
        for p in postings:
            prev = new_state["postings"].get(p["key"], {})
            new_state["postings"][p["key"]] = {"company": p["company"], "title": p["title"], "url": p["url"],
                                               "first_seen": prev.get("first_seen", today.isoformat()),
                                               "last_seen": today.isoformat(), "status": "open"}
        for cl in closed:
            new_state["postings"][cl["key"]].update(status="closed", closed_on=today.isoformat())
        out_dir.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(new_state, indent=2), encoding="utf-8")

    s = log["summary"]
    print(f"✓ {today} — {s['companies_checked']}/{s['companies']} boards read · {s['postings_listed']} postings listed · "
          f"{s['postings_matching']} match ({s['new_today']} new)")
    print(f"  Apply {s['Apply']} · Consider {s['Consider']} · Skip {s['Skip']} · Held for you {s['Held']} · "
          f"closed {s['closed_since_last_run']} · network {s['network_targets']} · not checked {s['not_checked']}")
    print(f"  {rel(day_dir / 'daily-check.md')}  +  {rel(day_dir / 'daily-check.json')}")
    return 0


CANNOT_VERIFY = [
    "Whether a listed posting is actually being filled: being on the board proves it is open on the board, not that anyone is hiring.",
    "Whether a sponsor on record will sponsor this role now: the H-1B counts are past filings, their years are not documented, and only up to 5 titles per company are listed.",
    "Anything about a company with no H-1B record in the data: 'unknown' is not 'does not sponsor'.",
    "E-Verify enrollment: the repo has no E-Verify data; the value is whatever you recorded in the targets file.",
    "How long a company really takes to hire: every hiring time is your estimate.",
    "Immigration rules: unemployment limit, STEM extension and E-Verify requirements are your inputs to confirm with your DSO.",
    "Experience, title and location filters read text with fixed rules; a posting worded unusually can be kept or dropped wrongly — excluded examples are listed so you can check.",
    "Funding: the SEC Form D samples that ship with the repo match none of these companies, so funding is not used.",
]


# ═══════════════════════════════════════════════════════════════ outputs
STATUS_WORDS = {"no-row": "no row in the data", "no-h1b-fields": "no H-1B history", "ambiguous": "ambiguous name",
                "duplicate-record": "untrusted (duplicate record)"}


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def cell(x):
    return str(x if x is not None else "—").replace("|", "\\|").replace("\n", " ")


def link(title, url):
    return f"[{cell(title)}]({url})" if url else cell(title)


def render_md(log):
    o = []
    s = log.get("summary") or {}
    o.append(f"# Daily job check — {log['today']}\n")
    o.append("## Executive summary\n")
    if log.get("stop"):
        o.append(f"This is the daily check of your target companies' job boards, but **it stopped early**: "
                 f"{log['stop']['reason']}. No posting was scored, and nothing was guessed to keep going. "
                 f"Fix what is named here and run it again.\n")
        for n in log.get("not_checked") or []:
            o.append(f"- {cell(n['company'])}: {cell(n['reason'])}")
        o.append("\n## Run record\n")
        o.append(f"- Recipe: `{log['_recipe']}` v{log['recipe_version']} · prototype `{log['_prototype']}`")
        o.append(f"- Stopped at: {log['stop']['gate']}")
        return "\n".join(o) + "\n"
    first = " This is the first run, so every matching posting counts as new." if log.get("first_run") else ""
    o.append(f"This report is today's check of your target companies' job boards for entry-level data roles you could "
             f"start before your work authorization runs out. Read it to decide where your application hours go today."
             f"{first} It read {s['companies_checked']} of {s['companies']} company boards, found {s['postings_listed']} "
             f"open postings and kept {s['postings_matching']} that match your titles, level, location and experience "
             f"({s['new_today']} new). **Apply: {s['Apply']} · Consider: {s['Consider']} · Skip: {s['Skip']} · "
             f"Needs you first: {s['Held']}.** "
             f"{plural(s['network_targets'], 'sponsor company has', 'sponsor companies have')} nothing open for you — "
             f"network into those instead. {plural(s['closed_since_last_run'], 'posting', 'postings')} closed since the "
             f"last check. The recommendation is a starting point; you decide.\n")
    rw = log["runway"]
    o.append(f"**Your clock:** the latest workable start date is **{rw['cliff']['value']}**, set by your "
             f"{rw['cliff']['binding']} (OPT ends {rw['opt_end_date']['value']}; unemployment allowance runs out "
             f"{rw['unemployment_runs_out']['value']}). You want {rw['buffer_days']['value']} days of slack before it. "
             f"*(your-input — confirm the rules with your DSO)*\n")
    o.append("Labels used below: *(record)* came from data or a job board · *(your-input)* came from your files · "
             "*(model-judgment)* would be an AI's judgment — this run makes none.\n")

    posts = log.get("postings") or []
    def sec(final, heading, blurb):
        rows = [p for p in posts if p["decision"]["final"] == final]
        o.append(f"## {heading} ({len(rows)})\n")
        o.append(blurb + "\n")
        if not rows:
            o.append("_None today._\n")
            return
        o.append("| New | Company | Role | Where | Experience | Sponsorship | Timeline | Why | Flags |")
        o.append("|---|---|---|---|---|---|---|---|---|")
        for p in sorted(rows, key=lambda p: -(p.get("scorer") or {}).get("composite", 0)):
            v = p.get("sponsorship_vote")
            spon = f"{v['tier']} *({v['source']})*" if v else f"{STATUS_WORDS.get(p['sponsorship_status'], p['sponsorship_status'])} *(record)*"
            reason = "; ".join(p["decision"]["reasons"])
            if final == "Held" and p.get("scorer"):
                reason += (f" — once cleared the scorer would say **{p['scorer']['recommendation']}** "
                           f"({p['scorer']['composite']:.3f})")
            o.append(f"| {'★' if p['new'] else ''} | {cell(p['company'])} | {link(p['title'], p['url'])} | "
                     f"{cell(p['location']['value'])} *(record)* | {cell(p['experience']['value'])} *(record)* | {spon} | "
                     f"{p['timeline']['value']} → start {p['timeline']['expected_start']} *(your-input)* | {cell(reason)} | "
                     f"{cell('; '.join(p['flags']) or '—')} |")
        o.append("")

    sec("Apply", "Apply today — tailor these", "Scored Apply by the existing scorer: a sponsor on record, a live posting, and a start date that fits.")
    sec("Consider", "Consider", "Above the floor but with a soft spot (a weaker sponsorship tier or a tight timeline).")
    sec("Held", "Needs you before a decision", "The recipe stops here instead of guessing. Each row says what is missing.")
    sec("Skip", "Skipped", "A closed gate (timeline, E-Verify, dead posting) or too weak a score. Skipping is a good outcome.")

    net = log.get("network_targets") or []
    o.append(f"## Network, don't apply ({len(net)})\n")
    o.append("Sponsors on record with no matching posting today — worth an informational chat before a role opens.\n")
    if net:
        o.append("| Company | Sponsorship | Next action |")
        o.append("|---|---|---|")
        for n in net:
            o.append(f"| {cell(n['company'])} | {n['tier']['value']} *({n['tier']['source']})* | {cell(n['next_action'])} |")
    else:
        o.append("_None today._")
    o.append("")

    closed = log.get("closed_since_last_run") or []
    o.append(f"## Closed since the last check ({len(closed)})\n")
    if closed:
        o.append("| Company | Role | First seen |")
        o.append("|---|---|---|")
        for c in closed:
            o.append(f"| {cell(c['company'])} | {link(c['title'], c['url'])} | {c['first_seen']} |")
    else:
        o.append("_None._")
    o.append("")

    nc = log.get("not_checked") or []
    o.append(f"## Companies not checked today ({len(nc)})\n")
    if nc:
        o.append("| Company | Why | Next action |")
        o.append("|---|---|---|")
        for n in nc:
            o.append(f"| {cell(n['company'])} | {cell(n['reason'])} | Check the careers page by hand today. |")
    else:
        o.append("_All boards were read._")
    o.append("")

    o.append("## Your target list today\n")
    o.append("| Company | Board | Sponsorship record | E-Verify | Hiring time | Listed | Matching | Filtered out (title / word / location / experience) |")
    o.append("|---|---|---|---|---|---|---|---|")
    for c in log.get("companies") or []:
        sp = c["sponsorship"]
        if sp.get("status") == "record":
            rec = (f"{sp['tier']['value']} — {int(sp['approvals']['value'])} approvals, {sp['approval_rate']['value']}% "
                   f"({sp['csv_row']['value']}) *(record)*")
        else:
            rec = f"{sp.get('status')}: {sp.get('hold', '')}"   # the hold text already carries any similar-name hint
        if sp.get("override"):
            rec += f" · you set **{sp['override']['tier']['value']}** ({sp['override']['tier'].get('source_note')}) *(your-input)*"
        if sp.get("flags"):
            rec += " · ⚠ " + "; ".join(sp["flags"])
        ev = c["e_verify"]["value"]
        evs = {True: "enrolled", False: "not enrolled", None: "not checked"}[ev] + " *(your-input)*"
        k = c.get("counts") or {}
        filt = (f"{k.get('not a target title', '—')} / {k.get('excluded title word', '—')} / "
                f"{k.get('outside the US', '—')} / {k.get('experience above limit', '—')}") if k else c.get("status", "")
        o.append(f"| {cell(c['name'])} | {cell(c.get('ats') or 'unsupported')} | {cell(rec)} | {evs} | "
                 f"{c['hiring_weeks']['value']} wk ({c['hiring_weeks']['from']}) *(your-input)* | "
                 f"{k.get('listed', '—')} | {k.get('matching', '—')} | {cell(filt)} |")
    o.append("")
    ex = [(c["name"], e) for c in log.get("companies") or [] for e in c.get("excluded_examples") or []]
    if ex:
        o.append("### Postings with a target title that were filtered out — check the filters are right\n")
        o.append("| Company | Role | Why it was dropped |")
        o.append("|---|---|---|")
        for name, e in ex:
            o.append(f"| {cell(name)} | {cell(e['title'])} | {cell(e['why'])} |")
        o.append("")

    o.append("## What this report cannot tell you\n")
    for x in log.get("cannot_verify") or []:
        o.append(f"- {x}")
    o.append("")

    o.append("## Run record\n")
    i = log.get("inputs") or {}
    o.append(f"- Recipe `{log['_recipe']}` v{log['recipe_version']} · prototype `{log['_prototype']}` · mode: {log['mode']}")
    o.append(f"- Sponsorship data `{i['sponsorship_csv']['path']}` — {i['sponsorship_csv']['rows']} rows, "
             f"{i['sponsorship_csv']['rows_with_h1b_fields']} with H-1B fields, sha256 `{i['sponsorship_csv']['sha256'][:16]}…`")
    o.append(f"- Board fetcher reused from `{i['fetcher']}`; decisions by the existing scorer `{i['scorer']}`")
    sc = log.get("scorer") or {}
    if sc.get("called"):
        o.append(f"- Scorer run: `{' '.join(sc['command'])}` → exit {sc['exit']}: {cell(sc['stdout'].splitlines()[0] if sc['stdout'] else '')}")
        o.append(f"- Scorer outputs: `{sc.get('scores_json')}` + `{sc.get('scores_md')}` (per-term arithmetic for every scored role)")
        o.append("- The scorer's counts above are *before* the recipe's own gates: a posting the scorer rates Apply is "
                 "still Skipped here if the employer is not E-Verify enrolled, or Held if enrollment is unchecked.")
    else:
        o.append(f"- Scorer not called: {sc.get('why')}")
    cfg = log.get("config") or {}
    o.append(f"- Sponsorship tier rule (proposal): Proven = ≥{TIER_RULE['proven_min_approvals']} approvals and ≥"
             f"{TIER_RULE['proven_min_approval_rate']:.0f}% approval rate; Likely = ≥{TIER_RULE['likely_min_approvals']} approval; "
             f"p Proven {TIER_P['Proven']}, Likely {TIER_P['Likely']}")
    o.append(f"- Timeline curve (proposal): {TIMELINE_CURVE}")
    o.append(f"- Filters *(your-input)*: titles {', '.join(cfg['title_phrases']['value'])}; excluded words "
             f"{', '.join(cfg['exclude_title_words']['value'])}; max {cfg['max_years_experience']['value']} years")
    o.append(f"- Skip rate: the scorer's own skip-rate line covers only the scored roles; "
             f"{s['postings_listed'] - s['postings_matching']} of {s['postings_listed']} listed postings were dropped earlier by the filters.")
    return "\n".join(o) + "\n"


def write_outputs(day_dir, log):
    (day_dir / "daily-check.json").write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")
    (day_dir / "daily-check.md").write_text(render_md(log), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", help="candidate constraints JSON (visa dates, limits, title phrases, fit values)")
    ap.add_argument("--targets", help="target companies JSON (name, board link, E-Verify, optional hiring weeks)")
    ap.add_argument("--out-dir", help="folder for daily reports and the state file")
    ap.add_argument("--boards-dir", help="read saved board responses from this folder instead of fetching (offline)")
    ap.add_argument("--today", help="run as if today were YYYY-MM-DD (default: today)")
    ap.add_argument("--fresh-state", action="store_true", help="ignore the previous run: everything open counts as new")
    ap.add_argument("--dry-run", action="store_true", help="write the reports but do not update the state file")
    ap.add_argument("--sample", action="store_true",
                    help="offline sample run: fictional persona from search/examples/, synthetic postings, real sponsorship CSV")
    args = ap.parse_args(argv)
    if args.sample:
        args.candidate = args.candidate or str(PERSONA / "daily-check.candidate.json")
        args.targets = args.targets or str(FIXTURES / "targets.sample.json")
        args.boards_dir = args.boards_dir or str(FIXTURES / "boards")
        args.today = args.today or SAMPLE_TODAY
        args.out_dir = args.out_dir or str(COMPONENT / "out" / "sample")
        args.fresh_state = True
    missing = [f"--{k.replace('_', '-')}" for k in ("candidate", "targets", "out_dir") if not getattr(args, k)]
    if missing:
        ap.error(f"missing {', '.join(missing)} (or use --sample)")
    if args.today:
        try:
            dt.date.fromisoformat(args.today)
        except ValueError:
            ap.error(f"--today must be YYYY-MM-DD, got {args.today!r}")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
