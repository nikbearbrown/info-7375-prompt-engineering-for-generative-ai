# GATE — Job-Search Agent 2 (the loop, the tools, and the diff)

Written 2026-11-10, **before any JS2 code existed** (this file is the first JS2 commit, `JS2-1`).

**Who decided what.** On 2026-11-10 Claude Code offered example options for each heading in
chat. Saloni chose `1A fail=a, 2A, 3A, 4A, 5B`; the option wording under those headings is
Claude's text, chosen by Saloni. The three wrong versions (§6) and the failure sentence (§7)
are **Saloni's own words**, quoted exactly as she typed them. Section 8 lists the details
Claude had to add to make the choices implementable; those are not Saloni's decisions until she
confirms them in the sign-off.

Persona: the fictional Priya Nair from JS1 (`../js1-contract-and-watch/personas/`). JS2 does
not judge relevance; it watches several boards and reports what is new.

## 1. Boards (choice 1A, deliberate failure (a))

| # | System | Board | Expected |
|---|---|---|---|
| 1 | Greenhouse | `anthropic` (the JS1 board) | 200, jobs |
| 2 | Greenhouse | `figma` | 200, jobs |
| 3 | Ashby | `openai` | 200, jobs |
| 4 | Greenhouse | `anthropic-doesnotexist` | **deliberate failure**: a misspelled name, which should return 404 |

Two applicant-tracking systems, three real boards, one board that fails on purpose.

## 2. Budgets (choice 2A)

Per run: **at most 5 boards, 10 HTTP requests, 60 seconds in total, 10 seconds per request.**

Who may change them: only Saloni, by a dated entry in this file. The code reads them from one
config file (`config/run.json`), and a test fails if that file and this table disagree.

## 3. Repeat rule (choice 3A)

"The same action" is the same **method + host + path**. The loop skips the repeat, logs it as
`repeat_skipped`, and does not spend budget on it.

## 4. Error policy (choice 4A)

Retry **once**, only after a timeout or a 5xx server error. Never retry a 404 or bad data,
because those won't fix themselves. Then skip the board, record the error, and end the run as
`incomplete`, never `finished`. A retry is safe because a GET changes nothing on the server.

## 5. Permission policy (choice 5B)

- **Hosts:** `boards-api.greenhouse.io`, `api.ashbyhq.com`. https only, GET only.
- **Folders:** writes only under `js2-loop-tools-diff/out/`. Reads are allowed anywhere inside
  the project folder (`js2-loop-tools-diff/`).
- **Approval:** overwriting `out/state/seen_ids.json` (the saved list of jobs already seen)
  needs Saloni's approval, given as `--approve-state`. Without approval, the new state goes to a
  pending file (`out/state/seen_ids.pending.json`) instead.
- **Never:** apply, email, message, log in, send POST/PUT/DELETE, write outside `out/`, or
  follow a symlink out of `out/`.

## 6. Wrong versions the tests must catch (Saloni's words)

1. "If a board returns an empty job list unexpectedly, the agent treats it as a successful run
   with zero new jobs instead of flagging the response as suspicious."
2. "If one board fails or times out, the agent silently skips it and still reports the entire
   run as successfully completed."
3. "If two different boards return the same job ID, the agent treats them as duplicates instead
   of identifying jobs using both the board name and job ID."

## 7. What a failure looks like (Saloni's words)

"The agent has failed if it reports finished when any board has failed or returned a suspicious
response, if it calls a host outside the approved allow-list, if it writes outside the permitted
folders or overwrites saved job history without approval, or if it reports a job as new that has
already been seen on that same board."

## 8. Details Claude added to make §1–§7 implementable (pending Saloni's confirmation)

**Exits.** Every run ends with exactly one status, and a stop is not a success:

| Status | When | What it reports |
|---|---|---|
| `finished` | every planned board was fetched, parsed and non-empty, within budget | per board: count seen, count new; total new |
| `incomplete` | at least one board failed (404, 5xx or timeout after its one retry, bad data) or came back empty, and the budget was not hit | the same, plus each failed/suspicious board with its reason; failed boards report **no** counts (never 0) |
| `budget-exhausted` | the next request would pass 10 requests or 60 seconds, or more than 5 boards were planned | what was done before the stop, and which boards were never tried |
| `error` | the loop itself could not run: a config that disagrees with this file, a request the policy refused, a state file that cannot be read | the reason; nothing is reported as new |

If several apply, the most serious wins: `error` > `budget-exhausted` > `incomplete` > `finished`.

**"Empty unexpectedly"** (wrong version 1). Any board that returns a valid response with zero
jobs is marked `suspicious_empty` and makes the run `incomplete`. Its state is not touched. A board
that is truly empty would have to be listed by Saloni as expected-empty in this file; none is.

**Job identity** (wrong version 3). A job's key is `system:board:id`, for example
`greenhouse:anthropic:4012345`. "New" means the key is not in the saved state.

**Failed boards keep their history.** A failed or suspicious board never adds or removes keys
from state.

**A retry is not a repeat.** The one retry allowed by §4 is the error policy, not a repeated
action; it does count against the request budget.

**Timeout.** "10 seconds per request" is the socket timeout passed to `urllib`; the 60-second
budget is checked before every request.

**Raw responses** are saved byte-for-byte (gzip-compressed, with the SHA-256 of the uncompressed
bytes) before they are parsed, so a TA can re-parse them.
