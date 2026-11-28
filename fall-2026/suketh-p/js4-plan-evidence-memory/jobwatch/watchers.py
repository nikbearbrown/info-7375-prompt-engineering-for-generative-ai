"""Two watchers and one notes file (PLAN.md v0.2 steps 3-4; MEMORY-GATE.md triggers 4 and 5).

A watcher reads only its own board's verified capture. It notes that board's new postings with the
pinned JS1 rule (jobwatch/rule.py, copied unchanged from JS3 ae850602) and writes only its own file,
notes.<watcher>.json. The coordinator alone writes notes.json, Anthropic then Databricks, and only
after every contribution matches the verified capture and the run's starting revision and hash.

Posting text is copied into the notes as JSON strings and is never read as an instruction: nothing
in this module, the replay or the writer takes an action from a note. instruction_like() only flags
such text for the plan owner's review.

The two watchers are not two opinions. They run the same code and the same rule on different boards'
text, so they catch nothing the rule itself gets wrong. Claude Code wrote this on 2026-11-28 to pass
tests/test_watchers.py (0117cf0b)."""

import json
import re
from pathlib import Path

from jobwatch import rule
from jobwatch.errors import AgentError

WATCHERS = {"anthropic": "greenhouse/anthropic", "databricks": "greenhouse/databricks"}
ORDER = ("anthropic", "databricks")
MERGED = "notes.json"
RULE = "the JS1 relevance rule: jobwatch/rule.py, copied unchanged from JS3 ae850602"
_CONTRIBUTION_FIELDS = {"watcher", "board", "run_id", "base", "source", "baseline", "rule", "notes"}
_NOTE_FIELDS = {"posting_key", "title", "location", "verdict", "failed_conditions", "justification",
                "source_locator"}
# Claude Code's choice: a small detector for review, not a defence. Nothing acts on note text either way.
_INSTRUCTION_LIKE = re.compile(
    r"\b(ignore|disregard)\b.{0,40}\b(instructions?|prompts?)\b|\byou are now\b|\bsystem\s*:|\bsystem prompt\b"
    r"|\bapprove\b.{0,40}\b(write|run|approval)\b", re.IGNORECASE | re.DOTALL)


class HandoffError(AgentError):
    """A watcher contribution cannot be merged (MEMORY-GATE.md trigger 4): the coordinator stops."""


def _locator(board, key):
    return f"jobs[].{'jobUrl' if board.startswith('ashby/') else 'id'} = {key}"


def watch(watcher, *, run_id, base, capture, postings, new_keys, persona):
    """One watcher's contribution: notes on its board's new postings (none for a baseline)."""
    board = WATCHERS.get(watcher)
    if board is None or capture.board != board:
        raise HandoffError(f"watcher {watcher!r} watches the board {board}, not {capture.board}")
    by_key = {posting.key: posting for posting in postings}
    notes = []
    for key in new_keys or []:
        posting = by_key.get(key)
        if posting is None:
            raise HandoffError(f"{board}: new posting {key!r} is not in the verified capture")
        verdict = rule.rule_verdict(persona, posting)
        notes.append({"posting_key": key, "title": posting.title, "location": posting.location_name,
                      "verdict": verdict["verdict"], "failed_conditions": verdict["failed_conditions"],
                      "justification": verdict["justification"], "source_locator": _locator(board, key)})
    return {"watcher": watcher, "board": board, "run_id": run_id, "base": dict(base),
            "source": {"capture_run_id": capture.capture_run_id, "path": capture.source_path,
                       "sha256": capture.source_sha256, "captured_at": capture.captured_at},
            "baseline": new_keys is None, "rule": RULE, "notes": notes}


def _write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_contribution(folder, contribution):
    """A watcher writes only its own file."""
    path = Path(folder) / f"notes.{contribution['watcher']}.json"
    _write(path, contribution)
    return path


def _problem(name, data, run_id, base, verified):
    if not isinstance(data, dict) or set(data) != _CONTRIBUTION_FIELDS:
        return f"{name}: a contribution must have exactly the fields {sorted(_CONTRIBUTION_FIELDS)}"
    watcher, board = data["watcher"], data["board"]
    if watcher not in WATCHERS:
        return f"{name}: {watcher!r} is not one of this run's watchers {list(ORDER)}"
    if board != WATCHERS[watcher]:
        return f"{name}: the {watcher} watcher must contribute its own board {WATCHERS[watcher]}, not {board}"
    if data["run_id"] != run_id:
        return f"{name}: it was written for run {data['run_id']!r}, not {run_id!r}"
    if data["base"] != base:
        return f"{name}: its base {data['base']} is not this run's starting revision and hash {base}"
    capture = verified.get(board)
    if capture is None:
        return f"{name}: {board} has no verified capture in this run"
    source = data["source"] if isinstance(data["source"], dict) else {}
    if source.get("path") != capture["source_path"] or source.get("sha256") != capture["source_sha256"]:
        return f"{name}: its source path or sha256 does not match the verified capture of {board}"
    if not isinstance(data["notes"], list) or not isinstance(data["baseline"], bool):
        return f"{name}: notes must be a list and baseline true or false"
    if data["baseline"] and data["notes"]:
        return f"{name}: a baseline contribution has no new postings to note"
    keys, seen = set(capture["keys"]), set()
    for note in data["notes"]:
        if not isinstance(note, dict) or set(note) != _NOTE_FIELDS:
            return f"{name}: every note must have exactly the fields {sorted(_NOTE_FIELDS)}"
        key = note["posting_key"]
        if key not in keys:
            return f"{name}: the note for posting {key!r} is not in the verified capture of {board}"
        if key in seen:
            return f"{name}: posting {key!r} is noted twice"
        seen.add(key)
    return None


def merge(folder, *, run_id, base, verified):
    """The coordinator: check every notes.<watcher>.json and write notes.json, Anthropic then Databricks.
    verified maps each board to its verified keys, source path and sha256. Raises HandoffError, and
    writes nothing, when a contribution is missing, duplicated or does not match."""
    folder = Path(folder)
    claims = {}
    for path in sorted(folder.glob("notes.*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as error:
            raise HandoffError(f"{path.name} is not valid JSON: {error}") from None
        board = data.get("board") if isinstance(data, dict) else None
        claims.setdefault(board, []).append((path.name, data))
    for board, files in claims.items():
        if len(files) > 1:
            raise HandoffError(f"two contributions claim the board {board}: "
                               f"{' and '.join(name for name, _ in files)}")
    for files in claims.values():
        problem = _problem(*files[0], run_id, base, verified)
        if problem:
            raise HandoffError(problem)
    for watcher in ORDER:
        if WATCHERS[watcher] not in claims:
            raise HandoffError(f"the {watcher} watcher's contribution (notes.{watcher}.json) is missing")
    merged = {"run_id": run_id, "base": dict(base), "merged_by": "coordinator", "order": list(ORDER),
              "contributions": [claims[WATCHERS[watcher]][0][1] for watcher in ORDER]}
    _write(folder / MERGED, merged)
    return merged


def instruction_like(text):
    return bool(_INSTRUCTION_LIKE.search(text))


def instruction_like_keys(merged):
    """(board, posting key) for every note whose text reads like an instruction, each once."""
    found = []
    for contribution in merged["contributions"]:
        for note in contribution["notes"]:
            text = " ".join(str(note[field]) for field in ("title", "location", "justification"))
            if instruction_like(text) and (contribution["board"], note["posting_key"]) not in found:
                found.append((contribution["board"], note["posting_key"]))
    return found
