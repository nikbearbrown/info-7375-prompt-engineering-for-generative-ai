# Sources and disclosure: Early Bird final project film

**Vrajesh N. - INFO 7375 - Fall 2026**

## What is mine
- The project (Early Bird), my design decisions, the four checks and their targets, the setup answers, and the choice to lock labels before the first run.
- The real results the film cites from my earlier work: the two Commure snapshots (80 postings, then 81, 12 new), my probe finding that a rule alone matched "Account Executive, AI Sales", and my JS1 result that three Claude runs read a "2+ years" posting as not entry level. These are in `js1-contract-and-watch/` and are checked in `FACTCHECK.md`.
- My run of greenhouse-watch on the Commure snapshots is described in grader feedback; I have not saved its raw output (see FACTCHECK.md row 6).

## What Claude contributed
- **Narration script:** drafted by Claude (Sonnet 5.5) from my decisions. It is NOT my own script. The film says so in its last line.
- **Film code:** the Software Walkthrough scene (`EarlyBirdWalkthrough.tsx`, `ebw/engine.ts`), the build scripts (`assemble.py`, `port_engine.py`, `master_audio.py`), adapted from the reference file I supplied.
- **On-screen words, the logo, and the paperwork set** (FACTCHECK, SHOTLIST, PROMPTS): drafted by Claude from my decisions; I checked the numbers against my repo.

## Tools
- Voice: Kokoro `am_onyx`, local, free, synthetic, through the brutalist.art toolkit script.
- Picture: Remotion, rendered by the toolkit's `remotion_scenes.py`; compiled by `./art run` and `./art final`.
- Sound effects: synthesized in the browser (Web Audio); no audio files.
- Fonts: DM Sans and DM Mono (SIL OFL, via Fontsource).
- Icons: Lucide (lucide-static 0.468.0, ISC licence, https://lucide.dev). No person icons, no company logos.
- Logo: a sunrise mark drawn in code (`drawLogo`), made with Claude.

## What is real, sample, or not yet run
- **Real:** the Commure counts and the dot grid built from them (which dots are the new ones is an illustrative seeded pick; the screen says so).
- **Sample, labelled on screen:** Northwind Labs, Lumen AI, Harbor Systems, "3 new roles", the "Must be authorized to work in the US" flag, and the repo match.
- **Not yet run:** job alert emails and job trackers; the cards are tagged NOT YET RUN.

## Tense
Everything about Early Bird that is not built uses "will". Things already done (the Commure test, the probe, the three Claude runs) are past tense.

## FRICTIONAL
`FRICTIONAL.md` is my own log, written by me. Claude did not write it.
