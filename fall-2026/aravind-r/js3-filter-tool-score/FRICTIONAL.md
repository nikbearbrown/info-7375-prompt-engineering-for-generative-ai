# FRICTIONAL — Job-Search Agent 3

**Status: in progress (2026-11-25).** Aravind writes this log. Entries Claude Code typed from Aravind's
dictation are marked as dictated.

## 2026-11-25: manual Phase 3 replies saved under the wrong filenames (dictated by Aravind)

- **What happened.** I skipped a `pbcopy` step while pasting the manual claude.ai replies, so the
  clipboard still held the previous reply. The replies for **A005** and **A010** were first saved
  under the wrong filenames (`A010.txt` and `A014.txt`).
- **How I caught it.** I grepped the replies for `posting_id` and compared each one with its
  filename. I renamed the files; **no content was edited**. A014 was then run afterward in its own
  incognito chat.
- **What changed.** `tools/import-manual.mjs` now rejects any reply whose `posting_id` names a
  different posting than its filename (`checkReplyPosting` in `src/justify.mjs`). Nothing is written
  for that reply, and the exit code is 3 (`test/import-manual.test.mjs`).
- **Verified before import (Claude Code, read-only, 2026-11-25):** all 7 files now have a
  `posting_id` that matches their filename.

---

# Structure (pre-filled by Claude Code: headings and commit hashes only; Aravind dictates the content)

## Gate and tests
Commits: `bb88c420` (FILTER.md + tests before code), `affdd761` (W11 fixture fix), Checkpoint 1 edits

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Filter v1.0.0 and the shortlist definition
Commits: `13b4c6c4`, `67e959fb`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Reject audit, first pass and recheck
Commits: `90fcd369`, `1c9ce17b`, `2c29cbab`, `7dc781af`, `8f27d02d`, `c711833a`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Persona correction and v1.1.0-a
Commits: `f3cefa22`, `cd672e2f`, `bdc146c8`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## v1.1.0-b to v1.1.0-e
Commits: `de871afa`, `537bebd0`, `242af122`, `6acfa20d`, `4abf4d39`, `70c22c16` (tag `js3-filter-final`)

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Veto check
Commits: `e0d80ff0`, `63aacc6b`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## False friends
Commits: `0797611f`, `df3c6ff8`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Labels
Commits: `28cfad43`, `106cd4a7`, `6fc19f50`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Claude calls: spend limit and manual route
Commits: `59d8fc69`, `3caf2978`, `21609f36`, `9ab830b9`, `0a3cc5e8`, `d495dfb8`, `1d65ff45`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Claim labels and the location-field amendment
Commits: `40cdc6e8`, `ffd5e49f`, `47cbd6e6`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## MCP server, clients, evaluations
Commits: `461b608d`, `82f18acc`, `592026e1`, `903d314b`, `8c91ddc0`, `111cc67b`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

## Phase 5
Commits: `452cffbf`, `450ee861`

- **Accepted from Claude:**
- **Modified:**
- **Rejected:**
- **What I checked:**
- **Unresolved:**

