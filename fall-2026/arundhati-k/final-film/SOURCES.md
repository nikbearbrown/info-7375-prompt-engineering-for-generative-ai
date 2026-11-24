# SOURCES — Final Project Film

## Executive summary

**What this is:** who did what in this film, and where every fact on screen comes from. **Why read it:** the film is
narrated in my name by a synthetic voice, and parts of the build were done by Claude Code; this file keeps those apart.
**What it says:** the searches, predictions, reasons, resources and pass/fail bar are mine; Claude Code wrote the
brand-name fix and its tests on my instruction, ran the evaluation script, and built the film.

## What I did (Arundhati Kandelkar)

- **My own searches** (Part 2): OpenSanctions (Robinhood, SoFi, Chime) and GLEIF (Robinhood, SoFi) — `MY-SEARCHES.md`,
  sent 2026-11-23 15:59 EST; USCIS H-1B Employer Data Hub for Capital One, 2026-10-25 20:22 (`../final-project-film/evidence/eval-25-rows-2026-10-25.md`, row 12).
- **My own legal-entity research** (Ramp, Plaid, Coinbase LEIs; Chime legal name), 2026-11-23 ~16:35 EST —
  `evidence/lei-check-2026-11-23.md`. Claude then verified the three LEIs and a Chime full-text search against GLEIF's public API.
- **My predictions** for the fix, written before any fix code (`PREDICTIONS.md`, 2026-11-23 15:32 EST). Claude asked
  open questions, not options. Claude had seen the dataset rows; I had not, and Claude did not tell me what it saw.
- **My words** for why anyone should care, what I need, and my pass/fail bar (`MY-SEARCHES.md` answers 2–4). The
  narration condenses them; `../youtube/coop-sponsor-check-final/FACTCHECK.md` rows 13, 23 and 31 say exactly what was cut.
- Chose to fix brand names before filming (fix A = first-word candidates, B = alias list, both proposed by Claude).
- `FRICTIONAL.md` — my own dated entries.

## What Claude Code did (on my instruction, 2026-11-22 to 11-23)

- Wrote the fix in my fork (`coop_sponsor_check.py`: `load_aliases`, `starts_with_words`, `resolve_company`),
  the alias file, a fixture of seven real dataset rows, 8 new tests and one rewritten test. Saved test output before
  and after the fix (`evidence/tests-*-2026-11-23.txt`).
- Wrote and ran `evidence/eval_rows_after_fix.py` on the same 25 companies; wrote `evidence/eval-after-fix-2026-11-23.md`.
- Wrote the beat sheet, the new Manim scenes, FACTCHECK / SHOTLIST, voiced the script with Kokoro, rendered the film,
  and checked the narration with a speech-to-text transcript.
- Reused from my graded pitch film: the opening three cards and beats B00–B03, B06, B07, B07A, B09 (some reworded).

## Tools and data

| What | Licence / terms | Used for |
|---|---|---|
| brutalist.art toolkit (local clone `brutalist-final`) | course toolkit | Manim + Remotion rendering, gates |
| Kokoro TTS, voice `bf_emma` (local, free) | Apache-2.0 model | narration — a synthetic voice reading my script, not my recorded voice |
| 80 Days to Stay CSV (in the Reallocation Engine repo) | repo data | the sponsor dataset |
| USCIS H-1B Employer Data Hub | U.S. government public data | my Capital One search; names shown in capitals as listed |
| OpenSanctions, GLEIF LEI search | public websites | my searches; only what I wrote down is shown (no screenshots) |

No image, video or voice generation service was used. No Claude response is shown on screen.
