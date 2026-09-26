#!/usr/bin/env bash
# build.sh -- INFO 7375 Week 01 Explainer Video (Swathi Baba Eswarappa)
# Rebuilds the whole video from scratch. Audio is the master clock.
#
#   ./build.sh            full rebuild (probe -> audio -> scenes -> mux)
#   ./build.sh --mux-only skip probe/audio/render, just re-mux
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

ART_HOME="${ART_HOME:-$HERE/../brutalist.art}"
VENV="${VENV:-$HERE/../.venv-kokoro}"
OUT="BabaEswarappa_Swathi_INFO7375_Week01_Video.mp4"
GAP=0.30                      # seconds of black between beats

export ART_HOME
export PHONEMIZER_ESPEAK_LIBRARY="${PHONEMIZER_ESPEAK_LIBRARY:-/opt/homebrew/lib/libespeak-ng.dylib}"
export ESPEAK_DATA_PATH="${ESPEAK_DATA_PATH:-/opt/homebrew/share/espeak-ng-data}"

SCENES=(B01_Hook B02_Claim B03_Tokenize B04_Indices B05_Embedding
        B06_TokenizerDependence B06B_Frequency B07_Banana B08_SpacedControl
        B09_Boundary B10_Close)

if [[ "${1:-}" != "--mux-only" ]]; then
  echo "==> [1/5] tokenizer probes (real numbers)"
  python3 code/tokenize_probe.py  > code/token_probe_output.txt
  python3 code/embedding_probe.py > code/embedding_probe_output.txt

  echo "==> [2/5] Kokoro narration (local, free)"
  "$VENV/bin/python" "$ART_HOME/runtime/scripts/generate_audio_kokoro.py" .

  echo "==> [3/5] Manim scenes @1080p60"
  for S in "${SCENES[@]}"; do
    echo "    - $S"
    manim -qh --disable_caching scene.py "$S" > "build/render_$S.log" 2>&1
  done
fi

echo "==> [4/5] frame-safety sweep (no content in the outer border)"
python3 qc_frames.py --border 16 --step 8

echo "==> [5/5] mux + concat"
python3 build_mux.py --gap "$GAP" --out "$OUT"

echo
echo "==> done: $OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
