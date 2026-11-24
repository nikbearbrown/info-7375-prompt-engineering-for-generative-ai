# Co-op Sponsor Check — Final Project Film

## Executive summary

**What this is:** my final project film, in the four parts the assignment asks for: what I'm building and why it
matters; what already exists; how I'm building it; and how I'll know it worked. **Why read it:** it is the record
behind every claim in the film. **What it shows:** a tool that tells international students whether a company has a
public record of sponsoring software jobs, says "unknown" instead of "no", and — after today's fix — lists the legal
names behind a brand (Robinhood, Chime, SoFi) for a person to choose, instead of missing them.

- **Name:** Arundhati Kandelkar · **Target role:** software / full-stack developer
- **Film:** `coop-sponsor-check-final.mp4` — 4:18 (257.8 s) · 3840×2160 · 24 fps · 24 beats · SHA-256 `9369f39d04521d39647027430559d2bc7786d002131ada5ac1e2e0e9773caf56`
- **Narration:** synthetic voice (Kokoro `bf_emma`, local, free) reading my script — not my recorded voice.

## The four parts

| Part | Beats | Evidence |
|---|---|---|
| 1 · What and why | BNAME, BBUILD, BIDEA, BWHAT | the recipe in my fork |
| 2 · What already exists | P2, B05, BOS, BGL, BCARE | `MY-SEARCHES.md` (my searches and words) |
| 3 · How I'm building it | P3, B00–B03, BFIX, B06, BRES, B09 | fork branch `final/arundhatik26-and-fix`; `evidence/tests-*-2026-11-23.txt` |
| 4 · How I'll know it worked | P4, B07, B07A, BAFTER, BBAR | `PREDICTIONS.md`, `evidence/eval-after-fix-2026-11-23.md` |

## Checked / Not checked

**Checked:** 26 tests pass after the fix (9 failed before) — `evidence/tests-*-2026-11-23.txt`; named tests
`test_robinhood_lists_robinhood_markets_for_a_human`, `test_chime_lists_chime_financial_not_only_chime_inc`,
`test_chime_does_not_pull_in_a_name_that_only_contains_it`, `test_sofi_with_alias_lists_social_finance_for_a_human`,
`test_a_single_candidate_is_still_not_auto_answered`. The 25-company re-run used the same CSV (sha256 identical to 10-25).
Every claim on screen has a row in `FACTCHECK.md`; toolkit gates T, V and layout pass.

**Not checked:**
- Whether my three new candidates are the same employers as the hub's rows. A GLEIF check (`evidence/lei-check-2026-11-23.md`)
  found matching legal names for Ramp and Coinbase, but Plaid's registered name is PLAID INC., not my row's
  PLAID TECHNOLOGIES INC — still a person's decision. All three have blank approvals in my dataset.
- Brands outside the 25 whose legal name shares no word with the brand: the alias list has one entry (SoFi), so they
  will still be missed.
- First-word matching on a common word (e.g. typing "Capital" or "First") — not tested; it could list hundreds of
  candidates, all sent to a human.
- The USCIS hub is not joined yet, so my pass/fail bar (Part 4) has not been run.
- My OpenSanctions and GLEIF searches are recorded in my words only; no screenshots or export were saved.
- (Resolved 16:39 EST) How Kokoro pronounces my name: the speech-to-text check cannot spell it, so I listened to the opening card and the outro myself — it is correct.

## Files

| File | What |
|---|---|
| `coop-sponsor-check-final.mp4` | the film |
| `PREDICTIONS.md` | my predictions for the brand-name fix, written before the fix (15:32 EST) |
| `MY-SEARCHES.md` | my two searches (OpenSanctions, GLEIF), why care, resources, pass/fail bar — my words |
| `FRICTIONAL.md` | my own dated entries |
| `evidence/` | tests before/after the fix, the 25-company re-run (script, JSON, write-up) |
| `SCRIPT-OUTLINE.md` | running order |
| `FACTCHECK.md`, `SHOTLIST.md` | every claim on screen with its source; every picture with its honesty tag |
| `reports/` | toolkit gates: GATE T `TYPECHECK.md` (PASS), Gate V (0 blocker / 0 major), layout audit (0 / 0) |
| `SOURCES.md` | who did what (me vs Claude Code), tools, data |
| `BUILD-LOG.md` | Claude's technical log |
| `source/` | `make_sheet.py`, `scenes.py`, `beat_sheet.json`, `PROMPTS.md`, copied from the reel folder `youtube/coop-sponsor-check-final/` |

## Rebuild

Copy `source/` into a reel folder first (here `youtube/coop-sponsor-check-final/`, which is not committed), then:

```bash
cd brutalist-final && export PATH="$PWD/.venv/bin:$PATH"
REEL=../info-7375-prompt-engineering-for-generative-ai/youtube/coop-sponsor-check-final
python3 $REEL/make_sheet.py && python3 runtime/scripts/generate_audio_kokoro.py $REEL
./art run $REEL --height 2160 && ./art final $REEL --height 2160
```

Earlier pitch film (graded 45.5/50): `../final-project-film/`.
