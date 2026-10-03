#!/usr/bin/env bash
# build.sh — rebuild this reel end to end, from a clean checkout.
#
#   ./build.sh /path/to/brutalist.art /path/to/info-7375-prompt-engineering-for-generative-ai
#
# Free pipeline only: Kokoro narration, Manim + Remotion rendering, all local,
# no API keys, no paid services, no upload.
set -euo pipefail

REEL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="${1:?usage: ./build.sh <brutalist.art> <course-clone> [python-for-crosscheck]}"
COURSE="${2:?usage: ./build.sh <brutalist.art> <course-clone> [python-for-crosscheck]}"
CROSS="${3:-}"

# 1. evidence — every on-screen number comes from here
if [ -n "$CROSS" ]; then
  python3 "$REEL/evidence/run_evidence.py" --course "$COURSE" --compare "$CROSS"
else
  python3 "$REEL/evidence/run_evidence.py" --course "$COURSE"
fi

# GATE A copies scenes.py alone into a temp dir; this is how it finds the data.
export WEEK01_EVIDENCE="$REEL/evidence/evidence.json"

# 2. audio is the clock
python3 "$TOOLKIT/runtime/scripts/generate_audio_kokoro.py" "$REEL"

# 3. render + compile (Manim 4K, Remotion, conform to audio, QC gates)
"$TOOLKIT/art" run "$REEL"

echo
echo "review cut : $REEL/$(basename "$REEL")-slate.mp4"
echo "master     : run '$TOOLKIT/art final $REEL'"
echo "             -> emits $(basename "$REEL").mp4 ; the submitted copy is that"
echo "                file renamed to Yadav_Shreyash_INFO7375_Week01_Video.mp4"
