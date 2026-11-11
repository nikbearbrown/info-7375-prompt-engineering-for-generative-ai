"""Three applicant-tracking systems, one posting shape.

Each posting becomes {"id", "title", "location", "url", "content_text"}. Ids are
"<ats>:<board>:<native id>", so ids from different boards can never collide.
"""
import html
import re


class Malformed(Exception):
    """The response is not a job list for this system."""


URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{board}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{board}",
}


def board_url(ats: str, board: str) -> str:
    if not re.fullmatch(r"[a-z0-9-]+", board):
        raise ValueError(f"board name must be a lowercase token, got {board!r}")
    return URLS[ats].format(board=board)


def html_to_text(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def _greenhouse(data, board):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Malformed("greenhouse: no 'jobs' list")
    return [{"id": f"greenhouse:{board}:{j['id']}", "title": (j.get("title") or "").strip(),
             "location": ((j.get("location") or {}).get("name") or "").strip(),
             "url": j.get("absolute_url") or "", "content_text": html_to_text(j.get("content"))}
            for j in data["jobs"]]


def _lever(data, board):
    if not isinstance(data, list):
        raise Malformed("lever: response is not a list of postings")
    out = []
    for j in data:
        lists = " ".join(f"{x.get('text', '')} {html_to_text(x.get('content'))}" for x in j.get("lists") or [])
        text = " ".join([j.get("descriptionPlain") or "", lists, j.get("additionalPlain") or ""])
        out.append({"id": f"lever:{board}:{j['id']}", "title": (j.get("text") or "").strip(),
                    "location": ((j.get("categories") or {}).get("location") or "").strip(),
                    "url": j.get("hostedUrl") or "", "content_text": re.sub(r"\s+", " ", text).strip()})
    return out


def _ashby(data, board):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise Malformed("ashby: no 'jobs' list")
    return [{"id": f"ashby:{board}:{j['id']}", "title": (j.get("title") or "").strip(),
             "location": (j.get("location") or "").strip(), "url": j.get("jobUrl") or "",
             "content_text": (j.get("descriptionPlain") or html_to_text(j.get("descriptionHtml"))).strip()}
            for j in data["jobs"] if j.get("isListed", True)]


PARSERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def parse(ats: str, data, board: str) -> list[dict]:
    try:
        return PARSERS[ats](data, board)
    except (KeyError, TypeError, AttributeError) as e:
        raise Malformed(f"{ats}: unexpected shape ({type(e).__name__}: {e})")
