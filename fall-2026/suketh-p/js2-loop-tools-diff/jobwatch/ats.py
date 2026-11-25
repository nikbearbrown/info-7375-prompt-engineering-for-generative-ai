"""Board payloads from Greenhouse and Ashby, read as postings with a key (GATE.md
'Repeat rule': Greenhouse `id`, Ashby `jobUrl`, a string that is never opened).

Greenhouse payloads go through JS1's board.parse_board unchanged. parse_ashby follows
the same contract: a jobs array, each posting checked, identical duplicates collapsed,
conflicting records with one key rejected."""

import json
from dataclasses import dataclass

from jobwatch import board as greenhouse_board
from jobwatch.errors import InputError


@dataclass(frozen=True)
class Posting:
    key: str
    title: str
    location_name: str
    content: str

    @property
    def id(self):
        """JS1's rule record (jobwatch/rule.py) reports this as posting_id."""
        return self.key


def parse(ats, body):
    if ats == "greenhouse":
        return [Posting(str(p.id), p.title, p.location_name, p.content) for p in greenhouse_board.parse_board(body)]
    if ats == "ashby":
        return parse_ashby(body)
    raise ValueError(f"unknown applicant-tracking system: {ats!r}")


def _ashby_posting(job, where):
    if not isinstance(job, dict):
        raise InputError(f"{where} must be an object")
    url = job.get("jobUrl")
    if not isinstance(url, str) or not url.strip():
        raise InputError(f"{where}.jobUrl must be a nonempty string")
    title = job.get("title")
    if not isinstance(title, str) or not title.strip():
        raise InputError(f"{where}.title must be a nonempty string")
    location = job.get("location")
    if not isinstance(location, str):
        raise InputError(f"{where}.location must be a string")
    content = job.get("descriptionHtml")
    if not isinstance(content, str) or not content.strip():
        raise InputError(f"{where}.descriptionHtml must be a nonempty string")
    return Posting(url, title, location, content)


def parse_ashby(body):
    try:
        data = json.loads(body)
    except ValueError as error:
        raise InputError(f"board response is not valid JSON ({error})") from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise InputError("board response must be an object with a jobs array")
    records, postings = {}, []
    for index, job in enumerate(data["jobs"]):
        posting = _ashby_posting(job, f"jobs[{index}]")
        record = json.dumps(job, sort_keys=True)
        if posting.key in records:
            if records[posting.key] != record:
                raise InputError(f"jobs[{index}]: jobUrl {posting.key} appears twice with different records")
            continue
        records[posting.key] = record
        postings.append(posting)
    return postings
