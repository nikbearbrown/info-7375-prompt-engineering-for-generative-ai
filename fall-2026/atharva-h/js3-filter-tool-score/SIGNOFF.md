# Sign-off — Job-Search Agent 3

**Status: Claude's draft. The signature is blank until I have checked every row below myself.**

## Checked

| Property | Checked by | How |
|---|---|---|
| The filter does what FILTER.md v1.0 says: R1–R4, the score, threshold 4, and a missing field never rejects | `tests/test_filter.py` (15 tests). Includes checks that the threshold and the role phrases in the code match FILTER.md's text. | With Claude's help: Claude wrote the tests, and the suite was run with AI help |
| Neither wrong version is the real filter | `test_wrong_1_substring_…` and `test_wrong_2_title_only_…` | With Claude's help. Each test shows the wrong version gives the wrong result and the real filter doesn't. |
| The labels are mine | `state/labels/labels.csv` and `labels_v1_1.csv`, `reviewed` column | I reviewed all 114 of Claude's drafts against Riley's profile on 2026-11-24 and 11-25 and kept every one. Claude's drafts are kept unchanged beside them. |
| Held-out labels were never used to choose | `split.json` and `split_v1_1.json` were drawn before any filter existed. The audit is drawn only from outside held-out (`audit.py`). The `SCORE.md` decisions cite held-out only. | With Claude's help; the commit order shows the labels before `filter.py` |
| The reject-audit verdicts are mine | `state/audit/audit_v1.0.csv`, `your_call` and `reason` columns | I judged all 50 rows myself on 2026-11-25, in my own copy of the sheet. They were copied in unchanged. Claude drafted none. |
| The claim labels are mine | `state/claims/base_checked.csv`, `my_label` column | I labeled all 72 myself on 2026-11-25 by checking each quote against its claim, in my own copy of the sheet. My labels were copied in unchanged. Then, at my request, the two labels that broke FILTER.md's exact-span rule were changed to insufficient (noted in the rows). Result: 41 supported, 3 contradicted, 28 insufficient, with 2 differing from the checker. |
| The tool server is read-only during a request | `test_a_request_never_writes_fetches_or_connects` | With Claude's help |
| The tool server works with a real client | `state/mcp/transcript_2026-11-25T190356Z.jsonl` (Claude Code 2.1.331) | Run with AI help on 2026-11-25 |
| Every number has an origin | `SCORE.md`, "Where every number comes from" | With Claude's help. Each row names the script and file that produced it. |

All 98 tests passed when `python3 -m unittest discover -s tests` was run with AI help on 2026-11-25.

## Not checked
1. **Recall on anything but 2 postings.** There are only 2 "yes" labels, both held-out and both FanDuel. Recall of 2/2 cannot separate a good filter from a lucky one.
2. **The job market.** The 14 boards were picked by rules aimed at analyst titles, and the supplement was picked to contain matches. No number here describes postings in general.
3. **Claude's run-to-run variation, beyond one repeat.** The base prompt was run twice. Two runs show variation exists, not how large it usually is.
4. **"Toronto, CA" counts as US.** "CA" is also California's code. It is one posting, found and left in v1.0.
5. **Spelled-out years.** "Five years of experience" doesn't fire R2. A test records this as known behavior.
6. **Other platforms.** macOS with Python 3.14.7 only. The Fetch server ran on Python 3.12.

## Not claiming
- **That a kept posting is worth applying to.** The filter keeps 12 postings, and I labeled only 2 of them "yes".
- **That "I cannot tell" is a correct answer.** It is reported as coverage, never as accuracy.
- **That a quote the checker found proves its claim.** I labeled two found quotes insufficient (`SHORTLIST.md`).
- **That anything was learned.** Saving labels, verdicts, and claims changed no model (`SCORE.md`, "Persistence is not training").
- **That the agent applies, emails, or contacts anyone.** No tool here does. The tool server has one read-only tool.

## Signed or withheld
Signed or withheld: ______

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The filter document | Interview me, offer options, and flag where its own recommendation fails | Choose every rule, weight, and version | The rules decide what counts as a match for Riley. That is a judgment about a person's job search, and Claude would be grading its own work. | `126a2fd` (FILTER v1.0) before `05cf8653` (code); `6a3ea0f` (v1.1 rule) before its probe |
| Labels | Draft each one with a reason | Review every one, and change any I disagree with | A label says whether Riley would apply. If Claude set the yardstick and also built the filter, the measurement would measure nothing. | `labels_claude_draft.csv` beside the `reviewed` labels |
| The reject audit | Draw the sample, and show the verdict and its reason | Judge every row myself | The brief requires it. It is also the only check on whether a rejected posting was worth Riley's time. | `state/audit/audit_v1.0.csv` |
| **Judging a posting's worth** | Report the filter's rule output, the claims, and the quotes; abstain when the evidence is missing | **Decide whether a posting is worth applying to** | **The filter and Claude read words. Whether a job is worth Riley's application depends on things no posting states and no rule tracks: how a 6-month internship compares to "1+ years", whether a part-time role is a stepping stone, how much a visa risk is worth taking. The tool server says so in every result ("not a judgment of whether to apply").** | `mcp_server.py` `note`; `SHORTLIST.md` counterexample 1 |
| What moves the score | Run one change at a time, and say when a difference is noise | Choose which changes to adopt | Adopting a change is a decision I sign. It rests on held-out evidence, not on Claude's account of its own change. | `SCORE.md`, "What I change" |
| Tools and trust | Build the server, test its claims, and read other servers' source before running them | Approve what gets installed, and which tools a session may hold | What a tool can reach is a risk to my data, not Claude's | `MCP_EVAL.md`; the Fetch install was approved in-session |
