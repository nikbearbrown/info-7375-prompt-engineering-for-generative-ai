# Day-1 baseline (2026-10-31), carried over from Job-Search Agent 1

These two files are copied unchanged from my JS1 folder. They are the "earlier day" that today's Samsara run is compared against.
Do not edit them. The JS2 loop reads them and never writes them.

| File | Copied from (JS1) | sha256 |
|---|---|---|
| `seen_ids.json` | `state/seen_ids.json` | `c8edc7a6b6012b2afc97825e75d0a64f357fbfd2a6897053fbc44349c700db24` |
| `samsara.json` | `evidence/raw/2026-10-31T212433_live_2/boards/samsara.json` | `1c2a5dc3ca5c16e6aef1c3f4b6916c6f02cb5f490cdb26b263cace006b70f853` |

- **What they are:** `samsara.json` is the raw live response from `boards-api.greenhouse.io` for Samsara's board, fetched 2026-10-31 21:24:33 ET
  (JS1 Run 2). `seen_ids.json` is the JS1 state after its last run (Run 3, 21:24:53 ET).
- **Checked on copy (2026-11-10):** the hashes of source and copy match, and the 323 ids in `seen_ids.json` are exactly the 323 job ids in
  `samsara.json`.
- **Only Samsara has a Day 1.** Every other JS2 board is baselined on its first JS2 run.
- The `raw_dir` paths inside `seen_ids.json` point to JS1's folders, which are not copied here. The full JS1 evidence is in the JS1 submission.
