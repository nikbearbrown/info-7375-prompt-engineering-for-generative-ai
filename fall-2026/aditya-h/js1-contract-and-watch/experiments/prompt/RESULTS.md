# Prompt experiment — results (Chapter 2)

The plan, frozen before any experiment call: [`PLAN.md`](PLAN.md). The labeling rule, written before labeling: [`LABELING-RULE.md`](LABELING-RULE.md).

**Runs:** 40 real `claude -p` calls (model `claude-sonnet-5-5`), on 2026-10-31 between 23:01 and 23:04 EDT. Each call was a fresh conversation with no tools. Raw replies are in `results/*.jsonl`. Scores are recomputed with:

```bash
python3 experiments/run_experiment.py --score
```

## Order of events (as it happened)

1. Claude Code picked the 20 postings (seeded and stratified; `select_postings.py`). The first draw was discarded because it put no PM titles in dev.
2. Aditya chose the labeling rule: "the contract rule".
3. Both prompts were frozen (commit `774c98e`). v2 = v1 plus the contract rule text.
4. All 40 experiment calls were collected. Collecting replies does not read the labels.
5. Aditya hand-labeled the 20 postings in chat. Nothing from these experiment calls was shown to Aditya first. (One earlier smoke-test verdict, on 8275556, had been shown; see `evidence/`.) Labels committed in `16a72a1`.
6. Scoring. The hand labels agreed with the rule's recomputed verdicts on **18/20**. Aditya reviewed the two mismatches, 8331852 (Toronto office) and 8238100 ("Product Counsel"), and called both **labeling slips**. The original labels are kept in `labels.csv` next to `corrected_label` and a dated note (commit `4158a63`).

## Scores

**Pass** = the reply is valid under the validator **and** the verdict equals the label.

| prompt | set | n | valid | pass vs original hand labels | pass vs corrected labels |
|---|---|---|---|---|---|
| v1 (no definition) | dev | 10 | 10 | 7/10 | 7/10 |
| v2 (+ contract rule) | dev | 10 | 10 | **10/10** | **10/10** |
| v1 (no definition) | held-out | 10 | 10 | 5/10 | 7/10 |
| v2 (+ contract rule) | held-out | 10 | 10 | 8/10 | **10/10** |

All 40 replies passed the format validator. No reply was `invalid`.

## What the misses were

- **v1, all 8 misses vs the original labels:** v1 said `not_relevant` for PM-family US roles because the posting asked for more experience than Maya has. For example: "requires 10+ years of product management experience, while the candidate has roughly 1.5 years" (7983725), "requires 5+ years" (8275556, 8248415), "requires 12+ years" (8226893). **v1 brought in its own criterion, seniority, which my rule deliberately excludes.** Its two held-out "misses" against the original labels (8331852, 8238100) were actually correct under the rule.
- **v2, both held-out misses vs the original labels:** these were the same two postings, and in both v2 applied the written rule correctly. For example: "the location is Toronto, Canada and the office is 'Canada Locations'". Against the corrected labels, v2 missed nothing.

## What I can conclude

- **The one change mattered, for this rule.** Spelling out the definition took dev from 7/10 to 10/10, and held-out from 7/10 to 10/10 (corrected labels). The direction held on the set I didn't tune on, and the misses had one consistent cause (seniority), so I don't think it's chance. With 10 cases, though, the size of the effect is weakly measured: one case is 10 points.
- **An unexpected result:** v2 was more consistent with the written rule than my own hand labels were (18/20). The experiment exposed two errors in *my* labeling. I'd only have found them by recomputing the rule against my labels.

## What I cannot conclude

- **That v2 is good at finding jobs Maya should take.** Both the labels and v2 encode the same narrow rule, so v2 scoring 10/10 mostly shows that Claude can follow an explicit rule. Claude was the more reliable labeler here, and that isn't evidence that the rule is a good one.
- **Anything general.** This is 20 postings, one board, one day, and one model. There was one sample per (prompt, posting) pair; run-to-run spread is in [`../sampling/REPORT.md`](../sampling/REPORT.md).
- **That v1 is "wrong" in an absolute sense.** Its seniority objections are arguably useful to a real job seeker. It just doesn't measure what my rule measures.
- **That the held-out set was untouched in every sense.** Its replies were collected alongside dev, before scoring. This is acceptable only because neither prompt was changed after any result, which the frozen-prompt commit shows.
