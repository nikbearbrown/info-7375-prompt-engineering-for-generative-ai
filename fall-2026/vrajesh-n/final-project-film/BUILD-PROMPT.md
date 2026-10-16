# BUILD-PROMPT — rebuild "Early Bird" from this folder

No API keys, no accounts, no paid services. Cost to rebuild: **$0.00**.

## 0. Environment of record
Windows 11 · Python 3.13.3 · Node 22.15.1 · Remotion 4.0.486 · ffmpeg 9.0.2 · Kokoro `am_onyx` · faster-whisper `base`.
Toolkit: the brutalist.art clone at `../../../../brutalist.art` (commit `519fcbb`) **plus** these local changes:

| File | Change |
|---|---|
| `runtime/remotion/src/EarlyBirdPitch.tsx` | **New.** Ten reel-local compositions: EbOpen, EbWhatItIs, EbProbe, EbAlternatives, EbFirstMinute, EbProves, EbFirstRun, EbRisk, EbWhyMe, EbOutro. A copy is kept in this folder as `toolkit/EarlyBirdPitch.tsx.txt` (stored as .txt: the course CI rejects .tsx files; copy it to `runtime/remotion/src/EarlyBirdPitch.tsx` to use it). |
| `runtime/remotion/src/Root.tsx` | Import plus a `<Folder name="EarlyBirdPitch">` registering the ten compositions; duration from `props.durationSeconds`. |
| (from my Doorman draft, 2026-10-13) `remotion_scenes.py` `npx` via `shutil.which`; `compile.py` filtergraph-escaped font path; `public/fonts/PTMono-Regular.ttf` | Windows fixes the pipeline needs (a bare `npx` is `npx.CMD` on Windows; `C:\` broke ffmpeg's filter parser). |

Set `PYTHONUTF8=1` on Windows.

## 1. Evidence (the only real data in the film)
```bash
cd evidence && python -I probe.py      # writes evidence/<today>/; the film uses 2026-10-14
```

## 2. Beat sheet → narration → timing
```bash
TK=../../../../brutalist.art
python build_beats.py                                   # beat_sheet.json from the spec
python $TK/runtime/scripts/generate_audio_kokoro.py .   # mp3/beat-*.mp3, measured durations
python $TK/runtime/scripts/align.py .                   # mp3/words.json
python build_beats.py --sync                            # durationSeconds + word cues into props
```

## 3. Scenes, review cut, master
```bash
python $TK/runtime/scripts/remotion_scenes.py . --stills   # 25/50/95% preview, read by eye
python $TK/runtime/scripts/remotion_scenes.py .            # media/B00.mp4 … B09.mp4 (3840x2160)
cd $TK && ./art run "<this folder>"                        # review cut + gates
./art final "<this folder>" --height 1080 --fps 30 --out "<this folder>/final"
```

## 4. Prompts that shaped the film (summarised; transcript kept private)
1. "I want to work on this assignment … and create a job search agent for myself."
2. Direction from me: target **software engineer** roles; do **not** skip jobs for skill gaps; keep it small; watch my 25–30 referral and dream companies; show which project fits; order by referral; LinkedIn connections only if allowed (kept local).
3. "Do more research … check that all the questions and answers make sense." → led to naming greenhouse-watch and removing the overstated Jobright line.
4. "Use Kokoro voice … pick public Greenhouse/Lever boards and label them examples. One is Commure."
5. "Start it. Now it's your turn. Go for it." → Claude Code built the beat sheet, scenes and render from the approved script.
