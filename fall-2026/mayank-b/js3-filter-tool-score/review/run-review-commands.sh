#!/usr/bin/env bash
# Run BY MAYANK in his own terminal (not by Claude). Works from any folder:
#   bash ~/Desktop/AgenticAI/Week_1/info-7375-repo/fall-2026/mayank-b/js3-filter-tool-score/review/run-review-commands.sh
# Writes review/run-by-mayank.txt (output verbatim, with real exit codes).
set -u
cd "$(cd "$(dirname "$0")" && pwd)/.." || exit 1
OUT="${OUT:-review/run-by-mayank.txt}"
{
  echo "# JS3 review commands run by Mayank Bhadrasen in his own terminal"
  echo "# date: $(date '+%Y-%m-%d %H:%M %Z')   commit: $(git rev-parse --short HEAD)   python: $(python3 -c 'import sys;print(sys.version.split()[0])')"
  run() { echo; echo "# expect: $1"; shift; echo "\$ $*"; bash -o pipefail -c "$*" 2>&1; echo "[exit $?]"; }
  run "Ran N tests ... OK" 'python3 -I -m unittest discover -s tests 2>&1 | grep -E "^(Ran|OK|FAILED)"'
  run "4/4 wrong versions caught (WF1-WF4)" 'python3 -I scripts/wrong_versions.py'
  run "the tool server's planted wrong version (WF6) is caught" 'python3 -I scripts/wrong_versions_mcp.py 2>&1 | tail -3'
  run "recomputed from the raw files: every saved v0.1 record is identical" 'python3 -I -c "
import json,sys; sys.path.insert(0,\"src\")
from jsa3 import corpus, filter as F
R=\"runs/2026-11-26T02-20-53Z-filter-v0.1\"; meta=json.load(open(R+\"/run.json\")); cfg=json.load(open(meta[\"config\"]))
c=corpus.load(meta[\"corpus\"]); saved=[json.loads(l) for l in open(R+\"/records.jsonl\")]
again=[F.evaluate(p,cfg) for p in c[\"postings\"]]
print(\"records\",len(saved),\"identical\",sum(a==b for a,b in zip(saved,again)))
print(\"raw SHA-256 checked for\",[b for b,i in c[\"boards\"].items() if \"sha256\" in i])"'
  run "the tool server imports no network module" 'grep -nE "^(import|from) " src/jsa3/mcp_server.py'
  run "nothing modified by these commands" 'git status --short -- src/ config/ FILTER.md'
} > "$OUT"
find . -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
echo "saved $OUT"; cat "$OUT"
