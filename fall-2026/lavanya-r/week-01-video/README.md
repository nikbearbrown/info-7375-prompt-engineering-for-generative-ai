# Lavanya Rajesh

Public work for INFO 7375, Fall 2026.

## Week 1 Video: Claude, Seeded?

I chose the concept **"A seed makes a run repeatable; it does not make the answer true"** because I've been caught by this mistake myself — I've trusted a reproducible result as if reproducibility alone made it correct, and this concept is exactly why that reasoning fails.

**Runtime:** 3:01.583.

### Rebuild

The video source record is in [`week-01-video/`](week-01-video/). Rendering requires a separate checkout of `brutalist.art`; this course folder alone does not include its rendering tools. Place this folder in that checkout as `youtube/claude-hai-seed-repeatable/`, then run the build from the `brutalist.art` checkout root:

```bash
python3 runtime/scripts/generate_audio_kokoro.py youtube/claude-hai-seed-repeatable --speed 1.0
python3 runtime/scripts/remotion_scenes.py youtube/claude-hai-seed-repeatable
./art run youtube/claude-hai-seed-repeatable
./art todo youtube/claude-hai-seed-repeatable
```

Review and resolve any missing media, then follow the quality-control steps in [`week-01-video/BUILD-PROMPT.md`](week-01-video/BUILD-PROMPT.md). After fixing any blockers or major defects, render the final video with:

```bash
./art final youtube/claude-hai-seed-repeatable
python3 runtime/scripts/captions.py youtube/claude-hai-seed-repeatable --master claude-hai-seed-repeatable-final.mp4
```

This produces `claude-hai-seed-repeatable-captioned.mp4`, the submitted video file.

The narration uses the local Kokoro engine with voice `af_bella`. Rebuilds should use the beat sheet, source notes, and checks in `week-01-video/`; do not publish or upload as part of the rebuild.