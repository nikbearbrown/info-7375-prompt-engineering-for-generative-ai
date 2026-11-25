"""Path redaction for saved transcripts. The ONLY edit made to a transcript before committing it.

Absolute local paths are replaced by placeholders so no home-directory name is published.
Every other byte is kept. The rules are listed in each evaluation's README.

    python3 -m jobfilter.redact IN.jsonl OUT.jsonl
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent.parent
RULES = [
    # (pattern, placeholder), applied in order
    (re.compile(r"/private/tmp/claude-\d+/[^\"\\\s]*?/scratchpad/probe-[a-z-]+"), "<THROWAWAY_PROBE_DIR>"),
    (re.compile(r"/private/tmp/claude-\d+/[^\"\\\s]*?/scratchpad"), "<SCRATCH_DIR>"),
    (re.compile(re.escape(str(FOLDER))), "<JS3_FOLDER>"),
    (re.compile(r"/Users/[^/\"\\\s]+"), "~"),
]


def redact(text: str) -> str:
    for pattern, placeholder in RULES:
        text = pattern.sub(placeholder, text)
    return text


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: python3 -m jobfilter.redact IN.jsonl OUT.jsonl", file=sys.stderr)
        return 2
    src, dst = Path(argv[0]), Path(argv[1])
    raw = src.read_text(encoding="utf-8")
    out = redact(raw)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"{src.name}: {len(raw)} chars, sha256 {hashlib.sha256(raw.encode()).hexdigest()[:16]} (unredacted) "
          f"-> {dst} ({len(out)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
