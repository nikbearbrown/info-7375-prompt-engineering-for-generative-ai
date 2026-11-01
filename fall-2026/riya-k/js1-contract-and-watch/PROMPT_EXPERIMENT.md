# Prompt experiment (Chapter 2)

## Setup

- **Postings:** 20 real postings from the live Databricks board fetched on 2026-10-31 (`snapshots/databricks-2026-10-31T233230Z-live.json`),
  picked by `experiments/select_postings.py` (seed 7375) in three strata: 8 with a title word and no seniority word,
  4 early-career, and 8 others. Positives are rare on this board, so likely candidates are oversampled. Then a random 10/10 split
  into development and held-out sets.
- **Labeling rule (written first, in CONTRACT.md):** relevant if Arya could apply honestly today: the role matches her
  AI/ML/data target, it is not senior, and she has at least 2 of the core skills the posting asks for. While labeling
  I added one blanket rule in the chat: any posting outside the US is not relevant.
- **Labels:** `labels/hand_labels.csv`, committed in c665200 **before** any Claude call on these postings.
  Dev: 2 relevant and 8 not. Held-out: **0 relevant** and 10 not.
- **Pass:** Claude's verdict equals my hand label. A reply the validator rejects counts as a fail.
- **Calls:** one fresh `claude -p` call per posting per prompt, model `claude-sonnet-5-5`, 2026-10-31 ~23:50 UTC.

## The one change

| prompt | file | difference |
|---|---|---|
| v1 baseline | `experiments/prompts/v1_baseline.md` | task, résumé, posting, and a fixed JSON output format |
| v2 revision | `experiments/prompts/v2_criteria.md` | v1 **plus one paragraph**: my labeling rule, including "located in the US" |

`diff experiments/prompts/v1_baseline.md experiments/prompts/v2_criteria.md` shows exactly that paragraph and a blank line.
I chose this change after seeing v1 on dev (9/10, with #4 the only miss). The question was: does giving Claude **my** criteria bring it closer to **my** labels?

## Run order (evidence that held-out ran last and the prompts didn't change)

From `called_at` and `prompt_sha256_12` in the results files (all 2026-10-31 UTC):

| run | calls between | prompt sha256 (first 12) |
|---|---|---|
| v1 dev | 23:50:44 – 23:50:51 | 5905a4d83c50 |
| v2 dev | 23:55:29 – 23:55:37 | 5e31e6e8294d |
| v1 held-out | 23:55:46 – 23:55:54 | 5905a4d83c50 |
| v2 held-out | 23:55:58 – 23:56:04 | 5e31e6e8294d |

Each prompt's hash is the same on dev and held-out, so neither prompt was edited between the two runs. The held-out calls came
after both dev runs. The dev and held-out results share one commit (105f2ba), so this ordering rests on the recorded timestamps,
not on commit order. I did not freeze the prompt hashes in a separate commit before the held-out run.

## Results (recomputed by `python3 -m experiments.summarize`)

| judge | dev (10) | held-out (10) | rejected by validator |
|---|---|---|---|
| Claude, v1 prompt | 9/10 | 10/10 | 0 |
| Claude, v2 prompt | 8/10 | 10/10 | 1 |
| written rule (record) | 8/10 | 10/10 | n/a |
| always "not_relevant" | 8/10 | 10/10 | n/a |

Per-call results: `experiments/results/v{1,2}_{dev,heldout}.jsonl`.

- **Dev:** v1 missed only #4, where my label was wrong (see SAMPLING.md). v2 also missed #4, and its reply on #7 was
  **rejected**: the key was `" justification"` with a leading space and there was extra text after the JSON. So v2's lower dev score
  comes from a format failure, not a different judgment.
- **Held-out:** both prompts scored 10/10, and so did the rule and "always say no". **All 10 held-out labels are
  not_relevant**, so this set cannot tell any of these judges apart.

## My decision

I made **no prediction** before running v2, and I had no keep/reject rule written down in advance. After seeing the results I decided
(2026-10-31): **keep v1.** v2 did not improve dev (8/10 vs 9/10), its only extra miss was a format error, and the held-out set can't tell
the two apart. A v2 win on a held-out set that has positive labels would have changed this.

## Honest limits

- **Ten cases show almost nothing.** The whole difference between v1 and v2 is one malformed reply. I can't say
  v2 is worse, and I can't say adding my criteria helps.
- **The held-out set has no positive cases.** 10/10 there is what a judge that never says "relevant" would get. The
  random split put both of my yeses into dev. Next time I'd stratify the split by label.
- **One of my two positive labels (#4) is itself wrong.** On the only posting where v1 "failed", Claude was right and my label was not.
  The answer key has errors too.
- **My written rule matched "always no" on all 20.** It said not relevant to every posting. It misses #3 and #4 because
  "Solutions Engineer" and "Software Engineer" are not in my title-word list. That's a gap in the rule, not a bug in the code.
- One call per posting per prompt: the sampling report shows a borderline posting can flip between calls.
