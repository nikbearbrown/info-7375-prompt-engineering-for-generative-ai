#!/usr/bin/env bash
# build_film.sh — rebuild the CheckedSQL pitch film with the Brutalist toolkit, then copy the
# film, captions, final beat sheet and every gate report back into this folder.
#
#   ./build_film.sh /path/to/brutalist.art           # reuse clips that are already rendered
#   ./build_film.sh /path/to/brutalist.art --fresh   # re-render every drawn scene from scratch
#
# Free pipeline only: Kokoro narration + Manim + Remotion, all local. No API keys.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="$(cd "${1:?usage: ./build_film.sh /path/to/brutalist.art [--fresh]}" && pwd)"
FRESH="${2:-}"
SLUG="checkedsql-pitch"
REEL="$TOOLKIT/youtube/$SLUG"

echo "== 1. copy the film sources into the toolkit: $REEL"
mkdir -p "$REEL"
cp "$HERE"/build/{make_sheet.py,scenes.py,FACTCHECK.md,SHOTLIST.md,PROMPTS.md} "$REEL/"
[ -f "$HERE/build/chat_test.png" ] && cp "$HERE/build/chat_test.png" "$REEL/"
if [ "$FRESH" = "--fresh" ]; then
  echo "   --fresh: clearing old drawn clips and the Manim cache"
  rm -rf "$REEL"/manim/*.mp4 "$REEL/media/videos" "$REEL"/media/B*.mp4
fi
(cd "$REEL" && python3 make_sheet.py)

cd "$TOOLKIT"
# Gate T fix found 2026-10-14: the terms card draws its meanings at 48px, which puts EB Garamond's
# x-height at 40px at 4K, one pixel under the 41px floor. 52px clears it.
sed -i.bak "s/const meanSize = 48;/const meanSize = 52;/" runtime/remotion/src/scenes/ClaudeDefinitions.tsx && rm -f runtime/remotion/src/scenes/ClaudeDefinitions.tsx.bak

echo "== 2. narration (Kokoro, local) — this measures every beat and sets the clock"
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"
python3 "$HERE/build/sync_props.py" "$REEL"          # cards take their length from the measured audio

echo "== 3. review cut + gates A, W, L, F, B, V (renders every pending scene)"
./art run "$REEL"

echo "== 4. GATE T (type check) + clean master"
./art final "$REEL"
cp "$TOOLKIT/renders/$SLUG.mp4" "$REEL/$SLUG.mp4"    # ./art final writes the master to renders/

echo "== 5. render-integrity (GATE MASTER), loudness, bookends"
python3 runtime/scripts/master_check.py "$REEL"
python3 runtime/scripts/loudness_check.py "$REEL"
python3 runtime/scripts/bookend_check.py "$REEL" | tee "$REEL/BOOKENDCHECK.txt"

echo "== 6. copy results back"
cp "$REEL/$SLUG.mp4" "$HERE/$SLUG.mp4"
cp "$REEL/beat_sheet.json" "$HERE/beat_sheet.json"
cp "$REEL/beat_sheet.json" "$HERE/build/beat_sheet.json"
python3 "$HERE/build/make_srt.py" "$REEL" "$HERE/$SLUG.srt"
mkdir -p "$HERE/gate-reports"
for f in TYPECHECK.md MASTERCHECK.md LOUDNESS.md BOOKENDCHECK.txt layout_audit.md FACTCHECK.md qc-sheet.png; do
  [ -f "$REEL/$f" ] && cp "$REEL/$f" "$HERE/gate-reports/"
done
[ -f "$REEL/_qc/REPORT.md" ] && cp "$REEL/_qc/REPORT.md" "$HERE/gate-reports/GATE-V-REPORT.md"
ls "$HERE/gate-reports"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$HERE/$SLUG.mp4")
echo "== done: $HERE/$SLUG.mp4  (${DUR}s — must be 120–240 s)"
