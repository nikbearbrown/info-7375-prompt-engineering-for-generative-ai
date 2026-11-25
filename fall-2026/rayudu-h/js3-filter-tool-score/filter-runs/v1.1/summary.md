# Filter run: FILTER.md v1.1

- FILTER.md sha256: `db915c94f4cb23e02cf74384de015e3371214183d7b9f07c06fe51bf7603c826`
- Corpus: 1176 unique postings from 3 live snapshots (2026-10-31T191245-live, 2026-11-07T184247-live, 2026-11-20T213031-live); latest version of each posting used
- Run at: 2026-11-24T22:49:24-05:00

| board | kept | rejected | cannot tell | total |
|---|---:|---:|---:|---:|
| anthropic | 150 | 665 | 0 | 815 |
| notion | 16 | 177 | 0 | 193 |
| perplexity | 46 | 122 | 0 | 168 |
| **all** | **212** | **964** | **0** | **1176** |

**Which rule decided:**

| decision | rule | postings |
|---|---|---:|
| kept | R10 | 212 |
| rejected | R10 | 100 |
| rejected | R2 | 507 |
| rejected | R3 | 8 |
| rejected | R8 | 349 |

**Boards with no result** (FILTER.md section 4: "no result", never "nothing relevant"):

- 2026-10-31T191245-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-10-31T191245-live: `ashby:openai`: no result (timeout: timed out (transient; retried once))
- 2026-11-07T184247-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-11-07T184247-live: `ashby:openai`: no result (timeout: timed out (transient; retried once))
- 2026-11-20T213031-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-11-20T213031-live: `ashby:openai`: no result (TimeoutError: timed out (transient; retried once))

Kept postings still listed in the latest snapshot (2026-11-20T213031-live): 176.
