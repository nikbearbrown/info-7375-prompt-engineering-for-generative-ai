# SCORE-REPORT.md: what moves the score (JS3, Chapter 9)

Tushar Patel · INFO 7375 · Fall 2026 · 2026-11-23

- **Rules frozen at commit `f3edf99`** ("js3: v0.2 erratum + C4 preferred-heading rule, frozen before held-out"). Neither FILTER.md nor `agent/` has changed since then.
- **Section 2 is the first and only comparison** of the held-out labels with any filter result.
- **Sources of the numbers.** Section 1 is written by hand and checked against the code constants by `tests/test_score_report.py`. Section 2 is the verbatim output of `python checks/score_report.py`, and the same test reruns the script and compares.

## 1. Origin of every number and word list

Origin categories:
- **hand-set:** written in FILTER.md v0.1 (commit `821ddee`, 2026-11-21) or in build-step-1 code (commit `6cc6880`, 2026-11-23) before any label existed.
- **inherited:** taken from JS1, with the file and line given.
- **chosen on development labels:** C1–C6, decided after reading the 48 audit rows.
- **fitted:** no number or list in the filter was fitted. Nothing was optimized against labels; every value below was typed in by hand.

| Item | Value | Where it's used | Origin | Evidence |
|---|---|---|---|---|
| G1 role list | Software Engineer, Software Developer, Backend Engineer, Back-End Engineer, Full Stack Engineer, Full-Stack Engineer, AI Engineer, Machine Learning Engineer, ML Engineer | G1, title (`G1_ROLES`, agent/filter.py:51) | **inherited** + **hand-set**. Software Engineer, AI Engineer and Backend Engineer come from JS1; the six spelling and role variants were added in v0.1 | JS1 `persona/cole-palmer.example.json`:32 (`target_titles`) and `CONTRACT.md`:112 (R1); FILTER.md v0.1 G1 row (`821ddee`) |
| G2 seniority list | Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, VP, Intern | G2, title (`G2_EXCLUDED`, agent/filter.py:54) | **inherited** + **hand-set**. Senior, Staff, Principal, Lead, Manager and Intern come from JS1; Sr, Director, Head and VP were added in v0.1 | JS1 `CONTRACT.md`:114 (R1); FILTER.md v0.1 G2 row |
| G3 US markers, cities, short forms, state names, state abbreviations (CA excluded) | United States, USA, U.S., US (uppercase only); San Francisco, South San Francisco, New York, New York City, New-York, Seattle, Chicago, Atlanta; SF, NYC, NY, SEA, CHI, ATL, DC; the 50 state names; the 49 state abbreviations other than CA, only after "," or ";" | G3 (`US_*`, agent/filter.py:67–90) | **inherited**, unchanged. JS1 built these lists from real Stripe location values on 2026-10-27, which is data but not labels | JS1 `CONTRACT.md`:123–129 (R3); the "Choice" comment at agent/filter.py:66 |
| G3 placeholders → unknown | "N/A"/"na", "LOCATION", empty, plus "TBD" | G3 (`_PLACEHOLDERS`, agent/filter.py:95) | **inherited** (JS1 R3), with "TBD" **hand-set** in build step 1 | JS1 `CONTRACT.md`:130 |
| G3 remote words | remote, hybrid, on-site, onsite, in-office, flexible | G3, to decide whether a value names no country (`_REMOTE_WORDS`, agent/filter.py:94) | **hand-set** (build step 1, an implementation choice) | agent/filter.py:93–94 |
| G3 regions → unknown | North America, AMER, Americas, Global, Worldwide, Anywhere | G3 (`US_CONTAINING_REGIONS`, agent/filter.py:92) | **hand-set**. A reading Tushar confirmed on 2026-11-21, before the code; JS1 R3 had failed "AMER" | agent/filter.py:12–13 docstring; JS1 `CONTRACT.md`:131 |
| G4 cutoff, v0.1 | 3 years (fail if the largest minimum is more than 3) | G4 (`check_g4`, agent/filter.py) | **inherited** + **hand-set**: JS1 R4 "3 or less → pass", restated in v0.1 | JS1 `CONTRACT.md`:134–137 (R4); FILTER.md v0.1 G4 row |
| G4 cutoff, v0.2 | 2 years | G4 (`cutoff = 2 if "C3"`, agent/filter.py:329) | **chosen on development labels** (C3). A search-scope decision for a persona with `years_experience` 0, made after the audit; not a conclusion the audit proved | FILTER.md v0.2 C3 row and changelog; `audit/AUDIT-RESULTS.md` section d |
| G4 minimum patterns, v0.1 | "N+ years", "N–M years" (lower bound), "at least N years", "N years of" | G4 (`_G4_PATTERN`, agent/filter.py:101) | **inherited** ("N+ years" and "N–M years", JS1 R4) + **hand-set** ("at least N years" and "N years of", v0.1) | JS1 `CONTRACT.md`:135; FILTER.md v0.1 G4 row |
| G4 C2 maximum phrases | "less than N years", "up to N years", "no more than N years" (also "year"); N may be digits or one–ten | G4 (`_MAX_KIND`, `SPELLED`, agent/filter.py:257–259) | **chosen on development labels** (C2). The spelled numbers one–ten were accepted by Tushar on 2026-11-23, after audit rows 20 and 39 | FILTER.md v0.2 C2 row and "C2 note" changelog line |
| G4 C4 preferred words, and the mixed → unknown rule | "preferred", "nice to have", "bonus", "a plus"; mandatory minimums on both sides of the cutoff → unknown | G4 (`PREFERRED_WORDS`, agent/filter.py:271) | **chosen on development labels** (C4) | FILTER.md v0.2 C4 row; audit rows 31, 33 and 35 |
| G4 C6 form | "word (N)" counts as N, e.g. "two (2) years" | G4 (`_N_C6`, agent/filter.py:247) | **chosen on development labels** (C6). The gap was found on the corpus in build step 1; the decision came after the audit | `audit/AUDIT-RESULTS.md` section f |
| Heading definition (C4) | an `<h1>`–`<h6>`; or a non-list block of 8 words or fewer that doesn't end in ".", "!" or "?" | G4 C4 preferred scope (`is_heading`, `HEADING_MAX_WORDS = 8`, agent/filter.py:275) | **chosen on development data**. The rule (a preferred heading marks its items) is Tushar's; the definition, including "8 words", was proposed by Claude from a survey of heading markup in all 979 postings' raw text (text only, no labels; that included the 30 held-out postings' text). Frozen in `f3edf99` | FILTER.md v0.2 "Heading"; C4 amended changelog line |
| G5 phrases | unable to sponsor, will not sponsor, does not sponsor, no sponsorship, without sponsorship, without the need for sponsorship; plus do not sponsor, cannot sponsor, not able to sponsor | G5 (`G5_PHRASES`, agent/filter.py:62) | **inherited** (the first six, JS1 R5) + **hand-set** (the three synonyms, build step 1). No posting in live-text-1 contains any of them, so G5 never fails | JS1 `CONTRACT.md`:141 (R5); agent/filter.py:59–61 comment |
| Topic words | v0.1: backend, API, distributed systems, infrastructure, platform, full-stack, LLM, machine learning. v0.2: the same without "platform" | Score (`TOPIC_WORDS`, `TOPIC_WORDS_V02`, agent/filter.py:55–57) | **hand-set** (v0.1); the removal of "platform" was **chosen on development data** (C5: a corpus false-friend count plus audit row 6) | FILTER.md v0.1 Score row; FILTER.md v0.2 "False friend" |
| Skills | Python, Java, TypeScript, SQL, PostgreSQL, Spring Boot, React, Docker, AWS | Score (read from the persona at runtime) | **inherited** | JS1 `persona/cole-palmer.example.json`:30 |
| Score caps | 3 for topic words, 3 for skills | Score (`TERM_CAP = 3`, agent/filter.py:48) | **hand-set** (v0.1) | FILTER.md v0.1 Score table |
| Keep threshold | score ≥ 2 | Verdict (`KEEP_THRESHOLD = 2`, agent/filter.py:47) | **hand-set** (v0.1) | FILTER.md v0.1: "Threshold and weights are hand-set in v0.1" |
| Near-threshold band | scores 1–3 | Audit sampling (`NEAR_THRESHOLD = (1, 3)`, agent/filter.py:49) | **hand-set** (v0.1) | FILTER.md v0.1 Score note |
| Text minimum | 200 characters | Text status → cannot_tell (`MIN_TEXT_CHARS = 200`, agent/filter.py:46) | **hand-set** (v0.1) | FILTER.md v0.1 "When the agent must say 'I cannot tell'" |
| Persona values | `years_experience` 0, `needs_sponsorship` true, `work_country` US | G4 range check, G5, G3 (read at runtime) | **inherited** | JS1 `persona/cole-palmer.example.json`:33–35 |
| Audit sample sizes | 15 near-threshold maximum (3 existed); 30 random rejects; 10 keeps (5 were available after the near-threshold draw); 10 cannot_tell | `agent/sheets.py`:32–33 | **hand-set** (build step 1, before any label) | `agent/sheets.py` docstring; `sheet-key.json` shortfall |
| Held-out sample size | 30, drawn from postings not on the audit sheet | `agent/sheets.py`:34 | **hand-set** (build step 1) | `agent/sheets.py`:66 |
| Seed | 7375 (the course number) | `agent/sheets.py`:31, one `random.Random` for the whole draw | **hand-set** | `agent/sheets.py`:12 |

## 2. Held-out measurement (unsealed once, after the freeze)

The held-out sheet holds Tushar's blind labels, committed in `f97f528` before any filter result was opened and unchanged since. Each single change is compared with v0.1; the combined v0.2 is reported separately.

<!-- BEGIN checks/score_report.py output -->
Held-out labels (blind, commit f97f528a): 4 keep, 24 reject, 2 cannot_tell; 30 rows.

Baseline: a filter that rejects every posting would agree on 24/30.

### Agreement per mode

| mode | change | agree / 30 | % | Wilson 95% | rows changed vs v0.1 | of those, now agree / now disagree |
|---|---|---|---|---|---|---|
| v0.1 | — | 24 | 80.0% | 62.7% – 90.5% | — | — |
| v0.1+C1 | G4: no stated experience passes | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.1+C2 | G4: stated maximum that 0 years satisfies | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.1+C3 | G4: cutoff 3 → 2 | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.1+C4 | G4: every mandatory minimum; mixed → unknown; preferred ignored | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.1+C5 | topic words without "platform" | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.1+C6 | G4: "two (2) years" forms | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |
| v0.2 | C1–C6 combined | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |

### Why the held-out set cannot separate the modes

The held-out rows were drawn at random from the 931 postings not on the audit sheet (agent/sheets.py, seed 7375). Under v0.1 that pool holds 0 keep, 921 reject and 10 cannot_tell, because the audit sheet took every v0.1 keep and 10 of the 20 cannot_tell.

| mode | pool postings whose verdict differs from v0.1 | chance a random 30 of the pool includes none |
|---|---|---|
| v0.1+C1 | 6 | 82% |
| v0.1+C2 | 0 | 100% |
| v0.1+C3 | 1 | 97% |
| v0.1+C4 | 1 | 97% |
| v0.1+C5 | 0 | 100% |
| v0.1+C6 | 1 | 97% |
| v0.2 | 7 | 79% |

In v0.2 the 30 held-out verdicts are decided by: G1 28, G3 2. C1–C4 and C6 change only G4 and C5 only the score, so a row rejected at G1, G2 or G3 cannot move.

### Held-out disagreements (identical in every mode)

| row | title | locations | me | filter (all modes) | decided by (v0.1) | decided by (v0.2) |
|---|---|---|---|---|---|---|
| 7 | Account Executive, Scaled Hunter – Startup SaaS Platforms (ROE) | Dublin | keep | reject | G1 fail | G1 fail |
| 20 | Operations Associate - Bridge (CDMX) | Mexico City | cannot_tell | reject | G1 fail | G1 fail |
| 24 | Deal Desk | North America | keep | reject | G1 fail | G1 fail |
| 25 | Technical Operations Engineer, Revenue | US | keep | reject | G1 fail | G1 fail |
| 26 | University Recruiter | N/A | cannot_tell | reject | G1 fail | G1 fail |
| 27 | Recruiting Scheduler | Chicago | keep | reject | G1 fail | G1 fail |

### v0.1

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

### v0.1+C1

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.1+C2

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.1+C3

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.1+C4

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.1+C5

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.1+C6

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.

### v0.2 (combined; reported separately)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 |
| **cannot_tell** | 0 | 0 | 0 |

No held-out row changes verdict versus v0.1.
<!-- END checks/score_report.py output -->

**What section 2 shows.**
- **Every mode agrees on 24 of 30**, which is exactly what rejecting everything would score. No change, alone or combined, moved a single held-out row.
- **This is not evidence that C1–C6 are useless, or that they help.** The held-out draw contained no row any of them could move:
  - 28 of the 30 are rejected at G1 and 2 at G3.
  - The pool the held-out was drawn from had no v0.1 keeps, because the audit sheet had taken all 8.
  - A random 30 from that pool had a 79–100% chance of containing none of the postings each change moves.
- **The six disagreements are all G1 title rejects** that Tushar labeled keep or cannot_tell: Account Executive, Deal Desk, Technical Operations Engineer, Recruiting Scheduler, Operations Associate and University Recruiter.
  - Four of them are keep labels on titles outside the persona's target roles, the same pattern as audit row 19 before its post-unblinding correction.
  - These labels stay as they were labeled blind. Changing a held-out label now, after seeing the filter's verdicts, would make the held-out set no longer blind.
  - Agreeing with them would need a G1 change, and the rules are frozen.

## 3. Honest limits

- **30 rows is small.** The held-out labels are 4 keep, 24 reject and 2 cannot_tell. Every mode scores 24/30 (80.0%), with a Wilson 95% interval of **62.7% – 90.5%**. A difference of 1–2 rows between modes would be within noise; here there is no difference at all, because no row moved.
- **Held-out label quality.** 4 held-out rows labeled keep are non-engineering titles (rows 7, 24, 27; plus 25 Technical Operations Engineer) and look like the same labeling slip as audit row 19. They were NOT corrected, to keep the held-out set blind, so held-out agreement measures label quality as well as the filter. Rejecting everything also scores 24/30 on this set.
- **The audit sheet overstates C1–C6.** They were chosen after reading the 48 audit rows, so audit agreement (v0.1 28/48 → v0.2 34/48 on blind labels; `audit/AUDIT-RESULTS-v0.2.md`) is development data. The held-out set is the fairer test, but it is small, and this draw gave it nothing to separate the modes. A fair measurement of C1–C6 needs new blind labels on postings these changes actually move, such as the 7 non-audit postings v0.2 changes, labeled before looking at their verdicts.
- **Nothing was trained.** Claude, the model, did not change. Every behavior change in this project is a change to a file: FILTER.md and `agent/filter.py`. Running it again tomorrow and getting the same results shows that the file changed and is deterministic, not that anything learned.
- **Rules were not revised after this comparison.** FILTER.md v0.2 says: "Decisions frozen 2026-11-23 before any held-out comparison. … Rules will not be revised in response to held-out results." The rules are as committed in `f3edf99`; this commit adds only the report, its script and its test.
- **The held-out postings' text was seen before the freeze, but their labels were not.** The C4 heading definition came from a survey of heading markup across all 979 postings, which included the 30 held-out postings. No held-out label was read before this report.
