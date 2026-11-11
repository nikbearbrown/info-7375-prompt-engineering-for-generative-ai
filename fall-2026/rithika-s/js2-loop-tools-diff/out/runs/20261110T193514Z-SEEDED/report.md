# Job-search run 20261110T193514Z-SEEDED (SEEDED)

**SEEDED**: responses were replayed from `out/runs/20261110T183029Z`. No network request was made. State used: `out/state/seeded`.

## Needs your attention

Nothing needs your attention.

## Result

- Exit: **finished** (code 0)
- Boards file: `config/boards_demo_3.json`
- This is the agent's own report, not an independent check. Independent check: `python3 -m checks.independent_check out/runs/20261110T193514Z-SEEDED`
- Succeeded: scaleai, databricks, openai
- Failed: none
- Never tried: none

## Boards

| board | ATS | status | HTTP | attempts | postings seen | duplicates | new |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scaleai | greenhouse | ok | 200 | 1 | 169 | 0 | 0 (baseline) |
| databricks | greenhouse | ok | 200 | 1 | 915 | 0 | 0 (baseline) |
| openai | ashby | ok | 200 | 1 | 830 | 0 | 0 (baseline) |

## New postings

- scaleai: baseline run; every current id was recorded and none is reported as new.
- databricks: baseline run; every current id was recorded and none is reported as new.
- openai: baseline run; every current id was recorded and none is reported as new.
- No new postings on any board that succeeded.

## Budget use

- Requests: 3 of 8
- Boards started: 3 of 4
- Elapsed: 0.077 s of 90 s (per request: 20 s)
- Claude calls: 0 of 0

## Notes

- A 200 with zero postings is accepted as a valid empty board (known limit, GATE.md section 4).
