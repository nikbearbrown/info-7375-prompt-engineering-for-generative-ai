"""Posting: the one shape of a job posting that the watch produces and the judges read.

It lives in common/ (not in the watch) so the judges depend only on this small model, never on
how postings are fetched; a board adapter's only job is to produce Postings.
"""

from dataclasses import dataclass

# Greenhouse ids are integers, Ashby ids are UUID strings (JS2 D2). GATE §3 says to keep each
# board's original id, so neither is converted to the other: a Greenhouse id stays an int, which
# also keeps JS1's saved state files and verdicts valid.
PostingId = int | str


@dataclass(frozen=True)
class Posting:
    """The four fields every judge needs. Names in the justification ("title", "location.name",
    "content") are the CONTRACT's field names, which follow the Greenhouse API; other adapters map
    their own fields onto them."""
    id: PostingId
    title: str
    location: str
    content: str  # raw HTML as the board sent it; judges strip it themselves via words.strip_html
