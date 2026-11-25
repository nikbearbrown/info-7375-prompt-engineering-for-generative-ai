# APPENDIX — Readback: methods and evaluation in detail

PLANNED · drafted by Claude Code from the repo, reviewed by Aravind on 2026-11-23. Nothing here has run.

How to read the labels:
- **Measured:** counted from a file in this repo, with the path given. Paths are relative to this file (`film/project/`).
- **Plan setting:** a value chosen for the plan. *(decided)* means it is already in `EVAL-PLAN.md`; *(proposed)* means it is not decided yet.
- **Illustration:** made up to show the method. No judge has run, so no verdict or judge reason in this appendix is real.

## A. How Readback traces a disagreement to a criterion

### Inputs

| Input | What it is | Status |
|---|---|---|
| Rubric clauses | C1–C5 in `../../case-study/constructed/rubric-v0.md` (CONSTRUCTED) | exists |
| Judge verdicts | Pass or fail per clause, per recap, per judge: 3 judges × 5 clauses × 10 recaps = 150 verdicts | planned |
| Each judge's stated reason | One per verdict: the reading the judge applied, quoting the recap line and the transcript line it relied on | planned; the reason format is a plan setting *(proposed)* |
| My labels | C1 only: each of the 86 AMI decisions marked covered or missing in its recap, committed before any judge runs | planned *(decided, `EVAL-PLAN.md` proposal A)* |

### Steps

1. **Flag.** For each clause and recap, flag a *split* when the three judges don't all give the same verdict. On C1, also flag a *divergence* when a judge's pass/fail differs from the pass/fail that follows from my labels.
   - Plan setting *(proposed)*: a clause is flagged if it has at least one split, and flagged clauses are ranked by how many recaps split on them.
2. **Group.** Collect each flagged clause's split cases. Within a clause, group the cases whose reasons point at the same kind of recap item, for example "goal agreed, method left open".
3. **Extract the readings.** From the reasons on each side of a split, write the reading that side applied, one sentence per side. Each reading must come from the judges' own reasons; Readback doesn't add a reading of its own.
4. **Ask the PM.** Write one clarifying question that offers a choice between those readings, quoting the real lines that caused the split. Readback never proposes new wording for the clause.
5. **The PM revises the clause.** The PM's answer revises the clause, in the PM's own words. The revised rubric is saved as a new version, with the question and the answer beside it.
6. **Re-run.** The judges re-score the revised clause on the held-out recaps (check 3 in `EVAL-PLAN.md`).
   - Plan setting *(proposed)*: steps 1–4 use only recaps outside the held-out split, so the recaps that shaped the question can't count toward its re-measure.

### Worked example: ES2010b and C4

**Real material:**

- **Transcript** (AMI ES2010b · CC BY 4.0), `../../case-study/data/sample/ES2010b/transcript.txt`, lines 428–436. Filler lines 430 and 432–434 ("What", "A", "And", "I") are left out.

  ```text
  [00:20:44] B (ID): Do we want this thing to be able to be found easily?
  [00:20:49] A (PM): I think so.
  [00:20:52] D (ME): Sure, yeah.
  [00:20:55] D (ME): we we need a like homing device.
  [00:20:56] B (ID): like if this is gonna get lost underneath the coach, how are we going to accommodate the quick ability to find it?
  ```

- **Recap** (real output · `claude-opus-5-5` · 14 Oct 2026), `../../case-study/outputs/feature-run/ES2010b.json`:
  - under Decisions: "The remote should be easy to find if lost [00:20:52]";
  - under Unresolved: "How to make the remote findable, such as a base with a locator button that makes it beep [00:21:23]".
- **AMI's human summary** (DECISIONS), `../../case-study/data/sample/ES2010b/summary.txt`: "The group will consider including speech recognition and a locator function in the functional design."
- **C4** (CONSTRUCTED), `../../case-study/constructed/rubric-v0.md`: "**Unresolved stays unresolved.** Disagreements and open questions the team didn't settle are reported as unresolved, not as decisions."

This is a line where C4 is hard to call, not a recap error.

**The steps applied** (verdicts and reasons are an **illustration**; the film's B14 shows the same ✓ ✗ ✓ split):

1. **Flag.** On C4, judges 1 and 3 pass the recap and judge 2 fails it, so C4 is flagged.
2. **Group.** All three reasons point at one item: a goal the team agreed on, with the method left open.
3. **Readings.**
   - Pass side (illustration): the team agreed the remote should be findable ("I think so", "Sure, yeah"), and the open method is listed under Unresolved, so nothing open is reported as decided.
   - Fail side (illustration): the team only agreed to consider a locator (AMI: "will consider"), so "easy to find if lost" is an open question reported as a decision.
   - **Reading A:** an agreed goal counts as settled, even when how to reach it is still open.
   - **Reading B:** an item counts as settled only once the team has decided what to do, so an agreed goal with the method left open is unresolved.
4. **Question to the PM:** "In ES2010b the team agreed the remote should be easy to find ("I think so", "Sure, yeah") but didn't decide how. Under C4, which did you mean: (A) an agreed goal is a decision, and the open method goes under unresolved; or (B) it isn't a decision until the team chooses what to build, so the whole item goes under unresolved?"
5. **The PM revises C4** in their own words. The film shows only "C4 · revised by the PM", because no revised wording exists.
6. **Re-run** C4 on the held-out recaps. ES2010b helped write the question, so it isn't one of them.

## B. Cost and compute

### Tokens, measured

Source: `../../case-study/outputs/feature-run/*.json`, field `usage` (Claude Code 2.1.283, `claude-opus-5-5`, 14 Oct 2026).
- Input = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`.
- Recap = `output_tokens` − `thinking_tokens` (the visible recap).
- Transcript words are whitespace-separated words in `../../case-study/data/sample/<meeting>/transcript.txt`.

| Meeting | Transcript words | Feature-run input tokens | Recap tokens |
|---|---:|---:|---:|
| ES2006d | 8,035 | 23,866 | 654 |
| ES2007a | 3,228 | 10,496 | 486 |
| ES2008c | 8,044 | 22,104 | 589 |
| ES2010b | 6,094 | 17,025 | 630 |
| ES2011b | 5,737 | 15,988 | 543 |
| ES2013d | 6,115 | 18,069 | 577 |
| IS1003c | 7,039 | 20,417 | 569 |
| IS1004d | 6,777 | 19,971 | 554 |
| IS1005c | 5,916 | 16,046 | 561 |
| IS1009d | 6,638 | 19,271 | 536 |
| **Total** | **63,623** | **183,253** | **5,699** |

Also measured from the same files:
- 691–1,355 thinking tokens per feature-run call;
- 14.7–21.1 s wall time per call (`duration_ms`).

The recap system prompt's body is 1,206 characters and the rubric is 1,219 characters (`../../case-study/constructed/`). So a feature-run input (system prompt plus transcript) is a close stand-in for a judge call's transcript, rubric and instructions.

### Judge-run tokens (plan)

- **Input per judge call** ≈ that meeting's feature-run input + its recap tokens. That is 188,952 tokens for one pass over the 10 recaps, or 18,895 per recap on average (computed from the table).
- **C1 calls** also carry the meeting's `summary.txt`. The 10 summaries total 20,846 characters (measured). At the transcripts' rate of about 2.08 characters per token (fitted from the 10 feature runs), that is at most 10,041 tokens per judge. Summaries are prose, which usually packs more characters per token, so this is an upper bound.
- **Output per call:** plan setting *(proposed)*: the verdict and a reason of at most 150 tokens. If a judge also thinks as much as the feature run did (up to 1,355 thinking tokens, measured), the output is up to 1,505 tokens per call.

| Run | Calls | Input tokens | Output tokens |
|---|---:|---:|---:|
| Base run: 3 judges × 5 clauses × 10 recaps | 150 | 2,864,403 | 22,500–225,750 |
| Check 1: 5 planted variants, each a full base run | 750 | 14,322,015 | 112,500–1,128,750 |
| Check 3: 3 judges × the revised clause × the held-out recaps (upper bound: all 10) | ≤ 30 | ≤ 566,856 | ≤ 4,500–45,150 |
| **Total** | **≤ 930** | **≤ 17,753,274** | **≤ 139,500–1,399,650** |
| Per judge (one third) | ≤ 310 | ≤ 5,917,758 | ≤ 46,500–466,550 |

- Check 2 reuses the base run's C1 verdicts and needs no extra calls.
- Check 1 is included because `EVAL-PLAN.md` runs one variant per clause *(decided)*. It is about 80 % of the tokens.
- These are Claude-tokenizer counts. The second provider's tokenizer and the local model's will count the same text differently, so their figures are approximate.

### Dollar cost

List prices, fetched 2026-11-23 between 23:35 and 23:42 EST:
- **Anthropic:** https://platform.claude.com/docs/en/about-claude/pricing. The Batch API is 50 % off input and output.
- **OpenAI:** https://openai.com/api/pricing/, which redirects to https://openai.com/business/pricing/#api. These are "standard processing rates for context lengths under 272K", and Batch is −50 %.

Which model each judge uses isn't decided (plan setting). The cost per judge slot below is for that judge's share of the total: ≤ 5.92 M input tokens and 46,500–466,550 output tokens.

| Model | Input / output per M tokens | Per judge slot, standard | Batch |
|---|---|---:|---:|
| Claude Opus 5.5 | $4 / $20 | $24.60–$33.00 | $12.30–$16.50 |
| Claude Sonnet 5.5 | $2 / $10 | $12.30–$16.50 | $6.15–$8.25 |
| Claude Haiku 5.5 | $0.10 / $0.50 (prompts up to 100,000 tokens) | $0.62–$0.83 | $0.31–$0.41 |
| GPT-6.2 Astra | $8 / $40 | $49.20–$66.00 | $24.60–$33.00 |
| GPT-6.2 Sol | $2 / $10 | $12.30–$16.50 | $6.15–$8.25 |
| GPT-6.1 Terra | $1 / $5 | $6.15–$8.25 | $3.08–$4.13 |
| GPT-6 Luna | $0.10 / $0.50 | $0.62–$0.83 | $0.31–$0.41 |

- **Claude on my subscription.** The Claude judge can run on `claude -p` under my subscription (set up on this Mac, CLI 2.1.323). That has no per-token charge, but the calls count against the plan's usage limits. API credits are billed at the rates above.
- **Prompt caching** (not applied in the table). The five clause calls for one recap share the same transcript. With Anthropic's 1-hour cache for Opus 5.5 (write $8, hit $0.20 per M tokens), one write and four hits average $1.76 per M tokens of shared input instead of $4.
- **Local judge.** The local judge costs $0 per token on this Mac. Ollama was installed 2026-11-23 (0.40.17), with no model pulled and the judge not wired. Its runtime is unmeasured, because nothing has run on it.
- **Compute.** This Mac runs the scripts and the local judge; the API judges run on the providers' servers.

## C. Statistical limits

### Kappa on 10 recaps per clause is unstable

Computed in Python two ways: the large-sample standard error of Fleiss, Cohen and Everitt (1969), and 100,000 simulated samples per row (2.5th–97.5th percentile of κ̂).

Plan settings:
- the true κ is 0.6, the check 2 bar *(decided)*;
- both raters give "covered" (or "pass") at the same rate p, the prevalence. It is unknown until my labels exist, so two values are shown.

| Items (n) | p = 0.5 | p = 0.8 |
|---|---|---|
| 10 | 95 % interval width ≈ 0.99 (±0.50); simulated κ̂ 0.00 to 1.00 | width ≈ 1.25 (±0.63); simulated κ̂ −0.15 to 1.00; κ undefined in 4.7 % of samples (one rater gives all 10 the same answer) |
| 86 | width ≈ 0.34 (±0.17); simulated κ̂ 0.42 to 0.76 | width ≈ 0.43 (±0.21); simulated κ̂ 0.36 to 0.80 |

What that means:
- **On 10 recaps, a judge at the bar can score almost anywhere** between 0 and 1. A per-clause kappa on 10 recaps can't support a pass or a fail.
- **Narrowing the interval to ±0.10** would take about 246 items at p = 0.5, or about 392 at p = 0.8.
- **Even on 86 items, a judge whose true κ is exactly 0.6 scores below 0.6** in 46–51 % of the simulated samples, so the bar passes or fails it by chance.
  - Plan setting *(proposed)*: report the 95 % interval beside every κ.
  - Whether an interval that contains 0.6 counts as a pass, a fail or "inconclusive" would change the decided rule in `EVAL-PLAN.md`, so that choice is mine to make.

### Why check 2 uses the 86 decision items

- **C1 is the only clause with an outside human reference:** AMI's DECISIONS lists.
- **My labels mark each decision covered or missing.** That gives 86 items: 7–12 per meeting, `../../case-study/data/sample/selection.csv` (measured). Pass/fail per recap would give only 10.
- **The 86 items are clustered, not independent.** A judge's misses can bunch up in one recap, so the n = 86 interval above is too narrow.
  - Plan setting *(proposed)*: also report a bootstrap interval that resamples whole meetings.

### Per-clause judge-vs-judge results are descriptive only

- **On every clause, pairwise percent agreement and kappa across the 10 recaps** are reported with no threshold and no pass/fail *(decided measures, `EVAL-PLAN.md`)*. They find the splits for section A; they don't grade the judges.
- **Each pair's percent agreement moves in steps of 10 points** on 10 recaps.

### The held-out split (check 3)

- **`EVAL-PLAN.md` doesn't set the size yet.** It says the size will be set there before any revision, and the film doesn't show it.
- **Limit:** whatever the size, the held-out set is part of only 10 recaps.
  - With h held-out recaps, a pair's percent agreement on the revised clause moves in steps of 100/h points. One recap changing its verdict can turn "rises" into "doesn't rise". For example, h = 5 (an example, not decided) gives steps of 20 points.
  - On this test case, check 3 can show a direction, not a reliable size.
- **The choice of h is mine to make.**

## D. Generality: a known gap

The film says Readback is for any AI feature's acceptance criteria. But every check in `EVAL-PLAN.md` runs on one test case: the meeting-recap feature (10 AMI meetings, 10 recaps, one rubric). Nothing in this repo shows that the method works on a second feature. That is a known gap.

**Plan:** add a second test feature with a different output type, taken from a public dataset with human ground truth. It gets its own rubric and the same three checks, with the same pass and fail conditions.

**Two candidates.** I fetched both pages on 2026-11-23 between 23:35 and 23:42 EST; each licence is as stated on its page.

| | HelpSteer2 | MT-Bench human judgments |
|---|---|---|
| Source | https://huggingface.co/datasets/nvidia/HelpSteer2 | https://huggingface.co/datasets/lmsys/mt_bench_human_judgments |
| Licence | CC-BY-4.0 | CC-BY-4.0 |
| Output type | Chat-assistant responses to prompts, one rated response per row | Multi-turn chat answers from 6 models to 80 MT-Bench questions |
| Human ground truth | Each response rated 0–4 on helpfulness, correctness, coherence, complexity and verbosity. The page says each sample had "a minimum of three annotators and up to five". | About 3.3K expert pairwise preferences: which of two answers is better (the "human" split, 3.36k rows). The annotators are mostly graduate students with expertise in each question's topic. There is also a GPT-4 judge split (2.4k rows). |
| Size (page) | 21,362 rows: train 20.3k, validation 1.04k | 5,755 rows in all |
| Fit for Readback | The ratings are per attribute, which matches per-criterion acceptance criteria, the thing Readback traces. Each attribute would need a pass/fail cut-off (a plan setting). | The human label is a preference between two answers, not a per-criterion verdict, so checks 1 and 3 would need a rubric judged per answer. Its strength: the page links a notebook that computes agreement between the humans and the GPT-4 judge. |

**The choice is mine (Aravind) to make. Not decided.**
