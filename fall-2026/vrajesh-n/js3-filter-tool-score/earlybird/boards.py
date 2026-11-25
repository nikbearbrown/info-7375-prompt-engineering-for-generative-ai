"""Board list, URLs, and one parser per ATS. Each posting is normalized to the field names JS1's rule reads."""
import html
import json
import re

URLS = {
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{name}",
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{name}?mode=json",
}


class ShapeError(ValueError):
    """The response is not JSON, or not the shape this platform sends. Never treated as an empty board."""


def load(text):
    boards = json.loads(text)
    for b in boards:
        if b["platform"] not in URLS:
            raise ValueError(f"unknown platform {b['platform']!r} for {b['key']}")
        if b["key"] != f"{b['platform']}:{b['name']}":
            raise ValueError(f"key {b['key']!r} must be platform:name")
    return boards


def url(board):
    return URLS[board["platform"]].format(name=board["name"])


def raw_name(board):
    return f"{board['platform']}_{board['name']}.json"


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
_US_WORDS = re.compile(r"\bunited states\b|\busa\b|\bu\.s\.(a\.)?|\bwashington,? d\.?c\.?", re.I)
_US_CODE = re.compile(r"\bUS\b")  # upper case only, so the English word "us" does not count
_STATE_CODE = re.compile(r",\s*(" + "|".join(US_STATES) + r")\b")
_STATE_NAME = re.compile(r"\b(" + "|".join(sorted(US_STATES.values(), key=len, reverse=True)) + r")\b", re.I)


# Review revision (Vrajesh, 2026-11-10): "If CA is preceded by a known Canadian city ... map it to Canada".
_CANADA_CA = re.compile(r"\b(toronto|vancouver|montreal|montréal|ottawa|calgary|edmonton|waterloo|winnipeg|"
                        r"halifax|quebec|victoria|mississauga|kitchener)\s*,\s*CA\b", re.I)
# Review revision: bare US city names resolve to the US. "Keep It to United States Only": no world list,
# only well-known US tech-hiring cities, plus the upper-case short forms seen in the 2026-11-01 data.
_US_CITY = re.compile(r"\b(new york city|san francisco|bay area|silicon valley|chicago|seattle|los angeles|boston|"
                      r"austin|denver|atlanta|san jose|palo alto|mountain view|sunnyvale|menlo park|redmond|"
                      r"san diego|philadelphia|pittsburgh|miami|dallas|houston|phoenix|salt lake city)\b", re.I)
_US_CITY_CODE = re.compile(r"\b(NYC|SF|SEA)\b")


def us_from_location(text):
    """Greenhouse has no country field, only free text such as 'San Mateo, CA, United States' or
    'Bellevue, Washington; ...; Vancouver, Canada'. Return 'USA' if any listed place is in the US, else None.
    A posting open in several places counts as US if one of them is (the applicant can pick that office)."""
    text = _CANADA_CA.sub(r"\1, Canada", text or "")  # 'Toronto, CA' is Canada, not California
    if (_US_WORDS.search(text) or _US_CODE.search(text) or _STATE_CODE.search(text) or _STATE_NAME.search(text)
            or _US_CITY.search(text) or _US_CITY_CODE.search(text)):
        return "USA"
    return None


def plain(markup):
    """Greenhouse content is HTML escaped once more; unescape twice, drop tags, squeeze spaces."""
    text = html.unescape(html.unescape(markup or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def parse(platform, body):
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ShapeError(f"not JSON: {e}") from e
    if platform in ("ashby", "greenhouse"):
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise ShapeError(f"{platform} response has no 'jobs' list")
        items = data["jobs"]
    elif platform == "lever":
        if not isinstance(data, list):
            raise ShapeError("lever response is not a list")
        items = data
    else:
        raise ShapeError(f"unknown platform {platform!r}")
    return [normalize(platform, j) for j in items]


def normalize(platform, j):
    if platform == "ashby":
        return {"id": str(j["id"]), "title": j.get("title", ""), "location": j.get("location"),
                "address": j.get("address"), "descriptionPlain": j.get("descriptionPlain", ""),
                "url": j.get("jobUrl")}
    if platform == "greenhouse":
        location = (j.get("location") or {}).get("name")
        # The country is always present (None when no US place is named), so R3's citation of it is real.
        return {"id": str(j["id"]), "title": j.get("title", ""), "location": location,
                "address": {"postalAddress": {"addressCountry": us_from_location(location)}},
                "country_inferred_from": "location.name",
                "descriptionPlain": plain(j.get("content")), "url": j.get("absolute_url")}
    # lever
    lists = " ".join(f"{li.get('text', '')} {plain(li.get('content'))}" for li in j.get("lists") or [])
    country = j.get("country")
    return {"id": str(j["id"]), "title": j.get("text", ""),
            "location": (j.get("categories") or {}).get("location"),
            "address": {"postalAddress": {"addressCountry": country}} if country else None,
            "descriptionPlain": " ".join(x for x in (j.get("descriptionPlain", ""), lists,
                                                    j.get("additionalPlain", "")) if x).strip(),
            "url": j.get("hostedUrl")}
