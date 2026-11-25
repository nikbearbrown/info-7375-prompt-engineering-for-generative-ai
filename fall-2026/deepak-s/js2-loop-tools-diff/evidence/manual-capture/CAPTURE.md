# CAPTURE.md: manual curl capture, 2026-11-10

Live capture, not SEEDED. Run by Claude Code (Claude Opus 5.5) in Deepak's session on 2026-11-10, 13:40 ET (18:40 UTC), before any JS2 code existed.

- Folder: `evidence/manual-capture/20261110T184001Z/`
- Method: `curl -sS --proto '=https' --max-redirs 0 --max-time 20 -X GET -D <name>.headers.txt -o <name>.body`, one GET per URL, 2 s apart, in the order below.
- Per-request log: `20261110T184001Z/curl_log.tsv` (start time, HTTP code, content-type, bytes, curl exit code).
- sha256 of every body and header file: `20261110T184001Z/SHA256SUMS`.
- Posting count: the length of the top-level JSON list (Lever) or of the `jobs` list (Greenhouse, Ashby). "n/a" means the body has no posting list.

| # | URL | HTTP status | content-type | bytes | posting count | sha256 (body) |
|---|---|---|---|---|---|---|
| 01 | https://boards-api.greenhouse.io/v1/boards/stripe/jobs | 200 | application/json | 484146 | 776 | b5b6d1879bc697d25701cb8fd828bd377107db0c79df564cdef7067764b15599 |
| 02 | https://boards-api.greenhouse.io/v1/boards/stripe-js2-nonexistent/jobs | 404 | application/json | 38 | n/a (body `{"status":404,"error":"Job not found"}`) | 76fe0d64c21edde1aa258ae01c07a04323d95ab31b21822348d9e3f1f400dffe |
| 03 | https://api.lever.co/v0/postings/lever?mode=json | 200 | application/json; charset=utf-8 | 2 | 0 (body `[]`) | 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945 |
| 04 | https://api.eu.lever.co/v0/postings/lever?mode=json | 200 | application/json; charset=utf-8 | 111100 | 6 | 5179dcd2ca0165aeabc34f43670a1403874c19448e09d70fd7d281a6de3a4b92 |
| 05 | https://api.lever.co/v0/postings/palantir?mode=json | 200 | application/json; charset=utf-8 | 5931064 | 304 | ca64b60df940ace0c1da750bc9cc275ec8a358410a02c051cfb3eda0dcfacc7d |
| 06 | https://api.ashbyhq.com/posting-api/job-board/linear | 200 | application/json; charset=utf-8 | 467923 | 33 | ac2e34215a8b41df85b357494c444e8df2505cc8d762cfd6951d7f9bd2e3d35a |
| 07 | https://api.ashbyhq.com/posting-api/job-board/notion | 200 | application/json; charset=utf-8 | 2795337 | 152 | f503bb8ff021d653b81a05c3eee7db054c95d11edfa2bb539afecb51e7e97f1c |

Facts from the saved headers, no interpretation:
- No response was a 3xx. All seven curl exit codes were 0 (`curl_log.tsv`).
- Rows 03 and 04 are the same board token, `lever`, on two hosts: the US host returned `[]`, the EU host returned 6 postings.
- Rows 06 and 07 carried `cf-cache-status: HIT` with `age: 48` and `age: 57` (`06-ashby-linear.headers.txt`, `07-ashby-notion.headers.txt`).
- Row 02's 404 body is JSON with content-type application/json (`02-greenhouse-stripe-js2-nonexistent.headers.txt`).
