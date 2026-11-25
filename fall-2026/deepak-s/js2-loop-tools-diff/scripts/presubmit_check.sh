#!/usr/bin/env bash
# Pre-submit check for JS2, adapted from JS1's scripts/presubmit_check.sh (b91c877) by Claude Code
# (Claude Opus 5.5), 2026-11-10. Run from inside js2-loop-tools-diff/ in a git clone with history:
#   bash scripts/presubmit_check.sh [ZipName.zip]
# Exits non-zero if anything a TA would deduct for is found. Builds the zip from the committed
# tree (git archive) only when every check passes, so the zip matches the commit it prints.
set -uo pipefail

ZIP="${1:-Sudharsanan_Deepak_INFO7375_JS2.zip}"
PY="${PYTHON:-.venv/bin/python}"
[ -x "$PY" ] || PY="python3"
fail=0
bad()  { echo "FAIL  $*"; fail=1; }
good() { echo "ok    $*"; }
MARK='TODO''(Deepak)'   # the marker string, split so this file does not contain it

# Email check (used in check 11). Exact allow-list: 7 URL-userinfo strings (not emails) in these files, as flagged on 2026-11-10.
# Each entry is file:match; the same string in any other file, and every other match, is flagged.
# Each "@" is quoted apart ("...""@""...") so this script's own text never matches the email pattern.
EMAIL_ALLOW=(
  "GATE.md:boards-api.greenhouse.io""@""evil.com"                                               # W03 example
  "POLICY.md:boards-api.greenhouse.io""@""evil.com"                                             # B03 request
  "tests/js2/checks.py:boards-api.greenhouse.io""@""evil.com"                                   # check_B03
  "evidence/pytest/20261110T193805Z-full-v.txt:user""@""boards-api.greenhouse.io"               # JS1 URL-check case id
  "evidence/pytest/20261110T195646Z-full-v.txt:user""@""boards-api.greenhouse.io"               # JS1 URL-check case id
  "evidence/review/full-suite-after-A3-20261110T204658Z.txt:user""@""boards-api.greenhouse.io"  # JS1 URL-check case id
  "evidence/review/full-suite-after-patch-20261110T204159Z.txt:user""@""boards-api.greenhouse.io"  # JS1 URL-check case id
)
email_hits() {  # reads file paths on stdin; prints file:line:match for each match not allowed
  xargs grep -H -n -o -I -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' 2>/dev/null | grep -v -i '@example\.com' \
    | EMAIL_ALLOW_LIST="$(printf '%s\n' "${EMAIL_ALLOW[@]}")" awk -F: \
        'BEGIN { n = split(ENVIRON["EMAIL_ALLOW_LIST"], a, "\n"); for (i = 1; i <= n; i++) ok[a[i]] = 1 } !(($1 ":" $3) in ok)'
}
# Probe: bash scripts/presubmit_check.sh --email-probe FILE...  (runs only this check on FILE...)
[ "${1:-}" = "--email-probe" ] && { shift; printf '%s\n' "$@" | email_hits; exit 0; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "FAIL  not inside a git repo"; exit 1; }
PREFIX="$(git rev-parse --show-prefix)"; PREFIX="${PREFIX%/}"
[ -n "$PREFIX" ] || { echo "FAIL  run this from the assignment folder, not the repo root"; exit 1; }
FOLDER="$(basename "$PREFIX")"
TRACKED="$(git ls-files .)"
RAW_BODIES='^(evidence/manual-capture/[^/]+/[^/]+\.body|runs/[^/]+/raw/.*|evidence/manual/[^/]+\.raw)$'

# 1. Required files
for f in README.md GATE.md POLICY.md REVIEW.md SIGNOFF.md FRICTIONAL.md SOURCES.md requirements.txt \
         config/budgets.json config/boards.json config/boards-fwa.json \
         evidence/manual-capture/CAPTURE.md jobwatch/loop.py jobwatch/tools.py jobwatch/policy.py jobwatch/verify.py; do
  echo "$TRACKED" | grep -qx "$f" && good "tracked: $f" || bad "missing or untracked: $f"
done

# 2. GATE.md + POLICY.md (with predictions) committed before the first commit touching a .py file here
gate_commit=""
for c in $(git log --reverse --format=%H -- GATE.md POLICY.md); do
  g="$(git show "$c:./GATE.md" 2>/dev/null)"; p="$(git show "$c:./POLICY.md" 2>/dev/null)"
  if [ -n "$g" ] && [ -n "$p" ] && ! printf '%s\n%s' "$g" "$p" | grep -q -F "$MARK"; then gate_commit="$c"; break; fi
done
py_commit="$(git log --reverse --format=%H -- '*.py' | head -1)"
if [ -z "$gate_commit" ]; then bad "no commit has GATE.md and POLICY.md without $MARK markers"
elif [ -z "$py_commit" ]; then bad "no .py file committed in this folder"
elif [ "$gate_commit" = "$py_commit" ]; then bad "GATE.md/POLICY.md and the first .py were committed together"
elif git merge-base --is-ancestor "$gate_commit" "$py_commit"; then good "GATE.md + POLICY.md (${gate_commit:0:7}) committed before the first .py (${py_commit:0:7})"
else bad "the first .py commit does not descend from the GATE.md + POLICY.md commit"; fi

# 3. budgets.json decision_ref names an entry in GATE.md section 2 (GATE.md, "Who may change a budget")
ref="$("$PY" -c 'import json; print(json.load(open("config/budgets.json"))["decision_ref"].split(",")[-1].strip())' 2>/dev/null)"
[ -n "$ref" ] && grep -q -- "^- $ref, " GATE.md && good "budgets.json decision_ref $ref is in GATE.md" || bad "budgets.json decision_ref '$ref' not found in GATE.md Budget decisions"

# 4. At least 10 boundary tests exist and pass
nb="$(grep -c -E '^def test_B[0-9]{2}_' tests/js2/test_boundary.py 2>/dev/null || echo 0)"
if [ "$nb" -ge 10 ] && "$PY" -m pytest -q -p no:cacheprovider tests/js2/test_boundary.py >/tmp/js2_boundary.txt 2>&1; then
  good "$nb boundary tests defined; $(tail -1 /tmp/js2_boundary.txt)"
else bad "boundary tests: $nb defined, or they did not all pass (see /tmp/js2_boundary.txt)"; fi

# 5. A committed live run whose trace records a failed board
nfail=0
for t in $(echo "$TRACKED" | grep -E '^runs/[^/]+/trace\.jsonl$'); do
  if grep -q '"label": "live"' "$t" && grep -q '"outcome": "board FAILED"' "$t"; then nfail=$((nfail + 1)); fi
done
[ "$nfail" -ge 1 ] && good "$nfail live run trace(s) record a failed board" || bad "no committed live run trace records a failed board"

# 6. Finished-wrong-answer evidence
for f in evidence/finished-wrong-answer/README.md evidence/finished-wrong-answer/verify-20261110T200830Z.txt \
         evidence/finished-wrong-answer/deepak-curl-check.txt; do
  echo "$TRACKED" | grep -qx "$f" && good "tracked: $f" || bad "missing finished-wrong-answer evidence: $f"
done
grep -q '^SUSPECT' evidence/finished-wrong-answer/verify-20261110T200830Z.txt 2>/dev/null \
  && good "verify output records SUSPECT" || bad "verify output has no SUSPECT flag"

# 7. No Deepak markers or template markers in tracked docs (CLAUDE.md is excluded, as in JS1)
MD="$(echo "$TRACKED" | grep -E '\.md$' | grep -v -x 'CLAUDE.md')"
hits="$(echo "$MD" | xargs grep -n -E 'TODO\(Deepak\)|YYYY-MM-DD|YOU WRITE|YOU CHOOSE|## Entry template|<!--' 2>/dev/null)"
[ -z "$hits" ] && good "no $MARK or template markers in docs" || { bad "markers remain:"; echo "$hits" | head -40; }

# 8. No open work in code
CODE="$(echo "$TRACKED" | grep -E '\.(py|sh|toml|cfg)$' | grep -v -x 'scripts/presubmit_check.sh')"
hits="$(echo "$CODE" | xargs grep -n -E 'TODO|FIXME|TBD|XXX|NotImplementedError|^\s*pass\s*#' 2>/dev/null)"
[ -z "$hits" ] && good "no TODO/stub markers in code" || { bad "open work in code:"; echo "$hits" | head -40; }

# 9. FRICTIONAL.md has a dated entry; SIGNOFF.md is signed or withheld with a name and date
grep -q -E '^### 20[0-9]{2}-[0-9]{2}-[0-9]{2}' FRICTIONAL.md && good "FRICTIONAL.md has dated entries" || bad "FRICTIONAL.md has no dated entry"
grep -A2 -E '^## Signed or withheld' SIGNOFF.md | grep -q -E '[A-Za-z].*20[0-9]{2}' && good "SIGNOFF.md is signed or withheld with a date" || bad "SIGNOFF.md has no name and date under Signed or withheld"

# 10. Things that must never be committed
hits="$(echo "$TRACKED" | grep -E '(^|/)(\.env[^/]*|\.venv|venv|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|private|transcripts)(/|$)|\.key$|\.zip$|\.pyc$|\.egg-info(/|$)')"
[ -z "$hits" ] && good "no caches, credentials, private dirs or zips tracked" || { bad "should not be tracked:"; echo "$hits"; }
hits="$(echo "$TRACKED" | grep -v -E "$RAW_BODIES" | xargs grep -n -I -E 'sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' 2>/dev/null)"
[ -z "$hits" ] && good "no credential patterns outside raw response bodies" || { bad "possible credentials:"; echo "$hits" | head -20; }

# 11. Persona privacy: emails outside example.com, except in raw response bodies (employers' own addresses).
SCAN="$(echo "$TRACKED" | grep -v -E "$RAW_BODIES")"
hits="$(echo "$SCAN" | email_hits)"
[ -z "$hits" ] && good "every email outside raw response bodies is @example.com" || { bad "non-example.com emails (check each):"; echo "$hits" | head -20; }

# 12. Personal denylist: one term per line in ~/.js2_denylist (or ~/.js1_denylist). Do not list your name.
DENY="$HOME/.js2_denylist"; [ -f "$DENY" ] || DENY="$HOME/.js1_denylist"
if [ -f "$DENY" ]; then
  hits="$(echo "$TRACKED" | xargs grep -n -i -I -F -f "$DENY" 2>/dev/null)"
  [ -z "$hits" ] && good "no denylisted personal terms ($(basename "$DENY"))" || { bad "personal terms found:"; echo "$hits" | cut -c1-160 | head -20; }
else echo "warn  no ~/.js2_denylist or ~/.js1_denylist; personal-data check skipped"; fi

# 13. Full test suite passes offline
if "$PY" -m pytest -q -p no:cacheprovider >/tmp/js2_pytest.txt 2>&1; then good "pytest: $(tail -1 /tmp/js2_pytest.txt)"
else bad "pytest failed (see /tmp/js2_pytest.txt)"; tail -15 /tmp/js2_pytest.txt; fi

# 14. Clean tree, so the zip and the GitHub folder are the same commit
if [ -n "$(git status --porcelain -- .)" ]; then bad "uncommitted changes in this folder:"; git status --short -- .
else good "working tree clean"; fi

echo
if [ "$fail" -ne 0 ]; then echo "NOT READY: fix the FAIL lines above. No zip built."; exit 1; fi
HASH="$(git rev-parse HEAD)"
OUT="$(cd .. && pwd)/$ZIP"
git -C "$(git rev-parse --show-toplevel)" archive --format=zip --prefix="$FOLDER/" -o "$OUT" "HEAD:$PREFIX"
echo "zip has $(unzip -Z1 "$OUT" | grep -vc '/$') files; sha256 $(shasum -a 256 "$OUT" | cut -d' ' -f1)"
echo "READY"
echo "zip:    $OUT (built from the commit below)"
echo "commit: $HASH"
echo "Check this commit is pushed: git branch -r --contains $HASH"
