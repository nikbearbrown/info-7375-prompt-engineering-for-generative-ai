"""State (CONTRACT.md, State): seen ids, the baseline run, and every run with its completion time."""
from __future__ import annotations

import json
import os
from pathlib import Path


def path_for(root: Path, mode: str) -> Path:
    return root / "state" / ("state.seeded.json" if mode == "seeded" else "state.json")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save(path: Path, state: dict) -> None:
    """Atomic: write a temp file next to it, then rename over it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def is_baseline(state) -> bool:
    """Missing file -> baseline. A file whose baseline never completed (crash) counts as missing, too."""
    return state is None or not state.get("baseline_run_id")
