#!/usr/bin/env bash
# build.sh — rebuild this pitch film end to end.
#
#   ./build.sh /path/to/brutalist.art
#
# Free pipeline only: Kokoro narration, Manim + Remotion rendering, all local,
# no API keys, no paid services, no upload.
set -euo pipefail

REEL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="$(cd "${1:?usage: ./build.sh <brutalist.art>}" && pwd)"

# The toolkit's static gate copies scenes.py alone into a temp dir; this is how
# the scenes find beat_sheet.json (timing) and the Dovetail evidence file.
export CLAIMCHECK_REEL="$REEL"

# 1. audio is the clock
python3 "$TOOLKIT/runtime/scripts/generate_audio_kokoro.py" "$REEL"

# 2. render + compile with the toolkit's quality gates
"$TOOLKIT/art" run "$REEL"

# 3. clean master, written into this folder
"$TOOLKIT/art" final "$REEL" --out "$REEL"

echo "master: $REEL/$(basename "$REEL").mp4"
echo "submitted copy: that file renamed to Yadav_Shreyash_INFO7375_FinalProjectFilm.mp4"
