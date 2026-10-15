#!/usr/bin/env bash
# build_film.sh — rebuild the CheckedSQL pitch film with the Brutalist toolkit, then
# copy the film, the final beat sheet and the gate reports back into this folder.
#
#   ./build_film.sh /path/to/brutalist.art
#
# Free pipeline only: Kokoro narration + Manim + Remotion, all local. No API keys.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="${1:?usage: ./build_film.sh /path/to/brutalist.art}"
TOOLKIT="$(cd "$TOOLKIT" && pwd)"
SLUG="checkedsql-pitch"
REEL="$TOOLKIT/youtube/$SLUG"

echo "== 1. copy the film sources into the toolkit: $REEL"
mkdir -p "$REEL"
cp "$HERE"/build/{make_sheet.py,scenes.py,FACTCHECK.md,SHOTLIST.md,PROMPTS.md} "$REEL/"
(cd "$REEL" && python3 make_sheet.py)

cd "$TOOLKIT"
sed -i "" "s/const meanSize = 48;/const meanSize = 52;/" runtime/remotion/src/scenes/ClaudeDefinitions.tsx   # Gate T fix, see FRICTIONAL.md
echo "== 2. narration (Kokoro, local) — this measures every beat and sets the clock"
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"

echo "== 3. review cut + gates A, W, L, F, B, V (renders every Manim scene)"
./art run "$REEL"

echo "== 4. GATE T (type check) + clean master"
./art final "$REEL"

echo "== 5. render-integrity (GATE MASTER) and loudness"
cp "$TOOLKIT/renders/$SLUG.mp4" "$REEL/" 2>/dev/null || true
python3 runtime/scripts/master_check.py "$REEL"
python3 runtime/scripts/loudness_check.py "$REEL" > "$REEL/LOUDNESS-run.txt" 2>&1 || { cat "$REEL/LOUDNESS-run.txt"; exit 2; }
python3 runtime/scripts/bookend_check.py "$REEL" | tee "$REEL/BOOKENDCHECK.txt"

echo "== 6. copy results back"
cp "$REEL/$SLUG.mp4" "$HERE/$SLUG.mp4"
cp "$REEL/beat_sheet.json" "$HERE/beat_sheet.json"
cp "$REEL/beat_sheet.json" "$HERE/build/beat_sheet.json"
mkdir -p "$HERE/gate-reports"
for f in TYPECHECK.md MASTERCHECK.md LOUDNESS.md LOUDNESS-run.txt BOOKENDCHECK.txt layout_audit.md FACTCHECK.md; do
  [ -f "$REEL/$f" ] && cp "$REEL/$f" "$HERE/gate-reports/"
done
ls "$HERE/gate-reports"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HERE/$SLUG.mp4")
echo "== done: $HERE/$SLUG.mp4  (${DUR}s — must be 120–240 s)"
