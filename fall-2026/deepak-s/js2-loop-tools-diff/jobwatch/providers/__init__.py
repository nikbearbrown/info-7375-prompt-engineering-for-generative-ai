"""One interface for three applicant-tracking systems: GATE.md section 4.

    provider.url(host, slug) -> str
    provider.parse(result, board) -> list[Posting] | BoardError

parse() never returns an empty list when in doubt: it returns [] only for a 200 with a JSON
content-type, a JSON body and the system's postings array present and empty. Everything else
is a BoardError, with `retryable` set from the GATE.md section 4 table.
"""
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Posting:
    id: str
    title: str
    location: str | None
    url: str | None
    board: str


@dataclass(frozen=True)
class BoardError:
    kind: str
    retryable: bool
    detail: str = ""
    http_status: int | None = None
    retry_after: str | None = None


def media_type(content_type):
    return (content_type or "").split(";")[0].strip().lower()


def classify_http(result):
    """The status and content-type rows of GATE.md section 4. Returns parsed JSON or a BoardError."""
    status = result.status
    if result.error is not None:
        return BoardError(result.error, True, f"no HTTP response ({result.error})")
    if 300 <= status < 400:
        return BoardError("redirect_refused", False, f"redirect to {result.headers.get('location')!r} refused",
                          http_status=status)
    if status == 429:
        return BoardError("http_429", False, "rate limited", http_status=status,
                          retry_after=result.headers.get("retry-after"))
    if 400 <= status < 500:
        return BoardError(f"http_{status}", False, "client error", http_status=status)
    if status >= 500:
        return BoardError(f"http_{status}", True, "server error", http_status=status)
    if status != 200:
        return BoardError(f"http_{status}", False, "unexpected status", http_status=status)
    if media_type(result.content_type) != "application/json":
        return BoardError("non_json", True, f"content-type {result.content_type!r}", http_status=status)
    try:
        return json.loads(result.body)
    except ValueError:
        return BoardError("non_json", True, "body is not JSON", http_status=status)


def wrong_shape(detail, status=200):
    return BoardError("wrong_shape", False, detail, http_status=status)


def posting_id(raw):
    if type(raw) is int and raw > 0:
        return str(raw)
    if isinstance(raw, str) and raw.strip():
        return raw
    return None


def build_postings(items, board, fields):
    """`fields(item)` -> (raw id, title, location, url). Any malformed item fails the whole board."""
    out = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            return wrong_shape(f"posting {i} is not an object")
        raw_id, title, location, url = fields(item)
        pid = posting_id(raw_id)
        if pid is None or not isinstance(title, str) or not title.strip():
            return wrong_shape(f"posting {i} has no usable id or title")
        out.append(Posting(pid, title, location if isinstance(location, str) else None,
                           url if isinstance(url, str) else None, board))
    return out


def get(system):
    from jobwatch.providers import ashby, greenhouse, lever

    return {"greenhouse": greenhouse, "lever": lever, "ashby": ashby}[system]
