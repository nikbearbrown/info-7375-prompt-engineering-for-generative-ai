# The reject audit (Chapter 7)

*Drafted by Claude Code on 2026-11-25. The hand verdicts are Shreyash's: 70 postings, typed into the
session between 17:53 and 18:04 EST and transcribed word for word into `labels/hand-verdicts.jsonl`.
They were frozen by sha256 (`labels/hand-verdicts.sha256`, commit `667a2932`) before they were compared
with the filter or with Claude. The generated tables are in `results/audit-v1.md`
(`python3 -m js3 audit`). The decisions in section 5 are Shreyash's. How each verdict was given,
including the six answers that changed, is in `labels/hand-verdicts-provenance.md`. That file was added
after the independent review of 2026-11-25 found that two first answers were missing from the record.*

## 1. What the filter saw and decided

- **What the agent collected:** 789 postings in all.
  - **637** came from today's live run (`runs/20261125T220655Z`, 17:06 EST): oscar 178, klaviyo 124,
    linear 30, palantir 305.
  - **152** were collected in JS2's three runs and have closed since.
  - `oscarhealth-doesnotexist` failed (not-found), and its postings are unknown; the agent does not
    report it as having zero. `whoop` returned an empty list.
- **Filter v1:** kept 5, said "I cannot tell" about 0, and rejected 784, of which **44 are closest
  calls** (fail exactly one rule).
- **Compared with JS2's rule v2 rev 3** (`results/whatif-v1.json`, `_more.v1_vs_js2_rule`): the same verdict on all 789. Only the reasons changed: for
  example, 122 location results became "cannot tell". JS2 had failed 84 of them and passed 38:
  - 29 Oscar ads whose office tag names one state, such as "Remote (Texas)", while the ad's own state
    list includes Massachusetts. JS2 trusted the list; answer 6a calls the two a disagreement.
  - 8 postings where the location field and the office list disagree about Boston.
  - 1 other.

  Every one of the 122 also fails another rule.

## 2. How the sample was drawn

`labels/SAMPLE-PLAN.md` was committed before any verdict, with seed 7375.

| Part | Postings | Supports |
|---|---|---|
| A1 | 30, uniform random from the 763 rejects not held out | **a rate** |
| A2 | 15 closest calls: the 6 outside Palantir not held out, and 9 of the 27 Palantir location-only ones | counts only |
| A3 | 2 of the 5 kept | counts only |
| H | 24 held out for SCORE.md: 3 kept, 11 closest calls, 10 other rejects | the experiments |

One posting is in both A1 and A2, so 46 postings were audited and 24 held out: 70 to label.

- **How they were shown:** all 70 came in one shuffled order, without the filter's verdict or the part
  each posting belonged to. They were summaries that Claude Code wrote in the chat
  (`labels/hand-verdicts-provenance.md`).
- **The one exception:** when Shreyash asked for a double-check of 31, 39 and 49, Claude Code told him
  how the rules read those three postings. Their final answers are therefore not blind.

## 3. How many the filter got wrong

| Part | Agree | Misses (rejected, Shreyash says yes) | False positives (kept, Shreyash says no) |
|---|---|---|---|
| A1 random rejects (30) | 30 | **0** | — |
| A2 closest calls (15) | 13 | **2** | — |
| A3 kept (2) | 1 | — | **1** |
| H held-out (24) | 24 | 0 | 0 |

**The disagreements**, with Shreyash's own reasons:

- **Miss: Software Engineer II - Recommendations** (`klaviyo:7855798003`, Boston, 2+ years). His "yes" came before the double-check, and he kept it.
  - Rule 4 found one skill, Python. The ad names MySQL and Postgres, which are not the whole term "SQL".
  - Shreyash: "I think MySQL and PostgreSQL should count towards Alex's SQL skill. The rule is too strict
    here."
- **Miss: Product Engineer** (`linear:0c7c2e26-…`, remote in North America, 2-5 years, React and
  TypeScript). This is his final answer, given after the double-check. His first answer was "no":
  "Product Engineer is not one of the listed target roles".
  - Rule 1: the title is not one of the nine phrases.
  - Shreyash: "Even though the title is Product Engineer, the actual work matches Alex's full-stack
    skills…"
- **False positive: Software Engineer II (Mobile Developer - Android/Kotlin) - Remote**
  (`klaviyo:7792539003`). This is his final answer, given after the double-check. His first answer was
  "yes", with the doubt: "It passes the written rules, but Android development is the main
  requirement, which is not among Alex's skills".
  - Every rule passed.
  - Shreyash: "The main requirement is Android and Kotlin, which Alex does not have. Just mentioning
    Python and React does not make it a good match."

**What a sample this size can honestly say**

- **Part A1, the only random part:** 0 misses in 30. That is **not** a 0% miss rate.
  - The 95% Wilson interval for the true miss rate among the 763 rejects is **0% to 11.4%**. The
    one-sided 95% upper bound is **9.5%**: up to about **73 missed postings** cannot be ruled out.
  - To bound it below 3%, we would need about 100 random rejects with no miss.
  - The 30 were mostly easy: 29 of them fail two or more rules, and only 1 is itself a closest call.
- **The closest calls (2 of 15) and the kept postings (1 of 2) are not random.** They are not rates,
  and they say nothing about all 44 closest calls or all 5 kept postings. They show where errors live:
  - both misses are closest calls;
  - the one false positive is a kept posting;
  - the 30 random rejects held none.
- **The 18 Palantir closest calls left unlabeled** are counted, not judged. Every labeled one of their
  kind (17 of 17) was a "no".
- **The whole audit describes the four boards that returned postings** (of the six checked), on
  2026-11-09, -10 and -25, for one fictional applicant. Another board, or another week, could fail in ways this sample never saw.

**Where a verdict was influenced, and how:**

- **Item 8.** It was first answered "yes" on an excerpt that left out its requirements. That was a
  Claude Code bug: a curly apostrophe in "What We’re Looking For:". Shreyash changed it to "no" after
  seeing the full section. The bug is fixed test-first (`tests/test_js3_sections_apostrophe.py`), and
  the fix changed no filter result.
- **Items 11 and 20.** Shreyash asked for the full ad and changed "cannot tell" to "yes".
- **Item 31.**
  - His first answer was "no" ("The job is closed"). Claude Code's chat summaries had left out "judge it
    as if it were open".
  - Asked to judge it as if open, he answered "yes" and asked for a double-check.
  - In the double-check, Claude Code told him how Rule 4 reads the ad, and he kept "yes". The final line
    is marked `not_blind`.
- **Items 39 and 49.**
  - He answered 39 "yes" and 49 "no", with notes, and asked for a double-check before they were saved.
  - Claude Code held both answers and told him how the rules read the two postings. It framed the
    label as his judgment, not the rules'.
  - He changed 39 to "no" and 49 to "yes".
  - His first answers never reached the frozen file. They are recorded in
    `labels/hand-verdicts-first-answers.jsonl`, transcribed from the session after the review.
- **Six answers changed in all** (8, 11, 20, 31, 39, 49). The frozen file keeps the first and final
  answers of the first four (74 lines for 70 postings; the last one counts).

**The audit set both ways** (`results/audit-v1.json`, `audit_set_both_ways`):

| Answers used | Agree | Misses | False positives |
|---|---|---|---|
| Final answers (the tables above) | 43 of 46 | 2 (31, 49) | 1 (39) |
| Answers given before any rule explanation (31 yes, 39 yes, 49 no) | 45 of 46 | 1 (31) | 0 |

Two of the three disagreements, the Product Engineer miss and the Android false positive, exist only
in answers given after Claude Code described the rules. The 30 random rejects and the held-out set
contain none of these three postings.

## 4. False friends: words that matched for the wrong reason

Measured by code over all 789 postings. They are listed by how much they mattered.

1. **"Python", "React", "TypeScript" in a kept Android job.**
   - In `klaviyo:7792539003` the three skills that kept the job appear only in "open to picking up new
     technologies (Python, React, AWS)", a "Technologies We Use (not exhaustive)" list, and "React
     Native". The words are right; the reason is wrong.
   - This is the one false friend that changed a verdict: it is the audit's false positive.
   - SHORTLIST.md shows it as the case where relevance is not entailment.
2. **"react", the verb.**
   - "who thrive in ambiguity, react quickly to new stimuli" matched Alex's skill React in 2 Palantir
     Deployment Strategist ads. Rule 4 counts React in 75 postings; in 2 of them it is the verb.
   - It changed no verdict: both ads still name two real skills and fail other rules. JS1 predicted
     this weakness (INTERPRETATIONS.md) without measuring it.
3. **"remote position".**
   - In 36 ads (35 Oscar, 1 Palantir) it matched "the ad says remote", in sentences like "This is a
     remote position, open to candidates who reside in: Dallas, TX."
   - The city and state vary: Dallas, Atlanta, San Francisco, Tempe, Florida.
   - Filter v1 read that as the location tag and the ad disagreeing (answer 6a), and said "cannot
     tell".
   - The same sentence limits the job to one state. The inherited reading counted a residence list
     only when it named two states or more, a number Claude Code set in JS2.
   - It changed no verdict. Decision A4 fixed it in v1.1.

## 5. Rules added, cut or rejected after measuring

Shreyash decided these in FILTER.md section "Version 1.1" (pasted about 18:07 EST, before any v1.1
code). The version log there has one row for each.

| Change | Measured before deciding | Decision |
|---|---|---|
| **A1** add the title phrase "Product Engineer" | fixes 1 audit miss; +1 kept of 789; no held-out posting affected | **Added** |
| **A2** count MySQL, PostgreSQL, Postgres as SQL | fixes 1 audit miss; +1 kept (closed); no held-out posting affected | **Added** |
| **A3** count a skill only where the ad asks for it | fixes the audit's false positive, **creates 2 held-out misses** (Growth, Flows) | **Rejected** |
| **A4** a residence line that names one state is a limit | 0 verdicts; location "cannot tell" becomes "fail" (35 of 36 after two code fixes; see below) | **Added** |
| **A5** minimum skills 1, fitted on the audit labels | +1 audit agreement; ties on the held-out set | **Rejected** |
| **B4** evidence rules: "full-time not stated" passes, marked not stated | all 5 kept were "I cannot tell" only for this | **Added** |

**Measured on the corpus before the labels existed, and not proposed**
(`results/whatif-v1.json`, `_more.filter_changes_corpus`):

- dropping Rule 2: 0 verdicts;
- JS2's reading of Palantir `Dev`: 0 verdicts;
- minimum skills 3: 0 verdicts;
- maximum years 5: +1 posting kept. Checked against the audit labels afterwards, that posting is one
  Shreyash rejected (7+ years), so it would be a false positive.

**Filter v1.1 against the same labels** (`results/filter-v1.1/`, 222 tests pass):

- **Kept:** 7 (5 open). It changes exactly 2 verdicts, the two misses.
- **Audit:** **45 of 46** agree.
  - This is in-sample: A1 and A2 were designed from these audit misses.
  - The Android false positive stays, because Shreyash rejected A3, and a test records it.
- **Held-out:** 24 of 24, but no longer an untouched test: A3 was rejected on these labels.
- **A4's count was first stated wrongly.** Claude Code gave its effect as "36" before running it; the
  first v1.1 code changed 12. Of the other 24:
  - 21 write the state as a code after "reside in" ("TX");
  - 2 write "reside:" without "in" (one of them also with a code);
  - 1 (Palantir, Warsaw) is not a residence line.

  Two test-first fixes brought it to 35 of 36, and FILTER.md carries a dated correction.
