#!/usr/bin/env bash
# Builds the JS3 course folder and the Canvas zip from the committed HEAD (nothing uncommitted).
# It refuses while a student placeholder, the unsigned sign-off, an unadopted FILTER.md or missing
# audit verdicts remain. It does not commit, push or upload anything.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
course_repo="$repo/../info-7375-prompt-engineering-for-generative-ai"
folder="$course_repo/fall-2026/shubham-b/js3-filter-tool-score"
zip_path="$repo/../Bagwe_Shubham_INFO7375_JS3.zip"

cd "$repo"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "refusing: commit or discard local changes first" >&2; exit 1
fi
# FOR_SHUBHAM.md quotes the placeholder marker while describing it.
if grep -q "Signed or withheld: ____" README.md \
  || grep -q "Status: Claude's draft, not yet" FILTER.md \
  || [[ ! -f experiments/js3/audit/hand_verdicts.json ]] \
  || grep -q "PENDING" docs/js3/audit/AUDIT_REPORT.md \
  || grep -rq --exclude=FOR_SHUBHAM.md "\[Shubham" README.md FRICTIONAL.md SOURCES.md FILTER.md docs/js3; then
  echo "refusing: a [Shubham ...] placeholder, the unsigned sign-off, an unadopted FILTER.md or the audit verdicts remain" >&2
  exit 1
fi

commit="$(git rev-parse HEAD)"
rm -rf "$folder"
mkdir -p "$folder"
git archive HEAD | tar -x -C "$folder"
rm -f "$zip_path"
(cd "$folder/.." && zip -qr "$zip_path" "$(basename "$folder")")

echo "folder: $folder"
echo "zip:    $zip_path"
echo "commit: $commit"
echo "Next, by hand: cd \"$course_repo\" && git add fall-2026/shubham-b/js3-filter-tool-score && git commit && git push"
