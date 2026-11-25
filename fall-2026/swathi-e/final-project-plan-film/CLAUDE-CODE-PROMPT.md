# Claude Code prompt — Final Project Film (Brutalist)

**Status: approved for Phase 1 only.** Phases 2–3 run only after Swathi reviews the Phase 1 inventory report and approves rendering in a separate message.

How to use (same as the pitch film): put this file, `beat_sheet.json`, `NARRATION.md` and `PLAN-APPENDIX.md` in `~/Downloads/brutalist/final-project-plan-film/`, open Claude Code there, and paste everything below the line.

---

You are helping me (Swathi) render my Final Project Film with Brutalist, using the same pipeline and settings as my pitch film. I decide; you execute, verify, and report. Stop and ask me whenever something conflicts with these instructions or looks private.

**In this session, do Phase 1 only, then stop.** Phases 2 and 3 are listed so you can plan for them; do not start them until I approve in a separate message.

## Ground rules

- Work only in `~/Downloads/brutalist/final-project-plan-film/`.
- Treat `~/Downloads/brutalist/final-project-film/` (my pitch film) as **read-only reference**. Do not modify, move, rename or delete anything in it.
- Do **not** run any git command that changes anything (no init, add, commit, branch, push), and do not create a PR, zip anything, or touch Canvas.
- Do not change the narration text or on-screen labels in `beat_sheet.json`. If something cannot render as written, stop and tell me.
- No logos, screenshots, company-branded images, or personal data in any frame. The persona Priya Nair is fictional and must be labelled FICTIONAL where shown.
- Report honestly: say what you ran and what you observed; label anything you did not run.

## Phase 1 — Inventory (this session; then STOP)

1. **Protect the pitch folder.** Write a SHA-256 manifest of every file in `~/Downloads/brutalist/final-project-film/` to `pitch-folder-before.sha256` in the **new** folder. Report the file count.
2. **Find the pitch film's setup.** List the pitch folder's files and report how the pitch film was rendered: its BUILD-PROMPT.md, build scripts, toolkit location and version, voice settings, and the gate commands (local and upstream, including render integrity).
3. **Check the new folder.** Confirm it contains exactly `beat_sheet.json`, `NARRATION.md`, `PLAN-APPENDIX.md` and `CLAUDE-CODE-PROMPT.md`. Validate that `beat_sheet.json` is valid JSON with the same schema as the pitch film's beat_sheet.json (same keys at metadata, beat and graphic level). Report any difference. Confirm 11 beats, voice `am_michael`, engine `kokoro`, `runtime_ceiling_s` 300, and the sum of `estimated_duration_s` (expected 257).
4. **Narration match.** Check that each beat's `narration_text` matches its paragraph in NARRATION.md, allowing only these voice spellings: "H one B" (H-1B), "H one B one" (H-1B1), "E three" (E-3), "U S C I S" (USCIS), "O P T" (OPT), "My Visa Jobs" (MyVisaJobs), "H one B Grader" (H1BGrader), and numbers written as words (e.g. "one thousand eight hundred thirty-two" for 1,832, "Version one point one" for Version 1.1). List every other difference.
5. **Label check.** Confirm from `production_viz` that: each beat's label starts with its part header (1 · EXECUTIVE SUMMARY for B01–B02, 2 · INTRODUCTION for B03–B04, 3 · METHODS for B05–B08, 4 · EVALUATION for B09–B11); B05 carries "COMPLETED · JS3"; B01, B04 and B06–B10 carry "PLANNED"; B11 carries "PROPOSED TARGETS — NOT RESULTS" for the whole beat; B07 shows the loop "collect -> filter -> match -> check -> record -> stop"; B06 shows Certified counted and Certified-Withdrawn listed separately and not counted; B03, B05 and B06 include source footers.
6. **B05 numbers.** Confirm the only completed-work numbers are: 1,832; Databricks 901, Stripe 789, Plaid 142; v1 shortlisted 4; 0 of 30 random rejects relevant (up to ~10%); v1.1 changed 7 verdicts; shortlist still 4; commits 0f689b8, d4a3b94, beb8a26, 815064e, 7672a21, c2e624e.
7. **Plan, without running it.** Report the exact render and gate commands you would run in Phase 2 (copied from the pitch film's setup, adapted only for the new folder and slug `job-search-agent-final-project-film`), and which pitch-film files you would copy (scripts and config only; no media, no pitch beat sheet).
8. **Recheck the pitch folder.** Recompute its SHA-256 manifest and confirm it is identical to `pitch-folder-before.sha256`.

**STOP. Report steps 1–8 and wait. Do not render, copy pipeline files, or run gates.**

## Phase 2 — Render (only after my separate approval)

9. Copy only the approved scripts/config into the new folder. Render all 11 beats with the same engine, voice, style preset and palette as the pitch film. Target runtime about 4 minutes 15 seconds; ceiling 5 minutes.
10. Every label, badge, number and source footer must appear exactly as written in `beat_sheet.json`.

## Phase 3 — Checks and drafts (only after my separate approval; then STOP)

11. Run the same quality gates as the pitch film (local and upstream, including render integrity) and save the reports. If a gate fails, report it and propose a fix; don't change narration or labels without my approval.
12. Report: final runtime; the time at which Part 1 ends (must be before 1:00); integrated loudness; SHA-256 of the mp4; and a contact sheet (one frame every 6 seconds).
13. Draft, for my review only: README.md (what the film is, runtime, how to rebuild, mp4 filename and SHA-256, and a note that media stays out of git because the course repo's .gitignore excludes it), SOURCES.md (what I wrote, what Claude Chat and ChatGPT contributed, what you did, toolkit and voice licences), BUILD-PROMPT.md (exact rebuild commands). Do **not** write FRICTIONAL.md; I write it.
14. Scan every file in the new folder for home-directory paths, email addresses, phone numbers, and names other than mine and the fictional persona. Report hits; don't edit.
15. Recheck the pitch folder manifest again.

**STOP. Do not commit, push, create a PR, zip, or submit. Wait for my review.**
