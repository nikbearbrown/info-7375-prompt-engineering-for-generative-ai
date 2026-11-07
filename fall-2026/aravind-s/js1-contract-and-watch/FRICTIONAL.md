# FRICTIONAL: Job-Search Agent 1

My log for JS1. Claude Code organized each day's entry from my own messages, picks and commands that day; times are Pacific. The decisions are listed with their commits in [DECISIONS.md](DECISIONS.md).

## Friday 2026-10-30

**What I was working on:** the contract, the watch and the Friday baseline, then my labels, the prompt experiment and the action surfaces.

**What I tried and expected**
- Before starting, I made sure the fictional persona could never touch my real profile (nothing is ever sent or applied for in its name), and I chose a plain name for it: Jane Doe.
- I made the contract's decisions in one batch of four multiple-choice questions (years, titles, wrong versions, failure sentence), comparing how many of the 814 live postings each option would keep, and had Claude Code put them into words before any code existed.

**What happened**
- I ran the tests (53 passed) and the planted mistakes (13 of 13 caught) myself before the watch was committed (304c0a0), then approved the commit and the baseline run: at 5:31 AM ET it recorded 814 postings, 0 new (629a279).
- Labeling took the most care. I checked how to apply my labeling rule to a posting before labeling it; posting 1 (Product Reliability Engineer) was not a match for me at all, so I labeled it a missing specialty. I labeled all 20 myself (882909e): the ten the rule rejects in one confirmation against the rule's record, because part 1 of my rule decides them, and the other ten one by one from their requirement lines.
- I asked whether my picks would change the agent itself. They do not change its rule or its verdicts: they measure how often the rule and Claude agree with me, and they decided which prompt to keep.

**What I took from Claude, and what I changed**
- I accepted the options Claude proposed for the design questions: the contract's four choices, the labeling rule, how the 20 postings are picked, the experiment's one change (the specialty point), keeping the baseline prompt, running live run 2 myself, pushing only after review, and running all three action surfaces for real. My labels for the ten postings the rule passes were my own reads, with nothing suggested; for the ten it rejects I confirmed the rule's failing check.
- I changed the plan where it did not fit how I work: instead of answering a long question sheet, I made the contract's calls in four multiple-choice questions and had Claude draft the text.
- I set how far Claude could go on its own: commit each step on Friday, but never push or open the PR without me.
- Before publishing, I asked for an independent review of the whole repo. It found that the validator did not check the contract's three-sentence limit, that one lockdown check could never fire, and that my account name sat in three commits. I chose to rewrite those three commits, to keep my contract's wording, and to relabel posting 11 with both scorings reported (5ab508d, c254ab9).

**What the day showed, and what is still open**
- The revision I picked went from 8 to 10 out of 10 on the development set. On the held-out set, scored with the contract's validator, it is 9 to 8 over the baseline with my current labels and 8 to 8 with my first ones. The difference is posting 11 (Systems Software Engineer, Silicon Bringup), which I relabeled as a missing specialty after the review, so the held-out set cannot separate the two prompts.
- The rule misses posting 19, which asks for "5+ years" in a sentence without the word "experience". Both prompts caught it.
- The agent that fetched the board itself could not read it: the 13.5 MB answer is over its fetch tool's 10 MB limit (ce7aea6).

**Evidence:** commits e989f8b (the contract) to c254ab9 (the relabel) and the docs after them; the baseline in `runs/2026-10-30T093102Z/`; my labels in `labels/labels.json`; the experiment in `experiment/`.

**Next:** run live run 2 myself on Saturday, then the sign-off.

## Saturday 2026-10-31

**What I was working on:** live run 2, my own checks, the sign-off and publishing.

**What happened**
- I ran live run 2 myself at 7:10 PM ET: 810 postings, 7 new and 11 gone since Friday. All seven new postings were senior, legal, management or non-software roles; the rule and Claude agreed that none fits Jane, and every Claude answer passed the validator.
- I ran the 99 tests, the 37 planted mistakes and the independent recompute myself. All passed, and the recompute matched run 2's report (7 new, 11 gone): the check my contract's failure sentence asks for.

**What I decided**
- My sign-off's four "not checked" items, way 1 as the least autonomy that suffices, signing it, and publishing: my public repo, the course PR and the zip.

**Looking back at Friday evening (logged on Saturday)**
- I asked whether the finished agent would land me interviews, and what it does if it never applies. It cannot promise interviews; it controls the blockers, freshness, referral notes and what I learn from responses. My friend's kit does not submit applications either. I added an apply-assist step to my personal plan: my saved answers for the factual questions, drafts for the open ones, and I submit.

**Evidence:** `runs/2026-10-31T231042Z/`; the sign-off and driver's seat at the end of README.md.

**Next:** JS2 (due Tue 11/10), and the personal layer starting Sunday.

