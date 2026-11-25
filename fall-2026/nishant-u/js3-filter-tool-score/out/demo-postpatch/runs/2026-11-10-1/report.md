# Run 2026-11-10-1

- Exit (controller status): **incomplete**
- Mode: live; profile: demo; started (UTC): 2026-11-10T18:02:42+00:00
- Used: 4/10 requests, 4/5 boards, 0.719/60 s
- `finished` only means every planned board returned a parsed response within budget. It is not the outcome check: run `python -m agent2.check out/runs/2026-11-10-1`.

## Boards

- `greenhouse:faire` — parsed, HTTP 200, 68 postings, baseline (ids saved; none reported as new)
- `greenhouse:instacart` — parsed, HTTP 200, 92 postings, baseline (ids saved; none reported as new)
- `ashby:poshmark` — parsed, HTTP 200, 22 postings, baseline (ids saved; none reported as new)
- `greenhouse:poshmark` — unverified-empty: HTTP 200 with an empty jobs list. Not a clean result; new postings: unknown, ids not saved. Escalated to me.

## New postings, rule verdicts [record]

None.

## Claude judge [judgment]

Status: not requested.

## Trace

| step | action | board | HTTP | bytes | decision | requests | seconds |
|---:|---|---|---:|---:|---|---:|---:|
| 1 | fetch | greenhouse:faire | 200 | 877374 | parsed: 68 postings | 1 | 0.219 |
| 2 | fetch | greenhouse:instacart | 200 | 1103124 | parsed: 92 postings | 2 | 0.469 |
| 3 | fetch | ashby:poshmark | 200 | 275869 | parsed: 22 postings | 3 | 0.625 |
| 4 | fetch | greenhouse:poshmark | 200 | 30 | unverified-empty: HTTP 200 with 0 postings (not a clean result); escalated | 4 | 0.719 |
