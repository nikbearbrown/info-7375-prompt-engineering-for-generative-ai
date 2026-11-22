#!/usr/bin/env bash
# package_submission.sh: the files the student uploads to Canvas, built from the checked 4K master and the records.
#   submission/Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.mp4   the film (1080p, the student's choice)
#   submission/Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.srt   its captions
#   submission/Produtoor_Suketh_INFO7375_FinalProjectFilm_Appendix.pdf the appendix the brief asks for
#   submission/Produtoor_Suketh_INFO7375_FinalProjectFilm_Records.zip  the records (script, fact-check, sources,
#                                                                       Frictional, evidence, film source, gate reports)
#   submission/SHA256SUMS
# Written by Claude Code, 2026-11-22. Run from anywhere: bash tools/package_submission.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/submission"
NAME="Produtoor_Suketh_INFO7375_FinalProjectFilm"

# re-encode the 1080p copy only when the 4K master is newer, so the film's checksum stays stable
if [ ! -e "$OUT/${NAME}_1080p.mp4" ] || [ film/exports/landscape/fine-print-film.mp4 -nt "$OUT/${NAME}_1080p.mp4" ]; then
  bash tools/make_1080p.sh > /dev/null
fi
python3 tools/make_script_md.py > /dev/null
python3 tools/appendix_pdf.py > /dev/null
cp APPENDIX.pdf "$OUT/${NAME}_Appendix.pdf"

STAGE="$(mktemp -d)/${NAME}_Records"
mkdir -p "$STAGE/film" "$STAGE/tools"
cp README.md ASSIGNMENT-BRIEF.md SCRIPT.md FACTCHECK.md SOURCES.md FRICTIONAL.md APPENDIX.md APPENDIX.pdf DESIGN.md PLAN.md "$STAGE/"
cp -R evidence "$STAGE/"
cp tools/*.py tools/*.sh "$STAGE/tools/"
for f in make_sheet.py beat_sheet.json scenes_body.py scene_data.py make_scene_data.py build_scenes.py build_audio.sh \
         finish_audio.py name_voice.py make_srt.py PRODUCTION-NOTES.md SHOTLIST.md PROMPTS.md \
         terminal_replay_record.json qc-sheet.png; do
  [ -e "film/$f" ] && cp "film/$f" "$STAGE/film/"
done
for f in film/*.py; do cp -n "$f" "$STAGE/film/" 2>/dev/null || true; done
cp -R film/gate-reports "$STAGE/film/"
[ -d film/_qc ] && cp -R film/_qc "$STAGE/film/"
find "$STAGE" -name ".DS_Store" -delete
rm -f "$OUT/${NAME}_Records.zip"
(cd "$(dirname "$STAGE")" && zip -qr -X "$OUT/${NAME}_Records.zip" "$(basename "$STAGE")")

cd "$OUT" && shasum -a 256 "${NAME}_1080p.mp4" "${NAME}_1080p.srt" "${NAME}_Appendix.pdf" "${NAME}_Records.zip" > SHA256SUMS
cat SHA256SUMS
ls -l "$OUT"
