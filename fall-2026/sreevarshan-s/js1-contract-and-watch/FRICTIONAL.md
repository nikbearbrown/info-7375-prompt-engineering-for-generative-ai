# Friction and corrections

## My words (verbatim)

**Q33.** My initial contract didn't include AI/ML Engineer as Priya's main target, and I originally misunderstood the two persona files. I also included PyTorch, TensorFlow, scikit-learn, and Spark without evidence that those skills appeared in her résumé. [correction: PyTorch, TensorFlow, scikit-learn and Spark were added in Draft 1 (`d6c24ff`), not Draft 0, and removed in Draft 3 (`67d61b8`).] These problems made me realize that the rules must be tied directly to the actual persona data.

**Q34.** I accepted the approach of preserving contract drafts in Git history, using a strict job-board allow-list, keeping rule-based and Claude judgments separate, and saving the baseline response and state as evidence. I'll document any implementation suggestions I accepted only after checking the relevant code or commit.

**Q35.** I corrected the target roles, removed unsupported résumé skills, made sponsorship handling more explicit, and replaced vague title-matching rules with more predictable checks. I also decided that Claude should not see the rule-based verdict before making its independent judgment.

**Q36.** At this stage, the second live watch run, the 20 independent hand labels, the repeated Claude sampling, the prompt experiment, and the full action-surface comparison still need verification or completion. I'll update this section as work is completed and leave any remaining limitations visible rather than hiding them.

**Status since Q36 (factual, 2026-10-31):**
- **Second live watch run:** done, `0dd01ab`. 901 fetched, 10 new, 14 removed.
- **20 hand labels:** done, `f55b88d`. All "not relevant".
- **Repeated Claude sampling:** done in the Claude app, `6064e8e`, with the report in `f3399e8`. 19/20 valid, all "not relevant".
- **Prompt experiment:**
  - Dev split done, `d7411f4`: baseline 10/10, revised 9/10, rule 9/10.
  - Held-out split: the CLI attempt was unusable because of the usage limit (`4a46925`). Rerun in the Claude app, `f5c008d`: baseline 10/10, revised 10/10, rule 9/10.
- **Action-surface comparison:** done on 8546367002, `3484999`.
- **Claude judgments for the 10 new watch postings:** not run before submission. The prompts are built (`experiments/watch_app/prompts/`); no replies exist. Rule records exist for all 10.

## Log

All entries come from the commits and notes in this repo or from the Claude Code session record. Dates are local (ET); UTC stamps are given where the evidence uses them.

**2026-10-29: board-survey crash.** In the survey before Draft 0, Claude Code's parser crashed on an f-string quoting bug after the boards had been fetched. All 8 boards were then fetched a second time.

**2026-10-29: blank Draft 6 avoided.** The first Draft 6 handed to Claude Code had empty answers. It was not committed; it was removed and later replaced by the real Draft 6 (`4da69e5`).

**2026-10-29: wrong sentence pointer in Draft 7.** Draft 7 told Claude Code to act on "the second sentence of D6-C§5", which the chat assistant had pointed to. That sentence was not the one meant. Claude Code flagged it, kept "Matching should be case-insensitive", and dropped the other sentence (`dfb37a7`).

**2026-10-29: denial-phrase approval wrongly called a contract requirement.** The chat assistant said the contract required me to approve the sponsorship denial phrases. Claude Code pointed out that it did not. My approval is recorded in `IMPLEMENTATION_CHOICES.md` as "my own approval step, not a contract requirement" (`a4021ff`).

**2026-10-29: "Databricks" as a company name.** "Databricks" appears in every posting because it is the employer's name (905 of 905 in the baseline), so counting it as a skill would match every posting. I chose option B in Draft 8 (`b8a5b81`): Databricks counts only when asked for as a skill.

**2026-10-29: CLI not logged in.** The first smoke test failed on both attempts with "Not logged in · Please run /login" (evidence 2026-10-30T00-43-34Z, `bb1f877`). I logged in and reran (`NOTES_FOR_FRICTIONAL.md`).

**2026-10-30: dispute over who wrote the labels.** Claude Code declined to commit the hand labels as "my labels" because another assistant had described them as drafted by ChatGPT. It was resolved by my statement that I wrote the 20 labels and their reasons myself, and that ChatGPT only formatted my notes into a table (`f55b88d`).

**2026-10-30: first dev run interrupted.** My Ctrl+C stopped the first dev experiment. Its partial folder, `evidence/experiment/dev/2026-10-31T00-55-10Z/`, has 4 results and ends at a baseline attempt on 8401114002 with no result file. It is kept, and the complete run is 00-59-14Z (`d7411f4`).

**2026-10-30: wrong "relevant" hidden as invalid.** In the dev run the revised prompt called 8401114002, "Staff Machine Learning Engineer", "relevant" on both attempts. Both replies were rejected by the validator, so the result showed only as "invalid".
- **Why they were rejected:** each reply cited `resume_experience_tools` as a résumé field.
- **Correction:** the chat assistant first described this as Claude inventing a field. In fact `resume_experience_tools` is a key in the judge's own input, and the validator only accepts the field names under it.

**2026-10-30: usage limit during held-out.** In the held-out run (2026-10-31T01-26-20Z), 38 of the 39 Claude calls made failed with "You've hit your limit · resets 8pm (America/New_York)" (`4a46925`). Two later smoke tests hit the same limit (`3484999`).

**2026-10-31: spoiled sampling runs.** 5 sampling runs were spoiled by my clipboard mistakes and redone. Shell text was saved instead of a reply three times (8546367002 runs 1–3), and the prompt was saved instead of a reply twice (8648494002 runs 3–4). The spoiled files are kept in `experiments/sampling/spoiled/` (`6064e8e`).

**2026-10-31: held-out rerun in the Claude app.** The CLI was still usage-limited, so I ran the held-out split by hand in the Claude app (incognito, Sonnet 4.6, web search off). I used prompts that are byte-identical to the judge's (`71e8f56`), one reply per prompt and no retry (`f5c008d`).
- **3 spoiled saves, redone:** the reply for 8574655002 was saved as 8560779002-revised; chat text was saved instead of a reply for 8870159002-baseline; a shell command was saved instead of a reply for 8923831002-baseline.
- **Kept:** the spoiled files are in `experiments/heldout_app/spoiled/`.
