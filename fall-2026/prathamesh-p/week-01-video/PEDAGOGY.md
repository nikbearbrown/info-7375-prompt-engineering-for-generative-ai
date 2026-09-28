# PEDAGOGY — Expected 665.24, Observed 630

## GATE P — narration review

VERDICT: PASS — signed by Prathamesh P, 2026-09-27. When I first signed, I had reviewed the narration by reading it silently. I then read the full narration aloud on 2026-09-27 and confirm this verdict.

The verdict above was written by the student. Claude recorded it here at the student's instruction and did not sign anything.

**What was signed:** the `narration_text` of beats B00–B09 in `beat_sheet.json` (351 words), including the B03, B06 and B07 wording edits (proposed by a separate Claude chat and approved by me) and the B07 cut of 'set in advance' (suggested by Claude Code and approved by me).
Narration fingerprint, SHA-256 of `json.dumps([{beat_id, narration_text} ...], ensure_ascii=False, sort_keys=True)`:
`8afc5b04f486a969caa66af0d24ed7c6a106ada5e64c8dec8dd89bb97b7c358c`
If any narration changes, this fingerprint no longer matches and GATE P has to be signed again.

## One concept

Expected count (1000 × 0.6652409557748218 = 665.24) versus observed count (630) for token 2 in the seed-7 run of `lessons/01-randomness-and-first-prompts/code/main.py`. They answer different questions: what chance was assigned, and what happened in this sample.

## Structure

| Beat | Role | Evidence on screen |
|---|---|---|
| B00 | Cold open: the two numbers | main.py output / computed from it |
| B01 | Overview: the misconception typed and corrected | labelled **constructed example** |
| B02 | Mechanism: real code, real probabilities | main.py source + output |
| B03 | Expected count: 665.24, not an integer | computed from main.py output |
| B04 | Observed count: the real seed-7 draws | `evidence/seed7_sequence.json` (counts verified = main.py) |
| B05 | Side by side: gaps +11.97 / +23.27 / −35.24, sum 0 | computed |
| B06 | Seed = repeatable, not correct | `evidence/main_output_rerun_2026-09-27.txt` (byte-identical) |
| B07 | **Boundary:** one run can't show whether 35.24 is typical | one real point; axis labelled constructed |
| B08 | Your turn: decide a criterion, then run 20 seeds | snippet checked (runs); results not shown |
| B09 | Title restate + provenance + synthetic-narration disclosure | — |

## Chapter 1 lines the narration relies on

`chapters/01-randomness-and-first-prompts.md` in the course repo: line 247 (B04), line 249 (B03), line 259 (B05), line 261 (B07).

## Departures from the ai-explainer SKILL.md (student decisions)

No Claude interface (cold-open composer, ask→result beats, verdict page, Your Turn composer, ClaudeTitleOutro). No instructor persona, channel chip, logo bug or "in for Bear" sign-off. Counters only, no equation beats. See FRICTIONAL.md Entries 6–7.
