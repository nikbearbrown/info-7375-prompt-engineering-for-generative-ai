"""Lever Postings API. Shape taken from evidence/manual-capture/20261110T184001Z/04-lever-eu-lever.body and
05-lever-us-palantir.body: a top-level list of {"id": str, "text": str, "categories": {"location": str}, "hostedUrl": str, ...}.
"""
from jobwatch.providers import BoardError, build_postings, classify_http, string_fields, wrong_shape

SYSTEM = "lever"


def url(host, slug, content=False):
    """Lever returns descriptions without a flag; `content` is accepted and has no effect."""
    return f"https://{host}/v0/postings/{slug}?mode=json"


def _fields(item):
    cats = item.get("categories")
    return item.get("id"), item.get("text"), cats.get("location") if isinstance(cats, dict) else None, item.get("hostedUrl")


def _text(item):
    """FILTER.md section 5: description, then each lists[].text heading followed by its
    lists[].content, then additional."""
    pairs = [("description", item.get("description"))]
    lists = item.get("lists")
    for i, entry in enumerate(lists if isinstance(lists, list) else []):
        if isinstance(entry, dict):
            pairs.append((f"lists[{i}].text", entry.get("text")))
            pairs.append((f"lists[{i}].content", entry.get("content")))
    pairs.append(("additional", item.get("additional")))
    return string_fields(pairs)


def parse(result, board):
    data = classify_http(result)
    if isinstance(data, BoardError):
        return data
    if not isinstance(data, list):
        return wrong_shape("expected a top-level JSON list")
    return build_postings(data, board, _fields, _text)
