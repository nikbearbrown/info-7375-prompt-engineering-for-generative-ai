# Sampling report (Chapter 1)

**Question:** if we ask Claude the same contract about the same posting in fresh conversations, how much do the answers vary, and does a repeated answer tell us it is right?

## Setup

| | |
|---|---|
| **Postings** | 5 dev postings (`manifest.json → sampling_ids`), drawn with `random.Random(7376)`: 2 rule-relevant, 2 near-misses, 1 other. The draw was fixed in `SAMPLE_PROCEDURE.md` before any call. |
| **Calls** | 4 per posting, **20 in total**, 2026-10-30 21:45:06–21:45:33Z. |
| **Model** | `claude-opus-5-5` via Claude Code CLI 2.1.310, effort `medium`. Temperature was not set because the CLI can't set it. |
| **Prompt** | v1, SHA-256 `1e86a4a4…3a15`. |
| **Isolation** | Each call was a fresh session: empty temp directory, no tools, no MCP, no settings, no session persistence. The calls are independent of the watch-run judgments. |
| **Raw data** | `experiments/sampling/raw/<id>_rep<n>.json` holds the prompt hash, full user message, full response, validation result and timing. |
| **Recompute** | `.venv/bin/python experiments/score.py sampling` |

## Results

| posting | title | RECORD (rule) | 4 Claude verdicts | valid | distinct raw responses | distinct quote sets | hand label | agreement with hand label |
|---|---|---|---|---|---|---|---|---|
| 8829039002 | Software Engineer, Infrastructure (US) | relevant | R R R R | 4/4 | 4 | 2 | relevant | 4/4 |
| 8829029002 | Software Engineer, Infrastructure (Bengaluru) | relevant | R R R R | 4/4 | 4 | 1 | relevant | 4/4 |
| 7647369002 | Senior Software Engineer (Data Platform) | not_relevant | N N N N | 4/4 | 4 | 2 | not_relevant | 4/4 |
| 7630152002 | Sr Staff Software Engineer (Backend) | not_relevant | N N N N | 4/4 | 4 | 3 | not_relevant | 4/4 |
| 8755666002 | Manager, Field Engineering - Polish speaker | not_relevant | N N N N | 4/4 | 4 | 2 | not_relevant | 4/4 |

## Spread

- **Verdict spread:** none. All 20 responses were valid, and every posting got the same verdict 4 times out of 4. Each verdict also matched the deterministic RECORD.
- **Wording spread:** in every case. All 20 raw responses are textually distinct, explanations included.
- **Evidence spread:** 4 of the 5 postings cited different quote sets across repeats. The set of cited *skills* never changed.

So the variation sits in *how* Claude justifies the answer, not in the verdict, at least on these 5 postings.

## What we can and cannot conclude

- **Can:** on these 5 postings, under prompt v1 and these settings on this date, the verdict is repeatable at 4/4 and the output format is reliable (20/20 valid).
- **Compared with Aditya's hand labels** (received 2026-10-31 14:33 EDT; Aditya confirmed he saw no model output, groups or RECORDs before or while labelling): all **20/20** verdicts agree. On these 5 postings, Claude was both repeatable and, measured against the hand labels, correct.
- **Cannot:**
  - That repeatability *implies* correctness. Repetition only shows the model is consistent; it could be consistently wrong. Here correctness was checked separately against the hand labels, and the two happened to coincide. The RECORD is not an independent reference, because the prompt restates the rule. The hand labels apply the same rule too, so 20/20 means Claude followed Aditya's rule, not that the rule picks good jobs.
  - That this generalises. Five postings, four repeats each, one day, one model version, and temperature uncontrolled.
  - Anything about hard cases. None of these 5 sits near a decision boundary in a way that would invite disagreement. The near-misses fail clearly on title condition B.

**Agreement with the hand labels:** 20/20 calls, 5/5 postings (`experiments/sampling/results.json`).
