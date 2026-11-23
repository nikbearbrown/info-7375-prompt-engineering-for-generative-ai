#!/usr/bin/env bash
# Capture REAL-beat evidence from the APG repo (read-only) into progress-film/evidence/.
set -uo pipefail
APG="$HOME/Documents/agent-proving-ground"
OUT="$1"
mkdir -p "$OUT"
cd "$APG"
HEAD_SHA=$(git rev-parse --short HEAD)
cap(){ # cap <file> <description> <command...>
  local f="$OUT/$1"; local desc="$2"; shift 2
  {
    echo "# $desc"
    echo "# Captured: 2026-11-23 by Claude Code, read-only, in ~/Documents/agent-proving-ground (HEAD $HEAD_SHA, clean tree)"
    echo "# Command: $*"
    echo "# ----------------------------------------------------------------------------"
    bash -c "$*" 2>&1
    echo "# exit code: $?"
    echo
  } >> "$f"
}
rm -f "$OUT"/B*.txt
# B6
cap B6.txt "B6: the 'apg run 001' result line, as recorded in PLAN.md T1.4 (apg run is not re-run: read-only)" "grep -n 'printed \`001  PASS  steps=3' PLAN.md"
cap B6.txt "B6: apg show of the run 001 trace (schema v0, so apg show prints only its header)" "go run ./cmd/apg show evidence/traces/20261112T053055Z-92239eb0.json"
cap B6.txt "B6: the trace's own step list (3 steps), read from the JSON because apg show prints only v0 headers" "python3 -c \"import json;d=json.load(open('evidence/traces/20261112T053055Z-92239eb0.json'));print('steps', len(d['steps']), 'verdict', d['verdict'], 'exit_reason', d['exit_reason']);[print(s['n'], s.get('tool','(no tool: end_turn)'), s['stop_reason']) for s in d['steps']]\""
# B7
cap B7.txt "B7: contract B held-out evals, rows for 008-config-parser with denied calls (results/eval-log.jsonl)" "python3 -c \"import json
for l in open('results/eval-log.jsonl'):
  r=json.loads(l)
  if r['set']!='held-out' or not r['prompt_version'].startswith('3de39bebb4df'): continue
  for row in r['rows']:
    if row['task'].startswith('008'): print(r['eval_id'], 'contract B', row['task'], row['verdict'], 'denied', row['denied'], row['trace'])\""
cap B7.txt "B7: the denied call in run 20261118T034327Z-b54f5cd6 (contract B, held-out, 008), from apg show" "go run ./cmd/apg show traces/20261118T034327Z-b54f5cd6.json | sed -n '1,9p;112,119p'"
cap B7.txt "B7: apg show of the human-answered gate approval (schema v0, so apg show prints only its header)" "go run ./cmd/apg show evidence/traces/20261113T224740Z-a9a2c258.json"
cap B7.txt "B7: the trace's gate section, read from the JSON" "python3 -c \"import json;print(json.dumps(json.load(open('evidence/traces/20261113T224740Z-a9a2c258.json'))['gate'],indent=1))\""
cap B7.txt "B7: what the gate's recheck means (docs/trace-schema.md)" "grep -n 'recheck_sha256' docs/trace-schema.md"
cap B7.txt "B7: who answered it (docs/trace-schema.md v0 table)" "grep -n 'a9a2c258' docs/trace-schema.md"
# B8
cap B8.txt "B8: tasks/README.md task list" "grep -n -E '^## |^\| 0[0-9]{2}-|^\| 01[0-6]-' tasks/README.md"
cap B8.txt "B8: task directories" "ls -d tasks/0*/ | wc -l; ls tasks | grep -E '^0'"
cap B8.txt "B8: the commit that wrote the task suite (date shown in the B8 frame)" "git log -1 --format='%h %ad %s' --date=format:'%a %b %d %H:%M %Y %z' 753612d"
cap B8.txt "B8: the split commit" "git show --stat 26b5305"
# B9
cap B9.txt "B9: key lines of evidence/isolation/20261117-isolation-d29.txt" "grep -n -E '^# (Date|Commit|Command)|uid=|setuid\(0\)|cpu.max|cpus_used|memory.max|OOMKilled|forked|fork error|sandbox \(policy on\)|No space left|ephemeral-storage limit|Evicted|^--- PASS|^PASS|^ok' evidence/isolation/20261117-isolation-d29.txt"
cap B9.txt "B9: Docker, kind, a spend-limited key (docs/01-brief.md)" "grep -n -i 'spend limit' docs/01-brief.md"
# B10
cap B10.txt "B10: header of docs/t5-predictions.md" "sed -n '1p' docs/t5-predictions.md"
cap B10.txt "B10: the predictions commit" "git log -1 6d7bafe"
cap B10.txt "B10: first held-out eval timestamp (after the commit above: 2026-11-18T03:41Z = Nov 17 22:41 ET)" "grep -m1 -o '\"eval_id\":\"20261118T034100Z-57e06904\",\"timestamp\":\"[^\"]*\"' results/eval-log.jsonl"
cap B10.txt "B10: the two system prompts (contract A: original; contract B: Tushar's, D30)" "wc -c contracts/A-system.txt contracts/B-system.txt; grep -n '^| D30' PLAN.md | cut -c1-200"
# B11
cap B11.txt "B11: evidence/compare/20261118-t51-a-vs-b.txt (full file)" "cat evidence/compare/20261118-t51-a-vs-b.txt"
cap B11.txt "B11: cost ratio, all tasks (B / A), from the totals above" "python3 -c \"print(f'{0.06637/0.04711:.4f}  -> B costs {100*(0.06637/0.04711-1):.1f}% more')\""
# B12
cap B12.txt "B12: FAILURES.md entry F2" "awk '/^## F2/{p=1} /^## F3/{p=0} p' FAILURES.md"
cap B12.txt "B12: the review covered all 40 PASS diffs (docs/07-evidence.md)" "grep -n -E 'reviewed all 40|No final diff edits' docs/07-evidence.md"
# B13
cap B13.txt "B13: milestones M0-M5 and the target submit date (PLAN.md)" "grep -n -E '^\| M[0-5] \||Target submit' PLAN.md | cut -c1-160"
cap B13.txt "B13: the repo's remote" "git remote get-url origin"
cap B13.txt "B13: what comes next (docs/01-brief.md)" "grep -n -i -E 'controlled failure|stranger' docs/01-brief.md"
cd - >/dev/null
