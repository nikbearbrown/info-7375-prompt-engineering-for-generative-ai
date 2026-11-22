#!/usr/bin/env bash
# make_1080p.sh: the 1080p submission copy of the film, scaled down from the checked 4K master.
# The student asked for 1080p on 2026-11-21 ("So cut it down to the normal 1080p"). The toolkit's gates run on the
# 4K render, and this copy only rescales it (lanczos). Audio is copied unchanged, and the captions are the same file.
# Written by Claude Code. Run from the project folder: bash tools/make_1080p.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/film/exports/landscape/fine-print-film.mp4"
OUT_DIR="$ROOT/submission"
OUT="$OUT_DIR/Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.mp4"
mkdir -p "$OUT_DIR"
ffmpeg -v error -y -i "$SRC" -vf "scale=1920:1080:flags=lanczos" -c:v libx264 -preset slow -crf 18 \
       -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
cp "$ROOT/film/exports/landscape/fine-print-film.srt" "$OUT_DIR/Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.srt"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name \
        -show_entries format=duration,size -of default=nw=1 "$OUT"
shasum -a 256 "$OUT"
