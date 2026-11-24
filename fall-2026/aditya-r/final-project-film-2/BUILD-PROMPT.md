# BUILD-PROMPT — how this film was made and how to rebuild it

## Prompts

The film was built in one Claude Code session on 2026-11-23. Aditya's requests, in order:

1. "Based on your analysis, what is the use case for this particular repository?" (about the
   Frictional repo).
2. Shared the October film, the October rubric and the new four-part rubric, and asked Claude
   to propose a plan for the new film, including whether a delegation contract and a
   custom-trained Hugging Face model fit the project, and to wait for approval.
3. Answered Claude's questions: keep the name DayThread; due Monday 23:30, so finish and upload
   tonight; Kokoro voice again, about the same length; use the recommended checker. Asked Claude to
   build the film with the local Brutalist toolkit, and to post to GitHub and Canvas only after
   Aditya has watched and approved it.

## Rebuild

Toolchain (macOS arm64):
- brutalist.art at `519fcbb`;
- conda env `brutalist-daythread` (Python 3.12.14, Manim 0.20.1, kokoro-onnx 0.6.1,
  faster-whisper 1.2.1, Pillow);
- FFmpeg; MacTeX; EB Garamond.

Put `source/` contents in a reel folder, with `SCRIPT.md` one level above it:

```bash
eval "$(/usr/libexec/path_helper)" && export PATH="/opt/anaconda3/envs/brutalist-daythread/bin:/opt/homebrew/bin:$PATH"
REEL=~/Desktop/Brutalist/my-videos/youtube/daythread-final/film
cd $REEL
python make_sheet.py                    # beat_sheet.json from ../SCRIPT.md
# Narration (the MP3s are in the Canvas ZIP only). From GitHub alone, regenerate:
python ~/Desktop/Brutalist/brutalist.art/runtime/scripts/generate_audio_kokoro.py .
# BOUT reuses the October film's raw audio for the identical line; copy it to mp3/raw/beat-BOUT.mp3 first
python audio_post.py                    # pads BOUT, measures beats, stores word timings
python assemble_scenes.py               # scenes.py = iso_kit + 11 props (verbatim) + scenes_body.py
cd ~/Desktop/Brutalist
./brutalist.art/art run   "$REEL" --height 2160                        # Gates F, L, A, W, B, V + review cut
./brutalist.art/art final "$REEL" --height 2160 --out "$REEL/exports"  # GATE T + verified 4K master
cd "$REEL" && python final_checks.py    # probe, transcript, frame sheets, bookend_check -> checks/
```

Kokoro output can vary slightly between runs, so a rebuild may differ in timing by fractions of
a second. The checksum below is for the submitted master only.
