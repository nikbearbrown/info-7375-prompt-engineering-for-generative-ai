# GATE — Job-Search Agent 2

Written 2026-11-07. The four boards are Stripe (`stripe`, Greenhouse), Cloudflare (`cloudflare`, Greenhouse), OpenAI (`openai`, Ashby), and `striqe` (Greenhouse, deliberately misspelled). A direct check returned 200 for `stripe` and 404 for `striqe`.

## 1. Exits

| Exit | When | What the summary says | State for the next run |
|---|---|---|---|
| `finished` | Every board ended `ok`. | Show each board's result. | Update seen job IDs for every board. |
| `incomplete` | At least one board ended `ok`, and at least one ended `failed` or `skipped` for a reason other than a budget (for example a 404, or the user interrupting the run). Three `ok` boards and one 404 produce this exit. | List every board with its status, and the app error code and reason for each `failed` or `skipped` board. | Keep updates for `ok` boards only. |
| `budget-exhausted` | A budget prevents scheduled work from finishing. | Name the exhausted budget and identify completed work and unfinished work with reasons. | Keep updates for boards that completed successfully. |
| `error` | Input is missing or invalid, all attempted boards fail after the list is processed, or a shared failure prevents further work. | Report the failing stage, app error code, and reason. Include any board results already available. | Keep prior state for every failed or unvisited board and preserve updates already committed for successful boards. |

If more than one row fits, the first match wins, in this order: `error` for missing input or a shared failure, then `budget-exhausted`, then `error` when no board ended `ok`, then `incomplete`, then `finished`.

Each board ends with its own status, named differently from the run exits so the two never mix: `ok` (fetched and fully processed), `failed` (an error code is recorded), or `skipped` (never attempted, because a budget ran out or the user interrupted). Each board is handled independently. A board is `ok` after its required processing completes. An empty job list is a validation error. A board that is `ok` and has 0 new postings is a normal result, not an error: it tells me there is nothing new to act on. Only successful boards update seen job IDs. A failed board has no job count. Record failure stages through three-character app error codes. The first digit identifies the stage, and the final two identify the failure. Resolve codes to messages through one shared mapping when reporting. Initial examples are `001` for missing input, `101` for board not found, `102` for a fetch timeout, `201` for an empty list, and `202` for an invalid board payload (for example, no `jobs` key). Preserve any upstream HTTP status separately in the trace.

Added 2026-11-09 (D21, Isaac; JS2 Step 8): `203` for a Greenhouse list whose length differs from the board's own `meta.total`, in either direction. A response with no `meta.total` (every Ashby response) can't be checked and is handled as before. This gap was known when this gate was written and left out on purpose (D6) so it could be shown as the finished-wrong demo and fixed in the review packet.

## 2. Budgets

| Budget | Maximum | Reason |
|---|---|---|
| Boards | 4 per run | Covers the three normal boards and one deliberate failure. |
| Board requests | 10 per run, including each retry | Gives each board an initial attempt and leaves room for eligible retries. Each outbound board request counts. |
| Total elapsed time, Claude off | 120 seconds | Bounds the default board run and its summary. |
| One board request | 10 seconds or the remaining board-phase time, whichever is lower | A slow board cannot consume the entire run. |
| Total elapsed time, Claude on | 480 seconds (8 minutes) | Allows 120 seconds for board work, 300 seconds for all Claude calls, and 60 seconds for reporting. |
| Optional Claude work | 30 calls and 300 seconds in total per run | 300 seconds of Claude already spends a fair amount of tokens. If there are 30 new postings, Claude runs 30 times. |

Claude is off by default. If enabled, finish board fetching first, then send every new posting to Claude, in board-list order and then posting order, whatever the rule judge decided: both judges look at each new posting so their differences show (JS1 "two judges"). Only the Claude budget limits how many are sent: stop at 30 calls or when the 300 seconds of Claude time are used up. Each call may use the Claude time that is left, so the last call can be cut short. Claude calls have a separate count from board requests. If a Claude call times out, record the timeout and keep the rule verdict. Report every new posting that was not sent because a Claude budget ran out; that makes the run `budget-exhausted`.

Changed 2026-11-08 (D20, Isaac): was "at most three rule-relevant new postings, 300 seconds per call, 1,080 seconds in total".

When a budget stops board work, mark unattempted boards `skipped` in the summary and name the budget. Only Isaac may change a budget. Record a new written decision in the task's `DECISIONS.md` before updating this gate.

## 3. Repeat rule

Within a run, skip and record a repeated request to the same URL or repeated processing of the same posting. Preserve the original job ID and identify a posting by source, board, and job ID. Continue after a skip.

An eligible retry under Section 4 is an exception to URL deduplication. Retry once. If the first retry fails with the same app error code, stop retrying that board. If it fails with a different retryable code, try one final time if the budget allows. Record all attempts. Each board gets at most three attempts, including its initial request.

## 4. Error policy

| Failure | Action | Retries | Reason |
|---|---|---|---|
| Fetch timeout, temporary connection failure, or temporary upstream failure | Retry within Section 3 and the budget. Continue to the next board if attempts fail. | Up to 2 | The failure may clear between attempts. |
| Board not found or request refused by policy | Record the failure and continue to the next board. | 0 | Repeating the same request leaves the cause in place. |
| Empty list, invalid board payload, or (added 2026-11-09, D21) a list whose length differs from the board's own `meta.total` | Record a validation error and continue to the next board. | 0 | The response failed validation. Leave its job count unset. |
| Invalid posting or individual Claude evaluation failure | Record the posting error and continue. Keep any existing rule verdict. | 0 | The failure is isolated to one posting or evaluation. |
| Missing required input, invalid shared configuration, or inability to write the required run record | Stop the run with `error` and print the stage, code, and reason. | 0 | Remaining work depends on the same required resource. |

Check whether the latest failure is retryable before comparing error codes. For example, a retry that changes from timeout to board not found ends the board immediately.

## 5. Permission policy

- Board requests may use HTTPS to the exact hosts `boards-api.greenhouse.io` and `api.ashbyhq.com`. Recheck every redirect destination before following it.
- With Claude explicitly enabled, the optional Claude Code judge may receive only selected posting and evaluation inputs. Board-fetch permissions apply separately.
- Only when Claude is enabled with `--claude-via api`, also allow HTTPS to the exact host `api.anthropic.com`. The default `claude -p` route needs no host here: Claude Code makes that connection itself, outside this program's allow-list.
- Anchor file checks to the project root. Read inputs under `data/`, `personas/`, `state/`, and `evidence/raw/`, plus `prompts/` when Claude is enabled.
- Allow writes under `runs/`, `evidence/raw/`, and `state/`. Creating a report and updating successful board state require no prompt. Check the resolved destination against the allowed directory before access.
- Ask the person running the tool before overwriting a historical report. Use a yes/no prompt identifying the destination. Proceed only on explicit `y`. Default to refusal when the answer is missing or input is noninteractive.
- Project data operations outside these boundaries are forbidden. The agent must never apply for jobs, email, message, or log in on the user's behalf.

### Boundary tests: expected outcome, written before running (≥10)

| # | Request | Expected (allow / refuse / ask me) | Why |
|---|---|---|---|
| 1 | Request a host outside the allowlist directly | Refuse | Only approved hosts may receive board requests. |
| 2 | Use `..` to reach a path outside the allowed output directory | Refuse | A relative path can escape the output directory and reach project files or user data outside the granted write boundary. |
| 3 | Write to `runs-evil/` next to the allowed `runs/` directory | Refuse | Write permission applies to the approved directory and its descendants. A sibling directory with a similar name is outside that boundary. |
| 4 | Write through a symlink inside the output directory that points outside it | Refuse | The resolved destination is outside the allowed output directory. Following the link could modify user files or place files outside the approved location. |
| 5 | Read and write the same configuration file in `data/` | Allow the read. Refuse the write. | The agent needs to read configuration to run. Keeping it read-only prevents a run from changing the settings that guide future runs. |
| 6 | Overwrite an existing historical report | Ask the user. Allow only after explicit confirmation. | Historical reports record prior runs. Confirmation prevents accidental changes to that record. |
| 7 | Request Stripe postings from `boards-api.greenhouse.io` | Allow | The host is on the board-fetch allowlist. |
| 8 | Create a new report under `runs/` | Allow without prompting | The directory is writable and the report does not already exist. |
| 9 | Follow a redirect from an allowed host to a host outside the allowlist | Refuse the redirected request | The redirect target requires its own permission check. |
| 10 | Attempt to overwrite an existing historical report and answer `n` | Refuse and leave the report intact | An overwrite requires explicit confirmation. |

## 6. Wrong versions

Implementations that look right but are wrong. Each one needs a test that catches it.

| # | Wrong version | What it would report | The test that catches it |
|---|---|---|---|
| 1 | Deduplicate postings using only the original job ID. | Both boards succeed and the run reports `finished`, but one distinct posting is skipped because its ID matches a posting on another board. | `test_same_job_id_on_different_boards_is_processed_separately`: return two distinct postings with job ID `123` from two different boards. Assert that both postings have separate rule verdicts and retain their original job IDs. Use the source, board, and job ID together for deduplication. |
| 2 | Save seen job IDs before the board completes its required processing. | The first run reports `finished` because another board succeeds. When the failed board recovers in the next run, the report misses a new posting that was prematurely marked as seen. | `test_failed_board_does_not_mark_new_posting_seen`: in run one, return a new posting, then fail required processing for that board while another board succeeds. Assert that the failed board’s prior state is unchanged. In run two, let the board succeed and return the same posting. Assert that it is reported and evaluated as new. |
| 3 | Read an empty job list, or a response with no `jobs` key, as zero postings. | That board looks `ok` with 0 new jobs, and if the other boards succeed the run reports `finished`, although nothing on that board was checked. | `test_empty_or_missing_jobs_list_is_a_validation_error`: a fake board returns `{"jobs": []}`, then `{}`. Assert the board ends `failed` with code `201`, then `202`, has no job count, and the run exit is not `finished`. |
| 4 | Give a failed board a job count of 0. | The summary shows `striqe: 0 jobs, 0 new`, a value the board never returned. | `test_failed_board_has_no_job_count`: a fake board returns 404. Assert its record has no job count (`null`), the summary shows code `101` and its reason instead of a number, and the board ends `failed`. |
| 5 (added 2026-11-09, D21) | Trust a well-formed Greenhouse list without comparing its length with the board's own `meta.total`. | A list missing postings ends `ok`; with the 86 new postings left out, the run reports `finished`, 0 new (Step 7 demo, `demo/finished_wrong/`). | `tests/test_meta_total.py`, committed failing before the patch (3c4aa5a): a list shorter or longer than `meta.total` ends `failed` with `203`, no job count, state unchanged, run not `finished`; no `meta.total` → `ok`. |
