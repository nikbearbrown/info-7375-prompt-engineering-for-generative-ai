# BUILD-PROMPT — how to rebuild this film

Everything is free and local: no API keys, no paid generation, no upload.

## 1. Toolkit (one time)

```bash
git clone https://github.com/nikbearbrown/brutalist.art Brutalist     # built against commit 519fcbb
cd Brutalist
python3.11 -m venv .venv && source .venv/bin/activate              # macOS system python3 (3.9) lacks the deps
pip install -r requirements.txt                                     # Manim 0.20.x pinned
./art smoke                                                         # end-to-end proof that a video renders
```

Put this folder beside the toolkit (`Final_Project_Film/` next to `Brutalist/`), or set `ART_HOME` to the toolkit.

## 2. The recorded evidence (`first-run/`)

The film typesets `first-run/results/2026-10-25/` (the hand rounds; `$RESULTS` overrides it) and the newest live loop
run in `first-run/loop-runs/` (`$LOOP` overrides it), both chosen in `film/embed_recorded.py`. To re-create them:

```bash
cd first-run
./run_all.sh            # downloads NYC TLC Jan 2025, makes the clean sample, runs pandera + dbt + GX Core
./score_round.sh 1      # plants the five defect types (seeds 25, 99), scores the baseline and Claude's round 1
./score_round.sh 2      # Claude's round 2
./run_loop.sh           # the loop: tests first, then up to 3 rounds with Claude Code headless (your logged-in subscription)
.venv/bin/python heldout_clean.py loop-runs/<run>/round3/checks.py loop-round3 loop-runs/<run>/round3   # second clean copy
```

`./run_loop.sh --fixture claude-checks` replays the saved hand-run replies instead of calling Claude (no login).

Claude's checks come from pasting `claude-checks/PROMPT-round1.md` (then `PROMPT-round2.md`) unchanged into a new
Claude desktop-app chat; the replies are saved verbatim as `claude-checks/round*-reply-<date>.md`.

## 3. Film (from `Final_Project_Film/film/`)

```bash
source ../../Brutalist/.venv/bin/activate
T=../../Brutalist

python make_sheet.py                                         # beat_sheet.json from the narration + visual plan
python $T/runtime/scripts/generate_audio_kokoro.py .         # narration first: the measured mp3s are the clock
python finish_audio.py                                       # 0.8 s lead on BIDEA, 1.0 s tail on BEND; re-measure
./build_scenes.sh                                            # scenes.py = iso_kit + props + recorded output + scenes_body.py
cd $T && ./art run   ../Final_Project_Film/film              # Gates F, L, A, W, B; 4K renders; review cut; Gate V
         ./art final ../Final_Project_Film/film --out ../Final_Project_Film/film/exports   # Gate T + verified master
```

Subtitles (after `art final`, from `film/`):

```bash
python $T/runtime/scripts/align.py .                 # word clock from the known narration
python make_captions.py                              # ../DataSentry_ProjectFilm_EthanGomes.srt + .vtt, all words kept
python $T/runtime/scripts/srt_check.py . --srt datasentry-project-film.srt
ffmpeg -i exports/datasentry-project-film.mp4 -i ../DataSentry_ProjectFilm_EthanGomes.srt -map 0:v -map 0:a -map 1:0 \
  -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng -disposition:s:0 default \
  -movflags +faststart ../DataSentry_ProjectFilm_EthanGomes.mp4   # soft track; picture and sound are stream-copied
```

Re-voicing one beat: `generate_audio_kokoro.py . --only B07` then `python finish_audio.py`.
Re-rendering one scene: edit `scenes_body.py`, run `./build_scenes.sh`, move `manim/<BID>.mp4` (and `media/videos/`)
aside, then `./art run` again.

## 4. The prompts (Claude Code, model Opus 5.5, 2026-11-23)

1. *"This is my next assignment:"* followed by the assignment text (four parts: executive summary, introduction,
   methods, evaluation) — *"Go through this and let me know what needs to be done"*
2. *"Create a new folder and make the video for this assignment using Brutalist library. It is the same project.
   Length is 4 mins. Free claude subscription. This is the whole assignment requirements which i pasted. Start
   building the video"*
3. *"Consider the feedback given and tell me if changes need to be made"* (the TA's pitch grading) — then *"Make this
   change first"*: build the loop that feeds the clean-copy false alarms back automatically.
4. I ran `./run_loop.sh` in my own terminal (2026-11-23 18:24) and pasted the output.
5. *"also go through these requirements for the final project submission … Will this project be able to satisfy all
   these requirements?"* then *"any suggestions for any changes that should be made in this project and the project
   film considering the final project requirements?"*
6. *"Out of all these changes, which need to be made now for the final project video submission? … is this agentic
   enough …?"* then *"Made these changes"* (the film's agent framing, the tools-and-permissions beat, the human-gate
   beat, the held-out data and planned failure cases; mutation testing folded into the grid).

Claude Code's working rules came from the toolkit's `CLAUDE.md` and `skills/make/show-tell/SKILL.md`, with the course's
rules kept from the pitch: narrate as yourself, no instructor name, persona or credit line, and the honesty rule
(past tense only for what ran).
