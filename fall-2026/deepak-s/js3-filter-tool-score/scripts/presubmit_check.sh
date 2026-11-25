#!/usr/bin/env bash
# Pre-submit check for JS3, written by Claude Code (claude-opus-5-5), 2026-11-25, replacing the JS2
# script imported from b2ac533 (its checks named JS2 files). Run from inside js3-filter-tool-score/
# in a git clone with history:
#   bash scripts/presubmit_check.sh
# Exits non-zero if any check fails. Reads committed content (git show HEAD:...) where it matters.
set -uo pipefail

PY="${PYTHON:-.venv/bin/python}"
[ -x "$PY" ] || PY="python3"
fail=0
bad()  { echo "FAIL  $*"; fail=1; }
good() { echo "ok    $*"; }
MARK='TODO''(Deepak)'   # built in two parts so this file does not contain the marker
FINAL_AUDIT='audit/snapshots/audit-v1''@''65c9863.csv'   # final audit verdicts; "@" split so check 8 does not match this file

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "FAIL  not inside a git repo"; exit 1; }
PREFIX="$(git rev-parse --show-prefix)"; PREFIX="${PREFIX%/}"
[ -n "$PREFIX" ] || { echo "FAIL  run this from the assignment folder, not the repo root"; exit 1; }
TRACKED="$(git ls-files .)"
# Raw or near-raw posting text and fetched pages: employers' own text, scanned for credentials only.
RAW='^(runs/[^/]+/raw/.*|evidence/manual-capture/[^/]+/[^/]+\.body|evidence/manual/[^/]+\.raw|evidence/mcp/spec-fetch/[^/]+/[^/]+\.body|data/postings-[^/]+\.jsonl|data/texts/.*|shortlist/judge/.*|experiments/E3/.*)$'

# 1. Required files
for f in README.md FILTER.md AUDIT.md SHORTLIST.md MCP_EVAL.md SCORE.md SOURCES.md SIGNOFF.md FRICTIONAL.md \
         requirements.txt config/boards.json config/budgets.json audit/audit-v1.csv "$FINAL_AUDIT" shortlist/claims.csv \
         labels/heldout.csv jobwatch/filter.py jobwatch/mcp_server.py scripts/mcp_client.py; do
  echo "$TRACKED" | grep -qx "$f" && good "tracked: $f" || bad "missing or untracked: $f"
done

# 2. The FILTER.md commit with no Deepak markers precedes the first commit of a .py file in this folder
filter_commit=""
for c in $(git log --reverse --format=%H -- FILTER.md); do
  t="$(git show "$c:./FILTER.md" 2>/dev/null)"
  if [ -n "$t" ] && ! printf '%s' "$t" | grep -q -F "$MARK"; then filter_commit="$c"; break; fi
done
py_commit="$(git log --reverse --format=%H -- '*.py' | head -1)"
if [ -z "$filter_commit" ] || [ -z "$py_commit" ]; then bad "no marker-free FILTER.md commit, or no .py commit"
elif [ "$filter_commit" != "$py_commit" ] && git merge-base --is-ancestor "$filter_commit" "$py_commit"; then
  good "FILTER.md (${filter_commit:0:7}) committed before the first .py (${py_commit:0:7})"
else bad "the first .py commit does not come after the marker-free FILTER.md commit"; fi

# 3. The sealed held-out draw precedes the first commit of the filter code
draw="$(git log --reverse --format=%H -- labels/heldout.csv | head -1)"
fcode="$(git log --reverse --format=%H -- jobwatch/filter.py | head -1)"
if [ -n "$draw" ] && [ -n "$fcode" ] && [ "$draw" != "$fcode" ] && git merge-base --is-ancestor "$draw" "$fcode"; then
  good "held-out draw (${draw:0:7}) committed before the first filter code (${fcode:0:7})"
else bad "held-out draw does not precede the first commit of jobwatch/filter.py"; fi

# 4. At least 30 random rejects with a verdict, in the final audit verdicts: the committed snapshot of the
#    third pass (65c9863). audit/audit-v1.csv at HEAD holds an unused fourth pass (f0568bc, 4 of 45).
n="$(git show "HEAD:./$FINAL_AUDIT" 2>/dev/null | "$PY" -c '
import csv, sys
rows = csv.DictReader(l for l in sys.stdin if not l.startswith("# "))
print(sum(1 for r in rows if r["group"] == "random_reject" and r["verdict"].strip() in ("relevant", "not_relevant")))')"
[ "${n:-0}" -ge 30 ] && good "$n random rejects have a verdict ($FINAL_AUDIT)" || bad "only ${n:-0} random rejects have a verdict in $FINAL_AUDIT"

# 5. Every claim labeled, in the committed claims sheet
read -r total done_ <<<"$(git show HEAD:./shortlist/claims.csv 2>/dev/null | "$PY" -c '
import csv, sys
rows = list(csv.DictReader(l for l in sys.stdin if not l.startswith("# ")))
print(len(rows), sum(1 for r in rows if r["label"].strip() in ("supported", "contradicted", "insufficient")))')"
[ "${total:-0}" -gt 0 ] && [ "${total}" = "${done_}" ] && good "all $total claims labeled" || bad "${done_:-0} of ${total:-0} claims labeled"

# 6. Transcripts for both servers
a="$(echo "$TRACKED" | grep -c -E '^evidence/mcp/transcripts/[^/]+\.jsonl$')"
b="$(echo "$TRACKED" | grep -c -E '^evidence/mcp/other-server/[^/]+-transcript\.jsonl$')"
[ "$a" -ge 1 ] && [ "$b" -ge 1 ] && good "transcripts: our server $a, other server $b" || bad "transcripts missing (our server $a, other server $b)"

# 7. No Deepak markers in delivered files (CLAUDE.md states the rule, so it is excluded)
hits="$(echo "$TRACKED" | grep -v -x 'CLAUDE.md' | grep -v -E "$RAW" | xargs grep -n -I -F "$MARK" 2>/dev/null)"
[ -z "$hits" ] && good "no $MARK markers" || { bad "$MARK markers remain ($(echo "$hits" | wc -l | tr -d ' ')):"; echo "$hits" | cut -c1-140 | head -60; }

# 8. Exact allow-list email check over non-raw files (each entry file:match; "@" split so this file never matches)
ALLOW=(
  "tests/js2/checks.py:boards-api.greenhouse.io""@""evil.com"   # JS2 check_B03, a URL with userinfo
  "FILTER.md:audit-v1""@""65c9863.csv"                          # a snapshot file name, not an email
  "AUDIT.md:audit-v1""@""65c9863.csv"
  "README.md:audit-v1""@""65c9863.csv"
  "SCORE.md:audit-v1""@""65c9863.csv"
)
hits="$(echo "$TRACKED" | grep -v -E "$RAW" | xargs grep -H -n -o -I -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' 2>/dev/null \
  | grep -v -i '@example\.com' | ALLOW_LIST="$(printf '%s\n' "${ALLOW[@]}")" awk -F: \
    'BEGIN { n = split(ENVIRON["ALLOW_LIST"], a, "\n"); for (i = 1; i <= n; i++) ok[a[i]] = 1 } !(($1 ":" $3) in ok)')"
[ -z "$hits" ] && good "every email-like string outside raw files is @example.com or allow-listed" || { bad "emails to check:"; echo "$hits" | head -20; }

# 9. No caches or credentials tracked
hits="$(echo "$TRACKED" | grep -E '(^|/)(\.env[^/]*|\.venv|venv|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|private|node_modules)(/|$)|\.key$|\.zip$|\.pyc$|\.egg-info(/|$)')"
[ -z "$hits" ] && good "no caches, credentials, private files or zips tracked" || { bad "should not be tracked:"; echo "$hits"; }
hits="$(echo "$TRACKED" | xargs grep -n -I -E 'sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' 2>/dev/null)"
[ -z "$hits" ] && good "no credential patterns" || { bad "possible credentials:"; echo "$hits" | head -20; }

# 10. Tree clean
st="$(git status --porcelain -- .)"
[ -z "$st" ] && good "working tree clean" || { bad "uncommitted changes:"; echo "$st" | head -20; }

# 11. Full test suite
if "$PY" -m pytest -q -p no:cacheprovider >/tmp/js3_presubmit_pytest.txt 2>&1; then good "pytest: $(tail -1 /tmp/js3_presubmit_pytest.txt)"
else bad "pytest failed: $(tail -1 /tmp/js3_presubmit_pytest.txt)"; fi

[ "$fail" -eq 0 ] && echo "PRESUBMIT: PASS" || echo "PRESUBMIT: FAIL"
exit "$fail"
