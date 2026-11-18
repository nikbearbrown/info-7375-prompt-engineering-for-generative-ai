# FILTER — Job-Search Agent 3

**Version 1.0 · 2026-11-14 · written before any code for this layer**

## Executive summary

This is the rulebook that decides which job postings reach the candidate and why. The
agent collects a few hundred postings from four public job boards. Most are not for a
new-grad software engineer. This file says, rule by rule, what keeps a posting, what
throws it out, and when the agent must say "I cannot tell" instead of guessing. Each rule
has one line of reasoning. It also says what counts as evidence for a claim, which boards
and fields the agent should see, and two wrong filters the tests must catch.

**Provenance.** Smit P. chose the boards, the role words, the exclusions, the skill
threshold, the abstention cases, the score, the tool, and the two wrong versions on
2026-11-14, by picking from options Claude offered in a Claude Code session. Claude wrote
those choices up as this file. Details Claude had to define to make the choices testable
are marked **[defined by Claude]** so they can be checked. The candidate is the fictional
persona Aarav Patel (`@example.com`, `555` phone), a new-grad software engineer on F-1 OPT
who needs a US job.

Later changes are added as new versions in the change log at the end. Earlier text is not
edited.

---

## 1. The filter

A posting gets exactly one verdict: **keep**, **reject**, or **cannot_tell**. Checks run in
this order and the first one that decides is the verdict. All word matching is
case-insensitive and **whole-word**: the match must not have a letter or digit directly
before or after it.

| # | Rule | Verdict if it fires | Reason |
|---|---|---|---|
| R1 | **Role words.** The title must contain one of: `software engineer`, `software developer`, `backend engineer`, `back-end engineer`, `back end engineer`, `full stack engineer`, `full-stack engineer`, `fullstack engineer`, `cloud engineer`, `platform engineer`. If none → reject | reject | These are the titles Aarav's experience fits; it is the same family as the hand-labeling rule from Job-Search Agent 1. |
| R2 | **Seniority words.** The title contains `senior`, `sr`, `staff`, `principal`, `lead`, `manager`, `director`, or `head` → reject | reject | A new grad is not hired into these levels; the title is the most reliable signal of level. |
| R3 | **No description.** The posting has no body text after tags are removed → cannot_tell | cannot_tell | Skills and years can only be checked in the text; a title alone is not evidence. |
| R4 | **Location.** If the location shows a US place → pass. If it shows only non-US places → reject. If it is empty, or says only "Remote" with no country → cannot_tell | reject / cannot_tell | Aarav needs a US job for OPT. Job-Search Agent 1's rule had no location check and called a São Paulo job relevant. |
| R5 | **Years.** If the text asks for **4 or more** years of experience → reject. If it gives a range that crosses the line (lower bound under 4, upper bound 4 or more, e.g. "3–5 years") or says "years of experience" with no number → cannot_tell | reject / cannot_tell | Smit's hand-labeling rule allows up to 3–4 years; a posting asking for more is not new-grad. |
| R6 | **Topic words (skills).** At least **2 distinct** of Aarav's résumé skills appear in the title or description → keep. Fewer → reject | keep / reject | Two matching skills is the threshold from Job-Search Agent 1. One shared word is too easy to hit by chance. |

**Résumé skills (R6).** Every string in the persona's `skills` lists except
`familiar_with_not_shipped`: TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL,
PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins. Rust and Terraform do not
count, because the résumé says they were never shipped.

**[defined by Claude] How R4 decides "US".** A location is US if, as a whole word or
phrase, it contains `United States`, `USA`, `U.S.`, `US`, a US state name, or a two-letter
US state code directly after a comma (`San Francisco, CA`). A structured country field
from the board (Lever `country`, Ashby `addressCountry`) is used first when present. A
location listing several places passes if any one of them is US.

**[defined by Claude] How R5 finds years.** A number counts only when it is followed by
`years` or `yrs` (with optional `+`, a range like `3-5` or `3 to 5`, or `or more`) and the
word `experience` appears within the same sentence. If several requirements appear, the
smallest lower bound is used, so "5+ years, or 3+ years with a Master's" counts as 3.

**Close calls.** A kept posting with exactly 2 skills, and a posting rejected by R6 with
exactly 1 skill, are the postings closest to the threshold. The audit looks at them on
purpose.

## 2. The score (kept postings only)

`score = (number of distinct résumé skills found) + 2 if the title contains "software engineer" or "software developer"`

| Number | Value | Origin |
|---|---|---|
| Skill threshold (R6) | 2 | inherited from Job-Search Agent 1, where Smit hand-set it |
| Years cut-off (R5) | 4 | hand-set by Smit from the hand-labeling rule ("up to 3–4 years") |
| Points per skill | 1 | hand-set by Smit (chosen option, 2026-11-14) |
| Title bonus | 2 | hand-set by Smit (chosen option, 2026-11-14) |

None of these numbers is fitted to labels. If one is later changed after measuring, the
change log says so.

## 3. Evidence rules

Every claim in a shortlist justification is labeled against **the posting's own text
only** (title, location, description), never against the company's reputation or a
model's prior knowledge:

| Label | When |
|---|---|
| **supported** | A quoted span of the posting, read in its sentence, states the claim. |
| **contradicted** | A quoted span states the opposite (the claim says entry-level, the text says "5+ years"; the claim says "uses Python", the text says "Python is not required"). |
| **insufficient** | No span states the claim or its opposite. A word appearing somewhere is not enough if its sentence does not say what the claim says. |

**When the agent must say "I cannot tell".** The verdict is cannot_tell when R3, R4, or R5
says so. A shortlist claim is never upgraded from insufficient to supported by
assumption. The agent prints "I cannot tell" and the reason, and the person decides.

## 4. Expected sources

| Board | System | Endpoint (public, read-only) | Title | Location | Description |
|---|---|---|---|---|---|
| Airbnb | Greenhouse | `boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true` | `title` | `location.name` | `content` (HTML, unescaped, tags removed) |
| Figma | Greenhouse | `boards-api.greenhouse.io/v1/boards/figma/jobs?content=true` | `title` | `location.name` | `content` |
| Spotify | Lever | `api.lever.co/v0/postings/spotify?mode=json` | `text` | `categories.location`, `country` | `descriptionPlain` + `lists` + `additionalPlain` |
| Linear | Ashby | `api.ashbyhq.com/posting-api/job-board/linear` | `title` | `location`, `address.postalAddress.addressCountry` | `descriptionPlain` |

The allow-list is exactly these three hosts. **When something is missing:** a missing
title or id makes the posting unreadable and it is listed, not judged; a missing
description or location gives cannot_tell (R3, R4), never a guess; a board that fails to
respond is reported as "not collected" and none of its postings are judged.

## 5. Wrong versions the tests must catch

1. **Substring matching.** A filter that matches words inside other words: `Java` inside
   `JavaScript`, `SQL` inside `PostgreSQL`, `lead` inside `leadership`, and, for location,
   `US` inside `Russia` or `Belarus`. Caught by tests with constructed postings where only
   a part-word match exists and the verdict must not change.
2. **Ignoring location.** A filter that keeps a software engineering posting in São Paulo
   or Berlin for a US OPT candidate. Caught by a test where the same posting is kept with
   a US location and rejected with a non-US one, and by a test where an empty location
   gives cannot_tell.

## Change log

| Version | Date | Change | Measured on | Who decided |
|---|---|---|---|---|
| 1.0 | 2026-11-14 | first version, before any code | — | Smit P. (choices), written up by Claude |
| 1.1 | 2026-11-14 | changes A, B, C below | Smit's hand verdicts on 71 audit postings: chosen on the 38 dev postings, reported on the 33 held-out | Smit P. |

### Version 1.1 — what changed after measuring (added 2026-11-14; the text above is v1.0, unchanged)

Each candidate was measured alone, as v1.0 plus one change (`src/measure_filter.py`,
`experiments/filter-changes.json`). Errors are disagreements with Smit's hand verdicts.

| Change | Status | Dev errors (of 38) | Held-out errors (of 33) | Reason (Smit's) |
|---|---|---|---|---|
| — v1.0 | baseline | 7 | 3 | — |
| **A.** R5 uses the **largest** lower bound, not the smallest | **added** (replaces the v1.0 "smallest lower bound" definition, which is **cut**) | 4 | 3 | "5+ years …, including 3+ years with Ruby" is one 5-year requirement; the smallest number kept three 4–5-year jobs. No held-out posting had this pattern, so held-out shows no harm, not an improvement. |
| **B.** `intern`, `internship`, `phd` join the R2 level words | **added** | 6 | 3 | Aarav has graduated; an internship is not the job he needs. |
| **C.** R6 needs **1** skill instead of 2 | **added** | 6 | **4 (worse)** | "Missing good jobs is worse": a missed relevant job (the Web and Android jobs) costs Aarav more than reading one extra posting. Smit chose it knowing held-out got worse. In combination with A, that held-out error goes away (the job is then rejected for 5+ years). |
| **D.** allow "Manager, Software Engineering" titles | **rejected after measuring** | 7 | 3 | Fixed nothing: those jobs then fail on skills. Smit's hand verdicts call two of them relevant; no rule here reproduces that. |
| **v1.1 = A + B + C** | current | **2** | **3** | — |

**Numbers that changed in v1.1:** skill threshold 2 → **1** (fitted by choice on dev labels,
no longer inherited); title bonus, points per skill and the 4-year cut-off unchanged.

**Caveat.** The held-out results for every candidate were shown before Smit chose, so the
held-out set is no longer untouched for v1.1. The three held-out errors that remain (an Engineering
Manager title and a Forward Deployed Engineer title, both outside the role words, and an Android job with
no résumé skills) were not used to design any change.
