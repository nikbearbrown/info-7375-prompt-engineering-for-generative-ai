#!/usr/bin/env bash
# run_upstream_gates.sh -- run the newer Brutalist toolkit gates on this film.
#
# The local toolkit checkout (../brutalist.art, commit 29ba0e8, 2026-09-15)
# predates GATE T, GATE MASTER, GATE LOUDNESS, GATE SRT and GATE SHARPNESS.
# No git command is run (not even fetch): the five gate scripts are read from
# a local copy extracted earlier from toolkit commit 519fcbb (2026-10-12),
# ../mode-build-video/gates/ by default, or $UPSTREAM_GATES. Gates added
# upstream after 2026-10-12 are therefore not run.
# A temporary copy of the film is staged the way those gates expect
# (<slug>.mp4, media/<beat>.mp4), the gates run there, and their reports are
# copied into qc_reports/upstream/. Nothing is written outside this folder
# except the temporary staging directory.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1

HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
PY="${PY:-/opt/anaconda3/bin/python3}"
OUT="BabaEswarappa_Swathi_INFO7375_FinalProjectPlanFilm"
SLUG=$("$PY" -c "import json;print(json.load(open('beat_sheet.json'))['metadata']['slug'])")
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
U="${UPSTREAM_GATES:-$HERE/../mode-build-video/gates}"
REV="519fcbb"

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
  echo "# Upstream Brutalist gates — scripts from toolkit $REV (local copy, no git), run $(date '+%Y-%m-%d %H:%M')"
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
