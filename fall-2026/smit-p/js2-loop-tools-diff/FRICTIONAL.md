# FRICTIONAL — Job-Search Agent 2

> **Smit: this file is not finished, and only you can finish it.** The course rule is that
> AI may organize your notes but you must supply the experience. Part A is a factual record
> of the Claude Code session, labeled as Claude's, which you can cite for traceability. Part
> B is yours. It needs your own attempts, what confused you, and what you accepted, changed,
> or rejected. Do not let Part A stand in for Part B; that would misrepresent who did the work.

## Part A — Session record (written by Claude Code, 2026-11-08)

Facts from the session, each tied to a commit or file. These are not Smit's reflections.

- **Gate first.** GATE.md committed alone (`f150426`), then the 25 boundary predictions
  (`2b3563e`), then the code (`f2c97b4`).
- **Ashby 403.** The first Python request to Ashby got HTTP 403, while curl to the same URL got
  200. Sending an explicit User-Agent fixed it. Evidence: `USER_AGENT` in `agent/fetch.py`.
- **Per-host gap invisible in the trace.** The first live run did wait 1 s between the two
  Greenhouse requests, but only the timestamps showed it. `host_gap_wait_s` was added to the
  trace afterwards, so run `2026-11-08T00-43-54Z` lacks that field and later runs have it.
- **Seeded runs would have overwritten the live baseline.** Noticed while writing the first
  seeded scenario, before running it; fixed in `45480d2` with a separate `jobs/seeded-state/`.
- **Finished wrong answer reproduced on v1.** `seeded-vanish-2` ended `finished` with exit 0;
  `verify_run.py` failed it; `seeded-vanish-3` then reported 145 old postings as new (`337cf1b`).
- **Test before patch.** `66d0cbc` added a test that failed 5 of 7 on v1.
- **First patch passed the suite but was wrong.** 57 tests OK; the independent check failed on
  `count 0` for a suspect board. Traced to two GATE.md tables disagreeing. Revised to
  `count: null` plus `observed_count` (`1b7f999`). REVIEW_PACKET.md section 5.
- **Redirect gap.** Found while writing POLICY.md's "not shown" list; test failed first
  (`evidence/redirect-test-before-fix.txt`), fixed in `1bfbb6d`.
- **Unresolved:** a board collapsing to a small nonzero count is not flagged; an all-suspect
  run ends `error`, which GATE.md did not explicitly decide.
- **No change seen live.** Three live runs minutes apart showed identical counts (145, 85, 32).

## Part B — Smit's entries

Use the course prompts. Short bullets are fine. Date each entry, and connect it to a commit,
test, or file.

### Entry 1 — date: ____

- What I was working on:
- I tried / expected:
- What happened:
- What I did:
- What Claude or another person contributed:
- What I understand now / still do not understand:
- Evidence and next step:

### Entry 2 — reviewing the patch (REVIEW_PACKET.md) — date: ____

- I re-ran (commands and what I saw):
- Did I agree with `null` over `0` for a suspect board? Why:
- My accept / revise / reject decision and the evidence it rests on:
- What I still do not understand about the diff:

### Entry 3 — what I accepted, changed, or rejected from Claude — date: ____

- Accepted:
- Changed:
- Rejected:
- Still unsure about:
