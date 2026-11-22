"""FILTER.md is the filter. This module reads its fenced ```filter block and nothing else."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import ROOT

FILTER_PATH = ROOT / "FILTER.md"
BLOCK = re.compile(r"^```filter\s*\n(.*?)^```", re.S | re.M)
REQUIRED = ("filter_version", "role_words_title", "exclude_title_words", "exclude_text_phrases", "skills",
            "skills_unshipped", "degree_terms", "seniority_title_words", "weights", "max_skill_hits",
            "threshold", "require_skill", "min_text_chars", "shortlist_size")


class FilterError(ValueError):
    """FILTER.md has no usable filter block."""


def parse(text: str) -> dict:
    blocks = BLOCK.findall(text)
    if len(blocks) != 1:
        raise FilterError(f"FILTER.md must contain exactly one ```filter block, found {len(blocks)}")
    try:
        flt = json.loads(blocks[0])
    except json.JSONDecodeError as e:
        raise FilterError(f"the ```filter block is not JSON: {e}") from e
    missing = [k for k in REQUIRED if k not in flt]
    if missing:
        raise FilterError(f"the ```filter block lacks {missing}")
    return flt


def load(path: Path = FILTER_PATH) -> dict:
    raw = Path(path).read_bytes()
    flt = parse(raw.decode("utf-8"))
    flt["filter_sha256"] = hashlib.sha256(raw).hexdigest()
    flt["filter_path"] = str(Path(path).name)
    return flt
