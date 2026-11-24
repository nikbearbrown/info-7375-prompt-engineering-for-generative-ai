# FRICTIONAL.md: Job-Search Agent 3

> **How this was written.** Claude Code organized these entries from the working sessions of Nov 20 and Nov 22, 2026 (EST). Every fact comes from those sessions, a committed file or a command's output. Quotations are Hemanth's words, verbatim, typos included. Where Hemanth gave no words, the entry says what was decided and nothing about how Hemanth felt.

## Nov 20, evening: starting, and a loose end from JS2

- **What happened:** Hemanth pasted the JS3 assignment and asked to "plan accordingly and perfectly".
  - While planning, Claude found that JS2 had been submitted on Nov 10 from commit `9061037`, with its sign-off still dated Oct 31 and still saying "no new postings yet". The Nov 7 run had made that line out of date, and the re-signing Claude had asked for never happened.
  - That can't be changed now, so it is recorded here and nowhere else.
- **What was done:**
  - JS2 was copied unchanged (`cf6b64d`).
  - One more live run was made with the unchanged JS2 loop at 9:30 PM. It brought in 131 new postings; the two deliberate failures from JS2 again had no result.
  - The corpus was frozen at **1,176 unique postings** (`aa22f37`).

## Nov 20–22 (committed Nov 22, 2:07 PM): the gate

- **Hemanth's answers:**
  - Q1 (role words): "b".
  - Q2 (exclusions): "I'm ok with c but what to I do with the sales and accounting roles?"
- **What Claude found when it measured Q2:**
  - The bare word "Account" would also remove three engineering jobs, such as "Staff+ Software Engineer, Account Abuse (Machine Learning)".
  - "Account" doesn't match "Accounting" (words match whole), and accounting roles fall out anyway.
  - Claude recommended excluding the phrases "Account Executive" and "Account Manager" instead.
- **What Hemanth decided:** "c without phrases and whatever the default is which is recommended and the deadline for submission is ectended until wednesday so we have to make sure everything is perfect". The bare word "Account" was kept, with its cost logged (FILTER.md section 6), and Q3–Q7 took the recommended defaults.
- **The rest:** Claude's proposals (evidence rules, sources, wrong versions) were accepted: "accept". FILTER.md v1.0 was committed alone at 2:07 PM (`12c826a`), and the six wrong-version tests followed at 2:08 PM, before any code (`47d33ef`).

## Nov 22, 2:23–3:24 PM: 95 blind verdicts

- **What happened:** Hemanth labeled 95 postings in 10 batches, with no scores shown. Each batch was committed as it came in.
  - Item 10 was left out of the first reply and item 77 out of a later one. Claude asked again, and both were answered.
  - One reply said "888 n", which was recorded as item 88 with a note in `audit/labels.csv`.
- **Evidence:** the `labeled_at` time on every row; commits `c037109` through `2dffab6`.

## Nov 22, about 3:25–3:36 PM: what the audit showed

- **The result:** 11 of 30 random rejects were postings Hemanth wanted. Claude reported this as a range (22%–54%, about 210–524 postings), not a rate.
- **Where the misses came from:**
  - The skill requirement caused 7 of them.
  - The seniority word "**Staff**" caused 3: Perplexity calls every engineer "Member of Technical Staff". That's the named false friend.
- **A tension Claude pointed out:** Hemanth's verdicts and Hemanth's Q3 answer disagree. The verdicts marked 11 of 14 senior-titled roles as worth reading, while Q3 said to penalize seniority.
- **What Hemanth decided:** "X1 accept, X2 reject, X3 reject, X4 Reject", which matched Claude's recommendation. FILTER.md became v1.1, and all four changes are in the changelog with their measurements (`b70deec`).
- **Unresolved:** the Q3 tension. Hemanth kept the penalty, and the level is left to the shortlist's level claim (C3).

## Nov 22, 3:38–4:12 PM: the claim labels

- **What happened:**
  - Claude labeled 69 claims on the 10 shortlisted postings, and every quote was found verbatim.
  - Hemanth checked them in two messages, "all ok" and "all ok".
  - Claude then re-applied the written rule itself and found **3 labels that break it**: a posting that says both "3+ years" and "hiring across a range of experience levels", and two Anthropic postings whose "We do sponsor visas!" sentence is followed by "However, we aren't able to … for every role".
- **What Hemanth decided:** "a" (correct them, and keep Claude's label and Hemanth's first check next to the final label).
- **What this showed:** a grounded quote and a human "ok" together still let 3 rule breaks through. Recorded in `SHORTLIST.md` section 5.
- **Unresolved:** whether "AWS, GCP, or Azure" asks for AWS, and whether a bare city counts against "Boston or remotely". The labels are inconsistent on both.

## Nov 22, 4:15–4:22 PM: the tool servers

- **Our server, the first real session with Claude Code.** Claude answered the question correctly, then added "I can't say whether Notion postings were covered", because the tool listed only the failed boards. Claude added `boards_with_result`, re-ran at 4:17 PM, and the answer said Notion was covered.
  - The same transcript shows Claude Code first trying a newer protocol (`server/discover`, `2026-07-28`) and falling back to `2025-11-25` after our "method not found".
- **The filesystem server.** Claude predicted the results and committed the predictions before the probe (`4b9b439`).
  - All five escape attempts were refused, as predicted.
  - One prediction was wrong: a relative path was allowed.
  - **The main finding:** a client that declares MCP roots silently replaced the folder the server was started with.
- **What Hemanth decided:** "T1 a, T2 a" at 5:36 PM. Our server is trusted read-only, for this folder only. The filesystem server is trusted only under four conditions.
- **Unresolved:** prompt injection through a posting snippet was not tested, and the filesystem server was only run on Node 23 (it requires 24).

## Nov 22, 5:38–5:44 PM: what moves the score

- **What happened:** 200 Claude calls on the 40 held-out postings, one change at a time. The held-out labels had been committed at 3:24 PM, before any experiment.
- **What was learned:**
  - The identical baseline ran twice with **0 flips**.
  - **Changing the prompt** to Hemanth's own question ("worth the candidate's time to read in full?") made Claude say "not relevant" to **all 40**. Agreement with Hemanth fell from 28 to 21.
  - Adding context or switching to Haiku changed **nothing** under the rule-bound prompt.
  - The accepted filter change, X1, couldn't be tested on the held-out set: none of the 40 is a "Technical Staff" posting.
  - The fitted threshold came back at the inherited 3.0.
- **Persistence:** JS1's exact Oct 31 prompts (hashes verified) gave the same 20 verdicts on Nov 22. `SCORE.md` section 3 explains why that isn't memory or training.
- **Unresolved:**
  - whether context matters under an open prompt, which would mean changing two things at once;
  - the tool-list change, which wasn't run;
  - X1 on held-out postings.

## Nov 22, evening – Nov 23: "Are you sure we are doing it right?"

- **What happened:** before signing, Hemanth asked: "Are you sure we are doing it right?"
  - Claude checked every requirement and found nothing missing.
  - It named three places where the evidence was thin:
    - X1 had never been tested on unseen labels;
    - the context experiment ran under a prompt where context couldn't matter;
    - prompt injection through the server had never been tried.
  - It also caught a wording problem in its own sign-off draft: the W1–W6 tests "failed" before the code only because the code didn't exist yet.
- **What Hemanth decided:** "1 and 2 plus 3".
- **What came of it:**
  - **X1, out of sample:** Hemanth labeled 20 more postings blind (96–115), with the seed committed first. On the 10 that X1 changes, v1.1 was right 7 and v1.0 3.
  - **E5:** context under the open prompt changed no verdicts, but made Claude more confident.
  - **The SEEDED injection:** not followed, and the caution came from the client, not my server.
  - **A new tension:** the London and San Francisco postings of the same AI Inference Engineer role got different verdicts (n / y), although FILTER.md says location never decides. It's recorded in AUDIT.md section 6 and not acted on.
- Hemanth re-asked for the test-1 items once ("Give me again test 1 questions and I will label again") before answering them.

