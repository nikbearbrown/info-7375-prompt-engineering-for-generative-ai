#!/usr/bin/env bash
# Runs the Brutalist toolkit's own GATE V (final_frame_check.py) on the finished film
# and saves its report in reports/.
# Usage (from the final-project-film folder, after `bash make_film.sh Gaikar`):
#   bash tools/run_gate_v.sh
set -e
FILM="${1:-Gaikar_pitch.mp4}"
BRUT="${BRUTALIST:-$HOME/brutalist.art}"
[ -f "$FILM" ] || { echo "No $FILM - run: bash make_film.sh Gaikar"; exit 1; }
[ -d build ] || { echo "No build/ folder - run: bash make_film.sh Gaikar"; exit 1; }

# 1. the toolkit (only the checkout; no install needed for this gate)
if [ ! -f "$BRUT/runtime/qc/final_frame_check.py" ]; then
  echo "Cloning the Brutalist toolkit into $BRUT ..."
  git clone --depth 1 https://github.com/nikbearbrown/brutalist.art "$BRUT"
fi

# 2. a private Python env with the gate's two libraries (kept outside the repo)
VENV="${VENV:-$HOME/.venv-brutalist-qc}"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q numpy pillow
fi

# 3. the gate needs each beat's real start time and length -> write them into a copy of the beat sheet
"$VENV/bin/python" - <<'EOF'
import json, subprocess
s = json.load(open('beat_sheet.json')); t = 0.0
for b in s['beats']:
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                       '-of', 'csv=p=0', f"build/{b['beat_id']}.mp4"]))
    b['t_start'] = round(t, 3); b['actual_duration_s'] = round(d, 3); t += d
json.dump(s, open('build/gate_sheet.json', 'w'), indent=2)
print(f"timeline: {len(s['beats'])} beats, {t:.1f} s")
EOF

# 4. run the toolkit's gate and keep its report
mkdir -p reports
set +e
"$VENV/bin/python" "$BRUT/runtime/qc/final_frame_check.py" . --mp4 "$FILM" --sheet build/gate_sheet.json | tee reports/gate-v-console.txt
rc=${PIPESTATUS[0]}
set -e
cp _qc/REPORT.md reports/GATE-V-REPORT.md
[ -f _qc/contact_sheet.png ] && cp _qc/contact_sheet.png reports/gate-v-contact-sheet.png
rm -rf _qc
echo "Toolkit commit: $(git -C "$BRUT" rev-parse --short HEAD)" >> reports/gate-v-console.txt
echo "Run on: $(date '+%Y-%m-%d %H:%M')" >> reports/gate-v-console.txt
RES=$([ $rc -eq 0 ] && echo "PASSED" || echo "FAILED (exit $rc)")
printf '\n**%s** — Ran the toolkit'"'"'s Gate V on the final film with `tools/run_gate_v.sh` (brutalist.art commit %s): %s. Report in `reports/GATE-V-REPORT.md`.\n' "$(date '+%Y-%m-%d, ~%-I:%M %p')" "$(git -C "$BRUT" rev-parse --short HEAD)" "$RES" > build/frictional_line.txt
"$VENV/bin/python" - <<'PY'
s = open('FRICTIONAL.md').read(); line = open('build/frictional_line.txt').read()
key = "**What I'd do differently:**"
open('FRICTIONAL.md', 'w').write(s.replace(key, line.strip() + "\n\n" + key) if key in s else s + line)
PY
if [ $rc -eq 0 ]; then echo "GATE V PASSED - report in reports/GATE-V-REPORT.md"; else echo "GATE V FAILED (exit $rc) - send the report to Claude"; fi
exit $rc
