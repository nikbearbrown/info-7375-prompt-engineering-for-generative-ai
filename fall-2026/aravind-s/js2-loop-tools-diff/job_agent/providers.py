"""The three job systems (GATE.md, Boards and "Postings from three systems").

A board is a system and a name. The URL is built here from one fixed template per system, and
policy.check_request checks it before any connection opens. Each answer is read into the fields
the rule reads (Ashby's names), by the mapping GATE.md writes down. A broken answer raises
Unverified, and the loop then keeps that board's state exactly as it was (GATE.md, Error policy).
"""

from __future__ import annotations

import html
import json
import re

from .errors import BrokenInput, Unverified

NAME = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
TEMPLATES = {
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{name}",
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{name}?mode=json",
}
SYSTEMS = tuple(TEMPLATES)

# Where each field the rule reads comes from, per system (shown in the report next to each verdict).
MAPPED_FROM = {
    "ashby": {},
    "greenhouse": {"id": "id", "title": "title", "jobUrl": "absolute_url",
                   "employmentType": 'metadata "Employment Type"', "location": "location.name (split at ;)",
                   "descriptionPlain": "content (HTML entities decoded, tags removed)"},
    "lever": {"id": "id", "title": "text", "jobUrl": "hostedUrl", "employmentType": "categories.commitment",
              "location": "categories.allLocations (or categories.location), with country",
              "descriptionPlain": "descriptionPlain, then each of lists (heading and items), then additionalPlain"},
}

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}
# "City, ST" with an optional "United States" after it, as in "San Mateo, CA United States" or "Palo Alto, CA".
PLACE = re.compile(r"\s*(?P<city>[^,;]+?)\s*,\s*(?P<code>[A-Z]{2}|D\.C\.)(?:\s*,?\s*(?:United States|USA|US))?\s*")
_BLOCK_TAG = re.compile(r"<\s*/?\s*(?:br|p|div|li|ul|ol|h[1-6]|tr|table|section|blockquote)\b[^>]*>", re.IGNORECASE)
_TAG = re.compile(r"<[^>]*>")


def board_url(system: str, name: str) -> str:
    """The one URL a board is read from. A list entry that names anything else is broken input."""
    if system not in TEMPLATES:
        raise BrokenInput(f"the board list names the system {system!r}; the gate allows {', '.join(SYSTEMS)}")
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise BrokenInput(f"the board name {name!r} is not 1 to 64 lowercase letters, digits and hyphens")
    return TEMPLATES[system].format(name=name)


def read(system: str, status: int, body: bytes) -> list:
    """The board's postings in the rule's fields, or Unverified naming what is wrong with the answer."""
    if status != 200:
        raise Unverified(f"the board answered HTTP {status}, not 200")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Unverified(f"the board's answer is not JSON ({type(exc).__name__})") from None
    jobs = _jobs(system, data)
    if not jobs:
        raise Unverified("the board's jobs list is empty")
    postings = []
    for index, raw in enumerate(jobs):
        if not isinstance(raw, dict):
            raise Unverified(f"job {index} is not an object")
        posting = MAPPERS[system](raw)
        for key in ("id", "title"):
            value = posting.get(key)
            if not isinstance(value, str) or not value.strip():
                raise Unverified(f"job {index} has no {key}")
        postings.append(posting)
    return postings


def _jobs(system: str, data):
    if system == "lever":  # Lever answers with a list of postings
        if not isinstance(data, list):
            raise Unverified("the board's answer is not a list of postings")
        return data
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Unverified("the board's answer has no jobs list")
    return data["jobs"]


def _ashby(raw: dict) -> dict:
    posting = dict(raw)  # already in the fields the rule reads
    posting["_system"] = "ashby"
    return posting


def _greenhouse(raw: dict) -> dict:
    location = raw.get("location") if isinstance(raw.get("location"), dict) else {}
    places = _split(location.get("name"), ";")
    primary, others = (places[0], places[1:]) if places else (None, [])
    return {
        "_system": "greenhouse",
        "id": _text_id(raw.get("id")),
        "title": raw.get("title"),
        "jobUrl": raw.get("absolute_url"),
        "employmentType": _employment(_metadata(raw, "Employment Type"), {"full-time": "FullTime"}),
        "location": primary,
        "address": postal(primary),
        "secondaryLocations": [{"location": p, "address": postal(p)} for p in others],
        "workplaceType": None,
        "descriptionPlain": html_text(html.unescape(raw.get("content") or "")),
    }


def _lever(raw: dict) -> dict:
    categories = raw.get("categories") if isinstance(raw.get("categories"), dict) else {}
    places = [p.strip() for p in categories.get("allLocations") or [] if isinstance(p, str) and p.strip()]
    if not places and isinstance(categories.get("location"), str) and categories["location"].strip():
        places = [categories["location"].strip()]
    primary, others = (places[0], places[1:]) if places else (None, [])
    country = raw.get("country")
    return {
        "_system": "lever",
        "id": raw.get("id"),
        "title": raw.get("text"),
        "jobUrl": raw.get("hostedUrl"),
        "employmentType": _employment(categories.get("commitment"), {"full-time": "FullTime", "internship": "Intern"}),
        "location": primary,
        "address": postal(primary, country=country),
        "secondaryLocations": [{"location": p, "address": postal(p)} for p in others],
        "workplaceType": raw.get("workplaceType"),
        "_us_remote": raw.get("workplaceType") == "remote" and country == "US",
        "descriptionPlain": _lever_text(raw),
    }


MAPPERS = {"ashby": _ashby, "greenhouse": _greenhouse, "lever": _lever}


def postal(text, country=None) -> dict:
    """An address read from location text: city, then a US state code. Nothing is guessed beyond that."""
    if not isinstance(text, str):
        return {}
    match = PLACE.fullmatch(text)
    code = match.group("code").replace(".", "") if match else None
    if code in US_STATES:
        city = match.group("city").strip()
        if city.lower() == "new york city":  # GATE.md: "New York City" counts as the city New York
            city = "New York"
        return {"postalAddress": {"addressCountry": "United States", "addressRegion": US_STATES[code],
                                  "addressLocality": city}}
    if country == "US":  # Lever's country names the primary location's country
        return {"postalAddress": {"addressCountry": "United States"}}
    return {}


def html_text(markup: str) -> str:
    """Text from HTML: block tags become line breaks, other tags go, entities are decoded."""
    text = _TAG.sub("", _BLOCK_TAG.sub("\n", markup))
    text = html.unescape(text)
    lines = (re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def _lever_text(raw: dict) -> str:
    parts = [raw.get("descriptionPlain")]
    for item in raw.get("lists") or []:
        if isinstance(item, dict):
            parts += [item.get("text"), html_text(item.get("content") or "")]
    parts.append(raw.get("additionalPlain"))
    return "\n".join(p.strip() for p in parts if isinstance(p, str) and p.strip())


def _employment(value, known: dict):
    """GATE.md: a listed spelling is mapped, any other value is kept as written, and a missing one is None."""
    if not isinstance(value, str) or not value.strip():
        return None  # not stated
    return known.get(value.strip().lower(), value.strip())


def _metadata(raw: dict, name: str):
    for item in raw.get("metadata") or []:
        if isinstance(item, dict) and item.get("name") == name and isinstance(item.get("value"), str):
            return item["value"]
    return None


def _split(text, separator: str) -> list:
    if not isinstance(text, str):
        return []
    return [part.strip() for part in text.split(separator) if part.strip()]


def _text_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    return value
