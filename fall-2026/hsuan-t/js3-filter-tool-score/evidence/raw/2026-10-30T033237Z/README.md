# Raw snapshot — Stripe Greenhouse board, 2026-10-29 23:32 EDT (2026-10-30 03:32 UTC)

Why this exists: the brief needs two runs with a real change between them (R14). This snapshot was
captured the evening before the agent code existed, so tomorrow's live fetch is a second calendar day.
It is evidence (R10), not agent output — it was fetched by a one-off `curl` run by Claude, not by the agent.

Order, for the record: CONTRACT.md already had a "What a failure looks like" section (file mtime
2026-10-29T23:31:21-0400) before this fetch ran. The rest of CONTRACT.md was still being written.

| File | URL | HTTP | Bytes | Jobs | sha256 |
|---|---|---|---|---|---|
| `stripe_list.json` | `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | 200 | 460062 | 737 | `ebc2e63bfd0e352a4cf323e32f95174e8851c8f23b21e8a61ee6ae2c0068b34e` |
| `stripe_content.json` | `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | 200 | 5732019 | 737 | `1b40ec8190bb662b4acf35c6c41e417aa6d08258dc04624135fd93d316523a08` |

`*.headers.txt` = the HTTP response headers for each request.
Both files have the same 737 posting ids; `first_published` ranges 2023-11-01 .. 2026-10-29.

Command (run from `job-search-agent/`):

```bash
U="https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
curl -s -m 120 -D stripe_list.headers.txt    -o stripe_list.json    "$U"
curl -s -m 120 -D stripe_content.headers.txt -o stripe_content.json "$U?content=true"
```
