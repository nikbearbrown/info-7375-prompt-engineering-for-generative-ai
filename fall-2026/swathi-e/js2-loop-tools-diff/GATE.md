# GATE.md — Job-Search Agent 2: exits, budgets and permissions

Written by Swathi Baba Eswarappa, 2026-11-04, before any JS2 code.
Claude (chat) helped me phrase my decisions; I confirmed every line.
Built on my JS1 agent (fall-2026/swathi-e/js1-contract-and-watch/).
Persona: Priya Nair (fictional).

## Boards
| Board | System | Endpoint host |
|---|---|---|
| Databricks | Greenhouse | boards-api.greenhouse.io |
| Stripe | Greenhouse | boards-api.greenhouse.io |
| Plaid | Ashby | api.ashbyhq.com |
| Deliberate failure: a board name that does not exist | Greenhouse | boards-api.greenhouse.io |

The deliberate failure uses an allow-listed host, so it tests my error
policy, not my permission policy.

## Exits
Every run ends with exactly one exit status, and reports it:
- finished: every board returned a valid, non-empty response that was
  successfully parsed. Reports new postings per board.
- incomplete: at least one board failed or was empty. Reports which boards
  succeeded, which failed, and why. Results for failed boards are not invented.
- budget-exhausted: a budget ran out before all boards were tried. Reports
  which budget, and which boards were not tried.
- error: the agent itself broke (bug, unreadable state file, invalid persona).
  Reports the error and changes no state.
A run that stops is not a run that succeeded: only "finished" means every
board returned a valid, non-empty, parsed response.

## Budgets (per run)
- Maximum 5 boards.
- Maximum 15 requests, retries included.
- Maximum 60 seconds.
A budget is checked before each request, not after. Only I can change a
budget, and only by a new dated decision in this file.

## Repeat rule
The same action means the same URL requested twice in one run.
- The one retry my error policy allows for a temporary failure is not a repeat.
- Every other duplicate request is skipped, not sent, and recorded as
  "skipped repeat".

## Error policy
- 404 (board not found): no retry, because a missing board will not appear on
  a second try. The board is marked failed; the loop continues.
- Timeout or server error (5xx): retry once after a short wait, because these
  are often temporary. If the retry also fails, the board is marked failed;
  the loop continues.
- Empty response (no body, or a job list with 0 postings): no retry. Never
  reported as "0 new jobs". The board is marked "empty, unverified", the state
  file is not updated for that board, and the run ends incomplete.
- Escalate to me: any exit other than finished is reported to me in the run
  summary. The agent never changes its own budgets, allow-list or boards.
The empty response and the timeout are demonstrated with SIMULATED responses
in tests, clearly labeled as simulated. The 404 is a real live failure.

## Permission policy (enforced in code, not in a prompt)
- Hosts: only boards-api.greenhouse.io and api.ashbyhq.com. The host must
  match exactly; a lookalike host is refused.
- Reads: only files inside my JS2 folder and Priya Nair's persona files.
- Writes: only inside my JS2 folder's runs/ and state/. Paths are resolved
  (including .. and symlinks) before checking; a path outside is refused.
- Evidence: raw responses and run traces are saved in separate new files for
  each run. The agent never silently overwrites earlier evidence.
- Needs my explicit approval before the action: deleting or resetting the
  state file. The agent cannot approve its own requests.
- Never: apply to a job, send email, send messages, or log in anywhere.

## Wrong versions my tests must catch
1. An empty board reported as "0 new jobs" and the run ending "finished"
   (the finished wrong answer).
2. A failed board silently dropped, with the run still ending "finished".
3. A 404 retried, or a temporary failure retried more than once.
4. A budget checked after the request, so a run makes one request too many.
5. The permitted retry treated as a repeat and skipped, or a real duplicate
   request sent twice.
6. A host check by substring, so a lookalike host
   (e.g. boards-api.greenhouse.io.evil.example) is allowed.
7. A path check by string prefix, so "jobs-evil" beside "jobs", a "..", or a
   symlink escapes the allowed folders.
8. A failed board's results filled in from the previous run, as if fetched.
9. The agent resets its state without my explicit approval, or approves its
   own reset.
10. A new run overwrites an earlier run's raw response or trace.

## Revision (2026-11-04, before any loop code)
Decided after reviewing Claude Code's loop proposal:
- Exit precedence: if several exits apply, error > budget-exhausted >
  incomplete > finished.
- Per-request timeout: 15 seconds, or the seconds left in the budget if fewer.
  Wait before the one permitted retry: 2 seconds.
- Other failures (other 4xx codes such as 403 or 429, invalid JSON, or a valid
  response of the wrong shape): the board is marked failed, with no retry.
- Ashby: postings with isListed false are skipped and counted in the trace;
  secondaryLocations are included in a posting's location.
- Each new posting gets my JS1 rule's verdict, labeled as a record.
- Because the deliberate bad board always fails, every live run ends
  incomplete. "finished" is demonstrated in tests with simulated responses.
