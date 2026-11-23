# Ground Truth SQL — final project film

**Riya Kapadnis** · `kapadnis.ri@northeastern.edu`
INFO 7375 — Prompt Engineering for Generative AI · Final Project Film · **four-part cut (v4), 2026-11-23**

| | |
|---|---|
| **Working title** | Ground Truth SQL: a test for AI data assistants (text-to-SQL evaluation harness) |
| **Target role** | AI Engineer (also readable for Data Analyst roles) |
| **Runtime** | **4:35 (274.9 s)** · 3840×2160 · 24 fps · 20 beats in four parts · burned-in captions |
| **Film** | [`riya-k-ground-truth-sql-v4.mp4`](riya-k-ground-truth-sql-v4.mp4), in this folder and in the Canvas zip (sha256 `e3f13e1f…`). It is the verified master (`gate-reports/verified.json`, sha256 `96461113…`) with captions burned in by `reel/burn_captions.py`. The root `.gitignore` excludes `*.mp4`, so it was added with `git add -f` |
| **Narration** | Written in the first person as me; voiced by a **synthetic** local voice (Kokoro `af_bella`), not a recording of my voice |
| **Cost** | $0.00. Kokoro, Manim, FFmpeg and faster-whisper, all local. Claude through my Claude Code access; no API key, no extra token credits |
| **Detail** | [`APPENDIX.md`](APPENDIX.md): prior work, data, steps, resources, scope, risks, evaluation criteria |

## The four parts

The final brief fixes the structure: executive summary, introduction, methods, evaluation, in
that order. The first beat of each part opens on a "Part N of 4" card with the part's name.

| Part | Beats | Time | On screen |
|---|---|---|---|
| **1. Executive summary**: what and why, no "how" | B01–B05 | 0:00–1:14 | Title and my name; a real wrong answer (USA $4,667 vs $523, no error); why it matters; what I'm building; who uses it |
| **2. Introduction**: what others have done | B06–B08 | 1:14–2:01 | BIRD (12,751 questions, 95 databases; people 93%, best AI lower; not your data); Vanna (my run: its own check **passed** the $4,667 answer); the gap |
| **3. Methods**: how I'll build it | B09–B15 | 2:01–3:18 | Chinook data (11 tables, 59 customers, 412 orders, 2009–2013); step 1 answer key + second check; step 2 Claude answers 3×, read-only; step 3 judge by results; step 4 report card by cause; what I need (laptop, Python, the free database, Claude Code; no cloud, no extra credits); scope |
| **4. Evaluation**: how I'll know it worked | B16–B20 | 3:18–4:35 | Checker vs hand labels (wording 6/9, results 9/9); first Claude run 22/24, both fails a tie in my question; the empty-answer bug it caught; the pass bar (worked if / didn't work if); conclusion |

## What changed since the pitch film (resubmission `b3825df`, 2026-10-22)

| Change | Why | Where |
|---|---|---|
| Re-cut into the four required parts, with part cards | The final brief now fixes the structure; the pitch film followed the earlier seven questions | the film, `reel/` |
| New Introduction: BIRD's human vs. AI scores, the gap | The brief asks what others got, not only what they built | B06, B08, APPENDIX §2 |
| New Methods: data, the four steps, resources, scope | The brief asks where the data comes from, step by step, and whether I have the credits, accounts and compute | B09–B15, APPENDIX §3 |
| New Evaluation pass bar: what result means it worked, and what means it didn't | The brief asks for both | B19, APPENDIX §4 |
| "How it works" moved out of the opening minute | The brief keeps the how out of the executive summary | B04 |
| Dropped "who looks first" and "why this project" | Not part of the four parts | — |
| After my review: a line from "AI data assistant" to the report card; a clearer conclusion ("In conclusion" / "So the takeaway is this") | My notes on the first v4 cut | B05, B20 |

The evidence is unchanged from the resubmission: no new model runs were made for this cut.

## What exists today

`evidence/run_slice.py` checks 8 gold questions over the public Chinook database and an
execution comparator on 9 variants (drafted with Claude, labels checked by me): 9/9.
`evidence/score_claude_runs.py` replays the three saved Claude runs offline: 22/24.
`evidence/cross_check.py` recomputes every gold answer in plain Python: 8/8 agree.
Everything else (about 50 harder questions, a direct Claude runner, the report card) is said
as a plan. Full answers are in [`PROJECT-BRIEF.md`](PROJECT-BRIEF.md) and [`APPENDIX.md`](APPENDIX.md).

## Verify the evidence (offline, a few seconds)

```bash
cd evidence
python3 run_slice.py              # last lines: 9/9 and 6/9; exit code 0
python3 score_claude_runs.py      # replays the saved Claude SQL: 7/8, 7/8, 8/8 by rows; 0/8 by text
python3 cross_check.py            # every gold answer recomputed without SQL: 8/8 agree, 2 flagged
# optional, needs `pip install vanna==2.0.2` in a separate venv:
python vanna_check.py             # Vanna OutputEvaluator PASS on 4,667.06; row comparison FAIL
```

All three re-run on 2026-11-23 with the outputs above. `data/Chinook_Sqlite.sqlite` sha256
`bdf635be69850bd3be09c9a2dbeef7ddfb80036bd3ef3381383cd03b61e4a61a`.

## Rebuild the film

Commands are in [`BUILD-PROMPT.md`](BUILD-PROMPT.md) (Stage 7 for v4). Short version, with a
brutalist.art checkout and its Python 3.11 venv:

```bash
cp -r reel/ <work>/riya-k-ground-truth-sql-v4/
cd <work>/riya-k-ground-truth-sql-v4
python3 make_sheet.py && cat _kit_header.py _body.py > scenes.py
source <brutalist.art>/.venv/bin/activate
python3 <brutalist.art>/runtime/scripts/generate_audio_kokoro.py .     # audio first: it is the clock
cd <brutalist.art>
./art run   <work>/riya-k-ground-truth-sql-v4
./art final <work>/riya-k-ground-truth-sql-v4
cd <work>/riya-k-ground-truth-sql-v4      # word_timings.json is included; regenerate with faster-whisper base.en if the audio changes
python3 burn_captions.py <brutalist.art>/renders/riya-k-ground-truth-sql-v4.mp4 riya-k-ground-truth-sql-v4.mp4
```

## Quality gates

Reports are in [`gate-reports/`](gate-reports/).

| Gate | Result | Report |
|---|---|---|
| Gate F (fact check, shot list, prompts present before render) | passed, render allowed | `FACTCHECK.md` |
| Gates L, A, W (beat mix, static pre-flight, contrast and margins) | passed (one non-blocking Gate A warning on B02) | `run.log` |
| Gate B layout audit (strict: warnings block) | **CLEAN** for all 20 scenes | `layout_audit.md` |
| Gate V (frame QC, 40 frames) | **PASS**: 0 BLOCKER, 0 MAJOR | `gate-V-REPORT.md` |
| GATE T (type size, contrast, kerning, 20 beats) | **PASS** | `TYPECHECK.md` |
| Render integrity (`verified.json`) | **ready**, 274.9 s | `verified.json` |

The run log's two SKIN LINT lines (no ClaudeComposerAsk cold open, no ClaudeTitleOutro) are
deliberate, as in the pitch film: `ClaudeTitleOutro` hardcodes "@NikBearBrown", and the film
ends on its own conclusion (B20). The gates missed two layout problems that I caught by looking
at every beat's last frame (an overlapping heading in B08, unreadably small labels in B13);
both were fixed before the final render. Home-directory paths in the reports are shortened to
`<INFO7375>/`.

## Folder

| File | What it is |
|---|---|
| `riya-k-ground-truth-sql-v4.mp4` | the rendered film, with captions |
| `riya-k-ground-truth-sql-v4.srt` | the captions as a subtitle file |
| `APPENDIX.md` | the detail behind each of the four parts |
| `PROJECT-BRIEF.md` | the seven pitch answers, plus "exists today" and "will exist" |
| `beat_sheet.json` | narration and visual plan (copy of `reel/beat_sheet.json`) |
| `BUILD-PROMPT.md` | prompts and commands that rebuild it |
| `SOURCES.md` | what I used, what I made, what Claude contributed, licences |
| `FRICTIONAL.md` | dated log |
| `evidence/` | the runnable slice, the saved Claude runs, the Vanna check, the cross-check, Chinook + licence |
| `reel/` | film source: `make_sheet.py`, `_body.py`, `scenes.py`, `burn_captions.py`, `SCRIPT-v4-four-parts.md`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` |
| `gate-reports/` | toolkit gate outputs |
