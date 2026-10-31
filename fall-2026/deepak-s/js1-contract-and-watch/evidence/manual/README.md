# Manual capture (by me, not the agent)
- File: stripe_20261030T000804Z.raw
- Taken: 2026-10-30 00:08:04 UTC (2026-10-29 20:08 ET), by hand with curl, before any agent code existed
- Command: curl -sS -o <file> "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
- sha256: 233c93bf7ede2c579b068e32f69da66ab7b9278707c6220b27fb4f842a7c4061
- Purpose: input for a run labelled seeded (--from-file), if the live baseline can't run the same day
