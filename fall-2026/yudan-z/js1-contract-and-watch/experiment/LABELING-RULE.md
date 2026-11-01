# Labeling rule (written before any posting was labeled)

## Executive summary

These are the instructions I followed when I hand-labeled the 20 real postings for the prompt experiment. I deliberately did **not** reuse the contract's eight checks. The hand label asks a different question, a person's judgment, so the experiment measures how close Claude comes to a person's call, not just whether it can follow a checklist.

- **Written:** 2026-10-30, before labeling.
- **Authorship:** the criterion is mine; Claude wrote it up in English.

## The question

> **Would I, as this persona (a new master's graduate in Information Systems on F-1 OPT, targeting data/analytics work), spend application time on this posting?**

Original wording (mine): 入门级的数据或分析岗位、在美国、不排除签证担保 ("an entry-level data or analytics role, in the US, that does not rule out visa sponsorship").

## Label `relevant` when all three hold

1. **Entry-level data or analytics work.** The day-to-day work is analysing data (analyst, BI, analytics, data science for new grads), judged from the title **and** the description, not the title alone. Entry-level means a new graduate could reasonably be hired, so a stated minimum of about 2 years or less, or none stated, with no senior title.
2. **In the US.** The role is located in, or can be done from, the United States.
3. **Sponsorship not ruled out.** The posting does not say it will not sponsor, and does not require citizenship, a green card or a clearance.

Otherwise label `not_relevant`.

## How I recorded labels

- One label per posting, plus one short reason in my own words.
- I labeled from the title, location and description shown on the labeling sheet (plus the link if I needed more). I did not look at the rule's verdict or Claude's verdict first.
- The 20 postings were split into development (10) and held-out (10) by a fixed random seed **before** labeling, so I could not choose which postings went where.
