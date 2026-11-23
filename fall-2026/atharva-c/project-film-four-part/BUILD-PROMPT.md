# BUILD-PROMPT — how to rebuild the film

Free pipeline only: Kokoro narration and Manim/ffmpeg rendering run locally. No API keys, no paid generation, no upload.

## 1. Toolkit (same install as the pitch film)
```bash
git clone https://github.com/nikbearbrown/brutalist.art ~/Applications/brutalist.art
cd ~/Applications/brutalist.art && git checkout b21f625
python3 -m venv .venv && source .venv/bin/activate && ./setup --install
```
At b21f625, `./setup` exits at its ElevenLabs guard (see the pitch film's FRICTIONAL.md, 2026-10-10); readiness is confirmed with `python3 runtime/scripts/setup_smoke_kokoro.py` and `./art --list`. Run everything below with that `.venv` active.

## 2. Beat sheet and build folder (outside the repo, so audio and render caches stay out of git)
```bash
python3 film-source/write_beat_sheet.py          # writes beat_sheet.json from the locked narration
B=~/Projects/seeded-faults-film-build/seeded-faults-project && mkdir -p $B
cp film-source/{scenes.py,make_sheet.py,FACTCHECK.md,SHOTLIST.md,PROMPTS.md} $B/
python3 $B/make_sheet.py                          # builds the toolkit's beat sheet from ./beat_sheet.json
```

## 3. Narration (Kokoro am_michael)
```bash
python3 runtime/scripts/generate_audio_kokoro.py $B
ffmpeg -y -i $B/mp3/beat-BOUT.mp3 -af "apad=pad_dur=1.0" -c:a libmp3lame -q:a 2 /tmp/bout.mp3 && mv /tmp/bout.mp3 $B/mp3/beat-BOUT.mp3
# then set BOUT's actual_duration_s in $B/beat_sheet.json to the padded length (3.18 s)
```
Pronunciation was checked with faster-whisper (base.en) on every beat. Whisper hears "Seeded" as "Seated", the same as on the approved pitch audio, so it was left as is.

## 4. Render and gates
```bash
./art run   $B --height 1080                                # Gates F, A, W, B, then V on the review cut
./art final $B --height 2160 --out $B/exports/landscape      # GATE T, then the verified master
python3 runtime/qc/factcheck_check.py $B
```

## Evidence scripts
The scripts in `evidence/` read the NYC TLC files from `~/Projects/seeded-faults-sandbox/` (override with `SEEDED_FAULTS_SANDBOX=/path`). They need pandas, pyarrow and pandera 0.36.0. Each folder's `output*.txt` is the recorded run.

## Prompts given to Claude Code (summarised; full conversation not included)
1. 2026-11-22: here is Professor Bear's four-part email and my submitted pitch film; do I make a new film?
2. 2026-11-22: verify the prior-work claims (Deequ, pandera, Great Expectations, mutation testing).
3. 2026-11-22: here is my TA's feedback on the pitch; review my FRICTIONAL entry and fault catalogue without rewriting them.
4. 2026-11-22: "Locked, build it". Fill the script from my locked catalogue, write the beat sheet, build the film, run the gates.
