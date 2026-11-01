# Labeling rule — Sreevarshan Sathiyamurthy, 2026-10-30, written before labeling any posting

## 1. Hand-labeling rule
I want to use the same eligibility requirements as my contract, but evaluate each posting manually without looking at the agent's verdict first. This gives me an independent answer to compare against the rule and Claude.

## 2. What I check differently
I'll read the complete description to understand whether a requirement actually applies to the candidate. I'll pay attention to the context instead of relying only on keyword matches. I won't introduce new eligibility rules after seeing the results.

## 3. Uncertain postings
If I'm unsure about a posting, I'll keep it in the dataset instead of replacing it. I'll record my best judgment, explain why I'm uncertain, and flag it as a borderline case. I don't want to remove difficult postings just to improve the results.

## 4. Selecting 20 postings
I'll select 20 real postings from the saved Databricks board response. I want a mixture of AI/ML engineering roles, data engineering roles, senior positions, and unrelated positions, including some borderline cases. I'll record the posting IDs before running the experiment.

## 5. Relevant versus not relevant
I'll aim for approximately 10 relevant and 10 not relevant postings so I can evaluate both outcomes. I won't change the labels just to achieve an even split.

## 6. Development and held-out split
I'll sort the 20 selected postings by posting ID, assign alternating entries to the development and held-out groups, and freeze the split before running any prompts. I'll use the 10 development cases to improve the prompt and leave the 10 held-out cases untouched until final evaluation.
