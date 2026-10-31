"""The written rule from CONTRACT.md, as a record anyone can recompute.

Each check returns an outcome of "pass", "fail" (a clear exclusion), or "unclear".
Any "fail" makes the verdict not_relevant; otherwise any "unclear" makes it
needs_human; otherwise it is relevant. The phrase lists below are the mechanical
reading of the location, sponsorship, and experience checks accepted on 2026-10-31.
"""
import html
import re
from html.parser import HTMLParser

PASS, FAIL, UNCLEAR = "pass", "fail", "unclear"
RELEVANT, NOT_RELEVANT, NEEDS_HUMAN = "relevant", "not_relevant", "needs_human"

US_STATES = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas", "CA": "california",
    "CO": "colorado", "CT": "connecticut", "DE": "delaware", "DC": "district of columbia",
    "FL": "florida", "GA": "georgia", "HI": "hawaii", "ID": "idaho", "IL": "illinois",
    "IN": "indiana", "IA": "iowa", "KS": "kansas", "KY": "kentucky", "LA": "louisiana",
    "ME": "maine", "MD": "maryland", "MA": "massachusetts", "MI": "michigan", "MN": "minnesota",
    "MS": "mississippi", "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada",
    "NH": "new hampshire", "NJ": "new jersey", "NM": "new mexico", "NY": "new york",
    "NC": "north carolina", "ND": "north dakota", "OH": "ohio", "OK": "oklahoma", "OR": "oregon",
    "PA": "pennsylvania", "RI": "rhode island", "SC": "south carolina", "SD": "south dakota",
    "TN": "tennessee", "TX": "texas", "UT": "utah", "VT": "vermont", "VA": "virginia",
    "WA": "washington", "WV": "west virginia", "WI": "wisconsin", "WY": "wyoming",
}
US_NAMES = ("united states", "united states of america", "usa", "u s a", "u s", "us")
# Every country except the US. "Georgia" is left out because the US state wins that collision.
NON_US_COUNTRIES = (
    "afghanistan", "albania", "algeria", "andorra", "angola", "antigua and barbuda", "argentina",
    "armenia", "australia", "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados",
    "belarus", "belgium", "belize", "benin", "bhutan", "bolivia", "bosnia and herzegovina", "botswana",
    "brazil", "brunei", "bulgaria", "burkina faso", "burundi", "cabo verde", "cambodia", "cameroon",
    "canada", "central african republic", "chad", "chile", "china", "colombia", "comoros", "congo",
    "costa rica", "cote d ivoire", "ivory coast", "croatia", "cuba", "cyprus", "czech republic", "czechia",
    "denmark", "djibouti", "dominica", "dominican republic", "ecuador", "egypt", "el salvador",
    "equatorial guinea", "eritrea", "estonia", "eswatini", "ethiopia", "fiji", "finland", "france",
    "gabon", "gambia", "germany", "ghana", "greece", "grenada", "guatemala", "guinea", "guinea bissau",
    "guyana", "haiti", "honduras", "hong kong", "hungary", "iceland", "india", "indonesia", "iran",
    "iraq", "ireland", "israel", "italy", "jamaica", "japan", "jordan", "kazakhstan", "kenya", "kiribati",
    "kosovo", "kuwait", "kyrgyzstan", "laos", "latvia", "lebanon", "lesotho", "liberia", "libya",
    "liechtenstein", "lithuania", "luxembourg", "macau", "madagascar", "malawi", "malaysia", "maldives",
    "mali", "malta", "marshall islands", "mauritania", "mauritius", "mexico", "micronesia", "moldova",
    "monaco", "mongolia", "montenegro", "morocco", "mozambique", "myanmar", "namibia", "nauru", "nepal",
    "netherlands", "new zealand", "nicaragua", "niger", "nigeria", "north korea", "north macedonia",
    "norway", "oman", "pakistan", "palau", "palestine", "panama", "papua new guinea", "paraguay", "peru",
    "philippines", "poland", "portugal", "qatar", "romania", "russia", "rwanda", "saint lucia", "samoa",
    "san marino", "saudi arabia", "senegal", "serbia", "seychelles", "sierra leone", "singapore",
    "slovakia", "slovenia", "solomon islands", "somalia", "south africa", "south korea", "korea",
    "south sudan", "spain", "sri lanka", "sudan", "suriname", "sweden", "switzerland", "syria", "taiwan",
    "tajikistan", "tanzania", "thailand", "timor leste", "togo", "tonga", "trinidad and tobago",
    "tunisia", "turkey", "turkiye", "turkmenistan", "tuvalu", "uganda", "ukraine", "united arab emirates",
    "uae", "united kingdom", "uk", "england", "scotland", "wales", "northern ireland", "uruguay",
    "uzbekistan", "vanuatu", "vatican", "venezuela", "vietnam", "viet nam", "yemen", "zambia", "zimbabwe",
)

SPONSOR_DENY = (
    r"\b(?:unable to|not able to|cannot|can not|will not|won't|do not|does not|don't|doesn't|"
    r"not in a position to|no longer)\b[^.;]{0,60}?\bsponsor",
    r"\bwithout\b[^.;]{0,50}?\bsponsorship\b",
    r"\b(?:must be|only|open to|limited to|restricted to|requires?)\b[^.;]{0,40}?"
    r"\b(?:u\.?s\.? citizens?|united states citizens?|u\.?s\.? citizenship|permanent residents?|green card holders?)",
    r"\b(?:u\.?s\.? citizens?|united states citizens?|permanent residents?|green card holders?)\b[^.;]{0,30}?\bonly\b",
    r"\bh-?1b transfers? only\b",
    r"\bonly\b[^.;]{0,30}?\bh-?1b transfers?\b",
)
SPONSOR_VAGUE = (
    r"\b(?:may|might|could|possibly|potentially|case[- ]by[- ]case)\b[^.;]{0,50}?\bsponsor",
    r"\bsponsor\w*\b[^.;]{0,50}?\b(?:may|might|case[- ]by[- ]case)\b",
)
SPONSOR_OFFER = (
    r"\b(?:will|we|can|able to|happy to|do)\s+(?:provide\s+|offer\s+)?(?:visa\s+|h-?1b\s+)?sponsor\b",
    r"\b(?:offer|offers|provide|provides)\s+(?:visa\s+|h-?1b\s+)?sponsorship\b",
    r"\bsponsorship\s+(?:is\s+)?(?:available|provided|offered)\b",
    r"\bsponsors?\s+h-?1b\b",
)

YEAR_RANGE = r"(\d{1,2})\s*(?:-|–|—|to)\s*\d{1,2}\s*years?"
YEAR_PATTERNS = (
    r"(\d{1,2})\s*\+\s*years?",
    r"at least\s+(\d{1,2})\s+years?",
    r"minimum (?:of\s+)?(\d{1,2})\s+years?",
    r"(\d{1,2})\s+or more\s+years?",
    r"(\d{1,2})\s+years?\s+(?:of\s+)?(?:[\w-]+\s+){0,4}?experience",
)
NUMBER_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
                "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
EXPERIENCE_CONTEXT = r"experience|years in\b|years of\b|years working"
PREFERRED = r"prefer|nice[- ]to[- ]have|bonus|ideally|\bplus\b"
MANDATORY = r"requir|\bmust\b|minimum|qualifications"
MS_ALTERNATIVE = r"master'?s|\bm\.s\.|\bms degree\b|\bms in\b|graduate degree"


def normalize(text):
    """Lowercase and drop punctuation, so 'Sr.' and 'U.S.' compare as words."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split())


def has_phrase(normalized_text, phrase):
    return f" {normalize(phrase)} " in f" {normalized_text} "


class _Blocks(HTMLParser):
    """Split posting HTML into text blocks and mark the ones that look like headings."""
    BLOCK = {"p", "div", "li", "ul", "ol", "br", "tr", "section", "h1", "h2", "h3", "h4", "h5", "h6"}
    HEADING = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self._buf = [], []
        self._bold = self._heading = self._bold_chars = self._chars = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self._flush()
        if tag in self.HEADING:
            self._heading += 1
        if tag in ("strong", "b"):
            self._bold += 1

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self._flush()
        if tag in self.HEADING:
            self._heading = max(0, self._heading - 1)
        if tag in ("strong", "b"):
            self._bold = max(0, self._bold - 1)

    def handle_data(self, data):
        self._buf.append(data)
        n = len(data.strip())
        self._chars += n
        if self._bold or self._heading:
            self._bold_chars += n

    def _flush(self):
        text = " ".join("".join(self._buf).split())
        if text:
            words = len(text.split())
            is_heading = bool(self._heading) or (words <= 10 and self._bold_chars >= 0.9 * self._chars) \
                or (words <= 8 and text.endswith(":"))
            self.blocks.append((text, is_heading))
        self._buf, self._bold_chars, self._chars = [], 0, 0

    def close(self):
        super().close()
        self._flush()


def description_blocks(content):
    """Greenhouse escapes its HTML once; unescape, then split into (text, is_heading) blocks."""
    parser = _Blocks()
    parser.feed(html.unescape(content or ""))
    parser.close()
    return parser.blocks


def description_text(content):
    """The plain description text that cites to the posting's "content" field are checked against."""
    return " ".join(text for text, _ in description_blocks(content))


def _cite(source, path, value):
    return {"source": source, "path": path, "value": str(value)}


def _sentence_around(text, start, end):
    left = max(text.rfind(". ", 0, start), text.rfind("; ", 0, start))
    left = 0 if left < 0 else left + 2
    right = min([i for i in (text.find(".", end), text.find(";", end)) if i >= 0] or [len(text)])
    return text[left:right + 1].strip()[:300]


def check_title(posting, resume):
    title = (posting.get("title") or "").strip()
    titles = resume["targets"]["titles"]
    if not title:
        return {"outcome": UNCLEAR, "reason": "the posting has no title",
                "cites": [_cite("resume", "targets.titles", ", ".join(titles)), _cite("posting", "id", posting.get("id"))]}
    norm = normalize(title)
    matched = [t for t in titles if has_phrase(norm, t)]
    if not matched:
        return {"outcome": FAIL, "reason": f'"{title}" contains none of the target title phrases',
                "cites": [_cite("resume", "targets.titles", ", ".join(titles)), _cite("posting", "title", title)]}
    return {"outcome": PASS, "reason": f'"{title}" contains "{matched[0]}"', "matched": matched[0],
            "cites": [_cite("resume", "targets.titles", matched[0]), _cite("posting", "title", title)]}


def check_seniority(posting, resume, title_check):
    if title_check["outcome"] != PASS:
        return {"outcome": PASS, "reason": "not applied: no matching title", "cites": []}
    title = posting["title"]
    norm = normalize(title)
    hits = [w for w in resume["targets"]["excluded_seniority"] if has_phrase(norm, w)]
    if hits:
        return {"outcome": FAIL, "reason": f'"{title}" contains the excluded word "{hits[0]}"',
                "cites": [_cite("resume", "targets.excluded_seniority", hits[0]), _cite("posting", "title", title)]}
    return {"outcome": PASS, "reason": "no excluded seniority word in the title", "cites": []}


def classify_place(piece):
    """'us', 'non_us', or 'unknown' for one stated location."""
    norm = normalize(piece)
    if not norm:
        return "unknown"
    if any(has_phrase(norm, name) for name in US_NAMES):
        return "us"
    code = re.search(r",\s*([A-Z]{2})\b", piece)
    if code and code.group(1) in US_STATES:
        return "us"
    if any(has_phrase(norm, state) for state in US_STATES.values()):
        return "us"  # checked before countries so "New Mexico" is not read as Mexico
    if any(has_phrase(norm, country) for country in NON_US_COUNTRIES):
        return "non_us"
    return "unknown"


def _field_status(strings):
    pieces = [p for s in strings for p in re.split(r";|\||/|\bor\b", s or "") if p.strip()]
    if not pieces:
        return "absent"
    kinds = [classify_place(p) for p in pieces]
    if "us" in kinds:
        return "us"  # several locations offered: one clear US option is enough
    if all(k == "non_us" for k in kinds):
        return "non_us"
    return "unknown"


def check_location(posting, resume):
    name = ((posting.get("location") or {}).get("name") or "").strip()
    office_strings = []
    for office in posting.get("offices") or []:
        office_strings += [office.get("name") or "", office.get("location") or ""]
    statuses = {"location.name": _field_status([name]), "offices": _field_status(office_strings)}
    present = {k: v for k, v in statuses.items() if v != "absent"}
    want = _cite("resume", "targets.locations", resume["targets"].get("locations", "US"))
    shown = _cite("posting", "location.name", name) if name else _cite("posting", "id", posting.get("id"))
    values = set(present.values())
    if "us" in values and "non_us" in values:
        return {"outcome": UNCLEAR, "reason": f"location fields conflict about the US: {present}", "cites": [want, shown]}
    if "us" in values:
        return {"outcome": PASS, "reason": f'"{name}" is a US location', "cites": [want, shown]}
    if "non_us" in values:
        return {"outcome": FAIL, "reason": f'"{name}" lists only non-US places', "cites": [want, shown]}
    return {"outcome": UNCLEAR, "reason": f'a US location cannot be established from "{name}"', "cites": [want, shown]}


def _first_match(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text.lower())
        if m:
            return m
    return None


def check_sponsorship(posting, resume):
    text = description_text(posting.get("content"))
    need = _cite("resume", "targets.work_authorization", resume["targets"]["work_authorization"])
    for patterns, outcome, label in ((SPONSOR_DENY, FAIL, "denies or limits sponsorship"),
                                     (SPONSOR_VAGUE, UNCLEAR, "is vague about sponsorship"),
                                     (SPONSOR_OFFER, PASS, "explicitly offers sponsorship")):
        m = _first_match(patterns, text)
        if m:
            base = text if len(text.lower()) == len(text) else text.lower()
            quote = _sentence_around(base, m.start(), m.end())
            return {"outcome": outcome, "reason": f"the description {label}", "cites": [need, _cite("posting", "content", quote)]}
    return {"outcome": UNCLEAR, "reason": "the description has no explicit sponsorship statement",
            "cites": [need, _cite("posting", "title", posting.get("title") or "")] if posting.get("title") else [need]}


def _year_minimums(sentence):
    low = sentence.lower()
    for word, digit in NUMBER_WORDS.items():
        low = re.sub(rf"\b{word}\b", digit, low)
    if not re.search(EXPERIENCE_CONTEXT, low):
        return [], low
    # A range's minimum is its first number; mask ranges so "1-3 years" is not also read as 3.
    found = [int(m.group(1)) for m in re.finditer(YEAR_RANGE, low)]
    masked = re.sub(YEAR_RANGE, " ", low)
    for pattern in YEAR_PATTERNS:
        found += [int(m.group(1)) for m in re.finditer(pattern, masked)]
    return found, low


def check_experience(posting, resume):
    limit = resume["targets"]["max_required_years"]
    have = _cite("resume", "targets.max_required_years", limit)
    heading, results = "", []
    for text, is_heading in description_blocks(posting.get("content")):
        if is_heading:
            heading = text.lower()
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            minimums, low = _year_minimums(sentence)
            for years in minimums:
                if years <= limit:
                    results.append((PASS, sentence, f"{years} years is within {limit}"))
                    continue
                context = f"{low} {heading}"
                if re.search(PREFERRED, context):
                    continue  # experience described only as preferred is ignored
                if re.search(MANDATORY, context):
                    if re.search(MS_ALTERNATIVE, low) and re.search(r"\bor\b", low):
                        results.append((PASS, sentence, f"{years} years, or a master's degree instead"))
                    else:
                        results.append((FAIL, sentence, f"requires {years}+ years, above {limit}"))
                else:
                    results.append((UNCLEAR, sentence, f"{years}+ years, unclear whether mandatory"))
    for outcome in (FAIL, UNCLEAR):
        hit = next((r for r in results if r[0] == outcome), None)
        if hit:
            return {"outcome": outcome, "reason": hit[2], "cites": [have, _cite("posting", "content", hit[1][:300])]}
    return {"outcome": PASS, "reason": "no mandatory experience minimum above the limit", "cites": []}


def judge(posting, resume):
    title = check_title(posting, resume)
    checks = {
        "title": title,
        "seniority": check_seniority(posting, resume, title),
        "location": check_location(posting, resume),
        "sponsorship": check_sponsorship(posting, resume),
        "experience": check_experience(posting, resume),
    }
    outcomes = [c["outcome"] for c in checks.values()]
    verdict = NOT_RELEVANT if FAIL in outcomes else NEEDS_HUMAN if UNCLEAR in outcomes else RELEVANT
    cites, seen = [], set()
    for check in checks.values():
        for c in check["cites"]:
            key = (c["source"], c["path"], c["value"])
            if key not in seen:
                seen.add(key)
                cites.append(c)
    return {
        "posting_id": posting.get("id"),
        "judge": "rule",
        "kind": "record",
        "verdict": verdict,
        "checks": {name: {"outcome": c["outcome"], "reason": c["reason"]} for name, c in checks.items()},
        "cites": cites,
        "reason": "; ".join(f"{name}: {c['outcome']} ({c['reason']})" for name, c in checks.items()),
    }
