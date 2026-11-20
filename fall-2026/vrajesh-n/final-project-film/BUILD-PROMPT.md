# BUILD-PROMPT — rebuild "Early Bird" (v1.0) from this folder

No API keys, no accounts, no paid services. Cost to rebuild: **$0.00**.

## 0. Environment of record (2026-10-24)
Windows 11 · Python 3.13.3 · Node 22.15.1 · Remotion 4.0.535 · ffmpeg 9.0.2 · Kokoro `am_onyx` · faster-whisper `base`.
Toolkit: the brutalist.art clone at `../../../../brutalist.art` (commit `519fcbb`) **plus** these local changes:

| File | Change |
|---|---|
| `runtime/remotion/src/EarlyBirdFilm.tsx` | **New (v1.0).** Ten reel-local compositions: EfOpen, EfWhat, EfExists, EfAlternative, EfWho, EfProves, EfScope, EfRisk, EfWhyMe, EfOutro. Copy kept here as `toolkit/EarlyBirdFilm.tsx.txt` (course CI rejects .tsx; copy it back to `runtime/remotion/src/EarlyBirdFilm.tsx`). |
| `runtime/remotion/src/Root.tsx` | Import plus a `<Folder name="EarlyBirdFilm">` registering the ten compositions; duration from `props.durationSeconds`. (The v0.2 `EarlyBirdPitch` folder is still registered; the v1.0 beat sheet does not use it.) |
| `runtime/qc/final_frame_check.py` | **New (2026-10-25).** `TIMECODE_EXCLUDE` box (top-right 20% × 4.5%) ignored like the existing burn-in strip: the review cut's drawtext timecode otherwise fails GATE V edge-bleed on every frame. |
| (from 2026-10-13) `remotion_scenes.py` `npx` via `shutil.which`; `compile.py` filtergraph-escaped font path; `public/fonts/PTMono-Regular.ttf` | Windows fixes the pipeline needs. |

Set `PYTHONUTF8=1` on Windows.

## 1. Evidence (the only real data in the film)
```bash
# a) board snapshots (one per day; the film uses 2026-10-14 and 2026-10-23)
cd evidence && python -I probe.py                 # writes evidence/<today>/

# b) new-ID diff, run from vrajesh-n/ (output: evidence/commure-new-ids-2026-10-14_to_2026-10-23.txt)
python -X utf8 -c "import json;L=lambda d:{j['id']:j['title'] for j in json.load(open(f'js1-contract-and-watch/data/raw/{d}/ashby_commure.json',encoding='utf-8'))['jobs']};a,b=L('2026-10-14'),L('2026-10-23');n=[b[i] for i in b if i not in a];print(len(a),len(b),'new:',len(n),'gone:',len(set(a)-set(b)));print(*n,sep='\n')"

# c) greenhouse-watch on the same two files, run from the-reallocation-engine/ (output: evidence/gw/)
F=<path to vrajesh-n>
for d in 2026-10-14 2026-10-23; do python -I .claude/skills/greenhouse-watch/scripts/greenhouse_watch.py \
  --ats ashby --board commure --resume search/examples/aarav-patel/resume.example.json \
  --state "$F/final-project-film/evidence/gw/state.json" --out "$F/final-project-film/evidence/gw/$d" \
  --fixture "$F/js1-contract-and-watch/data/raw/$d/ashby_commure.json"; done
```
Delete `evidence/gw/state.json` first to repeat (c) from a fresh baseline.

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
python $TK/runtime/scripts/remotion_scenes.py .            # media/B00.mp4 … B09.mp4 (3840x2160); existing files are skipped
cd $TK && ./art run "<this folder>"                        # review cut + gates
./art final "<this folder>" --height 1080 --fps 30 --out "<this folder>/final"
```

## 4. Prompts that shaped v1.0 (summarised; transcript kept private)
1. I pasted the grader's feedback: "So I want to recreate it."
2. "You have to regenerate from scratch" → I chose: full new film; I run the diff and greenhouse-watch myself; keep the Kokoro voice; script v1.0 approved as written.
3. Claude built the beat sheet, scenes, narration, render and gates from the approved script, then cut B03/B06/B07 for length and corrected B02 after a department check (both logged in FRICTIONAL.md and FACTCHECK.md).

The v0.2 prompts (2026-10-14) are in git history (`213233b`).
