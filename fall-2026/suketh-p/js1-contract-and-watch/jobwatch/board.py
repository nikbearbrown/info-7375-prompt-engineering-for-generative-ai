"""The board response contract (CONTRACT.md 'In'): a jobs array whose postings each have a
positive integer id, a nonempty title, a string location.name, and nonempty content."""

import json
from dataclasses import dataclass

from jobwatch.errors import InputError


@dataclass(frozen=True)
class Posting:
    id: int
    title: str
    location_name: str
    content: str


def _posting(job, where):
    if not isinstance(job, dict):
        raise InputError(f"{where} must be an object")
    job_id = job.get("id")
    if type(job_id) is not int or job_id <= 0:
        raise InputError(f"{where}.id must be a positive integer")
    title = job.get("title")
    if not isinstance(title, str) or not title.strip():
        raise InputError(f"{where}.title must be a nonempty string")
    location = job.get("location")
    if not isinstance(location, dict) or not isinstance(location.get("name"), str):
        raise InputError(f"{where}.location.name must be a string")
    content = job.get("content")
    if not isinstance(content, str) or not content.strip():
        raise InputError(f"{where}.content must be a nonempty string")
    return Posting(job_id, title, location["name"], content)


def parse_board(body):
    """Postings in response order. Identical duplicate ids collapse to one; conflicting
    records that share an id are an error."""
    try:
        data = json.loads(body)
    except ValueError as error:
        raise InputError(f"board response is not valid JSON ({error})") from None
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise InputError("board response must be an object with a jobs array")
    records, postings = {}, []
    for index, job in enumerate(data["jobs"]):
        posting = _posting(job, f"jobs[{index}]")
        record = json.dumps(job, sort_keys=True)
        if posting.id in records:
            if records[posting.id] != record:
                raise InputError(f"jobs[{index}]: id {posting.id} appears twice with different records")
            continue
        records[posting.id] = record
        postings.append(posting)
    return postings
