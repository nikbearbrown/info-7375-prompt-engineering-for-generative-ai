"""Text helpers carried over from JS2 (jsagent/rules.py, commit 6a800a2): whole-word matching, HTML to text, US location.

Unchanged from JS2 except that `is_us_location` is split so the bare-"Remote" case (FILTER.md A2) can be told apart.
"""

import html
import re

US_STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
             "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
             "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
             "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
             "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
             "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
             "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"]
US_CODES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
            "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
            "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
            "WI", "WY", "DC"]
US_MARKERS = ["United States", "USA"] + US_STATES
NON_US = ["Canada", "Mexico", "Brazil", "Costa Rica", "United Kingdom", "UK", "Ireland", "Germany", "France",
          "Netherlands", "Belgium", "Spain", "Portugal", "Italy", "Switzerland", "Sweden", "Denmark", "Norway",
          "Finland", "Poland", "Serbia", "Estonia", "India", "China", "Japan", "Korea", "Singapore",
          "Australia", "New Zealand", "Israel", "UAE", "EMEA", "APAC", "LATAM", "Europe", "Asia"]


def find_word(term, text, case_sensitive=False):
    """Whole-word match: the term may not sit inside a longer word ('SQL' does not match 'NoSQL')."""
    return find_span(term, text, case_sensitive) is not None


def find_span(term, text, case_sensitive=False):
    """(start, end) of the first whole-word match, or None. Used to quote evidence."""
    pattern = r"(?<![A-Za-z0-9])" + r"\s+".join(map(re.escape, term.split())) + r"(?![A-Za-z0-9])"
    m = re.search(pattern, text or "", 0 if case_sensitive else re.IGNORECASE)
    return (m.start(), m.end()) if m else None


def plain_text(content):
    """Greenhouse sends content as escaped HTML; unescape twice and drop tags."""
    text = html.unescape(html.unescape(content or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def names_us_place(location):
    """The location names a US place: a US marker, 'US' in capitals, or a capitalised state code."""
    return (any(find_word(m, location) for m in US_MARKERS) or find_word("US", location, True)
            or any(find_word(c, location, True) for c in US_CODES))


def names_non_us_place(location):
    return any(find_word(c, location) for c in NON_US)


def is_us_location(location):
    """JS2 behaviour: a US place, or Remote not tied to a non-US country."""
    if names_us_place(location):
        return True
    return find_word("Remote", location) and not names_non_us_place(location)
