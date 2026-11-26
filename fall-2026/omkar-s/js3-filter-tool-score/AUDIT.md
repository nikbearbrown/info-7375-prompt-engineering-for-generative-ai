# The reject audit (Chapter 7)

*Written by Claude Code on 2026-11-17 from the runs in this folder; where this page says "I", that is Claude Code. Parts marked **[Omkar]** are Omkar's.*

**Summary.** The filter ran on **everything the agent collected**: 1,142 postings from 7 boards on 2026-11-17 (the 8th board, `greenhouse:webflow`, is empty, so its answer is "I cannot tell"). From the v1.2 result, a **seeded, blind sample of 49 cards** was drawn: **30 uniform random rejects** (the only part that supports a rate), all 6 close calls, 8 gate near-misses, and all 9 kept postings. **Omkar's hand verdicts are the audit: all 49 labelled by Omkar (2026-11-18 to 2026-11-25).** Result: the filter was wrong on **0 of 30** random rejects (95% interval 0%–11.6%, an estimate, not a rate). Omkar would reject **5 of the 9** kept postings, 2 of which v1.6 already rejects. Omkar's reading: "the filter counts keywords but ignores years and main stack" (`audit/AUDIT-RESULTS.md`, §2 below). Also here: the sample, the blind cards, a **second rater** (49 fresh Claude calls, kept apart from the hand verdicts), five named **false friends** found by measuring the whole corpus, and every rule added, cut or rejected after measuring (FILTER.md section 5).

## 1. How the sample was drawn

`python3 -m js3.audit draw` (2026-11-17 06:23:44 UTC; corpus `2026-11-17T06-16-31Z`; filter v1.2; seed **7375003**). Anyone can redraw the identical sample from the same corpus and seed.

| Part | What | Cards | Why |
|---|---|---:|---|
| R | uniform random sample of the 1,133 rejects | 30 | the only part whose error count supports a rate (Lectern `audit_rejects.py`, Part 1) |
| C | every close call: gates pass, score 4.0 to 5.99 | 6 | where misses live (Lectern Part 2, near-misses) |
| G | random 8 of the 27 gate near-misses: score ≥ 5.0, exactly one gate failed | 8 | a high score thrown out by one gate is the other place a good job can hide |
| K | every kept posting | 9 | the shortlist is small enough to read whole (false positives) |

**Blind on purpose.** `audit/cards.md` and the labeler show company, title, location, link, the years sentences, and the requirements excerpt. They do **not** show the score, the filter's verdict, or the part a card came from. The cards are shuffled across parts. So a hand verdict cannot copy the filter. The key (`audit/sample-key.json`) is read only by `report`.

**Known defect in the cards (found 2026-11-24, while labelling).** The cards were drawn at 06:23 UTC on 2026-11-17, before the inline-bold bug was fixed (FILTER.md change log, 06:32). So a word in **bold inside a sentence** was dropped from a card's excerpt. A check of all 49 excerpts for the visible symptom ("You have , with…") found it on **card 33** (Klaviyo Software Engineer, Conversational Products), where the dropped words include the years and the language. The years sentence on that card still shows "3+ years". The cards were **not redrawn**, because 26 hand verdicts already existed and redrawing would change the sample. For a card with gaps, the labeler's **o** (open link) shows the full posting. The scores and the filter were never affected: they use the cleaned text, not the card excerpt.

**The rule for each card** is Omkar's own JS1 labeling rule (2026-10-26): role, level ≤ ~3 years, US location, meets most required qualifications.

## 2. [Omkar] The hand verdicts

```bash
python3 -m js3.audit label     # blind; k / r / c (cannot tell) / o (open link) / q (save and quit); resumes where you stopped
python3 -m js3.audit report    # recomputes audit/AUDIT-RESULTS.md
```

Omkar's verdicts are in `audit/omkar-verdicts.csv`, each with its time and his note. Card 1 was entered in the interactive labeler; cards 2–49 with `python3 -m js3.audit label --card N --verdict … --note …`, from his chat answers (marked in each note). Replaced rows are kept in `audit/omkar-verdicts-replaced.csv`. `draw` refuses to run again once verdicts exist.

| | |
|---|---|
| Cards labelled by hand | **49 of 49** (cards 1–49, 2026-11-18 to 2026-11-25; card 1 in the terminal labeler, cards 2–49 typed by Omkar in chat and entered by Claude Code, marked in each note) |
| Random rejects I would have kept (Part R misses) | **0 of 30** (computed by `js3.audit report`) |
| Kept postings I would have rejected (Part K) | **5 of 9**: cards 2, 5, 15, 33, 49 (computed). Cards 2 and 49 are already rejects under v1.6 |
| Close calls / gate near-misses I disagree with | close calls **2 of 6** (cards 5, 49); gate near-misses **0 of 8** (computed) |
| My one-sentence reading of what the misses have in common | "the filter counts keywords but ignores years and main stack" (Omkar, typed in chat 2026-11-25, entered by Claude Code) |

## 3. What a sample of 30 can honestly show (worked out before the verdicts)

The report computes an exact (Clopper–Pearson) 95% interval for the miss rate among rejects. The interval depends only on how many of the 30 are misses, so the honest statement can be written down now. **It is an estimate for this one corpus, never a measured rate for all postings.**

| Misses in 30 | Observed rate | 95% interval | If the top of the interval were true: good postings among the 1,135 v1.6 rejects |
|---:|---:|---:|---:|
| 0 | 0% | 0.0% – 11.6% | up to ~131 |
| 1 | 3.3% | 0.1% – 17.2% | up to ~195 |
| 2 | 6.7% | 0.8% – 22.1% | up to ~251 |
| 3 | 10% | 2.1% – 26.5% | up to ~301 |

So **even a perfect 0 of 30 cannot rule out more than a hundred missed postings**. What it can show is that misses are not *common* among rejects. Most rejects are sales, marketing and operations roles, where a miss is unlikely. That is why Parts C and G exist: they are chosen on purpose, so they show **where** the filter errs, not **how often**. They say nothing about a rate. A stratified sample of engineering-titled rejects would be the next step (FRICTIONAL, unresolved).

## 4. The second rater (Claude) — not a hand verdict

`python3 -m js3.audit claude-rate`: one fresh `claude -p` call per card (claude-sonnet-5-5, no tools, no session persistence), with the same rule and the same card. 2026-11-17, 06:24:05 – 06:24:41 UTC; 49 of 49 valid. Raw answers: `audit/claude-second-rater.jsonl`.

| Part | Cards | Claude agrees with the filter (v1.2) | Disagreements |
|---|---:|---:|---|
| R random rejects | 30 | 30 | none: Claude would keep none of the 30 |
| C close calls | 6 | 4 | card 5 Linear Product Engineer (filter keep, Claude reject); card 49 Toast Senior SWE Vision AI (keep / reject) |
| G gate near-misses | 8 | 8 | none |
| K kept | 9 | 5 | cards 2, 5, 26, 49: Claude rejects 4 of the 9 kept |

**What changed because of it.** On cards 2 and 49, Claude quoted a years requirement that the filter had not read: "5+ years building and shipping software in production" and "5+ years owning and operating cloud infrastructure". I checked both in the raw posting text. That led to **FILTER.md v1.5** (an explicit `N+ years` counts alone). Measuring v1.5 on the whole corpus then exposed a new error, fixed by **v1.6** (sub-requirements). Under v1.6 both cards are rejects. Card 26 (Klaviyo Android) is SHORTLIST.md counterexample (a), and is not fixed. Card 5 (Linear Product Engineer) is a judgment about React/GraphQL fit, which is Omkar's to make.

**Why it is not the audit.** Claude agreeing with the filter on 30 of 30 random rejects is two automatic readers agreeing, not a check by the person whose job search it is. The assignment asks for hand verdicts, and the report keeps Claude's column apart.

## 5. False friends (words that matched for the wrong reason)

Each was found by measuring the whole corpus (`runs/2026-11-17T06-16-31Z/filter-v1.x/summary.md`, section "Skill words by kind of title"), not from the sample.

| # | Word | Rule | Where it matched for the wrong reason (real postings) | What I did |
|---|---|---|---|---|
| 1 | **`Kubernetes`, `AWS`** | K1 skill | Datadog sells monitoring for these. They appear as requirements in **48** (Kubernetes) and **42** (AWS) Datadog **non-engineering** postings, e.g. Sales Engineer: "Advanced background in public cloud (AWS, Azure, GCP), Kubernetes, APM/tracing". The skill matches, but the job is selling the product, not building with it | **rejected** ignoring them: 56 scores change, 0 verdicts, because the title rules already reject these jobs; and the words are real evidence on Datadog's engineering postings |
| 2 | **`developer`** | T2 engineer title | "Developer Advocate – Service Management" earned +1.5 as a "close engineering role" and became a **close call** (4.5) | **added** `developer advocate` (+7 more) to the non-software list (v1.2) |
| 3 | **`early-career`** | Y1 level evidence | "You have experience mentoring and developing **early-career** PMs" in a *Principal Product Manager* posting: it describes the people you manage, not the level of the job | **rejected** cutting it: 0 verdicts change, and it is meant where it says "early-career program manager" |
| 4 | **`sales engineer`** (a false friend in reverse) | T2 exclusion | whole-word matching does **not** find "sales engineer" inside "**PreSales** Engineer", so "Lead PreSales Engineer – German Speaking" earned engineer points | **added** `presales engineer` (v1.2) |
| 5 | **`2+ years`** | G3 years | "5+ years of engineering experience, **with 2+ years** building AI/ML…" (Klaviyo Full Stack SWE – People Systems): under v1.5 the smallest-number rule read 2 and kept a 5-year job | **added** the sub-requirement rule (v1.6) |

Lectern's textbook false friend, "training" at an AI company, has no counterpart here, because this filter has no teaching words. The closest analogue is #1: a word that names the employer's **product** rather than the candidate's **work**.

## 6. Rules added, cut and rejected after measuring

All are in FILTER.md section 5 with the measurement behind each. In short:

| Version | Change | Verdicts flipped on 1,142 |
|---|---|---:|
| 1.1 | **added** G1: "…, USA" is a US location (120 US postings, 118 of them Datadog, had been rejected on G1 for the wrong reason) | 0 |
| 1.2 | **added** 8 non-software title phrases (false friends #2, #4) | 0 |
| 1.3 | **changed** headings: "Nice to Haves" (plural) ends a requirements section | 0 (2 claim labels) |
| 1.4 | **added** tech-stack headings end a requirements section | 0 (12 claim labels) |
| 1.5 | **added** explicit `N+ years` counts without "experience" (from the second rater) | 3 |
| 1.6 | **added** sub-requirements do not set the minimum (false friend #5) | 1 |
| — | **rejected** bare "N years" patterns (13 postings, all non-engineering) | would be 0 |
| — | **rejected** cutting `early-career` (#3) | would be 0 |
| — | **rejected** ignoring Kubernetes/AWS on Datadog (#1) | would be 0 |
| — | **rejected** `and` as a sub-requirement word (would hide "a BS **and** 2+ years") | — |

The audit sample was drawn under v1.2. v1.3–v1.4 changed only claim labels, while v1.5–v1.6 changed the verdicts on cards 2 and 49 (keep → reject). The report shows both the draw-time and the current verdict, and computes the parts from the draw-time one, because that is the filter the sample measured.
