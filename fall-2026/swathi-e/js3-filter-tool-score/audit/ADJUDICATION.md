# ADJUDICATION.md — reconsidered human audit judgments

Each entry records a judgment I reconsidered after the audit was committed.
`HUMAN_AUDIT.csv` (commit `fed055f`) is never edited: the original judgment stays
part of the historical human audit, and an adjudicated label is reported
separately, next to the original.

## 2026-11-19 — Row 35 (decision discussed 2026-11-18, recorded 2026-11-19)

| Field | Value |
|---|---|
| Row | 35 |
| Company | Databricks |
| Posting ID | 8843577002 |
| Title | Product Design New Grad (2027 Start) |
| Original human judgment | `relevant` (`how_judged`: "User checked posting after seeing ChatGPT AI-assisted draft") |
| Adjudicated judgment | `not relevant` |

**Reason.** Product design and UX are not AI/ML, data, or early-career
software engineering work under `AUDIT-RULE.md`, Check 1 ("the job is AI/ML,
data, or early-career software work"). The posting is for "an Associate
Product Designer" with "a bachelors or masters degree in HCI or related design
practice"; its SQL, Python and AI-tooling lines describe tools used in design
work, not the work itself.

**Timing.** This adjudication was made after comparing my original judgment
with the filter's prediction (filter v1: `not shortlisted`, R1 fail, "title
names no R1 role term"). It is not a blind judgment.

**Transparency.** The original judgment, `relevant`, remains part of the
historical human audit. Any report must show results with the original label
and, separately, with this adjudicated label; the adjudicated label must not
replace the original silently.

Recorded by Claude Code from Swathi's decision; decision by Swathi Baba Eswarappa.
