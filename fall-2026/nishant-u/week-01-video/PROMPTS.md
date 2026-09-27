# PROMPTS — week-01-softmax-max-subtraction

## Generation prompts: none

No AI image, video or voice-clone generation was used. No pantry assets, no Higgsfield,
no ElevenLabs, no API keys, no paid calls. Every visual is a deterministic Manim scene in
`manim/scenes.py`; every number on screen comes from `maxsub_runs.py` output or is labelled
as computed / worked by hand (see FACTCHECK.md).

## Build commands (free, local)

```bash
# evidence
python maxsub_runs.py > maxsub_runs.stdout.txt

# narration (Kokoro am_onyx, local) then the 0.8 s inter-beat gaps
python ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py ~/week-01-video
python ~/week-01-video/pad_gaps.py

# visuals — one Manim scene per beat, 4K, copied to manim/<BID>.mp4
cd ~/week-01-video/manim
manim render -r 3840,2160 --fps 24 --media_dir ../_manim_build scenes.py <SceneClass>

# clean 4K master
cd ~/brutalist.art && ./art final ~/week-01-video --out ~/week-01-video
```

Scene classes: B00 TitleCard · B01 OverflowOpen · B02 SoftmaxDefinition · B03 RawPath ·
B04 ShiftedPathSideBySide · B05 ShiftInvariance · B06 OverflowVsShifted · B06B GapNotSize ·
B07 LastDigit · B08 Limits.
