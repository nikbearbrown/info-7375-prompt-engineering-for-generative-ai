# Job-search run 20261110T200439Z-SEEDED (SEEDED)

**SEEDED**: responses were replayed from `data/seeded_demo/day2`. No network request was made. State used: `out/state/seeded`.

## Needs your attention

- **scaleai** failed: `empty_after_nonempty` (HTTP 200). New jobs: **unknown**. State file not updated. Raw: `out/raw/20261110T200439Z-SEEDED_scaleai_a1.json`

## Result

- Exit: **incomplete** (code 1)
- Boards file: `config/boards_demo_3.json`
- This is the agent's own report, not an independent check. Independent check: `python3 -m checks.independent_check out/runs/20261110T200439Z-SEEDED`
- Succeeded: databricks, openai
- Failed: scaleai
- Never tried: none

## Boards

| board | ATS | status | HTTP | attempts | postings seen | duplicates | new |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scaleai | greenhouse | failed | 200 | 1 | unknown | 0 | unknown |
| databricks | greenhouse | ok | 200 | 1 | 915 | 0 | 0 |
| openai | ashby | ok | 200 | 1 | 830 | 0 | 0 |

## New postings

- No new postings on any board that succeeded.

## Budget use

- Requests: 3 of 8
- Boards started: 3 of 4
- Elapsed: 0.062 s of 90 s (per request: 20 s)
- Claude calls: 0 of 0

## Notes

- A 200 with zero postings fails the board (`empty_after_nonempty`) if its saved state had postings; with no saved state, or an empty one, it is a valid empty board (GATE.md error-policy log, 2026-11-10).
