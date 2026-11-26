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

# Skeleton (pre-filled by Claude Code with facts and commit hashes; Aravind writes the account)

For each entry, write in your own words:
- what happened
- what you checked
- what you changed, or what is still unresolved
- what you accepted, modified, or rejected from Claude

Facts and hashes are pre-filled; the `> ` lines are yours.

## 1. The gate came first, and a gate test was wrong
- `bb88c420`: FILTER.md v1.0.0 and the tests, committed before any `src/`.
- `affdd761`: the W11 test fixture scored 1.0, so it could never fail; fixed after the gate commit.
- Checkpoint 1: threshold 0.70 → 0.80 and W13 added (your edits).
> 

## 2. The empty shortlist and the counts
- `13b4c6c4`: v1.0.0 kept 0 of 1,064.
- `67e959fb`: shortlist = keep ∪ cannot_tell, fixed before any verdict.
> 

## 3. The first audit pass was looser than the written definition
- `1c9ce17b`: 45 verdicts. `2c29cbab`: 12 of 15 closest calls disagreed.
- `90fcd369`: judging plan (first 30 in seeded order, not A001–A030).
- `c711833a`: recheck, 10 of 14 revised. Selection caveat: rows were chosen after seeing the
  results.
> 

## 4. The persona was corrected after the audit
- `f3cefa22`: `years_pm` 2 → preferred 4 / stretch 6. `cd672e2f` (v1.1.0-a) cites the 12 closest
  calls (dev use).
- Accepted, modified, or rejected from Claude: the recheck-scope question (adding 6 rows,
  `8f27d02d`).
> 

## 5. Rule changes v1.1.0-b to e, and the bugs found along the way
- `de871afa` (b, boilerplate topic words), `537bebd0` + `242af122` (c, vetoes; the CHANGELOG row was
  missing at first), `6acfa20d` (d, the "6–10+ years" misread, found by a test written for v1.1.0-a),
  `4abf4d39` (e, TPM tier).
- `e0d80ff0`: the sponsor/visa grep found 2 missed veto phrasings; the 0-veto result had been
  misleading.
> 

## 6. False friends
- Primary "program manager" (A027, A044, A052); secondary "training" (A014, A047; not a filter
  word); boilerplate "payments" (159 reworded intros). `df3c6ff8`.
> 

## 7. Spend limit, and the manual route for Claude
- `3caf2978`: all 7 `claude -p` calls failed with no reply. `21609f36` / `9ab830b9` / `0a3cc5e8`: the
  fallback.
- The misfiled replies (entry above); `d495dfb8`: the filing guard.
> 

## 8. Claim labels
- `ffd5e49f`: 46 accepted, 8 changed (6 location → contradicted; A010.4 and A042.4 → supported).
- `40cdc6e8`: the location field counts as text, an amendment made after seeing the replies.
> 

## 9. The MCP server and its clients
- `461b608d` server. `82f18acc` Claude Code (no `tools/call`: spend limit). `592026e1` Claude Desktop,
  3 calls.
- Finding: the description said "no posting text", but the veto quote is posting text; fixed in
  `111cc67b` after the run.
> 

## 10. Phase 5 found nothing to measure
- `452cffbf`: plan declared first. `450ee861`: held-out 0 relevant of 20; recall unmeasurable.
- Unresolved: an enriched sample with no positives. What would you do differently?
> 
