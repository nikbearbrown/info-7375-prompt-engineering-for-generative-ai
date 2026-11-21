# FRICTIONAL.md — Job-Search Agent 3

Written by Swathi Baba Eswarappa. ChatGPT provided reference drafts and
wording assistance, which I revised and approved; Claude Chat reviewed the
entries for factual consistency (see `SOURCES.md`).

## 1. Fixing the optional qualification rule

- **Date:** November 19, 2026
- **What happened:** While updating the experience filter to recognize optional qualifications, the existing `W3` test failed because the new rule treated words like "ideally" as making an entire experience requirement optional.
- **What I noticed / why it mattered:** A job can require three or more years of experience while only saying a specific domain is "ideal." Treating the whole sentence as optional could let roles requiring more experience slip past the experience check.
- **What I changed:** I approved scoping the optional check to the same clause and dropping "ideal" and "ideally" from the optional keywords, adding a new regression test before updating the code.
- **Rejected:** I rejected Option B (editing the existing test to fit the new rule) because the code needed to satisfy the original requirement, not have the test weakened to pass.
- **Evidence:** FILTER.md R5 addendum, TEST-PREDICTIONS.md R5l, commits c0790a4, bf291f2, 2c3ef12.

## 2. Protecting the held-out experiment

- **Date:** November 19, 2026
- **What happened:** While setting up the held-out dataset, we realized the existing collector still ran the JS1 title rule and would automatically generate relevance verdicts for new postings.
- **What I noticed / why it mattered:** Seeing pre-generated verdicts before labeling the postings myself would bias my decisions and compromise the independence of the held-out check.
- **What I changed:** I approved temporarily moving the state file so the collector treated the run as a clean baseline without generating verdicts; Claude Code then restored the original state file unchanged after the collection.
- **Rejected:** I rejected running the collector normally and hiding its output, since the verdicts would still be generated and saved in the trace.
- **Evidence:** HELDOUT-PLAN.md, commits 4cbb88c, 831d6af.

## 3. Correcting the R6 shortlist labels

- **Date:** November 20, 2026
- **What happened:** I originally marked all four R6 shortlist claims as `supported` because the postings didn't mention citizenship, security clearance, or a "will not sponsor" restriction. Claude Chat and ChatGPT flagged that this went against the evidence rules I had approved earlier.
- **What I noticed / why it mattered:** Not mentioning a restriction isn't the same as confirming visa sponsorship or F-1 OPT eligibility—I was treating missing information as positive proof.
- **What I changed:** After re-checking the evidence rules and the original postings, I updated all four R6 labels to `insufficient` and expanded the notes to explain what was missing.
- **Rejected:** I rejected keeping the original `supported` labels because they couldn't be backed up by an actual quote from the text.
- **Evidence:** shortlist/CLAIMS.csv (f4dadb2), shortlist/SHORTLIST.md, Labeling provenance (bf15eaf).

## 4. Questioning the external server recommendation

- **Date:** November 20, 2026
- **What happened:** Claude Chat initially suggested evaluating version `2.2.0` of the Filesystem server because of how long it had been out, but ChatGPT caught a security advisory affecting versions under `2.3.0`, which Claude Chat then verified.
- **What I noticed / why it mattered:** A release being older doesn't make it safer—I needed to check actual security advisories rather than relying on release age alone.
- **What I changed:** I switched to evaluating version `2.4.0` instead, and since my local Node.js version didn't meet its requirement, I chose to have Claude Code evaluate the published package by inspecting its compiled JavaScript rather than installing or running it.
- **Rejected:** I rejected the original age-based recommendation once the vulnerability was flagged, and I also chose not to upgrade my local Node environment just to run an external server.
- **Evidence:** tool/EVALUATION.md Section 2.1 and row G1, commit b3eb3dd, advisory GHSA-7m4x-rv66-mxhh.

## 5. Recognizing the limitations of AI-assisted audit labels

- **Date:** November 18, 2026
- **What happened:** I labeled the first four audit postings before looking at any AI draft, but for rows 5–48 I reviewed the postings after seeing ChatGPT’s suggested judgments.
- **What I noticed / why it mattered:** Even though I read every posting and made the final call myself, seeing suggested labels upfront could nudge my thinking—meaning the full 48-row set couldn't count as a blind, independent evaluation.
- **What I changed:** I logged how each row was judged, preserved the original audit records, and disclosed that limitation in the audit report, then created a fresh held-out sample for Chapter 9 (and documented the guidance I got on its first row).
- **Rejected:** I decided against treating the AI-assisted audit labels as independent held-out evidence when evaluating the updated filter.
- **Evidence:** audit/HUMAN_AUDIT.csv (fed055f), audit/AUDIT-REPORT.md Section F (815064e), HELDOUT-PLAN.md (4cbb88c), heldout/HELDOUT.csv (b09f9ce).
