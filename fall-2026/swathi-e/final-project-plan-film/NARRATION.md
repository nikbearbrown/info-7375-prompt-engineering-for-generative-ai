# Final Project Film — Narration

Swathi Baba Eswarappa · INFO 7375 · Revised 2026-11-22 · **Status: approved structure; final text pending my review**

Readable text. `beat_sheet.json` holds the same words with numbers and acronyms spelled out for the narration voice.

## Part 1 — Executive summary

**B01** (framing). My final project is a supervised job-search agent for international students. It finds early-career jobs on company job boards, sets aside the ones that don't fit, and for each job that remains, shows the evidence a student needs before applying, including whether the employer has a public record of sponsoring work visas.

**B02** (framing). It matters because students on OPT have limited time to find work, and many employers won't sponsor. A wrong "this job fits" wastes days. A wrong "they sponsor" can cost much more. So the agent shows its evidence, says when it isn't sure, and doesn't apply or send anything on its own.

## Part 2 — Introduction

**B03** (framing). Good tools already exist. USCIS publishes an H-1B Employer Data Hub with approval and denial counts by employer, back to 2009. The Department of Labor publishes case-level disclosure files every quarter. Sites like MyVisaJobs and H1BGrader turn this data into employer search, and browser extensions like Interstride's flag sponsors on LinkedIn and Indeed.

**B04** (framing). These tools answer an important question well: has this employer sponsored before? I'm adding a narrower one: what does this posting say, and how does that compare with the employer's record? My agent shows both, cites each, flags differences, and leaves the decision to a person.

## Part 3 — Methods

**B05** (completed). This builds on completed work. In Job-Search Agents 1 to 3, I wrote filter rules before code, and collected 1,832 public postings from Databricks, Stripe and Plaid on November 17. Version 1 shortlisted 4. I reviewed 30 random rejections and judged none relevant, though a sample that small can't rule out a miss rate up to about ten percent. Version 1.1 then fixed gaps the audit found, changing 7 verdicts; the shortlist stayed at 4.

**B06** (planned). The new data is the Labor Department's disclosure files. An employer must get a Labor Condition Application certified before filing an H-1B petition, so these records show historical sponsorship activity, not a visa approval or a promise for this job. I'll count only certified H-1B cases, list withdrawn certifications separately, and leave out H-1B1 and E-3. If a posting says it won't sponsor, that comes first; the employer's history is context.

**B07** (planned). The agent will run as a loop: collect, filter, match, check, record, stop. Outside sources are read-only; it writes only to its own memory, audit log, and decision records. Each run has a fixed budget, and stops when the queue is empty, the budget is spent, or an error limit is hit, not because the model says it's done.

**B08** (planned). I'll approve, refuse, or defer each job, and each decision is tied to the exact evidence I saw. The student in this project, Priya Nair, is fictional. Resources: my university's Claude Code seat covers model access, within usage limits; job-board APIs need no key; government data is free; my laptop is enough. Details are in my appendix.

## Part 4 — Evaluation

**B09** (planned). First, I'll hand-label 60 employers: 20 for development, and 40 locked away as a held-out test, including employers with no qualifying records. Missed matches count only employers that truly have records; the rest are checked for false matches.

**B10** (planned). A separate checker will re-verify each claim against the raw files: the right employer, the right source, and whether the record supports the sentence. I'll trigger one wrong match on purpose to show it gets caught, plus at least five deliberate failure cases and tests that try forbidden actions.

**B11** (planned). My proposed pass line: zero wrong matches, zero unsupported claims, zero unauthorized actions, every planted difference flagged, and at most two missed matches. After any fix, the first held-out result stays on record; a re-run is only a regression test. The employers are chosen on purpose, so this tests my rules, not a general error rate. These are targets, not results.
