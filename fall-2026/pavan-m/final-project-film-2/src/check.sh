#!/bin/bash
# check.sh — rebuild scenes.py, render a still of every scene, make a contact sheet,
# and run show-tell's two pre-checks (Gate A static check, layout audit).
# Run from the reel folder:   bash check.sh
set -u
TK=~/Desktop/Prompt2/brutalist-final
cd "$(dirname "$0")"

cat "$TK/skills/make/show-tell/templates/iso_kit.py" scenes_body.py > scenes.py
CLASSES=$(grep -oE '^class B[0-9]+_[A-Za-z]+' scenes.py | cut -d' ' -f2)
echo "Scenes found: $(echo "$CLASSES" | wc -l | tr -d ' ')"

echo "== 1/3 stills =="
rm -rf /tmp/ctl_stills
for c in $CLASSES; do
  if manim -ql -s --media_dir /tmp/ctl_stills scenes.py "$c" > "/tmp/ctl_$c.log" 2>&1 < /dev/null; then
    echo "  ok   $c"
  else
    echo "  FAIL $c  (tail -15 /tmp/ctl_$c.log)"
  fi
done
ffmpeg -y -v error -pattern_type glob -i '/tmp/ctl_stills/images/scenes/*.png' \
  -filter_complex "scale=480:-1,tile=4x5" -frames:v 1 contact.png && echo "  contact.png written"

echo "== 2/3 Gate A pre-audit (folder with ONLY scenes.py) =="
rm -rf /tmp/ctl_gateA && mkdir /tmp/ctl_gateA && cp scenes.py /tmp/ctl_gateA/
( cd /tmp/ctl_gateA && for c in $CLASSES; do
    echo "--- $c"; python3 "$TK/runtime/qc/static_scene_check.py" scenes.py --class "$c" 2>&1 | tail -3
  done ) > gateA_pre.txt
echo "  written gateA_pre.txt"

echo "== 3/3 layout audit =="
for c in $CLASSES; do
  echo "--- $c"; python3 "$TK/runtime/qc/manim_layout_audit.py" scenes.py --class "$c" --curve-strict 2>&1 | tail -4
done > layout_pre.txt
echo "  written layout_pre.txt"

echo "== problems found =="
grep -i -E "fail|error|warn|traceback" gateA_pre.txt layout_pre.txt | head -40 || echo "  none"
