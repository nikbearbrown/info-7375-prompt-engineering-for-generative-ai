#!/usr/bin/env bash
# Rebuild the narration from the script: beat sheet -> Kokoro am_eric -> pad bookends -> measure.
# Usage: bash build_audio.sh   (from final-project-film/, toolkit venv active; see BUILD-PROMPT.md)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$HERE"
ART_HOME="${ART_HOME:-$HERE/../brutalist.art}"
python3 make_sheet.py
rm -f mp3/*-unpad.mp3                     # finish_audio.py re-pads BIDEA/BOUT from fresh raw audio
python3 "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" "$HERE"
python3 name_voice.py "$ART_HOME"           # my name, from my Devanagari pronunciation guide (BIDEA, BOUT)
python3 finish_audio.py
