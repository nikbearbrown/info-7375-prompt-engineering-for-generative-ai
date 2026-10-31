#!/usr/bin/env bash
# Pre-submit check for JS1. Run from inside js1-contract-and-watch/ in your git clone:
#   bash scripts/presubmit_check.sh [ZipName.zip]
# Exits non-zero if anything a TA would deduct for is found. Builds the zip from the
# committed tree (git archive), so the zip matches the commit hash it prints.
set -uo pipefail

ZIP="${1:-Sudharsanan_Deepak_INFO7375_JS1.zip}"
fail=0
bad()  { echo "FAIL  $*"; fail=1; }
good() { echo "ok    $*"; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "FAIL  not inside a git repo"; exit 1; }
PREFIX="$(git rev-parse --show-prefix)"; PREFIX="${PREFIX%/}"
[ -n "$PREFIX" ] || { echo "FAIL  run this from the assignment folder, not the repo root"; exit 1; }
FOLDER="$(basename "$PREFIX")"
TRACKED="$(git ls-files .)"

# 1. Required files
for f in README.md CONTRACT.md SOURCES.md FRICTIONAL.md requirements.txt \
         reports/SAMPLING_REPORT.md reports/PROMPT_EXPERIMENT.md reports/ACTION_SURFACE.md \
         labels/LABELING_RULE.md labels/labels.csv examples/persona_resume.json; do
  echo "$TRACKED" | grep -qx "$f" && good "tracked: $f" || bad "missing or untracked: $f"
done

# 2. Unfilled template markers in docs (CLAUDE.md is excluded: it mentions TODO on purpose)
MD="$(echo "$TRACKED" | grep -E '\.md$' | grep -v -x 'CLAUDE.md')"
if [ -n "$MD" ]; then
  hits="$(echo "$MD" | xargs grep -n -E 'YYYY-MM-DD|___|YOU WRITE|YOU CHOOSE|Provenance note|<!--' 2>/dev/null)"
  [ -z "$hits" ] && good "no unfilled template markers in docs" || { bad "unfilled template markers:"; echo "$hits" | head -40; }
fi

# 3. Open work in code
CODE="$(echo "$TRACKED" | grep -E '\.(py|sh|toml|cfg)$' | grep -v -x 'scripts/presubmit_check.sh')"
if [ -n "$CODE" ]; then
  hits="$(echo "$CODE" | xargs grep -n -E 'TODO|FIXME|TBD|XXX|NotImplementedError|^\s*pass\s*#' 2>/dev/null)"
  [ -z "$hits" ] && good "no TODO/stub markers in code" || { bad "open work in code:"; echo "$hits" | head -40; }
fi

# 4. Things that must never be committed
hits="$(echo "$TRACKED" | grep -E '(^|/)(\.env|\.venv|__pycache__|\.pytest_cache|private|transcripts)(/|$)|\.key$|\.zip$|\.pyc$')"
[ -z "$hits" ] && good "no caches, credentials, private dirs or zips tracked" || { bad "should not be tracked:"; echo "$hits"; }

# 5. Persona privacy: emails outside example.com in résumé/test/doc files
#    (evidence/raw is skipped: real postings contain employers' own contact emails)
SCAN="$(echo "$TRACKED" | grep -v '^evidence/raw/')"
if [ -n "$SCAN" ]; then
  hits="$(echo "$SCAN" | xargs grep -n -o -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' 2>/dev/null | grep -v -i '@example\.com')"
  [ -z "$hits" ] && good "every email outside evidence/raw is @example.com" || { bad "non-example.com emails (check each):"; echo "$hits" | head -20; }
fi

# 6. Your own denylist: real email, phone, street, etc. One term per line in ~/.js1_denylist.
#    Do NOT list your name: it belongs in the sign-off.
if [ -f "$HOME/.js1_denylist" ]; then
  hits="$(echo "$TRACKED" | xargs grep -n -i -F -f "$HOME/.js1_denylist" 2>/dev/null)"
  [ -z "$hits" ] && good "no denylisted personal terms" || { bad "personal terms found:"; echo "$hits" | head -20; }
else
  echo "warn  ~/.js1_denylist not found; personal-data check skipped"
fi

# 7. Contract written before code (git history order)
c_commit="$(git log --reverse --diff-filter=A --format=%H -- CONTRACT.md | head -1)"
py_commit="$(git log --reverse --diff-filter=A --format=%H -- 'jobwatch/*.py' 'jobwatch/**/*.py' | head -1)"
if [ -z "$c_commit" ]; then bad "CONTRACT.md has never been committed"
elif [ -z "$py_commit" ]; then echo "warn  no jobwatch/*.py committed yet"
elif [ "$c_commit" = "$py_commit" ]; then bad "CONTRACT.md and the first code were added in the same commit"
elif git merge-base --is-ancestor "$c_commit" "$py_commit"; then good "CONTRACT.md (${c_commit:0:7}) committed before first code (${py_commit:0:7})"
else bad "first code commit does not descend from the CONTRACT.md commit"; fi

# 8. Evidence from two runs
nraw="$(echo "$TRACKED" | grep -c '^evidence/raw/' || true)"
nstate="$(echo "$TRACKED" | grep -c '^state/' || true)"
[ "$nraw" -ge 2 ] && good "$nraw raw evidence files tracked" || bad "need >= 2 raw responses in evidence/raw (found $nraw)"
[ "$nstate" -ge 1 ] && good "state file tracked" || bad "no state file tracked under state/"

# 9. Tests pass offline
if command -v python >/dev/null 2>&1; then
  if python -m pytest -q >/tmp/js1_pytest.txt 2>&1; then good "pytest: $(tail -1 /tmp/js1_pytest.txt)"
  else bad "pytest failed (see /tmp/js1_pytest.txt)"; tail -15 /tmp/js1_pytest.txt; fi
else echo "warn  python not on PATH; tests not run"; fi

# 10. Clean tree, so the zip and the GitHub folder are the same commit
if [ -n "$(git status --porcelain -- .)" ]; then bad "uncommitted changes in this folder:"; git status --short -- .
else good "working tree clean"; fi

echo
if [ "$fail" -ne 0 ]; then echo "NOT READY: fix the FAIL lines above. No zip built."; exit 1; fi
HASH="$(git rev-parse HEAD)"
OUT="$(cd .. && pwd)/$ZIP"
git -C "$(git rev-parse --show-toplevel)" archive --format=zip --prefix="$FOLDER/" -o "$OUT" "HEAD:$PREFIX"
unzip -l "$OUT" >/dev/null 2>&1 && echo "zip has $(unzip -Z1 "$OUT" | grep -vc '/$') files" || true
echo "READY"
echo "zip:    $(cd .. && pwd)/$ZIP (built from the commit below)"
echo "commit: $HASH"
echo "Check this commit is pushed: git branch -r --contains $HASH"
