# Filter run: FILTER.md v1.0

- FILTER.md sha256: `5a01ab6e39a22f9688c751b9f91aa5f5df7cdab5f4fba90c82d0914c7167ba6f`
- Corpus: 1176 unique postings from 3 live snapshots (2026-10-31T191245-live, 2026-11-07T184247-live, 2026-11-20T213031-live); latest version of each posting used
- Run at: 2026-11-22T14:10:56-05:00

| board | kept | rejected | cannot tell | total |
|---|---:|---:|---:|---:|
| anthropic | 150 | 665 | 0 | 815 |
| notion | 16 | 177 | 0 | 193 |
| perplexity | 28 | 140 | 0 | 168 |
| **all** | **194** | **982** | **0** | **1176** |

**Which rule decided:**

| decision | rule | postings |
|---|---|---:|
| kept | R10 | 194 |
| rejected | R10 | 118 |
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

Kept postings still listed in the latest snapshot (2026-11-20T213031-live): 159.
