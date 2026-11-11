"""Two applicant-tracking systems: Greenhouse and Ashby (public job-board APIs, no auth).

Each provider builds the board URL and parses the response into [{"id": str, "title": str}].
A response that is not the documented shape raises BadData; the loop never guesses a value.
"""
import json
import re
import urllib.parse
from collections import namedtuple

BOARD_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class BadData(ValueError):
    pass


Provider = namedtuple("Provider", "url parse")


def _jobs(raw):
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise BadData(f"not JSON: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise BadData("no 'jobs' list in the response")
    out = []
    for i, j in enumerate(data["jobs"]):
        if not isinstance(j, dict) or j.get("id") in (None, "") or not isinstance(j.get("title"), str):
            raise BadData(f"job #{i} has no id or no title")
        out.append({"id": str(j["id"]), "title": j["title"]})
    return out


def _q(board):
    if not BOARD_NAME.match(board):
        raise ValueError(f"board name {board!r} is not letters, digits, '-' or '_'")
    return urllib.parse.quote(board, safe="")


PROVIDERS = {
    "greenhouse": Provider(lambda b: f"https://boards-api.greenhouse.io/v1/boards/{_q(b)}/jobs", _jobs),
    "ashby": Provider(lambda b: f"https://api.ashbyhq.com/posting-api/job-board/{_q(b)}", _jobs),
}
