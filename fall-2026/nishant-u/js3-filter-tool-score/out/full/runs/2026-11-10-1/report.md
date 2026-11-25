# Run 2026-11-10-1

- Exit (controller status): **incomplete**
- Mode: live; profile: full; started (UTC): 2026-11-10T17:42:49+00:00
- Used: 5/10 requests, 5/5 boards, 0.782/60 s
- `finished` only means every planned board returned a parsed response within budget. It is not the outcome check: run `python -m agent2.check out/runs/2026-11-10-1`.

## Boards

- `greenhouse:faire` — parsed, HTTP 200, 68 postings, baseline (ids saved; none reported as new)
- `greenhouse:instacart` — parsed, HTTP 200, 88 postings, baseline (ids saved; none reported as new)
- `ashby:poshmark` — parsed, HTTP 200, 22 postings, baseline (ids saved; none reported as new)
- `greenhouse:poshmark` — parsed, HTTP 200, 0 postings, baseline (ids saved; none reported as new)
- `greenhouse:no-such-board-js2-test` — failed: not-found, HTTP 404. New postings: unknown (no value invented). Escalated to me.

## New postings, rule verdicts [record]

None.

## Claude judge [judgment]

Status: not requested.

## Trace

| step | action | board | HTTP | bytes | decision | requests | seconds |
|---:|---|---|---:|---:|---|---:|---:|
| 1 | fetch | greenhouse:faire | 200 | 877374 | parsed: 68 postings | 1 | 0.219 |
| 2 | fetch | greenhouse:instacart | 200 | 1055852 | parsed: 88 postings | 2 | 0.454 |
| 3 | fetch | ashby:poshmark | 200 | 275869 | parsed: 22 postings | 3 | 0.594 |
| 4 | fetch | greenhouse:poshmark | 200 | 30 | parsed: 0 postings | 4 | 0.688 |
| 5 | fetch | greenhouse:no-such-board-js2-test | 404 | 38 | failed: not-found (HTTP 404, no retry); escalated | 5 | 0.782 |
