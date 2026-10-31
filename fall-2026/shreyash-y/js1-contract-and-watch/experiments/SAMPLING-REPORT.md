# Sampling report (Chapter 1)

*Written by Claude Code on 2026-10-31 from the saved calls. Every number below can be recomputed from `experiments/sampling/sample-summary.jsonl` and the 20 files in `experiments/sampling/calls/`. The table comes from `experiments/sampling/spread-2026-10-31.txt`.*

## What was asked

- **Question:** the baseline prompt contract ([prompts/baseline-v1.md](../prompts/baseline-v1.md), sha256 `60bc794a6b2e…`).
- **Postings:** the first 5 development postings in the order fixed by [selected_postings.json](selected_postings.json), committed before any call.
- **Calls:** 4 per posting, each a fresh `claude -p` conversation. Tools were disabled, no session was saved, and each ran from an empty temporary folder.
- **When and which model:** 20 calls on 2026-10-31 between 19:55:12 and 19:55:41 UTC. Model `claude-opus-5-5` at the CLI's default settings; the CLI exposes no temperature setting.
- **Pass mark:** a fifth answer per posting comes from the development run of the prompt experiment, made with the same prompt the same day. The hand label is Shreyash's ([labels/hand-labels.csv](../labels/hand-labels.csv)).

## What came back

| Posting | Title | 4 verdicts | Failed conditions in the 4 calls | 5th call | Hand label | Rule record |
|---|---|---|---|---|---|---|
| 8264996 | Senior Market Researcher | 4 × Not Relevant | [1,2,3,4,5] × 4 | same | Not Relevant | [1,2,3,4,5] |
| 8188906 | Manager, Data Mining | 4 × Not Relevant | [1,2,3,4,5,6] × 4 | same | Not Relevant | [1,2,3,4,5,6] |
| 8083703 | Senior Data Scientist | 4 × Not Relevant | [1,2,3,5] × 4 | same | Not Relevant | **[1,2,3]** |
| 6555819 | Staff Software Engineer, Backend | 4 × Not Relevant | [3,4,5,6] × 4 | same | Not Relevant | **[4,5,6]** |
| 8289735 | Director of Product | 4 × Not Relevant | [1,2,3,4,5,6] × 4 | same | Not Relevant | [1,2,3,4,5,6] |

- **Validator:** 20 of 20 answers passed.
- **Verdicts:** none varied. Each posting got the same verdict and the same failed-condition set every time.
- **Fields cited:** the `resume_fields` set was the same on all four calls for every posting.
- **Wording:** this is what varied. All 20 justifications are different texts, and the length ranged from 77 to 109 words.

## What this shows and does not show

- **Repeatability, not correctness.** Twenty-five answers agree with each other, and that tells us nothing about whether they are right.
- **Where repeatability met a disagreement.** On 8083703 and 6555819 Claude gave the same answer every time, and that answer disagrees with the rule's record. Reading the ad text sided with Claude both times:
  - **8083703:** the ad asks for "4+ years of industry or other quantitative technical fields". The rule's experience pattern misses this because the word "experience" isn't there.
  - **6555819:** the office tag is "Remote", but the ad says "This is a hybrid position, you will need to live within commutable distance" of New York, Tempe or Los Angeles.

  A model that is consistently right and a rule that is consistently wrong look exactly alike in a repeat test. Only reading the source separates them.
- **The hand label settles only the verdict.** All five hand labels are Not Relevant, so they confirm the verdicts but say nothing about which conditions failed. Shreyash recorded verdicts only. The reading of the two ads above was done by Claude Code, which then checked that the quoted words are in the saved raw response. It is not a hand label.
- **Too easy a test.** Four calls on five easy postings cannot show how Claude varies on a hard case. Every one of these postings fails at least two conditions, so the verdict was never close. A posting that fails only on a borderline experience reading would be a better test, and none was in the sample.
- **One snapshot.** One model on one day, called within 30 seconds. Nothing here says the answers will be the same next week or on another model.
