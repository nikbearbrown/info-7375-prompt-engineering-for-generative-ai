# FRICTIONAL — Job-Search Agent 2

## Executive summary

This is my dated log of what was tried, what broke, what was checked, and what I accepted, changed or rejected from Claude.
- **The biggest finding** came from running the JS1 rule on more real data: R3 rejected 364 US postings that spell their state in full.
- **Three other gaps** were found along the way, each fixed with a test written first:
  - a redirect could leave the allow-list;
  - a workdir outside `runs/` was caught only after a request;
  - two runs in the same second collided on file names.
- Each entry names who did the work and points to a commit or file.

## 2026-11-09

| # | What happened | What was checked, changed or learned | Who · trace |
|---|---|---|---|
| 1 | Chose the starting point: my own JS1 code, not the Reallocation Engine or Lectern | I already understood my JS1 rule, and the assignment allows building on it. Copied unchanged, so the diff from JS1 is visible | My choice · `317d931` |
| 2 | GATE decisions. Claude offered options; I chose | All four boards (Greenhouse ×2, Ashby, Lever) plus one failing board; 6 boards / 12 requests / 120 s; retry once only for timeouts and 5xx; approval for both risky writes. Claude drafted the exits, the repeat rule and W1–W5. **I approved GATE before any code** | **Me**, wording by Claude · `a78bea8` |
| 3 | Probing the boards, Claude asked Greenhouse for `ramp` | It returned HTTP 200 with **one** posting ("Copy of Chief Legal Officer"), while Ramp's real board on Ashby has 176. This became the finished-wrong-answer demonstration | Claude found · `FINISHED-WRONG.md` |
| 4 | Tests committed before the loop code; first run 74/75 pass | (a) The same-stamp test showed that two runs in one second would collide on file names, so the loop now adds a counter (evidence is never overwritten). (b) The symlink case was **skipped**: this Windows account cannot create symlinks (WinError 1314). Rather than accept a skip, the test now uses a directory junction, which an ordinary user can create and which escapes the same way. No assertion was weakened | Claude · `ff7a40c` → `14909bd` |
| 5 | **Real run 1**: 4 boards ok, `no-such-board-js2` → 404 | Exit `incomplete`, as GATE says. The 404 was not retried (one request in the trace). The failed board shows no count and no "0 new". 5/12 requests, 3.1 s | `runs/live/` |
| 6 | Finished-wrong run + crosscheck | The agent said `finished`, Ramp = 1. The independent crosscheck flagged it (Ashby = 176). A side finding: Ashby's raw response had 176 postings, but the agent kept 172, because it drops `isListed: false`. Checked in the raw file (4 such postings) | Claude ran, I read the output · `runs/wrong-ats/` |
| 7 | Ran the JS1 rule over all 1,561 real postings | **364** Databricks postings failed R3 although they are in the US (`San Francisco, California`), because R3 knew only two-letter codes. The same defect as JS1's unresolved Stripe note, now measured | Claude found · `review/01` |
| 8 | **I predicted** the hard cases before any patch | D.C., `Remote - California` and `California` alone pass; `Tbilisi, Georgia` fails. The test failed on the old code (4/8) | **Me** · `20799aa`, `review/02` |
| 9 | A separate Claude Code session wrote the patch | Behaviour on real data: 358 fixed, 0 broken, **6 still failing**, because the patch had silently dropped Georgia. Its docstring also announced a "Revision 2026-11-09" that I had not approved | Claude Code wrote; reviewed together · `review/04`, `review/05`, `review/06` |
| 10 | **My decision: revise** | Two Georgia tests were written first and failed (`db56c1e`). The same session revised the patch. Result: 364 fixed, 0 broken, 0 still failing. **No final verdict changed**: every affected posting fails another check | **Me** · `review/10`–`review/13` |
| 11 | **I ran the commands myself** in PowerShell | `git diff agent/rule.py`, the full suite (86 OK) and the comparison (364 changed, 0 verdicts). I learned how to run commands and save their output. Then I **accepted** | **Me** · `review/07`, `review/08`, `59e9c5c` |
| 12 | I asked whether Claude had read Lectern; it had not | Reading it, Claude noticed Lectern refuses redirects, and that my fetch followed them, a way around the allow-list. **I decided to close it** as a dated GATE revision; the test was written first | **Me** decided · `30a3ac7` → `eedf18d` |
| 13 | Claude told me there were 87 tests before my run; my run showed 86 | A miscount in the chat, not in a file. The README uses the counts from actual output | Corrected |

## 2026-11-10

| # | What happened | What was checked, changed or learned | Who · trace |
|---|---|---|---|
| 14 | Claude tried every README command in a scratch folder | `--workdir ../outside` **made a real request first**, had its writes refused, then crashed with a traceback (exit 1, not a GATE code). No file was written outside, but the order was wrong. Test first (`test_cli.py`), then the fix: the workdir is checked before any request, exit 2 | Claude found · `e2dfc4b` |
| 15 | **Real run 2**, 23:43 UTC, on the state left by run 1 | 34 new postings (Pinterest 6, Databricks 16, Ramp 9, Palantir 3), all `not_relevant` for the persona. The 404 board again gave `incomplete`, one request, no retry. Pinterest listed 165, two fewer than run 1, although 6 were new: postings are also removed, and the agent does not report removals. Claude compared the JS1 rule with the accepted one on these 34: R3 differs on 2 (`New York City, New York`, `Remote - Washington`), fail → pass, no verdict changed | Claude ran · `runs/live/terminal-run2.txt`, `review/14` |
| 16 | After run 2, `review/reproduce_r3.py` and `compare_behaviour.py` would have read run 2's files too, so their output would no longer match the saved `review/01`–`13` | Both now read only run 1's stamp, as the README says. Checked: `reproduce_r3.py` output is identical to `review/13` | Claude · this commit |
| 17 | Before submitting, Claude scanned every tracked file for private data | The first line of each Claude Code session log (`review/03-…jsonl`, `review/10-…jsonl`) was the system `init` record, which lists local paths and the connectors on my account; it was removed, as in JS1. Nothing else in those logs changed. In `review/07` my Windows user name in temp-file paths was replaced by `<user>`. Everything else is unchanged; job postings mention words like "password" only in their public text | Claude · this commit |
| 18 | A check of the zip (by another reviewer I asked) found two gaps: (a) `review/compare_behaviour.py` called `git show`, so without `.git` it crashed (`AttributeError: module 'rule_before' has no attribute 'judge'`); `run2_old_vs_new.py` had the same problem. (b) The commit hashes cited in the docs could not be checked from the zip | (a) The old rule is now saved as `review/rule_before_r3.py` and both scripts read it; their output is identical to `review/12` and `review/14`, and every README command was then run in a copy with no `.git`. (b) `.git` is still left out, because its old file versions contain what #17 removed; instead `review/git-log.txt` prints the full history, and the README says so | Found by the reviewer; fixed by Claude; my decision to keep `.git` out |

## What I accepted, modified or rejected from Claude

- **Accepted:**
  - the drafted exits, repeat rule and W1–W5;
  - all code and tests;
  - the junction fallback for B09;
  - the finished-wrong demonstration;
  - the workdir fix.
- **Modified:**
  - the R3 patch: Georgia kept, and the "Revision" wording removed before I accepted it;
  - the policy, by my redirect revision.
- **Rejected:**
  - the first R3 patch as written;
  - a docstring claiming a contract revision I had not approved.

## Still unresolved

- No real timeout, 5xx or budget exhaustion against the live APIs. Only the 404 is real; the others are tested with fakes.
- The crosscheck cannot catch a wrong board name on the right system (Lectern's HubSpot case).
- The test output is noisy with `ResourceWarning: unclosed file`, from file reads in the tests and in JS1's `watch.py`. It is harmless, but not cleaned up.
- Cities of the country Georgia outside the 4-city list are read as the US state.
