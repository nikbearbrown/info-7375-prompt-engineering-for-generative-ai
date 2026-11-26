"""JS3: read a saved snapshot (FILTER.md section 3). Raw responses are stored gzipped; each is checked against the sha256 of the
original bytes recorded in manifest.json before it is used. Boards that were not observed or were empty yield no postings, and
their outcome is reported, never turned into "no relevant jobs".
"""
import gzip
import hashlib
import json
from pathlib import Path

from . import providers

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "snapshot" / "2026-11-25"


class IntegrityError(Exception):
    pass


def manifest(snap_dir=DEFAULT):
    return json.loads((Path(snap_dir) / "manifest.json").read_text())


def raw_bytes(snap_dir, row):
    data = gzip.decompress((Path(snap_dir) / row["file"]).read_bytes())
    if hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise IntegrityError(f"{row['file']}: sha256 does not match manifest.json")
    return data


def load(snap_dir=DEFAULT):
    """Returns (postings, outcomes). postings: every posting on an observed board. outcomes: {board: outcome} for all boards."""
    m = manifest(snap_dir)
    postings, outcomes = [], {}
    for row in m["boards"]:
        outcomes[row["board"]] = row["outcome"]
        if row["status"] == 200 and row["file"] and row["outcome"] == "observed":
            postings += providers.parse_list(row["provider"], raw_bytes(snap_dir, row), row["board"])
    return postings, outcomes
