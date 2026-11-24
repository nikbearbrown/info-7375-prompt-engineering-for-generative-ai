#!/usr/bin/env bash
# run_gates.sh — every Brutalist quality gate against the progress film, in order.
# Run from the toolkit root with the venv active:  bash <progress-film>/gates/run_gates.sh
# Writes reports to $R/_qc/gates/ and a one-line-per-gate SUMMARY.txt.
set -uo pipefail
R=youtube/brutalist/agent-proving-ground-progress
G=$R/_qc/gates
M=$R/exports/agent-proving-ground-progress.mp4
mkdir -p "$G/08_gate_B"
: > "$G/SUMMARY.txt"
sum(){ echo "$1" | tee -a "$G/SUMMARY.txt"; }
CLASSES=$(grep -o '^class B[0-9]*_[A-Za-z]*' $R/scenes.py | sed 's/class //')

# 01 schema (jsonschema from the system python3; it is not in the toolkit venv)
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -c "
import json,jsonschema
s=json.load(open('runtime/schema/beat_sheet.schema.json')); d=json.load(open('$R/beat_sheet.json'))
e=list(jsonschema.validators.validator_for(s)(s).iter_errors(d))
[print(list(x.path), x.message) for x in e]; print(f'{len(e)} error(s)'); raise SystemExit(1 if e else 0)" > $G/01_schema.txt 2>&1
rc=$?; sum "$([ $rc = 0 ] && echo PASS || echo FAIL) 01 schema ($(tail -1 $G/01_schema.txt))"

python3 runtime/scripts/build_safety.py $R > $G/02_build_safety.txt 2>&1; rc=$?
sum "$([ $rc = 0 ] && echo PASS || echo FAIL) 02 build_safety (rc=$rc)"

python3 runtime/qc/factcheck_check.py $R > $G/03_paperwork.txt 2>&1; rc=$?
sum "$([ $rc = 0 ] && echo PASS || echo FAIL) 03 paperwork / factcheck (rc=$rc)"

python3 runtime/qc/beat_lint.py $R/beat_sheet.json > $G/04_beat_lint.txt 2>&1; rc=$?
sum "$([ $rc -lt 2 ] && echo PASS || echo FAIL) 04 beat_lint (rc=$rc)"

python3 runtime/qc/gate_shape.py $R/beat_sheet.json > $G/05_gate_shape.txt 2>&1; rc=$?
sum "$([ $rc -lt 2 ] && echo PASS || echo FAIL) 05 gate_shape (rc=$rc)"

T=$(mktemp -d); cp $R/scenes.py $T/; worst=0; : > $G/06_gate_A.txt
for C in $CLASSES; do
  PYTHONPATH=runtime/manim python3 runtime/qc/static_scene_check.py $T/scenes.py --class $C >> $G/06_gate_A.txt 2>&1; rc=$?
  [ $rc -gt $worst ] && worst=$rc
done; rm -rf $T
sum "$([ $worst = 0 ] && echo PASS || ([ $worst = 1 ] && echo "PASS(warn)" || echo FAIL)) 06 Gate A static pre-flight, 13 scenes (worst rc=$worst)"

worst=0; : > $G/07_gate_W.txt
for C in $CLASSES; do
  python3 runtime/qc/wcag_margin_check.py $R/scenes.py --class $C >> $G/07_gate_W.txt 2>&1; rc=$?
  [ $rc -gt $worst ] && worst=$rc
done
sum "$([ $worst = 0 ] && echo PASS || echo FAIL) 07 Gate W contrast/margins/overlap, 13 scenes (worst rc=$worst)"

worst=0
for C in $CLASSES; do
  (cd $R && python3 ../../../runtime/qc/manim_layout_audit.py scenes.py --class $C --curve-strict > /dev/null 2>&1); rc=$?
  cp $R/layout_audit.md $G/08_gate_B/$C.md; [ $rc -gt $worst ] && worst=$rc
done
sum "$([ $worst = 0 ] && echo PASS || echo FAIL) 08 Gate B strict layout audit, 13 scenes (worst rc=$worst; strict fails on warnings too)"

python3 runtime/qc/final_frame_check.py $R --mp4 $M > $G/09_gate_V.txt 2>&1; rc=$?
cp $R/_qc/REPORT.md $G/09_gate_V_REPORT.md; cp $R/_qc/contact_sheet.png $G/09_gate_V_contact_sheet.png
sum "$([ $rc -lt 2 ] && echo PASS || echo FAIL) 09 Gate V on the final master ($(grep -o 'frames=.*MAJOR=[0-9]*' $G/09_gate_V.txt | head -1))"

cp $R/TYPECHECK.md $G/10_gate_T_TYPECHECK.md
sum "$(grep -q 'GATE T: PASS' "$(ls -t $R/_qc/art_final_*.log | head -1)" && echo PASS || echo FAIL) 10 Gate T (run by ./art final before the master; TYPECHECK.md)"

# 11 render integrity (the toolkit has no gate by this name; same checks as the October pitch)
{
  set +e
  ok(){ echo "OK   $*"; }; bad(){ echo "FAIL $*"; FAILS=$((FAILS+1)); }; FAILS=0
  V=$(ffprobe -v error -select_streams v -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$M")
  A=$(ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 "$M")
  NV=$(ffprobe -v error -select_streams v -show_entries stream=index -of csv=p=0 "$M" | wc -l | tr -d ' ')
  NA=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$M" | wc -l | tr -d ' ')
  [ "$NV" = 1 ] && [ "$NA" = 1 ] && ok "streams: 1 video, 1 audio" || bad "streams: $NV video, $NA audio"
  [ "$V" = "h264,3840,2160,24/1" ] && ok "video $V" || bad "video $V"
  echo "$A" | grep -q "^aac," && ok "audio $A" || bad "audio $A"
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$M")
  TL=$(python3 -c "import json;print(round(sum(float(b.get('render_duration_s') or b['actual_duration_s']) for b in json.load(open('$R/beat_sheet.json'))['beats']),3))")
  NAR=$(python3 -c "import json;print(round(sum(float(b['actual_duration_s']) for b in json.load(open('$R/beat_sheet.json'))['beats']),2))")
  python3 -c "import sys;sys.exit(0 if abs($DUR-$TL)<=1/24+1e-6 else 1)" && ok "duration ${DUR}s vs timeline ${TL}s" || bad "duration ${DUR}s vs timeline ${TL}s"
  python3 -c "import sys;sys.exit(0 if abs($TL-$NAR)<=13/24 else 1)" && ok "timeline ${TL}s vs narration sum ${NAR}s (<=1 frame/beat)" || bad "timeline ${TL}s vs narration ${NAR}s"
  NF=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$M")
  EXP=$(python3 -c "print(round($DUR*24))")
  [ "$NF" = "$EXP" ] && ok "decoded frames $NF vs expected $EXP" || bad "decoded frames $NF vs expected $EXP"
  ERR=$(ffmpeg -v error -xerror -i "$M" -f null - 2>&1 | head -3)
  [ -z "$ERR" ] && ok "full decode with -xerror: clean" || bad "decode: $ERR"
  VOL=$(ffmpeg -i "$M" -af volumedetect -vn -f null - 2>&1 | grep -E "mean_volume|max_volume" | awk '{print $5}' | tr '\n' ' ')
  set -- $VOL
  python3 -c "import sys;sys.exit(0 if $1>-40 and $2<=0 else 1)" && ok "audio mean $1 dB, peak $2 dB (floor -40 dB, no clipping above 0)" || bad "audio mean $1 peak $2"
  SHA=$(shasum -a 256 "$M" | cut -d' ' -f1)
  grep -q "$SHA" $R/exports/agent-proving-ground-progress.verified.json && ok "sha256 $SHA matches .verified.json" || bad "sha256 $SHA not in .verified.json"
  echo "size $(stat -f%z "$M") bytes"
  echo "failures: $FAILS"
} > $G/11_render_integrity.txt 2>&1
sum "$(grep -q '^failures: 0' $G/11_render_integrity.txt && echo PASS || echo FAIL) 11 render integrity ($(grep -c '^OK' $G/11_render_integrity.txt) checks OK)"

python3 -m unittest discover -s tests > $G/12_unit_tests.txt 2>&1; rc=$?
sum "$([ $rc = 0 ] && echo PASS || echo FAIL) 12 toolkit unit tests ($(grep -E '^Ran ' $G/12_unit_tests.txt))"

./art smoke > $G/13_smoke.txt 2>&1; rc=$?
sum "$([ $rc = 0 ] && echo PASS || echo FAIL) 13 smoke test ($(grep -o 'SMOKE PASS' $G/13_smoke.txt || echo 'no SMOKE PASS'))"
