# Facts for the JS3 sign-off (collected by Claude, 2026-11-25)

Facts only. Which of them Shubham checked himself, and how, is his to say in the sign-off.

## Tests that exist (all in `tests/js3/`, run offline)

| Test file | What it pins |
|---|---|
| `test_filter.py` | FILTER.md is the frozen v0.3; v0.1 has "api" and no blockers; one filter block only; the CONTRACT bar scores exactly 7 and is kept; skill cap; topic once; R2 and its blockers; blockers never touch R1; each veto; unknown location is 0 |
| `test_wrong_versions.py` | WV1–WV5 from FILTER.md §4: the real code passes all five checks, each wrong version fails its named check |
| `test_claims.py` | Labels for C1–C5, silence → insufficient, contradiction first, both ways → insufficient, short text, years parsing; two documented limits pinned (`test_limit_*`) |
| `test_audit.py` | Clopper–Pearson against known values (0/40 → 0–8.81%); the committed draw has the registered sizes and strata; tally counts both error directions; a blank verdict file is refused |
| `test_mcp_server.py` | Version negotiation; nothing before `initialized`; one read-only tool; bad arguments are tool errors; unknown tool/method are protocol errors; notifications get no reply; transcript only under `data/js3/mcp/`; a real stdio session |

Whole suite on 2026-11-25 after the JS3 work: see README "Commands" for the count at the final commit.

## Things that ran (all by Claude, 2026-11-25)

See README "What ran". Commits: FILTER v0.1 `bd34a42` (before code), v0.2 `0a79edf`, v0.3 `3d0f3ed`,
audit draw `e470923`, predictions `5448d94`, results `4d8395f`.

## Candidate "Not checked" items (true; pick and phrase your own)

1. No hand verdicts existed when the filter was changed (v0.2, v0.3); those changes were judged
   by Claude's counts and reading, and only the audit verdicts test them.
2. The held-out labels are 10 Stripe postings labelled against the JS1 rule, not against "worth
   my time"; they cannot show the effect of changes that act on Figma or Ramp titles.
3. The C2 "supported" labels are word matches: "such as Python, or similar" counts as asking for Python.
4. C4 reads only "N+ years" minimums: it misses ceilings ("no more than 18 months"), spelled-out
   numbers with a parenthesis ("three (3) years"), and treats "preferred" as required.
5. C5 is insufficient on all 1,235 postings. Before the review fix, its "offer" pattern wrongly
   labelled two Ramp postings "supported" (a golfer sponsorship, a relocation sponsorship); after
   it, no sponsorship pattern fires on real data, only in tests.
9. C4 counts any "N years" in a sentence that mentions experience ("systems that have run for
   20 years" would read as a 20-year minimum), and misses "Two years" and "3+ yrs".
6. The corpus is from 2026-11-11 or earlier; it was not re-fetched. A separate live check on
   2026-11-25 found 36 of the 53 shortlisted postings still listed; 2 of the 17 gone had already
   left the board before 2026-11-11 but stayed in the corpus (`docs/js3/LIVENESS.md`).
7. The MCP server was used by one client (Claude Code 2.1.330); Playwright MCP was evaluated
   from its tool list and source, never run.
8. E3 ran each condition once (10 calls each); a re-run could differ.

## Candidate "Not claiming" items

- That a kept posting is worth applying to, or that a rejected one is not.
- A miss rate for the filter: the audit gives an interval from 40 postings, not a measured rate.
- That any model was trained or adapted: nothing was.
- That Playwright MCP is unsafe in general: only that it is wrong for an agent that must never act.
