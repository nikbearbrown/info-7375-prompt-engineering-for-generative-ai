"""The JS3 filter: gates G1–G5, the score, and the verdict, as FILTER.md states them.

CLI: python -m agent.filter --run evidence/runs/live-text-1 --out out/filter-v0.1
     [--persona PATH] [--rules v0.1 | v0.2 | v0.1+C1 … v0.1+C6]

--rules picks the rule mode (FILTER.md v0.2 "Rule modes"). v0.1 is the default and runs the
v0.1 code path unchanged. v0.2 is v0.1 with C1–C6; v0.1+Cn is v0.1 with that one change only.

Writes results.jsonl (one result per posting) and summary.json. Persona fields are read
from the JS1 persona file at runtime; a missing field stops the run with exit 2 and no output.

Readings of FILTER.md v0.1 confirmed by Tushar on 2026-11-21 (before this code was written):
- G3: a location naming only a region that contains the US but doesn't name it
  ("North America", "AMER", "Americas", "Global", "Worldwide", "Anywhere") is unknown.
- A G3 fail rejects even when the posting has no usable text. With no usable text, G4 and
  G5 are unknown, so such a posting is cannot_tell unless G1, G2 or G3 fails.
Implementation choices that FILTER.md leaves open are marked "Choice:" below.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from . import PROJECT_DIR
from .postings import RunError, load_run
from .text import word_pattern

FILTER_VERSION = "0.1"
CONTRACT = "FILTER.md v0.1 (commit 821ddee)"
CONTRACT_V02 = "FILTER.md v0.2 (frozen 2026-11-24)"

# ---------- rule modes (FILTER.md v0.2) ----------
CHANGES = ("C1", "C2", "C3", "C4", "C5", "C6")
G4_CHANGES = frozenset({"C1", "C2", "C3", "C4", "C6"})
V01 = frozenset()
RULE_MODES = {"v0.1": V01, "v0.2": frozenset(CHANGES), **{f"v0.1+{c}": frozenset({c}) for c in CHANGES}}
DEFAULT_PERSONA = PROJECT_DIR.parent / "js1-contract-and-watch" / "persona" / "cole-palmer.example.json"

PASS, FAIL, UNKNOWN = "pass", "fail", "unknown"
KEEP, REJECT, CANNOT_TELL = "keep", "reject", "cannot_tell"
GATES = ("G1", "G2", "G3", "G4", "G5")

MIN_TEXT_CHARS = 200
KEEP_THRESHOLD = 2
TERM_CAP = 3
NEAR_THRESHOLD = (1, 3)

G1_ROLES = ("Software Engineer", "Software Developer", "Backend Engineer", "Back-End Engineer",
            "Full Stack Engineer", "Full-Stack Engineer", "AI Engineer", "Machine Learning Engineer",
            "ML Engineer")
G2_EXCLUDED = ("Senior", "Sr", "Staff", "Principal", "Lead", "Manager", "Director", "Head", "VP", "Intern")
TOPIC_WORDS = ("backend", "API", "distributed systems", "infrastructure", "platform", "full-stack",
               "LLM", "machine learning")
TOPIC_WORDS_V02 = tuple(w for w in TOPIC_WORDS if w != "platform")  # C5: "platform" is a false friend

# Choice: FILTER.md gives "unable to sponsor", "will not sponsor", "without sponsorship" as
# examples. The closed list is JS1's R5 list plus three plain synonyms. No posting in
# live-text-1 contains a visa-refusal phrase (checked 2026-11-21), so G5 never fails there.
G5_PHRASES = ("unable to sponsor", "will not sponsor", "does not sponsor", "do not sponsor",
              "cannot sponsor", "not able to sponsor", "no sponsorship", "without sponsorship",
              "without the need for sponsorship")

# ---------- G3 lists. Choice: JS1 CONTRACT.md R3's US lists, unchanged. ----------
US_MARKERS = ("United States", "USA", "U.S.")
US_MARKER_UPPERCASE_ONLY = "US"
US_CITIES = ("San Francisco", "South San Francisco", "New York", "New York City", "New-York",
             "Seattle", "Chicago", "Atlanta")
US_CITY_SHORT_FORMS = ("SF", "NYC", "NY", "SEA", "CHI", "ATL", "DC")
US_STATE_NAMES = (
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming",
)
# "CA" is excluded: on Stripe's board "Toronto, CA" means Canada.
US_STATE_ABBREVIATIONS = (
    "AL", "AK", "AZ", "AR", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
    "UT", "VT", "VA", "WA", "WV", "WI", "WY",
)
_STATE_ABBREVIATION_AFTER_SEPARATOR = re.compile(
    r"[,;]\s*(" + "|".join(US_STATE_ABBREVIATIONS) + r")(?![A-Za-z0-9])")
# Confirmed reading: regions that contain the US without naming it make G3 unknown.
US_CONTAINING_REGIONS = ("North America", "AMER", "Americas", "Global", "Worldwide", "Anywhere")
# A location is "no country" if nothing is left after removing these words and punctuation.
_REMOTE_WORDS = re.compile(r"(?i)(?<![A-Za-z0-9])(remote|hybrid|on-site|onsite|in-office|flexible)(?![A-Za-z0-9])")
_PLACEHOLDERS = ("na", "location", "tbd", "")  # compared with all punctuation removed ("N/A" -> "na")

# ---------- G4: the four stated-minimum forms in FILTER.md ----------
# One alternation scanned left to right, so "3–5 years of" is read once as a range (minimum 3)
# and not again as "5 years of". Digits glued to a preceding digit, "." or "," don't start a match.
_N = r"(?<![\d.,])(\d+)"
_G4_PATTERN = re.compile(
    r"at\s+least\s+" + _N + r"\s*\+?\s*years(?![A-Za-z0-9])"      # at least N years
    r"|" + _N + r"\s*\+?\s*[-–—]\s*\d+\s*\+?\s*years(?![A-Za-z0-9])"  # N–M years
    r"|" + _N + r"\s*\+\s*years(?![A-Za-z0-9])"                     # N+ years
    r"|" + _N + r"\s+years\s+of(?![A-Za-z0-9])",                    # N years of
    re.IGNORECASE,
)


class PersonaError(Exception):
    """A persona field the filter reads is missing or outside what FILTER.md v0.1 defines."""


# ---------- persona ----------

def _lookup(data, dotted: str):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise PersonaError(f"persona field {dotted!r} is missing")
        node = node[part]
    return node


def _string_list(value, name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
        raise PersonaError(f"persona field {name!r} must be a non-empty list of non-empty strings")
    return list(value)


def load_persona(path) -> dict:
    """The five persona fields FILTER.md reads, validated. Nothing else is returned."""
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as err:
        raise PersonaError(f"cannot read persona {path}: {err}") from None
    skills = _string_list(_lookup(data, "skills"), "skills")
    titles = _string_list(_lookup(data, "job_search.target_titles"), "job_search.target_titles")
    years = _lookup(data, "job_search.years_experience")
    sponsorship = _lookup(data, "job_search.needs_sponsorship")
    country = _lookup(data, "job_search.work_country")
    if not isinstance(years, int) or isinstance(years, bool):
        raise PersonaError("persona field 'job_search.years_experience' must be an integer")
    if not isinstance(sponsorship, bool):
        raise PersonaError("persona field 'job_search.needs_sponsorship' must be true or false")
    if not isinstance(country, str):
        raise PersonaError("persona field 'job_search.work_country' must be a string")
    # Choice: FILTER.md v0.1 is written for these values; outside them the rule is undefined.
    if country != "US":
        raise PersonaError(f"rule undefined for work_country {country!r}: G3 is written for US")
    if not 0 <= years <= 3:
        raise PersonaError(f"rule undefined for years_experience {years}: G2/G4 are written for 0–3 years")
    roles = {r.lower() for r in G1_ROLES}
    missing = [t for t in titles if t.lower() not in roles]
    if missing:
        raise PersonaError(f"rule undefined: target title(s) {missing} are not in the G1 role list")
    return {"skills": skills, "target_titles": titles, "years_experience": years,
            "needs_sponsorship": sponsorship, "work_country": country}


# ---------- gates ----------

def _gate(result: str, matched, detail: str) -> dict:
    return {"result": result, "matched": matched, "detail": detail}


def _found(text: str, phrases, ignore_case: bool = True) -> list[str]:
    return [p for p in phrases if word_pattern(p, ignore_case).search(text)]


def check_g1(title) -> dict:
    if title is None:
        return _gate(UNKNOWN, [], "title missing")  # Choice: no title to read is unknown, not fail
    roles = _found(title, G1_ROLES)
    if roles:
        return _gate(PASS, roles, f"title {title!r} names a target role")
    return _gate(FAIL, [], f"title {title!r} names no target role")


def check_g2(title) -> dict:
    if title is None:
        return _gate(UNKNOWN, [], "title missing")
    excluded = _found(title, G2_EXCLUDED)
    if excluded:
        return _gate(FAIL, excluded, f"title {title!r} has seniority/intern word(s)")
    return _gate(PASS, [], f"title {title!r} has no seniority/intern word")


def us_matches(location: str) -> list[str]:
    matches = _found(location, US_MARKERS)
    matches += _found(location, (US_MARKER_UPPERCASE_ONLY,), ignore_case=False)
    matches += _found(location, US_CITIES + US_CITY_SHORT_FORMS + US_STATE_NAMES)
    matches += [f", {a}" for a in _STATE_ABBREVIATION_AFTER_SEPARATOR.findall(location)]
    return matches


def classify_location(location: str) -> tuple[str, list[str]]:
    """("us" | "region" | "no-country" | "non-us", matched words) for one location value."""
    us = us_matches(location)
    if us:
        return "us", us
    regions = _found(location, US_CONTAINING_REGIONS)
    if regions:
        return "region", regions
    rest = re.sub(r"[\W_]+", "", _REMOTE_WORDS.sub(" ", location)).lower()
    if rest in _PLACEHOLDERS:
        return "no-country", []
    return "non-us", []


def check_g3(locations) -> dict:
    if not locations:
        return _gate(UNKNOWN, [], "location field missing")
    kinds = [(loc, *classify_location(loc)) for loc in locations]
    us = [f"{loc!r}: {', '.join(m)}" for loc, kind, m in kinds if kind == "us"]
    if us:
        return _gate(PASS, us, "a listed location is in the US")
    vague = [loc for loc, kind, _ in kinds if kind in ("region", "no-country")]
    if vague:
        # Choice: a region or bare "Remote" next to non-US locations still can't rule the US out.
        return _gate(UNKNOWN, vague, "no US location; a region or bare remote/placeholder doesn't say the country")
    return _gate(FAIL, [], f"every listed location is outside the US: {locations!r}")


def g4_minimums(text: str) -> list[tuple[str, int]]:
    out = []
    for m in _G4_PATTERN.finditer(text):
        n = next(g for g in m.groups() if g is not None)
        out.append((m.group(0), int(n)))
    return out


def check_g4(text) -> dict:
    found = g4_minimums(text)
    if not found:
        return _gate(UNKNOWN, [], "no stated minimum years")
    largest = max(n for _, n in found)
    spans = [span for span, _ in found]
    if largest > 3:
        return _gate(FAIL, spans, f"largest stated minimum is {largest} years (> 3)")
    return _gate(PASS, spans, f"largest stated minimum is {largest} years (<= 3)")


# ---------- G4 under FILTER.md v0.2 (C1–C4, C6). v0.1 mode never reaches this code. ----------

# C6: a number may be written "word (N)", e.g. "two (2)"; the digit is the value.
_N_C6 = r"(?:(?<![\d.,])(\d+)|(?<![A-Za-z0-9])(?:[A-Za-z]+\s*)?\(\s*(\d+)\s*\))"
_M_C6 = r"(?:\d+|(?:[A-Za-z]+\s*)?\(\s*\d+\s*\))"
_G4_PATTERN_C6 = re.compile(
    r"at\s+least\s+" + _N_C6 + r"\s*\+?\s*years(?![A-Za-z0-9])"
    r"|" + _N_C6 + r"\s*\+?\s*[-–—]\s*" + _M_C6 + r"\s*\+?\s*years(?![A-Za-z0-9])"
    r"|" + _N_C6 + r"\s*\+\s*years(?![A-Za-z0-9])"
    r"|" + _N_C6 + r"\s+years\s+of(?![A-Za-z0-9])",
    re.IGNORECASE,
)
# C2: maximums. In a maximum, N may also be a spelled number one–ten.
SPELLED = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
           "nine": 9, "ten": 10}
_MAX_KIND = r"(?<![A-Za-z0-9])(less\s+than|up\s+to|no\s+more\s+than)\s+"
_SPELLED = r"(" + "|".join(SPELLED) + r")(?![A-Za-z0-9])"


def _max_pattern(c6: bool) -> re.Pattern:
    digit = r"(?<![\d.,])(\d+)"
    paren = r"(?:[A-Za-z]+\s*)?\(\s*(\d+)\s*\)" if c6 else r"(?!)(\d)"  # (?!) never matches
    return re.compile(_MAX_KIND + r"(?:" + paren + r"|" + digit + r"|" + _SPELLED + r")"
                      r"\s*\+?\s*years?(?![A-Za-z0-9])", re.IGNORECASE)


_MAX_PATTERNS = {False: _max_pattern(False), True: _max_pattern(True)}
PREFERRED_WORDS = ("preferred", "nice to have", "bonus", "a plus")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def sentences(blocks) -> list[str]:
    """FILTER.md v0.2 "Sentence": each block split after ".", "!" or "?" followed by a space."""
    return [s for b in blocks for s in _SENTENCE_END.split(b) if s]


def g4_maximums(text: str, rules) -> list[tuple[str, int, str, tuple[int, int]]]:
    """(span, N, kind, (start, end)) for each stated maximum (C2)."""
    out = []
    for m in _MAX_PATTERNS["C6" in rules].finditer(text):
        kind = re.sub(r"\s+", " ", m.group(1).lower())
        paren, digit, word = m.group(2), m.group(3), m.group(4)
        n = int(paren) if paren else int(digit) if digit else SPELLED[word.lower()]
        out.append((m.group(0), n, kind, m.span()))
    return out


def _zero_satisfies(kind: str, n: int) -> bool:
    return n >= 1 if kind == "less than" else True


def check_g4_rules(text: str, rules, blocks=None) -> dict:
    """G4 with any of C1–C4, C6 on top of v0.1 (FILTER.md v0.2 "G4 in v0.2")."""
    cutoff = 2 if "C3" in rules else 3
    pattern = _G4_PATTERN_C6 if "C6" in rules else _G4_PATTERN
    units = sentences(blocks or [text]) if "C4" in rules else [text]
    mandatory, ignored, maximums = [], [], []
    for unit in units:
        unit_max = g4_maximums(unit, rules) if "C2" in rules else []
        maximums += unit_max
        preferred = "C4" in rules and bool(_found(unit, PREFERRED_WORDS))
        for m in pattern.finditer(unit):
            if any(m.start() < end and start < m.end() for *_, (start, end) in unit_max):
                continue  # C2: a number inside a maximum phrase is not also a minimum
            n = int(next(g for g in m.groups() if g is not None))
            (ignored if preferred else mandatory).append((m.group(0), n))
    matched = [span for span, _ in mandatory]
    matched += [f"max: {span}" for span, *_ in maximums]
    matched += [f"ignored (preferred): {span}" for span, _ in ignored]
    if mandatory:
        values = [n for _, n in mandatory]
        if "C4" in rules:
            if all(n <= cutoff for n in values):
                return _gate(PASS, matched, f"every mandatory minimum is <= {cutoff} years")
            if all(n > cutoff for n in values):
                return _gate(FAIL, matched, f"every mandatory minimum is > {cutoff} years")
            return _gate(UNKNOWN, matched, f"mandatory minimums on both sides of {cutoff} years")
        largest = max(values)
        if largest > cutoff:
            return _gate(FAIL, matched, f"largest stated minimum is {largest} years (> {cutoff})")
        return _gate(PASS, matched, f"largest stated minimum is {largest} years (<= {cutoff})")
    if maximums:
        if all(_zero_satisfies(kind, n) for _, n, kind, _ in maximums):
            return _gate(PASS, matched, "no mandatory minimum; 0 years satisfies every stated maximum")
        return _gate(FAIL, matched, "no mandatory minimum; 0 years does not satisfy a stated maximum")
    if "C1" in rules:
        return _gate(PASS, matched, "no stated experience requirement (C1: passes G4 only)")
    return _gate(UNKNOWN, matched, "no stated minimum years" if not ignored else "only preferred minimums stated")


def check_g5(text, needs_sponsorship: bool) -> dict:
    if not needs_sponsorship:
        return _gate(PASS, [], "not applicable: needs_sponsorship is false")
    phrases = _found(text, G5_PHRASES)
    if phrases:
        return _gate(FAIL, phrases, "the posting states it will not sponsor")
    return _gate(PASS, [], "no stated refusal to sponsor")


# ---------- score and verdict ----------

def score(text: str, skills, rules=V01) -> dict:
    topic = _found(text, TOPIC_WORDS_V02 if "C5" in rules else TOPIC_WORDS)
    skill_hits = _found(text, skills)
    t_points, s_points = min(len(topic), TERM_CAP), min(len(skill_hits), TERM_CAP)
    return {"topic": {"matched": topic, "points": t_points},
            "skills": {"matched": skill_hits, "points": s_points},
            "total": t_points + s_points}


def text_status(text) -> str:
    if text is None:
        return "missing"
    return "short" if len(text) < MIN_TEXT_CHARS else "ok"


def evaluate(posting: dict, persona: dict, rules=V01) -> dict:
    text = posting.get("text")
    status = text_status(text)
    gates = {"G1": check_g1(posting.get("title")),
             "G2": check_g2(posting.get("title")),
             "G3": check_g3(posting.get("locations"))}
    if status == "ok":
        gates["G4"] = (check_g4_rules(text, rules, posting.get("blocks")) if rules & G4_CHANGES
                       else check_g4(text))
        gates["G5"] = check_g5(text, persona["needs_sponsorship"])
    else:
        reason = "no posting text" if status == "missing" else f"text is {len(text)} chars (< {MIN_TEXT_CHARS})"
        gates["G4"] = _gate(UNKNOWN, [], f"cannot tell: {reason}")
        gates["G5"] = _gate(UNKNOWN, [], f"cannot tell: {reason}")

    first_fail = next((g for g in GATES if gates[g]["result"] == FAIL), None)
    first_unknown = next((g for g in GATES if gates[g]["result"] == UNKNOWN), None)
    result_score = None
    if first_fail:
        verdict = REJECT
    elif first_unknown:
        verdict = CANNOT_TELL
    else:
        result_score = score(text, persona["skills"], rules)
        verdict = KEEP if result_score["total"] >= KEEP_THRESHOLD else REJECT
    near = result_score is not None and NEAR_THRESHOLD[0] <= result_score["total"] <= NEAR_THRESHOLD[1]
    return {"board": posting["board"], "id": posting["id"], "title": posting.get("title"),
            "verdict": verdict, "text_status": status,
            "text_chars": None if text is None else len(text),
            "gates": gates, "first_failing_gate": first_fail, "first_unknown_gate": first_unknown,
            "score": result_score, "near_threshold": near}


def summarize(results: list[dict], failures: list[dict], run_dir, persona_path, mode: str = "v0.1") -> dict:
    by_board = {}
    for r in results:
        counts = by_board.setdefault(r["board"], {KEEP: 0, REJECT: 0, CANNOT_TELL: 0, "total": 0})
        counts[r["verdict"]] += 1
        counts["total"] += 1
    rejects = [r for r in results if r["verdict"] == REJECT]
    first_failing = Counter(r["first_failing_gate"] or "score below 2" for r in rejects)
    first_unknown = Counter(r["first_unknown_gate"] for r in results if r["verdict"] == CANNOT_TELL)
    header = ({"filter_version": FILTER_VERSION, "contract": CONTRACT} if mode == "v0.1" else
              {"filter_version": mode, "contract": CONTRACT_V02,
               "rules": {"mode": mode, "changes": sorted(RULE_MODES[mode])}})
    return {
        **header,
        "run": str(run_dir), "persona": str(persona_path),
        "postings": len(results),
        "by_verdict": {v: sum(r["verdict"] == v for r in results) for v in (KEEP, REJECT, CANNOT_TELL)},
        "by_board": by_board,
        "by_first_failing_gate": {k: first_failing.get(k, 0) for k in (*GATES, "score below 2")},
        "cannot_tell_by_first_unknown_gate": {g: first_unknown.get(g, 0) for g in GATES},
        "near_threshold": sum(r["near_threshold"] for r in results),
        "text_status": dict(Counter(r["text_status"] for r in results)),
        "board_failures": failures,
    }


def run_filter(run_dir, out_dir, persona_path=DEFAULT_PERSONA, mode: str = "v0.1") -> dict:
    if mode not in RULE_MODES:
        raise ValueError(f"unknown rule mode {mode!r}; choose from {sorted(RULE_MODES)}")
    rules = RULE_MODES[mode]
    persona = load_persona(persona_path)  # before reading the run or writing anything
    postings, failures = load_run(run_dir, with_blocks=True)
    results = [evaluate(p, persona, rules) for p in postings]
    summary = summarize(results, failures, run_dir, persona_path, mode)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "results.jsonl", "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m agent.filter", description="JS3 filter (FILTER.md v0.1 / v0.2).")
    parser.add_argument("--run", type=Path, required=True, help="agent run folder (summary.json + raw/)")
    parser.add_argument("--out", type=Path, required=True, help="output folder for results.jsonl and summary.json")
    parser.add_argument("--persona", type=Path, default=DEFAULT_PERSONA, help="persona JSON (default: JS1's Cole Palmer)")
    parser.add_argument("--rules", choices=list(RULE_MODES), default="v0.1",
                        help="rule mode: v0.1 (default), v0.2, or v0.1+Cn for one change alone")
    args = parser.parse_args(argv)
    try:
        summary = run_filter(args.run, args.out, args.persona, args.rules)
    except (PersonaError, RunError) as err:
        print(f"error: {err}; nothing was written", file=sys.stderr)
        return 2
    print(f"[{args.rules}] {summary['postings']} postings: {summary['by_verdict']}; "
          f"near-threshold {summary['near_threshold']}; written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
