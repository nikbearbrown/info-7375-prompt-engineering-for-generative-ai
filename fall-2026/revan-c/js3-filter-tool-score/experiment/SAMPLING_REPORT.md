# Sampling report (Chapter 1)

## What was asked

- **Question:** the baseline prompt contract (`prompts/baseline.txt`, sha256 `d96d6a80649a…`, last committed in the current history as `87f68dd`; the run metadata retains its earlier hash from before the history rewording) applied to five postings.
- **Model:** `claude-opus-5-5` at effort `medium`. No temperature was sent, because current models reject sampling parameters.
- **Calls:** each posting got **4 separate API requests**. Every request is stateless, so each one is a fresh conversation that never sees another call's answer.
- **When:** the calls ran on 2026-10-31 from 06:03:41 to 06:04:44 UTC, run by Revan in a terminal.
- **Which postings:** all five are from the **development** set; held-out ids are refused by the script.
- **Hand labels:** each posting's label comes from `experiment/labels.csv`, completed before these calls. An AI assistant drafted the rows; I read all 20 full postings, checked each label against my rule, and adopted them before the experiment.
- **Cost:** 20 calls used 73,200 input and 6,775 output tokens.

## What came back

| Posting | Title | Hand label | relevant | not_relevant | invalid | Same verdict | Matches hand label |
|---|---|---|---|---|---|---|---|
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | relevant | 4 | 0 | 0 | 4/4 | 4/4 |
| 8041054003 | Software Engineer, Conversational Products & Agent Workflows | relevant | 4 | 0 | 0 | 4/4 | 4/4 |
| 7822352003 | Full Stack Software Engineer - People Systems (San Francisco) | not_relevant | 0 | 4 | 0 | 4/4 | 4/4 |
| 7777369003 | Senior Software Engineer - Infrastructure Security | not_relevant | 0 | 2 | 2 | 2/4 valid | 2/4 |
| 8035953003 | Senior Machine Learning Platform Engineer | not_relevant | 0 | 4 | 0 | 4/4 | 4/4 |

**Spread.** No posting got both `relevant` and `not_relevant`: 18 of 20 calls passed the validator, and all 18 matched the hand label. The only variation was in **format**. Two calls on 7777369003 were rejected as `invalid`.
- **Why they failed:** both cited `"resume_field": "devops_cicd"`, which is missing the required `skills.` prefix.
- **What was inside:** the JSON in both still said `not_relevant`.
- **The other two calls on that posting** cited the path correctly (`skills.devops_cicd`) and passed.

**The justifications varied even where the verdict did not.**
- **8041054003:** across its four calls Claude cited 8, 6, 6, and 7 pieces of evidence. AWS appeared in only two calls. One call paired `target_titles: "backend engineer"` with the content phrase "This is a backend-heavy role".
- **7822352003:** two calls cited `target_titles`, and the other two cited `years_experience` twice instead. Every call cited the location mismatch: résumé `Boston, MA` against posting `San Francisco, CA`.
- **7855793003 and 8035953003:** these cited the same evidence each time, sometimes in a different order.

## What this can and cannot show

**It can show:**
- **For these five postings, under this prompt and model on this date, the verdict was repeatable.** Every valid answer was the same verdict for a given posting.
- **That verdict matched the labels I reviewed every time it was valid.**
- **Format compliance was less repeatable than the verdict.** Two of four calls on one posting were unusable; four calls do not establish a general failure probability.

**It cannot show:**
- **Correctness.** Four identical answers are one judgment repeated, not four independent confirmations. The comparison that matters is with the reviewed label, which can still be wrong.
- **That the judge is reliable in general.** Five postings and four calls each is a tiny sample. Three of the five are decided by title (Senior) or by location, which are the easiest calls.
- **Anything about other models, other efforts, or later dates.** The served model was `claude-opus-5-5` for all 20 calls, so no fallback model answered.
- **That the justifications are sensible.** The validator checks only that a cited value exists in the résumé and the cited phrase exists in the posting. It does not check that the pairing makes sense. The `"backend engineer"` ↔ "backend-heavy role" citation passed even though "backend engineer" is not in the posting's title.

## What I would change next time

- **Sample harder cases.** Use postings near the boundary of my labeling rule, such as three-year requirements or role mixes where backend work is only part of the job. Those are where verdicts could split.
- **Record the invalid outputs' inner verdicts separately.** "Invalid" mixes "unusable" with "would have agreed".
