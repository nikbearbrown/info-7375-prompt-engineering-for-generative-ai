# Appendix: A Job-Search Agent You Can Check

Varnika M · INFO 7375 · Final Project Film · 2026-11-23

The film keeps each part short. The detail behind it is here, in the same four parts and the
same order. Past tense is used only for what exists and can be shown. Everything else is the plan.

## 1. Executive summary: what and why

I'm building a job-search agent. It reads public job boards and picks out the few postings that
fit one person. It shows why each posting made the list, and it leaves the decision to that
person. It never applies for a job or sends anything.

Why it matters: most postings don't fit. On 2026-10-31 my written rules checked all 675 postings on
Anthropic's board against a made-up candidate, and one matched. Reading every posting by hand
takes hours. A tool that does the reading for you is only worth using if you can check its
reasons, so the agent shows them instead of asking you to trust it.

## 2. Introduction: what others have done

All of these come from the companies' own pages, fetched on 2026-11-23. Quotes, URLs and
fingerprints are in [evidence/others-2026-11-23/README.md](evidence/others-2026-11-23/README.md).

| Kind | Tool | What its own page says | What it leaves out (on that page) |
|---|---|---|---|
| Job alerts | LinkedIn Job Alerts | An alert for your current search; daily by default, by email and in-app | Why a job matched |
| Job alerts | Indeed job alerts | Email about new jobs that match your search, daily or weekly | Why a job matched |
| AI matching | LinkedIn Skills Match | Compares your profile with the job description | A rule you can recheck |
| AI agent | Jobright Agent | "matching roles, customizing your resume, and applying for you" | Whether a person approves first |
| Auto-apply | LazyApply | "Our agent handles the entire application process." | Whether a person approves first |
| Auto-apply | Simplify Autopilot | "There is no review step before submission." | A review step |
| Assisted apply | Simplify Copilot | Fills the form; you click the final Submit button yourself | Applies to one form, not to a shortlist |

**So what's left?** Finding and applying are both automated. The human step that exists
(Simplify Copilot) covers a single application form. None of these pages mentions rules you can
recheck, a separate program that checks each run, or a person approving a whole shortlist. Those
three are what this project adds.

**Limits of this survey:** seven pages, read on one day. They are company claims, and nobody tried
the products. LinkedIn's Premium "how you match" page returned 404 and is not included.

## 3. Methods: how I'll build it

### Data

| Source | Feed | Login? |
|---|---|---|
| Anthropic | Greenhouse, `boards-api.greenhouse.io/v1/boards/anthropic/jobs` | No |
| Palantir | Lever, `api.lever.co` | No |
| Linear | Ashby, `api.ashbyhq.com` | No |
| The candidate | `persona/` (fictional, `@example.com`, 555 phone): Aarav Patel | — |

No real person's data is used. My own résumé stays on my machine.

### What exists today

| Assignment | What it does | Evidence |
|---|---|---|
| JS1, due 2026-10-31 | Watches Anthropic's board and reports only new postings. Judges each one with five written rules (title, seniority, location, experience, skills) and, labeled as an opinion, with Claude. | [../../js1-contract-and-watch/](../../js1-contract-and-watch/README.md), 73 tests (re-run OK 2026-11-23) |
| JS2, due 2026-11-10 | A bounded loop over four boards on three systems (one fails on purpose), with request and time budgets and a permission policy in code. A separate `check_run.py` checks every run. Live run 2026-11-10 read 677 + 304 + 33 = 1,014 postings. The checker caught a real bug in my own run 2. | [../../js2-loop-tools-diff/](../../js2-loop-tools-diff/README.md), 122 tests (re-run OK 2026-11-23) |

### The plan, step by step

1. **JS3 (Chapters 7–9):** a filter written as a document I can read, with a reject audit of at
   least 30 rejected postings. A shortlist where every claim is labeled supported, contradicted
   or insufficient against the posting text. The agent offered to Claude as a tool through a small
   tool server I write myself. Measured changes to the score, one change at a time.
2. **JS4 (Chapters 10–12), due 2026-12-01:** a written, reviewed plan before every run, a check on
   every claim the agent makes about a posting, and versioned memory across days.
3. **JS5 (Chapters 13–15), due 2026-12-13:** the human approval gate, bound to a fingerprint of the
   exact shortlist. A register of data and people. A controlled failure, triggered on purpose.
4. **Final project, due 2026-12-20:** the ten-document packet, a stranger run from the README, and
   a demo of five minutes or less.

### Do I have what I need?

| Need | Have it? |
|---|---|
| Language and libraries | Yes: Python standard library only, nothing to install |
| Model access | Yes: Claude Code, provided through NEU. JS1's Claude judge runs through `claude -p`. |
| Data | Yes: free public feeds, no accounts or keys |
| Compute | Yes: my laptop. Every run so far took seconds. |
| Paid API credits | Not needed |

## 4. Evaluation: how I'll know it worked

Pass lines chosen by me on 2026-11-23 ("strict").

| # | Check | It worked if | It didn't work if |
|---|---|---|---|
| 1 | **Reject audit:** 30 postings the filter rejected, picked at random, each judged by me against the candidate | At most 1 of the 30 fits the candidate | 2 or more fit |
| 2 | **Must-skip list:** postings the agent must skip (closed, wrong location, keywords only) | Every one of them is skipped, and the run skips at least half of everything it evaluates (the JS5 rule) | Even one gets through, or it skips less than half |
| 3 | **Planted failures:** failures I trigger on purpose | The separate checker catches every one | Any planted failure passes the checker |
| 4 | **Approval binding:** change one posting after approval | The old approval stops counting | A changed shortlist still counts as approved |

If all four pass, it worked. If any one fails, it didn't, and the final report will say which.

**What these checks cannot show.** A sample of 30 cannot prove the filter misses nothing. Even 0
misses in 30 is consistent with a true miss rate of up to about 10% (the "rule of three", 3/30). The
must-skip list only covers the traps I thought of. The checker can only catch failures it has a
rule for. And all of it is tested on one made-up candidate, so it says nothing about other
people's searches.
