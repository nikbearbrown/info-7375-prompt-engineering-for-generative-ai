"""Parsing the board body and building the posting document: CONTRACT.md Order step 7, Out › Citations."""
import html
import json
import re
from dataclasses import dataclass, field

from jobwatch.errors import OTHER, Stop
from jobwatch.textmatch import has_tokens

CONTENT_TEXT_LIMIT = 6000
DOCUMENT_FIELDS = ("id", "title", "location", "absolute_url", "departments")
_ID = re.compile(r"[1-9][0-9]*")
_TAG = re.compile(r"<[^>]*>")


def normalise_id(raw):
    """A positive int (not bool) or a ^[1-9][0-9]*$ string, as a string; otherwise None."""
    if type(raw) is int and raw > 0:
        return str(raw)
    if isinstance(raw, str) and _ID.fullmatch(raw):
        return raw
    return None


def content_text(content):
    """html.unescape, strip tags, html.unescape again, normalise whitespace, keep 6000 characters.

    Greenhouse content is escaped HTML, so the first unescape yields the markup and the second
    turns entities left in its text (such as &nbsp;) into characters (Amendment A3).
    """
    if not isinstance(content, str):
        return ""
    text = html.unescape(_TAG.sub(" ", html.unescape(content)))
    return " ".join(text.split())[:CONTENT_TEXT_LIMIT]


def posting_document(job):
    """Exactly what citations resolve against and what the judge is sent."""
    doc = {k: job[k] for k in DOCUMENT_FIELDS if k in job}
    doc["content_text"] = content_text(job.get("content"))
    return doc


def location_name(job):
    loc = job.get("location")
    name = loc.get("name") if isinstance(loc, dict) else None
    return name if isinstance(name, str) else None


@dataclass
class Parsed:
    total: int
    kept: list = field(default_factory=list)  # (posting_id, job) in response order, first occurrence
    skipped_bad_id: list = field(default_factory=list)
    skipped_bad_title: list = field(default_factory=list)
    duplicates_dropped: int = 0

    def judgeable(self):
        bad = set(self.skipped_bad_title)
        return [(pid, job) for pid, job in self.kept if pid not in bad]


def parse_body(body):
    try:
        data = json.loads(body)
    except ValueError:
        raise Stop(OTHER, 'response body is not JSON') from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Stop(OTHER, 'response body is not {"jobs": [...]}')

    parsed = Parsed(total=len(data["jobs"]))
    seen_here = set()
    for job in data["jobs"]:
        raw_id = job.get("id") if isinstance(job, dict) else None
        pid = normalise_id(raw_id) if isinstance(job, dict) else None
        if pid is None:
            parsed.skipped_bad_id.append(raw_id)
            continue
        if pid in seen_here:
            parsed.duplicates_dropped += 1
            continue
        seen_here.add(pid)
        parsed.kept.append((pid, job))
        title = job.get("title")
        if not isinstance(title, str) or not has_tokens(title):
            parsed.skipped_bad_title.append(pid)
    return parsed
