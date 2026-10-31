# Sampling report (Chapter 1)

**Ran:** 2026-10-31 · **Script:** `python experiments/sampling.py --n 4 <5 ids>` · **Raw:** `experiments/results/sampling.json` (all 20 answers, with session ids)
**Model:** claude-sonnet-5-5 via `claude -p`. Each call was a separate process with no tools, no settings, no MCP and no saved session, so every one was a fresh conversation.
**Prompt:** `experiments/prompts/baseline.txt`. **Postings:** 5 from the dev set of the 2026-10-31 live Commure snapshot.
**Written by:** drafted by Claude from `sampling.json`; hand labels are mine (Vrajesh), from `experiments/labels.csv`.

## Every verdict

| Posting | My hand label | Written rule | Claude, 4 fresh runs | Valid format |
|---|---|---|---|---|
| Software Engineer, AI Integrations | relevant | relevant | not_relevant ×4 | 4/4 |
| Fullstack Engineer, Ambient AI | relevant* | relevant | not_relevant ×4 | 4/4 |
| Software Engineer, AI Billing | not_relevant | not_relevant | not_relevant ×4 | 4/4 |
| Software Engineer, Billing Agents | not_relevant | not_relevant | not_relevant ×4 | 4/4 |
| Senior Software Engineer, Claims Intelligence | not_relevant | not_relevant | not_relevant ×4 | 4/4 |

\* I first labeled Ambient AI `not_relevant`, then changed it to `relevant` after seeing the dev results (see PROMPT-EXPERIMENT.md).

## Spread
- Verdicts: **zero spread**. 20 of 20 answers gave the same verdict as the other three runs on their posting.
- Format: 20/20 passed the validator (exact keys, real field paths, matching posting id).
- Wording: the justifications differed run to run, but the reasons were stable. On **AI Integrations**, all 4 runs named "the candidate needs sponsorship (a blocker)" and the "2+ years of professional experience". On **Ambient AI**, all 4 runs named sponsorship and also said the posting asks for "professional experience", even though the posting gives no year count.

## What I can conclude
- Under this prompt and model, Claude's verdict on these 5 postings is **repeatable**.
- It is **repeatably wrong** against my label on 2 of the 5 (40%). Asking more times would not have found that; only the hand label did.
- The wrong answers have one main cause I can name. Claude reads my 10-24 sentence "if it requires sponsorship … it is a blocker" as "if the candidate needs sponsorship", which is not what my contract's R4 says. That became the one change in the prompt experiment.

## What I cannot conclude
- 4 samples per posting cannot show a rare flip. A verdict that changes 1 time in 10 could easily show 4/4 here.
- 5 postings, all from one company (Commure) and one day, say nothing about other boards.
- Repeatable is not correct. Zero spread does not mean Claude is right; on 2 of these 5 it was consistently wrong.
- One model, one prompt. A different model or temperature could spread differently. I did not set a temperature; `claude -p` used its default.
