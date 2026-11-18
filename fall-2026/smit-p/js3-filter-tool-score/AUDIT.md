# The reject audit

> **Authorship.** Claude drafted this report from the files it cites. The hand verdicts in it
> are Smit's (`audit/hand-verdicts.json`); every number is recomputed by
> `python3 src/audit.py score --run-id live-20261114` → `audit/audit-numbers.json`.

## Executive summary

The filter threw away 467 of the 473 postings the agent collected on 2026-11-14. This audit
asks how many of those it should have kept, and how many of the 6 it kept it should have
thrown away. Smit judged 71 postings by hand: 30 rejects drawn at random, every posting the
filter kept, every software-engineering title it rejected for location, years or skills, and
every engineering title it rejected only because the title wording was not on its list.

The filter (version 1.0) disagreed with Smit on 10 of the 71. The worst part was what it
kept: 4 of its 6 "keeps" were wrong. Three of those came from one false friend. The filter
read "5+ years of experience, *including 3+ years* with Ruby" as a 3-year job. In the 30
random rejects it was wrong twice, and both are jobs Smit's own written yardstick would
reject (Engineering Manager roles). A sample of 30 cannot tell a 1% miss rate from a 22% one,
so this is not a measured rate for all 467 rejects. After the audit, three rule changes
(version 1.1) brought the disagreements to 5 of 71.

## Run record

| | |
|---|---|
| Collection | `runs/live-20261114/` · 2026-11-14 23:59 UTC · Airbnb, Figma (Greenhouse), Spotify (Lever), Linear (Ashby) · 473 postings, 0 unreadable, 0 boards failed |
| Filter audited | v1.0 (`FILTER.md`, commit `c25d7660`) · 6 keep, 467 reject (R1 title 417, R2 seniority 33, R4 location 7, R5 years 4, R6 skills 6), 0 cannot_tell |
| Sample | `src/audit.py sample`, seed 7375, drawn and committed (`ace3d80c`) **before** any hand verdict |
| Hand verdicts | Smit P., 2026-11-14, `audit/hand-verdicts.json` (commit `03368121`) |
| Yardstick Smit used | his Job-Search Agent 1 hand-labeling rule: a software / cloud / full-stack engineering IC job, not senior, staff, principal or manager, about 4 years or less, US or remote-US, with his own judgment where he disagreed |

## How the sample was built

| Stratum | What | n |
|---|---|---|
| random_reject | 30 drawn uniformly from all 467 rejects (28 were rejected by title, 1 by seniority, 1 by location) | 30 |
| kept | every posting v1.0 kept | 6 |
| close_call | every posting that passed the title rules and was then rejected for location, years or skills | 17 |
| near_miss | every title-rule reject whose title says Engineer or Developer and has no seniority word | 21 |
| **unique postings** | (two random rejects were also near misses, one also a close call) | **71** |

Before judging, each posting was split into **dev** (38) or **held-out** (33) by a second
seeded draw. Rule changes were chosen on dev and reported on held-out (`FILTER.md`, v1.1).

**What Smit saw.** A fact card per posting: title, board, location, and every sentence that
gives years of experience. He never saw the filter's verdict or the skills it found. The
first version of the cards showed only the sentence the filter had used, and that would have
hidden the very error the audit found. It was fixed before any judging (`de37311d`).

## Results

| Stratum | v1.0 wrong | 95% interval (Clopper–Pearson) | v1.1 wrong |
|---|---|---|---|
| random_reject | **2 / 30** | 0.8% – 22.1% | 2 / 30 |
| kept by v1.0 | **4 / 6** | 22% – 96% | 0 / 6 |
| close_call | 3 / 17 | 3.8% – 43.4% | 2 / 17 |
| near_miss | 1 / 21 | 0.1% – 23.8% | 1 / 21 |
| all 71 | 10 / 71 | 7.0% – 24.4% | 5 / 71 |

**Every disagreement with v1.0:**

| Posting | Filter v1.0 | Smit | Why the filter differed |
|---|---|---|---|
| Figma · Software Engineer - Application Platform | keep | not relevant | false friend: "including **3+ years** … with Ruby" inside a 5+ year requirement |
| Figma · Software Engineer - AI Platforms | keep | not relevant | same: "3+ years of experience in one or more of: AI…" next to "5+ years of Software Engineering" |
| Figma · Software Engineer - C++ | keep | not relevant | same: "2+ years … in a technical lead role" next to "4+ years of professional Software Engineering" |
| Figma · Software Engineer Intern (Summer 2027) | keep | not relevant | v1.0 had no rule against internships |
| Airbnb · Software Engineer, Profile & Community, Web | reject (1 skill) | relevant | the skill list misses the posting's main words (JavaScript, React) |
| Airbnb · Software Engineer, Profile & Community, Android | reject (0 skills) | relevant | same (Android, Kotlin are not résumé skills) |
| Spotify · Fullstack Engineer - Backstage (Stockholm) | reject (location) | relevant | Smit judged a Sweden job relevant. See note 2 below |
| Figma · Forward Deployed Engineer | reject (title) | relevant | "Forward Deployed Engineer" is not a role word |
| Figma · Manager, Software Engineering - AI Infrastructure | reject (title) | relevant | see note 1 below |
| Figma · Manager, Software Engineering - Design Systems Adherence | reject (title) | relevant | see note 1 below |

## What the random sample can honestly say

- In 30 random rejects, 2 disagreed with Smit. The exact 95% interval for the share of
  rejects Smit would call relevant is **0.8% to 22.1%**. Applied to 467 rejects, that range
  runs from about 4 postings to about 103. That width is the finding. **This is a sample
  estimate, not a measured rate for all rejects.**
- Both disagreements are "Manager, Software Engineering" roles, which ask for 3+ years of
  *managing* engineers. Smit's written yardstick excludes Manager titles. When asked, he
  kept them as relevant (note 1). If those two followed the yardstick, the result would be
  0 of 30, and the interval would still reach **11.6%**. Zero errors in 30 does not mean zero errors.
- 28 of the 30 random rejects were thrown out on the title alone (sales, legal, design,
  marketing). A uniform sample of rejects is mostly easy cases. That is why the close calls
  and near misses were judged as well, and where the informative errors turned up.

## False friends: words that matched for the wrong reason

1. **"3+ years" in "Bring 5+ years of professional software engineering experience,
   including 3+ years building production systems with Ruby"** (Figma, Application
   Platform). Rule R5 as first defined used the *smallest* number of years it found, so this
   5-year job passed as a 3-year job. The same pattern caused two more false keeps. Fixed in
   v1.1 (change A: use the largest).
2. **"TypeScript" and "Python" in "Proficiency in TypeScript, Python, or Ruby"** (Figma, AI
   Platforms). An either/or list counted as two skills the job uses. Not fixed in the filter.
   The claim checker labels such matches "insufficient" (see `SHORTLIST.md`).
3. **"Python" and "Java" in "C++, JavaScript, Python, Java, etc."** (Figma, Software
   Engineer Intern). A list of acceptable languages for an internship. The skills matched
   and the job was still wrong for Aarav. Fixed in v1.1 by rejecting intern titles (change B),
   not by changing the skill match.

## Rules added, cut, and rejected after measuring

Full table with dev and held-out numbers: `FILTER.md` → "Version 1.1".
**Added:** A (largest years number), B (intern / internship / PhD are level words), C (1 skill
is enough). **Cut:** the v1.0 "smallest lower bound" definition (replaced by A). **Rejected:**
D (allow "Manager, Software Engineering"), which fixed nothing. Smit chose C knowing that
on its own it made held-out worse (3 → 4 errors).

## Notes on the hand verdicts

1. Smit was asked once whether the two Engineering Manager roles were meant as relevant:
   they ask for 3+ years of engineering management, and his yardstick excludes Manager. He
   answered "Yes, keep relevant". A third, similar role ("Manager, Software Engineering - UX
   Platform", 2+ years managing) he marked not relevant. All three are recorded as given.
2. Smit marked two Stockholm "Backend Engineer - Data Platform" jobs and a 5+ year job
   relevant. When asked, he changed all three to not relevant. He then marked a third
   Stockholm job ("Fullstack Engineer - Backstage") relevant, and that is recorded as given.
3. These verdicts are the yardstick the filter was measured against. Where they conflict
   with the written yardstick, the audit counts the filter as wrong. That is why "the
   filter was wrong" here means "the filter disagreed with Smit", not "the filter broke its
   own rule".

4. **Time taken.** The 71 verdicts and 3 clarifying answers were given between 19:01 and 19:09
   US Eastern on 2026-11-14 (commits `de37311d` → `03368121`), mostly three postings per
   question. That is about 7 seconds per posting. Most were sales, legal or senior titles, but
   a reader should weigh the close calls with that speed in mind.

## Not covered by this audit

- Postings the boards did not return. Only one collection run (2026-11-14) was audited.
- A second judge. Every verdict is one person's, given once, with no re-test of the same postings.
- The filter's behavior on boards other than these four.
