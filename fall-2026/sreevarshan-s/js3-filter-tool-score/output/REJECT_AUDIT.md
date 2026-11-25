# REJECT AUDIT — Job-Search Agent 3

Run date: 2026-11-24
Filter version: FILTER.md v0.2
Total postings: 1779 (Databricks 929, Stripe 765, Spotify 85)
Passed: 47 | Rejected: 1732

## Sample

30 random rejects + 10 closest calls = 40 postings judged by hand.
Seed: random.seed(42). Full sample in output/audit_sample.json.
All 40 are Greenhouse postings (Databricks 23, Stripe 17). No Spotify postings were drawn.

## Verdicts

| Verdict | Count |
|---|---|
| Correct | 38 |
| Can't tell | 2 |
| False reject | 0 |

Full verdicts with notes in output/audit_sheet.md.

## What the sample can show

40 hand-judged postings from 1732 rejected. A false-reject rate of 0/40 gives an upper bound of roughly 7% at 95% confidence (rule of three). This is not a measured rate for all rejects. The sample is entirely Greenhouse postings; the false-reject rate for Spotify rejects is unknown.

## The two can't-tell rows

Rows 12 and 38 are US-based Software Engineer postings rejected under the "software engineer needs a topic word" rule. No description was available to confirm or deny ML/data work. I recorded these as can't tell rather than forcing a verdict. They represent the main cost of the no-description gap in the Greenhouse data.

## Named false friend

Row 40: "Senior Solutions Architect (EDW Enterprise Data Warehouse Migrations)" at Databricks. Reached the closest-call pool because "data warehouse" appears in its title — a topic word. The role is senior pre-sales, based in Amsterdam. The filter correctly rejected it, but the case exposed that topic words in titles of non-target roles can generate false closest-call matches.

## What is outside the sample

Across all 1732 rejects, 8 titles contain "AI Engineer" (including "Applied AI Engineer" at Databricks and "AI Engineer" at Stripe). None was drawn into the sample. FILTER.md (v0.1 and the current v0.2) does not include "AI Engineer" as a role word. This gap was found by inspecting filter_results.json but cannot be measured from this sample.

## Rules changed after measuring

- Identified "AI Engineer" and "Applied AI Engineer" as FILTER.md v0.3 candidates. They are noted here only; FILTER.md itself has not been changed.
- No rules removed. No thresholds changed.
- Location is not a FILTER.md rule. 19 of the 38 correct rejects are outside the US; for 3 of them (rows 4, 35, 39) location was the only practical reason, while the filter rejected them on no_match.
