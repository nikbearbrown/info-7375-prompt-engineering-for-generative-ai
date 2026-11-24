"""Two applicant-tracking systems, one posting shape.

Every posting becomes {key, system, board, id, title, location, text, url}. The key is
(system, board, id): ids are only unique inside one board (GATE.md, repeat rule).
"""
from __future__ import annotations

import json
import re
from urllib.parse import quote

from .rule import plain_text


class BadResponse(Exception):
    """The response is not JSON, or not the shape this system returns."""


GREENHOUSE_TOKEN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def _json(raw: bytes):
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise BadResponse(f"not JSON: {e}") from e


def _posting(system, board, pid, title, location, text, url):
    return {"key": f"{system}:{board}:{pid}", "system": system, "board": board, "id": pid,
            "title": (title or "").strip(), "location": (location or "").strip(),
            "text": (text or "").strip(), "url": url}


class Greenhouse:
    name = "greenhouse"

    @staticmethod
    def url(board: str) -> str:
        if not GREENHOUSE_TOKEN.match(board or ""):
            raise BadResponse(f"not a Greenhouse board token: {board!r}")
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

    @staticmethod
    def parse(board: str, raw: bytes) -> list:
        data = _json(raw)
        jobs = data.get("jobs") if isinstance(data, dict) else None
        if not isinstance(jobs, list) or not all(isinstance(j, dict) and "id" in j for j in jobs):
            raise BadResponse("not a Greenhouse board (no jobs[] with ids)")
        return [_posting("greenhouse", board, j["id"], j.get("title"), (j.get("location") or {}).get("name"),
                         plain_text(j.get("content") or ""), j.get("absolute_url")) for j in jobs]


class Ashby:
    name = "ashby"

    @staticmethod
    def url(board: str) -> str:
        if not board or "/" in board or ".." in board:
            raise BadResponse(f"not an Ashby board name: {board!r}")
        return f"https://api.ashbyhq.com/posting-api/job-board/{quote(board, safe='')}"

    @staticmethod
    def parse(board: str, raw: bytes) -> list:
        data = _json(raw)
        jobs = data.get("jobs") if isinstance(data, dict) else None
        if not isinstance(jobs, list) or not all(isinstance(j, dict) and "id" in j for j in jobs):
            raise BadResponse("not an Ashby job board (no jobs[] with ids)")
        out = []
        for j in jobs:
            if j.get("isListed") is False:
                continue
            text = j.get("descriptionPlain") or plain_text(j.get("descriptionHtml") or "")
            out.append(_posting("ashby", board, j["id"], j.get("title"), j.get("location"), text, j.get("jobUrl")))
        return out


SYSTEMS = {"greenhouse": Greenhouse, "ashby": Ashby}
