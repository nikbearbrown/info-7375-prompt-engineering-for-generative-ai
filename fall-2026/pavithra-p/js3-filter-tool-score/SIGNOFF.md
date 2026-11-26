# Sign-off: Job-Search Agent 3

```text
Sign-off - Job-Search Agent 3

Checked:      1. The filter does what FILTER.md says, for v1.0 and v1.1: test_filter.py (16 tests) and
                 test_filter_v1_1.py (12), on constructed postings and on the real postings behind each v1.1
                 change, including the counts on the saved run (7 kept by v1.0, 15 by v1.1).
              2. My own predictions for three constructed postings (A keep, B reject, C keep), given before
                 test_my_predictions.py existed: all three held, for v1.0 and v1.1.
              3. The three wrong versions in FILTER.md section 5 are each caught: test_filter_wrong_versions.py.
              4. A failed board is never counted as rejected: test_failed_board_gives_no_postings_and_is_listed_as_failed,
                 and in the real run no-such-board failed with HTTP 404 and gave no postings.
              5. The reject audit: my 68 blind hand labels (audit/hand-labels.csv), with the two location
                 corrections I asked for noted in the file, and my second pass on the 27 engineering postings
                 (audit/reread-labels.csv). The counts in AUDIT.md come from python3 -m agent audit.
              6. The shortlist: my own labels on all 37 of Claude's claims against the posting text
                 (audit/claim-labels.csv), including five I changed after review because the claim said more than its quote.
              7. The tool server: test_toolserver.py (16): no network connection, writes only its transcript inside
                 its folder, refuses undeclared arguments and tools, declares the boards from config/boards.json,
                 answers "I cannot tell" for the failed board, and survives malformed params. The real transcripts show Claude calling it
                 with only that one tool available (transcripts/claude-client-20261125T223407Z.jsonl).
              8. The other server: its 13 answers were the same with the network blocked (scripts/run_blocked.py,
                 checked by test_run_blocked.py).
              9. What moves the score: every filter change measured alone on the held-out set
                 (python3 -m agent measure), after the v1.1 choices were committed (70ddf4b), and one change to
                 the context Claude is given, measured on the same labels (python3 -m agent judge).

How:          By hand: approving FILTER.md v1.0 before any code; rejecting change G; the 68 posting labels and
                 the 27 second-pass labels; the 37 claim labels.
              By a test whose expected answers I set before reading Claude's code: tests/test_my_predictions.py.
                 Claude Code showed me three constructed postings and I gave the verdicts (A keep, B reject, C keep);
                 Claude Code then wrote the test code around my answers. Claude Code wrote every other test, and I
                 chose what they check (FILTER.md sections 2, 4 and 5 came first).
              By recomputation: every number in AUDIT.md, SHORTLIST.md and SCORE-REPORT.md is recomputed by a
                 script from the saved raw responses, Claude's saved replies and my label files (README.md).
              With Claude's help: Claude Code wrote the code, the tests, the labelling pages, and the first
                 drafts of these documents. It ran the commands, and it applied the two location corrections I asked
                 for. Claude (claude-opus-5-5 through claude -p) wrote the 37 shortlist claims and the 40 held-out
                 verdicts.

Not checked:  1. My labels were quick, judged from the title, the location and the years line on the page, and
                 my two passes disagree on 13 of 27. No second person labelled them.
              2. Prediction B (Austin, TX) matched, but v1.1 rejects it only because Austin is not on the G1 city
                 list. A US city that is not on that list and has no "US" in its location is still rejected.
              3. The checker's skills rule still asks for a résumé skill word in the quote (SHORTLIST.md, #37).
              4. The abstention rule does not check whether a supported claim is in Rohan's favour (the Android
                 counterexample). Not fixed.
              5. My tool server's filter file path is fixed in the code, it answers tools/call before initialize,
                 and its "idempotent" holds only within one collection.
              6. Two word-rule limits (FILTER.md section 8): G3 reads "operating for 10 years" as an ask for
                 10 years, and G4 reads "alongside senior software engineers" as a senior role.
              7. Whether any shortlisted posting is still open, or would interview Rohan.
              8. Only one collection (2026-11-25). Nothing here shows how the filter does on later postings.

Not claiming: That v1.1 is better than v1.0: on the held-out set both agree with my labels on 13 of 20, and on
              my second pass v1.0 agrees on 21 of 27 and v1.1 on 18.
              Any rate for all 577 rejects: the sample found 5 of 30, which is a 95% interval of 7% to 34%.
              That Claude's claims are true beyond the posting's own text.
              That anything was trained: every number was set by me or inherited (SCORE-REPORT.md).
              That the tool server is safe with any client other than the two I tested (my scripted client and
              Claude Code 2.1.294).
              That claude mcp serve behaves the same under other settings: I probed it once, as installed.
              The agent never applied, emailed, messaged anyone or logged in anywhere.

Signed or withheld: Signed, Pavithra Prasad, 2026-11-25
```

## Driver's seat

| Task | What Claude should do | What I should do | Why |
|---|---|---|---|
| Collect postings | run the bounded loop, save every raw response, report a failed board as failed | choose the boards, the budgets and the allow-list | which sites the agent may touch is a permission decision |
| Write the filter | turn my rules into code and tests, and show each verdict with its reason | write the rules with a reason each, approve them before any code, decide every change | the rules say what Rohan wants; Claude can only guess that |
| Audit the rejects | draw the sample with a fixed seed, build a blind page, count, compute the intervals | label each posting myself, without seeing the filter's verdict, and say what the errors mean | the audit measures the filter against my judgment; if Claude labelled, it would be measuring itself |
| Choose changes | try each candidate alone and report the tuning numbers | decide which changes to make (I rejected G against my own labels) and keep the held-out set out of it | a change that fits my labels can still be wrong for Rohan |
| Justify the shortlist | write claims with quotes copied from the posting, and give a first label | label every claim against the posting text | finding a quote is not the same as proving a claim (`SHORTLIST.md`) |
| Use the tool | call `score_posting` and report what it returned | decide which tools Claude gets, and whether to trust a server | a server's description is its own claim; only checking its behaviour tests it |
| Decide whether a posting is worth Rohan's time | nothing beyond the record and the reasons | read the posting and decide | the filter sees words, and Claude sees only the text it is given. Neither knows what Rohan wants, where Rohan can work, what pay or role Rohan would accept, or how far to stretch. My own labels disagreed with my own rules, which shows this judgment is not a word match. The decision, and being accountable for it, stays mine |
