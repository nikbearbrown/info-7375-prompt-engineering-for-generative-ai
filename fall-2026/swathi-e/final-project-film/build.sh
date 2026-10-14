#!/usr/bin/env bash
# build.sh -- INFO 7375 Final Project Pitch Film (Swathi Baba Eswarappa)
# Rebuilds the whole film from scratch. Audio is the master clock.
#
#   ./build.sh            full rebuild (facts -> audio -> scenes -> gates -> mux)
#   ./build.sh --mux-only skip audio + render; re-run every gate and re-mux
#
# Gate reports land in qc_reports/ (and _qc/ for the toolkit's Gate V).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

ART_HOME="${ART_HOME:-$HERE/../brutalist.art}"
# .venv-kokoro was not found on this machine; the Anaconda Python already has
# kokoro_onnx, onnxruntime and manim installed, and passed the toolkit's smoke test
PY="${PY:-/opt/anaconda3/bin/python3}"
MANIM="${MANIM:-/opt/anaconda3/bin/manim}"
OUT="BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4"
GAP=0.30                      # seconds of black between beats
QC="$ART_HOME/runtime/qc"

export ART_HOME
export PHONEMIZER_ESPEAK_LIBRARY="${PHONEMIZER_ESPEAK_LIBRARY:-/opt/homebrew/lib/libespeak-ng.dylib}"
export ESPEAK_DATA_PATH="${ESPEAK_DATA_PATH:-/opt/homebrew/share/espeak-ng-data}"

SCENES=($("$PY" -c "import json;print(' '.join(b['graphic']['manim'] for b in json.load(open('beat_sheet.json'))['beats']))"))
mkdir -p build/logs qc_reports/gateB

echo "==> [1/8] facts gate (every on-screen number from data/facts.json)"
"$PY" check_facts.py > /dev/null

if [[ "${1:-}" != "--mux-only" ]]; then
  echo "==> [2/8] Kokoro narration (local, free)"
  "$PY" "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" . --dry-run
  "$PY" "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" .
fi

echo "==> [3/8] toolkit Gate A (static scene check) + Gate W (WCAG/margins)"
for S in "${SCENES[@]}"; do
  echo "### $S"
  "$PY" "$QC/static_scene_check.py" scene.py --class "$S" 2>&1 | grep -vE '^\s*$' || true
done > qc_reports/gateA_static_scene_check.txt
"$PY" "$QC/wcag_margin_check.py" scene.py > qc_reports/gateW_wcag_margin_check.txt 2>&1
# Gate W only resolves the toolkit's own palette names, so append the real
# WCAG contrast of this film's text colours against its ground
"$PY" - "$QC" >> qc_reports/gateW_wcag_margin_check.txt <<'PYEOF'
import sys; sys.path.insert(0, sys.argv[1]); import wcag_margin_check as w
print("\n## Supplementary: WCAG contrast of every text colour vs ground #0B0B0C")
for n, h in [("FG", "#F5F3EF"), ("DIM", "#8A8A90"), ("AMBER", "#FFB020"), ("RED", "#FF4D3D"),
             ("GREEN", "#3DDC84"), ("BLUE", "#4FC3F7"), ("VIOLET", "#B388FF")]:
    c = w.contrast(h, "#0B0B0C")
    print(f"  {n:7} {h}  {c:5.2f}:1  {'PASS AA (>=4.5)' if c >= 4.5 else 'FAIL'}")
PYEOF

if [[ "${1:-}" != "--mux-only" ]]; then
  echo "==> [4/8] Manim scenes @2160p24 (Beat assertions run after every cue)"
  build/render_all.sh "-qk --frame_rate 24" 2160p24
  ! grep -l Traceback build/logs/render_B*.log
fi

echo "==> [5/8] toolkit Gate B (Manim layout audit, real bounding boxes)"
for S in "${SCENES[@]}"; do
  "$PY" "$QC/manim_layout_audit.py" scene.py --class "$S" > "qc_reports/gateB/$S.log" 2>&1 || true
  mv layout_audit.md "qc_reports/gateB/$S.md"; mv layout_audit.json "qc_reports/gateB/$S.json"
done

echo "==> [6/8] Week 1 frame-safety sweep (no content in the outer 16 px)"
"$PY" qc_frames.py --border 16 --step 4 | tee qc_reports/week1_qc_frames.txt

echo "==> [7/8] mux + concat + captions (Week 1 runtime gate 120-240 s)"
"$PY" build_mux.py --gap "$GAP" --out "$OUT" | tee qc_reports/week1_build_mux.txt
"$PY" make_srt.py

echo "==> [8/8] toolkit Gate V (final-frame check on the master)"
# Gate V times its samples from beat durations alone; give it a timeline that
# includes the 0.30 s gaps so late beats are not sampled seconds early
"$PY" - <<'EOF'
import json, subprocess
sh = json.load(open("beat_sheet.json")); n = len(sh["beats"])
for i, b in enumerate(sh["beats"]):
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", f"build/segments/seg_{b['beat_id']}.mp4"],
                             capture_output=True, text=True).stdout)
    b["render_duration_s"] = round(d + (0.30 if i < n - 1 else 0), 3)
json.dump(sh, open("build/qc_timeline_sheet.json", "w"), indent=1)
EOF
rm -rf _qc
"$PY" "$QC/final_frame_check.py" . --mp4 "$OUT" --sheet build/qc_timeline_sheet.json
cp _qc/REPORT.md qc_reports/gateV_final_frame_check_REPORT.md
cp _qc/contact_sheet.png qc_reports/gateV_contact_sheet.png

echo
echo "==> done: $OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
