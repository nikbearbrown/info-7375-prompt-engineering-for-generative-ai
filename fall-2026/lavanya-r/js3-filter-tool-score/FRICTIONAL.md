# FRICTIONAL — Job-Search Agent 3

An honest, dated log, including what went wrong and what is unresolved.
Lavanya R. Entries are from 2026-11-24 (ET) unless dated otherwise. Commit hashes are in brackets.

## In my own words (Lavanya R, written 2026-11-25)

I wrote this section myself. Claude only fixed capitalisation.

- **What surprised me most:** CA was taken as California even though the province said Ontario, and also keywords in the Databricks footer was being considered in the evaluation.
- **What was hard, and what I did:** Understanding what a tool server is and how the jobs were being graded. Judging 71 different postings was exhausting. I asked Claude to explain everything to me before I gave my input in anything.
- **What I'd do differently in JS4:** Probably read the full postings first instead of the summaries.

## 17:00 — starting point and collection

- **Tried:** start from my JS2 folder unchanged [6f14d20] and collect from 6 boards: JS2's databricks, notion and palantir, plus anthropic, openai and zoox.
- **Unexpected:** collection 1 returned 3,117 postings, but the Greenhouse files were tiny (32–45 KB for 632 and 890 jobs). JS2's Greenhouse URL never asked for job text, because JS2 only needed ids and titles. The JS3 filter and evidence rules need the text.
- **Response:** added `?content=true`, the only change to JS2's code, and collected again. Collection 2 is the corpus: `check.py` 9/9, frozen in `CORPUS.sha256` [8d0122c]. Both runs are kept.

## 17:09 — the tool server came before FILTER.md

- A Claude Code subagent built the MCP server, tap, client and tests while FILTER.md was still a skeleton waiting for my rules [309c996].
- FILTER.md v1.0 was committed later [75b2de8], but **before any filter code** [a40e9bb tests, 2c1b967 code]. The server contains no filter rule.
- I'm recording the order rather than presenting the tool server as coming after the gate.

## ~22:00–23:00 — writing FILTER.md

- **Friction:** I did not write the rules in my own words first. Claude showed counts and real titles for each rule and offered options, and I chose one rule at a time.
  - My JS1 feedback asked for the opposite.
  - FILTER.md says which wording is Claude's.
- **Two titles checked against the rules before any code:**
  - "Software Engineer, Sales Platform" is not rejected for "Sales", which I dropped from R2. But R5 rejects that real posting, because it asks for 5+ years. The test `test_real_sales_platform_posting_rejected_by_r5_only` pins this down.
  - R1 rejects "Software Engineer, Ads Manager" for "Manager", which here is a product name. It's a false friend I noted but didn't measure.
- **Decided:** R3 needed state codes and US cities. JS1's markers alone missed 112 "San Francisco" and 34 "Foster City, CA" postings.

## 23:00–23:14 — the hand verdicts

- **Tried:** 80 postings, blind, in batches of 10, answering y / n / ? from multiple-choice cards.
- **Stopped at 71:** labelling stopped once all 30 random rejects and all 10 closest calls were done. The 9 held-out items left are unlabelled, so the Chapter 9 measurement uses 21.
- **Unresolved:** I judged from one-line summaries Claude wrote of each posting's requirement lines, not from the full postings. Later evidence shows some of my y verdicts missed eligibility facts:
  - item 7 is restricted to French Grandes Écoles graduates (Claude's judge said so in `score/runs/E0a`);
  - item 47 is for current students, and Priya graduated in Dec 2025.

  I didn't change any verdict after seeing the filter or Claude.

## 23:15–23:20 — the audit

- **Result:** 0 of 29 random rejects wrong, 4 of 10 closest calls, 2 of 10 kept.
- **What I learned:** "0 of 29" doesn't mean "never". The 95% interval goes up to 11.7%, which could be about 350 good postings among the 3,002 rejects. The errors sit at the threshold.
- **False friend 1:** "Ontario, CA". In Anthropic's locations, CA means Canada. I adopted X4 even though it changed no verdict, because it fixes a wrong reason.
- **Rejected after measuring:** X1 (threshold 4: one fewer mistake in 49, but twice the reading), X2 and X3 (no change on my labels). I followed Claude's recommendations on all four. [b5230a4]

## 23:21–23:36 — the second tool server

- **Tried:** Claude proposed `@modelcontextprotocol/server-filesystem`, but that needs a package download. It then used the MCP server built into Claude Code (`claude mcp serve`), which was already installed, so nothing new was downloaded.
- **Unexpected:**
  - Its first run **hung**. It doesn't exit when the client closes stdin, so it was stopped by hand.
  - Claude changed my client to terminate a server after 10 s and record that in the transcript.
  - It declares 29 tools with no safety annotations, and Read returned `/etc/shells` with no prompt.
- **Decided:** T1, trust my own server within its read-only scope. T2, don't connect Claude Code's server to my agent.
- **Considered:** making my server find *new* postings. The brief's "search new postings" is only an example. A server that goes online would break the rule that it can't send data outside my folder, so new postings come from running the collector first. Reading the newest saved run instead of a fixed one was offered; I chose to leave the server as it is.

## 23:36–23:45 — the scorer and the shortlist

- **Unexpected 1, the checker's own bug:** the quote checker overrode 8 of Claude's "supported" labels as "quote not found". Claude's quotes began with `Title:` / `Location:`, as the labelling prompt shows the posting; the checker didn't include those prefixes.
  - Fixed, with a test added [ba07a9f].
  - The output before the fix is kept in `logs/js3-06`.
- **Unexpected 2, false friend 2:** every Databricks posting ends with an "About Databricks" footer that mentions agents, Databricks and Unity Catalog, so the filter gives all 890 of them free points.
  - Removing it changes 6 verdicts in the corpus, none of them among my hand verdicts.
  - I decided to record it and fix it in the next version.
- **Unexpected 3:** the Claude judge said "no" to 13 of the 14 held-out postings I marked y. Only the prompt change moved it beyond the noise floor (6 verdicts vs 1).
- **Not saved:** before running the experiments, Claude made one test call to check the CLI flags (after the experiments were committed, [0b7f903]). Its reply, "cannot_tell" for the first held-out posting, was printed but not saved. E0a later answered "no" for the same posting, so this is a second example of noise, without saved evidence.
- **Hand check:** I checked 3 labels.
  - I first disagreed with a "contradicted" label, then agreed once Claude restated what the labels mean.
  - I still disagree on Unity Catalog. A Databricks job will use it, but my own rule says the quote must say so. I haven't resolved this.

## What I accepted, modified or rejected from Claude

The full table is in SOURCES.md. In short:
- **Accepted:**
  - every FILTER.md rule and reason, each one of Claude's options [75b2de8];
  - FILTER.md sections 2–4 as drafted;
  - Claude's recommendations on X1–X4 [b5230a4] and on deferring the footer fix (X5);
  - all code and tests, which Claude wrote.
- **Modified:**
  - added "Head of" to R1;
  - dropped JS1's "Sales" from R2, after seeing it would reject "Full Stack Software Engineer, Sales Platform";
  - added wrong version W6.
- **Rejected:**
  - Claude's "insufficient" label on "The role uses Unity Catalog" (SHORTLIST.md §4);
  - the offer to make the tool server read the newest saved run;
  - labelling the last 9 held-out postings.
- **Changed my answer after Claude explained:** one claim-label check, from "disagree" to "agree", once Claude restated what "contradicted" means (SHORTLIST.md §4).

## What I understand now / still don't

- **Relevance vs entailment:** the highest-scoring posting (score 9) says it is "not intended for … new graduate, or entry-level applicants".
- **The abstention rule:** it only abstains when the evidence is missing. It can't notice when the question is wrong: the internships "support" under one year of experience, but Priya can't enrol.
- **Still open:**
  - whether X3 really helps (it needs a fresh held-out set);
  - how much the footer matters;
  - whether a judge stricter than me is wrong, or right about facts I didn't see.
