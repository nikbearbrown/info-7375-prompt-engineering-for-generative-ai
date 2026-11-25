# SEEDED second run

Seeded second run (2026-10-31): replayed the saved baseline response
with 3 ids removed from the seen file, because a second calendar day
was not available before the deadline.

**This is not a real second-day run.** No new fetch was made; the agent
re-read the same Greenhouse response it saved at the baseline.

## What was done
- Seen file: `state/seen_ids.json` (156 ids, from the 2026-10-31 baseline)
  copied to `seeded_run/state/seen_ids_before_run.json` with 3 ids removed:
  7855793003, 7855798003, 8041054003 (153 ids).
- Command (Claude ON, run 2026-10-31 23:05 EDT):

  ```bash
  python3 -m agent.main --replay raw/klaviyo_20261031T175121.json \
    --state seeded_run/state/seen_ids.json --out seeded_run --label SEEDED
  ```
- The real `state/` and `results/` were not changed.

## Result
The agent reported exactly the 3 removed ids as new (156 postings, 3 new).

| id | title | rule (`record`) | Claude (`judgment`) |
|---|---|---|---|
| 8041054003 | Software Engineer, Conversational Products & Agent Workflows | relevant | relevant |
| 7855798003 | Software Engineer II - Recommendations | relevant | no Claude verdict (reply wrapped in a ```json fence; verdict inside was `relevant`) |
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | relevant | relevant |

The agent uses `prompts/baseline.txt`, so the fenced reply is the same
failure seen in the prompt experiment.

## Files
- `run_output.txt` — screen output of the run
- `results/2026-10-31.json` — run record (`"label": "SEEDED"`, `"replay": true`)
- `claude_responses/` — the 3 raw Claude replies
- `state/seen_ids_before_run.json` — seeded seen file before the run (153 ids)
- `state/seen_ids.json` — seen file after the run (156 ids)
