# evidence/claude

CONSTRUCTED: every file dated 2026-10-30T00-43-34Z, 2026-10-30T00-46-34Z and 2026-10-30T01-09-16Z (UTC) in this folder comes from the smoke test on posting 8000002, a CONSTRUCTED posting from `tests/fixtures/constructed_postings.json`, not a real Databricks posting.

- **00-43-34Z:** failed twice with "Not logged in · Please run /login".
- **00-46-34Z:** valid, and ran before the model was pinned, so its result does not record a model.
- **01-09-16Z:** valid, and ran after pinning; its result records `"model": "claude-sonnet-4-6"`.

## Usage-limit failures, 2026-10-31

CONSTRUCTED: every file dated 2026-10-31T01-36-35Z and 2026-10-31T01-46-19Z (UTC) in this folder comes from the same smoke-test command on posting 8000002, the CONSTRUCTED posting, not a real Databricks posting. Both runs failed on both attempts, with exit code 1 and "You've hit your limit · resets 8pm (America/New_York)" on stdout. Result: `"status": "invalid"`.

- **01-36-35Z:** run by me in Terminal.
- **01-46-19Z:** run by Claude Code at my request, to confirm the message.
