#!/usr/bin/env bash
# stage_github.sh: copy the film's records into the course fork at fall-2026/suketh-p/final-project-film-2/.
# The October pitch film already uses final-project-film/. The copy holds the same files as the Canvas records zip,
# which is later built from the pushed commit with `git archive`, so the two match exactly.
# MP4s are left out (the course's .gitignore excludes them); the film is named by filename and SHA-256 in README.md.
# Privacy: in the toolkit's own logs, the home folder is replaced with "~". The terminal evidence files are copied
# byte for byte, so that their SHA256SUMS still hold.
# Written by Claude Code, 2026-11-22. Run: bash tools/stage_github.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORK="$ROOT/../fork"
DEST="$FORK/fall-2026/suketh-p/final-project-film-2"
cd "$ROOT"
python3 tools/make_script_md.py > /dev/null
python3 tools/appendix_pdf.py > /dev/null
rm -rf "$DEST"; mkdir -p "$DEST/film" "$DEST/tools"
cp README.md ASSIGNMENT-BRIEF.md SCRIPT.md FACTCHECK.md SOURCES.md FRICTIONAL.md APPENDIX.md APPENDIX.pdf \
   DESIGN.md PLAN.md "$DEST/"
cp submission/Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.srt "$DEST/"
cp -R evidence "$DEST/"
cp tools/*.py tools/*.sh "$DEST/tools/"
cp film/*.py film/*.sh film/beat_sheet.json film/terminal_replay_record.json film/qc-sheet.png "$DEST/film/"
for f in film/*.md; do [ -L "$f" ] || cp "$f" "$DEST/film/"; done      # FACTCHECK.md there is a symlink to ../
cp -R film/gate-reports "$DEST/film/"
[ -d film/_qc ] && cp -R film/_qc "$DEST/film/"
find "$DEST" -name ".DS_Store" -delete
# scrub the home folder from every text file except the hashed terminal evidence
find "$DEST" -type f \( -name "*.md" -o -name "*.log" -o -name "*.json" -o -name "*.txt" -o -name "*.py" -o -name "*.sh" \) \
     ! -path "*/evidence/terminal/*" -print0 | xargs -0 sed -i '' "s#$HOME#~#g"
echo "staged: $(find "$DEST" -type f | wc -l | tr -d ' ') files, $(du -sh "$DEST" | cut -f1)"
