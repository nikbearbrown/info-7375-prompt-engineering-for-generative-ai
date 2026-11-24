# FACTCHECK - Early Bird final project film

Every figure and factual claim the film shows or says, with what backs it. Verdicts: VERIFIED (I checked it against a file in this repo
on 2026-11-23), PER FEEDBACK (stated in graded feedback on my earlier submissions, no saved evidence file found), AUTHOR-STATED (my own
statement), PLAN (not built; film uses future tense), ILLUSTRATIVE (labelled as such on screen).

| # | Claim in the film | Verdict | Source | Fix / note |
|---|---|---|---|---|
| 1 | Commure snapshot on Oct 14 had 80 postings | VERIFIED | `js1-contract-and-watch/data/raw/2026-10-14/ashby_commure.json` (80 jobs) | none |
| 2 | Commure snapshot on Oct 23 had 81 postings | VERIFIED | `.../2026-10-23/ashby_commure.json` (81 jobs); `summary.json` says 81 | none |
| 3 | 12 of the 81 were new (69 already seen) | VERIFIED | set difference of posting ids, Oct 23 minus Oct 14 = 12 new, 11 gone, 69 in both | none |
| 4 | Dot grid: one dot per posting, 12 dots become "new" | VERIFIED (counts), ILLUSTRATIVE (which dots) | counts as rows 1-3; the 12 new dots are chosen by a seeded random pick, not by real ids | on-screen label reads COMMURE - REAL COUNTS, ONE DOT = ONE POSTING, NEW DOTS: ILLUSTRATIVE |
| 5 | "A rule alone matched a sales job called Account Executive, AI Sales" | VERIFIED | `data/raw/2026-10-23/summary.json`: greenhouse:stripe keyword sample lists "Account Executive, AI Sales"; raw `greenhouse_stripe.json` holds the posting; `TEST-EXPECTATIONS.md` row 7 | it is the Stripe board, not Commure; the film says "my probe" |
| 6 | greenhouse-watch, run on my Commure snapshots, kept a marketing job because the posting mentioned Python and SQL | PER FEEDBACK | grader feedback on my pitch resubmission (Oct 25) | no saved output of that run was found in this repo; add the raw run output to this folder or soften the line before submitting |
| 7 | On one posting, three Claude runs read "2+ years" as not entry level; my rule keeps anything under 3 years | VERIFIED | `js1-contract-and-watch/ACTION-SURFACE.md` (all three arms answered not_relevant, citing 2+ years; my hand label was relevant, "2 years is under my rule's 3-year line") | evidence is one posting, so the film says "one posting", not a general finding |
| 8 | The judge is Claude Sonnet 5.5 | VERIFIED | `js1-contract-and-watch/README.md` line 23: `claude -p`, model `claude-sonnet-5-5` | none |
| 9 | Boards: Greenhouse, Lever and Ashby, public JSON, no login | VERIFIED | `js2-loop-tools-diff/earlybird/boards.py` has one parser per ATS; raw snapshots exist for Ashby (Commure), Greenhouse (several) and Lever (Palantir) | none |
| 10 | Early Bird will watch 25-30 companies I choose | PLAN | my project notes (company list kept private) | the film says "will" |
| 11 | Order: referral first, then freshness, then match | PLAN | my project notes | the film says "will" |
| 12 | It never skips a job for a skill gap; it flags only hard blockers and quotes the line | PLAN | my design decision; the exact wording is not in CONTRACT.md | keep future tense; add the line to CONTRACT.md if the course asks |
| 13 | Each posting will be matched to my real GitHub projects (Screenr, Market-Data-Service shown) | PLAN / ILLUSTRATIVE | repo names are mine; the posting "Full-Stack Engineer, Northwind Labs" and the pairing are invented, labelled SAMPLE MATCH | none |
| 14 | LinkedIn connections lookup uses my own Connections.csv, kept local | PLAN | my project notes; no real contact data is in any repo | keep private data out of the repository |
| 15 | Setup: Claude access, public data, my own connections export, my laptop | AUTHOR-STATED | my statement on 2026-11-22 ("the setup I already have") | confirm before submitting |
| 16 | Four checks and targets (no repeats on a second run; at least 95% of relevant roles; every flag quotes the line; referral match agrees with my check) | AUTHOR-STATED | my confirmation of these targets on 2026-11-22 | they are targets, not results; each row is tagged TARGET |
| 17 | Labels will be locked before the first run | AUTHOR-STATED | lesson from JS1 feedback ("lock labels before any run") | none |
| 18 | Northwind Labs, Lumen AI, Harbor Systems, "3 new roles", the "Must be authorized to work in the US" flag | ILLUSTRATIVE | invented | labelled SAMPLE REPORT / SAMPLE DATA / SAMPLE FLAG on screen |
| 19 | Job alert emails and job trackers behave as described | PLAN | what I expect, not tested | cards are tagged NOT YET RUN and worded "Expected:" |
| 20 | The voice is synthetic and the script was drafted with Claude from my decisions | VERIFIED | Kokoro `am_onyx` through the toolkit; `SOURCES.md` | said aloud in the last beat |

## Third-party assets
Lucide icons (ISC, lucide-static 0.468.0), DM Sans and DM Mono (SIL OFL, via Fontsource). The Early Bird mark was drawn in code. No company logos, no person icons.
