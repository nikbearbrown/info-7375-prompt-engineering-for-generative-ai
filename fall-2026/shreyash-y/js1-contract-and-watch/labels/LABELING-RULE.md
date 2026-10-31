# Labeling rule and how the labels were made

*Both sections below are Shreyash's words, pasted into the Claude Code session on 2026-10-31,
after the 20 postings were picked (commit `20041e3`) and before any Claude call was made on
any of them. Claude changed nothing in them and added only this note and the headings.*

## My labeling rule (in my own words)

I marked a job as relevant only if the title matches software engineering or AI/ML roles, the department is suitable, and the job is based in Boston or allows remote work in the US. I also checked that it mentions at least two of my selected skills, requires no more than 3 years of experience, and isn't a Staff, Director, Principal, Lead, or Manager position. If any of these conditions fail, I mark the job as not relevant and explain why.

## Hand-labeled job postings

Using the rule above and the 20 Oscar job descriptions you provided, all 20 postings are Not Relevant under this strict rule. This doesn't mean none would be worth considering in a real job search; it means none pass every condition of the assignment rule.

## What the labels do and do not contain (note by Claude)

- `hand-labels.csv` holds Shreyash's verdict for each of the 20 postings: Not Relevant for all 20.
- Shreyash recorded verdicts only. The `failed_conditions` column is blank because no per-condition labels were given. So the prompt experiment's pass mark against the hand labels is **verdict agreement**.
- Claude's failed conditions are compared separately against the rule's record, which anyone can recompute. That comparison is labeled as such and is **not** a hand label.
