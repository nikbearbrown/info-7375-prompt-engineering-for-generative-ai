# FILTER.md - Early Bird filter, version 1 (JS3)

Written 2026-11-25, before any JS3 code. Decisions are Vrajesh's (given 2026-11-25); the one-line reasons
were drafted with Claude from those decisions and are open for Vrajesh to rewrite.
Base: Early Bird JS2 (commit 3bd808f), rules R1-R4 from JS2. Changes from JS2 are marked NEW or WIDENED.
Tests use the fictional persona Rohan Desai (needs sponsorship), never the real resume.

## 1. The filter

A posting is relevant only if it passes every rule, checked in this order. The first failing rule is
recorded as the reason.

| Rule | What it checks | Reason (one line) |
|---|---|---|
| R1 WIDENED | Title contains a role phrase from the list below | These are the roles Vrajesh will apply to; JS2's list missed real ones |
| R2 | Title has senior, sr, staff, principal, lead, manager, head, director; or the description asks for 3+ years | Targets are new-grad / early-career roles |
| R3 | Posting country is the US | Vrajesh wants US roles only (JS2 review decision) |
| R4 | Description says it cannot sponsor, and the persona needs sponsorship | A hard blocker, quoted from the text |
| R5 NEW | Description requires a security clearance | Clearance needs US citizenship, which the persona does not have |

### R1 role phrases (v1)
From Vrajesh: backend engineer, Java engineer, Python engineer, .NET engineer, full stack engineer,
frontend software engineer, React developer, UI/UX developer, AI engineer, LLM engineer,
solutions architect / forward deployed engineer.
Carried over from JS2: software engineer, software developer, full-stack / back-end / front-end engineer.

**Not roles for Vrajesh (decided 2026-11-25):** machine learning (ML) roles are not wanted. AI engineer
roles are kept. Reason: Vrajesh's target is full-stack and AI-application work, not model research.

**Open, not added:** "Software Development Engineer" (seen in the JS2 rejects), "Platform Engineer",
"Web Application Developer". Not on Vrajesh's list, so not in v1. The reject audit will measure
how many real misses they are, then Vrajesh decides.

### Topic words
Topic words only count in the title. A word in the description alone never makes a posting relevant
("training" appears in sales, HR and ops postings). Reason: description text matches for the wrong reason.

## 2. Evidence rules

Every claim in a shortlist justification is labelled against the posting's own text:
- **supported**: a quoted span in the posting says it.
- **contradicted**: a quoted span in the posting says the opposite.
- **insufficient**: the text neither says it nor denies it.

The agent must answer "I cannot tell" (verdict `cannot_tell`, not `not_relevant`) when:
1. the posting's location is not mentioned, or
2. the posting's description is not mentioned (missing or empty).

Reason: a missing field is not evidence of a bad match. JS2 rejected every Greenhouse posting for
missing country; that was the wrong answer. A cannot_tell posting goes to the "check yourself" list.

## 3. Expected sources

Nine public boards, read through the JS2 allow-list and budget: Ashby (commure); Greenhouse (stripe,
figma, gleanwork, databricks, doordashusa, twitch, roblox); Lever (palantir). Snapshot: 2026-11-01.
Fields expected: id, title, location, description, url. Ashby and Lever give a country field; Greenhouse gives
only free-text location. When a field is missing the answer is cannot_tell (section 2), never a guess.

## 4. Wrong versions the tests must catch

- **W1 Senior/Staff kept**: a filter with no seniority rule keeps "Senior" and "Staff" titles. Must fail the tests.
- **W2 "training" as a topic word**: a filter that treats "training" as an AI signal keeps non-AI postings
  that mention training. Must fail the tests.
- **W3 Clearance ignored**: a filter with no clearance rule keeps "security clearance required" postings.
  Must fail the tests.

## 5. Version log

- v1 (2026-11-25): first JS3 version. R1 widened, R5 added, cannot_tell added, ML roles excluded.
- v2 (2026-11-25, after the hand-judged reject audit, labels in review/audit-labels.csv):
  - R4 widened: also "may not be able to employ ... sponsorship" and visa-word + "sponsorship at this time".
    Measured: v1 R4 matched 0 of 3068 postings (dead code); v2 moves 14 Roblox postings to R4 (items 6, 15 in the sample).
    False friend kept out: "executive sponsor", "gain sponsorship for deployments" (bare "sponsor" matched 77 sentences).
  - R5 widened: also "secret clearance" and "government clearance". Moves 1 posting (item 18). Bare "clearance" NOT added.
  - R1 widened: "Backend / API Engineer" (only "/ API"). Moves 4 postings, 2 relevant, 2 rejected by R3 (item 60).
  - Rejected after measuring: adding "Web Application Developer", "Security Engineer", "Solutions Engineer",
    "Integration Reliability Engineer" to R1 (audit items 5, 29, 42, 47, 52 were hand-judged N).
  - Rejected after measuring: a PhD/degree rule (one case, item 26, now labelled "?"; no evidence for a rule).
  - Known limit, not fixed: R5 still rejects "clearance is a plus" (audit item 55).
