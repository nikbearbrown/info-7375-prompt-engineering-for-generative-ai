"""Run folders and the raw response as evidence (CONTRACT.md, Out; Refuses 6)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from .errors import Refused

PACKAGE = Path(__file__).resolve().parent


def code_fingerprint(package: Path = PACKAGE) -> str:
    """SHA-256 over the agent's own source files, so a report says exactly which code produced it."""
    digest = hashlib.sha256()
    for path in sorted(Path(package).glob("*.py")):
        digest.update(path.name.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def git_head(repo: Path = PACKAGE.parent):
    """The commit checked out, read from .git without running git; None in a copy without .git."""
    try:
        head = (Path(repo) / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref: "):
            return head
        ref = head[len("ref: "):]
        loose = Path(repo) / ".git" / ref
        if loose.exists():
            return loose.read_text(encoding="utf-8").strip()
        packed = Path(repo) / ".git" / "packed-refs"
        for line in packed.read_text(encoding="utf-8").splitlines() if packed.exists() else []:
            if line.endswith(" " + ref):
                return line.split()[0]
    except OSError:
        pass
    return None


def run_id_for(started: datetime) -> str:
    return started.strftime("%Y-%m-%dT%H%M%SZ")


def new_run_dir(runs_root: Path, run_id: str) -> Path:
    """Create runs/<run id>/. A folder that already exists is never reused: saved runs are not edited."""
    path = Path(runs_root) / run_id
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise Refused(f"refused: {path} already exists, and a saved run is never overwritten") from None
    return path


def save_response(run_dir: Path, response, source: str) -> str:
    """Write the body byte for byte, its SHA-256, and where it came from. Returns the hash."""
    digest = hashlib.sha256(response.body).hexdigest()
    (run_dir / "response.json").write_bytes(response.body)
    # The same line `shasum -a 256 -c response.sha256` checks, run inside the folder.
    (run_dir / "response.sha256").write_text(f"{digest}  response.json\n", encoding="utf-8")
    meta = {
        "url": response.url,
        "status": response.status,
        "received_at": response.received_at,
        "bytes": len(response.body),
        "sha256": digest,
        "headers": response.headers,
        "source": source,
    }
    (run_dir / "response.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return digest
