# Sampling report (Chapter 1)

**Question:** if I ask Claude my contract about the same posting several times, each time in a fresh conversation, how much do the verdicts vary? And does a repeated verdict mean a correct one?

## Setup

- **Postings:** the 5 development postings whose titles pass the title test, minus one near-duplicate. "Staff+ Software Engineer, Experimentation" was left out because it's close to "…, Platform". These are the postings where a disagreement was possible: a title that fails the title test is a near-certain "not relevant".
- **Calls:** 4 per posting, 20 in all, with prompt v1 (`prompts/judge_v1.md`). Each call was a separate `claude -p` process with no tools, no settings, no saved session, and an empty working folder, so it was a fresh conversation every time.
  - Model: `claude-sonnet-5-5`, through Claude Code 2.1.316.
  - The calls ran on Oct 31, 2026, between 14:46:29 and 14:46:48 ET.
- **Hand label:** Hemanth's, made by the written rule in CONTRACT.md (`experiment/labels.csv`).
- **Commands:**
  - `python scripts/claude_batch.py sample experiment/sampling/calls.jsonl 5436697008 4935314008 5157847008 5432583008 5224564008`
  - then `python scripts/analyze.py sampling`

## Results (every verdict recorded)

| id | title | hand label | rule (record) | Claude verdicts, 4 fresh calls (confidence) | spread | modal = hand label? |
|---|---|---|---|---|---|---|
| 5436697008 | Staff + Sr. Software Engineer, Cloud Inference Launch Engineering | relevant | relevant | not relevant (high) ×4 | 4/4 same | **no** |
| 4935314008 | Recruiter, AI Research | not relevant | not relevant | not relevant (high) ×4 | 4/4 same | yes |
| 5157847008 | Staff+ Software Engineer, Platform | relevant | relevant | not relevant (high) ×4 | 4/4 same | **no** |
| 5432583008 | [London] Applied AI Architect, Partnerships | relevant | relevant | not relevant (medium) ×4 | 4/4 same | **no** |
| 5224564008 | Performance Engineer, Inference Systems | relevant | relevant | not relevant (medium) ×4 | 4/4 same | **no** |

- All 20 answers passed the validator.
- None quoted words Claude hadn't been shown.
- The raw answers are in `experiment/sampling/calls.jsonl`.

## What I can conclude

- **There was no spread at all.** All 20 verdicts were identical within each posting, and even the confidence levels matched.
- **That repeatability didn't mean correctness.** Claude disagreed with my hand label on 4 of the 5 postings, every time, usually with high confidence. Its justifications point at seniority and domain, for example a co-op versus a Staff role. My rule doesn't consider those. So Claude's judgment and my rule were measuring different things, and asking 4 times couldn't reveal that.
- **The calls agreed with the prompt experiment.** The dev-set run of prompt v1 earlier the same afternoon (14:45–14:46) also said "not relevant" on these five postings. That makes 5 calls per posting, all the same.

## What I cannot conclude

- **Four calls can't rule out rare flips.** If Claude flips on 1 call in 10, four calls would often miss it.
- **Variation did show up on a different posting, under different conditions.** On "Data Engineer" (5464234008) with the same prompt v1, Claude said **relevant** in the agent's seeded run (14:44). It said **not relevant** twice a few minutes later (14:47, `ACTION-SURFACE.md`). So the verdicts aren't always fixed. The posting where the rule's tests pass most clearly flipped; four Staff-level postings didn't.
- **One model, one prompt and one afternoon.** Another model version, another day or prompt v2 could behave differently.
- **"Fresh conversation" means a new CLI process with no session saved.** I can't see whether anything is cached on the server side.
