# Trace of replay `SEEDED-1-2026-11-08` (SEEDED): **finished**

The request rows are the original capture's, read from its saved bodies; nothing was fetched.

| # | At | Event | Board | HTTP | Bytes | Outcome | Jobs | Raw file |
|---:|---|---|---|---:|---:|---|---:|---|
| 1 | 2026-11-08T11:17:26Z | request | greenhouse/anthropic | 200 | 10279433 | usable | 675 | ../../../runs/2026-11-08-normal-1/raw/greenhouse-anthropic.body.gz |
| 2 | 2026-11-08T11:17:27Z | request | greenhouse/databricks | 200 | 10058900 | usable | 922 | ../../../runs/2026-11-08-normal-1/raw/greenhouse-databricks.body.gz |
| 3 | 2026-11-08T11:17:28Z | request | ashby/linear | 200 | 452742 | usable | 32 | ../../../runs/2026-11-08-normal-1/raw/ashby-linear.body.gz |

| Step | At | What happened |
|---|---|---|
| preflight | 2026-11-28T13:44:17Z | state replay/state/state.json at revision 0 (sha256 f046969f9ae5…); approval: given |
| verify | 2026-11-28T13:44:17Z | greenhouse/anthropic: usable, 675 jobs; greenhouse/databricks: usable, 922 jobs; ashby/linear: usable, 32 jobs |
| watcher anthropic | 2026-11-28T13:44:17Z | 0 note(s) on greenhouse/anthropic |
| watcher databricks | 2026-11-28T13:44:17Z | 0 note(s) on greenhouse/databricks |
| coordinator | 2026-11-28T13:44:17Z | notes.json written: anthropic 0, databricks 0 |
| stage | 2026-11-28T13:44:17Z | proposal and diff staged: {'first seen': 1629, 'listed': 1629} |
| checks | 2026-11-28T13:44:18Z | passed |
| publish | 2026-11-28T13:44:18Z | revision 0 → 1 (sha256 3539364075cf…) |
| exit | 2026-11-28T13:44:18Z | finished: every board was usable, both watchers' notes merged, the checks passed and revision 1 was committed |
