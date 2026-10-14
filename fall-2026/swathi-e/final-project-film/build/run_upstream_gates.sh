#!/usr/bin/env bash
# run_upstream_gates.sh -- run the CURRENT Brutalist toolkit's gates on this film.
#
# The local toolkit checkout (../brutalist.art, commit 29ba0e8, 2026-09-15)
# predates GATE T, GATE MASTER, GATE LOUDNESS, GATE SRT and GATE SHARPNESS.
# This script takes the gate scripts from upstream origin/main (or from
# $UPSTREAM_ART if you point it at a fresh clone), stages a temporary copy of
# the film laid out the way those gates expect (<slug>.mp4, media/<beat>.mp4),
# runs them there, and copies their reports into qc_reports/upstream/.
# Nothing is written into the toolkit or into this folder except the reports.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
PY="${PY:-/opt/anaconda3/bin/python3}"
OUT="BabaEswarappa_Swathi_INFO7375_FinalProjectFilm"
SLUG=$("$PY" -c "import json;print(json.load(open('beat_sheet.json'))['metadata']['slug'])")
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

if [[ -n "${UPSTREAM_ART:-}" ]]; then
  UP="$UPSTREAM_ART"; REV=$(git -C "$UP" rev-parse --short HEAD)
else
  git -C ../brutalist.art fetch -q origin
  REV=$(git -C ../brutalist.art rev-parse --short origin/main)
  mkdir -p "$TMP/up"
  git -C ../brutalist.art archive origin/main runtime/scripts runtime/qc | tar -x -C "$TMP/up"
  UP="$TMP/up"
fi
U="$UP/runtime/scripts"

R="$TMP/$SLUG"; mkdir -p "$R/media"
cp beat_sheet.json "$R/"; cp -R mp3 "$R/"
cp "$OUT.mp4" "$R/$SLUG.mp4"; cp "$OUT.srt" "$R/$SLUG.srt"
"$PY" - "$R" <<'PYEOF'
import json, shutil, sys
for b in json.load(open("beat_sheet.json"))["beats"]:
    shutil.copy(f"media/videos/scene/2160p24/{b['graphic']['manim']}.mp4",
                f"{sys.argv[1]}/media/{b['beat_id']}.mp4")
PYEOF

mkdir -p qc_reports/upstream
{
  echo "# Upstream Brutalist gates — toolkit origin/main $REV, run $(date '+%Y-%m-%d %H:%M')"
  echo
  for g in "loudness_check.py --mp4 $R/$SLUG.mp4" "master_check.py --mp4 $R/$SLUG.mp4" \
           "srt_check.py --srt $R/$SLUG.srt" "sharpness_check.py" "type_check.py"; do
    set -- $g
    "$PY" "$U/$1" "$R" "${@:2}" > "$TMP/log" 2>&1; rc=$?
    echo "## $1  (exit $rc)"; echo '```'; grep -vE "^\s*$" "$TMP/log" | tail -6; echo '```'; echo
  done
} > qc_reports/upstream/SUMMARY.md
for f in LOUDNESS.md MASTERCHECK.md SRTCHECK.md SHARPNESS.md TYPECHECK.md; do
  [[ -f "$R/$f" ]] && cp "$R/$f" qc_reports/upstream/
done
cat qc_reports/upstream/SUMMARY.md
