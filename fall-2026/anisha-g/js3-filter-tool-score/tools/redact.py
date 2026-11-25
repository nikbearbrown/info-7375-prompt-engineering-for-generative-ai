"""Redact local machine paths from transcripts and logs before they are committed. Only paths are replaced; message
structure, ids, timestamps and every model/tool text stay as received. Counts go to transcripts/REDACTIONS.md.
Run:  python3 tools/redact.py"""
import re
from pathlib import Path
RULES = [(re.compile(r"/private/tmp/claude-\d+/-Users-[^/\"\\]+/[0-9a-f-]{36}/scratchpad"), "<SCRATCH>"),
         (re.compile(r"/tmp/claude-\d+/-Users-[^/\"\\]+/[0-9a-f-]{36}/scratchpad"), "<SCRATCH>"),
         (re.compile(r"/private/tmp/claude-\d+/-Users-[A-Za-z0-9._-]+/[0-9a-f-]*"), "<SCRATCH>"),
         (re.compile(r"-Users-[A-Za-z0-9._]+(?=[-/])"), "-Users-~"),
         (re.compile(r"/Users/[A-Za-z0-9._-]+"), "~")]
rows = []
for f in sorted(list(Path("transcripts").glob("*.jsonl")) + list(Path("transcripts").glob("*.txt")) + list(Path("logs").glob("2*.txt"))):
    s = f.read_text(); n = 0
    for rx, rep in RULES: s, k = rx.subn(rep, s); n += k
    if n: f.write_text(s)
    rows.append(f"| `{f}` | {n} |")
md = Path("transcripts/REDACTIONS.md")
md.write_text("# Redactions\nLocal paths only (home folder -> `~`, Claude Code scratch folder -> `<SCRATCH>`), by `tools/redact.py`. "
              "Nothing else in any transcript was edited.\n\n| File | Paths replaced (this pass) |\n|---|---|\n" + "\n".join(rows) + "\n")
print("\n".join(rows))
