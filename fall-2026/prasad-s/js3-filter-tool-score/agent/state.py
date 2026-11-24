"""Board response parsing, the id rule, and the state files (CONTRACT.md §1 item 3, §2;
v0.5 item 4; v0.6 items 1-2).

State is one JSON object per run, keyed by board key, each holding that
board's seen ids as strings. All file access goes through the tool layer.
"""

import json
import re
from dataclasses import dataclass

from .errors import RunError

# v0.6 item 1: state/state_<UTC>.json, the UTC time written like 2026-11-06T201500Z.
STATE_NAME = re.compile(r"state_\d{4}-\d{2}-\d{2}T\d{6}Z\.json")
TMP_SUFFIX = ".tmp"


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


def newest_state_file(tools, state_dir):
    """The newest state file by name, or None. Temporary and other files are ignored (v0.6 item 1)."""
    names = sorted(name for name in tools.list_dir(state_dir) if STATE_NAME.fullmatch(name))
    return f"{state_dir}/{names[-1]}" if names else None


def load_state(tools, state_dir):
    """(path, sections). Both are None when state/ holds no state file: every board is a baseline.

    An unreadable or malformed newest file is a RunError: the run ends as error
    and writes no new state (v0.6 item 1).
    """
    path = newest_state_file(tools, state_dir)
    if path is None:
        return None, None
    try:
        data = json.loads(tools.read(path))
    except (OSError, ValueError) as exc:
        raise RunError(f"cannot read state file {path}: {exc}") from exc
    if not isinstance(data, dict) or not all(
        isinstance(key, str) and isinstance(ids, list) and all(isinstance(i, str) for i in ids)
        for key, ids in data.items()
    ):
        raise RunError(f"{path} must be a JSON object of board key -> list of string ids (v0.5 item 4)")
    return path, data


def board_ids(sections, board_key):
    """That board's saved ids, or None when it has none yet: its next valid run is its baseline.

    Decision 2026-11-06: a board with no section is a baseline, like JS1's
    missing state.json; a section that exists, even [], is not (JS1 v0.3).
    """
    if sections is None:
        return None
    return sections.get(board_key)


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


def state_paths(state_dir, stamp):
    final = f"{state_dir}/state_{stamp}.json"
    return final + TMP_SUFFIX, final


def write_state_tmp(tools, state_dir, stamp, sections):
    """v0.6 item 2, first half: the new state goes to a temporary file in state/."""
    tmp, final = state_paths(state_dir, stamp)
    tools.write(tmp, json.dumps(sections, indent=2, sort_keys=True) + "\n")
    return tmp, final


def commit_state(tools, tmp, final):
    """v0.6 item 2, second half: move the temporary file into place. Never overwrites."""
    tools.move(tmp, final)
