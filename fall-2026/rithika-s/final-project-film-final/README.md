# Agentic Retrieval Lab — final project film

**Assignment:** INFO 7375 Final Project Film
**Student:** Rithika Sankar Rajeswari (github.com/rithika-sr)
**Status:** reviewed local final (rendered 2026-11-23; not published)

## Project
**Agentic Retrieval Lab.** A small, open experiment on public MS MARCO data. It asks whether agent-written search queries find the right passage as well as the original human question, and which search method (BM25, bge-small, e5-small, a BM25+bge hybrid) handles them best.

Public repo: https://github.com/rithika-sr/agentic-retrieval-lab at commit `71c42ce`, which holds every number shown in the film (`results/foundation/`, `results/m2/`). `FACTCHECK.md` maps each spoken and on-screen claim to its file and value.

## The film
| | |
|---|---|
| File | `agentic-retrieval-lab-final.mp4` |
| Runtime | 3:40.8 (220.79 s) |
| Resolution | 3840×2160, 24 fps, h264 · AAC 48 kHz · 27.2 MB |
| sha256 | `c7b9d6ae515f0e550137beb2eb7fc30c46a51e4ab6dfc766682852e8eeb4bf23` |
| Narration | Kokoro af_bella synthetic voice, first person, reading Rithika's brief word for word. It is not a recording of Rithika. |
| Pictures | Drawn in Manim on the brutalist.art show-tell kit (free pipeline). No stock, photo, music or AI-generated media. |

The course repo ignores `*.mp4`. If the film is to be committed with this folder, it needs `git add -f`; nothing has been added or committed.

### Structure
Each part opens with its own title card.

| Part | Starts | What it covers |
|---|---|---|
| 1 · Executive summary | 0:00.0 | What and why: agents write the queries now; does the right passage still come back? |
| 2 · What others have done | 0:38.9 | Q2D-Web (private data), MS MARCO (human queries only), BM25 vs embedding models, the gap |
| 3 · Methods | 1:24.3 | Data and rewrites, leak check, test corpus, four retrievers, measures (with one real example from the data), resources, next steps |
| 4 · Evaluation | 2:38.8 | The four pass/fail rules as a checklist (Met / Provisional / Provisional-flattered / Human ahead), worked-if / failed-if, title and name |

Part start times are from the measured narration audio. The compiled master runs 0.4 s longer than the audio total (220.37 s).

## Contents
| Path | What it is |
|---|---|
| `agentic-retrieval-lab-final.mp4` | Final 4K master |
| `FILM-BRIEF.md` | The brief: the film's narration, word for word, in four parts |
| `beat_sheet.json` | The exact beat sheet: script, spoken respellings, measured durations, cues, build stamps |
| `FACTCHECK.md` | 40 rows: every claim → file → value, with verdicts |
| `SOURCES.md` | Sources, dataset and paper citations, synthetic-voice disclosure, third-party licences, contributions |
| `SHOTLIST.md` | Beat-by-beat pictures and on-screen text, plus scene notes and the Gate T fixes |
| `PROMPTS.md` | Generation prompts (none: everything is drawn) |
| `BUILD-PROMPT.md` | Rithika's prompts, verbatim, and the rebuild commands |
| `scenes.py` | Every beat's Manim scene (kit, October cartoon cast, choreography) |
| `make_sheet.py` | Generator for `beat_sheet.json`; checks narration == brief and that every on-screen number is in the brief |
| `word_times.json` | Whisper word timestamps of the narration, used to time every cue |
| `evidence/` | The B14 example (queries 846513 / 846513_p), copied verbatim from the repo's git-ignored data files |
| `toolkit-local-patch.diff` | Local, uncommitted toolkit edits (beat-1 name stamp inside title-safe; an npm lockfile change) |
| `gate-reports/` | Gate F; the `art run` and `art final` logs; Gate V and Gate T reports; `FINAL.md` (master checks) |

## How to rebuild
See `BUILD-PROMPT.md` §1. In short:
1. Clone brutalist.art at `b21f625`.
2. Create a Python 3.12 venv and run `./setup --install`.
3. Apply `toolkit-local-patch.diff`.
4. Copy this folder's sheet, scenes and paperwork into a reel folder, then voice the narration with Kokoro and pad the silences.
5. Run `./art run <reel> --height 2160`, then `./art final <reel> --height 2160`.

## Contributions
- **Claude Code** built the Milestone 2 code, tests and film, and drafted README/BUILD-PROMPT.
- **Claude (chat)** drafted the brief and the pass/fail rules.
- **Rithika** chose the scope, adopted the rules, reviewed results and the film, and made the final decisions.

## License
MIT. Third-party material keeps its own terms (MS MARCO, the Q2D-Web paper, Kokoro, EB Garamond, Manim, the brutalist.art toolkit); see `SOURCES.md`.
