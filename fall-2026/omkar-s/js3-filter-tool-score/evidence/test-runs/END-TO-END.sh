#!/bin/bash
# End-to-end check of JS3 on a FRESH COPY of this folder (the real folder is never written).
#   bash evidence/test-runs/END-TO-END.sh [--no-live]
# Steps: tests, mutants, offline pipeline (+ compare with the saved outputs), MCP probe, live collection +
# pipeline on it, one live Claude-client session, and edge cases. The edge cases write FAKE hand verdicts
# into the temp copy only, to exercise the statistics path; they are deleted with the copy.
set -u
SRC="$(cd "$(dirname "$0")/../.." && pwd)"
LIVE=1; [ "${1:-}" = "--no-live" ] && LIVE=0
T=$(mktemp -d)
echo "=== END-TO-END $(date -u +%Y-%m-%dT%H:%M:%SZ) · python $(python3 --version 2>&1 | cut -d' ' -f2) · claude $(claude --version 2>/dev/null | cut -d' ' -f1) · live=$LIVE"
rsync -a --exclude '__pycache__' --exclude 'transcripts/test' --exclude '.DS_Store' "$SRC/" "$T/js3-copy/"
cd "$T/js3-copy" || exit 9
fail=0
step() { echo; echo "--- $1"; }
check() { if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fail=$((fail+1)); fi; }

step "1. tests"
python3 -W error::ResourceWarning -m unittest discover -s tests -t . > ../t.txt 2>&1; tail -3 ../t.txt
check "all tests pass" "grep -q '^OK' ../t.txt"

step "2. mutants"
python3 tests/run_mutants.py | tee ../m.txt
check "control passed and every mutant KILLED" "grep -q 'CONTROL (no change): passed' ../m.txt && ! grep -q -E 'SURVIVED|ERROR' ../m.txt"

step "3. offline pipeline reproduces the saved outputs"
python3 -m js3.run_filter
python3 -m js3.shortlist
python3 -m js3.audit report
python3 -m js3.experiments report
check "shortlist-v1.6.md identical to the saved one" "diff -q shortlist/shortlist-v1.6.md '$SRC/shortlist/shortlist-v1.6.md'"
check "filter-v1.6 summary identical" "diff -q runs/2026-11-17T06-16-31Z/filter-v1.6/summary.md '$SRC/runs/2026-11-17T06-16-31Z/filter-v1.6/summary.md'"
check "SCORE-RESULTS identical apart from the generation time (lock status compared too)" "diff <(sed -E 's/^Generated [0-9TZ:-]+/Generated/' experiments/SCORE-RESULTS.md) <(sed -E 's/^Generated [0-9TZ:-]+/Generated/' '$SRC/experiments/SCORE-RESULTS.md') >/dev/null"
check "AUDIT-RESULTS identical apart from the generation time" "diff <(sed -E 's/^Generated [0-9TZ:-]+/Generated/' audit/AUDIT-RESULTS.md) <(sed -E 's/^Generated [0-9TZ:-]+/Generated/' '$SRC/audit/AUDIT-RESULTS.md') >/dev/null"
check "v1.6 keeps 7" "grep -q 'keep 7 · reject 1135' runs/2026-11-17T06-16-31Z/filter-v1.6/summary.md"
check "coverage line says INCOMPLETE + I cannot tell for greenhouse:webflow" "grep -q 'I cannot tell whether Webflow (old Greenhouse board)' shortlist/shortlist-v1.6.md"

step "4. MCP server probe"
python3 -m js3.mcp_client probe-mine | tee ../p.txt
check "path traversal refused" "grep 'path traversal' ../p.txt | grep -q -- '-32602'"
check "unknown tool refused" "grep 'apply_to_job' ../p.txt | grep -q -- '-32602'"
check "pre-initialize refused" "grep 'BEFORE initialize' ../p.txt | grep -q -- '-32002'"
check "transcript has both directions" "f=\$(ls -t transcripts/client-mine-*.jsonl | head -1); grep -q 'client->server' \$f && grep -q 'server->client' \$f"
check "no server log outside transcripts/" "[ -z \"\$(find . -name 'server-*.jsonl' -not -path './transcripts/*')\" ]"

if [ $LIVE = 1 ]; then
  step "5. live collection on the copy, then the pipeline on the new corpus"
  python3 -m js3.collect; echo "collect exit $?"
  NEW=$(ls data/corpus | sort | tail -1 | sed 's/.jsonl.gz//')
  python3 -m js3.run_filter --run "$NEW"
  check "new corpus has postings from 7 sources and webflow empty" "python3 -c \"import json;s=json.load(open('data/runs/$NEW/sources.json'));st={x['source']:x['status'] for x in s['sources']};import sys;sys.exit(0 if list(st.values()).count('ok')==7 and st['greenhouse:webflow']=='empty' else 1)\""
  python3 -m js3.shortlist --run "$NEW" | tee ../s.txt
  echo "(the live board changes daily, so the new shortlist is reported, not compared)"

  step "6. one live Claude Code session as MCP client (final server code)"
  claude -p "Use the score_posting tool on posting_id 8334794 and report the verdict and shortlist status in one sentence. Do not add a recommendation." \
    --model claude-sonnet-5-5 --strict-mcp-config --mcp-config mcp/js3.mcp.json --allowedTools "mcp__js3-score__score_posting" \
    --tools "" --setting-sources "" --no-session-persistence --output-format stream-json --verbose < /dev/null > ../c.jsonl 2>/dev/null
  python3 -c "
import json
for l in open('../c.jsonl'):
    e=json.loads(l)
    if e.get('type')=='assistant':
        for c in e['message']['content']:
            if c.get('type')=='tool_use': print('tool_use', json.dumps(c['input']))
            if c.get('type')=='text': print('answer:', c['text'][:400])
"
  check "Claude called score_posting" "grep -q '\"name\":\"mcp__js3-score__score_posting\"' ../c.jsonl"
fi

step "7. edge cases (temp copy only)"
check "store refuses a write into config/" "python3 -c 'from js3 import store
try:
    store.check(\"config/x.json\"); raise SystemExit(1)
except store.WriteRefused: pass'"
# FAKE hand verdicts (temp copy only): keep every card the filter kept, reject the rest, so the stats path runs
python3 -c "
import json
k=json.load(open('audit/sample-key.json'))
ans=''.join(('k' if e['filter_verdict']=='keep' else 'r')+'\nfake verdict (END-TO-END, temp copy)\n' for e in k['key'])
open('../answers.txt','w').write(ans)"
python3 -m js3.audit label < ../answers.txt > /dev/null
python3 -m js3.audit report
check "report computes Part R with an interval once all 49 are labelled" "grep -q 'The filter was wrong on 0 of 30 random rejects' audit/AUDIT-RESULTS.md && grep -q '0.0% to 11.6%' audit/AUDIT-RESULTS.md"
check "draw refuses once verdicts exist" "! python3 -m js3.audit draw > /dev/null 2>&1"
python3 -m js3.experiments fit-threshold
check "fit-threshold writes a dev-only report" "grep -q 'reported, not adopted' experiments/FIT-THRESHOLD-dev.md"
# the lock: delete one cached Claude row, then a run must refuse (scorer/textutil changed after lock 1)
sed -i '' '$d' experiments/runs/C0.jsonl
python3 -m js3.experiments run > ../r.txt 2>&1
check "experiments run refuses a new call under a broken lock" "grep -q 'lock 1 broken' ../r.txt"
check "collect refuses to overwrite a run of the same name" "python3 -c '
import datetime as dt
from js3 import collect
from js3.js2 import transport
now=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc)
g=lambda u,t,m: transport.Response(200,b\"{\\\"jobs\\\": []}\")
collect.collect(\"config/sources.json\",\"config/budgets.json\",\"e2e\",get=g,now=now)
try:
    collect.collect(\"config/sources.json\",\"config/budgets.json\",\"e2e\",get=g,now=now); raise SystemExit(1)
except SystemExit as e:
    raise SystemExit(0 if \"already exists\" in str(e) else 1)'"
mkdir -p transcripts/sub && echo "{\"cwd\": \"$HOME/x\"}" > transcripts/sub/planted.jsonl
check "redact exits 0, walks subfolders, and leaves no home path" "python3 -m js3.redact && ! grep -rq \"$HOME\" transcripts/"

echo; echo "=== $fail FAILED checks"; rm -rf "$T"; exit $fail
