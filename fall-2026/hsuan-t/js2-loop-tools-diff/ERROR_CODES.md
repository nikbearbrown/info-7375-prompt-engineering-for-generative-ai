# Error codes

What each code in a run's summary, `verdicts.json` and `trace.jsonl` means (GATE §1, JS2 D17).
The program reads the same table from `job_agent/loop/codes.py`; `tests/test_loop.py` fails if
this file and that table ever differ.

- **First digit = the stage** where the failure happened: `0` inputs, `1` fetch, `2` validate, `3` judge (Claude, only with `--claude`), `4` output.
- **Retry**: GATE §3-§4. A retryable failure is tried again once; if it fails with a different retryable code, one final time. At most 3 attempts per board, all inside the request budget. Claude calls are never retried.
- **Scope**: `board` = only that board fails and the loop goes on; `posting` = only that posting's Claude verdict is an error, its rule verdict stands; `run` = the whole run stops with exit `error`.
- The HTTP status, when there is one, is kept separately in the trace (`http`).
- `304` also makes the run's exit `budget-exhausted`: a new posting Claude never saw is scheduled work a budget kept from finishing (GATE §1-§2, D20).

| Code | Stage | Meaning | Retry | Scope |
|---|---|---|---|---|
| `001` | inputs | a required input file is missing | no | run |
| `002` | inputs | an input file is invalid | no | run |
| `003` | inputs | the board's state file is broken | no | board |
| `004` | inputs | an input or output was refused by the permission policy | no | run |
| `101` | fetch | board not found (HTTP 404) | no | board |
| `102` | fetch | the request timed out | yes | board |
| `103` | fetch | could not connect | yes | board |
| `104` | fetch | the board had a temporary failure (HTTP 5xx or 429) | yes | board |
| `105` | fetch | the request was refused by the permission policy | no | board |
| `106` | fetch | the board refused the request (HTTP 4xx other than 404 and 429) | no | board |
| `201` | validate | the board returned an empty job list | no | board |
| `202` | validate | the board response has the wrong shape | no | board |
| `203` | validate | the job list's length differs from the board's own total (meta.total) | no | board |
| `301` | judge | the Claude call timed out | no | posting |
| `302` | judge | the Claude judge could not run (no CLI or key, API error, empty job description) | no | posting |
| `303` | judge | Claude's reply was rejected (validator, refusal, or cut off) | no | posting |
| `304` | judge | the posting was not sent to Claude: the Claude budget (30 calls or 300 s) was used up | no | posting |
| `401` | output | the run record could not be written | no | run |
