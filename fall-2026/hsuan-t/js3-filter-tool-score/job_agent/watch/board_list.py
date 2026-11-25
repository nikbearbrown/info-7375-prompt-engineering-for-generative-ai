"""The board list: which boards a run watches, read from data/boards.json (JS2 R13, R14, R18; D2).

A data file instead of a constant in code, so adding or dropping a board is an edit Isaac can
review in one line, and the loop (Step 5) reads the same list the CLI does. Everything is checked
before any board is touched: a typo here is an input error (GATE code 001), not a failed board.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from ..common.errors import InputError, MissingInputError
from .boards import ADAPTERS

KEYS = {"name", "ats", "slug"}
OPTIONAL = {"note"}  # free text for humans (e.g. "misspelled on purpose"); the code never reads it

# name becomes a file name (state/<name>.state.json, evidence/raw/<run>/<name>_content.json), so
# only lower-case letters, digits and "-"; no "/" or "." means it can never point outside a folder.
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
# slug becomes part of the board URL path; same idea, but systems allow mixed case and "_".
SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


@dataclass(frozen=True)
class Board:
    name: str            # our name: state and raw files use it
    ats: str             # which adapter: a key of boards.ADAPTERS
    slug: str            # the board's name on that system, as it goes into the URL
    adapter: ModuleType


def load(path: Path) -> list[Board]:
    try:
        doc = json.loads(path.read_text())
    except FileNotFoundError:
        raise MissingInputError(f"board list not found: {path}") from None
    except json.JSONDecodeError as e:
        raise InputError(f"board list is not valid JSON: {path} ({e})") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("boards"), list) or not doc["boards"]:
        raise InputError(f"board list must be {{\"boards\": [...]}} with at least one board: {path}")
    boards = [_board(entry, i) for i, entry in enumerate(doc["boards"])]
    _no_duplicates(boards)
    return boards


def find(boards: list[Board], name: str) -> Board:
    for b in boards:
        if b.name == name:
            return b
    raise InputError(f"board {name!r} is not in the board list; known: {', '.join(b.name for b in boards)}")


def _board(entry, i: int) -> Board:
    if not isinstance(entry, dict) or not KEYS <= set(entry) or set(entry) - KEYS - OPTIONAL:
        raise InputError(f"boards[{i}] must have the keys {sorted(KEYS)} (optional: {sorted(OPTIONAL)})")
    name, ats, slug = entry["name"], entry["ats"], entry["slug"]
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise InputError(f"boards[{i}].name {name!r} must be lower-case letters, digits and '-'")
    if ats not in ADAPTERS:
        raise InputError(f"boards[{i}].ats {ats!r} is not supported; supported: {sorted(ADAPTERS)}")
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        raise InputError(f"boards[{i}].slug {slug!r} must be letters, digits, '_' and '-'")
    return Board(name, ats, slug, ADAPTERS[ats])


def _no_duplicates(boards: list[Board]) -> None:
    """Two entries with one name would share a state file; two with one (ats, slug) would fetch the
    same board twice, which GATE §3's repeat rule forbids."""
    names = [b.name for b in boards]
    targets = [(b.ats, b.slug) for b in boards]
    if len(set(names)) != len(names):
        raise InputError("board list has the same name twice")
    if len(set(targets)) != len(targets):
        raise InputError("board list has the same board (ats + slug) twice")
