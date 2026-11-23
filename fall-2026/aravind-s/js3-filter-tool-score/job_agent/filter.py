"""JS3's filter (FILTER.md v1.0): what reaches the person, and why.

Every word list and number comes from FILTER.md Section 7 (load_rules). The person's facts (preferred places,
years of experience, earliest start, work authorization) come from the profile passed in: Jane Doe by default, so
every course run and test uses her, and the same engine can be called later on another profile without change.
FILTER.md Sections 1, 2, 3 and 6 say what each rule does; each function names the rule it implements.

Each posting gets a record (judge): its fate ("rejected", "kept" or "cannot_tell"), every rule's result with its
quote, the hard rules that failed (the first, in the order R1 to R8, decides), the rule-level "cannot tell" flags
with their penalties, the score with each term, the topic groups with the sentence that earned each one, and which
of Section 6's implementation choices fired on it. shortlist() then applies the cutoff, duplicates and ties.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import resume as resume_mod
from .providers import US_STATES
from .errors import BrokenInput
from .rule import NUMBER_WORDS, YEARS, _MONTH_YEAR, MONTHS, _flat, _has_word, role_part
from .rule import _NOT_A_REQUIREMENT_AFTER, _NOT_A_REQUIREMENT_BEFORE

REPO = Path(__file__).resolve().parent.parent
FILTER_MD = REPO / "FILTER.md"
JANE = REPO / "persona" / "jane-doe.json"
HARD_RULES = ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8")
RULE_NAMES = {"R1": "employment type", "R2": "location", "R3": "job level", "R4": "job role",
              "R5": "work authorization and sponsorship", "R6": "start date", "R7": "years of experience",
              "R8": "AI training and data annotation"}
REQUIRED_KEYS = ("version", "employment_type_keep", "level_words", "role_includes", "role_excludes",
                 "status_us_person_phrases", "status_sponsorship_phrases", "caution_phrase", "start_phrases",
                 "start_unclear_words", "years_optional_phrases", "years_company_words", "years_max",
                 "action_words", "topic_groups", "case_sensitive_words", "annotation_titles",
                 "annotation_responsibility_phrases", "annotation_task_phrases", "ranking")
RANKING_KEYS = ("start", "per_topic_group", "topic_cap", "other_us_location", "location_cannot_tell",
                "employment_type_cannot_tell", "start_cannot_tell", "years_cannot_tell", "shortlist_min",
                "shortlist_size")
PROFILE_FIELDS = ("experience.full_time_years", "work_authorization.us_person", "work_authorization.needs_sponsorship",
                  "availability.earliest_full_time_start", "preferences.regions", "preferences.cities",
                  "preferences.remote_locations")

# Section 6, item 1: the agent's splitter, except that "Dec. 2026" (a month abbreviation, a period, a year) stays one.
_SPLIT = re.compile(r"(?<=[.!?]) |\r\n|\r|\n")
_MONTH_ABBREVIATION_END = re.compile(r"(?i)\b(?:jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\.$")
_YEAR_START = re.compile(r"^\d{4}\b")
# Section 6, item 2: season and quarter months (vague words such as "early" have none, so they are never decided).
SEASON_FIRST_MONTH = {"spring": 3, "summer": 6, "fall": 9, "autumn": 9, "winter": 12, "q1": 1, "q2": 4, "q3": 7,
                      "q4": 10}
# Section 6, item 5: a US place named in location text.
_US_WORDS = re.compile(r"\b(?:United States|USA|US)\b")
_STATE_CODE = re.compile(r",\s*([A-Z]{2})\b")
_GENERIC_PLACE = re.compile(r"(?i)^[\s,;/()\-]*(?:(?:remote|anywhere|hybrid|flexible|global|worldwide)[\s,;/()\-]*)*$")


def load_rules(path: Path = FILTER_MD, version: str = None) -> dict:
    """The machine-readable copy in FILTER.md Section 7, checked for every key the engine reads.

    FILTER.md keeps every version (a later one is added below with its date, the earlier ones are never edited),
    each with its own Section 7. version=None reads the newest; a run, kit or server tied to an earlier version
    names it (for example "1.0").
    """
    text = Path(path).read_text(encoding="utf-8")
    blocks = []
    for heading in re.finditer(r"^## Section 7[^\n]*\n", text, re.M):
        match = re.search(r"```json\n(.*?)\n```", text[heading.end():], re.S)
        if match:
            blocks.append(match.group(1))
    if not blocks:
        raise BrokenInput(f"{Path(path).name} has no JSON block under '## Section 7'")
    try:
        versions = [json.loads(block) for block in blocks]
    except ValueError as exc:
        raise BrokenInput(f"{Path(path).name} Section 7 is not valid JSON ({exc})") from None
    if version is None:
        rules = versions[-1]
    else:
        rules = next((v for v in versions if v.get("version") == version), None)
        if rules is None:
            raise BrokenInput(f"{Path(path).name} has no Section 7 for version {version}")
    missing = [k for k in REQUIRED_KEYS if k not in rules] + \
              [f"ranking.{k}" for k in RANKING_KEYS if k not in (rules.get("ranking") or {})]
    if missing:
        raise BrokenInput(f"{Path(path).name} Section 7 lacks {', '.join(missing)}")
    return rules


def load_profile(path: Path = JANE) -> dict:
    """The course default: Jane Doe, through the persona validator. Another caller may pass its own profile dict."""
    return resume_mod.load(Path(path))


def check_profile(profile: dict) -> None:
    """The person facts the filter reads (FILTER.md Section 6, item 8) must be present."""
    missing = []
    for field in PROFILE_FIELDS:
        value = profile
        for part in field.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        if value is None:
            missing.append(field)
    if missing:
        raise BrokenInput(f"the profile lacks {', '.join(missing)}, which the filter reads")


def split_sentences(text: str, keeps=()) -> tuple:
    """(sentences, merges): the agent's split, with month abbreviations kept with their year (Section 6, item 1).

    merges lists each sentence the fix kept together, so a report can count how often it fired. keeps lists
    abbreviations the split must not end a sentence after (Section 7's optional "splitter_keeps", a v1.1
    candidate; v1.0 has none, so v1.0 splits after "U.S." as it always did).
    """
    guards = {f"\x00{i}\x00": abbr for i, abbr in enumerate(keeps or ())}
    for mark, abbr in guards.items():
        text = (text or "").replace(abbr, mark)
    pieces, merges, start = [], [], 0
    for sep in _SPLIT.finditer(text or ""):
        pieces.append((text[start:sep.start()], sep.group()))
        start = sep.end()
    pieces.append(((text or "")[start:], ""))
    out = []
    for piece, sep in pieces:
        if out and out[-1][1] == " " and _MONTH_ABBREVIATION_END.search(out[-1][0]) and _YEAR_START.match(piece):
            joined = out[-1][0] + " " + piece
            out[-1] = (joined, sep)
            merges.append(joined)
            continue
        out.append((piece, sep))
    sentences = [p for p, _ in out if p.strip()]
    merges = [m for m in merges if any(m in s for s in sentences)]
    for mark, abbr in guards.items():
        sentences = [s.replace(mark, abbr) for s in sentences]
        merges = [m.replace(mark, abbr) for m in merges]
    return sentences, merges


def judge(posting: dict, profile: dict, rules: dict, board: str = None) -> dict:
    """One posting's record. Every hard rule runs, so an audit can see each one, not only the deciding one."""
    title = posting.get("title") if isinstance(posting.get("title"), str) else ""
    description = posting.get("descriptionPlain") if isinstance(posting.get("descriptionPlain"), str) else ""
    record = {"board": board, "id": posting.get("id"), "title": title, "jobUrl": posting.get("jobUrl"),
              "publishedAt": posting.get("publishedAt"), "locations": _location_texts(posting),
              "employmentType": posting.get("employmentType"), "fate": None, "cannot_tell": None,
              "deciding_rule": None, "rules": [], "failed_rules": [], "flags": [], "location_category": None,
              "topics": {}, "score": None, "score_terms": [], "cautions": [],
              "section6": {"company_words": [], "season_rule": [], "dec_merges": []}}
    reason = posting.get("_cannot_tell")
    if not reason and not title.strip():
        reason = "the posting has no title"
    if not reason and not description.strip():
        reason = "the posting has no description"
    if reason:  # FILTER.md Section 2, "I cannot tell" for a whole posting; Section 3 for the missing field
        record.update(fate="cannot_tell", cannot_tell=reason)
        return record
    sentences, merges = split_sentences(description, rules.get("splitter_keeps", ()))
    record["section6"]["dec_merges"] = merges
    checks = [r1_employment(posting, rules), r2_location(posting, profile), r3_level(title, rules),
              r4_role(title, rules), r5_status(description, sentences, profile, rules, record),
              r6_start(description, sentences, profile, rules, record), r7_years(sentences, profile, rules, record),
              r8_annotation(title, sentences, rules)]
    record["rules"] = checks
    record["location_category"] = checks[1].get("category")
    record["failed_rules"] = [c["rule"] for c in checks if c["result"] == "reject"]
    record["flags"] = [{"rule": c["rule"], "why": c["why"], "penalty": c["penalty"]} for c in checks
                       if c["result"] == "cannot_tell" or c.get("penalty")]
    if record["failed_rules"]:
        first = next(c for c in checks if c["result"] == "reject")
        record.update(fate="rejected", deciding_rule=first["rule"])
        return record
    record["topics"] = topic_groups(sentences, rules)
    record["score"], record["score_terms"] = score(record, rules)
    record["fate"] = "kept"
    return record


def r1_employment(posting: dict, rules: dict) -> dict:
    """R1: keep only the listed type; a missing type is "cannot tell", minus 10."""
    value = posting.get("employmentType")
    if not isinstance(value, str) or not value.strip():
        return _result("R1", "cannot_tell", None, "the employment type is missing",
                       rules["ranking"]["employment_type_cannot_tell"])
    if value in rules["employment_type_keep"]:
        return _result("R1", "pass", value, f"employment type {value!r} is kept")
    return _result("R1", "reject", value, f"employment type {value!r} is not one of {rules['employment_type_keep']}")


def r2_location(posting: dict, profile: dict) -> dict:
    """R2: one preferred place or US remote passes; other US places lose 15; no US place rejects; unclear loses 10.

    Reads the main location, the secondary locations and the structured address (Section 6, item 5).
    """
    prefs = profile["preferences"]
    regions = {r.lower() for r in prefs["regions"]}
    cities = {c.lower() for c in prefs["cities"]}
    remote = {r.strip().lower() for r in prefs["remote_locations"]}
    places = _places(posting)
    us_seen, foreign_seen = [], []
    for text, address in places:
        postal = address.get("postalAddress") if isinstance(address, dict) else None
        postal = postal if isinstance(postal, dict) else {}
        country = str(postal.get("addressCountry") or "")
        region, city = str(postal.get("addressRegion") or ""), str(postal.get("addressLocality") or "")
        is_us_address = country.lower() in ("united states", "usa", "us")
        if is_us_address and (region.lower() in regions or city.lower() in cities):
            return _result("R2", "pass", text, f"{text!r} is in one of the preferred places", category="preferred")
        if isinstance(text, str) and text.strip().lower() in remote:
            return _result("R2", "pass", text, f"{text!r} is one of the person's remote phrases", category="preferred")
        if is_us_address or _names_us(text):
            us_seen.append(text)
        elif isinstance(text, str) and not _GENERIC_PLACE.match(text) or country:
            foreign_seen.append(text or country)
    if posting.get("_us_remote") is True:  # GATE.md: Lever, workplaceType remote and country US
        return _result("R2", "pass", "remote, US", "a Lever posting marked remote with country US",
                       category="preferred")
    if us_seen:
        return _result("R2", "soft", us_seen[0], f"{us_seen[0]!r} is in the US but outside the preferred places",
                       -15, category="other_us")
    if foreign_seen:
        return _result("R2", "reject", "; ".join(str(t) for t in foreign_seen),
                       "every listed location is outside the US", category="outside_us")
    return _result("R2", "cannot_tell", "; ".join(str(t) for t, _ in places if t) or None,
                   "no location field names a US place or another country", -10, category="unclear")


def r3_level(title: str, rules: dict) -> dict:
    """R3: a level word anywhere in the title, as a complete word, rejects."""
    found = next((w for w in rules["level_words"] if _has_word(title, w)), None)
    if found:
        return _result("R3", "reject", title, f"the title contains the level word {found!r}")
    return _result("R3", "pass", title, "no level word in the title")


def r4_role(title: str, rules: dict) -> dict:
    """R4: the role part must contain an included phrase and no excluded phrase, as complete words."""
    part = role_part(title)
    included = next((p for p in rules["role_includes"] if _has_word(part, p)), None)
    excluded = next((p for p in rules["role_excludes"] if _has_word(part, p)), None)
    if included is None:
        return _result("R4", "reject", part, f"the role part {part!r} contains none of the included phrases")
    if excluded is not None:
        return _result("R4", "reject", part, f"the role part {part!r} contains the excluded phrase {excluded!r}")
    return _result("R4", "pass", part, f"the role part {part!r} contains {included!r}")


def r5_status(description: str, sentences: list, profile: dict, rules: dict, record: dict) -> dict:
    """R5: a U.S.-person, clearance or no-sponsorship phrase rejects when it conflicts with the person's status."""
    auth = profile["work_authorization"]
    text = _flat(description).lower()
    groups = []
    if auth["us_person"] is False:
        groups.append(rules["status_us_person_phrases"])
    if auth["needs_sponsorship"] is True:
        groups.append(rules["status_sponsorship_phrases"])
    record["cautions"] = [_flat(s).strip() for s in sentences if rules["caution_phrase"] in _flat(s).lower()]
    for phrases in groups:
        for phrase in phrases:
            if phrase.lower() in text:
                quote = next((_flat(s).strip() for s in sentences if phrase.lower() in _flat(s).lower()), phrase)
                return _result("R5", "reject", quote, f"the description contains {phrase!r}")
    return _result("R5", "pass", None, "no status phrase that conflicts with the person's status")


def r6_start(description: str, sentences: list, profile: dict, rules: dict, record: dict) -> dict:
    """R6: a start phrase, or a month and year before the earliest start, rejects; a season or quarter is unclear.

    Section 6, item 2: a sentence with "start" and a season or quarter word followed by a year, but no month, is
    "cannot tell" unless the season lies wholly after the earliest start.
    """
    earliest = profile["availability"]["earliest_full_time_start"]
    limit = (int(earliest[:4]), int(earliest[5:7]))
    text = _flat(description).lower()
    for phrase in rules["start_phrases"]:
        if phrase.lower() in text:
            quote = next((_flat(s).strip() for s in sentences if phrase.lower() in _flat(s).lower()), phrase)
            return _result("R6", "reject", quote, f"the description contains {phrase!r}")
    unclear = None
    for sentence in sentences:
        if not _has_word(sentence, "start"):
            continue
        months = _MONTH_YEAR.findall(sentence)
        for month, year in months:
            if (int(year), MONTHS[month.lower()]) < limit:
                return _result("R6", "reject", _flat(sentence).strip(),
                               f"a required start in {month} {year}, before {earliest}")
        if months:
            continue
        for word, year in _season_mentions(sentence, rules):
            after = _season_wholly_after(word, int(year), limit)
            record["section6"]["season_rule"].append({"sentence": _flat(sentence).strip(), "season": f"{word} {year}",
                                                      "outcome": "passes" if after else "cannot tell"})
            if not after and unclear is None:
                unclear = (_flat(sentence).strip(), f"{word} {year}")
    if unclear:
        return _result("R6", "cannot_tell", unclear[0], f"the start is given as {unclear[1]!r}, with no month",
                       rules["ranking"]["start_cannot_tell"])
    return _result("R6", "pass", None, "no required start before the earliest start")


def r7_years(sentences: list, profile: dict, rules: dict, record: dict) -> dict:
    """R7: years more than the person's are required by default; optional words excuse; company words are unclear.

    Every sentence with a number of years counts, with or without "experience"; "N years ago" and "the next N years"
    are ignored; a range's smallest number is its minimum (Section 6, item 3).
    """
    have = profile["experience"]["full_time_years"]
    unclear = None
    for sentence in sentences:
        for match in YEARS.finditer(sentence):
            if _NOT_A_REQUIREMENT_AFTER.match(sentence[match.end():]) or \
                    _NOT_A_REQUIREMENT_BEFORE.search(sentence[:match.start()]):
                continue
            word = match.group("n").lower()
            n = int(word) if word.isdigit() else NUMBER_WORDS[word]
            if n <= have:
                continue
            flat = _flat(sentence).strip()
            if any(_has_word(sentence, p) for p in rules["years_optional_phrases"]):
                continue
            company = next((w for w in rules["years_company_words"] if _has_word(sentence, w)), None)
            if company:
                record["section6"]["company_words"].append({"word": company, "sentence": flat, "years": n})
                if unclear is None:
                    unclear = (flat, company, n)
                continue
            return _result("R7", "reject", flat, f"asks for {n} years, more than {have}, with no optional phrase")
    if unclear:
        return _result("R7", "cannot_tell", unclear[0], f"{unclear[2]} years in a sentence with the company word "
                       f"{unclear[1]!r}", rules["ranking"]["years_cannot_tell"])
    return _result("R7", "pass", None, f"no required years above {have}")


def r8_annotation(title: str, sentences: list, rules: dict) -> dict:
    """R8: an annotation title, or a sentence naming the main responsibility as labeling or rating, rejects."""
    found = next((t for t in rules["annotation_titles"] if _has_word(title, t)), None)
    if found:
        return _result("R8", "reject", title, f"the title contains {found!r}")
    for sentence in sentences:
        duty = next((p for p in rules["annotation_responsibility_phrases"] if _has_word(sentence, p)), None)
        task = next((p for p in rules["annotation_task_phrases"] if _has_word(sentence, p)), None)
        if duty and task:
            return _result("R8", "reject", _flat(sentence).strip(), f"{duty!r} with {task!r} in one sentence")
    return _result("R8", "pass", None, "no annotation title or main-responsibility sentence")


def topic_groups(sentences: list, rules: dict) -> dict:
    """{group: the first sentence that earned it}: a term and an action word in the same sentence.

    Terms match as whole words ignoring case, except the case-sensitive words, which must match exactly.
    """
    exact = set(rules["case_sensitive_words"])
    found = {}
    for sentence in sentences:
        if not any(_has_word(sentence, w) for w in rules["action_words"]):
            continue
        for group, terms in rules["topic_groups"].items():
            if group in found:
                continue
            for term in terms:
                hit = _has_exact_word(sentence, term) if term in exact else _has_word(sentence, term)
                if hit:
                    found[group] = {"term": term, "sentence": _flat(sentence).strip()}
                    break
    return found


def score(record: dict, rules: dict) -> tuple:
    """(score, terms): the start, the topic points (capped) and each penalty from Section 1's ranking."""
    rank = rules["ranking"]
    groups = len(record["topics"])
    terms = [("start", rank["start"]),
             (f"{groups} topic group(s), {rank['per_topic_group']} each, capped at {rank['topic_cap']}",
              min(rank["topic_cap"], rank["per_topic_group"] * groups))]
    for flag in record["flags"]:
        if flag["penalty"]:
            terms.append((f"{flag['rule']}: {flag['why']}", flag["penalty"]))
    if record.get("cautions") and rank.get("caution_penalty"):  # optional, a v1.1 candidate; v1.0 has none
        terms.append((f"caution: {rules['caution_phrase']}", rank["caution_penalty"]))
    return sum(points for _, points in terms), terms


def normalized_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").lower()).strip()


def shortlist(records: list, rules: dict) -> dict:
    """The cutoff, one copy per board and normalized title (the newest), the order, and the top N."""
    rank = rules["ranking"]
    eligible = [r for r in records if r["fate"] == "kept" and r["score"] >= rank["shortlist_min"]]
    newest = {}
    for record in eligible:
        key = (record["board"], normalized_title(record["title"]))
        if key not in newest or _newer(record, newest[key]):
            newest[key] = record
    kept_ids = {id(r) for r in newest.values()}
    duplicates = [r for r in eligible if id(r) not in kept_ids]
    ordered = sorted(newest.values(), key=_order)
    return {"eligible": len(eligible), "duplicates_removed": duplicates, "ordered": ordered,
            "top": ordered[:rank["shortlist_size"]]}


def _order(record: dict):
    """Score high to low, then newest first (a missing date counts as oldest), then posting id A to Z."""
    when = _when(record.get("publishedAt"))
    return (-record["score"], 0 if when else 1, -(when.timestamp() if when else 0), str(record["id"]))


def _newer(a: dict, b: dict) -> bool:
    wa, wb = _when(a.get("publishedAt")), _when(b.get("publishedAt"))
    if wa and wb and wa != wb:
        return wa > wb
    if bool(wa) != bool(wb):
        return bool(wa)
    return str(a["id"]) < str(b["id"])


def _when(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        when = datetime.fromisoformat(text)
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(tzinfo=timezone.utc)


def _season_mentions(sentence: str, rules: dict) -> list:
    words = "|".join(re.escape(w) for w in rules["start_unclear_words"])
    return [(m.group(1), m.group(2)) for m in re.finditer(rf"(?i)\b({words})\s+(\d{{4}})\b", sentence)]


def _season_wholly_after(word: str, year: int, limit: tuple) -> bool:
    """Section 6, item 2: wholly after the earliest start; a vague word (early, mid, late) is never decided."""
    if year > limit[0]:
        return True
    first = SEASON_FIRST_MONTH.get(word.lower())
    if year < limit[0] or first is None or word.lower() == "winter":
        return False
    return first > limit[1]


def _places(posting: dict) -> list:
    places = [(posting.get("location"), posting.get("address"))]
    places += [(s.get("location"), s.get("address")) for s in posting.get("secondaryLocations") or []
               if isinstance(s, dict)]
    return places


def _location_texts(posting: dict) -> list:
    return [t for t, _ in _places(posting) if isinstance(t, str) and t.strip()]


def _names_us(text) -> bool:
    if not isinstance(text, str):
        return False
    if _US_WORDS.search(text):
        return True
    return any(code in US_STATES for code in _STATE_CODE.findall(text))


def _has_exact_word(text: str, word: str) -> bool:
    pattern = r"\s+".join(re.escape(piece) for piece in word.split())
    return re.search(rf"(?<![A-Za-z0-9]){pattern}(?![A-Za-z0-9])", text) is not None


def _result(rule: str, result: str, quote, why: str, penalty: int = 0, **extra) -> dict:
    return {"rule": rule, "name": RULE_NAMES[rule], "result": result, "quote": quote, "why": why,
            "penalty": penalty, **extra}
