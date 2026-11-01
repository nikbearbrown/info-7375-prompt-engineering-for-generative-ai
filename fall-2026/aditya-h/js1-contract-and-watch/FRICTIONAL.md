# FRICTIONAL — what I tried and what happened

**About this log:** Claude Code drafted the entries in Part 1 on 2026-10-31 from what actually happened in the session; the commit hashes and files show each one. Part 2 is for my own reflections, written by me.

## Part 1 — Log of events (dated, traceable)

| # | When (EDT) | What I tried | What happened | What I checked, changed or learned | Trace |
|---|---|---|---|---|---|
| 1 | Oct 31 | Answered the contract questions. I said matching should look at "all" fields, including the posting body. | Claude checked the live board: "product manager" appears in 101 posting bodies but only 37 titles. The extras were roles like Android Engineer and Customer Success Manager. | **Changed:** relevance is decided by the title only; the body is cited as evidence. | CONTRACT.md provenance, `aee1aab` |
| 2 | Oct 31 | Asked Claude to write the failure sentence and say I wrote it. | Claude refused to attribute its words to me, and offered four drafts marked as drafted. | **Accepted** the honest version: I chose the "watch + verdict" sentence, recorded as "drafted by Claude, chosen by Aditya". | CONTRACT.md, last section |
| 3 | Oct 31 | Asked Claude to review my contract as a TA would. | It found real gaps: what "whole word" means for "US-Remote" vs "Business", corrupt or missing state, empty or failed fetches, no résumé validation. | **Accepted.** These became testable clauses. A TA could not have predicted verdicts without them. | `aee1aab` |
| 4 | 22:41 | First live baseline fetch. | **Failed:** `SSL: CERTIFICATE_VERIFY_FAILED`. The python.org build of Python has no CA bundle. | The bad-fetch refusal held, and no state file was written. **Fix:** verified TLS using the macOS system bundle `/etc/ssl/cert.pem`, rather than turning verification off. | `03f865f` |
| 5 | 22:41 | Retried the baseline. | 745 postings, 0 new, raw response saved (5.5 MB). | The UTC timestamps in filenames show Nov 1 for an Oct 31 local run. **Learned:** run the second run after 8 pm EDT so both dates differ. | `runs/`, `03f865f` |
| 6 | ~22:50 | Ran the tests and the wrong-version harness myself. | 53/53 passed. Each of the 3 planted wrong versions made 2, 15 and 10 tests fail. | I saw for myself that the tests catch the wrong versions. | `evidence/test-run-by-aditya-2026-10-31.md` |
| 7 | ~22:52 | Claude judge, first live call. | **Failed:** "OAuth session expired". | I logged the CLI back in myself (`/login`). The smoke test then worked: a valid reply in about 6 s. | `evidence/claude-smoke-test-2026-10-31.md` |
| 8 | ~22:55 | First random draw of the 20 postings. | Zero PM titles landed in the dev set, so dev couldn't separate the prompts. | **Discarded** before any labeling or Claude call. Redrew with an even split by title type. | `select_postings.py` docstring, `96ab08e` |
| 9 | 23:05 | Asked Claude to "run it and finish the assignment", including the labels. | Claude would not produce my hand labels. It froze both prompts, collected all Claude replies without reading labels, and asked me to label. | I labeled all 20 in chat without seeing the experiment results. | `774c98e`, `16a72a1` |
| 10 | ~23:10 | Scored my labels against the rule's recomputed verdicts. | **18/20 agreed.** I had labeled 8331852 (Staff PM, Risk, *Toronto*) and 8238100 (*Product Counsel*) relevant. The written rule says not_relevant for both. | **My failure sentence's second clause fired**, and the error was in my hand application, not the code. I judged both to be slips. Originals are kept, with a dated correction column; scores are reported both ways. | `4158a63`, `labels.csv` |
| 11 | 23:00–23:05 | Action-surface mode 3: let an agent fetch the board and edit its own state file. | It reached the right verdict, but made 5 summarized fetches, counted 743 (my fetch had 745), saved no raw response, and set `last_run` to a date *earlier* than the previous run. | **Learned** why fetch and state stay in deterministic code. That backed the choice of mode 1 for Claude. | `ACTION-SURFACE.md` |
| 12 | 23:11–23:13 | Second run. I had to submit within 30 minutes, so a second calendar day wasn't possible. | The live second run found **0 new**: Stripe hadn't changed since 22:41, and my two earlier saved fetches matched it too, so there was no real earlier response to diff against. | **SEEDED instead:** I rebuilt a "before Oct 30" state from the saved response's own `first_published` dates (`experiments/seed_state.py`). That gave 17 new, both judges agreeing on all 17. Labeled SEEDED everywhere. The planned real second day is not shown. | `runs/`, `runs-seeded/` |

### Unresolved

- I didn't test the agent on a board that returns an HTTP error live. That path is only covered by unit tests with a fake fetcher.
- The prompt experiment shows that Claude can follow my rule. It doesn't show that my rule finds good jobs for Maya; v1's seniority objections may be more useful in real life.
- No second calendar day was observed. The change between runs is a SEEDED reconstruction.

## Part 2 — My reflections (Aditya)

*To be written by Aditya in their own words:*
- *What surprised me:*
- *What I would do differently:*
- *Where I disagreed with Claude, and why:*
