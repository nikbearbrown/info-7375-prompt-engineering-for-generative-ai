#!/usr/bin/env bash
# Runs the Brutalist toolkit's GATE F on this folder:
#   presence check (FACTCHECK.md, SHOTLIST.md, PROMPTS.md exist, as run.sh requires)
#   + runtime/qc/factcheck_check.py (the content half)
# Saves the result in reports/ and logs it in FRICTIONAL.md.
# Usage (from the final-project-film folder):  bash tools/run_gate_f.sh
set -e
BRUT="${BRUTALIST:-$HOME/brutalist.art}"
[ -f "$BRUT/runtime/qc/factcheck_check.py" ] || git clone --depth 1 https://github.com/nikbearbrown/brutalist.art "$BRUT"
mkdir -p reports
{
  echo "# Gate F — paperwork + fact-check"
  echo
  for f in FACTCHECK.md SHOTLIST.md PROMPTS.md; do
    if [ -s "$f" ]; then echo "- $f: present"; else echo "- $f: MISSING"; fi
  done
  echo
  echo '```'
} > reports/GATE-F-REPORT.md
set +e
python3 "$BRUT/runtime/qc/factcheck_check.py" . | tee -a reports/GATE-F-REPORT.md
rc=${PIPESTATUS[0]}
set -e
for f in FACTCHECK.md SHOTLIST.md PROMPTS.md; do [ -s "$f" ] || rc=2; done
{
  echo '```'
  echo
  echo "Toolkit commit: $(git -C "$BRUT" rev-parse --short HEAD) · run on $(date '+%Y-%m-%d %H:%M') · exit $rc"
} >> reports/GATE-F-REPORT.md
RES=$([ $rc -eq 0 ] && echo "PASSED (clean)" || echo "exit $rc")
python3 - "$RES" "$(date '+%Y-%m-%d, ~%-I:%M %p')" "$(git -C "$BRUT" rev-parse --short HEAD)" <<'PY'
import sys
res, when, commit = sys.argv[1:4]
# FRICTIONAL: one dated line
s = open('FRICTIONAL.md').read(); key = "**What I'd do differently:**"
line = (f"**{when}** — Compared my folder with the toolkit's show-tell workflow: it requires FACTCHECK.md, SHOTLIST.md and PROMPTS.md "
        f"(\"Gate F refuses to render without all three\"), which I didn't have. Added them (Claude listed the claims; I checked each against its source) "
        f"and ran the toolkit's Gate F with `tools/run_gate_f.sh` (brutalist.art {commit}): {res}. Report in `reports/GATE-F-REPORT.md`.")
if 'run_gate_f.sh' not in s:
    s = s.replace(key, line + "\n\n" + key) if key in s else s + "\n" + line + "\n"
    open('FRICTIONAL.md', 'w').write(s)
# README: list the new files
r = open('README.md').read()
if 'FACTCHECK.md' not in r:
    r = r.replace("| `BUILD-PROMPT.md` |", "| `FACTCHECK.md` | Every claim in the narration, its verdict and source (toolkit format) |\n"
                  "| `SHOTLIST.md` | What each beat shows and why |\n| `PROMPTS.md` | Generation prompts: none used |\n| `BUILD-PROMPT.md` |")
    r = r.replace("bash make_film.sh Gaikar\n```", "bash make_film.sh Gaikar\n# 3. toolkit checks\nbash tools/run_gate_v.sh   # visual QC\nbash tools/run_gate_f.sh   # paperwork + fact-check\n```")
    open('README.md', 'w').write(r)
# BUILD-PROMPT: log the prompt and the gate
b = open('BUILD-PROMPT.md').read()
if 'run_gate_f.sh' not in b:
    b = b.replace("## 2. Brutalist", "- 2026-10-14: \"see [brutalist.art] and tell me I have done every part like the minor parts too\" → Claude compared the folder with the show-tell workflow, wrote FACTCHECK.md, SHOTLIST.md and PROMPTS.md, and `tools/run_gate_f.sh`\n\n## 2. Brutalist")
    b = b.replace("bash tools/run_gate_v.sh      # clones brutalist.art if needed, writes reports/GATE-V-REPORT.md",
                  "bash tools/run_gate_v.sh      # clones brutalist.art if needed, writes reports/GATE-V-REPORT.md\nbash tools/run_gate_f.sh      # Gate F: paperwork present + factcheck_check.py, writes reports/GATE-F-REPORT.md")
    open('BUILD-PROMPT.md', 'w').write(b)
print("docs updated")
PY
[ $rc -eq 0 ] && echo "GATE F PASSED - report in reports/GATE-F-REPORT.md" || echo "GATE F FAILED (exit $rc) - send the report to Claude"
exit $rc
