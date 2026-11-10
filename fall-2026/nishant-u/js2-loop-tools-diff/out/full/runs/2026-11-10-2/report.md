# Run 2026-11-10-2

- Exit (controller status): **incomplete**
- Mode: live; profile: full; started (UTC): 2026-11-10T18:08:03+00:00
- Used: 5/10 requests, 5/5 boards, 0.766/60 s
- `finished` only means every planned board returned a parsed response within budget. It is not the outcome check: run `python -m agent2.check out/runs/2026-11-10-2`.

## Boards

- `greenhouse:faire` — parsed, HTTP 200, 68 postings, 0 new
- `greenhouse:instacart` — parsed, HTTP 200, 92 postings, 4 new
- `ashby:poshmark` — parsed, HTTP 200, 22 postings, 0 new
- `greenhouse:poshmark` — unverified-empty: HTTP 200 with an empty jobs list. Not a clean result; new postings: unknown, ids not saved. Escalated to me.
- `greenhouse:no-such-board-js2-test` — failed: not-found, HTTP 404. New postings: unknown (no value invented). Escalated to me.

## New postings, rule verdicts [record]

- **greenhouse:instacart:8373034** Senior Product Manager, Instacart Business - Growth: `not_relevant` [record]. R1 failed: title 'Senior Product Manager, Instacart Business - Growth' contains none of the title terms.
- **greenhouse:instacart:8373036** Senior Product Manager, Instacart Business - Growth: `not_relevant` [record]. R1 failed: title 'Senior Product Manager, Instacart Business - Growth' contains none of the title terms.
- **greenhouse:instacart:8372848** Staff Software Engineer, Ads Data Platform: `not_relevant` [record]. R3 failed: no part of location.name 'Canada - Remote (ON, AB, BC, or NS Only)' is a US location.
- **greenhouse:instacart:8372846** Staff Software Engineer, Ads Data Platform: `not_relevant` [record]. R3 failed: no part of location.name 'United States - Remote' is a US location.

## Claude judge [judgment]

Status: not requested.

## Trace

| step | action | board | HTTP | bytes | decision | requests | seconds |
|---:|---|---|---:|---:|---|---:|---:|
| 1 | fetch | greenhouse:faire | 200 | 877374 | parsed: 68 postings | 1 | 0.235 |
| 2 | fetch | greenhouse:instacart | 200 | 1103124 | parsed: 92 postings | 2 | 0.453 |
| 3 | fetch | ashby:poshmark | 200 | 275869 | parsed: 22 postings | 3 | 0.594 |
| 4 | fetch | greenhouse:poshmark | 200 | 30 | unverified-empty: HTTP 200 with 0 postings (not a clean result); escalated | 4 | 0.688 |
| 5 | fetch | greenhouse:no-such-board-js2-test | 404 | 38 | failed: not-found (HTTP 404, no retry); escalated | 5 | 0.766 |
