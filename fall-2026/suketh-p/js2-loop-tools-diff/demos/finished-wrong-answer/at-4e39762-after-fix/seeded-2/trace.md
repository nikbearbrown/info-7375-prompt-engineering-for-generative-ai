# Trace of run `seeded-2`: **incomplete**

Every event the loop recorded, in order. Times are UTC; `elapsed_s` is measured by the run's clock.

| # | At | Event | Board | HTTP | Elapsed s | Bytes | Outcome | Jobs | Raw file | Reason |
|---:|---|---|---|---:|---:|---:|---|---:|---|---|
| 1 | 2026-11-09T05:41:05Z | request | greenhouse/anthropic | 200 | 0.0 | 10279433 | usable | 675 | raw/greenhouse-anthropic.body.gz | — |
| 2 | 2026-11-09T05:41:05Z | request | greenhouse/databricks | 200 | 0.0 | 10058900 | usable | 922 | raw/greenhouse-databricks.body.gz | — |
| 3 | 2026-11-09T05:41:05Z | request | ashby/linear | 200 | 0.0 | 31 | unverified | — | raw/ashby-linear.body.gz | empty jobs list: the board answered 200 with no postings, so it could not be verified |
| 4 | 2026-11-09T05:41:05Z | exit | — | — | — | — | incomplete | — | — | not every board could be verified: ['ashby/linear']; results are provisional |
