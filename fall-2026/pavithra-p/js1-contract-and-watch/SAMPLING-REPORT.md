# Sampling report (Chapter 1)

What ran: `python3 -m agent sample` on 2026-10-30, 14:05:42Z to 14:07:32Z. The five postings are the first five dev postings in frozen order (fixed in `agent/experiments.py` before the run). Each was asked four times in a fresh `claude -p` conversation, with the baseline prompt contract (`experiment/prompts/baseline.md`), model `claude-sonnet-5-5`, no tools and no saved session. All 20 replies are saved as they came back in `evidence/claude/sampling/`. All 20 passed the validator.

My hand labels were written before Claude saw any posting (commit `7327ccd`).

| Job ID | Company | Title | Claude's 4 verdicts | Same every time? | My hand label | Matches my label? | Rule (record) |
|---|---|---|---|---|---|---|---|
| 7697137 | Pinterest | Machine Learning Engineer II, Visual AI | Not Relevant ×4 | yes | Not Relevant | yes | Not Relevant |
| 8015547 | Pinterest | Security Software Engineer II, Detection and Response | Not Relevant ×4 | yes | Not Relevant | yes | Not Relevant |
| 8213988 | Pinterest | Software Engineer II, Data Analytics & Engineering | Relevant ×4 | yes | Not Relevant | no | Relevant |
| 7661919 | Twilio | Software Engineer - Video | Not Relevant ×4 | yes | Relevant | no | Not Relevant |
| 8009057 | Twilio | Software Engineer L3 | Not Relevant ×4 | yes | Relevant | no | Not Relevant |

## How much the verdicts varied

Not at all. Each posting got the same verdict in all four conversations, so the spread is 0 of 5 postings. The reasons varied only in wording. For 7661919, one of the four reasons also called the "Minimum 2-3+ years" wording "ambiguous" and its verdict "a conservative call", but the verdict was the same.

## What I can conclude

* With this prompt and model, Claude's verdict on these five postings was repeatable: 4 out of 4 every time.
* Claude's verdicts matched the written rule (the record) on all 5, and my hand labels on only 2 of 5.
* The three disagreements point at my labels, not at Claude. I labelled from the title and did not check years. Claude's reasons quote the descriptions: 8009057 asks for "4+ years" and 7661919 for "Minimum 2-3+ years", both over my 0–2 year limit. 8213988 names SQL and Python and asks for 2 years, which passes the written rule. I had marked it Not Relevant as a data role.

## What I cannot conclude

* Repeatability is not correctness. Four identical answers show Claude is consistent, not that it is right. On 3 of 5 postings it consistently disagreed with my label.
* Five postings and one model are far too few to estimate how often Claude is wrong in general.
* Claude Code checked Claude's quotes against the saved postings. On 2026-10-31 I checked all three myself and found the same lines (7661919 with `sed -n '33p'`). `8009057.txt` line 35 "4+ years of professional software engineering experience"; `7661919.txt` line 33 "Minimum 2-3+ years of hands-on experience"; `8213988.txt` line 28 "Minimum of 2 years of experience", plus the words SQL and Python.
* My labels stay as written. Changing them after seeing Claude's answers would make the prompt experiment meaningless.

## My conclusion

The sampling report tests how consistent Claude is when judging job postings. I used five jobs and asked Claude four times about each one. Claude gave the same verdict every time, but three verdicts differed from my own labels. I learned that getting the same answer repeatedly doesn't prove it is correct, and I should check the full job description before labeling a job.

## Driver's seat for this report

* Delegated: running the 20 conversations, checking the format and tabulating (Claude Code).
* Kept: the hand labels, written before any Claude answer, and the conclusion above.
