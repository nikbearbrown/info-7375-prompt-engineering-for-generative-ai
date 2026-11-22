# Final Project Film Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a narrated film of at most 5:00, "Fine Print, built on jobwatch", in the brief's four parts, plus its
appendix and records, ready for the student's single approval checkpoint.

**Architecture:** October's brutalist.art `show-tell` pipeline is reused. `film/make_sheet.py` holds the narration and
beat definitions, and `film/scenes_body.py` holds one Manim scene per beat. `art run` and `art final` handle the gates
and the 4K master. Real jobwatch runs are captured as verbatim terminal logs (with SHA-256) and replayed in a Manim
terminal frame. Every sentence of the script traces to a record in `FACTCHECK.md`.

**Tech Stack:** Python 3.12.7 (toolkit venv), Manim 0.20.1, Remotion 4, Kokoro-82M `am_eric` (kokoro-onnx 0.6.1),
FFmpeg 8.1, and brutalist.art at `519fcbb` in `../Assignment 4/brutalist.art`.

**Spec:** [DESIGN.md](DESIGN.md). The brief, verbatim, is [ASSIGNMENT-BRIEF.md](ASSIGNMENT-BRIEF.md).

**Execution:** the student asked to approve once, at the end ("After everything you finished setting up let me know
for approval"). Claude runs the tasks itself and uses subagents for the parts that gain from fresh eyes: the prior-art
research (Task 2), the fact-check (Task 3), and the final review (Task 7). This folder is not a git repo, and no commits
were asked for, so each step goes into Claude's timeline in `FRICTIONAL.md` instead.

## Global Constraints

- Length: at most **300 s**, with a target of about 270 s. Part 1 ends by **60 s**.
- The four parts come in the brief's order. A part tag sits top right on every beat: `1 · What and why`,
  `2 · What exists`, `3 · How`, `4 · Did it work?`.
- Honesty stamp, top left, on every beat that pictures something:
  - `real · …` (with source and date) for anything that ran or was checked;
  - `constructed · not built` for the plan;
  - `constructed example` for any made-up sentence.
- Voice: Kokoro `am_eric`. The student's name is voiced by `name_voice.py` from `सुकेत रेड्डी फ्रंदटूर`.
- Never show `@NikBearBrown`, the instructor's name, a persona, `ClaudeTitleOutro`, or `ClaudeDefinitions`.
- Use past tense only for what ran. Numbers on screen come from the run logs, never from the script.
- No home-folder paths, usernames, or tokens on screen. Use the fictional personas only (Alex Morgan, Arjun Rao).
- The student's own words (Frictional entries, the "worked / didn't work" bar, script edits) are placed verbatim and never
  written by Claude.
- The film describes JS3–JS5 only in their briefs' own terms. It never drafts the student's `FILTER.md`.

## Review Focus

1. **A past-tense or present-tense line about something not yet built.** A viewer would expect "will" for every Fine
   Print capability. Task 3's fact-check marks each sentence's tense against the records.
2. **A number on screen that differs from the run log.** Task 4 builds every terminal frame from
   `evidence/terminal/*.json`, never from typed text, and Task 5's check greps each on-screen number back to its log.
3. **Private details in a terminal frame**, such as a `/Users/...` path or a username. Task 1 scrubs `~` at capture and
   records the substitution, and Task 5 checks the frames at 85% of each beat.
4. **Part 1 over 60 s, or method words in it.** Task 4 measures cumulative audio at the end of Part 1, and Task 3's
   checklist bans loop, tool, gate and budget there.
5. **A prior-art claim stronger than its source.** Task 3 allows only claims that `evidence/prior-art/PRIOR-ART.md`
   quotes from the source's own page, with an access date.

---

### Task 1: Capture the real jobwatch runs

**Files:**
- Create: `tools/capture.py`, `evidence/terminal/<run>.txt`, `evidence/terminal/<run>.json`,
  `evidence/terminal/SHA256SUMS`, and `work/jobwatch/` (a clone; not submitted)

**Interfaces:**
- Produces: `evidence/terminal/<run>.json`, shaped as
  `{"command": str, "cwd_shown": "~/…", "started_utc": str, "exit_code": int, "lines": [{"t": float, "text": str}]}`.
  Task 4 replays it.

- [ ] Clone the fork's branch `js2-loop-tools-diff` into `work/jobwatch`, then check out `9c1db18`. Verify that
  `git -C work/jobwatch rev-parse --short HEAD` prints `9c1db18`.
- [ ] Write `tools/capture.py CMD... --out evidence/terminal/<run>`. It runs the command in `work/jobwatch/<subdir>`,
  records each stdout and stderr line with its elapsed time, replaces the home path with `~`, and writes `.txt` and
  `.json`.
- [ ] Capture `tests-2026-11-21`: `python3 -m unittest`. Expected: `Ran 164 tests` and `OK`, exit 0.
- [ ] Copy `state/state.json` to `evidence/state-before-film-normal-noapproval.json`.
- [ ] Capture `film-normal-noapproval-2026-11-21`:
  `python3 -m jobwatch run --run-id film-normal-noapproval-2026-11-21`. Expected: `incomplete` (approval missing),
  exit 3.
- [ ] Compare the state file before and after. Run `cmp` on the two state copies and expect no output.
- [ ] Capture `film-failure-2026-11-21`: `python3 -m jobwatch run --run-id film-failure-2026-11-21 --failure-control`.
  Expected: `incomplete`, 404 as expected, exit 3.
- [ ] Copy the Nov 8 student run's terminal log (`evidence/terminal/2026-11-08-normal-1-run-by-student.txt` in JS2) into
  `evidence/terminal/`, unchanged. Record its JS2 path and SHA-256.
- [ ] Write `SHA256SUMS`. Verify with `shasum -a 256 -c SHA256SUMS`; every line must say `OK`.

### Task 2: Research prior work (subagent)

**Files:** Create `evidence/prior-art/PRIOR-ART.md`.

**Interfaces:**
- Produces: one entry per example, with:
  - the name and URL;
  - the access time;
  - what it produces, quoted in 15 words or fewer from its own page;
  - what its page shows it does not do;
  - a confidence level.

- [ ] Find three to five examples across these categories:
  - sponsorship-history lookups built on public H-1B or LCA data;
  - résumé-to-posting match scorers;
  - published research on extracting skills or requirements from job postings.
- [ ] Use only the source's own page or the paper itself. No logins, forms or personal data, and searches use generic
  terms only.

### Task 3: Script, shot list and fact-check

**Files:**
- Create: `film/make_sheet.py`, `film/beat_sheet.json`, `SCRIPT.md` (generated for review), `SHOTLIST.md`,
  `FACTCHECK.md`

**Interfaces:**
- Consumes: Task 1's run JSON (numbers) and Task 2's `PRIOR-ART.md`.
- Produces: `beat_sheet.json` with beat ids `B01`… and `BOUT`. Each beat has `narration_text`, `voice`, `shot.manim.class`
  (named `B##_Name`, since Gate W needs that pattern), `on_screen_status` (the stamp) and `part`.

- [ ] Write the narration part by part, following DESIGN §6. Leave `B19_Bar` (the student's bar) as `PENDING-STUDENT`.
  It is rendered last.
- [ ] Generate `SCRIPT.md` from the sheet: beat, part, stamp, narration and estimated seconds.
- [ ] Write `FACTCHECK.md`, with one row per factual sentence: the claim, its record path or URL, and its tense (did /
  does / will).
- [ ] Dispatch a fresh subagent to check `SCRIPT.md` against `FACTCHECK.md`'s records and report each unsupported claim.
  Fix every genuine finding.

### Task 4: Scenes, narration and terminal replays

**Files:**
- Create: `brutalist.art`, a symlink to `../Assignment 4/brutalist.art`, so the October scripts' `HERE.parent` lookups
  work. Also create `film/build_scenes.py`, `film/scenes_body.py`, `film/build_audio.sh`, `film/name_voice.py` and
  `film/finish_audio.py`. Adapt each from `Assignment 4/final-project-film/`, changing only the slug, the bookend beat
  ids and the narration heads.

**Interfaces:**
- Consumes: `beat_sheet.json` and `evidence/terminal/*.json`.
- Produces: `film/manim/<BID>.mp4`, `film/mp3/beat-<BID>.mp3` and `film/mp3/timings.json`.

- [ ] Write the scenes:
  - Reuse October's helpers (`gplay`, `at`, `label`, `stamp`) and the approved 25 props.
  - Add `term_frame(run_json, lines)`, which draws a terminal window with mono text at a size that passes GATE T at 4K
    (x-height of at least 41 px).
  - Add `part_tag(text)`, drawn top right.
- [ ] Run `bash film/build_audio.sh`. Verify that `film/mp3/timings.json` sums to 300 s or less and that Part 1 ends by
  60 s.
- [ ] Run `art run film --height 2160`. Verify that Gates F, L, A, W and B pass, then look at frames at 85% of each beat.

### Task 5: Master, captions and checks

- [ ] Run `art final film --height 2160 --out film/exports/landscape`. GATE T must pass.
- [ ] Generate the captions with `film/make_srt.py`.
- [ ] Run `master_check`, `loudness_check`, `sharpness_check`, `srt_check` and `factcheck_check`. Each must pass, and
  each report is saved under `film/gate-reports/`.
- [ ] Make a contact sheet of frames at 85% of each beat. Check every on-screen number against its log, every stamp, and
  the absence of any private path.

### Task 6: Appendix and records

**Files:** `APPENDIX.md` (and `APPENDIX.pdf`), `README.md`, `SOURCES.md`, `FRICTIONAL.md`, and the GitHub-ready staging
folder `submission/github/` (not pushed).

- [ ] `APPENDIX.md` has the detailed plan, the data sources, the resources, the evaluation design, and links to
  `evidence/`.
- [ ] `README.md` gives what the film is, how it was made, what is real and what is constructed, and the MP4's filename
  and SHA-256.
- [ ] `SOURCES.md` separates the student's work, the student's choices among Claude's options, and Claude's work.
- [ ] `FRICTIONAL.md` holds the student's entries verbatim, with dates, followed by Claude's factual timeline.

### Task 7: Independent review and handoff

- [ ] A fresh subagent watches the contact sheet and reads the script, `FACTCHECK.md`, the README and `SOURCES.md`
  against the records. It reports anything that misstates what ran, who did what, or what a source says.
- [ ] Fix every genuine finding, then re-render only the affected beats.
- [ ] Bring the student the draft for approval, with what only they can do:
  - script edits in their voice;
  - the "worked / didn't work" bar and the test-set size (beat `B19`);
  - Frictional entry 2.
