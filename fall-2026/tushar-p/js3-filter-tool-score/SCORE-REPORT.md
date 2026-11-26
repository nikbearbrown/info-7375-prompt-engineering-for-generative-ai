# SCORE-REPORT.md: what moves the score (JS3, Chapter 9)

Tushar Patel · INFO 7375 · Fall 2026 · 2026-11-23

- **Rules frozen at commit `f3edf99`** ("js3: v0.2 erratum + C4 preferred-heading rule, frozen before held-out"). Neither FILTER.md nor `agent/` has changed since then.
- **Section 2 is the first and only comparison** of the held-out labels with any filter result. Section 2b measures a separate, later blind sheet of postings the changes actually move.
- **Sources of the numbers.** Section 1 is written by hand and checked against the code constants by `tests/test_score_report.py`. Sections 2 and 2b are the verbatim output of `python checks/score_report.py --section 2` and `--section 2b`, and the same test reruns the script and compares.

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

## 2b. Changed-postings set

**Why this set exists.** The held-out draw contained no posting any change could move (section 2). So after the comparison, with rules still frozen at `f3edf99`, every posting outside the audit and held-out sheets whose verdict differs from v0.1 under some mode was put on a new blind sheet: N = 8 changed postings. To these were added 8 random postings from the same pool whose verdict is the same in every mode (seed 7375).

- The sheet was built by `tools/changed_sheet.py` and committed empty in `685f22d`.
- Tushar labeled it blind between 22:54:55 and 22:57:36 on 2026-11-23 (2 min 41 s).
- The labels were committed in `8d8e92f` before the group key was read.

<!-- BEGIN checks/score_report.py --section 2b output -->
Changed-postings sheet (blind labels, commit 8d8e92f): 8 changed + 8 controls = 16 rows; labels 7 keep, 7 reject, 2 cannot_tell.

### Agreement per mode

| mode | changed rows (8) | controls (8) | all 16 |
|---|---|---|---|
| v0.1 | 1/8 | 5/8 | 6/16 |
| v0.1+C1 | 6/8 | 5/8 | 11/16 |
| v0.1+C2 | 1/8 | 5/8 | 6/16 |
| v0.1+C3 | 1/8 | 5/8 | 6/16 |
| v0.1+C4 | 0/8 | 5/8 | 5/16 |
| v0.1+C5 | 1/8 | 5/8 | 6/16 |
| v0.1+C6 | 2/8 | 5/8 | 7/16 |
| v0.2 | 6/8 | 5/8 | 11/16 |

### Per change: rows it moves versus v0.1

Toward: the new verdict equals the label and the old one did not. Away: the old verdict equalled the label and the new one does not. Stayed wrong: neither equals the label.

| change | rows moved | toward my label | away from my label | stayed wrong |
|---|---|---|---|---|
| C1 | 6 | 5 | 0 | 1 |
| C2 | 0 | 0 | 0 | 0 |
| C3 | 1 | 0 | 0 | 1 |
| C4 | 1 | 0 | 1 | 0 |
| C5 | 0 | 0 | 0 | 0 |
| C6 | 1 | 1 | 0 | 0 |
| v0.2 (combined) | 7 | 5 | 0 | 2 |

#### C1 (G4: no stated experience passes)

| row | title | v0.1 | new | my label | my note | direction | decided by (new) |
|---|---|---|---|---|---|---|---|
| 2 | Software Engineer, Collections Infra | cannot_tell | keep | keep |  | toward | score 4 (topic backend, distributed systems, infrastructure, platform; skills TypeScript) |
| 3 | Software Engineer, High Availability and Disaster Recovery | cannot_tell | keep | reject |  | stayed wrong | score 4 (topic infrastructure, platform; skills Java, SQL) |
| 6 | Software Engineer, Infrastructure Security | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills AWS) |
| 9 | Software Engineer, Early Career — Immediate Start | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills Java) |
| 13 | Software Engineer, Mobile Platform (iOS) | cannot_tell | keep | keep |  | toward | score 2 (topic infrastructure, platform; skills -) |
| 14 | Software Engineer, New Grad | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills Java) |

#### C2 (G4: stated maximum that 0 years satisfies)

Moves no row on this sheet.

#### C3 (G4: cutoff 3 → 2)

| row | title | v0.1 | new | my label | my note | direction | decided by (new) |
|---|---|---|---|---|---|---|---|
| 8 | Full Stack Engineer, Web Presence and Platform | cannot_tell | reject | keep |  | stayed wrong | G4 fail (3+ years) |

#### C4 (G4: every mandatory minimum; mixed → unknown; preferred ignored)

| row | title | v0.1 | new | my label | my note | direction | decided by (new) |
|---|---|---|---|---|---|---|---|
| 4 | Software Engineer, Secrets Infrastructure | reject | cannot_tell | reject | Location not given also 5 years of minimum experience required | away | G3 unknown (na) |

#### C5 (topic words without "platform")

Moves no row on this sheet.

#### C6 (G4: "two (2) years" forms)

| row | title | v0.1 | new | my label | my note | direction | decided by (new) |
|---|---|---|---|---|---|---|---|
| 3 | Software Engineer, High Availability and Disaster Recovery | cannot_tell | reject | reject |  | toward | G4 fail (five (5) years of; three (3) years of; three (3) years of) |

#### v0.2 (combined; reported separately)

| row | title | v0.1 | new | my label | my note | direction | decided by (new) |
|---|---|---|---|---|---|---|---|
| 2 | Software Engineer, Collections Infra | cannot_tell | keep | keep |  | toward | score 4 (topic backend, distributed systems, infrastructure; skills TypeScript) |
| 3 | Software Engineer, High Availability and Disaster Recovery | cannot_tell | reject | reject |  | toward | G4 fail (five (5) years of; three (3) years of; three (3) years of) |
| 6 | Software Engineer, Infrastructure Security | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills AWS) |
| 8 | Full Stack Engineer, Web Presence and Platform | cannot_tell | reject | keep |  | stayed wrong | G4 fail (3+ years) |
| 9 | Software Engineer, Early Career — Immediate Start | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills Java) |
| 13 | Software Engineer, Mobile Platform (iOS) | cannot_tell | reject | keep |  | stayed wrong | score 1 (topic infrastructure; skills -) |
| 14 | Software Engineer, New Grad | cannot_tell | keep | keep |  | toward | score 3 (topic backend, infrastructure; skills Java) |

### Confusion matrix, v0.1 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 1 | 6 | 2 |
| **cannot_tell** | 6 | 1 | 0 |

### Confusion matrix, v0.1+C1 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 5 | 1 | 0 |
| **reject** | 1 | 6 | 2 |
| **cannot_tell** | 1 | 0 | 0 |

### Confusion matrix, v0.1+C2 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 1 | 6 | 2 |
| **cannot_tell** | 6 | 1 | 0 |

### Confusion matrix, v0.1+C3 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 2 | 6 | 2 |
| **cannot_tell** | 5 | 1 | 0 |

### Confusion matrix, v0.1+C4 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 1 | 5 | 2 |
| **cannot_tell** | 6 | 2 | 0 |

### Confusion matrix, v0.1+C5 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 1 | 6 | 2 |
| **cannot_tell** | 6 | 1 | 0 |

### Confusion matrix, v0.1+C6 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 0 | 0 | 0 |
| **reject** | 1 | 7 | 2 |
| **cannot_tell** | 6 | 0 | 0 |

### Confusion matrix, v0.2 (all 16 rows)

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 4 | 0 | 0 |
| **reject** | 3 | 7 | 2 |
| **cannot_tell** | 0 | 0 | 0 |
<!-- END checks/score_report.py --section 2b output -->

**What section 2b shows (direction only).**
- **C1 moved 6 rows: 5 toward the label and 1 stayed wrong.** Each of the six went from cannot_tell to keep. The one that stayed wrong is row 3: it states "five (5) years", which v0.1 cannot read, and you labeled it reject.
- **C6 moved that same row 3 toward the label** (cannot_tell → reject on "five (5) years of"). Combined in v0.2, C1 and C6 get row 3 right.
- **C3 moved row 8 from cannot_tell to reject** on "3+ years"; your label is keep, so it stayed wrong. That fits C3 being a search-scope choice rather than something the labels support. On this row, at least, you would accept a 3-year minimum.
- **C4 moved row 4 away from the label**, from reject to cannot_tell. The posting states mandatory minimums of 3+ and 5+ years, and C4 calls that mixed. Your note gives the reason you'd reject it: "Location not given also 5 years of minimum experience required". C4's mixed → unknown rule doesn't reject on the higher minimum.
- **C2 and C5 alone move no row here.** In v0.2, C5 contributes to row 13 staying wrong. C1 lets the row reach the score, and without "platform" it scores 1 and is rejected; you labeled it keep. That only shows up in combination.
- **v0.2 moved 7 rows: 5 toward, 0 away, 2 stayed wrong** (rows 8 and 13). Changed-row agreement goes from 1/8 to 6/8.
- **The controls stay at 5/8 in every mode,** because no mode moves them by construction.

**Limits of section 2b.**
- **Selected, not random.** The 8 changed rows were chosen *because* a change moves them, so their agreement is not an estimate of how often the filter is right on postings in general. Only the 8 controls are a random draw, and they are an unchanged-by-construction group.
- **n is tiny.** There are 8 changed rows, and each change moves at most 6 of them. One row more or less is the whole difference.
- **This tests direction, not a rate.** It answers "when this change moves a posting, does it move it toward Tushar's blind judgment?" It does not give an error rate for any mode.
- **Labeling pace.** The sheet was labeled faster than the audit sheet: the gaps between rows were 3–35 s, with a median of 7 s. None was the 1-second pattern of the discarded first audit pass, and the verdicts are mixed.
- **Rules were not revised** after this measurement; they remain as frozen at `f3edf99`.

## 3. Honest limits

- **30 rows is small.** The held-out labels are 4 keep, 24 reject and 2 cannot_tell. Every mode scores 24/30 (80.0%), with a Wilson 95% interval of **62.7% – 90.5%**. A difference of 1–2 rows between modes would be within noise; here there is no difference at all, because no row moved.
- **Held-out label quality.** 4 held-out rows labeled keep are non-engineering titles (rows 7, 24, 27; plus 25 Technical Operations Engineer) and look like the same labeling slip as audit row 19. They were NOT corrected, to keep the held-out set blind, so held-out agreement measures label quality as well as the filter. Rejecting everything also scores 24/30 on this set.
- **The audit sheet overstates C1–C6.** They were chosen after reading the 48 audit rows, so audit agreement (v0.1 28/48 → v0.2 34/48 on blind labels; `audit/AUDIT-RESULTS-v0.2.md`) is development data. The held-out set is the fairer test, but it is small, and this draw gave it nothing to separate the modes. A fair measurement of C1–C6 needs new blind labels on postings these changes actually move, such as the 7 non-audit postings v0.2 changes, labeled before looking at their verdicts.
- **Nothing was trained.** Claude, the model, did not change. Every behavior change in this project is a change to a file: FILTER.md and `agent/filter.py`. Running it again tomorrow and getting the same results shows that the file changed and is deterministic, not that anything learned.
- **Rules were not revised after this comparison.** FILTER.md v0.2 says: "Decisions frozen 2026-11-23 before any held-out comparison. … Rules will not be revised in response to held-out results." The rules are as committed in `f3edf99`; this commit adds only the report, its script and its test.
- **The held-out postings' text was seen before the freeze, but their labels were not.** The C4 heading definition came from a survey of heading markup across all 979 postings, which included the 30 held-out postings. No held-out label was read before this report.

2026-11-25: agent/claims.py and tools/mcp_server.py were added after this report; agent/filter.py is unchanged since f3edf99
