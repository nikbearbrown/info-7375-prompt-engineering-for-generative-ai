# SHORTLIST.md — source-grounded shortlist (Chapter 7)

2026-11-20. Labels, quotes and notes are mine (Swathi Baba
Eswarappa), entered as described under "Labeling provenance". Claude Code
prepared the claims and evidence, applied the approved recommendation rule to
my labels, and drafted this report.

**Sources**
- The plan: `shortlist/SHORTLIST-PLAN.md`, commit `534c517`.
- The claims and my labels: `shortlist/CLAIMS.csv`, commit `f4dadb2`.
- The filter verdicts:
  `runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json`, filter
  v1.1 applied to the saved LIVE run of 2026-11-17.
- Persona: Priya Nair (fictional), in `persona/`.

## Summary

| Posting | Filter v1.1 verdict and score | Labels (supported / insufficient / contradicted) | Evidence-based recommendation | Triggering step |
|---|---|---|---|---|
| databricks 6865698002 | shortlisted, 6 | 5 / 1 / 0 | needs human check | step 3: R6 insufficient |
| databricks 6865704002 | shortlisted, 5 | 4 / 1 / 0 | needs human check | step 3: R6 insufficient |
| stripe 8128744 | shortlisted, 5 | 4 / 1 / 0 | needs human check | step 3: R6 insufficient |
| stripe 8212508 | shortlisted, 5 | 4 / 1 / 0 | needs human check | step 3: R6 insufficient |

- **Totals:** 21 claims, with 17 supported, 4 insufficient and 0
  contradicted.
- **No posting is an "evidence-supported fit".** None of the four postings
  says anything about visa sponsorship or F-1 OPT, so every one needs a human
  check.
- **The filter verdicts stand.** All four stay "shortlisted"; this report
  does not change them.

## Claims per posting
Every quote below is copied from `shortlist/CLAIMS.csv` and appears exactly in
the posting's reading file. "(none)" means I gave no quote; for insufficient
claims, the note says what evidence is missing.

### databricks 6865698002 — Software Engineer - New Grad (2027 Start)

- **Location:** Bellevue, Washington; Mountain View, California; San Francisco, California; Vancouver, Canada
- **Reading file:** `audit/read/databricks-6865698002.txt`
- **Filter v1.1 (unchanged):** shortlisted, score 6 (role 3 + early 2 + topics 1)
- **My labels:** supported 5, insufficient 1, contradicted 0
- **Evidence-based recommendation:** **needs human check** (step 3: R6 insufficient)
- **R3/R7 caveats:** none

| Claim ID | Rule | Claim | My label | My quote | My note |
|---|---|---|---|---|---|
| databricks-6865698002-R1 | R1 | Role match: title names Software Engineer, New Grad (a target role) | supported | "Software Engineer - New Grad (2027 Start)" | The title explicitly names Software Engineer, New Grad, matching a target role. |
| databricks-6865698002-R3 | R3 | The title names no seniority or internship term | supported | "Software Engineer - New Grad (2027 Start)" | The claim concerns the complete title text, quoted in full, which contains no senior/staff/lead seniority term or internship term. |
| databricks-6865698002-R4 | R4 | The job is in the US: location names California, Washington | supported | "Bellevue, Washington; Mountain View, California; San Francisco, California; Vancouver, Canada" | The location header explicitly lists Bellevue, Washington, Mountain View, California, and San Francisco, California. |
| databricks-6865698002-R5 | R5 | The job is early-career: the posting gives explicit early-career evidence | supported | "You will graduate in fall 2026 or spring 2027 with a degree in Computer Science, Engineering, or related subject" | The posting explicitly targets new grads graduating in fall 2026 or spring 2027. |
| databricks-6865698002-R6 | R6 | The posting states no U.S. citizenship, security clearance or 'will not sponsor' requirement | insufficient | (none) | The posting contains no U.S. citizenship, security clearance, or 'will not sponsor' restriction (only a standard export-control discretion clause). However, it does not explicitly establish visa sponsorship availability or F-1 OPT eligibility. |
| databricks-6865698002-R7-python | R7 | The job's responsibilities or requirements name the topic word 'Python' | supported | "You have implementation skills with a general purpose program language, such as Python, Java, or C++" | Python is explicitly listed under 'What we look for' as a general-purpose programming language. |

### databricks 6865704002 — Software Engineer - New Grad, Distributed Data Systems (2027 Start)

- **Location:** Bellevue, Washington; Mountain View, California
- **Reading file:** `audit/read/databricks-6865704002.txt`
- **Filter v1.1 (unchanged):** shortlisted, score 5 (role 3 + early 2 + topics 0)
- **My labels:** supported 4, insufficient 1, contradicted 0
- **Evidence-based recommendation:** **needs human check** (step 3: R6 insufficient)
- **R3/R7 caveats:** none

| Claim ID | Rule | Claim | My label | My quote | My note |
|---|---|---|---|---|---|
| databricks-6865704002-R1 | R1 | Role match: title names Software Engineer, New Grad (a target role) | supported | "Software Engineer - New Grad, Distributed Data Systems (2027 Start)" | The title explicitly names Software Engineer - New Grad, Distributed Data Systems, matching a target role. |
| databricks-6865704002-R3 | R3 | The title names no seniority or internship term | supported | "Software Engineer - New Grad, Distributed Data Systems (2027 Start)" | The claim concerns the complete title text, quoted in full, which contains no senior/staff/lead seniority term or internship term. |
| databricks-6865704002-R4 | R4 | The job is in the US: location names California, Washington | supported | "Bellevue, Washington; Mountain View, California" | The location header explicitly lists Bellevue, Washington and Mountain View, California. |
| databricks-6865704002-R5 | R5 | The job is early-career: the posting gives explicit early-career evidence | supported | "You will graduate in Fall 2026 or Spring 2027 with a degree in Computer Science, Engineering, or related subject" | The posting explicitly targets new grads graduating in Fall 2026 or Spring 2027. |
| databricks-6865704002-R6 | R6 | The posting states no U.S. citizenship, security clearance or 'will not sponsor' requirement | insufficient | (none) | The posting contains no U.S. citizenship, security clearance, or 'will not sponsor' restriction (only a standard export-control discretion clause). However, it does not explicitly establish visa sponsorship availability or F-1 OPT eligibility. |

### stripe 8128744 — Software Engineer, New Grad

- **Location:** San Francisco, Seattle, New York
- **Reading file:** `audit/read/stripe-8128744.txt`
- **Filter v1.1 (unchanged):** shortlisted, score 5 (role 3 + early 2 + topics 0)
- **My labels:** supported 4, insufficient 1, contradicted 0
- **Evidence-based recommendation:** **needs human check** (step 3: R6 insufficient)
- **R3/R7 caveats:** none

| Claim ID | Rule | Claim | My label | My quote | My note |
|---|---|---|---|---|---|
| stripe-8128744-R1 | R1 | Role match: title names Software Engineer, New Grad (a target role) | supported | "Software Engineer, New Grad" | The title explicitly names Software Engineer, New Grad, matching a target role. |
| stripe-8128744-R3 | R3 | The title names no seniority or internship term | supported | "Software Engineer, New Grad" | The claim concerns the complete title text, quoted in full, which contains no senior/staff/lead seniority term or internship term. |
| stripe-8128744-R4 | R4 | The job is in the US: location names New York | supported | "San Francisco, Seattle, New York" | The location header explicitly lists New York (along with San Francisco and Seattle). |
| stripe-8128744-R5 | R5 | The job is early-career: the posting gives explicit early-career evidence | supported | "A Bachelor’s or Master’s degree in computer science or a directly related field, obtained by summer 2027, or equivalent work experience; New grad candidates should have no more than 18 months of professional experience (excluding internship experience)." | The posting explicitly targets new grad candidates graduating by summer 2027 with no more than 18 months of professional experience. |
| stripe-8128744-R6 | R6 | The posting states no U.S. citizenship, security clearance or 'will not sponsor' requirement | insufficient | (none) | The posting contains no mention of U.S. citizenship, security clearance, or sponsorship restrictions. However, it does not explicitly establish visa sponsorship availability or F-1 OPT eligibility. |

### stripe 8212508 — Software Engineer, Early Career — Immediate Start

- **Location:** San Francisco, Seattle, New York
- **Reading file:** `audit/read/stripe-8212508.txt`
- **Filter v1.1 (unchanged):** shortlisted, score 5 (role 3 + early 2 + topics 0)
- **My labels:** supported 4, insufficient 1, contradicted 0
- **Evidence-based recommendation:** **needs human check** (step 3: R6 insufficient)
- **R3/R7 caveats:** none

| Claim ID | Rule | Claim | My label | My quote | My note |
|---|---|---|---|---|---|
| stripe-8212508-R1 | R1 | Role match: title names Software Engineer, Early Career (a target role) | supported | "Software Engineer, Early Career — Immediate Start" | The title explicitly names Software Engineer, Early Career, matching a target role. |
| stripe-8212508-R3 | R3 | The title names no seniority or internship term | supported | "Software Engineer, Early Career — Immediate Start" | The claim concerns the complete title text, quoted in full, which contains no senior/staff/lead seniority term or internship term. |
| stripe-8212508-R4 | R4 | The job is in the US: location names New York | supported | "San Francisco, Seattle, New York" | The location header explicitly lists New York (along with San Francisco and Seattle). |
| stripe-8212508-R5 | R5 | The job is early-career: the posting gives explicit early-career evidence | supported | "New grad candidates should have no more than 18 months of professional experience (excluding internship experience)" | The posting explicitly states it is an Early Career role for new grad candidates with no more than 18 months of professional experience. |
| stripe-8212508-R6 | R6 | The posting states no U.S. citizenship, security clearance or 'will not sponsor' requirement | insufficient | (none) | The posting contains no mention of U.S. citizenship, security clearance, or sponsorship restrictions. However, it does not explicitly establish visa sponsorship availability or F-1 OPT eligibility. |

## Relevance versus entailment
- **A supported claim isn't the same as a fit.** A claim can be fully
  supported by the posting while the posting still does not fit the person.
  The claims test what the posting says, not whether it fits Priya.
- **The two Databricks postings.** R5's claim is "The job is early-career:
  the posting gives explicit early-career evidence". I labeled it supported
  for both, with these quotes:
  - databricks 6865698002 (`audit/read/databricks-6865698002.txt`, line 19):
    "You will graduate in fall 2026 or spring 2027 with a degree in Computer
    Science, Engineering, or related subject"
  - databricks 6865704002 (`audit/read/databricks-6865704002.txt`, line 25):
    "You will graduate in Fall 2026 or Spring 2027 with a degree in Computer
    Science, Engineering, or related subject"
- **Priya graduated before that window.** The persona file
  `persona/priya-nair.resume.example.json`, `education[0]`, has
  `"end_date": "2025-12"` and `"status": "completed"` (MS, Information
  Systems, Northeastern University). `persona/priya-nair.targets.json` has
  `visa.current_status`: "F-1 OPT (post-completion, year 1)".
- **So the claim is supported, but the fit isn't.** The quotes entail that
  the job is early-career. They also state a graduation window, fall 2026 or
  spring 2027, that Priya's December 2025 graduation falls outside. The
  filter scored both postings for the early-career evidence (+2) and has no
  rule that compares a graduation window with the persona.
- **The audit's "university" false friend.** This is the same gap
  between matching a word and establishing a fact.
  - In v1, R5 counted the word "university" anywhere in a description as
    early-career evidence. The JS3 audit scan (`audit/AUDIT-REPORT.md`,
    section G) found it in stripe 8186445: "…working collaboratively on
    multi-person coding projects (in a university or professional
    setting)."
  - That sentence describes where experience can come from, not the job's
    level. The same sentence appears in both shortlisted Stripe postings
    (`audit/read/stripe-8128744.txt`, line 24;
    `audit/read/stripe-8212508.txt`, line 27). In the v1 results
    (`runs/filter-2026-11-17T21-47-06-167440-0500/results.json`), it was one
    of the R5 quotes for both.
  - The v1.1 change log entry "University false-friend correction (D3)" in
    FILTER.md (commit `4a6dcfb`) now counts "university" only in the title.
    Both Stripe postings still pass R5 in v1.1, on their titles and the
    "New grad candidates…" line.

## Abstention rule and a counterexample
### The approved rule
From `SHORTLIST-PLAN.md`. The requirement claims are R4 location, R5
experience and R6 work authorization. The first row that applies decides:

| Step | Condition | Recommendation |
|---|---|---|
| 1 | Any claim is contradicted (any rule) | do not recommend |
| 2 | Any R1 role claim is insufficient | needs human check |
| 3 | Any R4, R5 or R6 claim is insufficient | needs human check |
| 4 | Otherwise | evidence-supported fit |

- **R3 and R7 don't decide the result.** An insufficient R3 or R7 claim is
  disclosed as a caveat but does not, on its own, change the
  recommendation.
- **"Evidence-supported fit" is not a guarantee.** It does not mean
  guaranteed employment eligibility, visa sponsorship or F-1 OPT
  eligibility.

### What the rule can see
- **It labels only what the filter says.** The rule works only on claims the
  filter generates: one per rule (R1, R3, R4, R5, R6) and one per matched R7
  topic word.
- **Other requirements never become claims.** A mandatory requirement that
  no rule reads cannot be labeled contradicted, so it cannot trigger "do not
  recommend" or "needs human check".

### Counterexample: dated requirements outside every rule
- **Stripe 8212508**, "Software Engineer, Early Career — Immediate Start"
  (`audit/read/stripe-8212508.txt`):
  - line 10: "This role is for applicants actively looking to start before
    December 1, 2026."
  - line 23, under "Minimum requirements": "Must be available to start
    full-time before December 1, 2026"
  - line 24, under "Minimum requirements": "A Bachelor’s or Master’s degree
    in computer science or a directly related field, obtained by summer 2026,
    or equivalent work experience"
- **The Databricks postings 6865698002 and 6865704002** state the graduation
  window quoted above, fall 2026 or spring 2027.

None of R1–R7 reads a graduation window, a degree deadline or a start-by
date.

**What is known and what is not, for Priya:**
- **Known mismatch: the Databricks graduation window.** Her degree was
  completed in 2025-12, outside the fall 2026 / spring 2027 window.
- **Known: Stripe 8212508's degree deadline is met.** A degree completed in
  2025-12 is "obtained by summer 2026". The same holds for stripe 8128744's
  "obtained by summer 2027" (`audit/read/stripe-8128744.txt`, line 22).
- **Unknown: start-date availability.** No persona file states when Priya
  can start, so whether she meets "Must be available to start full-time
  before December 1, 2026" cannot be determined. For timing: the posting was
  collected on 2026-11-17, 14 days before that date, and this report is
  dated 2026-11-20.

**Hypothetical limitation (not a measured result):**
- **The result here.** All four postings are "needs human check" because R6
  is insufficient, so these extra requirements did not change any
  recommendation.
- **What would happen if R6 were supported.** Suppose a posting like these
  had an explicit statement supporting sponsorship or OPT, and every other
  evaluated claim stayed supported. The rule would then reach step 4,
  "evidence-supported fit". It would do so while the posting still had a
  graduation window Priya does not meet, or a start-by date she may not
  meet.
- **Why.** The rule would not detect these requirements, because they are
  never extracted as claims.
- **This is an illustration of the rule's scope.** It was not observed on
  these postings.

## Known limitations
- **R5 doesn't read months.**
  - Neither `job_filter.py` nor FILTER.md handles experience stated in
    months.
  - Both Stripe postings say "New grad candidates should have no more than
    18 months of professional experience (excluding internship experience)".
    That is a **maximum** (a cap on experience), not a **required minimum**.
    R5's rejection rule is about required experience.
  - The filter never parsed the 18 months. R5 passed on early-career title
    wording ("New Grad", "Early Career") and the "New grad candidates" line.
  - I kept my supported R5 labels for both Stripe postings. A month-based
    requirement, such as "at least 18 months", would currently be missed by
    R5.
- **Empty location isn't documented.** When the location is empty, the code
  makes R4 "cannot tell" and so abstains (`job_filter.py:259`, since
  `6e6b4bf`). FILTER.md does not say so. This is recorded as a
  documentation gap; neither file is changed.
- **Evidence-supported fit is not a guarantee.** It does not mean guaranteed
  employment eligibility, visa sponsorship or F-1 OPT eligibility. The R6
  claim only says no restriction wording was found, which is why all four R6
  claims are insufficient.
- **Requirements outside R1–R7 are not checked.** Graduation windows, degree
  deadlines and start-by dates are examples (see the counterexample above).
- **Four postings, one batch.** This is the v1.1 shortlist of one saved
  collection (2026-11-17). The batch was also used to build v1.1, so it is
  development data, not held-out evidence.
- **Multi-location postings.** R4 is supported when the location names a US
  place, even when other locations are outside the US. For example,
  databricks 6865698002 also lists "Vancouver, Canada".

## Labeling provenance
- **Who wrote the sheet.** Claude Code prepared the 21 claims and filter
  quotes (`1442650`), and did not suggest labels.
- **My first labels.** I entered the initial labels, quotes and notes.
- **The R6 correction.**
  - Claude Chat pointed out that my four R6 labels conflicted with the
    approved absence-of-evidence rule and the quote requirement.
  - ChatGPT reviewed the labels and recommended the same correction.
  - I accepted the feedback and relabeled the four R6 claims as
    insufficient.
- **Other feedback I received and entered:**
  - from Claude Chat and ChatGPT, on documenting the R3 reasoning: that R3
    concerns the complete title text, quoted in full;
  - from Claude Chat and ChatGPT, on clarifying the four R6 notes to state
    the missing evidence about sponsorship and F-1 OPT eligibility. I
    reviewed it and entered the revised notes.
- **Checking.** Claude Code checked the completed sheet and did not change
  any label, quote or note. It checked that the label values are valid, the
  quotes are exact and the original columns are unchanged.
- **These labels are my judgments, formed with the AI feedback described
  above. They are not independent or blind human labels.**
