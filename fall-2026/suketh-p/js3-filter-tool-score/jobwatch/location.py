"""Which words make a location U.S. (FILTER.md, "Additions before the build").

The student chose the option "Country or state", worded by Claude Code:
"U.S. if it says United States, USA, US or U.S., or names a U.S. state, in full or as a
2-letter code ('San Francisco, CA'). Outside if it names only other countries. Remote,
regions or a bare city go to review. Risk: CA can mean Canada, IN India." Both options said
that a posting with any U.S. location counts as U.S.

Matching uses JS1's tokens (decoded, lowercased, split on everything outside a-z0-9), so
"U.S." is the two tokens "u s" and a two-letter code must be a whole token.

Where the word lists come from (Claude Code's choices, open to the student's revision):
- the U.S. country words are the four the option names;
- the 50 states and their USPS codes, plus the District of Columbia ("dc"), which is not a state;
- "other countries" are the names in jobwatch/data/iso3166.tab, copied unchanged from tzdata
  2026e (public domain), minus the United States and its territories, plus ALIASES below.
  Two-letter country codes are NOT read as country names; a code such as "IN" is only ever
  read as a state.
"""

from pathlib import Path

from jobwatch.normalize import contains_phrase, tokens

US_COUNTRY_WORDS = ("united states", "usa", "us", "u s")

US_STATES = {
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar", "california": "ca",
    "colorado": "co", "connecticut": "ct", "delaware": "de", "florida": "fl", "georgia": "ga",
    "hawaii": "hi", "idaho": "id", "illinois": "il", "indiana": "in", "iowa": "ia",
    "kansas": "ks", "kentucky": "ky", "louisiana": "la", "maine": "me", "maryland": "md",
    "massachusetts": "ma", "michigan": "mi", "minnesota": "mn", "mississippi": "ms",
    "missouri": "mo", "montana": "mt", "nebraska": "ne", "nevada": "nv", "new hampshire": "nh",
    "new jersey": "nj", "new mexico": "nm", "new york": "ny", "north carolina": "nc",
    "north dakota": "nd", "ohio": "oh", "oklahoma": "ok", "oregon": "or", "pennsylvania": "pa",
    "rhode island": "ri", "south carolina": "sc", "south dakota": "sd", "tennessee": "tn",
    "texas": "tx", "utah": "ut", "vermont": "vt", "virginia": "va", "washington": "wa",
    "west virginia": "wv", "wisconsin": "wi", "wyoming": "wy", "district of columbia": "dc",
}

US_WORDS = US_COUNTRY_WORDS + tuple(US_STATES) + tuple(US_STATES.values())

# ISO 3166 codes for the United States and its territories: never "other countries".
US_AND_TERRITORIES = {"US", "AS", "GU", "MP", "PR", "UM", "VI"}

# Names in iso3166.tab that carry a parenthesis, read as these phrases instead.
PARENTHESES = {
    "Britain (UK)": ("britain", "uk"),
    "Korea (North)": ("north korea",),
    "Korea (South)": ("south korea", "korea"),
    "Myanmar (Burma)": ("myanmar", "burma"),
    "Eswatini (Swaziland)": ("eswatini", "swaziland"),
    "Virgin Islands (UK)": ("british virgin islands",),
}

# Added by Claude Code: everyday names the table does not use.
ALIASES = ("united kingdom", "england", "scotland", "wales")

_TABLE = Path(__file__).resolve().parent / "data" / "iso3166.tab"


def _country_phrases():
    phrases = []
    for line in _TABLE.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        code, name = line.split("\t")
        if code in US_AND_TERRITORIES:
            continue
        variants = PARENTHESES.get(name) or (name.split(" (")[0],)
        for variant in variants:
            for form in {variant, variant.replace("&", "and")}:
                phrase = " ".join(tokens(form))
                if phrase and phrase not in phrases:
                    phrases.append(phrase)
    for alias in ALIASES:
        if alias not in phrases:
            phrases.append(alias)
    return tuple(phrases)


COUNTRY_PHRASES = _country_phrases()


def classify(text):
    """One location string -> "us", "outside" or "unresolved", with the words that decided it."""
    words = tokens(text or "")
    us_words = [w for w in US_WORDS if contains_phrase(words, w)]
    countries = [c for c in COUNTRY_PHRASES if contains_phrase(words, c)]
    if us_words:
        outcome = "us"
    elif countries:
        outcome = "outside"
    else:
        outcome = "unresolved"
    return {"text": text, "outcome": outcome, "us_words": us_words, "countries": countries}
