# Run `2026-11-08-failure-2`: **incomplete**

not every board could be verified: ['greenhouse/jobwatch-no-such-board-js2']; results are provisional

- Started 2026-11-08T11:19:32Z, ended 2026-11-08T11:19:34Z (UTC).
- Used 4/4 boards, 4/4 requests, 2.045 s of 30 s (each request at most 5 s).
- State advanced: **no**. Every count below is provisional: the next finished run decides.
- Approval given: none
- Approval problem: no approval was given for this run

| Board | Role | Outcome | Jobs | Baseline | New | Reason |
|---|---|---|---:|---|---:|---|
| greenhouse/anthropic | normal | usable | 675 | False | 0 | — |
| greenhouse/databricks | normal | usable | 922 | False | 0 | — |
| ashby/linear | normal | usable | 32 | False | 0 | — |
| greenhouse/jobwatch-no-such-board-js2 | failure-control | failed-as-expected | — | — | — | HTTP 404, as expected for the failure control |
