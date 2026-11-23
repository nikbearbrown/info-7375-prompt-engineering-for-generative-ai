"""The shortlist's claims kit (JS3 step 3), made from one filter run BEFORE any human label exists.

THE CLAIMS. Each posting on the run's shortlist gets FILTER.md Section 5's claims, one small statement each:
  1. The posting is full time (R1).
  2. It is in one of Jane's areas, or US remote (R2).
  3. Its title has no level word (R3).
  4. Its title names a software engineering role (R4).
  5. It states no U.S.-person, clearance or no-sponsorship requirement (R5).
  6. It requires no start before May 2027 (R6).
  7. It asks for 3 years or fewer, or makes more years optional (R7).
  8. It describes work in a topic group: one claim per group that earned points, in Section 7's order of groups,
     with the term that earned it, as the filter run's report shows it ("Developer tools (CI/CD)").
The person's facts (her areas, May 2027, 3 years) are read from the profile, as the filter reads them.

THE PASSAGES, word for word from the saved posting (each board's saved answer, checked against the SHA-256 the filter
run recorded). Claims 1 to 4 quote the board's own fields: 1. the employment type (Ashby employmentType, Greenhouse
metadata "Employment Type", Lever categories.commitment); 2. the location fields (Ashby location and
secondaryLocations with their addresses; Greenhouse location.name; Lever categories.allLocations, country and
workplaceType); 3 and 4. the title (Lever: text). Claims 5 to 7 quote every sentence of the description that bears on
them, or "none found": 5. every sentence with a status word (STATUS_WORDS) or one of Section 7's status phrases;
6. every sentence with a start word (START_WORDS), one of Section 7's start phrases, or a month or season with a year;
7. every sentence with a number of years. Claim 8 quotes the sentence that earned the group its points in the filter
run. Sentences are the filter's (FILTER.md Section 6, item 1), joined back where the split fell after "U.S.", "e.g." or
"i.e.", so "To comply with U.S. export control laws ..." stays one sentence; a leading bullet mark is dropped. Every
quoted sentence is a span of the saved description, with each run of white space shown as one space.

THE CHECKER: a rule-based first opinion on every claim, by FILTER.md Section 2's labels. Silence is never support: a
claim the posting says nothing about is insufficient, never supported.
  1. Supported when the employment type, as the agent reads it (GATE.md), is one Section 7 keeps; contradicted when
     another type is stated; insufficient when none is.
  2. R2's reading of the location fields: a place in the person's areas, or US remote, is supported; places only
     elsewhere in the US or outside it are contradicted; no place, or none named clearly, is insufficient.
  3. Contradicted when the title has one of Section 7's level words (whole words); otherwise supported.
  4. Supported when the role part R4 reads has one of Section 7's role phrases and none of its excluded phrases;
     contradicted when it has an excluded phrase; insufficient when it has no role phrase.
  5. Contradicted when a quoted sentence has one of Section 7's status phrases that conflict with the person's status
     (read as R5 reads them, by containment) or a refusal to sponsor (NO_SPONSORSHIP_MORE); supported when a sentence
     says visa sponsorship is offered (SPONSORSHIP_OFFERED, with no negation word in that sentence), since a role
     open to a candidate who needs sponsorship asks neither U.S.-person status nor a clearance; otherwise
     insufficient: "none found", or sentences on the topic that settle nothing, such as an export-control sentence.
  6. Contradicted when a quoted sentence has a start phrase, or a start word with a month and year before the
     earliest start, or a season or quarter with a year lying wholly before it; supported when a sentence with a
     start word gives a month and year on or after the earliest start, or a season wholly after it, or says the start
     is flexible (FLEXIBLE_START); a season that overlaps the earliest start, or "early", "mid" or "late" in its year,
     settles nothing. Contradicted beats unsettled, which beats supported; otherwise insufficient.
  7. Each number of years is read as R7 reads it (a range's smallest number; "N years ago" and "the next N years" are
     not about the candidate): asking the person's years or fewer, or in a sentence with an optional phrase, supports;
     asking more with no optional phrase contradicts, except in a sentence with a company word (Section 6, item 3),
     where it settles nothing. Contradicted beats unsettled, which beats supported; no years sentence is insufficient.
  8. Supported when the sentence names one of the group's terms (Section 6, item 6) with an action word and is about
     this role, its team or its candidate: a list item, a first word that is an action word or one of OPENERS, a
     second-person word, or one of ROLE_WORDS ("this role", "the team", "looking for", "candidates" ...). Otherwise
     insufficient: the sentence may describe the company, not this role (FILTER.md Section 5's counterexample, "We
     build infrastructure for ..."). The checker never labels a topic claim contradicted, and it does not read word
     sense: a term used in another sense passes when the sentence is about the role.
The checker's labels go to sealed/checker-labels.json, whose SHA-256 is printed in README.md. They are committed with
the kit, before any human label, and opened only after Aravind's labels are committed. Only Aravind may mark a claim
supported (FILTER.md Section 2): the checker is a second opinion, never the answer.

The postings appear in an order shuffled with the seed, so a posting's number says nothing about its rank or score.

Usage (from the repo root):
  python3 tools/claims_kit.py js3/filter-run/<run id> [--seed N] [--out js3/claims]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(TOOLS))

import audit_kit  # noqa: E402
from job_agent import filter as flt  # noqa: E402
from job_agent import providers  # noqa: E402
from job_agent.rule import MONTHS, NUMBER_WORDS, YEARS, _MONTH_YEAR, _flat, _has_word, role_part  # noqa: E402
from job_agent.rule import _NOT_A_REQUIREMENT_AFTER, _NOT_A_REQUIREMENT_BEFORE  # noqa: E402

DEFAULT_SEED = 2026112102
SUPPORTED, CONTRADICTED, INSUFFICIENT = "supported", "contradicted", "insufficient"
NONE_FOUND = "none found"
STATUS_WORDS = ("citizen", "citizens", "citizenship", "U.S. person", "U.S. persons", "US person", "US persons",
                "clearance", "clearances", "green card", "permanent resident", "permanent residents",
                "permanent residency", "sponsor", "sponsors", "sponsored", "sponsoring", "sponsorship", "visa", "visas",
                "export control", "export controls", "ITAR", "authorized to work", "authorization to work",
                "work authorization", "employment authorization", "work permit", "immigration", "legal status")
NO_SPONSORSHIP_MORE = ("not sponsor", "n't sponsor", "n’t sponsor", "no visa sponsorship",
                       "not provide sponsorship", "not offer sponsorship", "not provide visa sponsorship",
                       "not offer visa sponsorship")
SPONSORSHIP_OFFERED = ("visa sponsorship is available", "sponsorship is available", "visa sponsorship available",
                       "will sponsor", "can sponsor", "we sponsor", "able to sponsor", "offer visa sponsorship",
                       "offers visa sponsorship", "provide visa sponsorship", "provides visa sponsorship",
                       "sponsor visas", "sponsors visas", "sponsor work visas", "open to sponsoring",
                       "eligible for visa sponsorship", "immigration support")
NEGATIONS = ("not", "no", "unable", "cannot", "can't", "can’t", "never", "without", "won't", "won’t",
             "don't", "don’t", "doesn't", "doesn’t")
START_WORDS = ("start", "starts", "starting", "begin", "begins", "beginning", "commence", "commences")
FLEXIBLE_START = ("flexible start", "start date is flexible", "start dates are flexible", "start date flexible")
ROLE_WORDS = ("this role", "the role", "this position", "the position", "the team", "this team", "our team",
              "looking for", "seeking", "candidate", "candidates")
SECOND_PERSON = ("you", "your", "yours", "yourself")
OPENERS = ("have", "bring", "experience")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December")
SEASON_MONTHS = {"spring": (3, 5), "summer": (6, 8), "fall": (9, 11), "autumn": (9, 11), "winter": (12, 14),
                 "q1": (1, 3), "q2": (4, 6), "q3": (7, 9), "q4": (10, 12)}
TYPES = {1: "R1", 2: "R2", 3: "R3", 4: "R4", 5: "R5", 6: "R6", 7: "R7", 8: "topic words"}
_JOINED_AFTER = re.compile(r"(?:(?<![A-Za-z])U\.S\.|(?<![A-Za-z])[eE]\.g\.|(?<![A-Za-z])[iI]\.e\.)$")
_BULLET = re.compile(r"^[-•*–]\s+")


def earliest_start(profile: dict) -> str:
    """The person's earliest full-time start in words ("2027-05" is "May 2027")."""
    earliest = profile["availability"]["earliest_full_time_start"]
    return f"{MONTH_NAMES[int(earliest[5:7]) - 1]} {earliest[:4]}"


def claim_texts(profile: dict) -> dict:
    """Section 5's eight claims in words, with the person's own facts (the 8th takes the group and its term)."""
    first = (profile.get("name") or "the person").split()[0]
    when = earliest_start(profile)
    years = profile["experience"]["full_time_years"]
    return {1: "The posting is full time.", 2: f"It is in one of {first}'s areas, or US remote.",
            3: "Its title has no level word.", 4: "Its title names a software engineering role.",
            5: "It states no U.S.-person, clearance or no-sponsorship requirement.",
            6: f"It requires no start before {when}.",
            7: f"It asks for {years} years or fewer, or makes more years optional.",
            8: "It describes work in the topic group {group} (\"{term}\")."}


def passage_sentences(text: str) -> list:
    """The description's sentences for quoting: the filter's split (Section 6, item 1), with "U.S.", "e.g." and "i.e."
    kept with what follows. Each sentence is a span of the text."""
    text = text or ""
    pieces, start = [], 0
    for sep in flt._SPLIT.finditer(text):
        pieces.append((text[start:sep.start()], sep.group()))
        start = sep.end()
    pieces.append((text[start:], ""))
    out = []
    for piece, sep in pieces:
        if out and out[-1][1] == " " and (_JOINED_AFTER.search(out[-1][0]) or (
                flt._MONTH_ABBREVIATION_END.search(out[-1][0]) and flt._YEAR_START.match(piece))):
            out[-1] = (out[-1][0] + " " + piece, sep)
            continue
        out.append((piece, sep))
    return [p for p, _ in out if p.strip()]


def quote(sentence: str) -> str:
    """A sentence as the sheet shows it: white space runs as one space, the leading bullet mark dropped."""
    return _BULLET.sub("", _flat(sentence).strip())


# Claims 1 to 4: the board's own fields.

def employment_field(system: str, raw: dict) -> tuple:
    if system == "greenhouse":
        return 'metadata "Employment Type"', providers._metadata(raw, "Employment Type")
    if system == "lever":
        categories = raw.get("categories") if isinstance(raw.get("categories"), dict) else {}
        return "categories.commitment", categories.get("commitment")
    return "employmentType", raw.get("employmentType")


def location_passages(system: str, raw: dict) -> list:
    if system == "greenhouse":
        location = raw.get("location") if isinstance(raw.get("location"), dict) else {}
        return [f"location.name: {_quoted(location.get('name'))}"]
    if system == "lever":
        categories = raw.get("categories") if isinstance(raw.get("categories"), dict) else {}
        places = categories.get("allLocations")
        first = (f"categories.allLocations: {', '.join(_quoted(p) for p in places)}" if places
                 else f"categories.location: {_quoted(categories.get('location'))}")
        return [first, f"country: {_quoted(raw.get('country'))}", f"workplaceType: {_quoted(raw.get('workplaceType'))}"]
    out = [f"location: {_quoted(raw.get('location'))}{_address(raw.get('address'))}"]
    for place in raw.get("secondaryLocations") or []:
        if isinstance(place, dict):
            out.append(f"secondaryLocations: {_quoted(place.get('location'))}{_address(place.get('address'))}")
    return out


def title_field(system: str, raw: dict) -> tuple:
    return ("text", raw.get("text")) if system == "lever" else ("title", raw.get("title"))


def check_employment(posting: dict, rules: dict) -> tuple:
    value = posting.get("employmentType")
    keep = rules["employment_type_keep"]
    if not isinstance(value, str) or not value.strip():
        return INSUFFICIENT, "the employment type is not stated"
    if value in keep:
        return SUPPORTED, f"the employment type is read as {value!r}, one of {keep}"
    return CONTRADICTED, f"the employment type is read as {value!r}, not one of {keep}"


def check_location(posting: dict, profile: dict) -> tuple:
    result = flt.r2_location(posting, profile)
    label = {"preferred": SUPPORTED, "other_us": CONTRADICTED, "outside_us": CONTRADICTED}.get(result["category"],
                                                                                              INSUFFICIENT)
    return label, f"R2's reading: {result['why']}"


def check_level(title: str, rules: dict) -> tuple:
    if not title.strip():
        return INSUFFICIENT, "the posting has no title"
    found = next((w for w in rules["level_words"] if _has_word(title, w)), None)
    if found:
        return CONTRADICTED, f"the title has the level word {found!r}"
    return SUPPORTED, f"the title has none of the {len(rules['level_words'])} level words"


def check_role(title: str, rules: dict) -> tuple:
    if not title.strip():
        return INSUFFICIENT, "the posting has no title"
    part = role_part(title)
    included = next((p for p in rules["role_includes"] if _has_word(part, p)), None)
    excluded = next((p for p in rules["role_excludes"] if _has_word(part, p)), None)
    if excluded:
        return CONTRADICTED, f"the role part {part!r} has the excluded phrase {excluded!r}"
    if included is None:
        return INSUFFICIENT, f"the role part {part!r} has none of the {len(rules['role_includes'])} role phrases"
    return SUPPORTED, f"the role part {part!r} has {included!r} and no excluded phrase"


# Claims 5 to 8: sentences of the description.

def status_passages(sentences: list, rules: dict) -> list:
    phrases = rules["status_us_person_phrases"] + rules["status_sponsorship_phrases"]
    return [s for s in sentences if any(_has_word(s, w) for w in STATUS_WORDS)
            or any(p.lower() in _flat(s).lower() for p in phrases)]


def check_status(passages: list, profile: dict, rules: dict) -> tuple:
    auth = profile["work_authorization"]
    conflicts = []
    if auth["us_person"] is False:
        conflicts += rules["status_us_person_phrases"]
    if auth["needs_sponsorship"] is True:
        conflicts += list(rules["status_sponsorship_phrases"]) + list(NO_SPONSORSHIP_MORE)
    for s in passages:
        found = next((p for p in conflicts if p.lower() in _flat(s).lower()), None)
        if found:
            return CONTRADICTED, f"a sentence has {found!r}"
    for s in passages:
        offer = next((p for p in SPONSORSHIP_OFFERED if _has_word(s, p)), None)
        if offer and not any(_has_word(s, n) for n in NEGATIONS):
            return SUPPORTED, f"a sentence says sponsorship is offered ({offer!r}), with no negation"
    if not passages:
        return INSUFFICIENT, "no sentence speaks to status, sponsorship or clearance; silence is never support"
    return INSUFFICIENT, (f"{len(passages)} sentence(s) speak to status, but none states a U.S.-person, clearance or "
                          "no-sponsorship requirement or offers sponsorship")


def start_passages(sentences: list, rules: dict) -> list:
    return [s for s in sentences if any(_has_word(s, w) for w in START_WORDS)
            or any(p.lower() in _flat(s).lower() for p in rules["start_phrases"])
            or _MONTH_YEAR.search(s) or flt._season_mentions(s, rules)]


def check_start(passages: list, profile: dict, rules: dict) -> tuple:
    earliest = profile["availability"]["earliest_full_time_start"]
    limit = int(earliest[:4]) * 12 + int(earliest[5:7])
    against, unsettled, backing = [], [], []
    for s in passages:
        phrase = next((p for p in rules["start_phrases"] if p.lower() in _flat(s).lower()), None)
        if phrase:
            against.append(f"the start phrase {phrase!r}")
            continue
        if not any(_has_word(s, w) for w in START_WORDS):
            continue
        if any(_has_word(s, p) for p in FLEXIBLE_START):
            backing.append("a flexible start")
        for month, year in _MONTH_YEAR.findall(s):
            when = int(year) * 12 + MONTHS[month.lower()]
            (against if when < limit else backing).append(f"a start word with {month} {year}")
        for word, year in flt._season_mentions(s, rules):
            first, last = _season_span(word, int(year))
            target = against if last < limit else backing if first >= limit else unsettled
            target.append(f"a start word with {word} {year}")
    if against:
        return CONTRADICTED, f"{against[0]}, before {earliest}"
    if unsettled:
        return INSUFFICIENT, f"{unsettled[0]}, which may or may not be before {earliest}"
    if backing:
        return SUPPORTED, f"{backing[0]}, not before {earliest}"
    if not passages:
        return INSUFFICIENT, "no sentence mentions a start or a date; silence is never support"
    return INSUFFICIENT, (f"{len(passages)} sentence(s) mention a start word or a date, but none gives a start month, "
                          "season or a flexible start")


def years_passages(sentences: list) -> list:
    return [s for s in sentences if YEARS.search(s)]


def check_years(passages: list, profile: dict, rules: dict) -> tuple:
    have = profile["experience"]["full_time_years"]
    against, unsettled, backing = [], [], []
    for s in passages:
        optional = next((p for p in rules["years_optional_phrases"] if _has_word(s, p)), None)
        company = next((w for w in rules["years_company_words"] if _has_word(s, w)), None)
        for match in YEARS.finditer(s):
            if _NOT_A_REQUIREMENT_AFTER.match(s[match.end():]) or _NOT_A_REQUIREMENT_BEFORE.search(s[:match.start()]):
                continue
            word = match.group("n").lower()
            n = int(word) if word.isdigit() else NUMBER_WORDS[word]
            if n <= have:
                backing.append(f"asks for {n} years, not more than {have}")
            elif optional:
                backing.append(f"{n} years, marked optional ({optional!r})")
            elif company:
                unsettled.append(f"{n} years in a sentence with the company word {company!r}")
            else:
                against.append(f"asks for {n} years, more than {have}, with no optional phrase")
    if against:
        return CONTRADICTED, against[0]
    if unsettled:
        return INSUFFICIENT, f"{unsettled[0]}: it may not be about the candidate"
    if backing:
        return SUPPORTED, backing[0]
    if not passages:
        return INSUFFICIENT, "no sentence states a number of years; silence is never support"
    return INSUFFICIENT, "every years sentence is about the past or a plan (\"ago\", \"next\"), not the candidate"


def topic_passage(cited: str, sentences: list) -> str:
    """The whole sentence holding the one the filter cited (the same, unless "U.S.", "e.g." or "i.e." split it)."""
    return next((s for s in sentences if cited in _flat(s)), cited)


def check_topic(group: str, passage: str, rules: dict) -> tuple:
    exact = set(rules["case_sensitive_words"])
    term = next((t for t in rules["topic_groups"][group]
                 if (flt._has_exact_word(passage, t) if t in exact else _has_word(passage, t))), None)
    if term is None or not any(_has_word(passage, w) for w in rules["action_words"]):
        return INSUFFICIENT, "the sentence does not name a term of the group with an action word"
    scope = role_scope(passage, rules)
    if scope:
        return SUPPORTED, f"it names {term!r} with an action word, and is about the role ({scope})"
    return INSUFFICIENT, (f"it names {term!r} with an action word, but nothing in it says this is the role's work; "
                          "it may describe the company")


def role_scope(sentence: str, rules: dict):
    """Why the sentence is about this role, its team or its candidate, or None (claim 8's scope test)."""
    flat = _flat(sentence).strip()
    if _BULLET.match(flat):
        return "a list item"
    first = re.match(r"[A-Za-z]+", _BULLET.sub("", flat))
    if first and first.group().lower() in {w.lower() for w in rules["action_words"]} | set(OPENERS):
        return f"it opens with {first.group()!r}"
    word = next((w for w in SECOND_PERSON if _has_word(flat, w)), None)
    if word:
        return f"the word {word!r}"
    phrase = next((p for p in ROLE_WORDS if _has_word(flat, p)), None)
    return f"the phrase {phrase!r}" if phrase else None


def claims_for(posting: dict, raw: dict, system: str, record: dict, profile: dict, rules: dict) -> list:
    """[{type, rule, group, text, passages, field, label, why}] for one shortlisted posting."""
    texts = claim_texts(profile)
    sentences = passage_sentences(posting.get("descriptionPlain") or "")
    title = posting.get("title") or ""
    field, value = employment_field(system, raw)
    title_name, title_value = title_field(system, raw)
    title_passage = [f"{title_name}: {_quoted(title_value)}"]
    out = [(1, [f"{field}: {_quoted(value)}"], True, check_employment(posting, rules)),
           (2, location_passages(system, raw), True, check_location(posting, profile)),
           (3, title_passage, True, check_level(title, rules)),
           (4, title_passage, True, check_role(title, rules))]
    status = status_passages(sentences, rules)
    start = start_passages(sentences, rules)
    years = years_passages(sentences)
    out += [(5, status, False, check_status(status, profile, rules)),
            (6, start, False, check_start(start, profile, rules)),
            (7, years, False, check_years(years, profile, rules))]
    claims = [{"type": t, "rule": TYPES[t], "group": None, "text": texts[t], "passages": p, "field": f,
               "label": label, "why": why} for t, p, f, (label, why) in out]
    for group in rules["topic_groups"]:
        if group not in record["topics"]:
            continue
        passage = topic_passage(record["topics"][group]["sentence"], sentences)
        label, why = check_topic(group, passage, rules)
        text = texts[8].format(group=group, term=record["topics"][group]["term"])
        claims.append({"type": 8, "rule": TYPES[8], "group": group, "text": text,
                       "passages": [passage], "field": False, "label": label, "why": why})
    return claims


def build(run_dir: Path, out_root: Path, seed: int = DEFAULT_SEED) -> Path:
    run_dir = Path(run_dir)
    data = json.loads((run_dir / "verdicts.json").read_text(encoding="utf-8"))
    if not data.get("shortlist"):
        raise SystemExit(f"{run_dir} has no shortlist, so there are no claims to label")
    rules = flt.load_rules(version=data["meta"].get("filter_version", "1.0"))  # the run's own version
    profile = flt.load_profile()
    saved = audit_kit.saved_postings(data)
    systems = {s["key"]: s["system"] for s in data["meta"]["sources"]}
    records = {(r["board"], r["id"]): r for r in data["records"]}
    ranked = [records[(k["board"], k["id"])] for k in data["shortlist"]]
    rank = {(r["board"], r["id"]): n for n, r in enumerate(ranked, 1)}
    order = list(ranked)
    random.Random(seed).shuffle(order)
    run_id = data["meta"]["run_id"]
    out = Path(out_root) / run_id
    if out.exists():
        raise SystemExit(f"{out} already exists; the kit is made once, before any label")
    postings, claims, sheet = [], [], []
    for n, record in enumerate(order, 1):
        posting, raw = saved[(record["board"], record["id"])]
        postings.append({"posting": n, "board": record["board"], "id": record["id"], "title": record["title"],
                         "shortlist_rank": rank[(record["board"], record["id"])], "score": record["score"]})
        sheet += [f"## Posting {n:02}: {record['title'].strip()}", "", f"- Board: {record['board']}",
                  f"- Posting id: `{record['id']}`", f"- Link: {record['jobUrl']}", "",
                  "| Claim | What the shortlist claims | Passages, word for word from the saved posting | Supported | "
                  "Contradicted | Insufficient | Note |", "|---|---|---|---|---|---|---|"]
        letters = iter("abcdefghijklmnopqrstuvwxyz")
        for claim in claims_for(posting, raw, systems[record["board"]], record, profile, rules):
            cid = f"{n:02}.{claim['type']}" + (next(letters) if claim["type"] == 8 else "")
            claims.append({"claim": cid, "posting": n, "type": claim["type"], "rule": claim["rule"],
                           "group": claim["group"], "text": claim["text"], "label": claim["label"],
                           "why": claim["why"]})
            sheet.append(f"| {cid} | {_cell(claim['text'])} | {_passages_cell(claim['passages'], claim['field'])} "
                         "| | | | |")
        sheet.append("")
    sealed = json.dumps({"kit": "claims", "filter_run": run_id, "seed": seed, "postings": postings,
                         "claims": claims}, indent=1, ensure_ascii=False) + "\n"
    (out / "sealed").mkdir(parents=True)
    (out / "sealed" / "checker-labels.json").write_text(sealed, encoding="utf-8")
    digest = hashlib.sha256(sealed.encode("utf-8")).hexdigest()
    texts = claim_texts(profile)
    counts = {t: sum(1 for c in claims if c["type"] == t) for t in TYPES}
    (out / "LABELS.md").write_text("\n".join([
        f"# My claim labels, the shortlist of filter run {run_id}", "",
        f"{len(order)} postings, {len(claims)} claims. For each row, put an x under one of Supported, Contradicted or "
        "Insufficient (FILTER.md Section 2), and a short note: why, and for Insufficient, what is missing. A row left "
        "blank is \"not reviewed\". Silence is never support: \"none found\" means the saved posting does not say. "
        "How to label: INSTRUCTIONS.md.", ""] + sheet), encoding="utf-8")
    saved_on = ", ".join(sorted({s["run"][:10] for s in data["meta"]["sources"] if s.get("run")}))
    (out / "README.md").write_text(readme(run_id, seed, len(order), counts, texts, digest, saved_on),
                                   encoding="utf-8")
    (out / "INSTRUCTIONS.md").write_text(instructions(profile, saved_on), encoding="utf-8")
    return out


def readme(run_id: str, seed: int, n_postings: int, counts: dict, texts: dict, digest: str, saved_on: str) -> str:
    texts = {**texts, 8: "It describes work in a topic group (one claim per group that earned points)."}
    rows = [f"| {t}. {texts[t]} | {TYPES[t]} | {counts[t]} |" for t in TYPES]
    return "\n".join([
        f"# The shortlist's claims, filter run {run_id}", "",
        f"Made by `tools/claims_kit.py` (Claude Code, at Aravind's request) from `js3/filter-run/{run_id}/`, before "
        "any human label existed. The rules for the claims, the passages and the checker are written in the tool's "
        "docstring.", "",
        f"- **The postings:** the {n_postings} on the run's shortlist, shown in LABELS.md in an order shuffled with "
        f"seed **{seed}**, so a posting's number says nothing about its rank or score. The sheet shows no score; the "
        "topic rows are the reason's own claims, so how many there are is visible by design.",
        "- **The claims:** FILTER.md Section 5's list, one small statement each (Section 2: a claim with \"and\" in "
        "it is split in two).",
        f"- **The passages:** word for word from each posting as saved on {saved_on} (the board's saved answer, "
        "checked against the SHA-256 the filter run recorded): the board's own field for claims 1 to 4, every "
        "sentence that bears on claims 5 to 7 (or \"none found\"), and the sentence that earned the points for "
        "claim 8.",
        "- **The checker:** a rule-based first opinion on every claim, by FILTER.md Section 2's labels. Its labels "
        f"are in `sealed/checker-labels.json`, SHA-256 `{digest}`, committed with this kit before any human label. "
        "Only Aravind may mark a claim supported (Section 2); the checker's labels are a second opinion, never the "
        "answer.",
        "", "| Claim | Rule | Claims |", "|---|---|---:|"] + rows + [f"| total | | {sum(counts.values())} |", "",
        "## The order of the steps", "",
        "1. This kit, with the sealed checker labels, is committed before any human label exists.",
        "2. Aravind labels every claim in LABELS.md himself, first (chapter 7: label each row yourself first), and "
        "commits the sheet.",
        "3. Only then is `sealed/checker-labels.json` opened. Its SHA-256 must still be the one above. Claude Code "
        "computes the agreement between the checker and Aravind, by claim type.",
        "4. For each row where they disagree, Claude is asked for the sentence that would change Aravind's label, "
        "and whether it did is recorded (chapter 7).", ""])


def instructions(profile: dict, saved_on: str) -> str:
    prefs = profile["preferences"]
    first = (profile.get("name") or "the person").split()[0]
    areas = ", ".join(prefs["regions"] + prefs["cities"])
    remote = ", ".join(f'"{r}"' for r in prefs["remote_locations"])
    return "\n".join([
        "# How to label the claims", "",
        "1. Open LABELS.md. Each posting on the shortlist has one row per claim: what the shortlist claims, and the "
        f"passages that bear on it, copied word for word from the posting as saved on {saved_on}. Label from the "
        "passages. The link opens today's posting, which may have changed or closed; if you use it, say so in the "
        "note.",
        "2. Put an x in one column per row (FILTER.md Section 2):",
        "   - **Supported:** a passage states the claim, within its scope: the same role, the same place, the same "
        "time.",
        "   - **Contradicted:** a passage states something that cannot be true at the same time as the claim.",
        "   - **Insufficient:** the passages are on the topic but do not settle the claim, or there are none. The "
        "note names what is missing. Silence is never support: \"none found\" means the posting does not say, so the "
        "claim cannot be supported.",
        "   - A row left blank stays **not reviewed**.",
        f"3. {first} (fictional) is an F-1 student, not a U.S. person, who will need H-1B sponsorship later; her "
        f"earliest full-time start is {earliest_start(profile)}; she has {profile['experience']['full_time_years']} "
        f"years of full-time experience. Her areas: {areas}, or US remote ({remote}).",
        "4. Claim 5 covers three requirements at once, as Section 5 writes it: Contradicted if the posting states any "
        "one of them, Supported only if its text says the role is open on status (for example, that it sponsors "
        "visas), otherwise Insufficient. Claims 3 and 4 are about the title's words; claim 8 is about the quoted "
        "sentence: does it say this role's work is in that topic group?",
        "5. Only you may mark a claim supported, and you label each row yourself first (chapter 7). Do not open "
        "`sealed/checker-labels.json` until your labels are committed.",
        "6. After that commit, Claude Code computes how often the checker agrees with you, by claim type. For each "
        "row where you disagree, Claude finds the sentence that would change your label, and you record whether it "
        "did.",
        ""])


def _season_span(word: str, year: int) -> tuple:
    """(first, last) months as year * 12 + month; "early", "mid" and "late" may be any month of the year."""
    first, last = SEASON_MONTHS.get(word.lower(), (1, 12))
    return year * 12 + first, year * 12 + last


def _address(address) -> str:
    postal = address.get("postalAddress") if isinstance(address, dict) else None
    if not isinstance(postal, dict):
        return ""
    parts = [f"{key} {_quoted(postal[key])}" for key in ("addressLocality", "addressRegion", "addressCountry")
             if postal.get(key)]
    return f" (address: {', '.join(parts)})" if parts else ""


def _quoted(value) -> str:
    if not isinstance(value, str) or not value:
        return "not stated"
    return f'"{value}"'


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _passages_cell(passages: list, fields: bool) -> str:
    if not passages:
        return NONE_FOUND
    return "<br>".join(_cell(p) if fields else _cell(f'"{quote(p)}"') for p in passages)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make the shortlist's claims kit from one filter run.")
    parser.add_argument("run", type=Path, help="a filter run folder (js3/filter-run/<run id>)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=REPO / "js3" / "claims")
    args = parser.parse_args(argv)
    out = build(args.run, args.out, args.seed)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
