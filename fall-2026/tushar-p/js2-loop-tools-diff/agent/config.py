"""Board config: load through the FileGate and validate (F6, F7, F14).

Format: {"boards": [{"provider": "greenhouse", "token": "stripe"}, ...]}

Invalid config raises ConfigError, and the run exits error before any transport call:
- an unknown provider or a token that fails a full match of [a-z0-9-]+ (F7);
- zero boards (F14);
- more than MAX_DISTINCT_BOARDS distinct (provider, token) pairs (F6);
- any other key, so the config cannot try to raise a limit (GATE "Changing the limits").
Duplicate pairs are skipped, logged by the caller, and count once toward the limit.
"""

import json
from dataclasses import dataclass

from .errors import ConfigError, ReadDenied
from .limits import MAX_DISTINCT_BOARDS
from .providers import Board

TOP_LEVEL_KEYS = {"boards"}
ENTRY_KEYS = {"provider", "token"}


@dataclass(frozen=True)
class Duplicate:
    board: Board
    index: int        # position of the skipped entry in the config list
    first_index: int  # position of the entry that was kept


@dataclass(frozen=True)
class BoardConfig:
    boards: tuple[Board, ...]        # distinct boards, in config order
    duplicates: tuple[Duplicate, ...]


def parse_config(data: bytes, source: str = "config") -> BoardConfig:
    try:
        loaded = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise ConfigError(f"{source} is not valid JSON: {err}") from None
    if not isinstance(loaded, dict):
        raise ConfigError(f"{source} must hold a JSON object")
    extra = set(loaded) - TOP_LEVEL_KEYS
    if extra:
        raise ConfigError(f"{source} has unsupported key(s) {sorted(extra)}; only 'boards' is allowed")
    entries = loaded.get("boards")
    if not isinstance(entries, list):
        raise ConfigError(f"{source} must have a 'boards' list")

    boards, duplicates, first_seen = [], [], {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ConfigError(f"{source} board {index} must be an object with exactly 'provider' and 'token'")
        board = Board(entry["provider"], entry["token"])  # F7: raises ConfigError
        if board in first_seen:
            duplicates.append(Duplicate(board, index, first_seen[board]))
            continue
        first_seen[board] = index
        boards.append(board)

    if not boards:
        raise ConfigError(f"{source} lists no boards (F14)")
    if len(boards) > MAX_DISTINCT_BOARDS:
        raise ConfigError(
            f"{source} lists {len(boards)} distinct boards; the limit is {MAX_DISTINCT_BOARDS} (F6)"
        )
    return BoardConfig(tuple(boards), tuple(duplicates))


def load_config(gate, path) -> BoardConfig:
    """Read the selected config through the FileGate, then validate it."""
    try:
        data = gate.read(path)
    except ReadDenied as err:
        raise ConfigError(f"cannot read config: {err}") from None
    return parse_config(data, str(path))
