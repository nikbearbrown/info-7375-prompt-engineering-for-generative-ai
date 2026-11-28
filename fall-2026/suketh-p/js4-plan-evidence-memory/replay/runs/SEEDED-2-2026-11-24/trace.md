# Trace of replay `SEEDED-2-2026-11-24` (SEEDED): **finished**

The request rows are the original capture's, read from its saved bodies; nothing was fetched.

| # | At | Event | Board | HTTP | Bytes | Outcome | Jobs | Raw file |
|---:|---|---|---|---:|---:|---|---:|---|
| 1 | 2026-11-24T22:36:19Z | request | greenhouse/anthropic | 200 | 9545028 | usable | 631 | ../../../runs/2026-11-24-js3-corpus/raw/greenhouse-anthropic.body.gz |
| 2 | 2026-11-24T22:36:20Z | request | greenhouse/databricks | 200 | 9748826 | usable | 890 | ../../../runs/2026-11-24-js3-corpus/raw/greenhouse-databricks.body.gz |
| 3 | 2026-11-24T22:36:24Z | request | ashby/linear | 200 | 418959 | usable | 30 | ../../../runs/2026-11-24-js3-corpus/raw/ashby-linear.body.gz |

| Step | At | What happened |
|---|---|---|
| preflight | 2026-11-28T13:50:21Z | state replay/state/state.json at revision 1 (sha256 3539364075cf…); approval: given |
| verify | 2026-11-28T13:50:21Z | greenhouse/anthropic: usable, 631 jobs; greenhouse/databricks: usable, 890 jobs; ashby/linear: usable, 30 jobs |
| watcher anthropic | 2026-11-28T13:50:21Z | 93 note(s) on greenhouse/anthropic |
| watcher databricks | 2026-11-28T13:50:21Z | 99 note(s) on greenhouse/databricks |
| coordinator | 2026-11-28T13:50:21Z | notes.json written: anthropic 93, databricks 99 |
| stage | 2026-11-28T13:50:21Z | proposal and diff staged: {'listed': 1551, 'first seen': 193, 'missing from the list': 271} |
| checks | 2026-11-28T13:50:22Z | passed |
| publish | 2026-11-28T13:50:22Z | revision 1 → 2 (sha256 dc40d7b9d7bf…) |
| exit | 2026-11-28T13:50:22Z | finished: every board was usable, both watchers' notes merged, the checks passed and revision 2 was committed |
