"""Gate G4 (FILTER.md A, "Location"): is the posting in the US? Returns "us", "not_us" or "unknown"."""
from __future__ import annotations

import re

from .textprep import whole_word

STATES = {
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar", "california": "ca", "colorado": "co",
    "connecticut": "ct", "delaware": "de", "florida": "fl", "georgia": "ga", "hawaii": "hi", "idaho": "id",
    "illinois": "il", "indiana": "in", "iowa": "ia", "kansas": "ks", "kentucky": "ky", "louisiana": "la",
    "maine": "me", "maryland": "md", "massachusetts": "ma", "michigan": "mi", "minnesota": "mn",
    "mississippi": "ms", "missouri": "mo", "montana": "mt", "nebraska": "ne", "nevada": "nv",
    "new hampshire": "nh", "new jersey": "nj", "new mexico": "nm", "new york": "ny", "north carolina": "nc",
    "north dakota": "nd", "ohio": "oh", "oklahoma": "ok", "oregon": "or", "pennsylvania": "pa",
    "rhode island": "ri", "south carolina": "sc", "south dakota": "sd", "tennessee": "tn", "texas": "tx",
    "utah": "ut", "vermont": "vt", "virginia": "va", "washington": "wa", "west virginia": "wv",
    "wisconsin": "wi", "wyoming": "wy", "district of columbia": "dc",
}
CODES = set(STATES.values())
US_WORDS = ("united states", "usa", "us", "u.s.")
US_COUNTRY_VALUES = {"united states", "united states of america", "us", "usa"}
SPLIT_RE = re.compile(r";|\||/|(?<![a-z0-9])or(?![a-z0-9])")
TRAILING_CODE_RE = re.compile(r",\s*([a-z]{2})\s*$")
NORTH_AMERICA = whole_word("north america")


def part_place(part: str) -> str:
    """One location part, by name only."""
    p = part.strip().lower()
    if not p:
        return "unknown"
    if any(whole_word(w).search(p) for w in US_WORDS):
        return "us"
    m = TRAILING_CODE_RE.search(p)
    if m and m.group(1) in CODES:
        return "us"
    if any(whole_word(name).search(p) for name in STATES):
        return "us"
    if "remote" in p:
        if NORTH_AMERICA.search(p):
            return "us"
        rest = re.sub(r"[^a-z]+", " ", p.replace("remote", " ")).strip()
        return "unknown" if not rest else "not_us"       # a bare "Remote" is cannot tell; "Remote - Canada" is not
    return "not_us"          # a place the rule does not recognise as US is not guessed to be US


def place_of(name: str, country) -> tuple[str, str]:
    """(place, the text that decided). A country field, when present, decides instead of the name."""
    if country:
        return ("us" if str(country).strip().lower() in US_COUNTRY_VALUES else "not_us"), f"country={country}"
    places = [(part_place(part), part.strip()) for part in SPLIT_RE.split((name or "").lower())]
    places = [x for x in places if x[1]] or [("unknown", "")]
    for want in ("us", "unknown"):
        for pl, part in places:
            if pl == want:
                return pl, part
    return "not_us", places[0][1]


def posting_place(loc: dict) -> dict:
    """Gate G4 for a collected posting: any US entry passes; else unknown if any entry is unknown; else not_us."""
    entries = [(loc.get("name") or "", loc.get("country"))] + [(o.get("name") or "", o.get("country"))
                                                              for o in (loc.get("other") or [])]
    results = [(*place_of(n, c), n) for n, c in entries]
    for want in ("us", "unknown"):
        for pl, why, n in results:
            if pl == want:
                return {"place": pl, "decided_by": why, "entry": n}
    return {"place": "not_us", "decided_by": results[0][1], "entry": results[0][2]}
