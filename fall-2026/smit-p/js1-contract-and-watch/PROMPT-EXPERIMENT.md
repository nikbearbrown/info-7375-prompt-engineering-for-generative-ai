# Prompt experiment (Chapter 2)

> **Authorship.** Drafted by Claude Code from runs it carried out on 2026-10-24 in Smit P.'s session. The hand labels and the decisions are Smit's (see DECISIONS.md). Every number can be recomputed with `python3 experiments/score.py`.

## Executive summary

I hand-labeled 20 real Airbnb engineering postings, then tested two versions of the
instructions given to Claude: a baseline, and a revision that changes exactly one thing
by adding "the job must be in the US." The revision fixed the mistake it was aimed at:
Claude stopped calling jobs in Brazil relevant. But it broke the required answer format
three times, because Claude quoted the job's location and the format has nowhere to put a
location. Net result: both versions passed 9 of 10 on the held-out postings. Ten cases,
only one of which I labeled relevant, cannot tell these two prompts apart. What the
experiment does show is a real bug in my output format.

## Design

| | |
|---|---|
| Postings | 20 real postings from the 2026-10-24 Airbnb fetch (`runs/raw-20261024T192545-live.json`) |
| Selection | postings with "engineer" in the title, stratified: all 6 non-senior titles plus 14 random senior-titled ones, seed 7375, split 10 development / 10 held-out (`experiments/selection.json`). A first unstratified draw had 19/20 senior titles and was discarded before any labeling (`selection-v1-degenerate.json`, see FRICTIONAL.md) |
| Labels | mine, under `experiments/LABELING-RULE.md` **v2** (Software/Cloud/Full-Stack IC, not Senior/Staff/Principal/Manager, ≤4 years, US or remote-US). Committed (`56ca4e8`) before any prompt ran |
| Label balance | development: 0 relevant / 10 not. Held-out: **1 relevant** / 9 not |
| Baseline | `prompts/baseline.md`: the CONTRACT.md rule (title, seniority, ≥2 skills) plus the fixed JSON output format |
| Revision | `prompts/revision.md`: **one change**, a 4th condition: "The posting location is in the United States or is remote within the United States." (plus "three" → "four") |
| Why that change | **chosen by Claude, not by me**, about 13 seconds after the development baseline finished (`asked_at` in the result files). The Brazil miss (8154749, Software Engineer, São Paulo) had already shown up 4/4 in the sampling run, which uses 5 of the development postings. The development baseline confirmed it as the only development miss |
| Pass | the reply is ACCEPTED by the validator AND its verdict equals my label. A rejected reply fails |
| Model / calls | `claude-sonnet-5-5`, one fresh conversation per posting per prompt, 40 calls |
| Order | dev-baseline → (choose revision) → dev-revision → held-out baseline → held-out revision. Held-out results were not looked at until both prompts were fixed |

## Results

| set | prompt | n | accepted | rejected | **pass** | false relevant | false not-relevant |
|---|---|---|---|---|---|---|---|
| development | baseline | 10 | 10 | 0 | **9/10** | 1 | 0 |
| development | revision | 10 | 8 | 2 | **8/10** | 0 | 0 |
| held-out | baseline | 10 | 10 | 0 | **9/10** | 1 | 0 |
| held-out | revision | 10 | 9 | 1 | **9/10** | 0 | 0 |

Every miss (from `experiments/results/SCORES.md`):

| set | prompt | posting | location | mine | Claude | what happened |
|---|---|---|---|---|---|---|
| dev | baseline | 8154749 Software Engineer, Tech Foundations | São Paulo | not | relevant | prompt has no location condition |
| dev | revision | 8154749 (same) | São Paulo | not | REJECTED | verdict `not_relevant` was right, but it quoted «Sao Paulo - Brazil» as `content`, and the location is not in the content |
| dev | revision | 8312713 Systems Engineer (Jira cloud) | Bangalore | not | REJECTED | same: right verdict, location quoted as content |
| held-out | baseline | 8263303 Software Engineer, Analytics Infrastructure | Brazil | not | relevant | prompt has no location condition |
| held-out | revision | 8053132 Senior Business Solutions Engineer | Bangalore | not | REJECTED | quoted location as `title`, then added a prose "Correction:" after the JSON. Not a bare JSON object |

For comparison, the **written rule** (a record) scores 9/10 on development and 9/10 on
held-out, missing exactly the same two Brazil postings as the baseline prompt.

## What it shows

1. **The revision fixed the verdict it targeted.** The sample has 6 postings outside the
   US (China, Brazil ×2, India ×2, UK). The revision's reply on 3 of them was readable,
   and all 3 were right. The other 3 were rejected for format, though the verdict inside
   each was also right. False-relevant replies went from 1 to 0 on both sets.
2. **The revision broke the format.** All 3 rejections share one cause. Adding a location
   condition made Claude want to cite location as evidence, and my output contract only
   allows `title` or `content`. The validator did its job: it refused to accept a quote it
   could not find, even when the verdict was right. The next fix is in the format (add a
   `location` evidence field), not the wording. It would be a second change, so it is
   **not** made here.
3. **The pass rate did not move on held-out (9/10 → 9/10).** The gain on verdicts was
   offset exactly by a format failure.

## Honest limits

- **Ten cases show very little.** With one relevant posting in held-out and none in
  development, the experiment has almost no power to detect missed relevant jobs (false
  negatives). A 9/10 pass rate is consistent with a true rate anywhere from about 55% to
  99.7% (exact binomial 95% interval).
- **The labels are lopsided** because Airbnb's board is mostly senior roles (46 of 52
  engineering titles are senior). "Always say not relevant" would score 10/10 on
  development and 9/10 on held-out, as well as either prompt.
- **My labeling rule changed mid-labeling** (v1 → v2, `LABELING-RULE.md`). No model
  output had been seen at that point, but it is still a weakness.
- **The revision was chosen from one development miss.** That is overfitting-shaped even
  though it held up on held-out.
- **The held-out set was not completely unseen.** No Claude *judgment* was run on it
  until both prompts were fixed. But when the 20 postings were drawn, Claude printed
  every held-out title, location, and rule verdict, before choosing the revision. So
  Claude had seen that the held-out set also has postings in Brazil and India. I cannot
  rule out that this influenced the choice of a location condition.
- The prompt contract adds the location condition, but the **written rule in
  CONTRACT.md does not**. The record and the judgment now follow different rules. That
  is deliberate (the contract was written first and is not edited after the fact), and
  it is the next thing to fix in layer 2.
- One run per prompt per posting. The sampling report shows the verdict is stable but the
  format fails about 5% of the time, so a single rejection could be noise.
- Neither prompt checks years of experience, which my labels use. No posting in this
  sample tested that gap.
