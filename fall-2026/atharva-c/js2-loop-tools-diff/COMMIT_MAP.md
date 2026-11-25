# COMMIT_MAP

The JS2 work was built in a local repository and copied onto this branch on Nov 10, 2026 with `git cherry-pick -x`. That gives every commit a new hash but keeps its original author date and content. The documents in this folder (GATE, FRICTIONAL, REVIEW_PACKET, SOURCES, SIGNOFF, README) cite the **local** hashes; this table maps each one to its commit on this branch. Every commit message on this branch also ends with `(cherry picked from commit <local hash>)`.

| Local hash (cited in docs) | This branch | Date | Commit |
|---|---|---|---|
| `ed62f68` | `b6aa4c4` | 2026-11-08 | JS2: folder skeleton (empty headings only) |
| `777cef4` | `aa95cb2` | 2026-11-08 | JS2: GATE before code |
| `6ab952c` | `b2880bb` | 2026-11-08 | JS2: FRICTIONAL Nov 8 entry |
| `ab4ac2c` | `faf7ad0` | 2026-11-08 | JS2: boards.json (2 Greenhouse, 1 Lever, 1 deliberate failure) |
| `459e7b3` | `7549c11` | 2026-11-08 | JS2: WRONG_VERSIONS before tests |
| `75ff81e` | `fccff8f` | 2026-11-08 | JS2: BOUNDARY_TABLE predictions before tests |
| `f357831` | `42be988` | 2026-11-08 | JS2: permission policy in code + 12 boundary tests |
| `6981c72` | `142fd92` | 2026-11-08 | JS2: boundary table actual results, test evidence, FRICTIONAL step 6 |
| `4369abf` | `9c84617` | 2026-11-08 | JS2: bounded loop, budget.json, 17 loop tests, first live run evidence |
| `f982c6a` | `e0f0002` | 2026-11-09 | JS2: port JS1 skill matcher unchanged + reproduce React/Go defect on real postings |
| `e5a4ebc` | `d427652` | 2026-11-09 | JS2: React/Go skill tests written before the patch (RED, 7 failures) |
| `80e4fa1` | `3fe8a7d` | 2026-11-09 | JS2: React/Go skill-match patch by Claude, accepted by Atharva (GREEN, 35 tests) |
| `b690f1b` | `690a5ca` | 2026-11-09 | JS2: review packet (React/Go patch accepted) + after-patch check on real postings |
| `47a5e5d` | `33e7cac` | 2026-11-09 | JS2: second live run; budget demo exposes 'stopped mid-board' mislabel; failing test (RED) |
| `27483af` | `0c5fa19` | 2026-11-09 | JS2: fix budget-stop mislabel (board never requested is 'not reached'); demo re-run (GREEN, 36 tests) |
| `b166b17` | `b68d0a0` | 2026-11-09 | JS2: finished-wrong-answer demo (SEEDED empty board, naive loop, independent check) + independent recompute of new jobs |
| `b728f8d` | `fa6559e` | 2026-11-09 | JS2: FRICTIONAL entries for step 7 (written Nov 9) and Nov 9 |
| `5f0e305` | `594a5b0` | 2026-11-09 | JS2: GATE records the 10-second request timeout (decided Nov 9) |
| `64d795f` | `018d28b` | 2026-11-09 | JS2: README (commands tested on fresh clone, what ran, index; 'How the loop works' by Atharva) |
| `a45f592` | `177081d` | 2026-11-09 | JS2: SOURCES (starting point, endpoints, Claude vs. my contributions per commit) |
| `8c46481` | `315291b` | 2026-11-09 | JS2: sign-off and driver's seat (signed, Atharva C., Nov 9) |
| `c33b5a8` | `a47d152` | 2026-11-10 | JS2: sign-off 'How' section, driver's seat with Claude/me columns, review packet 'tests would still miss' |
