"""FILTER.md v1.0, sections 2.2-2.8, as code.

score_posting(posting) takes the common shape agent/adapters.py produces
({"title", "location", "content"}) and returns a decision with points, matched
categories, flags and human-readable reasons naming the rules that fired.

All weights and cutoffs below are hand-set (FILTER.md section 7).
"""

import html
import re

FILTER_VERSION = "1.0"

# ---------- Weights and cutoffs (FILTER.md 2.1, 2.5, 2.6, 7) ----------

TITLE_POINTS = 4
TARGET_LOCATION_POINTS = 2
THRESHOLD = 8
MIN_TITLE_POINTS_FOR_KEEP = 2
YEARS_REJECT_CUTOFF = 8
MIN_DESCRIPTION_WORDS = 50

# ---------- Titles (FILTER.md 2.2, 2.5) ----------

TARGET_TITLES = ("software engineer", "backend engineer", "backend software developer")
REVIEW_TITLE_WORDS = ("senior", "sr", "lead")  # "Sr." normalizes to "sr"
REVIEW_FLAG = "review: senior/lead"

# (rule name, regex over the normalized title)
TITLE_REJECT_RULES = (
    ("Engineering Manager", re.compile(r"\bengineering manager\b")),
    ("Director / VP Engineering", re.compile(r"\b(director|vp|vice president)\b")),
    ("Principal Engineer", re.compile(r"\bprincipal\b(?: \w+)* engineer\b")),
)

# ---------- Technical categories, in FILTER.md 2.3 table order ----------

CATEGORIES = (
    ("Programming", ("java", "python")),
    ("Frameworks", ("spring boot",)),
    ("APIs", ("rest apis", "rest api")),
    ("Databases", ("postgresql", "redis")),
    ("Messaging", ("apache kafka", "kafka")),
    ("Containers", ("docker", "kubernetes")),
    ("Cloud", ("aws", "amazon web services")),
    ("Development workflow", ("git", "ci cd", "continuous integration", "continuous delivery")),
)

# ---------- Years of experience (FILTER.md 2.5) ----------
# Run over lowercased, whitespace-normalized text (punctuation kept, so "8+" survives).

YEARS_PATTERNS = (
    re.compile(r"\b(\d{1,2})\s*\+\s*(?:years|yrs)\b"),                       # 8+ years
    re.compile(r"\b(\d{1,2})\s+or\s+more\s+(?:years|yrs)\b"),                # 8 or more years
    re.compile(r"\bminimum\s+(?:of\s+)?(\d{1,2})\s*\+?\s*(?:years|yrs)\b"),  # minimum (of) 8 years
    re.compile(r"\bat\s+least\s+(\d{1,2})\s*\+?\s*(?:years|yrs)\b"),         # at least 8 years
)
# A minimum stated in the same sentence as one of these is preferred, not mandatory.
PREFERRED_MARKERS = re.compile(r"\b(preferred|preferably|nice to have|bonus|ideally|a plus)\b")

# ---------- Locations (FILTER.md 2.4) ----------
# All entries are in normalized form: lowercase, punctuation -> space, single spaces.

LOCATION_SPLIT = re.compile(r";|\||/| or ", re.IGNORECASE)

TARGET_LOCATIONS = (
    "mountain view",
    "san francisco",          # also covers "San Francisco, CA" and "San Francisco Bay Area"
    "sf",                     # only as its own word, e.g. "SF" or "SF, CA"
    "san francisco bay area",
)

REMOTE_WORDS = ("remote",)

US_COUNTRY_WORDS = ("us", "usa", "u s", "u s a", "united states", "united states of america")

US_STATE_CODES = (
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", "ia",
    "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
    "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt",
    "va", "wa", "wv", "wi", "wy", "dc",
)

# US cities that appear in postings without a state code.
US_CITIES = (
    "new york", "new york city", "nyc", "seattle", "washington dc", "washington d c",
    "palo alto", "sunnyvale", "san jose", "oakland", "los angeles", "san diego", "chicago",
    "austin", "boston", "denver", "nashville", "miami", "honolulu", "atlanta",
)

NON_US_COUNTRIES = (
    "united kingdom", "uk", "england", "scotland", "ireland", "germany", "france", "spain",
    "netherlands", "switzerland", "sweden", "poland", "lithuania", "italy", "portugal",
    "japan", "india", "singapore", "south korea", "korea", "australia", "new zealand",
    "brazil", "mexico", "canada", "united arab emirates", "uae", "china", "israel",
)

NON_US_CITIES = (
    "london", "dublin", "munich", "berlin", "paris", "madrid", "amsterdam", "zurich",
    "stockholm", "warsaw", "vilnius", "tokyo", "seoul", "singapore", "sydney", "canberra",
    "melbourne", "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "hyderabad",
    "são paulo", "sao paulo", "mexico city", "toronto", "ontario", "abu dhabi", "dubai",
)

# Location classes, best first
TARGET, US_OTHER, UNKNOWN, NON_US = "target", "us_other", "unknown", "non_us"


# ---------- Text helpers (FILTER.md 2.8, 4.5) ----------

def clean_text(raw) -> str:
    """html.unescape first, then each tag -> a space, then collapse whitespace."""
    if not isinstance(raw, str):
        return ""
    text = html.unescape(raw)
    text = re.sub(r"<[^>]*>", " ", text)
    return " ".join(text.split())


def normalize(text: str) -> str:
    """Lowercase, punctuation -> space, single spaces. Used for whole-word matching."""
    return " ".join(re.sub(r"[^\w]+", " ", text.lower()).split())


def has_phrase(normalized_text: str, phrase: str) -> bool:
    """Whole-word / whole-phrase match on normalized text; never a substring."""
    return f" {phrase} " in f" {normalized_text} "


def _present(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


# ---------- Rules ----------

def _title_points(norm_title):
    for t in TARGET_TITLES:
        if has_phrase(norm_title, t):
            return TITLE_POINTS, t
    return 0, None


def _categories(norm_text):
    """[(category, first matching keyword)] in FILTER.md 2.3 order, each at most once."""
    found = []
    for name, keywords in CATEGORIES:
        for kw in keywords:
            if has_phrase(norm_text, kw):
                found.append((name, kw))
                break
    return found


def _years_minimum(text):
    """The first explicit mandatory minimum >= cutoff, as (years, phrase), or None."""
    lowered = text.lower()
    sentences = re.split(r"(?<=[.!?;])\s+", lowered)
    for sentence in sentences:
        for pattern in YEARS_PATTERNS:
            for m in pattern.finditer(sentence):
                n = int(m.group(1))
                if n >= YEARS_REJECT_CUTOFF and not PREFERRED_MARKERS.search(sentence):
                    return n, m.group(0)
    return None


def _classify_location_part(part):
    norm = normalize(part)
    if not norm:
        return UNKNOWN
    if any(has_phrase(norm, p) for p in TARGET_LOCATIONS):
        return TARGET
    us_country = any(has_phrase(norm, w) for w in US_COUNTRY_WORDS)
    if any(has_phrase(norm, w) for w in REMOTE_WORDS) and us_country:
        return TARGET  # Remote explicitly open to US applicants
    # A state code counts only after a comma ("Seattle, WA"), so words like "in"/"or" don't.
    state = re.search(r",\s*([A-Za-z]{2})\.?\s*$", part.strip())
    has_state = bool(state) and state.group(1).lower() in US_STATE_CODES
    if us_country or has_state or any(has_phrase(norm, c) for c in US_CITIES):
        return US_OTHER
    if any(has_phrase(norm, c) for c in NON_US_COUNTRIES + NON_US_CITIES):
        return NON_US
    return UNKNOWN


def classify_location(location):
    """Return (class, points, per-part classes). Best eligible part wins (FILTER.md 2.4)."""
    if not _present(location):
        return UNKNOWN, 0, []
    parts = [p.strip() for p in LOCATION_SPLIT.split(location) if p.strip()]
    classes = [(p, _classify_location_part(p)) for p in parts]
    kinds = {c for _, c in classes}
    if TARGET in kinds:
        return TARGET, TARGET_LOCATION_POINTS, classes
    if US_OTHER in kinds:
        return US_OTHER, 0, classes
    if kinds == {NON_US}:
        return NON_US, 0, classes
    return UNKNOWN, 0, classes  # ambiguous or missing is never treated as non-US


# ---------- Decision (FILTER.md 2.7) ----------

def score_posting(posting):
    title, location, content = posting.get("title"), posting.get("location"), posting.get("content")
    reasons, flags = [], []
    result = {
        "decision": None, "score": None, "title_points": None, "location_points": None,
        "categories": [], "flags": flags, "reasons": reasons, "location_class": None,
    }

    def done(decision, why):
        reasons.append(f"decision: {decision} ({why})")
        result["decision"] = decision
        return result

    # Title (2.2) -------------------------------------------------------
    if not _present(title):
        reasons.append("title missing (§2.7, §4.4)")
        return done("CANNOT TELL", "title missing; role relevance not calculated")
    norm_title = normalize(clean_text(title))
    title_pts, title_hit = _title_points(norm_title)
    result["title_points"] = title_pts
    if title_hit:
        reasons.append(f"title matches '{title_hit}': +{title_pts} (§2.2)")
    else:
        reasons.append("title matches no target role: +0 (§2.2)")
    review = [w for w in REVIEW_TITLE_WORDS if has_phrase(norm_title, w)]
    if review:
        flags.append(REVIEW_FLAG)
        reasons.append(f"title contains '{review[0]}': flagged for review, not rejected (§2.5)")

    # Location (2.4) ----------------------------------------------------
    loc_class, loc_pts, parts = classify_location(location)
    result["location_class"] = loc_class
    if _present(location):
        detail = "; ".join(f"'{p}' = {c}" for p, c in parts)
        reasons.append(f"location {detail} -> {loc_class}, +{loc_pts} (§2.4)")
    else:
        reasons.append("location missing -> unknown (§2.4, §4.4)")

    # Description (2.6) -------------------------------------------------
    text = clean_text(content)
    words = len(text.split())
    description_ok = words >= MIN_DESCRIPTION_WORDS
    cats = []
    if description_ok:
        cats = _categories(normalize(text))
        result["categories"] = [c for c, _ in cats]
        result["location_points"] = loc_pts
        result["score"] = title_pts + len(cats) + loc_pts
        if cats:
            hits = ", ".join(f"{c} ('{kw}')" for c, kw in cats)
            reasons.append(f"technical categories {hits}: +{len(cats)} (§2.3)")
        else:
            reasons.append("no technical category matched: +0 (§2.3)")

    # Mandatory rejections decidable without the description (2.5) ------
    for rule, pattern in TITLE_REJECT_RULES:
        if pattern.search(norm_title):
            reasons.append(f"title is '{rule}' (§2.5)")
            return done("REJECT", f"mandatory negative rule: {rule}")
    if loc_class == NON_US:
        reasons.append("every listed location is outside the US (§2.4, §2.5)")
        return done("REJECT", "mandatory negative rule: explicit non-US-only position")

    # Missing or nearly empty description (2.6) -------------------------
    if not description_ok:
        if not _present(content):
            reasons.append("description missing (§2.6)")
        else:
            reasons.append(f"description has {words} words, fewer than {MIN_DESCRIPTION_WORDS} (§2.6)")
        return done("CANNOT TELL", "I cannot tell from the available posting text")

    # Years of experience (2.5) -----------------------------------------
    years = _years_minimum(text)
    if years:
        reasons.append(f"explicit minimum '{years[1]}' >= {YEARS_REJECT_CUTOFF} years (§2.5)")
        return done("REJECT", f"mandatory negative rule: {YEARS_REJECT_CUTOFF}+ years required")

    # Score conditions (2.7) --------------------------------------------
    score = result["score"]
    best_case = score + (TARGET_LOCATION_POINTS if loc_class == UNKNOWN else 0)
    failures = []
    if title_pts < MIN_TITLE_POINTS_FOR_KEEP:
        failures.append(f"title points {title_pts} < {MIN_TITLE_POINTS_FOR_KEEP}")
    if not cats:
        failures.append("no technical category")
    if best_case < THRESHOLD:
        failures.append(f"score {score} < {THRESHOLD}"
                        + (" even with +2 for the unknown location" if loc_class == UNKNOWN else ""))
    if failures:
        return done("REJECT", "; ".join(failures) + " (§2.7)")

    if loc_class == UNKNOWN:
        why = "location missing" if not _present(location) else "geographic eligibility unknown"
        return done("CANNOT TELL", f"would otherwise qualify, but {why} (§2.7)")

    return done("KEEP", f"score {score} >= {THRESHOLD}, title >= {MIN_TITLE_POINTS_FOR_KEEP}, "
                        f"{len(cats)} technical categor{'y' if len(cats) == 1 else 'ies'}, "
                        f"eligible US location (§2.7)")
