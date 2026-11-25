# Trace of run `2026-11-08-failure-1`: **incomplete**

Every event the loop recorded, in order. Times are UTC; `elapsed_s` is measured by the run's clock.

| # | At | Event | Board | HTTP | Elapsed s | Bytes | Outcome | Jobs | Raw file | Reason |
|---:|---|---|---|---:|---:|---:|---|---:|---|---|
| 1 | 2026-11-08T10:45:43Z | request | greenhouse/anthropic | 200 | 0.643 | 10279433 | usable | 675 | raw/greenhouse-anthropic.body.gz | — |
| 2 | 2026-11-08T10:45:44Z | request | greenhouse/databricks | 200 | 0.851 | 10058900 | usable | 922 | raw/greenhouse-databricks.body.gz | — |
| 3 | 2026-11-08T10:45:45Z | request | ashby/linear | 200 | 0.229 | 452742 | usable | 32 | raw/ashby-linear.body.gz | — |
| 4 | 2026-11-08T10:45:45Z | request | greenhouse/jobwatch-no-such-board-js2 | 404 | 0.12 | 38 | failed-as-expected | — | raw/greenhouse-jobwatch-no-such-board-js2.body.gz | HTTP 404, as expected for the failure control |
| 5 | 2026-11-08T10:45:45Z | exit | — | incomplete | — | — | — | — | — | not every board could be verified: ['greenhouse/jobwatch-no-such-board-js2']; results are provisional |
