"""Normalize saved board responses into one posting shape (FILTER.md v0.1 "Expected sources").

Each posting becomes {board, id, title, locations, text, date, url}:

| Field     | greenhouse/stripe                              | ashby/notion, ashby/linear                 |
|-----------|------------------------------------------------|--------------------------------------------|
| text      | `content`, HTML-unescaped then tag-stripped    | `descriptionPlain`, whitespace-normalized  |
| locations | [`location.name`]                              | [`location`] + `secondaryLocations[].location` |
| date      | `first_published`, else `updated_at`           | `publishedAt`                              |
| url       | `absolute_url`                                 | `jobUrl`                                   |

FILTER.md also lists Ashby's `isRemote` and `workplaceType` as location fields. They are not
copied here: under the G3 rule (a bare "Remote" is unknown, a region is unknown) they cannot
change a G3 result on their own, so the normalized shape stays exactly the seven keys above.

A missing or empty field becomes None (JSON null), never "". A board that failed in the run
contributes no postings; it is returned as a board failure, never as zero postings.
"""

import json
from pathlib import Path

from .text import normalize, strip_html

FIELDS = ("board", "id", "title", "locations", "text", "date", "url")


class RunError(Exception):
    """The run folder can't be read as a JS2/JS3 agent run."""


def _clean(value):
    """A non-empty stripped string, or None."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _locations(values) -> list[str] | None:
    cleaned = [c for c in (_clean(v) for v in values) if c is not None]
    return cleaned or None


def normalize_greenhouse(board: str, job: dict) -> dict:
    location = job.get("location")
    content = job.get("content")
    return {
        "board": board,
        "id": job["id"],
        "title": _clean(job.get("title")),
        "locations": _locations([location.get("name") if isinstance(location, dict) else None]),
        "text": _clean(strip_html(content)) if isinstance(content, str) else None,
        "date": _clean(job.get("first_published")) or _clean(job.get("updated_at")),
        "url": _clean(job.get("absolute_url")),
    }


def normalize_ashby(board: str, job: dict) -> dict:
    secondary = job.get("secondaryLocations")
    secondary = secondary if isinstance(secondary, list) else []
    plain = job.get("descriptionPlain")
    return {
        "board": board,
        "id": job["id"],
        "title": _clean(job.get("title")),
        "locations": _locations([job.get("location")]
                                + [s.get("location") if isinstance(s, dict) else None for s in secondary]),
        "text": _clean(normalize(plain)) if isinstance(plain, str) else None,
        "date": _clean(job.get("publishedAt")),
        "url": _clean(job.get("jobUrl")),
    }


NORMALIZERS = {"greenhouse": normalize_greenhouse, "ashby": normalize_ashby}


def normalize_response(provider: str, board: str, body: bytes) -> list[dict]:
    if provider not in NORMALIZERS:
        raise RunError(f"unknown provider {provider!r}")
    data = json.loads(body)
    return [NORMALIZERS[provider](board, job) for job in data["jobs"]]


def _raw_file(run_dir: Path, run_id: str, raw_path: str) -> Path:
    """Map a summary raw path ("runs/<run_id>/raw/...") into run_dir, refusing escapes."""
    prefix = f"runs/{run_id}/"
    if not raw_path.startswith(prefix):
        raise RunError(f"raw path {raw_path!r} is not inside runs/{run_id}/")
    path = (run_dir / raw_path[len(prefix):]).resolve()
    if not path.is_relative_to(run_dir.resolve()):
        raise RunError(f"raw path {raw_path!r} leaves the run folder")
    return path


def load_run(run_dir) -> tuple[list[dict], list[dict]]:
    """(postings, board_failures) from a run folder holding summary.json and raw/.

    Only succeeded boards are read, from their last saved attempt.
    """
    run_dir = Path(run_dir)
    try:
        summary = json.loads((run_dir / "summary.json").read_text())
    except (OSError, json.JSONDecodeError) as err:
        raise RunError(f"cannot read {run_dir / 'summary.json'}: {err}") from None
    postings, failures = [], []
    for entry in summary.get("boards", []):
        if entry.get("status") != "succeeded":
            failures.append({"board": entry.get("board"), "status": entry.get("status"),
                             "failure": entry.get("failure")})
            continue
        if not entry.get("raw_paths"):
            raise RunError(f"board {entry.get('board')} succeeded but has no raw path")
        raw = _raw_file(run_dir, summary["run_id"], entry["raw_paths"][-1])
        postings.extend(normalize_response(entry["provider"], entry["board"], raw.read_bytes()))
    return postings, failures
