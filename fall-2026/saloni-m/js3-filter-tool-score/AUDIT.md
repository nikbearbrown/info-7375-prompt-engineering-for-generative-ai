# The reject audit (Chapter 7)

Filter: FILTER.md **v1.0**. Run on the live snapshot `out/snapshots/20261126T162725Z`
(collected 2026-11-26 16:27 UTC: anthropic 634, figma 141, openai 876 = **1,651** postings,
3 of 3 boards seen, 0 with missing text). v1.0 **kept 89 and rejected 1,562**
(`out/filter/v1.0/summary.json`).

## 1. The sample (SEEDED, seed 7375, drawn once: `labels/SAMPLE.json`)

| Stratum | n | How chosen |
|---|---|---|
| random_reject | 35 | uniform random from the 1,562 rejects |
| near_threshold | 12 | 6 random rejects with score 2 (one point below), **the only** keep at exactly 3, and 5 random keeps at 4 |
| random_keep | 10 | uniform random from the remaining keeps |
| **dev total** | **57** | shuffled into `labels/audit_sheet.csv`; the sheet shows no score or decision (blind) |
| held-out (not used here) | 30 | 15 random keeps + 15 random rejects, disjoint from dev, for SCORE.md only |

Claude Code redrew the sample once, before any label existed. The first draw missed the single posting at
exactly the threshold, so I changed the rule to always include it (FRICTIONAL.md, entry 3).

## 2. Hand verdicts — PENDING SALONI

> **Not done yet.** Every verdict in `labels/audit_sheet.csv` is empty. Saloni labels with
> `python3 scripts/label.py labels/audit_sheet.csv`, using `labels/LABELING-RULE.md`. Then
> `python3 scripts/audit_report.py` computes the tables below into `out/audit_report.json`.
> Nothing in this section may be filled in by Claude.

| Stratum | n | cannot tell | judged | filter wrong (by Saloni's label) | exact 95% interval |
|---|---|---|---|---|---|
| random_reject | 35 | _ | _ | _ | _ |
| near_threshold | 12 | _ | _ | _ | (not random: no rate) |
| random_keep | 10 | _ | _ | _ | _ |

**What the sample can honestly say.** Write it from the numbers, in this form: "k of n random
rejects were wrong. If this sample is typical, between a and b of the 1,562 rejects could be
wrong (exact 95% interval). That is a sample estimate, not a measured count." For scale: even
**0 of 35** wrong only shows the reject error rate is probably below **10.0%**, which is up
to about 156 of 1,562 postings. A sample of 35 cannot show that the filter misses "almost
nothing". The near-threshold stratum was chosen by score, so it shows where the filter is
fragile, and gives no rate for anything.

## 3. False friend — measured by code; Saloni confirms by hand

**`training` (rule R3, topic word).** It matched **819** postings, more than any other word
(`matched_word_counts`). **634** of them are Anthropic postings, which is **all 634** Anthropic
postings. Every Anthropic posting carries two boilerplate sentences:

- "Minimum education: Bachelor's degree or an equivalent combination of education, **training**,
  and/or experience"
- "…relevant to the role as demonstrated through coursework, **training**, or professional
  experience"

So in those postings "training" means *an education requirement*, not *model training*. It
added +1 to Priya's score for every Anthropic posting, including "IT Systems Engineer, M&A" and
"Support Engineer". FILTER.md §2 had flagged it as a suspect before any data was collected.
These counts measure it.

What removing it does (candidate C1, `config/filter_variants/C1-no-training.json`, measured on
all 1,651 by `scripts/run_filter.py`): **610 scores change and 0 keep/reject decisions flip.**
The score-2 band just below the threshold shrinks from 265 to 148 rejects. "training" never
decided a keep, because the topic cap is +2 and a keep needs a title role word. It did crowd
the near-threshold band with postings that are not close calls. So the false friend matters
for ranking and for which calls look close, not for v1.0's decisions.

**A second word that matched for the wrong reason: `applied ai` (R1, title).** It matched 147
titles; **74 are "Applied AI Architect"**, and 34 of the 89 keeps are Architect roles. Every
Architect posting Claude justified (SHORTLIST.md) describes a customer-facing advisory role
("act as the 'CTO of your book of business'"). That is the kind of role labeling rule 1
excludes. Saloni's hand labels on the 10 random keeps will show whether that is a real error.

## 4. Rules added, cut, or rejected after measuring — PENDING SALONI'S DEV LABELS

Three candidates were written after reading v1.0's output. None is adopted yet. Each is
measured on the dev labels with `python3 scripts/experiments.py measure --sheet audit` (see
SCORE.md), and Saloni decides. FILTER.md §6 records the outcome as added, cut, or rejected.

| Candidate | Change | Effect on all 1,651 (measured, no labels needed) | Dev result | Decision |
|---|---|---|---|---|
| C1 | cut topic word `training` | 610 score changes, 0 decision flips | _ | _ |
| C2 | add title veto `architect`, `recruiter` | 34 keeps become rejects | _ | _ |
| C3 | R4 reads "5+ years" without the word "experience" | 187 score changes, 12 keeps become rejects | _ | _ |

C2 has a trap that Claude Code spotted while drafting it. A veto on `recruiting` would have rejected "Recruiting
Analytics Data Engineer", which is a data-engineering job. So the word list stops at `recruiter`.
