# SOURCES

Revised 2026-10-21 for the resubmission. The first version (commit `42d8c48`, 2026-10-14) said
the variants were hand-written and that I had checked Vanna myself; neither was accurate.
This version records who did what.

## What I used
| Thing | What it is | Licence / terms | When |
|---|---|---|---|
| Chinook database v1.4.5 (`Chinook_Sqlite.sqlite`) | Public sample database (music store), Luis Rocha, github.com/lerocha/chinook-database | MIT, copy in `evidence/data/CHINOOK-LICENSE.md` | downloaded 2026-10-09, sha256 `bdf635be…a61a` |
| brutalist.art toolkit | Pipeline, show-tell skill, iso kit and approved original props, quality gates | per the toolkit repository | commit `22264a33`, pulled 2026-10-09 |
| Kokoro TTS, voice `af_bella` | Local text-to-speech, runs offline | model ships with the toolkit | 2026-10-09, re-voiced 2026-10-21 |
| faster-whisper `base.en` | Word timestamps for the burned-in captions (caption text is the script) | MIT | 2026-10-19, 2026-10-21 |
| Inter (caption font), EB Garamond (scene font) | Fonts shipped with the toolkit | SIL OFL | — |
| Manim Community 0.18.1, Remotion, FFmpeg | Rendering | open source | — |
| BIRD benchmark page, bird-bench.github.io | Cited in B06: 12,751 question–SQL pairs, 95 databases, execution accuracy | cited, nothing copied | summarised by Claude 2026-10-09; checked by me on the live page 2026-10-21 ("over 12,751 unique question-SQL pairs, 95 big databases", leaderboard by Execution Accuracy) |
| Vanna 2.0.2 (`pip install vanna`), github.com/vanna-ai/vanna | Compared in B06. Run on Chinook by `evidence/vanna_check.py`: its `SqliteRunner` and built-in `OutputEvaluator` | MIT | installed and run 2026-10-21 |
| Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code | The model under test in `evidence/claude_runs/2026-10-21/` | NEU Claude Code access | 2026-10-21 |

No third-party images, footage or music. The one screenshot (B07 in v4, B06 in the pitch film) is my own terminal. No private data: no résumé, contacts, job tracker,
TwinAI code, or conversation transcripts appear in the film or this folder.

## What I made
- The project idea, its scope, and the choice of target role
- Checking the Claude-drafted gold set: each gold query, its result, and each variant's label
- Review and approval of every narration line and every claim (FACTCHECK.md sign-off)
- FRICTIONAL.md entries dated 2026-10-19 onward, written by me
- Checking the BIRD page myself on 2026-10-21 (numbers above)
- Running `evidence/cross_check.py` myself on 2026-10-21 (8/8 agree, Q02 and Q04 flagged)
- **v4 (2026-11-22/23):** the decisions behind the four-part cut: reach Claude through my Claude
  Code access rather than an API key, the evaluation pass bar (kept Claude's draft), approving
  the script, and after watching the first cut, asking for the B05 line and a clearer conclusion
  (B20); the final watch and FACTCHECK sign-off
- Running `evidence/vanna_check.py` myself on 2026-10-21 (`evidence/vanna_check_output_2026-10-21.txt`)
  and the terminal screenshot of it shown in B06 (`reel/images/vanna_run_crop.png`, cropped to the two verdict lines)

## What Claude contributed
Claude (Opus 5.5, in Claude Code):
- **2026-10-09:** recommended the AI Engineer framing; drafted `evidence/gold_set.json`
  (questions, gold SQL, and the equivalent and wrong variants) and `evidence/run_slice.py`. The
  draft's Q08 gold answer had a wrong year, which the first run exposed (see FRICTIONAL.md).
  Read the BIRD and Vanna pages and summarised them.
- **2026-10-09 to 2026-10-14:** drafted PROJECT-BRIEF.md, the narration, `make_sheet.py`,
  `scenes.py`, FACTCHECK.md, SHOTLIST.md, and this folder's documents, including the
  FRICTIONAL.md entries dated 2026-10-09 to 2026-10-14 (from my decisions and the run outputs).
  Ran the toolkit pipeline and gates, and fixed what they flagged.
- **2026-10-19:** rebuilt the film as v2 after the instructor's feedback: new narration and
  scenes, captions (`burn_captions.py`).
- **2026-10-21:** wrote `evidence/vanna_check.py`, `evidence/score_claude_runs.py` and
  `evidence/cross_check.py` (a second check of every gold answer, written by Claude, so not a
  substitute for a second person), ran the
  three blind Claude runs, revised four beats so the film matches the evidence, and updated
  this file, PROJECT-BRIEF.md, README.md and BUILD-PROMPT.md.

- **2026-11-22/23 (v4):** re-cut the film into the four required parts: drafted the v4 script
  (`reel/SCRIPT-v4-four-parts.md`), nine new scenes and the edits to eleven reused ones, the part
  cards, APPENDIX.md, and the v4 FACTCHECK, SHOTLIST, README and BUILD-PROMPT Stage 7. Re-read
  bird-bench.github.io on 2026-11-22 through a web-fetch subagent (human 92.96 test EX; highest
  model row read 83.40; the page was truncated, so no #1 is named) and re-ran the Chinook counts.
  Ran the pipeline and gates, and fixed the layout problems they and the end-frame check found.
  No new model runs.

## Claude output shown in the film
Only B17 (B10 in the pitch film): the scored result of the three Claude runs of 2026-10-21. The raw replies are saved
unedited in `evidence/claude_runs/2026-10-21/`. Every wrong query shown elsewhere in the film
(B02 and B13 in v4) was drafted with Claude and checked by me as an example mistake. None is presented
as a model's live answer.
