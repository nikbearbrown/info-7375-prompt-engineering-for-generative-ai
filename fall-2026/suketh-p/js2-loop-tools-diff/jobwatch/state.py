"""The watch state (GATE.md 'Repeat rule' and 'Error policy').

Per board (ATS + slug): every posting key ever saved, with the run that first saw it.
The first usable snapshot of a board is its baseline; later, a key is new only if it
was never saved for that board. Only a finished run replaces the file, atomically and
through the permission policy, which requires the student's approval. A damaged file is
an error, never a silent fresh start."""

import copy
import json

from jobwatch.errors import StateError
from jobwatch.policy import STATE_FILE

SCHEMA = "jobwatch-state/2"
_TOP_FIELDS = {"schema", "boards", "runs"}
_BOARD_FIELDS = {"ats", "slug", "first_snapshot_run", "last_snapshot_run", "seen"}


def _problem(data):
    if not isinstance(data, dict) or set(data) != _TOP_FIELDS:
        return f"expected exactly the fields {sorted(_TOP_FIELDS)}"
    if data["schema"] != SCHEMA:
        return f"schema must be {SCHEMA!r}"
    if not isinstance(data["boards"], dict):
        return "boards must be an object"
    for name, entry in data["boards"].items():
        if not isinstance(entry, dict) or set(entry) != _BOARD_FIELDS:
            return f"boards[{name!r}] must have exactly the fields {sorted(_BOARD_FIELDS)}"
        texts = [entry[f] for f in ("ats", "slug", "first_snapshot_run", "last_snapshot_run")]
        if not all(isinstance(t, str) and t for t in texts):
            return f"boards[{name!r}] has an empty or non-text field"
        if name != f"{entry['ats']}/{entry['slug']}":
            return f"boards[{name!r}] does not match its ats and slug"
        seen = entry["seen"]
        if not isinstance(seen, dict) or not all(isinstance(k, str) and k and isinstance(v, str) and v
                                                 for k, v in seen.items()):
            return f"boards[{name!r}].seen must map posting keys to run ids"
    if not isinstance(data["runs"], list):
        return "runs must be a list"
    return None


def load_state(files):
    if not files.exists(STATE_FILE):
        return None
    try:
        data = json.loads(files.read_bytes(STATE_FILE).decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise StateError(f"{STATE_FILE} is damaged: {error}") from None
    problem = _problem(data)
    if problem:
        raise StateError(f"{STATE_FILE} is damaged: {problem}")
    return data


def new_keys(current, board_name, keys):
    """None if the board has no saved snapshot (this one is its baseline); otherwise the
    keys never saved for this board, in the order given."""
    if current is None or board_name not in current["boards"]:
        return None
    seen = current["boards"][board_name]["seen"]
    return [key for key in keys if key not in seen]


def advanced(current, run_id, finished_at, snapshots):
    """The state after a finished run. snapshots: {name: (ats, slug, keys)}. Keys that
    vanished stay saved; the input is not changed."""
    after = copy.deepcopy(current) if current is not None else {"schema": SCHEMA, "boards": {}, "runs": []}
    summary = {}
    for name, (ats, slug, keys) in snapshots.items():
        entry = after["boards"].get(name)
        baseline = entry is None
        if baseline:
            entry = {"ats": ats, "slug": slug, "first_snapshot_run": run_id, "last_snapshot_run": run_id, "seen": {}}
            after["boards"][name] = entry
        fresh = [key for key in keys if key not in entry["seen"]]
        for key in fresh:
            entry["seen"][key] = run_id
        entry["last_snapshot_run"] = run_id
        summary[name] = {"jobs": len(keys), "new": 0 if baseline else len(fresh), "baseline": baseline}
    after["runs"].append({"run_id": run_id, "finished_at": finished_at, "boards": summary})
    return after


def save_state(files, data):
    problem = _problem(data)
    if problem:
        raise StateError(f"refusing to save a damaged state: {problem}")
    files.write_atomic(STATE_FILE, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
