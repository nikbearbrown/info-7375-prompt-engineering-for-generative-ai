# Prompt experiment (Chapter 2)

Pass rate = how often Claude's verdict equals my hand label (`experiment/labels.csv`, written before any Claude answer). An invalid reply counts as a fail. Development set: 10 postings. Held-out set: 10 postings, run last, once per prompt, and never used to change a prompt.

## The one change

| | File | What it says about experience |
|---|---|---|
| Baseline | `experiment/prompts/baseline.md` | the title has no senior/intern word, and the description does not ask for 3 or more years |
| Revision | `experiment/prompts/revision-no-years.md` | the title has no senior/intern word. Do not use any years of experience the description asks for. |

Nothing else differs (`diff` shows one changed line: line 6). I chose this change after the baseline dev run, because my hand labels did not check years.

Prediction, written before the revision ran: dev goes from 3/10 to about 7/10. 7661919, 8009057, 5552549004 and 5691886004 should flip to Relevant and match my labels. 5551730004 should stay Not Relevant (no matching skills). 8213988 and 8026211 should stay Relevant and still not match.

## Results

All four runs used `python3 -m agent experiment PROMPT --split dev|held-out`, model `claude-sonnet-5-5`, one fresh `claude -p` conversation per posting. Every reply is saved in `evidence/claude/experiment/<prompt>-<split>/`, and each run's `results.md` has the full table with Claude's reasons.

| | Dev (10) | Held-out (10) |
|---|---|---|
| Baseline (`baseline.md`) | 3/10 (2026-10-31 00:27:55Z) | 4/10 (16:37:46Z) |
| Revision (`revision-no-years.md`) | 7/10 (16:36:42Z) | 8/10 (16:38:45Z) |
| For comparison: "Not Relevant" every time | 5/10 | 4/10 |
| For comparison: the written rule (record) | 3/10 | 4/10 |

Invalid replies: 0 of 40.

* The prediction held. On dev, the four predicted postings flipped to Relevant and matched my labels, and the other three misses stayed as predicted.
* Held-out ran last. It was run once per prompt after the revision was fixed, and nothing was changed after seeing it. The revision went from 4/10 to 8/10 there too, so the gain was not only on the postings I looked at.
* The baseline did no better than answering "Not Relevant" every time (3 vs 5 on dev, 4 vs 4 on held-out). With the baseline, Claude agreed with the written rule on all 20 postings.

## Second measurement: against the written rule (added 2026-10-31, after the experiment)

After all four runs, a ChatGPT cross-check of my draft recomputed my 20 labels with the rule in `CONTRACT.md` and found that 13 differ. `python3 -m agent audit` now scores the saved replies a second way: against the written rule (the record) instead of my labels. No prompt was re-run, no label was changed, and the held-out set was not used to change anything. Full table: `experiment/label-audit.md`.

| Compared with | Baseline, dev | Revision, dev | Baseline, held-out | Revision, held-out |
|---|---|---|---|---|
| My hand labels | 3/10 | 7/10 | 4/10 | 8/10 |
| The written rule (record) | 10/10 | 6/10 | 10/10 | 6/10 |

* The revision matched my labels more and my contract less. It flipped 8 postings to Relevant (4 dev, 4 held-out). Every one of them asks for 3 or more years, so the written rule says Not Relevant.
* My labels differ from my own written rule on 13 of 20 postings. 9 are Relevant by my label but fail the rule: all 9 ask for 3 or more years, and 5551730004 also names too few of Rohan's skills. 4 are Not Relevant by my label but pass all four parts of the rule (8213988, 8026211, 7838591, 8026207): I left them out by role type.
* So the jump from 3/10 to 7/10 measures how closely Claude copies my labelling, not how well it applies my contract. The baseline applied the contract on all 20 postings. So a prompt can score higher against labels while following the contract less.

## My conclusion

The scores improved, but I am not sure the answers actually got better. The new prompt matched my labels more closely, but I may have made mistakes when labeling the jobs.

## Honest limits

* The higher score does not mean Claude judged better. The revision matches my labels more because it copies how I labelled: by title, without reading years. It drops the contract's rule that the description asks for under 3 years. Against the written rule it fell from 10/10 to 6/10 on both sets. For a 0–2 year candidate, a job asking for 4+ or 5+ years is a weak match, and the revision calls those Relevant.
* The watcher still uses `baseline.md` and the written rule, which follow `CONTRACT.md`. The baseline matched the written rule on all 20 postings; the revision matched it on 12. The revision is only part of this experiment.
* Both prompts still miss the same 4 postings: 8213988 and 8026211 (dev), 7838591 and 8026207 (held-out). Both prompts call them Relevant and I labelled them Not Relevant, so no wording change about years can fix them. 5551730004 is a miss for both because its description names none of the candidate's skills.
* The sets are small. Ten postings per set means one posting moves the score by 10 points. Each prompt ran once per posting. The sampling report showed repeatable verdicts for the baseline on five postings, but the revision's repeatability was not tested.
* One labeller and one model. The labels are mine, from one sitting, and stayed unchanged after I saw Claude's answers, even though 13 of 20 differ from my written rule. Only `claude-sonnet-5-5` was tried.

# Experiment 2: 20 new postings (2026-10-31)

After the label audit I repeated the experiment on 20 new postings from seven more boards, frozen and labelled before any Claude answer (`experiment-2/README.md`). Experiment 1 above is unchanged.

Labels: 8 Relevant, 12 Not Relevant. Claude Code listed each posting's years lines and résumé skills by text search; I decided the labels: "all more than 3 yoe skip it i wont apply" and "ok all the others i would recommend" (`experiment-2/my-labels.txt`). They agree with my written rule on 16 of 20; the 4 others name fewer than two of Rohan's skills.

The one change: `experiment-2/prompts/revision-range-lowest.md` adds to line 6: *If the description gives a range of years, such as "2–12+ years", use the lowest number.* I left the choice to Claude Code; it chose this over "accept one skill", which would have copied my labels instead of my contract. Why I accepted it, in my words: "yes because there could be multiple postings based on the yoe so thats why i feel its better to consider the lower bound since they have mention ed and sk;ll matches". Prediction, written before the revision ran: dev stays 8/10.

| | Dev (10) | Held-out (10) |
|---|---|---|
| Baseline (`experiment/prompts/baseline.md`) | 8/10 (22:46:45Z) | 8/10 (22:50:38Z) |
| Revision (`revision-range-lowest.md`) | 8/10 (22:49:37Z) | 8/10 (22:51:30Z) |
| For comparison: "Not Relevant" every time | 6/10 | 6/10 |
| For comparison: the written rule's code (record) | 7/10 | 6/10 |

Invalid replies: 0 of 40. Every reply and each run's `results.md` are in `evidence/claude/experiment-2/`.

* The prediction held, and the change made no difference. Both prompts gave the same verdict on all 20 postings. The baseline already read both ranges (6176758, 7292520) by the lowest number.
* All 4 misses are the same kind: I labelled Relevant postings that name fewer than two of Rohan's skills (8147559 and 8546367002 on dev, 7819445003 and 8089353 on held-out). Claude followed my written two-skill rule there; I went by years only.
* Claude read years better than my own code. The record read "2–12+ years" as 12 (6176758, 7292520) and "1.5+ years" as 5 (8003020003), so it called those three Not Relevant. Claude read the lowest number and 1.5. The decimal reading is now fixed in `agent/rule.py` (`test_experience_reads_decimal_years_whole`), so the record says Relevant for 8003020003. Ranges are left as they are: my contract does not say how to read them, and reading the lowest number would also change experiment 1's 7661919 ("Minimum 2-3+ years"), which Claude read as 3. The table shows the record as it was when the runs were made.
* Limits: ten postings per set, one run per prompt, one labeller and one model. A change that makes no difference on 20 postings can still matter on others.
