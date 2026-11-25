"""Greenhouse Job Board API. Shape taken from evidence/manual-capture/20261110T184001Z/01-greenhouse-stripe.body:
{"jobs": [{"id": int, "title": str, "location": {"name": str}, "absolute_url": str, ...}], "meta": {...}}
"""
from jobwatch.providers import BoardError, build_postings, classify_http, string_fields, wrong_shape

SYSTEM = "greenhouse"


def url(host, slug, content=False):
    """content=True asks for posting descriptions (config/boards.json "content", FILTER.md section 5)."""
    base = f"https://{host}/v1/boards/{slug}/jobs"
    return base + "?content=true" if content else base


def _fields(item):
    loc = item.get("location")
    return item.get("id"), item.get("title"), loc.get("name") if isinstance(loc, dict) else None, item.get("absolute_url")


def _text(item):
    """FILTER.md section 5: Greenhouse text is `content` (escaped HTML)."""
    return string_fields([("content", item.get("content"))])


def parse(result, board):
    data = classify_http(result)
    if isinstance(data, BoardError):
        return data
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        return wrong_shape('expected {"jobs": [...]}')
    return build_postings(data["jobs"], board, _fields, _text)
