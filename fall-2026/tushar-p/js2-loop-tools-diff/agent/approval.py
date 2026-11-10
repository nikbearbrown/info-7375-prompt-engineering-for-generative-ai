"""In-code approval for the one protected write (GATE.md "Protected write", F16).

An Approval binds a destination, the SHA-256 of the exact bytes, and a run ID. JS2 has no CLI
approval option and normal runs never write the shortlist; the file gate checks approvals.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

PROTECTED_DIR = "protected"
SHORTLIST_NAME = "shortlist.json"

_SHA256_HEX = re.compile(r"[0-9a-f]{64}")


def protected_path(root) -> Path:
    """<root>/protected/shortlist.json."""
    return Path(root) / PROTECTED_DIR / SHORTLIST_NAME


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Approval:
    dest: str | Path
    sha256: str
    run_id: str

    def __post_init__(self):
        if not isinstance(self.sha256, str) or _SHA256_HEX.fullmatch(self.sha256) is None:
            raise ValueError("sha256 must be 64 lowercase hex characters")
        if not isinstance(self.run_id, str) or not self.run_id:
            raise ValueError("run_id must be a non-empty string")

    @classmethod
    def for_bytes(cls, dest, data: bytes, run_id: str) -> "Approval":
        return cls(dest=dest, sha256=sha256_hex(data), run_id=run_id)
