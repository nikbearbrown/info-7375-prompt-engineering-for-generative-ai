# AUDIT.md: the reject audit of filter v1

Job-Search Agent 3. Facts in sections 1 to 6 were written by Claude Code (claude-opus-5-5) on 2026-11-25 from committed files only; each number cites its file. Sections 7 to 9 are Deepak's.

## 1. What was audited

- Filter: v1 (FILTER.md as committed in 494cfdd, with the clarifications in 9c3a903 and 685d231), run on every posting of `data/postings-20261125T200226Z.jsonl` (1285 postings from the live run `runs/20261125T200226Z`). Output: `data/filter-v1.jsonl`: keep 3, reject 1282, abstain 0, plus one board-level abstention for `greenhouse:stripe-js2-nonexistent` (commit e9573dc).
- Sheet: `audit/audit-v1.csv`, drawn with audit seed 7375031 (commit 8be6822), near-decision group appended (commit de07a0e, FILTER.md section 2 as amended in ce97f9a). The 40 held-out postings were excluded; their keys were recomputed from the held-out seeds and `labels/heldout.csv` was not opened.
- Verdicts, three passes, all Deepak's, all 45 rows each time:
  1. First pass, committed in ad58e97. Cleared after the section 0 consistency check (first run, commit 9a055be) found mis-keys: Deepak reported he had likely used r as "reject". The labeler then gained a hint on every row and a `--clear` option (commit aadf062).
  2. Second pass, committed in 2c9665e: 5 of 45 rows differed from the first (commit 0ffa01e holds its facts). Deepak reported it still had errors.
  3. Third pass, final, used everywhere below: cleared and relabeled with `python -m jobwatch label --checklist`, which asks the three FILTER.md section 0 checks per row and derives the verdict from them (commit 000a284), committed in 65c9863. 13 of 45 verdicts differ from the second pass. In this pass 15 rows have a check answer that contradicts the question's own wording: the seniority answer is y on 8 rows whose titles contain a word the question names (Manager 4, Intern 3, Staff 1), and the location answer is y on 8 rows whose location is not one the question names (Singapore, Washington D.C., North America, San Francisco 2, Chicago, London, N/A); one row (Staff Machine Learning Engineer, Radar) has both. Found by a scratch comparison of `audit/audit-v1.csv` at 65c9863 with the question texts in `jobwatch/label.py`; not computed by `audit-stats`, which by Deepak's decision does not check checklist rows.
  4. A fourth pass with `python -m jobwatch label --family` (seniority and location applied mechanically, commits f0348bd and 76f7bad) was started by Deepak and stopped after 4 of 45 rows, and later committed in f0568bc (4 of 45 verdicts). It is not used: Deepak chose the third pass as final. The Phase 3d measurements use a byte-identical copy of the committed third pass, `audit/snapshots/audit-v1@65c9863.csv` (commit a090720).
- The first two passes were replaced because answers contradicted the labeling rule's wording; the final third pass still has the 15 contradicting answers above, and every number below rests on it as committed.
- Facts: `python -m jobwatch audit-stats` wrote `audit/audit-v1-stats.json` and `audit/audit-v1-facts.md`; `scripts/clopper_pearson_check.py 9 30` wrote `audit/audit-v1-ci-check.txt` (commit fb02ee4; the facts files were regenerated in 520fee6 to add a failed-experience column, 0 in every group, with no other change). Earlier passes' versions of these files are in commits 9a055be and 0ffa01e.

| Group (FILTER.md section 2) | Asked | Drawn | Pool | Note |
|---|---|---|---|---|
| close_call_reject | 10 | 0 | 0 | v1 has no scored rejects (shortfall 10) |
| close_call_keep | 5 | 3 | 3 | every kept posting (shortfall 2) |
| random_reject | 30 | 30 | 1242 | random.Random(7375031).sample |
| random_keep | 10 | 0 | 0 | all 3 keeps already drawn above (shortfall 10) |
| near_decision | all | 12 | 12 | every role-matched v1 reject outside the held-out set; no sampling |

Source: the comment lines of `audit/audit-v1.csv`.

## 2. The filter's errors against Deepak's verdicts

An error is a kept posting judged not_relevant, or a rejected posting judged relevant (`jobwatch/auditstats.py`).

| Group | Audited | Judged relevant | Judged not_relevant | Filter errors | OVERRIDEs |
|---|---|---|---|---|---|
| close_call_keep | 3 | 3/3 | 0/3 | 0/3 | 3/3 |
| random_reject | 30 | 9/30 | 21/30 | 9/30 (misses) | 6/30 |
| near_decision | 12 | 6/12 | 6/12 | 6/12 (misses) | 0/12 |

Checklist answers (the questions stop at the first n, so a later check is not asked):

| Group | Answered with checklist | Failed job family | Failed seniority | Failed location | All three y (no experience question in this pass) |
|---|---|---|---|---|---|
| close_call_keep | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 |
| random_reject | 30/30 | 10/30 | 3/30 | 8/30 | 9/30 |
| near_decision | 12/12 | 4/12 | 0/12 | 2/12 | 6/12 |

Source: `audit/audit-v1-facts.md`, both tables. The 15 errors, by the first reason in the filter's output: exclusion term 6, no role word 5, known nonmatching location 3, E01 1 (`audit/audit-v1-stats.json`, `groups.*.errors`). Each error is listed with its title, location, filter reasons and verdict in `audit/audit-v1-facts.md`, "Filter errors".

The close_call_keep and near_decision groups are the whole of their pools, not samples, so no sampling interval applies to them: 0 of the 3 kept postings and 6 of the 12 role-matched rejects were judged against the filter.

## 3. The random rejects: miss rate and its exact interval

- Misses: 9 of 30 random rejects were judged relevant. Rate 9/30 = 0.3000.
- Exact (Clopper-Pearson) 95% interval: [0.1473, 0.4940] (`jobwatch/stats.py`, bisection on exact binomial sums; `audit/audit-v1-facts.md`).
- Independent recomputation: lower 0.147345, upper 0.493959 (`scripts/clopper_pearson_check.py`, beta quantiles from a continued-fraction incomplete beta function, no shared code; `audit/audit-v1-ci-check.txt`). The two agree to 4 decimals; `tests/js3/test_js3_stats.py` checks them against each other for 8 (k, n) pairs and against the closed forms for k = 0 and k = n.
- Sample size: n = 30, drawn from a frame of 1242 rejects (all v1 rejects outside the held-out set). The run has 1282 rejects; the 40 held-out postings, all rejected by v1, are outside the frame.
- As a count: the interval times the frame is 183.0 to 613.5, so between about 183 and 614 of the 1242 rejects in the frame would be judged relevant by the same verdicts, at 95% confidence, if the 30 are representative of the frame (`audit/audit-v1-facts.md`).
- Earlier passes, for the record: 15/30, [0.3130, 0.6870] (commit 9a055be); 14/30, [0.2834, 0.6567] (commit 0ffa01e).

## 4. OVERRIDEs

9 rows have an override_reason (`audit/audit-v1-stats.json`, `overrides`; listed with their reasons in `audit/audit-v1-facts.md`): 3 close_call_keep (reasons "Works with location", "yes", "yes") and 6 random_reject (reasons "location", "loation", "location", "Locaition and language", "Loc", "position"). In all 9 the overriding label is the same label the three checks give (`label.derive` on the row's check columns, compared with its verdict in `audit/audit-v1.csv` at 65c9863), so no OVERRIDE changes a verdict.

## 5. Relevant verdicts where a mechanical reading of FILTER.md section 0 differs

Not applied to this pass: every row was answered with the checklist, and by Deepak's decision (commit 000a284) `audit-stats` does not run this check on checklist rows. For the earlier passes, the check listed 18 of 24 (commit 9a055be) and 16 of 23 (commit 0ffa01e) relevant verdicts.

## 6. False-friend candidates

Every positive match (a role, location or topic rule) in an audited posting judged not_relevant: 32 matches in 12 postings (`audit/audit-v1-stats.json`, `false_friend_candidates`; each with its span, quote and sentence in `audit/audit-v1-facts.md`). By rule: T01 Python 8, T06 Machine Learning 6, L02 New York 4, R05 Data Scientist 4, T12 Inference 4, R01 Machine Learning Engineer 2, T05 scikit-learn 2, L05 Remote 1, L04 Seattle 1.

Sentences in which a candidate matched, quoted from the facts file:
- T12 "inference": "Applying probability distributions, statistical inference, and hypothesis testing to quantify uncertainty and evaluate business outcomes" (greenhouse:stripe:8194283 and 8194285); "... machine learning, statistical modeling, causal inference, optimization, experimentation, and all forms of analytics." (greenhouse:stripe:5601879 and 8043052).
- T01 "Python": "Experience coding in programming languages, such as Java, C++, Python, TypeScript, JavaScript, or similar languages." (lever:palantir:f221738b-e97c-4ce3-a12a-17ada2b855e4); "Python, R, Matlab, SQL) is a plus." (lever:palantir:79c3f906-622b-4261-8fc6-8af0028caa27).
- R05 "Data Scientist" in the titles "Data Scientist" (greenhouse:stripe:5601879, 8043052) and "PhD Data Scientist, Intern" (greenhouse:stripe:8194283, 8194285).

All 12 postings were rejected by v1 for other reasons, so none of these matches changed a decision in this sample.

## 6b. Rule changes measured on the audit rows (Phase 3d)

Five candidate changes, each one change to v1, measured with `python -m jobwatch measure-change` on the 45 audit rows only (never the held-out set) against the final verdicts, and decided by Deepak's criterion set at Gate 3b before measuring: adopt only if the change fixes at least one filter error and creates none (`audit/changes/C1.md` to `C5.md`; FILTER.md section 8).

| Change | Errors on the 45 rows, v1 → change | Fixed | Created | Result |
|---|---|---|---|---|
| C1: "Forward Deployed" as an exclusion term | 15 → 16 | 0 | 1 (the kept "Forward Deployed AI Engineer", New York, judged relevant) | rejected |
| C2: title role patterns R11-R14 | 15 → 15 | 0 | 0 | rejected |
| C3: T12 "Inference" → "model inference" | 15 → 15 | 0 | 0 | rejected |
| C4: location "N/A" read as missing | 15 → 15 | 0 | 0 | rejected |
| C5: "Internship" as an exclusion term | 15 → 15 | 0 | 0 | rejected |

C2's patterns, against the audited titles (`audit/changes/C2.md`): "Software Engineer, Machine Learning", "Engineer, Machine Learning" and "Software Engineer, AI" match no audited title; "Machine Learning" matches 8 titles, all of which already match R01 "Machine Learning Engineer". No audit miss has a title of the form the patterns describe. C5's "Internship" matches 2 audited titles, both already rejected. C4's one "N/A" row (Staff Machine Learning Engineer, Radar) is already rejected by X02 Staff.

No change was adopted, so the final filter version is v1.

## 7. What this sample can honestly show

Of 30 random rejects (drawn from 1,242 rejects outside the held-out set), I judged 9 relevant, so v1 missed 9 of 30. The exact 95% interval for the miss rate among rejects is 14.7% to 49.4%, which is roughly 183 to 614 of the 1,242 rejects. With only 30 rows, the sample can say that v1 misses a substantial share of relevant postings; it cannot say which rule causes most misses, and it says nothing about the held-out set. The near-decision group points the same way: 6 of the 12 role-matched gate rejects were relevant to me. The interval rests on my third verdict pass (65c9863), in which 15 checklist answers contradict the question wording (section 1). I did not fix them, so the true miss rate could be lower or higher than these numbers; I read them as a sign that v1 is too strict, not as a measurement I would defend to one decimal.

## 8. The named false friend

My false friend is T12 "inference": it matched "statistical inference" and "causal inference", which are about statistics, not serving models. It changed no decision in v1. It matched 8 of the 45 audited postings: the 2 kept ones have 6 topic words each and would be kept without it, and the 6 rejected ones were rejected by a gate.

I first also named R03 "AI Engineer" inside "Forward Deployed AI Engineer", because FILTER.md section 1's notes say forward-deployed roles are not target roles. My own final verdicts disagree: I judged all four Forward Deployed postings relevant (65c9863), and my section 0 labeling rule does not mention forward-deployed roles. So R03 is not a false friend by my verdicts. The disagreement is between my section 1 note and my judgment, and I have not resolved it.

## 9. Rule decisions after this audit

Five candidate changes (C1 to C5, proposed in the claude.ai chat and sent by me) were measured by Claude Code on the audit rows only, one at a time, and each was decided by the criterion I set at Gate 3b: adopt only if it fixes at least one filter error and creates none. All five were rejected. C1 ("Forward Deployed" as an exclusion) created one new error, because I judged those postings relevant; C2 to C5 fixed none, and C2 changed no decision: R11 to R13 matched no audited title, and R14 'Machine Learning' matched 8 audited titles, 4 of them misses, all already matched by R01. The final filter is v1.

Among the 9 random-reject misses, "no role word" is the most common first reason (5 of 9). Across all 15 misses, an exclusion term leads (6), then no role word (5), location (3) and E01 (1). Several exclusion-term misses are rows where my answers contradict my own rule (for example Manager or Intern titles judged relevant), so some of these misses may be my label errors rather than filter errors.
