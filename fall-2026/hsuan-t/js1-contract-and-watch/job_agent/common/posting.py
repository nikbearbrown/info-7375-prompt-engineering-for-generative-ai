"""Posting: the one shape of a job posting that the watch produces and the judges read.

It lives in common/ (not in the watch) so the judges depend only on this small model, never on
how postings are fetched; a board adapter's only job is to produce Postings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Posting:
    """The four fields every judge needs. Names in the justification ("title", "location.name",
    "content") are the CONTRACT's field names, which follow the Greenhouse API."""
    id: int
    title: str
    location: str
    content: str  # raw HTML as the board sent it; judges strip it themselves via words.strip_html
