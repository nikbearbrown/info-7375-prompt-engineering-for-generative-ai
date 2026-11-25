# Job-search run 20261110T183029Z (LIVE)

## Needs your attention

- **rithika-js2-no-such-board** failed: `http_404` (HTTP 404). New jobs: **unknown**. State file not updated. Raw: `out/raw/20261110T183029Z_rithika-js2-no-such-board_a1.json`

## Result

- Exit: **incomplete** (code 1)
- This is the agent's own report, not an independent check. Independent check: `python3 -m checks.independent_check out/runs/20261110T183029Z`
- Succeeded: scaleai, databricks, openai
- Failed: rithika-js2-no-such-board
- Never tried: none

## Boards

| board | ATS | status | HTTP | attempts | postings seen | duplicates | new |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scaleai | greenhouse | ok | 200 | 1 | 169 | 0 | 0 (baseline) |
| databricks | greenhouse | ok | 200 | 1 | 915 | 0 | 0 (baseline) |
| openai | ashby | ok | 200 | 1 | 830 | 0 | 0 (baseline) |
| rithika-js2-no-such-board | greenhouse | failed | 404 | 1 | unknown | 0 | unknown |

## New postings

- scaleai: baseline run; every current id was recorded and none is reported as new.
- databricks: baseline run; every current id was recorded and none is reported as new.
- openai: baseline run; every current id was recorded and none is reported as new.
- No new postings on any board that succeeded.

## Budget use

- Requests: 4 of 8
- Boards started: 4 of 4
- Elapsed: 2.603 s of 90 s (per request: 20 s)
- Claude calls: 0 of 0

## Notes

- A 200 with zero postings is accepted as a valid empty board (known limit, GATE.md section 4).
