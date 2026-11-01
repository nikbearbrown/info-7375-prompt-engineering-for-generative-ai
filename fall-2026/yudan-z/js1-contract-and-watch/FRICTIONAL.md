# FRICTIONAL — Job-Search Agent 1

## Executive summary

This is my dated log of what I tried, what broke, what I checked, and what I accepted, changed or rejected from Claude (Claude Code, used through the desktop app and its CLI).

- The pre-written tests caught **two** bugs in Claude's first implementation.
- Real runs and reviews caught **four** more:
  - an evidence overwrite;
  - "CA" read as California for a Toronto job;
  - "ITAR" matched inside "military";
  - a 6,000-character truncation that hid a no-sponsorship sentence from Claude.
- Each entry names who did the work and points to a commit or file.

## 2026-10-30

| # | What I tried / what happened | What I checked, changed or learned | Who · trace |
|---|---|---|---|
| 1 | Asked Claude to install the Claude Code CLI so the agent could call Claude. My PowerShell said `claude` was not recognized, even after reopening the terminal. | The desktop app had installed it into its own virtualized AppData, which my terminal cannot see. I installed it myself with `npm install -g @anthropic-ai/claude-code` and logged in with my own account. | Me + Claude diagnosed |
| 2 | Wrote my relevance rule in Chinese: title has Data Analyst / Business Intelligence; not Senior/Manager; in the US; no 3+ years required; no citizenship required; master's accepted; ≥2 résumé skills. | Claude pointed out 7 places a TA could not predict (other senior words, bare "Remote", year ranges, **no-sponsorship wording**, what "accepts master's" means, more title families, how skills match). I accepted all 7. | Rule mine, refinements suggested by Claude · `077c5e0` |
| 3 | Claude reviewed the contract against the assignment. | Three gaps: (a) the justification must name résumé fields, but 7 checks used none; (b) R5/R6 said "e.g.", so they were not predictable; (c) the year patterns were not listed. I accepted all three. Each check now names its résumé field, and the phrase lists are complete. | Claude found, I approved · `077c5e0` |
| 4 | "What a failure looks like": I had no idea at first. Claude gave three examples; I picked A and added my own three (an irrelevant posting called relevant, the same posting twice, an expired posting). | Claude explained that "expired" cannot be observed from a board and rewrote it as "a posting not in this run's response". I approved the merged sentence. | Mine, wording with Claude · CONTRACT §6 |
| 5 | Tests were committed **before** the implementation (`3fcb128` then `e008d0d`). First test run: **2 failures**. | `2-4 years of SQL` was read as 4 (the "N years of" pattern caught the range's top). `Must be a U.S. citizen.` was missed (the sentence splitter broke at "U.S."). Both fixed; the tests are unchanged. | Claude's code, caught by tests · `e008d0d` |
| 6 | Real baseline: 170 Pinterest postings, 0 reported new. | Matches failure condition (1). | `runs/live/` |
| 7 | Seeded second run (5 real ids removed from a copy of the response, labelled SEEDED). | Both runs started in the same second and got the same stamp, so **the first run's raw evidence was overwritten**. Fixed (counter suffix), added `test_same_second_runs_keep_both_evidence_files`, re-ran. | Found by me reading the output with Claude · `a5915eb` |
| 8 | Compared the rule's and Claude's reasons in the seeded run. | Toronto's location `Toronto, ON, CA` passed R3 because `, CA` is California's code. Claude said "Toronto … not the US". The contract was wrong, not the code. I decided on a **dated revision** (Canadian province ⇒ CA is Canada), keeping the original text. | My decision · `83ac0d1` |
| 9 | While building the labeling sheet, Claude saw ITAR "matches" in three postings. | `ITAR` matched inside "milit**ar**y" (substring). R5/R6 now use whole-word matching, plus a test. | Claude found · `fc7b632` |
| 10 | **Labeled 20 real postings myself**, under my labeling rule (written first, `acc396f`). 6 relevant. | I mixed in other companies' Greenhouse boards because Pinterest has almost no entry-level analyst roles (same allow-listed host). | **Me** · `50a1f2d` |
| 11 | Claude asked whether to change two labels. | **#3 (Stripe intern): I rejected the suggestion** and kept `relevant`, because a co-op could move my graduation to December 2027 and I would also search for internships. **#12:** I accepted that my reason misread "Bachelor's or 3 years", and changed the reason (not the label) to "finance, not data analysis". Both are dated in `labels.json`. | **Me** · `08ca1ae` |
| 12 | After labeling I proposed a new rule: graduation timing. | Added as **R9** (dated revision), driven by the résumé's graduation window (May 2027, or Dec 2027 with a co-op). | My idea, Claude implemented · `08ca1ae` |
| 13 | Baseline v1 on dev: 9/10. I chose the single revision: R1 judges the work, not the title. | — | **My choice** · `prompts/contract_v2.txt` |
| 14 | v2 on dev scored 6/10, and one justification said "no … sponsorship limits stated" for Affirm, which does say it. | `judge.py` cut descriptions at **6,000 characters**; Affirm's sentence is at character 6,861. Every model result so far was affected. Removed the cut, added a test, moved the old results to `superseded-truncated-input/`, re-ran **dev only**. | Found reading Claude's justification · `d7f69c1` |
| 15 | Re-run: v1 dev 9/10, v2 dev 7/10. Held-out once each: v1 8/10, v2 9/10. | The direction flips between splits. I did not make a second revision. I report "no detectable difference". | `575b5bb` |
| 16 | Sampling, 5 × 4 fresh calls. | #4 was wrong vs my label in every valid try, and 1/20 was invalid (over 400 characters). That is repeatability, not correctness. | `575b5bb` |
| 17 | Action surfaces. | The file and agent surfaces both returned `location.name`, which my validator rejects. The agent said it never had raw bytes. Chosen: paste surface, no tools. | `4a1f484` |

## 2026-10-31

| # | What I tried / what happened | What I checked, changed or learned | Who · trace |
|---|---|---|---|
| 18 | Real second-day run on the live board, about 20 hours after the baseline. | 0 new. Compared the two raw responses: the same 170 ids, none added or removed, so 0 is correct and not a missed change. The real change requirement is still met only by the seeded run. | Claude ran it, I checked · `runs/live/run3-day2-terminal.txt` |

## What I accepted, modified or rejected from Claude

- **Accepted:**
  - the 7 + 3 contract refinements;
  - the two wrong versions (they were the assignment's own examples, and I agreed they fit);
  - all code, tests and the reports' first drafts.
- **Modified:**
  - the failure sentence (merged Claude's option A with my three cases);
  - label #12's reason.
- **Rejected:**
  - changing label #3 to `not_relevant`;
  - writing "translated by AI" in the contract; I asked for "my content, integrated and refined by Claude".
- **Mine alone:**
  - the relevance rule;
  - the labeling rule;
  - all 20 labels;
  - R9;
  - the R3 revision decision;
  - the choice of the one prompt change;
  - running the CLI login.

## Still unresolved

- No second labeler, so I cannot tell whether #9 and #14 are model misses or label noise.
- No real new posting has been observed yet; only the seeded run shows the agent reporting a change.
- R1's title list misses real analyst work (#4, #15), and R3 fails US locations written without a state code (Stripe's "New York, Seattle, South San Francisco HQ").
