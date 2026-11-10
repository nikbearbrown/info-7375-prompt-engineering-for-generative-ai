"""Postings from a saved run, never fetched: Amendment A7 (sample and experiment take --run RUN_DIR)."""
import json
from dataclasses import dataclass
from pathlib import Path

from jobwatch.errors import REFUSED, Stop
from jobwatch.evidence import sha256_hex
from jobwatch.postings import parse_body


@dataclass
class SavedRun:
    run_dir: str
    run_id: str
    board: str
    raw_path: str
    raw_sha256: str
    postings: dict  # posting_id -> job, judgeable postings only, in response order


def load_saved_run(run_dir):
    """The run's manifest and raw response, with the raw bytes checked against the manifest's sha256."""
    run_dir = Path(run_dir)
    try:
        manifest = json.loads((run_dir / "manifest.json").read_bytes())
    except (OSError, ValueError):
        raise Stop(REFUSED, f"--run {run_dir.as_posix()}: no readable manifest.json") from None
    raw_path = manifest.get("raw_path")
    if not raw_path:
        raise Stop(REFUSED, f"--run {run_dir.as_posix()}: the run saved no raw response")
    if manifest.get("http_status") not in (200, None):
        raise Stop(REFUSED, f"--run {run_dir.as_posix()}: the board answered HTTP {manifest['http_status']}")
    try:
        body = Path(raw_path).read_bytes()
    except OSError:
        raise Stop(REFUSED, f"--run {run_dir.as_posix()}: cannot read {raw_path}") from None
    if sha256_hex(body) != manifest.get("sha256"):
        raise Stop(REFUSED, f"--run {run_dir.as_posix()}: {raw_path} does not match the manifest's sha256")
    return SavedRun(run_dir.as_posix(), manifest["run_id"], manifest["board"], raw_path, manifest["sha256"],
                    dict(parse_body(body).judgeable()))


def postings_for(saved, posting_ids):
    """The jobs for these ids, refusing any id the saved response does not hold."""
    missing = [p for p in posting_ids if p not in saved.postings]
    if missing:
        raise Stop(REFUSED, f"not a judgeable posting in {saved.raw_path}: {', '.join(missing)}")
    return {p: saved.postings[p] for p in posting_ids}
