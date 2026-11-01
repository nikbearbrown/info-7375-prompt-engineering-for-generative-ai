#!/bin/sh
# Chapter 3: the same task (judge one posting for Priya) on three action surfaces.
# Each surface runs in its own empty temp dir; everything it produced is copied to results/action-surfaces/.
# Usage: CLAUDE_BIN=/path/to/claude sh scripts/action_surfaces.sh
set -e
BIN="${CLAUDE_BIN:-claude}"
MODEL="${CLAUDE_MODEL:-claude-sonnet-5-5}"
OUT="$(pwd)/results/action-surfaces"
mkdir -p "$OUT"
ID=5432575008   # "Applied AI Engineer, Startups" (dev set)
python3 -c "
import sys,json; sys.path.insert(0,'.')
from agent.claude_judge import posting_view, resume_view
from agent.resume import load_resume
j={x['id']:x for x in json.load(open('evidence/raw/anthropic-20261101T185817Z.json'))['jobs']}[$ID]
json.dump(posting_view(j), open('$OUT/posting.json','w'), indent=2, ensure_ascii=False)
json.dump(resume_view(load_resume('personas/priya-nair.resume.json')), open('$OUT/resume_view.json','w'), indent=2, ensure_ascii=False)"
ASK='Is this posting relevant for this candidate? Answer relevant or not_relevant, then one sentence naming the resume fields and posting fields you used.'

# 1. Paste into a chat: text in, text out, no tools.
D=$(mktemp -d); cd "$D"
"$BIN" -p "$ASK

Candidate: $(cat "$OUT/resume_view.json")

Posting: $(cat "$OUT/posting.json")" --model "$MODEL" --disallowedTools "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,NotebookEdit,Task,TodoWrite" --output-format json < /dev/null > "$OUT/1-paste.json"
cd - >/dev/null

# 2. Give Claude a file to read: Read tool only, scoped to its own temp dir.
D=$(mktemp -d); cp "$OUT/posting.json" "$OUT/resume_view.json" "$D/"; cd "$D"
"$BIN" -p "Read posting.json and resume_view.json in this folder. $ASK" --model "$MODEL" \
  --allowedTools "Read" --disallowedTools "Bash,Edit,Write,Glob,Grep,WebFetch,WebSearch,NotebookEdit,Task,TodoWrite" --output-format json < /dev/null > "$OUT/2-file.json"
ls -la "$D" > "$OUT/2-file.dir-after.txt"; cd - >/dev/null

# 3. Let an agent fetch and write its own state file: WebFetch (one host) + Write, nothing else.
D=$(mktemp -d); cp "$OUT/resume_view.json" "$D/"; cd "$D"
"$BIN" -p "Fetch https://boards-api.greenhouse.io/v1/boards/anthropic/jobs . Write state.json containing the list of all posting ids you saw. Then, for posting id $ID only, using resume_view.json in this folder: $ASK" \
  --model "$MODEL" --disallowedTools "Bash,Edit,Glob,Grep,WebSearch,NotebookEdit,Task,TodoWrite" \
  --allowedTools "WebFetch(domain:boards-api.greenhouse.io) Write Read" --output-format json < /dev/null > "$OUT/3-agent.json"
ls -la "$D" > "$OUT/3-agent.dir-after.txt"
[ -f state.json ] && cp state.json "$OUT/3-agent.state.json"
cd - >/dev/null
echo "saved to $OUT"
