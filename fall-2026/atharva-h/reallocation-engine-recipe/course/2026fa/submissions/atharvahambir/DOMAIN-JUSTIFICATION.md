# Domain justification — a daily board check for entry-level data roles on a short OPT clock

## Executive summary

This page says who the recipe is for, what they can't see without it, and how it changes their day. Each morning it turns "open fifteen job boards and research every posting" into one short report: where to apply, where to network, what to skip. Every number is traced to a record or to the student's own input.

## Who, in exactly what situation

An international MS student hunting **entry-level data roles**: Data Analyst, BI Analyst, Business Analyst, Analytics Engineer, Data Engineer. That means 0–3 years of experience, nothing senior, any US city or US-remote. The student is on **post-completion F-1 OPT with the OPT end date ~90 days out**, holds a **STEM degree with the extension not yet filed**, and so needs an employer that **sponsors H-1B and is enrolled in E-Verify**. They keep a short list of target companies with known Greenhouse or Ashby boards.

## The information asymmetry

From outside, this student can't easily see:
- **Postings:** which of today's postings at *their* companies fit *their* level, location and experience limit, without reading every ad.
- **Sponsorship:** whether a company has a sponsorship record. The public data files it under a legal name ("Robinhood" is `ROBINHOOD MARKETS INC`, 824 approvals), so a miss reads like "doesn't sponsor". Only 1,557 of 30,369 companies carry H-1B history at all.
- **The deadline:** which of **two clocks** ends first, the OPT end date or the unemployment allowance.
- **E-Verify:** whether a sponsor can also support the STEM extension.
- **Networking targets:** which sponsors have nothing open today, and are worth networking into instead.

## How it connects to the engine

| Layer | Use |
|---|---|
| **Job-Ops** | board APIs via the repo's `greenhouse-watch` fetcher; being listed on the company's own board is the liveness record (a gate) |
| **80 Days to Stay** | the shipped sponsorship CSV, exact-name matches only (a vote) |
| **Visa timeline** (Ch.10) | factor from the earlier of the two clocks (a gate) |
| **Scorer** (Ch.11) | the existing `role-scorer.mjs` makes every Apply / Consider / Skip call |
| **Cognitive Pivot** | display only: BLS median wage at zero weight |

## Where it fits the 3-3-2 day

It takes over the **finding and first-pass research** inside the two research-and-apply hours. Apply rows go straight to tailoring. "Network, don't apply" rows (Robinhood, in the worked run) feed the **three networking hours**. The tested, limits-stated build is evidence for the **three credibility hours**.

**Time saved — an estimate from stated assumptions, not a measurement:**
- By hand: 15 companies × ~2 min to scan a board, plus ~3 plausible postings × ~6 min to check requirements, sponsorship and dates. About **50 min a day**.
- With the tool: one command (the live one-board run took 0.66 s), plus ~10 min reading the report.
- **Net: about 40 min a day, roughly 3 h a week.**

## Domain-specific failure modes

1. **Right sponsor, wrong name.** The everyday name misses the legal name (Robinhood), or matches a *different* entity (`CHIME INC`, 2 approvals, instead of `CHIME FINANCIAL INC`, 580). The result is a confident "no record" or a wrong tier. *Hardest to catch for* a student skimming for a familiar name. The recipe holds unmatched companies as "Needs you" and prints similar-name hints.
2. **The second clock.** A hiring timeline that fits the OPT end date still fails if the unemployment allowance runs out first. For the sample persona that's 2026-12-17, against an OPT end of 2027-03-15. *Hardest to catch for* a student who only remembers their EAD date. The recipe names both clocks and scores against the earlier; the rules stay DSO questions.
