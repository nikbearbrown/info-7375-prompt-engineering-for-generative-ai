# One change to one object, measured on held-out labels (Chapter 9)

Claude Code drafted this report on 2026-11-24 from the committed records. The choice of the change, the held-out design, the scoring rules and every label are the student's. Claude Code wrote the options, the code and the tests. Where every number came from: [NUMBERS.md](NUMBERS.md).

## The change

| | |
| --- | --- |
| Object | The experience-minimum rule: `jobwatch.screen.EXPERIENCE_MINIMUM_YEARS`. It is `None` in v0.1 (no such rule) and 3 in v0.2. The version label moves with it. Spec: [`variants/v0.2-experience-minimum.json`](../variants/v0.2-experience-minimum.json) |
| The rule | "Reject when the description sets a minimum of 3+ years that is not marked preferred." Claude Code worded the option, and the student chose it at about 19:30 EST (FILTER.md, committed `4fec7d70` at 19:33) |
| How the description is read | Claude Code's reading, in [`jobwatch/experience.py`](../jobwatch/experience.py), pinned by 22 tests in [`tests/test_experience.py`](../tests/test_experience.py), written first (`92cecb57`) and passing at `d9f5a96e`. Claude Code designed it from FILTER.md, the development postings and the other non-held-out postings, and did not read the 30 held-out postings to write it |
| What stayed the same | Everything else: the corpus, tokenizer, role, level and topic word lists, weights, cutoff, location rule, sample and labels. `variants.applied()` patches only the named attributes. With the rule off, today's code reproduces all 1,551 committed v0.1 records (`V01UnchangedTest`) |
| Why this change | On the 50 development labels, 5 of v0.1's 6 wrong keeps state minimums of 4 to 6 years in the description, and v0.1 reads the level only from titles ([REJECT-AUDIT.md](REJECT-AUDIT.md)) |

## Before the held-out set was touched

These were all fixed in FILTER.md and in code before the run:
- **Can’t tell rows.** They are left out, and the pass mark scales to 90% of the Yes and No rows (the student: "Leave out, scale to 90%").
- **Wrong rejects.** At most one Yes may be rejected (the student's bar).
- **Unmet requirements.** No unmet requirement may be cleared. The student chose "Both": this applies to the filter's kept rows and to the shortlist claims. For the filter, Claude Code's mechanical reading is a reaching row labelled No whose reason states years without "preferred", or names a minimum, a requirement, a clearance, new graduates or entry-level applicants (`jobwatch/held_out.py`).
- **v0.2 on the development rows.** It agrees on 39 of the 41 decided rows; v0.1 agreed on 34. Wrong keeps went from 6 to 1 (P49), and the one wrong reject (P30) is unchanged ([`audit/v0.2/DEV-COMPARISON.md`](../audit/v0.2/DEV-COMPARISON.md), committed `845c8783`).
- **Across all 1,551 postings.** v0.2 keeps 27, holds 1 for review and rejects 1,523. v0.1 kept 41, held 1 and rejected 1,509.

## The held-out measurement, run once

`python3 -m jobwatch.js3 held-out runs/2026-11-24-js3-corpus --sample labels/v0.1-sample.json --labels labels/hand-labels.json --variant variants/v0.2-experience-minimum.json --out reports/held-out`, at 19:43:26 EST on top of `845c8783` ([`evidence/terminal/2026-11-24-held-out.txt`](../evidence/terminal/2026-11-24-held-out.txt)). The command refuses a second run into the same folder; that refusal was tested and then shown on the real folder (exit 1). Full table: [`held-out/HELD-OUT.md`](held-out/HELD-OUT.md).

| | v0.1 | v0.2 |
| --- | --- | --- |
| Held-out rows / Can’t tell / scored | 30 / 4 / 26 | 30 / 4 / 26 |
| Scored rows that match | 18 of 26 (69%) | **24 of 26 (92%)** |
| At least 90% match | fail | pass |
| Yes rejected | none | none |
| At most one Yes rejected | pass | pass |
| No kept (false inclusions) | P17, P18, P27, P34, P41, P53, P55, P69 | P27, P53 |
| …of which an unmet requirement was cleared | 7 (all but P27) | **1 (P53)** |
| No unmet requirement cleared | fail | **fail** |
| Every deliberate failure caught | 11 of 11 | 16 of 16 (WV1–WV4, C1–C12; `evidence/test-runs/2026-11-24-08-…`) |
| **The student's bar** | **not met** | **not met** |

**What changed:**
- **Six rows moved, and nothing else.** v0.2 rejects P17 (7+ years), P18 (6+), P34 (5+), P41 (8+), P55 (4+) and P69 (4+). The student labelled each No, giving those minimums as the reasons.
- **The rule read "preferred" the way the student did.** All three held-out Yes rows (P11, P21, P62) and all four Can’t tell rows stay kept. P21's 8+ years and P62's 5+ years appear under preferred qualifications, and the rule read them as preferred, as the student's reasons do. The rule was written without reading those postings.
- **The 15 held-out rejects stay rejected and agree under both versions.**

**What the held-out numbers can show:**
- **24 of 26 is not a rate for all postings.** The held-out set is 15 kept or review plus 15 rejected, which is not the corpus mix. The held-out option the student chose says so: "The 50/50 mix isn't the corpus mix, so agreement isn't a rate for all postings."
- **Even within this design the sample is small.** The exact 95% interval for 24 of 26 is 74.9% to 99.1%; for v0.1's 18 of 26 it is 48.2% to 85.7%.
- **The change helped on rows that guided no choice.** It removed six of the seven cleared unmet requirements, on held-out rows. It did not meet the bar.

## Why v0.2 still misses (diagnosed after the run; nothing changed)

- **P53, Pre-training Data Infrastructure Engineer.** It is kept with score 3. The student said No: "The description specifies Staff level and asks for 5+ years outside internships." The posting writes the minimum as "**5+ YOE** outside of internships". The rule's units are "years" and "yrs", so it never sees "YOE". The description also says "We are seeking a Staff level Engineer", but FILTER.md reads level words only in titles.
- **P27, Red Team Engineer, Safeguards.** It is kept with score 2. The student said No: "The core work is application security and red teaming for deployed AI products." Its one topic point is the first false friend again: "adversarial machine learning" under "Preferred qualifications".

Reading "YOE" as years, or ignoring description topics found under preferred headings, would each be a next change to one object. These 30 labels have now been used, so measuring either change would need **new** held-out labels. Neither was made.

## What "it persisted" does not prove

v0.2 is a file (`variants/v0.2-experience-minimum.json`) and a rule in the repository. A later run that behaves differently because of it shows that **the input changed**. It does not show that anything learned, or that Claude's weights moved: nothing in this project can see or change them. The test is the one above: change one object, keep the rest fixed, and measure on labels that guided no choice ([NUMBERS.md](NUMBERS.md#what-persistence-does-not-prove-here)).
