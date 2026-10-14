# A job-search agent that shows its evidence — final project pitch film

**Nishant Upadhyay** · INFO 7375, Fall 2026 · runtime **3:54** (234.17 s) · 3840×2160, 24 fps

**Target roles:** data analyst, data scientist, analytics engineer.

**This is a pitch. Nothing of the agent exists yet.** The film describes an agent I will build;
every picture of its output (a shortlist, a scorecard, a posting with evidence labels) is labelled
**constructed** on screen.

## Summary

The film pitches a job-search agent that will watch public job boards at retail and e-commerce
companies and tell a fictional international data-analytics graduate which new postings are worth
their time. Each verdict will cite the exact posting text and resume field behind it; a claim such
as "sponsors visas" will be labelled supported, contradicted or insufficient, and a posting that is
silent gets "insufficient" instead of a guess from company history. The agent will never apply or
send anything: I will approve the shortlist. The film compares it with two tools I used (LinkedIn
Job Alerts and Jobright), says what it will prove and how (tests, a held-out evaluation with
deliberate failure cases, a predicted and triggered failure, a stranger's run of the README), names
the main risk (postings that state nothing) and closes on what exists today versus what will exist.
It is a show-tell film: one isometric drawing per beat, a few words of label, and my own narration
(Kokoro voice `am_michael`, free and local). No Claude responses appear in the film.

## Files

| File | What it is |
|---|---|
| `final-project-pitch-nishant-u.mp4` | The final 4K master (13.8 MB) |
| `final-project-pitch-nishant-u.verified.json` | The toolkit's render-integrity record for the master: status, SHA-256, input hashes (local paths replaced with `~`) |
| `PROJECT-BRIEF.md` | The seven pitch answers, plus "Exists today" and "Will exist" |
| `beat_sheet.json` | The film's beat sheet: narration, visuals, labels, "constructed" flags, measured durations |
| `make_sheet.py` | Generates `beat_sheet.json`; the narration lives in its `NARRATION` table |
| `scenes.py` | The 13 isometric Manim scenes (the show-tell kit `iso_kit.py` pasted in, then the film's scenes) |
| `mp3/timings.json` | Measured narration duration of each beat (the mp3s themselves are regenerated, not committed) |
| `SHOTLIST.md` | Beat-by-beat shot list with start times, durations, labels and "constructed" flags |
| `PROMPTS.md` | "Generation prompts: none", plus the free local build commands |
| `FACTCHECK.md` | Every factual claim in the narration with its source; signed off by me |
| `SOURCES.md` | Tools and licences, sources, what I made, what Claude contributed |
| `BUILD-PROMPT.md` | The prompts I gave Claude Code, in order, and the exact rebuild commands |
| `FRICTIONAL.md` | Dated log of what went wrong and what I did |
| `brutalist-fixes.diff` | My local fixes to the Brutalist toolkit (Windows font path, review timecode position, `npx` on Windows) |
| `.gitignore` | Keeps caches, clips, review renders and local ledgers out of Git |

## Gate reports

| Report | Gate | Result |
|---|---|---|
| `_qc/REPORT.md` | Gate V, frame-level visual QC on the final candidate | 30 frames, 0 BLOCKER, 0 MAJOR |
| `_qc/contact_sheet.png` | Gate V's sampled frames (its sheet shows the first 16: BIDEA–B05) | — |
| `qc-sheet.png` | Review contact sheet, one mid-frame per beat (all 15) | — |
| `TYPECHECK.md` | Gate T, type lock | PASS, 15 beats |
| `layout_audit.md`, `layout_audit.json` | Gate B, Manim layout audit (holds the **last** scene audited, B09; every scene passed before its clip was kept) | 0 errors, 0 warnings |
| `final-project-pitch-nishant-u.verified.json` | Render-integrity (streams, duration, full decode, audible audio, inputs unchanged) | `status: ready` |

Also passed during the build (they print to the terminal and write no report file): build_safety,
Gate F (paperwork), Gate L (beat mix), Gate A (static pre-check), Gate W (contrast and margins), the
no-slates check. `factcheck_check.py`: clean. No SHARPNESS, LOUDNESS or MASTERCHECK reports were
produced: those gates run only in `art post` or by hand, and I did not run them.

## Rebuild

See [BUILD-PROMPT.md](BUILD-PROMPT.md) for the exact commands, from a fresh Brutalist checkout:
apply `brutalist-fixes.diff`, set `PYTHONUTF8=1`, put Manim on PATH, point Remotion at a local
Chrome, then `make_sheet.py`, Kokoro audio, `art run` and `art final`. Everything is free and local:
no API keys, no paid generation, no uploads.
