#!/usr/bin/env bash
# Builds the pitch film: animated scenes (clips/B00.mp4 ... B09.mp4) + narration.
#
#   bash make_film.sh Gaikar            -> makes the AI voice with macOS `say` from RECORDING-SCRIPT.txt, then builds
#   bash make_film.sh Gaikar myvoice    -> uses your own recordings in audio/B00.m4a ... B09.m4a instead
#
# Change the voice:  VOICE=Daniel bash make_film.sh Gaikar      (list voices: say -v '?' | grep en_)
# Needs ffmpeg (Mac: brew install ffmpeg)
set -e
NAME="${1:-LastName}"
MODE="${2:-ai}"
VOICE="${VOICE:-Samantha}"
RATE="${RATE:-180}"
mkdir -p build audio
: > build/list.txt
for clip in clips/B*.mp4; do
  id=$(basename "$clip" .mp4)
  if [ "$MODE" = "ai" ]; then
    awk -v b="$id" 'index($0,"=== audio/" b " "){getline; print; exit}' RECORDING-SCRIPT.txt > "build/$id.txt"
    say -v "$VOICE" -r "$RATE" -f "build/$id.txt" -o "audio/$id.aiff"
    a="audio/$id.aiff"
  else
    a=$(ls audio/"$id".* 2>/dev/null | grep -v '\.aiff$' | head -1)
    [ -z "$a" ] && a=$(ls audio/"$id".* 2>/dev/null | head -1)
    if [ -z "$a" ]; then echo "Missing recording for $id (put it in audio/$id.m4a)"; exit 1; fi
  fi
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$a")
  cdur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")
  total=$(awk -v d="$dur" 'BEGIN{printf "%.2f", d+0.8}')
  # stretch the scene so its drawings and subtitles line up with the real narration length
  factor=$(awk -v d="$dur" -v c="$cdur" 'BEGIN{printf "%.4f", d/c}')
  ffmpeg -y -loglevel error -i "$clip" -i "$a" \
    -filter_complex "[0:v]setpts=PTS*${factor},fps=24,tpad=stop_mode=clone:stop_duration=600[v];[1:a]aresample=48000,apad=pad_dur=0.8[a]" \
    -map "[v]" -map "[a]" -t "$total" -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -ac 2 "build/$id.mp4"
  echo "file '$id.mp4'" >> build/list.txt
  echo "built $id ($(printf %.0f "$dur") s of narration)"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i build/list.txt -c copy "${NAME}_pitch.mp4"
echo "Done: ${NAME}_pitch.mp4  runtime: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "${NAME}_pitch.mp4" | cut -d. -f1) seconds"
