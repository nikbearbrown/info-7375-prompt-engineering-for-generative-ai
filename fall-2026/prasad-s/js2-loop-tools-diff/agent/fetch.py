"""Raw evidence and seeded boards (CONTRACT.md §1 item 6, §2; v0.5 item 5; GATE.md §4).

The request itself is agent/tool_layer.py's fetch. This module saves what
came back, through the tool layer's write, and reads seed files through its
read. Neither ever overwrites a file.
"""

import hashlib
import json
from pathlib import Path

from .errors import Refusal, RunError

SIDECAR_SUFFIX = ".sidecar.json"


def utc_stamp(moment):
    """UTC time written like 2026-11-06T201500Z (v0.6 item 1)."""
    return moment.strftime("%Y-%m-%dT%H%M%SZ")


def save_evidence(tools, evidence_dir, board, attempt, fetched_at, url, result=None, error=None):
    """One attempt's evidence (v0.5 item 5; Prasad, CP5b: one file per attempt).

    A response with a status is saved byte-for-byte, with a sidecar note; a
    timeout or connection error has no body, so it gets the sidecar only.
    Returns the sidecar note.
    """
    name = f"{board.ats}_{board.name}_{utc_stamp(fetched_at)}_a{attempt}.json"
    note = {
        "board": board.key,
        "attempt": attempt,
        "url": url,
        "fetched_at": fetched_at.isoformat(timespec="seconds"),
    }
    if result is not None:
        tools.write(f"{evidence_dir}/{name}", result.body)
        note.update({
            "status": result.status,
            "content_type": result.content_type,
            "file": name,
            "bytes": len(result.body),
            "sha256": hashlib.sha256(result.body).hexdigest(),
        })
        if result.location:
            note["location"] = result.location
    else:
        note.update({"status": None, "error": str(error), "error_kind": getattr(error, "kind", None), "file": None})
    sidecar = f"{evidence_dir}/{name}{SIDECAR_SUFFIX}"
    tools.write(sidecar, json.dumps(note, indent=2) + "\n")
    note["sidecar"] = name + SIDECAR_SUFFIX
    return note


def load_seed(tools, seed_path, evidence_dir):
    """§1 item 6: a seeded board reads one saved board response from evidence/ only.

    Decision 2026-11-06: the seed path is relative to the project folder, like
    every other path the agent is given.
    """
    seed = tools.policy.resolve(seed_path)
    evidence = tools.policy.resolve(evidence_dir)
    if seed == evidence or not seed.is_relative_to(evidence):
        raise Refusal(f"seed file {str(seed_path)!r} is not inside {evidence_dir} (§1 item 6)")
    if seed.name.endswith(SIDECAR_SUFFIX):
        raise Refusal(f"{seed.name} is a sidecar note, not a saved board response")
    try:
        raw = tools.read(seed_path)
    except OSError as exc:
        raise RunError(f"cannot read seed file {seed_path}: {exc}") from exc
    source = {
        "file": Path(seed.relative_to(evidence)).as_posix(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return raw, source
