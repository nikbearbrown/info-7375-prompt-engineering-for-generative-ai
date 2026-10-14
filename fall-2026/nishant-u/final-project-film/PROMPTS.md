# PROMPTS — final-project-pitch-nishant-u

## Generation prompts: none

No AI image, video or voice-clone generation is used. No pantry assets, no Higgsfield, no API keys, no
paid calls. Narration is local Kokoro (`am_michael`). Every visual will be a deterministic Manim scene in
`manim/scenes.py` (not written yet) or one of two Remotion bookends rendered by the toolkit
(`BrutalistHesitantWriter`, `ClaudeDefinitions`). No logos are drawn.

## Build commands (free, local)

```bash
# beat sheet (narration lives in make_sheet.py NARRATION; durations carry forward while it is unchanged)
python make_sheet.py

# narration (Kokoro am_michael, local); after editing one beat's line, re-voice only that beat
python ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py <this folder>
python ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py <this folder> --only <BID>

# review cut (Gates A, W, B, V), then the clean 4K master (Gate T, then render-integrity + Gate V)
cd ~/brutalist.art
PYTHONUTF8=1 ./art run   <this folder> --height 2160
PYTHONUTF8=1 ./art final <this folder> --height 2160 --out <this folder>/exports/landscape
```

Scene classes: B00_Agent · B01_Repo · B02_Alerts · B03_Jobright · B04_ThreeWays · B05_SixtySeconds ·
B06_Proves · B07_Evidence · B08_OutFirst · B09_Risk · B10_Skills · B11_ExistsWill · BEND_Close.
