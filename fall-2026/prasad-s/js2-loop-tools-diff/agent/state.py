"""Board response parsing, the id rule, and state.json (CONTRACT.md §1 item 3, §2)."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .errors import RunError


def parse_board_response(raw):
    """§4 cleanup step 1 (JSON parse) and the §1 id rule.

    Each numeric id becomes str(id) here, once, and the numeric form is
    dropped so nothing downstream can compare a number to a stored string.
    """
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise RunError(f"board response is not JSON: {exc}") from exc
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise RunError("board response has no 'jobs' list")
    postings = []
    for index, job in enumerate(jobs):
        if not isinstance(job, dict) or "id" not in job:
            raise RunError(f"job #{index} in the board response has no id")
        posting = dict(job)
        posting["posting_id"] = str(posting.pop("id"))
        postings.append(posting)
    return postings


def load_state(path):
    """None if state.json does not exist (baseline); otherwise its list of string ids.

    An existing file is never a baseline, even when it holds [] (v0.3).
    """
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RunError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise RunError(f"{path} must be a JSON list of string ids (§1 item 3)")
    return data


@dataclass(frozen=True)
class Watch:
    baseline: bool
    new_ids: list
    state_after: list


def compute_watch(state_before, response_ids):
    """Decide what is new by comparing strings to strings only (§1 item 3, §2).

    state_before is None for a missing state file. state_after keeps every id
    seen up to and including this run, including ids gone from the response.
    """
    for posting_id in response_ids:
        if not isinstance(posting_id, str):
            raise TypeError(f"id {posting_id!r} was not converted with str() at the boundary (§1 item 3)")
    response = list(dict.fromkeys(response_ids))
    if state_before is None:
        return Watch(baseline=True, new_ids=[], state_after=response)
    seen = set(state_before)
    new_ids = [posting_id for posting_id in response if posting_id not in seen]
    return Watch(baseline=False, new_ids=new_ids, state_after=list(dict.fromkeys(state_before)) + new_ids)


def write_state(path, ids):
    """Write state.json in one step, so a crash mid-write cannot leave a partial file."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(list(ids), indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
