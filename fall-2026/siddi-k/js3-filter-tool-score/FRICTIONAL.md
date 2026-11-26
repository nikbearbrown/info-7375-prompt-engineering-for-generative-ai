# FRICTIONAL — JS3

> **Not written yet.** The entries below must be Siddi's own: what you tried, what surprised you, what you accepted, changed or rejected from Claude, and what you still don't understand. The event list underneath is Claude's, for reference only. It is not Siddi's account and earns nothing by itself.

## Siddi's entries

*(Write these yourself. Prompts from `prerequisites/frictional.md`:)*

- Date and what I was working on:
- I tried / expected:
- What happened:
- What I did:
- What Claude or another person contributed:
- What I understand now / still do not understand:
- Evidence and next step:

## Events Claude can point to (for reference; times ET, 2026-11-25)

| Time | Event | Evidence |
|---|---|---|
| ~21:50 | Siddi chose "Claude drafts, I edit" for FILTER.md and a 30-request budget | chat; FILTER.md header |
| 21:59 | Siddi answered the three open questions (anywhere in the USA; years cap 4; keep 30, though Claude's "~30" was really 31) and approved the rest | `4e62099c` |
| 22:00 | The collection ended `budget-exhausted`. Canva had grown to 29 postings, so 2 had no text. | `40f9ea3e` |
| 22:03 | Filter v1 kept only 8 of 975. Claude found that G4 reads "Chicago", "SF, NYC" and the like as not US. | `2ffbb8f9`; AUDIT.md |
| 22:07 | The real Claude CLI session probed the 2026-07-28 `server/discover` before falling back to `initialize` | `evidence/mcp/2026-11-26T03-06-55Z/` |
| 22:12 | The shortlist showed the Security Engineer: supported claims, wrong answer | SHORTLIST.md |
| 22:18 | The first course-server session failed (the tap's folder bug) and Claude said it would not guess. Re-run worked. | `evidence/other-server/` |
| 22:21 | Five Claude variants: identical verdicts on all held-out postings | `6dcc3edd` |
| 22:25 | Siddi's 62 blind labels: 39 relevant, 25 of which conflict with LABELING.md; Stripe 7392697 flipped from Oct 31 | `4d633be9` |
| ~22:28 | Siddi kept the labels as-is, adopted v1.1 and rejected v1.2 | `labels/DECISION.md`, FILTER.md §E |
