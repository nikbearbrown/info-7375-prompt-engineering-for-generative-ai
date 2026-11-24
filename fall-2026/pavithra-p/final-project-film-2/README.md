# DryRun: Final Project Film

- Name: Pavithra Prasad
- Course: INFO 7375, Prompt Engineering for Generative AI (Fall 2026)
- Project: DryRun, see what an AI's command will do before it touches your files (my final project, pitched in October)
- Film: `dryrun-project-film.mp4`, 4:23 (263.25 s), 3840×2160, 24 fps
- SHA-256 of the film: `a1e8f12de1d590fff6ed689217db55ac61ace0218bcfc3f31546a4c9dbf257a1`

> Where the video is: in the Canvas zip (`Prasad_Pavithra_INFO7375_FinalProjectFilm2.zip`), as with my pitch film. Everything else in the zip matches this folder, and the SHA-256 above matches the zip's film.

> A plan, not a build. No DryRun code exists yet. Everything the film says DryRun does is what I will build. The real artifacts are a Claude reply (2026-10-11), my test of its preview (2026-10-13) and what I read about the tools that already exist (2026-11-23), all in `evidence/`.

## The four parts

The film follows the professor's four parts, in order. A kicker on every frame names the part ("PART 2 OF 4").

| Part | Beats | Time | What it covers |
|---|---|---|---|
| 1 · What and why | B00–B05 | 0:00–0:54 | What DryRun is, with no "how"; the problem; the real Claude reply and my test of it; why it matters |
| 2 · What others have done | B06–B09 | 0:54–1:40 | Coding agents' permission prompt, `try`, InterCode and NL2SH, and what they got; why mine is still worth building |
| 3 · Methods | B10–B19 | 1:40–3:35 | How it will work, the human approval, the trap folders, where the data comes from, the steps with dates, and the credits, accounts, access and compute I have |
| 4 · Evaluation | B20–B25 | 3:35–4:23 | What I'll measure, the held-out set, at least five planted wrong commands, what result means it worked or didn't, and what it can't show |

The detail behind parts 2 to 4 is in [`APPENDIX.md`](APPENDIX.md), including two more existing tools (ShellCheck and explainshell) and the task counts for the evaluation (30 tasks, 10 held out).

## What's in this folder

| File | What it is |
|---|---|
| `dryrun-project-film.mp4` | The film (Canvas zip only) |
| [`APPENDIX.md`](APPENDIX.md) | Prior work with sources, the method, the data, the dated steps, resources, evaluation targets, scope and risks |
| [`beat_sheet.json`](beat_sheet.json) | Narration and picture plan for every beat (from `make_sheet.py`) |
| [`BUILD-PROMPT.md`](BUILD-PROMPT.md) | The commands and prompts that rebuild the film |
| [`SOURCES.md`](SOURCES.md) | What I used, what I made, what Claude contributed, what is real and what is constructed |
| [`FRICTIONAL.md`](FRICTIONAL.md) | Dated log of how this was made |
| `scenes_body.py`, `build_scenes.py` | The drawings (one Manim scene per beat) |
| `boost_audio.py`, `sharpness_on_final.py` | Narration +3 dB; the sharpness gate run on the delivered film |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | The toolkit's required paperwork |
| [`reports/`](reports/) | The toolkit's gate reports. Every gate that ran passed on the delivered film: layout audit (26/26 scenes clean), visual QC (0 blockers, 0 major), type check, loudness (−19.3 LUFS), master check, and sharpness on both the review cut and the delivered film. `run-gates.log` shows the two earlier runs that stopped on layout warnings. `master-check.md` notes one skipped sub-check: its file (`clock_check.py`) is missing from the toolkit at `b21f625`, as in my pitch. |
| [`evidence/`](evidence/) | The real Claude reply, my preview test, and the prior-work notes |

My pitch film for the same project is in [`../final-project-film/`](../final-project-film/). Eleven of its beats are reused here word for word; the rest are new.

## Rebuild it

Full steps in [`BUILD-PROMPT.md`](BUILD-PROMPT.md). In short, from the Brutalist toolkit (commit `b21f625`) checked out beside this folder, with its venv active:

```bash
python3 ../final-project-film-2/make_sheet.py && python3 runtime/scripts/generate_audio_kokoro.py ../final-project-film-2 --speed 0.95 && python3 ../final-project-film-2/boost_audio.py
```

```bash
ART_HOME=$PWD python3 ../final-project-film-2/build_scenes.py && ./art run ../final-project-film-2 --height 2160
```

```bash
./art final ../final-project-film-2 --height 2160 --out ../final-project-film-2/exports
```

## Narration and credits

- The narration is a synthetic voice (Kokoro `af_heart`, run locally) reading my script.
- Built with help from Claude Code; see `SOURCES.md`.
