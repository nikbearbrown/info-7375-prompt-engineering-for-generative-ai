#!/usr/bin/env python3
"""check_docs.py: the last check before submission. It looks for broken relative links and leftover placeholders
in the records.

Exit 1 on any problem. Written by Claude Code, 2026-11-22. Run: python3 tools/check_docs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "SCRIPT.md", "FACTCHECK.md", "SOURCES.md", "FRICTIONAL.md", "APPENDIX.md",
        "evidence/terminal/README.md", "evidence/prior-art/PRIOR-ART.md"]
PLACEHOLDERS = re.compile(r"(?i:\b(TBD|TODO|PENDING|after render|Not yet|not received yet|waiting for the student)\b)"
                          r"|\*\*DRAFT\b|PENDING-")
LINK = re.compile(r"\]\(([^)#\s]+)(#[^)]*)?\)")
problems = []
for rel in DOCS:
    p = ROOT / rel
    text = p.read_text()
    for n, line in enumerate(text.split("\n"), 1):
        for m in LINK.finditer(line):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (p.parent / target).exists():
                problems.append(f"{rel}:{n}: broken link -> {target}")
        if PLACEHOLDERS.search(line):
            problems.append(f"{rel}:{n}: placeholder? {line.strip()[:110]}")
for msg in problems:
    print(msg)
print(f"{len(problems)} problem(s) in {len(DOCS)} documents")
sys.exit(1 if problems else 0)
