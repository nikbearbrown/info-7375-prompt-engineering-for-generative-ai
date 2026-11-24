# Final Project Film — A Job-Search Agent You Can Check

**Yash Saraf** · INFO 7375 · Fall 2026 · due 2026-11-23

My final project is a **job-search agent**. It watches company job boards and reports only the
postings that are new. It explains each keep or reject with written rules anyone can recheck,
then stops and lets a person decide. It never applies, emails or logs in. The candidate is
**Priya Nair, a fictional persona**; no real résumé is used.

This film presents the project in the professor's four parts: executive summary, introduction
(what others have done), methods (how I will build it) and evaluation (how I will know it worked).

## What changed since my October pitch

In October I pitched **actions-docs-qa**, a question-answering tool for the GitHub Actions docs
(`../final-project-film/`). The final project must be **agentic**: a loop, tools with a
permission policy, a stop condition and a human gate. A question-answering tool is not, so I
changed my final project to the job-search agent I have been building in JS1 to JS3. The reason
is in `FRICTIONAL.md` (2026-11-23).

## The film

- **File:** `job-search-agent.mp4` · **Length:** 5 min 23 s (322.96 s) · 1920×1080, H.264 + AAC
- **SHA-256:** `6a6fe350d099868fff7f8e6f9a2da43a753acc30cf99f2672588d14dac96820d`
- **Gates:** F, L, A, W, B, V, GATE T and the bookend check all PASS (`gate-reports/README.md`)
- The MP4 is not in Git (the course repository's `.gitignore` blocks video files). It is in the
  Canvas zip; the SHA-256 shows the two copies match.
- Format: a Brutalist show-tell film, built the same way as my October pitch. Every beat is a
  drawn, moving Manim picture. The voice is the local Kokoro `am_onyx` voice reading my script: a
  **synthetic voice, not mine**. The terminal beats typeset the real recorded output of my agent
  (`youtube/job-search-agent/evidence/terminal-2026-11-23.txt`) and are labelled as a
  reconstruction, not a screen recording. The comparison beats are drawn from my dated
  screenshots and say so on screen.

## What is in this folder

| File | What it is |
|---|---|
| `SCRIPT.md` | The narration, beat by beat, as the voice reads it, in the four parts, with what is on screen |
| `youtube/job-search-agent/` | The build: `make_sheet.py` (beat sheet), `beat_sheet.json`, `scenes.py` (one Manim scene per beat), `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, and the recorded terminal output |
| `gate-reports/` | The Brutalist quality-gate logs and reports |
| `FRICTIONAL.md` | My dated log: the project decision, my predictions before comparing tools, and what I found |
| `SOURCES.md` | What I used, what I wrote, what Claude contributed |
| `evidence/` | 10 dated screenshots from 2026-11-23: LinkedIn (3), Jobright (5), Claude (2) |

## What is completed, and what is planned

| Status | What | Where |
|---|---|---|
| **Completed** | JS1: watcher for one board, written-rule verdict plus a checked Claude judgment, 77 tests, two live runs | [`../js1-contract-and-watch/`](../js1-contract-and-watch/) |
| **Completed** | JS2: bounded loop over four boards, permission policy in code, independent check, three planted bugs caught, 65 tests, two live runs | [`../js2-loop-tools-diff/`](../js2-loop-tools-diff/) |
| **In progress** | JS3: filter with written rules, 63 tests, a first run on 2026-11-18 (2,418 saved postings: 63 to review, 2,355 rejected, each with a recorded reason) | [`../js3-filter-tool-score/`](../js3-filter-tool-score/) |
| **Planned** | JS4 (Dec 1): plan before each run, verification, memory across days | — |
| **Planned** | JS5 (Dec 13): approval gate bound to the exact shortlist, data and people register, supervised run | — |
| **Planned** | Final project (Dec 20): held-out evaluation, five or more deliberate failures, a triggered failure, a stranger run, the demo | — |

## How to rerun the terminal part of the film

Offline. Python 3.9 or newer, standard library only; nothing to install. From the course
repository root:

```bash
cd fall-2026/yash-s/js2-loop-tools-diff
python3 -m unittest discover -s tests                                   # Ran 65 tests ... OK
python3 wrong_versions.py                                               # RESULT: every wrong version was caught
python3 independent_check.py runs/run-2026-11-10T025118Z                # Nothing flagged.
T="$(mktemp -d)"
python3 agent.py --reset-state greenhouse-anthropic --state-dir "$T/state"                  # REFUSED: needs explicit approval
python3 agent.py --reset-state greenhouse-anthropic --state-dir "$T/state" --approve-reset  # reset: ...
```

The last two use a temporary folder, so no committed state changes. I ran all of them on
2026-11-23 with these results.

## How to rebuild the film

From the folder that holds both a `brutalist.art` checkout and this film's build folder, with
ffmpeg, Node, and a Python that has `manim` and `kokoro-onnx` first on `PATH` (I used
`/opt/anaconda3/bin/python3`). Free local pipeline only: no API key, no paid service.

```bash
REEL="final-project-film-2/youtube/job-search-agent"
python3 $REEL/make_sheet.py                                               # beat sheet
python3 brutalist.art/runtime/scripts/generate_audio_kokoro.py $REEL      # Kokoro voice; durations written back
./brutalist.art/art run   $REEL --height 1080                             # gates F, L, A, W, B, V + review cut
./brutalist.art/art final $REEL --height 1080 --out final-project-film-2  # GATE T, then the master
```

## Honesty notes

- Past tense only for what ran. JS4, JS5 and the final evaluation are plans.
- LinkedIn's "medium" match was computed from my own LinkedIn profile, not Priya's, so it is not
  compared with my agent.
- The Claude test was not fully isolated: Claude read its memory during it (shown in the
  screenshot).
- Jobright and the Claude test used Priya Nair's fictional résumé.
- The voice in the film is synthetic (Kokoro `am_onyx`), reading my first-person script.
- The LinkedIn search screenshot in `evidence/` is a blurred copy
  (`linkedin_search_23_Nov_2026-blurred.png`): my own profile photo is pixelated. The comparison
  beats are drawn from the screenshots; no screenshot is shown full-screen in the film.
