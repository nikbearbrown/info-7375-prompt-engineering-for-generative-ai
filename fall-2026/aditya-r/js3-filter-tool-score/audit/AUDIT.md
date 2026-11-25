# Reject audit: filter v1.0 against Aditya's dev labels

- **Labels:** Aditya, blind, 2026-11-25. There are 63 rows in `labels/dev_labels.csv`, which are dev under amendment A3.
- **Recompute:** every number below comes from `.venv/bin/python -m js3.audit`, which writes `audit/audit_results.json`.
- **Counting:**
  - An **error** is a filter verdict that disagrees with a decided label (`yes` or `no`).
  - `unsure` (10 rows) is reported, never counted as right or wrong.
  - The groups are **stratified samples**. They are not the population.

## 1. Errors by sampling group (v1.0, threshold 6)

| Group (how it was drawn) | n | Aditya: yes / no / unsure | v1.0 errors | Which |
|---|---|---|---|---|
| D-random-reject (uniform over the 1,249 non-H rejects, seed 7376) | 30 | 0 / 27 / 3 | **0 of 27** decided | — |
| H-other-reject (10 clusters, uniform within "other rejects", seed 7375) | 10 | 0 / 10 / 0 | 0 of 10 | — |
| D-close-below (score 5, just rejected) | 6 | 2 / 2 / 2 | **2 of 4** decided (missed yes) | S05, S43 |
| H-near-reject (score 3–5) | 10 | 1 / 5 / 4 | **1 of 6** decided (missed yes) | S26 |
| D-close-above (score 6, just kept) | 3 | 2 / 0 / 1 | 0 of 2 | — |
| D-kept (all keep clusters outside the old H) | 4 | 3 / 0 / 1 | 0 of 3 | — |
| H-keep | 3 | 3 / 0 / 0 | 0 of 3 | — |

Across the 53 decided labels, v1.0 has **TP 6, FP 0, FN 3, TN 44**. All three errors are **missed yeses at score 5, one point below the threshold.** No keep was labeled `no`. S35, S39 and S48 belong to both "close-above" and "kept"; they are counted once in the totals.

## 2. What 30 random rejects can and cannot tell us

- **Observed:** 0 of the 27 decided random rejects was a `yes`. The exact 95% interval for the miss rate **among v1.0 rejects** is **0 % to 12.8 %**.
- **Worst case:** counting the 3 `unsure` rows as misses gives 3/30, with a 95% interval of **2.1 % to 26.5 %**.
- **What that allows us to say:** v1.0 rejected 1,282 postings. **Zero** misses among 30 is still compatible with as many as roughly 160 worthwhile postings among them (0.128 × 1,282), or around 340 in the worst case.
- **Why it is not more:** a sample of 30 can rule out a *high* miss rate. It cannot show that the miss rate is low. This is an interval estimate from one sample, **not a measured rate**.
- **A further caveat:** the draw skipped a posting whose near-duplicate cluster had already been drawn (A1), which slightly under-weights large clusters.
- **The near-threshold rows** (16 at score 3–5, 3 of them misses) were chosen *because* they sit next to the cut-off. They show **where** the errors concentrate. They cannot estimate an overall error rate, because their selection depends on the score whose errors we would be estimating.

## 3. False friend: "agent(s)" and "unity catalog" from employer boilerplate

- **The predicted wrong reason** (FILTER.md §6): support or sales *agents*.
- **The actual wrong reason:** the employer's product names, in its "About us" text. The board's boilerplate list (`filters/boilerplate_segments.json`) contains the Databricks sentence:

  > "Headquartered in San Francisco with 30+ offices around the globe, Databricks offers a unified platform that includes Genie, Lakebase, Agent **Bricks**, Lakeflow, Lakehouse, and **Unity Catalog**."

- **Measured:**
  - On Databricks, "agent(s)" and "unity catalog" match in all 995 postings. The only match is in a boilerplate segment in 892 postings ("agent"), 897 ("agents") and 950 ("unity catalog").
  - On Notion, "agents" matches in all 155 postings, 124 of them only in boilerplate.
  - So v1.0 gives almost every Databricks posting **T4 + T7 = +2** for words that describe the employer, not the role.
- **Effect on one posting:** S35, `greenhouse:databricks:8133691002`, "Software Engineer - New Grad (2027 Start) - Aarhus".
  - v1.0: `R 2 + S 0 + T 3 + E 1 + Y 0 = 6`, so **keep**. T3 = python + agent (boilerplate) + unity catalog (boilerplate).
  - With the boilerplate removed (`--filter cand-a_boilerplate`): `R 2 + S 0 + T 1 + E 1 + Y 0 = 4`, so **reject**.
  - Aditya labeled it **yes**. **The false friend produced a right answer for the wrong reason.** The same is true of S48 and S11, which are also New Grad postings.
- **Two smaller false friends:**
  - `junior` in S41: "…from the most **junior** data scientists and machine learning engineers to the world class experts". That describes the product's users, not the role, yet it scores E +1. The posting itself asks for "2-8 years".
  - The Y rule's smallest number in S05: "5+ years of industry experience …, with **3+ years** focused on applied machine learning". That reads N = 3, which is the sub-requirement, not the floor.

## 4. Every rule considered after measuring (dev labels)

Each change was made alone against v1.0, unless it is marked as a combination. The comparison uses the 53 decided dev labels, with corpus keeps out of 1,294.

| Candidate | Object changed | TP / FP / FN | Recall · Precision | Corpus keeps | Flips (sheet id: label) | Status |
|---|---|---|---|---|---|---|
| v1.0 | — | 6 / 0 / 3 | 6/9 · 6/6 | 11 | — | baseline |
| **C-a** boilerplate removed from topic matching | filter file | 3 / 0 / 6 | 3/9 · 3/3 | 4 | S11 yes, S35 yes, S48 yes, S39 unsure: keep → reject | **rejected alone**: it fixes the false friend but loses 3 correct keeps |
| **C-b** years: only N ≥ 5 gives −1 (was −3, and 3–4 gave −1) | filter file | 9 / 0 / 0 | 9/9 · 9/9 | 18 | S05 yes, S26 yes, S43 yes, S04 unsure: reject → keep | candidate |
| C-e early-career +1 → +3 | filter file | 6 / 1 / 3 | 6/9 · 6/7 | 19 | S23 no (Product Design New Grad): reject → keep | rejected alone: adds a false keep |
| C-t threshold 6 → 5 | setting | 9 / 2 / 0 | 9/9 · 9/11 | 27 | S23 no, S52 no (Systems PhD) become keeps, plus the C-b flips | rejected: 2 false keeps |
| C-r add "forward deployed engineer", "solutions engineer" | filter file | 6 / 0 / 3 | 6/9 · 6/6 | 17 | only S27 and S42, both unsure | rejected: no `yes` supports it |
| **C-a + C-b + C-e** | three filter-file changes | 9 / 0 / 0 | 9/9 · 9/9 | 15 | S05, S26, S43 yes: → keep; S39 unsure: → reject | candidate (a combination) |

**Honest reading:**
- Both candidates reach 9/9 · 9/9 on dev, but they were **chosen to fix the same three misses** on that same dev set. Dev cannot separate them, and either could be over-fitted to these three postings.
- That is what the fresh held-out set H2 is for. H2 has no v1.0 keep (A3), so it mainly tests **recall near the threshold** and **false keeps among the postings a revision newly keeps**.

## 5. Freeze decision (Aditya)

**Pending.** The choice for **v1.1** is between:
- **C-b alone**: one change. The false friend stays.
- **C-a + C-b + C-e**: removes the false friend, and keeps New Grad postings for the explicit new-grad signal.

The frozen choice is recorded in `FREEZE.json`, together with the single-change comparisons that will be measured on H2.
