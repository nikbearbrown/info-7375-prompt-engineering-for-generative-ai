# Prompt experiment (Chapter 2)

## Design

- **Labels:** Aditya hand-labelled 20 real postings from the 2026-10-30 snapshot using his CONTRACT.md §4 rule, which was written before any labelling. He confirmed he saw no model output, groups or RECORDs before or while labelling.
- **Sample:** a deliberately selected **diagnostic** sample (`experiments/SAMPLE_PROCEDURE.md`, seed 7375), **not representative of the board**. It contains 5 rule-relevant postings, 7 near-misses and 8 others.
  - Dev: 3 / 3 / 4. Held-out: 2 / 4 / 4.
  - Duplicate jobs are kept in the same split. The procedure needed no adjustment.
- **Prompts:**
  - **Baseline:** `prompts/judge_v1.md`.
  - **Revision:** `prompts/judge_v2.md`, which changes **one thing**. It adds a "Résumé check first" paragraph: find the résumé entry before citing a skill, because a skill in no résumé array can never count.
  - **Origin of the change:** Claude identified the problem and proposed the change. Aditya accepted the stated rationale on 2026-10-30.
  - **Rationale:** it targets the one unsupported-evidence failure observed anywhere. In watch run 2, attempt 1 on posting 8892970002 cited `spark` from `skills.languages`, and the validator rejected it. That posting is **in neither split**.
- **Freeze:** both prompts were frozen at 2026-10-30 17:46:59 EDT, with their hashes in `prompts/FROZEN.json` (commit `469d0a2`). That was before any held-out call (commit `f97aca7`) and before any hand label was received.
- **Settings:** each posting was evaluated once per prompt in a fresh, isolated `claude-opus-5-5` CLI session (effort `medium`, temperature not controllable).

## How the outcomes are counted

- **Format/contract pass:** the response passes `agent/validate.py`. That means exact JSON keys, an allowed verdict, the matching `posting_id`, cited quotes found in the posting, cited skills present in the cited résumé array, and internal consistency.
- **Agreement (strict):** valid **and** the verdict equals the hand label. An invalid response counts as **wrong** and is never converted into a verdict.
- **Agreement among valid:** reported separately, as `correct/valid`.

Every rate is given as a count over its denominator (n = 10 per split).

## Reference points kept separate

1. **Agreement with the deterministic RECORD.** Known now: v1 and v2 each matched the RECORD on 10/10 dev postings, with 10/10 valid. *This is not the experiment's measure.* The prompt restates the rule, so agreeing with the RECORD shows rule-following, not correctness against a human.
2. **Agreement with Aditya's hand labels.** This is the experiment's measure. The labels were received 2026-10-31 14:33 EDT, committed as received (`83c0b7e`), then quote-repaired with no label changed (`4d6322a`).
3. **The "always not_relevant" baseline,** which shows how much a trivial classifier would score: dev 7/10, held-out 8/10.

The hand labels and the RECORD agree on all 20 postings (dev 10/10, held-out 10/10).

## Results

Recompute with `.venv/bin/python experiments/score.py prompt`. The full per-posting tables are in `experiments/prompt_experiment/results_tables.md`.

| split | hand labels (R / N) | "always not_relevant" | prompt | format/contract pass | agreement, invalid = wrong | agreement among valid | confusion (label → prediction) |
|---|---|---|---|---|---|---|---|
| dev | 3 / 7 | 7/10 | v1 | 10/10 | 10/10 | 10/10 | R→R 3, N→N 7 |
| dev | 3 / 7 | 7/10 | v2 | 10/10 | 10/10 | 10/10 | R→R 3, N→N 7 |
| held-out | 2 / 8 | 8/10 | v1 | 10/10 | 10/10 | 10/10 | R→R 2, N→N 8 |
| held-out | 2 / 8 | 8/10 | v2 | 10/10 | 10/10 | 10/10 | R→R 2, N→N 8 |

There were no invalid responses, so the strict and among-valid rates coincide. v1 and v2 gave the same verdict on every one of the 20 postings.

## Independence of the held-out set (checked 2026-10-30)

- **Spark posting:** the posting that motivated v2 (8892970002) is in neither dev nor held-out.
- **No held-out label or held-out experiment result** was available or used before the freeze. Held-out experiment calls happened only after it.
- **Disclosed exposures** that did not inform the revision:
  1. **The pre-approval feasibility count** (before the sample existed) printed the titles, locations and RECORD verdicts of all 5 rule-relevant postings. Two of them later became the held-out group R.
  2. **Watch run 2** judged all 258 new postings with prompt v1 before the freeze. One held-out posting is among them. Its individual result was never displayed; it entered the assistant's view only through the aggregate "258/258 RECORD–JUDGMENT agreement" count.
  3. **The held-out composition by RECORD group** (2/4/4) is known, because the frozen procedure fixes it.
- **A fresh held-out set is not possible** under the frozen procedure. It requires all 5 rule-relevant postings, and every one is already in the sample (and was exposed by item 1). The original held-out set is therefore kept, and these exposures are disclosed rather than hidden.

## Limits

- **Small and selected:** n = 10 per split, chosen by the rule's own groups. One posting changes a rate by 10 points, and nothing generalises to the board.
- **Ceiling on dev:** both prompts already matched the RECORD on 10/10 dev postings. The dev set therefore can't show improvement; at most it shows that v2 does no harm.
- **The targeted failure is rare:** it occurred in 1 of 259 watch-run attempts. A 10-posting held-out set is unlikely to contain that failure even once, so this experiment is underpowered to show whether v2 fixes it.
- **One call per posting per prompt:** sampling noise isn't averaged out.

## Conclusion

**The revision did not measurably help, and it did not hurt.** Both prompts scored 10/10 on both splits, so this experiment cannot tell them apart.

What the results support:
- Both prompts beat the trivial "always not_relevant" baseline by exactly the relevant postings: +3 on dev, +2 on held-out. They found every posting Aditya labelled relevant and flagged no extra ones.
- The held-out score matches the dev score, so nothing points to overfitting to the dev set. With n = 10 and a ceiling result, that is weak evidence.

What they don't support:
- **That v2 fixes the failure it targets.** That failure (an unsupported résumé citation) occurred once in 259 watch-run attempts and never in the 40 experiment calls. Testing it would take many more calls, or postings chosen to tempt that failure, such as descriptions that mention Spark.
- **That the model would agree with a different person's judgment of a job.** The hand labels apply the same written rule the prompt restates. 20/20 shows Claude followed Aditya's rule, not that the rule picks good jobs.

**Next step, if continued:** build a test set aimed at the failure, for example postings that mention Spark and other skills not on the résumé. Run v1 and v2 several times each, and compare validator-rejection rates rather than verdict agreement.
