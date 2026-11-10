# Sources and contributions

## What I used

- **The brief:** "Job-Search Agent 2 — The Loop, the Tools, and the Diff", INFO 7375 Fall 2026
  (`assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` on `main`, and Canvas).
- **My JS1** (`fall-2026/ashwin-t/js1-contract-and-watch/`, commit `d95f05e`): `rule.py`, `text.py`,
  `persona.py` and the fictional résumé were copied unchanged (each file says so in its first line).
  `state.py` was adapted (per-board keys).
- **Lectern's `ATS.md`** (`fall-2026/nik-bear-brown/lectern/ATS.md` on `main`), read for which public
  endpoints Greenhouse, Ashby and Lever expose. No Lectern code was copied.
- **Data:** public, keyless board listings, fetched 2026-11-08 (probe, one GET each) and 2026-11-09 (the live
  run): Greenhouse `klaviyo`, `hubspotjobs`; Ashby `notion`, `supabase`; Lever `palantir`; and the
  nonexistent Greenhouse board `klaviyo-nonexistent-js2`. Postings are those companies' text, saved
  unchanged in `runs/*/raw/` as evidence.
- **Tools:** Python 3 standard library; Claude Code (desktop app) with Claude Opus 5.5 (`claude-opus-5-5`);
  Codex for review; git.
- **Persona:** Supriya Sharma is invented (from JS1). No real résumé is used.

## What I wrote

- `GATE.md`: TODO(Ashwin): confirm "all of it" and whether Codex drafted or reviewed any of it.
  Claude Code changed only the Status line, at my request ("Approved on 2026-11-09").
- The decision to keep the gate's state rule after Claude Code pointed out that no run with the
  deliberate-failure board can finish.
- The Predicted and Why columns of `policy/BOUNDARY-TABLE.md` (my own, `6c1c5b3`).
- The choice to add the Codex-drafted test before the patch, and sending the review-packet prompt to Claude
  Code (quoted in `review-packet/REVIEW-PACKET.md`). TODO(Ashwin): say whether I wrote that prompt or Codex
  drafted it.
- TODO(Ashwin): diff reading, decision; the sign-off; FRICTIONAL lines.

## What Claude Code contributed

- The board probe (2026-11-08) and `drafting/GATE-QUESTIONS.md` (questions only).
- All code in `jobloop/` except the copied JS1 files, `independent_check.py`, `wrong_versions/`,
  `seeded/finished-wrong-answer/build.py`, and every test file except the review-packet test.
- The live run and the seeded demo runs, and the independent checks of them.
- The boundary-case list (inputs only) and the Actual column, filled from test output.
- Finding and reproducing the interrupted-request defect (`review-packet/reproduce_interrupt.py`).
- Drafts of `README.md`, `finished-wrong-answer/README.md`, the facts sections of
  `review-packet/REVIEW-PACKET.md`, the facts table and driver's-seat draft in `SIGNOFF.md`, this file, and
  the "What happened" / "Evidence" lines of `FRICTIONAL.md`.
- Its own bug, found and fixed: the misleading seeded state line (`a11a167`).

## What Codex contributed

- 2026-11-10: Codex drafted `tests/test_review_interrupt.py` (the review-packet regression test) using the
  existing reproduction and test helpers. I added it to the project and committed it, red, before the patch
  (`279c10f`).
- TODO(Ashwin): anything else Codex drafted or reviewed, with dates.
