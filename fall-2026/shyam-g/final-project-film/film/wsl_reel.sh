#!/usr/bin/env bash
# Run inside Ubuntu (WSL). Works on the render copy of the reel at
# ~/reels/stopline-pitch (outside OneDrive) and copies results back.
#   bash film/wsl_reel.sh scenes            re-paste kit + scenes_body.py into the reel's scenes.py
#   bash film/wsl_reel.sh stills [Class..]  low-res last frames into film/stills/
#   bash film/wsl_reel.sh pad               add the 1.0 s silent tail to BOUT and re-measure it
#   bash film/wsl_reel.sh whisper [BID..]   transcribe beats to check pronunciation
#   bash film/wsl_reel.sh run | final       the toolkit's render + gates
#   bash film/wsl_reel.sh collect           copy the film and gate reports back into film/
set -euo pipefail
source "$HOME/brutalist-venv/bin/activate"
TK="$HOME/brutalist.art"
PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REEL="$HOME/reels/stopline-pitch"
KIT="$TK/skills/make/show-tell/templates/iso_kit.py"
cmd="${1:-}"; shift || true

case "$cmd" in
  scenes)
    { sed -e '$a\' "$KIT"; echo; cat "$PROJ/film/scenes_body.py"; } > "$REEL/scenes.py"
    cp "$REEL/scenes.py" "$PROJ/film/reel/scenes.py"
    echo "scenes.py rebuilt" ;;
  stills)
    mkdir -p "$PROJ/film/stills"; cd "$REEL"
    classes=("$@"); [ ${#classes[@]} -eq 0 ] && mapfile -t classes < <(grep -o '^class B[0-9]*_[A-Za-z]*' scenes.py | cut -d' ' -f2)
    for c in "${classes[@]}"; do
      rm -rf "/tmp/stills_media/$c"
      if manim -ql -s --media_dir "/tmp/stills_media/$c" scenes.py "$c" > "/tmp/manim_$c.log" 2>&1; then
        cp "$(find "/tmp/stills_media/$c" -name '*.png' | head -1)" "$PROJ/film/stills/$c.png"; echo "$c ok"
      else echo "$c FAILED"; tail -8 "/tmp/manim_$c.log"; fi
    done ;;
  pad)
    cd "$REEL"
    ffmpeg -y -loglevel error -i mp3/beat-BOUT.mp3 -af "apad=pad_dur=1.0" mp3/beat-BOUT.padded.mp3
    mv mp3/beat-BOUT.padded.mp3 mp3/beat-BOUT.mp3
    d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 mp3/beat-BOUT.mp3)
    python3 - "$d" <<'EOF'
import json, sys
s = json.load(open("beat_sheet.json"))
for b in s["beats"]:
    if b["beat_id"] == "BOUT":
        b["actual_duration_s"] = round(float(sys.argv[1]), 2)
json.dump(s, open("beat_sheet.json", "w"), indent=2, ensure_ascii=False)
print("BOUT actual_duration_s =", round(float(sys.argv[1]), 2))
EOF
    ;;
  whisper)
    cd "$REEL"
    python3 - "$@" <<'EOF'
import subprocess, sys, numpy as np
from faster_whisper import WhisperModel
bids = sys.argv[1:] or ["BIDEA", "B00", "B03", "B08", "BOUT"]
m = WhisperModel("base.en", device="cpu", compute_type="int8")
for bid in bids:
    # decode with ffmpeg ourselves: this faster-whisper/PyAV pairing can't open mp3 directly
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"mp3/beat-{bid}.mp3", "-f", "s16le",
                          "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segs, _ = m.transcribe(audio)
    print(bid, "::", " ".join(s.text.strip() for s in segs))
EOF
    ;;
  run)
    # Ubuntu's ffmpeg has drawtext, so compile.py burns a running timecode into the
    # review cut's top-right corner; Gate V excludes only the bottom-left label strip
    # and reads the timecode as edge-bleed on every frame. ART_NO_DRAWTEXT is the
    # toolkit's own switch for builds without drawtext. The master never carries it.
    cd "$TK"; ART_NO_DRAWTEXT=1 ./art run "$REEL" --height 2160 ;;
  final)
    cd "$TK"; ./art final "$REEL" --height 2160 --out "$REEL/exports/landscape" ;;
  collect)
    mkdir -p "$PROJ/film/gate_reports"
    for f in _qc/REPORT.md _qc/contact_sheet.png TYPECHECK.md layout_audit.md build-state.json; do
      [ -f "$REEL/$f" ] && cp "$REEL/$f" "$PROJ/film/gate_reports/$(basename "$f")" && echo "copied $f"
    done
    find "$REEL/exports" -name '*.mp4' -exec cp {} "$PROJ/film/" \; -exec echo "copied {}" \;
    cp "$REEL/beat_sheet.json" "$PROJ/film/reel/beat_sheet.json"
    cp "$REEL/beat_sheet.json" "$PROJ/beat_sheet.json" ;;
  *) sed -n '2,10p' "$0"; exit 1 ;;
esac
