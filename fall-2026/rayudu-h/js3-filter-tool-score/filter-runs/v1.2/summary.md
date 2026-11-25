# Filter run: FILTER.md v1.2

- FILTER.md sha256: `29524bf5cd11f7556f12cdb530348f5028ebec5c325989c9e42aac5cf7e39653`
- Corpus: 1176 unique postings from 3 live snapshots (2026-10-31T191245-live, 2026-11-07T184247-live, 2026-11-20T213031-live); latest version of each posting used
- Run at: 2026-11-24T23:19:49-05:00

| board | kept | rejected | cannot tell | total |
|---|---:|---:|---:|---:|
| anthropic | 65 | 750 | 0 | 815 |
| notion | 9 | 184 | 0 | 193 |
| perplexity | 31 | 137 | 0 | 168 |
| **all** | **105** | **1071** | **0** | **1176** |

**Which rule decided:**

| decision | rule | postings |
|---|---|---:|
| kept | R10 | 105 |
| rejected | R10 | 55 |
| rejected | R17 | 317 |
| rejected | R2 | 507 |
| rejected | R3 | 8 |
| rejected | R8 | 184 |

**Boards with no result** (FILTER.md section 4: "no result", never "nothing relevant"):

- 2026-10-31T191245-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-10-31T191245-live: `ashby:openai`: no result (timeout: timed out (transient; retried once))
- 2026-11-07T184247-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-11-07T184247-live: `ashby:openai`: no result (timeout: timed out (transient; retried once))
- 2026-11-20T213031-live: `ashby:notion-does-not-exist-js2`: no result (HTTP 404 (permanent; not retried))
- 2026-11-20T213031-live: `ashby:openai`: no result (TimeoutError: timed out (transient; retried once))

Kept postings still listed in the latest snapshot (2026-11-20T213031-live): 85.
