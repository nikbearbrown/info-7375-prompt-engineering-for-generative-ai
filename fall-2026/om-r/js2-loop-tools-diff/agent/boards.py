"""Board registry (GATE.md "Boards and ATS systems") and the per-ATS URL and
response handling. Only registered boards can be run."""
import json

BOARDS = {
    "gitlab": ("greenhouse", "gitlab"),
    "stripe": ("greenhouse", "stripe"),
    "palantir": ("lever", "palantir"),
    # Exists ONLY to exercise the deliberate-failure path; not a target board.
    "badslug-gitlab-typo": ("greenhouse", "badslug-gitlab-typo"),
}

LEVER_PAGE_SIZE = 100


class MalformedResponse(ValueError):
    pass


def ats_of(board):
    if board not in BOARDS:
        raise ValueError(f"unknown board {board!r}; registered: {sorted(BOARDS)}")
    return BOARDS[board][0]


def page_url(board, page):
    ats, slug = BOARDS[board]
    if ats == "greenhouse":
        assert page == 0, "greenhouse is a single request"
        return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    return f"https://api.lever.co/v0/postings/{slug}?mode=json&limit={LEVER_PAGE_SIZE}&skip={page * LEVER_PAGE_SIZE}"


def parse_page(board, raw):
    """Return (postings, has_more). Postings are normalized to
    {"id", "title", "url"}. Anything not in the documented shape - including
    an empty body - raises MalformedResponse."""
    ats = BOARDS[board][0]
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise MalformedResponse(f"unparseable JSON ({len(raw)} bytes): {e}") from None
    if ats == "greenhouse":
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise MalformedResponse(f"expected an object with a 'jobs' list, got {type(data).__name__}")
        items, id_key, title_key, url_key = data["jobs"], "id", "title", "absolute_url"
        has_more = False
    else:
        if not isinstance(data, list):
            raise MalformedResponse(f"expected a JSON list of postings, got {type(data).__name__}")
        items, id_key, title_key, url_key = data, "id", "text", "hostedUrl"
        has_more = len(data) == LEVER_PAGE_SIZE
    postings = []
    for it in items:
        if not isinstance(it, dict) or it.get(id_key) in (None, ""):
            raise MalformedResponse(f"posting without an {id_key!r}: {str(it)[:120]}")
        postings.append({"id": it[id_key], "title": it.get(title_key), "url": it.get(url_key)})
    return postings, has_more
