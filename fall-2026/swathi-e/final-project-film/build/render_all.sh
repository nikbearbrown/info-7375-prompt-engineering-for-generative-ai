#!/usr/bin/env bash
# render every scene in parallel, each with its own media dir (Manim's text
# cache is not safe to share), then collect the mp4s where build_mux expects
set -uo pipefail
Q="${1:--qk --frame_rate 24}"; SUB="${2:-2160p24}"
cd "$(dirname "$0")/.."
S=$(/opt/anaconda3/bin/python3 -c "import json;print(' '.join(b['graphic']['manim'] for b in json.load(open('beat_sheet.json'))['beats']))")
mkdir -p build/logs media/videos/scene/$SUB
for s in $S; do
  ( /opt/anaconda3/bin/manim $Q --disable_caching --media_dir build/mq/$s scene.py $s > build/logs/render_$s.log 2>&1
    rc=$?; [ $rc -eq 0 ] && cp build/mq/$s/videos/scene/$SUB/$s.mp4 media/videos/scene/$SUB/
    echo "$s exit=$rc" ) &
done; wait
grep -h "\[slack\]" build/logs/render_*.log
