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

## 2. Hand verdicts

> Filled by `python3 scripts/finish.py` from Saloni's labels in `labels/audit_sheet.csv`
> (labelled with `scripts/label.py`, rule `labels/LABELING-RULE.md`). Until then the block is empty.
> Claude Code wrote the script; it did not write any label.

<!-- finish.py:verdicts -->
Labelled by Saloni with `scripts/label.py`, blind to the filter's decision. Computed by
`scripts/audit_report.py` into `out/audit_report.json` and written here by `scripts/finish.py`.

| Stratum | n | cannot tell | judged | filter wrong (by Saloni's label) | exact 95% interval |
|---|---|---|---|---|---|
| random_reject | 35 | 0 | 35 | 7 | 8.4% – 36.9% |
| near_threshold | 12 | 0 | 12 | 2 | (not random: no rate) |
| random_keep | 10 | 0 | 10 | 2 | 2.5% – 55.6% |

**What the sample can honestly say.** 7 of 35 judged random rejects were
wrong by my label. Between 132 and 577 of the 1,562 rejects could be wrong (95% exact interval, k=7, n=35); a sample estimate, not a measured count. For keeps: 2 of
10 judged random keeps were wrong; between 2 and 49 of the 89 keeps could be wrong (95% exact interval, k=2, n=10); a sample estimate, not a measured count. A sample of
35 cannot show that the filter misses "almost nothing". The near-threshold stratum was
chosen by score, so it shows where the filter is fragile and gives no rate for anything.

**Relabelled after seeing the first results.** After the first `finish.py` run I re-answered 9 dev rows whose first label conflicted with my rule (`labels/relabel_log.csv` keeps the first answers and times). 2 changed: row 4 Data Center Strategic Sourcing Lead - Construction worth_time → not_worth_time; row 26 Applied AI Architect, Commercial worth_time → not_worth_time; 7 I kept. The sheet still hid the filter's decision, but I had seen the error list, so these rows were not labelled blind the second time.

**Rows where the filter and I disagree:**

- near_threshold: **Applied AI Engineer, Codex** — filter reject, my label worth_time, score 2
- near_threshold: **Data Engineer, Billing & Payments** — filter reject, my label worth_time, score 2
- random_keep: **Applied AI Architect, Commercial** — filter keep, my label not_worth_time, score 5
- random_keep: **Applied AI Engineer, Cyber | Tokyo** — filter keep, my label not_worth_time, score 5
- random_reject: **Software Engineer, Product Velocity** — filter reject, my label worth_time, score 1
- random_reject: **Software Engineer, Infrastructure Security** — filter reject, my label worth_time, score 2
- random_reject: **Product Data Scientist - Youth, Families and Learning** — filter reject, my label worth_time, score 2
- random_reject: **Camera Software Engineer, Consumer Devices** — filter reject, my label worth_time, score 0
- random_reject: **Anthropic Fellows Program, AI Safety & Security** — filter reject, my label worth_time, score 2
- random_reject: **Software Engineer, Codex Core Agents** — filter reject, my label worth_time, score 0
- random_reject: **Safeguards Enforcement Analyst, Targeting, Tracking & Surveillance** — filter reject, my label worth_time, score 2

**Each matched word against my labels (dev rows only; top 12 by count):**

| matched word | worth time | not worth time | cannot tell |
|---|---|---|---|
| `R3:training` | 16 | 19 | 0 |
| `R3:python` | 14 | 11 | 0 |
| `R3:evaluation` | 9 | 8 | 0 |
| `R3:llm` | 7 | 6 | 0 |
| `R1:applied ai` | 8 | 4 | 0 |
| `R3:sql` | 4 | 4 | 0 |
| `R1:machine learning` | 4 | 0 | 0 |
| `R1:ai engineer` | 2 | 1 | 0 |
| `R1:ml` | 2 | 0 | 0 |
| `R3:airflow` | 1 | 1 | 0 |
| `R1:data engineer` | 2 | 0 | 0 |
| `R3:spark` | 0 | 1 | 0 |
<!-- /finish.py:verdicts -->

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
excludes. **My hand labels did not confirm this.** Of the 7 "Applied AI Architect" rows in the dev
sample, I labelled 6 worth Priya's time and 1 not (row 26, Commercial), after re-reading all 7 a
second time (`labels/relabel_log.csv`); the one Architect manager role I labelled not worth it. So
`applied ai` is a suspect word by Claude's reading of the postings, not an error by my labels,
and that is why C2 was rejected (§4).

## 4. Rules added, cut, or rejected after measuring

Three candidates were written after reading v1.0's output. Each is measured on the 57 dev labels
(`python3 scripts/experiments.py measure --sheet audit`, run by `scripts/finish.py`).

**Decision rule, fixed 2026-11-26 before any label existed** (so the labels cannot be used to
pick a rule after the fact): adopt a candidate only if, on the dev labels, it makes fewer filter
errors than v1.0 **and** turns no row v1.0 got right into an error. A tie is a rejection, so
v1.0 stays when there is no evidence for the change. Rows labelled "cannot tell" count for
neither side. FILTER.md §6 records the outcome.

<!-- finish.py:candidates -->
| Candidate | Change | Effect on all 1,651 (measured, no labels needed) | Dev result (Saloni's 57 labels) | Decision (by the rule above) |
|---|---|---|---|---|
| C1 | cut topic word `training` | 610 score changes, 0 decision flips | v1.0 11 errors → 11; fixes 0, breaks 0 | **rejected**: no fewer dev errors than v1.0 (tie = keep v1.0) |
| C2 | add title veto `architect`, `recruiter` | 34 keeps become rejects | v1.0 11 errors → 16; fixes 1, breaks 6 (fixes Applied AI Architect, Commercial; breaks Applied AI Architect - Tokyo; breaks Applied AI Architect (Brazil); breaks Applied AI Architect, Education; breaks Cyber Partner Applied AI Architect; breaks Applied AI Architect; breaks Applied AI Architect) | **rejected**: would turn a correct row into an error |
| C3 | R4 reads "5+ years" without the word "experience" | 187 score changes, 12 keeps become rejects | v1.0 11 errors → 11; fixes 1, breaks 1 (fixes Applied AI Engineer, Cyber | Tokyo; breaks Applied AI Engineer, Codex) | **rejected**: would turn a correct row into an error |
<!-- /finish.py:candidates -->

C2 has a trap that Claude Code spotted while drafting it. A veto on `recruiting` would have rejected "Recruiting
Analytics Data Engineer", which is a data-engineering job. So the word list stops at `recruiter`.
