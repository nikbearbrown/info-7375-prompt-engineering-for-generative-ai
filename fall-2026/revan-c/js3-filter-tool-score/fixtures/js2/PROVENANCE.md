# Seeded fixtures for Job-Search Agent 2

These files are **seeded**, not live board responses. Any run that reads one is labeled `seeded`.

| File | What it is | Made by | Date |
|---|---|---|---|
| `klaviyo_empty_seeded.json` | A Greenhouse-shaped board with zero postings: `{"jobs": [], "meta": {"total": 0}}`. Written by hand, not fetched. It stands in for a board that answers HTTP 200 with an empty list. | Claude Code, at Revan's direction | 2026-11-10 |

Why it exists: it drives the finished-wrong-answer demonstration (README, "Finished-wrong demonstration").
JS1 reads it as "0 new" and exits 0; JS2 reads the same bytes as a failed board and ends `incomplete`.

Is the empty board realistic? On 2026-11-09 Claude Code probed Webflow's Greenhouse board (`boards-api.greenhouse.io/v1/boards/webflow/jobs`)
and got HTTP 200 with `{"jobs": [], ...}`, while Webflow's Ashby board listed 21 postings. That probe's response was not saved,
so it is a note, not evidence; Webflow is not on GATE.md's allow-list and JS2 never fetches it.
