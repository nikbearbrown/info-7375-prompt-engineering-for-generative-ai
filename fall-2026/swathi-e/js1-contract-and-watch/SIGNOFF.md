# SIGNOFF.md — Job-Search Agent 1

Swathi Baba Eswarappa, 2026-10-27.
Claude (chat) compiled the table and lists below from our session records;
I checked every row and confirmed them. The closing paragraph is my own words.

## Checked (which property, by which test)
| Property | Test / evidence | How |
|---|---|---|
| The rule does what my contract says | tests/test_rule_cases.py — my 12 hand-fixed cases (0c9e8a0, fcf28eb) | By tests written before the rule code they test (cases 1-8 before any rule code; cases 9-12 before the Revision 2 rule-code change, c7b25d1): I chose the inputs and verdicts; Claude Code wrote them into the test file |
| The agent's report checks reject wrongly-shifted labels and justifications that cite no field | tests/test_agent.py | With Claude's help (Claude Code wrote these tests) |
| The judge's validator accepts and rejects exactly what my judge contract says | tests/test_judge.py (24 tests; all 50 tests in the suite pass, also with claude removed from PATH) | With Claude's help (Claude Code wrote these tests) |
| The second run's 3 new ids are really new | recomputed from the two raw board files | With Claude's help (Claude Code recomputed them) |
| The baseline prompt matches my judge contract | line-by-line comparison | By hand, with Claude's help (Claude Code listed where it departed from my contract; Claude chat also compared it with me) |
| My 20 labels follow my labeling rule | I read all 20 saved descriptions | By hand |
| The 8 rule-passing jobs don't fit Priya | I read all 8 descriptions (Oct 25) | By hand |
| Experiment scores (measures A and B) | experiments/results_development.json, results_held_out.json | With Claude's help (Claude Code's scorer, fixed before any run) |
| The chat surface | I ran it myself | By hand |

## Not checked
- All 20 of my labels are "not relevant", so the experiment can't show whether a prompt finds relevant jobs.
- One call per posting in the experiment; only 4 calls per posting in the sampling report.
- The validator checks quotes, not the reason text; citation lists don't prove which fields Claude used.
- The agent surface's fetched text wasn't saved, and the chat surface's model wasn't pinned.
- The rule: multi-location strings, the broad "Analyst" keyword, and it never reads descriptions.
- One board, two days of board data (Oct 25 and Oct 26 snapshots).

## Not claiming
- I am not claiming the judge can find relevant jobs; my data had none.
- I am not claiming my prompt change works beyond these 20 Databricks postings.
- I am not claiming Claude's "reason" text is accurate; only its quotes were checked.
- I am not claiming the rule or judge would work on other boards.

## Driver's seat — who decided each thing
| Decision | Who suggested | Who decided | Pointer |
|---|---|---|---|
| Watch Databricks only (not 5 boards) | Claude recommended Databricks | Me (rejected 5 boards) | FRICTIONAL.md, Oct 25 |
| Relevance rule + Revisions 1(b) and 2 | Me; Claude showed real-title results | Me | 4f2b42e, 2b4ce77, 2ea6437 |
| 12 hand-fixed test cases | Me | Me | 0c9e8a0 (1-8), fcf28eb (9-12) |
| Judge contract rules (0-1 yrs, citizenship → not relevant, "experience not stated") | Claude asked the questions | Me | 1c08af1 |
| "Remote" means US only | Claude Code flagged the gap | Me (approved) | 20587be |
| Baseline prompt wording | Claude Code wrote it | Me (reviewed against my contract) | 6593b5e, a5c956e |
| Labeling rule (4 checks + my "no experience stated" rule) | Claude offered the checks | Me (added my own rule) | a554f58 |
| 8 already-read jobs → development set | Claude Code | Me | 6b1d5b5 |
| The 20 hand labels | — | Me (read every description) | 778614a |
| Sampling postings, the one prompt change, measures A and B | Claude (chat) suggested | Me (approved) | bd9c03c |
| Keeping the revision prompt | My plan's rule | Me | 02cec7c |
| Chat reply recorded as rejected, not repaired | Claude Code offered options | Me | e069d8e |
| File-based judge as least autonomy | Claude Code laid out the risks | Me (my defense) | dfc2bb9 |

## Driver's seat — what Claude does, what I do, and why
| Task | What Claude should do | What I should do | Why that part stays mine (my words) | Pointer |
|---|---|---|---|---|
| Code and tests | Write the code and the tests | Check the results myself | I let Claude handle the coding and tests because it can do the technical work faster, and I can check the results to make sure everything works as expected. | 0c9e8a0 (my cases, before code), then 6b7552c (Claude Code's code) |
| Relevance rule and contracts | Ask questions, show where my rule gives unexpected results, phrase my decisions | Make every rule decision | I wanted to make these decisions myself because I need to decide what kind of jobs are actually suitable for Priya, rather than letting Claude decide for me. | 4f2b42e, 2ea6437, 1c08af1 |
| Labeling the 20 jobs | Lay out the facts of each posting against my checks | Read each description and decide the label | I did this myself because a job might look relevant based on its title, but only after reading the description can I decide whether it's really a good fit for Priya. | 778614a |
| Sign-off | Draft tables from the records and check every line against the commits | Decide what I can honestly claim | This has to be mine because only I know what I personally checked and what I didn't. I don't want to claim I verified something just because Claude said it worked. | 0d5de4a (committed only after Claude Code checked every line; before committing, I removed a claim I couldn't support) |

## In my words
I want the grader to know that even though I used Claude for coding, testing, and suggestions, I made the final decisions myself. I didn't just accept everything Claude suggested. I checked the job descriptions, decided which roles were suitable for Priya, made changes to my rules when I found problems, and chose the approach I felt was easier to verify. This assignment helped me understand that getting an output from AI isn't the same as knowing whether it's correct.

## Signed
Signed: Swathi Baba Eswarappa, 2026-10-27.
