#!/usr/bin/env bash
# Package the repo for submission. No network, no push.
#
#   tools/package.sh TARGET_DIR
#
# 1. Writes TARGET_DIR/GIT_HISTORY.txt: every commit, oldest first, with full hash, date,
#    author name (no email) and whether it has a Co-Authored-By trailer.
# 2. Writes TARGET_DIR/history.bundle (git bundle create --all), so every hash can be verified:
#    git clone history.bundle check && cd check && git log
# 3. Copies every tracked file (git ls-files) into TARGET_DIR.
# 4. Scans TARGET_DIR for email addresses (except @example.com), phone numbers (except 555
#    numbers) and the author's real name outside author/credit lines. Any hit fails the run
#    before the ZIP is built.
# 5. Builds Sathiyamurthy_Sreevarshan_INFO7375_JS1.zip next to TARGET_DIR (in its parent folder),
#    excluding .DS_Store and __pycache__.
#
# Refuses if TARGET_DIR exists and is not empty, or if tracked files have uncommitted changes
# (so the copied files match HEAD and the bundle). PACKAGE_ALLOW_DIRTY=1 skips that check, only
# for dry runs of an uncommitted version of this script; such a package does not match HEAD.
#
# Redaction: in the copy only, the home-folder path in experiments/sampling/spoiled/,
# experiments/heldout_app/spoiled/ and tests/test_persona.py is replaced with "~". Those files then differ from HEAD and the bundle;
# TARGET_DIR/REDACTED.txt lists them.

set -euo pipefail

ZIP_NAME="Sathiyamurthy_Sreevarshan_INFO7375_JS1.zip"

if [ $# -ne 1 ]; then
  echo "usage: tools/package.sh TARGET_DIR" >&2
  exit 2
fi

REPO="$(cd "$(dirname "$0")/.." && git rev-parse --show-toplevel)"
TARGET="$1"
cd "$REPO"

if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "refusing: $TARGET exists and is not empty" >&2
  exit 3
fi
if [ "${PACKAGE_ALLOW_DIRTY:-}" != "1" ] && ! git diff --quiet HEAD --; then
  echo "refusing: tracked files have uncommitted changes; commit or stash them first" >&2
  exit 4
fi

mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
PARENT="$(dirname "$TARGET")"
BASE="$(basename "$TARGET")"

# 1. Commit history, author names only.
{
  echo "# Git history of this repository, oldest first."
  echo "# full hash | date (author, ISO 8601) | author name | Co-Authored-By trailer | subject"
  git log --reverse --date=iso-strict \
    --format='%H%x1f%ad%x1f%an%x1f%(trailers:key=Co-Authored-By,valueonly,separator=;)%x1f%s' |
  while IFS=$'\x1f' read -r hash date name trailer subject; do
    if [ -n "$trailer" ]; then co="yes"; else co="no"; fi
    printf '%s | %s | %s | %s | %s\n' "$hash" "$date" "$name" "$co" "$subject"
  done
} > "$TARGET/GIT_HISTORY.txt"

# 2. Bundle of every ref.
git bundle create "$TARGET/history.bundle" --all

# 3. Tracked files.
git ls-files -z | tar --null -T - -cf - | tar -xf - -C "$TARGET"

# 3b. Redact the home-folder path in the copies of the spoiled sampling and held-out files (pasted shell text)
#     and of tests/test_persona.py (source-résumé path; that test skips when the path is missing).
python3 - "$TARGET" "$HOME" <<'PY'
import sys
from pathlib import Path

target, home = Path(sys.argv[1]), sys.argv[2]
changed = []
paths = (sorted((target / "experiments" / "sampling" / "spoiled").glob("*"))
         + sorted((target / "experiments" / "heldout_app" / "spoiled").glob("*"))
         + [target / "tests" / "test_persona.py"])
for path in paths:
    text = path.read_text(encoding="utf-8")
    if home in text:
        path.write_text(text.replace(home, "~"), encoding="utf-8")
        changed.append(str(path.relative_to(target)))
if changed:
    (target / "REDACTED.txt").write_text(
        "These files differ from the committed versions in history.bundle: the home-folder path\n"
        "was replaced with \"~\" when packaging. Nothing else was changed.\n\n"
        + "".join(f"{c}\n" for c in changed), encoding="utf-8")
    for c in changed:
        print(f"redacted home path: {c}")
PY

# 4. Scan.
python3 - "$TARGET" <<'PY'
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w.])(?:\+?1[\s.-]?)?\(?(\d{3})\)?[\s.-](\d{3})[\s.-](\d{4})(?![\w.])")
NAME = re.compile(r"sreevarshan|sathiyamurthy", re.I)
# Author/credit lines: markdown headings naming the author, the README sign-off signature line,
# and the author column of GIT_HISTORY.txt.
CREDIT_HEADING = re.compile(r"^#+ .*Sreevarshan Sathiyamurthy")
SIGNATURE = re.compile(r"^Signed: Sreevarshan Sathiyamurthy, \d{4}-\d{2}-\d{2}$")
# Deliberate refusal fixtures: values the tests feed in to prove they are refused. Exact values only.
FIXTURES = {
    ("tests/test_persona.py", "email", "someone@gmail.com"),
    ("tests/test_persona.py", "email", "someone@northeastern.edu"),
    ("tests/test_persona.py", "phone", "(617) 373-2000"),
    ("tests/test_persona.py", "phone", "617-373-2000"),
    ("tests/test_allowlist.py", "email", "boards-api.greenhouse.io@evil.example"),
}

hits, skipped = [], []
for path in sorted(p for p in target.rglob("*") if p.is_file()):
    rel = path.relative_to(target)
    if any(part in (".DS_Store", "__pycache__") for part in rel.parts):
        continue
    if str(rel) == "tools/package.sh":
        # The scanner itself: its patterns, fixture list and the ZIP name must contain these strings.
        skipped.append(f"{rel} (the scanner itself)")
        continue
    data = path.read_bytes()
    if b"\0" in data:
        skipped.append(f"{rel} (binary)")
        continue
    text = data.decode("utf-8", errors="replace")
    for n, line in enumerate(text.splitlines(), 1):
        for m in EMAIL.finditer(line):
            if not m.group(0).lower().endswith("@example.com"):
                hits.append((rel, n, "email", m.group(0)))
        for m in PHONE.finditer(line):
            if m.group(2) != "555":
                hits.append((rel, n, "phone", m.group(0)))
        if NAME.search(line):
            credit = (CREDIT_HEADING.search(line) or str(rel) == "GIT_HISTORY.txt"
                      or (str(rel) == "README.md" and SIGNATURE.match(line)))
            if not credit:
                m = NAME.search(line)
                hits.append((rel, n, "name", line[max(0, m.start() - 40):m.end() + 40].strip()))

for rel in skipped:
    print(f"scan: skipped {rel}")
allowed = [h for h in hits if (str(h[0]), h[2], h[3]) in FIXTURES]
hits = [h for h in hits if (str(h[0]), h[2], h[3]) not in FIXTURES]
for rel, n, kind, text in allowed:
    print(f"scan allowed (refusal fixture): {rel}:{n}: {kind}: {text}")
for rel, n, kind, text in hits:
    print(f"scan hit: {rel}:{n}: {kind}: {text}")
if hits:
    print(f"scan FAILED: {len(hits)} hit(s); no ZIP built", file=sys.stderr)
    sys.exit(1)
print("scan passed: no email, phone or real-name hits")
PY

# 5. ZIP.
rm -f "$PARENT/$ZIP_NAME"
(cd "$PARENT" && zip -q -r -X "$ZIP_NAME" "$BASE" -x '*.DS_Store' '*__pycache__*')
echo "files in $TARGET: $(find "$TARGET" -type f | wc -l | tr -d ' ')"
echo "zip: $PARENT/$ZIP_NAME ($(stat -f%z "$PARENT/$ZIP_NAME") bytes)"
