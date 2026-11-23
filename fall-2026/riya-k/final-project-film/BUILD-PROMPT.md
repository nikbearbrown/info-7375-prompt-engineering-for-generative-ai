# BUILD-PROMPT

How this film and its evidence were built, in the order it happened: v1 on 2026-10-09, the v2
redo on 2026-10-19, and the resubmission changes on 2026-10-21 (Stages 5 and 6 at the end). Every
command below was actually run on macOS 14 (Darwin 23.6.0, Apple Silicon).

## Environment

| Component | Version | Note |
|---|---|---|
| Python (toolkit venv) | 3.11.14 (Homebrew) | Manim 0.18 requires `<3.13` |
| Python (evidence) | system `python3`, standard library only | `run_slice.py` needs no packages |
| Manim Community | 0.18.1 | no LaTeX needed |
| Kokoro TTS | voice `af_bella` | local, free |
| brutalist.art | `22264a332f6bf8825cdd639bcd33864563801f55` | show-tell skill |
| Font | EB Garamond (OFL), from `brutalist.art/runtime/fonts/EB_Garamond/static/` | had to be copied to `~/Library/Fonts`, see FRICTIONAL.md |

## Stage 1: evidence before script

```bash
cd evidence
mkdir -p data && cd data
curl -fsSL -o Chinook_Sqlite.sqlite https://github.com/lerocha/chinook-database/releases/download/v1.4.5/Chinook_Sqlite.sqlite
curl -fsSL -o CHINOOK-LICENSE.md https://raw.githubusercontent.com/lerocha/chinook-database/master/LICENSE.md
shasum -a 256 Chinook_Sqlite.sqlite   # bdf635be69850bd3be09c9a2dbeef7ddfb80036bd3ef3381383cd03b61e4a61a
cd ..
python3 -I run_slice.py | tee run_slice_output.txt     # prints 9/9, exits 0
```

`run_slice_output_v0_first_run.txt` is the first run (8/9), before the Q08 gold fix. It is
kept on purpose. It cannot be regenerated from the current `gold_set.json`. The v0 Q08 used
`'2023'` in both queries, and the `note` field in `gold_set.json` records what changed.

**Prompt used (to Claude Code):**
> Build the first runnable slice of a text-to-SQL evaluation harness over the public Chinook
> SQLite database: about 8 questions with gold SQL, plus hand-written variants, some
> equivalent (different SQL, same answer) and some plausible wrong queries, each labelled with
> its mistake. Write a stdlib-only runner that executes everything read-only, judges each
> variant by comparing result rows (not SQL text), and also reports what exact-string
> matching would have said. Do not call any model. Nothing here may be presented as model output.

## Stage 2: brief and beat sheet

**Prompt used:**
> Write PROJECT-BRIEF.md answering the assignment's seven questions for this project, framed for
> AI Engineer roles. Past tense only for what exists in evidence/; everything else "will".
> Name BIRD and Vanna as alternatives, using only what their own pages say. End with
> "Exists today" and "Will exist" lists. Then turn it into a show-tell beat sheet: one drawn
> picture per beat, narrated in the first person as me with Kokoro af_bella, no instructor
> name/persona/credit line, a conclusion beat before the outro, 2–4 minutes.

```bash
# in the reel folder (built outside the toolkit, as its CLAUDE.md requires)
python3 make_sheet.py                                            # -> beat_sheet.json
~/Documents/INFO7375/brutalist.art/.venv/bin/python \
  ~/Documents/INFO7375/brutalist.art/runtime/scripts/generate_audio_kokoro.py .   # audio = the clock
```

First pass measured 257.8 s, over the limit. The narration was cut and re-voiced to 233.1 s.

## Stage 3: drawings and render

`scenes.py` = `iso_kit.py` + `iso_originals_25.py` pasted at the top (Gate A copies only
`scenes.py`), then one `class BNN_Name(Scene)` per body beat. Every scene lands its labels
by 40% of the beat and holds still until 58%, so nothing is mid-motion at the 50% frame that
GATE T and Gate V sample.

```bash
cd ~/Documents/INFO7375/brutalist.art
export PATH="$PWD/.venv/bin:$PATH"
./art run   <reel>      # Gates F, L, A, W, then render + compile the review cut
./art final <reel>      # GATE T type check, then the clean master
```

## Stage 4: checks

- Whisper transcript of the key beats (`faster_whisper`, `base.en`) to catch mispronunciations.
- The toolkit's gate reports, copied into `gate-reports/`.
- Watching the cut end to end. See FRICTIONAL.md for what that found.

## Stage 5: v2 redo (2026-10-19)

The instructor's feedback on v1: the problem was not clear, the animations were weak, and there
were no examples. I also asked for burned-in captions, plain language, where it will be used, a
title card with my name, a female voice and a real conclusion.

**Prompt used (to Claude Code, summarised):**
> Redo the pitch film from the instructor's feedback: open by showing the problem with one real
> wrong number, explain it with one real invoice, give more real examples, explain why it happens
> in real life, then the tool, who it helps and where it will be used. Simple everyday words,
> SQL explained once. Animate every beat. Burn in captions. Under 4:00.

```bash
cd ~/Documents/INFO7375/films/riya-k-ground-truth-sql-v2        # the reel (copied into reel/)
python3 make_sheet.py                                            # -> beat_sheet.json
cat _kit_header.py _body.py > scenes.py                          # Gate A reads scenes.py alone
~/Documents/INFO7375/brutalist.art/.venv/bin/python \
  ~/Documents/INFO7375/brutalist.art/runtime/scripts/generate_audio_kokoro.py .
cd ~/Documents/INFO7375/brutalist.art && export PATH="$PWD/.venv/bin:$PATH"
./art run   ~/Documents/INFO7375/films/riya-k-ground-truth-sql-v2
./art final ~/Documents/INFO7375/films/riya-k-ground-truth-sql-v2
```

## Stage 6: resubmission changes (2026-10-21)

From the TA's feedback on the 2026-10-14 submission: try Vanna on Chinook, say "drafted with
Claude, checked by me" instead of "hand-written", and run Claude on the eight questions with the
raw output saved and dated.

```bash
# Vanna, in its own venv (not part of the course stack; comparison only)
python3.11 -m venv ~/Documents/INFO7375/vanna-venv
~/Documents/INFO7375/vanna-venv/bin/pip install vanna          # 2.0.2
cd evidence
~/Documents/INFO7375/vanna-venv/bin/python vanna_check.py       # Vanna's OutputEvaluator: PASS on 4,667.06; rows: FAIL

# Claude: three Claude Code subagents, each given only claude_runs/2026-10-21/prompt.txt
# (schema + 8 questions, no tools, no gold); replies saved unedited as run1-3_raw.json
python3 score_claude_runs.py > claude_runs/2026-10-21/score_output.txt   # 22/24 by rows, 0/24 by text
```

Film: B03, B06, B10, B11, B13 and B15 re-narrated, and B02's on-screen tag changed, so the film
matches the evidence. B01 and B05 were trimmed to stay under 4:00. Re-voiced with Kokoro, word
timings re-taken with faster-whisper (`reel/_qc/make_word_timings.py`), changed scenes
re-rendered, the same `./art run` / `./art final` gates, then `python3 burn_captions.py <master> <out>`.
Later the same day: B13's classmate line became "every answer is checked a second way"
(`evidence/cross_check.py`), B06 got Riya's own terminal screenshot, and the still window around each
beat's midpoint was narrowed from 40–58% to 47–53% (the gates sample only the 50% frame) so labels
land on the spoken word. GATE T then read dark box edges touching g/p descenders as overlapping text
in B03 and B08; those boxes got grey edges and a little more padding. All 15 beats re-rendered.

Then Riya watched the cut and listed changes, made in one batch: "Reno" → "Reno, Nevada" (B03);
opening headings so no beat starts on an empty screen (B04, B05, B06, B11, B15); "9 test queries"
explained (B09); the questions and database named, and Q02's question shown (B10); the old B13 split
into scope (B13) and risk (B14); separate "today" and "next" rows and a new closing line, "Running SQL
is easy. Being right is the test." (B16). Two phrases were trimmed to stay under 4:00.



## Stage 7: four-part final cut, v4 (2026-11-22 to 2026-11-23)

Instructions to Claude Code: the reposted Final Project Film brief (four parts in order:
executive summary, introduction, methods, evaluation), pasted by me. Claude read the v3 reel,
mapped its beats onto the four parts, and drafted `reel/SCRIPT-v4-four-parts.md`. My answers
before the build: Claude access = my Claude Code plan; pass bar = keep the draft; script = build it.
My notes after watching the first cut: add a line from "AI data assistant" to the report card
(B05); make the ending sound like a conclusion (B20). Then "okay now its good".

```bash
cp -R films/riya-k-ground-truth-sql-v2 films/riya-k-ground-truth-sql-v4   # v3 reel, kept intact
cd films/riya-k-ground-truth-sql-v4
python3 make_sheet.py && cat _kit_header.py _body.py > scenes.py         # 20 beats
source <brutalist.art>/.venv/bin/activate
python3 <brutalist.art>/runtime/scripts/generate_audio_kokoro.py .        # must come before ./art run
python3 <brutalist.art>/runtime/qc/manim_layout_audit.py scenes.py --class <Scene> --curve-strict   # pre-audit each scene
cd <brutalist.art> && ./art run <reel> && ./art final <reel>
python3 <reel>/burn_captions.py renders/riya-k-ground-truth-sql-v4.mp4 <out>.mp4
# re-renders after fixes: move manim/BNN.mp4 aside, then ./art run again (it skips filled beats)
python3 <brutalist.art>/runtime/scripts/generate_audio_kokoro.py <reel> --only B20   # after the B20 wording change
```

Word timings for captions: faster-whisper `base.en`, `word_timestamps=True`, on each `mp3/beat-BNN.mp3`.
What went wrong on the way is in FRICTIONAL.md.
