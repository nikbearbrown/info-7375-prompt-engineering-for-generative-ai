"""The seen-id state: CONTRACT.md Out (State file), Refuses 6, Order steps 3 and 11."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

from jobwatch.errors import CORRUPT_STATE, Stop
from jobwatch.evidence import atomic_write, json_bytes

STATE_DIR = Path("state")
SCHEMA_VERSION = 1
_DIGITS = re.compile(r"[0-9]+")


def state_path(token):
    return STATE_DIR / f"{token}.json"


@dataclass
class State:
    exists: bool
    raw: bytes | None
    seen_ids: set


def load_state(token):
    """Missing means baseline; anything corrupt raises Stop(4) before any request or write."""
    path = state_path(token)
    if not path.exists() and not path.is_symlink():
        return State(False, None, set())
    try:
        raw = path.read_bytes()
    except OSError:
        raise Stop(CORRUPT_STATE, f"corrupt state file {path.as_posix()}: unreadable") from None
    return parse_state(raw, token, path.as_posix())


def parse_state(raw, token, where):
    """The checks of Refuses 6 on bytes already read; `where` names the file in the message."""

    def corrupt(why):
        raise Stop(CORRUPT_STATE, f"corrupt state file {where}: {why}")

    if not raw.strip():
        corrupt("empty")
    try:
        data = json.loads(raw)
    except ValueError:
        corrupt("invalid JSON")
    if not isinstance(data, dict):
        corrupt("not an object")
    version = data.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        corrupt("unknown schema_version")
    if data.get("board") != token:
        corrupt("board does not match")
    seen = data.get("seen_ids")
    if (
        not isinstance(seen, list)
        or not all(isinstance(s, str) and _DIGITS.fullmatch(s) for s in seen)
        or len(set(seen)) != len(seen)
    ):
        corrupt("seen_ids is not a list of unique digit strings")
    return State(True, raw, set(seen))


def write_state(token, seen_ids, updated_at, run_id):
    doc = {
        "schema_version": SCHEMA_VERSION,
        "board": token,
        "seen_ids": sorted(seen_ids, key=int),
        "updated_at": updated_at,
        "last_run_id": run_id,
    }
    atomic_write(state_path(token), json_bytes(doc))
