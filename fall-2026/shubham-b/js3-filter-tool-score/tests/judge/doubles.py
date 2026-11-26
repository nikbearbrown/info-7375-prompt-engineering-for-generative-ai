"""Test doubles for the judge and experiment tests.

* ``MemoryWriter``: the real ``fsio.OutputRoot`` that also records every JSON
  document it writes (``.json``), so tests can assert on what was written.
* ``valid_reply``: a reply object that passes the CONTRACT §8 validator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from job_search_agent.fsio import OutputRoot


class MemoryWriter(OutputRoot):
    """The real ``OutputRoot`` on ``root`` (created), recording what it writes.

    Attributes:
        json: Every JSON document written, by data-relative path.
        bytes: Every byte write, by data-relative path.
        made_dirs: Every empty directory made, in order.
    """

    def __init__(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        super().__init__(root)
        self.json: dict[str, Any] = {}
        self.bytes: dict[str, bytes] = {}
        self.made_dirs: list[str] = []

    def write_json_atomic(self, rel: str, obj: Any, *, sort_keys: bool = True) -> Path:
        self.json[rel] = json.loads(json.dumps(obj))
        return super().write_json_atomic(rel, obj, sort_keys=sort_keys)

    def write_bytes_atomic(self, rel: str, data: bytes) -> Path:
        self.bytes[rel] = data
        return super().write_bytes_atomic(rel, data)

    def make_empty_dir(self, rel: str) -> Path:
        self.made_dirs.append(rel)
        return super().make_empty_dir(rel)


def valid_reply(**overrides: Any) -> dict[str, Any]:
    reply: dict[str, Any] = {
        "label": "RELEVANT",
        "summary": "Title, skills and location line up.",
        "evidence": [
            {
                "resume_path": "$.skills.languages[2]",
                "posting_path": "$.content",
                "reason": "Java appears in the posting.",
            }
        ],
        "uncertainties": ["Sponsorship policy is not stated."],
    }
    reply.update(overrides)
    return reply
