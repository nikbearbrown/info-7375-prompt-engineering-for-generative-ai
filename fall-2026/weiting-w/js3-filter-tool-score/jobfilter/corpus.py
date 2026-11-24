"""The corpus: JS2's captured postings, with their body text where it exists.

No network. This reads the raw HTTP responses JS2 saved on 2026-11-11T00:18Z
and committed in `../js2-loop-tools-diff/evidence/raw/`, so every posting JS3
judges is a posting that a real board really returned, and the same bytes are
available to anyone with the repository.

**Which fields make up "the body".** FILTER.md §1 scores the plain-text body
and never markup, and the three systems disagree about where that text lives:

| board | body is built from |
|---|---|
| `ashby:*` | `descriptionPlain` |
| `lever:*` | `descriptionPlain` + `additionalPlain` + each `lists[].text` and `lists[].content` |
| `greenhouse:*` | **nothing — the endpoint returns no description** |

Lever is the awkward one. Its `descriptionPlain` is a one-paragraph preamble
(~1.1 KB); the actual duties and requirements live in `lists`, whose `content`
is HTML. Dropping `lists` would score Lever postings on their marketing blurb
alone, so the HTML is stripped to text first — tags *and* their attributes, so
a URL in an `href` can never match a signal word. That is the same failure
wrong version W3 exists to catch, approached from the other side.

Greenhouse returns no description on `/v1/boards/<token>/jobs` unless asked
with a parameter JS2 did not send, so 157 of 452 postings have `body is None`.
That is not an empty body and must never be read as one: see `Posting.body`
and FILTER.md §3.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from inherited import providers

HERE = Path(__file__).resolve().parents[1]
DEFAULT_RAW = HERE.parent / "js2-loop-tools-diff" / "evidence" / "raw"

#: `<...>` including attributes, so href targets never survive into the body.
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\r\f\v]+")


def strip_html(fragment: str) -> str:
    """HTML to plain text: drop every tag with its attributes, keep the text."""
    if not fragment:
        return ""
    text = _TAG.sub(" ", fragment)
    for entity, char in (
        ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
        ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " "),
    ):
        text = text.replace(entity, char)
    return _WS.sub(" ", text).strip()


@dataclass(frozen=True)
class Posting:
    """One posting, with provenance for every part of it."""

    identity: str          # provider:id, namespaced as in JS2
    board: str             # e.g. "ashby:ramp"
    provider: str
    posting_id: str
    title: str
    location: str
    job_family: str | None
    url: str
    body: str | None       # None means the board sent no description at all
    body_fields: tuple[str, ...] = ()   # which native fields the body came from
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def has_body(self) -> bool:
        return bool(self.body and self.body.strip())

    def for_rule(self) -> dict:
        """The shape JS2's R-v3 expects, so the gates run unchanged."""
        return {
            "title": self.title,
            "location": {"name": self.location},
            "job_family": self.job_family,
            "provider_field": {
                "title": "title", "location": "location", "job_family": "job_family",
            },
        }


def _body_for(provider_name: str, record: dict) -> tuple[str | None, tuple[str, ...]]:
    if provider_name == "ashby":
        text = (record.get("descriptionPlain") or "").strip()
        return (text or None), (("descriptionPlain",) if text else ())

    if provider_name == "lever":
        parts, fields = [], []
        for key in ("descriptionPlain", "additionalPlain"):
            value = (record.get(key) or "").strip()
            if value:
                parts.append(value)
                fields.append(key)
        for i, item in enumerate(record.get("lists") or []):
            heading = (item.get("text") or "").strip()
            content = strip_html(item.get("content") or "")
            if heading or content:
                parts.append(f"{heading}\n{content}".strip())
                fields.append(f"lists[{i}]")
        text = "\n\n".join(parts).strip()
        return (text or None), tuple(fields)

    # greenhouse: this endpoint carries no description field at all.
    return None, ()


def load(raw_dir: Path | str | None = None) -> list[Posting]:
    """Every posting JS2 captured, parsed by JS2's own adapters."""
    raw_dir = Path(raw_dir) if raw_dir else DEFAULT_RAW
    if not raw_dir.is_dir():
        raise FileNotFoundError(
            f"{raw_dir} does not exist. JS3 reads the postings JS2 captured; "
            "run it from a clone that contains the js2-loop-tools-diff folder, "
            "or pass --raw-dir."
        )

    out: list[Posting] = []
    for path in sorted(raw_dir.glob("*.json")):
        stamp, board_key = path.name.split("-", 1)
        board_key = board_key[: -len(".json")]
        provider_name = board_key.split("-", 1)[0]
        payload = json.loads(path.read_text(encoding="utf-8"))
        parsed = providers.get(provider_name).parse(board_key, payload)
        for posting in parsed:
            body, fields = _body_for(provider_name, posting.raw)
            out.append(
                Posting(
                    identity=posting.identity,
                    board=board_key.replace("-", ":", 1),
                    provider=provider_name,
                    posting_id=posting.posting_id,
                    title=posting.title,
                    location=posting.location,
                    job_family=posting.job_family,
                    url=posting.url,
                    body=body,
                    body_fields=fields,
                    raw=posting.raw,
                )
            )
    return out


def inventory(postings: list[Posting]) -> dict:
    """Counts per board, and how many have a body. Used by the reports."""
    per_board: dict[str, dict] = {}
    for p in postings:
        row = per_board.setdefault(p.board, {"postings": 0, "with_body": 0})
        row["postings"] += 1
        row["with_body"] += int(p.has_body)
    return {
        "total": len(postings),
        "with_body": sum(1 for p in postings if p.has_body),
        "without_body": sum(1 for p in postings if not p.has_body),
        "boards": per_board,
    }
