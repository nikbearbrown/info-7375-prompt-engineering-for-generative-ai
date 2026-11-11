#!/bin/zsh
# End-to-end on a fresh copy of the JS2 folder. Usage: e2e.sh <assignment-folder>
SRC="$1"
FRESH=$(mktemp -d)/js2
rsync -a --exclude '__pycache__' --exclude '.DS_Store' "$SRC"/ "$FRESH"/
cd "$FRESH" || exit 9
TS=$(date -u +%Y-%m-%dT%H-%M-%SZ)
echo "# END-TO-END 2 in a fresh copy (rsync of the folder minus caches into a temp dir). Run by Claude Code at $TS. The temp path is shown as \$FRESH."
echo
echo "## 1. tests"; python3 -m unittest discover -s tests -t . 2>&1 | tail -3; echo "exit=$pipestatus[1]"
echo; echo "## 2. mutants"; python3 tests/run_mutants.py 2>&1 | grep -E "CONTROL|KILLED$|SURVIVED|INVALID|W1[1-3]"
echo; echo "## 3. live run, main watch list (state carried over from earlier runs)"
python3 -m agent.loop --label e2e2 > /tmp/e2e2-$$.txt 2>&1; echo "exit=$?"; head -14 /tmp/e2e2-$$.txt
R=$(ls -d runs/*-e2e2 | tail -1)
echo "warnings in trace: $(grep -c '"event": "warning"' $R/trace.jsonl)"
echo; echo "## 4. independent check of that run"
python3 -m verify.independent_check "$R" > /tmp/ic-$$.txt 2>&1; echo "exit=$? (1 = a contradiction was found)"
grep -E "contradiction|CONTRADICTED" /tmp/ic-$$.txt | cut -c1-160
echo; echo "## 5. drop rule, first run into an empty output folder -> no_baseline on every board that answered"
python3 -m agent.loop --out runs/e2e2-fresh-out --label first > /tmp/fo-$$.txt 2>&1; echo "exit=$?"
grep -A8 "## Warnings" /tmp/fo-$$.txt | cut -c1-140
echo; echo "## 6. drop rule on real data: the copy's state for ashby:linear is edited (in this temp copy only) to say the last run had 100 postings"
python3 - <<'PY'
import json; p="runs/state/ashby-linear.state.json"; d=json.load(open(p)); d["runs"][-1]["postings"]=100; json.dump(d,open(p,"w"))
PY
python3 -m agent.loop --label droptest > /tmp/dt-$$.txt 2>&1; echo "exit=$? (warning only: exit unchanged)"
grep -A4 "## Warnings" /tmp/dt-$$.txt | cut -c1-160; head -1 /tmp/dt-$$.txt
echo; echo "## 7. edge: --out outside the folder"
python3 -m agent.loop --out /tmp/js2-outside-$$ > /dev/null 2>/tmp/o-$$.txt; echo "exit=$?"; cut -c1-160 /tmp/o-$$.txt
echo; echo "## 8. edge: unknown ATS and a ../ slug (no request may be sent for either)"
echo '{"boards":[{"ats":"workday","slug":"acme"},{"ats":"greenhouse","slug":"../etc"}]}' > config/e2e-bad.json
python3 -m agent.loop --watchlist config/e2e-bad.json --label bad > /tmp/b-$$.txt 2>&1; echo "exit=$?"
grep -E "EXIT|workday|etc" /tmp/b-$$.txt | cut -c1-160
B=$(ls -d runs/*-bad 2>/dev/null | tail -1); [ -n "$B" ] && echo "observations (requests sent): $(grep -c '"event": "observation"' $B/trace.jsonl)"
echo; echo "## 9. edge: missing config"
python3 -m agent.loop --watchlist config/nope.json > /dev/null 2>/tmp/m-$$.txt; echo "exit=$?"; cut -c1-160 /tmp/m-$$.txt
echo; echo "## 10. edge: same label twice in a row"
python3 -m agent.loop --label twice > /dev/null 2>&1; echo "exit=$?"
python3 -m agent.loop --label twice > /dev/null 2>&1; echo "exit=$?"
ls -d runs/*twice* | sed 's#.*/##'
echo; echo "## 11. nothing was written outside the copy"; ls /tmp/js2-outside-$$ 2>&1 | head -1
rm -f /tmp/*-$$.txt
