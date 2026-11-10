# Review packet: rule v2 (Chapter 6)

*Assembled by Claude Code on 2026-11-09 from the files in `review/` and the commit history. The decisions and the command runs marked as Shreyash's are Shreyash's, quoted word for word in `review/05`, `review/18`, `review/04` and `review/17`.*

## What I understood from the diffs

*Shreyash's words, typed into the session on 2026-11-10. Claude Code did not change them.*

The main thing I learned from reviewing these revisions is that passing tests does not always mean the code is making the right decisions.

In revision 1, the code treated a benefit as an experience requirement. The phrase "based on country requirements" appeared inside the benefits section, but the parser interpreted it as the start of a requirements section. Because of that, 16 Linear postings were incorrectly flagged for the four-year paid-time-off benefit. All 84 tests passed, but the behavior was still wrong.

Revision 2 fixed that problem but introduced another one. When the parser encountered words such as "preferred" within a bullet point, it sometimes treated later mandatory requirements as optional. Around 37 genuine experience requirements were missed.

Revision 3 took a more focused approach by evaluating each experience phrase within its own sentence instead of applying one heading to everything that followed.

Before accepting the final revision, I considered the test results, the changes in failure reasons across 685 saved postings, whether the patch stayed within scope, and the remaining limitations. I accepted revision 3 because the specific problem was corrected, not because the tests were simply green.

## Index of review/ (read in this order)

| File | What it is | Whose |
|---|---|---|
| 01 | the test run before any patch: 10 of 15 fail | run |
| 02, 03 | rev 1: behavior diff; finding (the perk read as a requirement) | Claude Code |
| 04, 05 | rev 1: Shreyash's three commands; the **revise** decision | **Shreyash** |
| 06 | the regression test fails on rev 1 | run |
| 07, 08 | rev 2: tests; correction of one test's expectation | run, Claude Code |
| 09, 10, 11 | rev 2: behavior diff; failures it drops; finding (about 37 requirements lost) | Claude Code |
| 13 | the second regression test fails on rev 2 | run |
| 14, 15, 16 | rev 3: tests; behavior diff; reading | run, Claude Code |
| 17, 18 | rev 3: Shreyash's three commands; the **accept** decision | **Shreyash** |

| 19 | three open items settled after reading the ads: 7809608003, the two Linear ads, Palantir `Dev` | **Shreyash** |

There is no 12; that check went into 16.

## The change Shreyash asked Claude Code to make

GATE.md section 8 asks for a fix to the three JS1 rule defects Shreyash found on 2026-10-31:

- **Experience:** count only mandatory qualifications.
- **Hybrid:** reject hybrid or in-office jobs even when they carry a "Remote" tag.
- **Massachusetts:** count a remote job only if it can be done from Massachusetts.

It is non-trivial because experience and location are read out of free ad text, in three different applicant-tracking systems' formats.

## 1. The defect reproduced, and the test written before the patch

| Step | Commit | Evidence |
|---|---|---|
| Real postings copied unchanged from JS1's saved raw files, with sha256: the five Shreyash reviewed, Klaviyo 7783904003, and Shreyash's four Klaviyo positives as a guard | `6f4ae08` | `tests/fixtures/js1_real_postings.json` |
| Test written before any patch: 6 real defects, 1 guard test, 8 constructed edges | `6f4ae08` | `tests/test_rule_v2.py` |
| Run on rule v1: 10 of 15 fail, including all 6 real defects | `6f4ae08` | `review/01-reproduce-before-patch.txt` |
| Shreyash re-ran it in Shreyash's own terminal: `Ran 15 tests … FAILED (failures=10)` | — | `review/04-commands-run-by-shreyash-2026-11-09.txt` |

## 2. The diff read as a change in behavior

Each revision was run with the old rule and the new one over the same **685 real postings** from live run 1. The reading looked at every condition a revision stopped failing, and at the new failures by phrase.

| Revision | Tests | Behavior on 685 real postings | Verdict |
|---|---|---|---|
| rev 1 (`b0498a5`) | 84/84 | 0 verdict changes, 156 condition changes. **16 Linear postings fail experience on a perk**: "Paid month off after 4 years & every 2 years thereafter", read as a requirement because "Health coverage (based on country requirements)" looked like a heading. It also dropped 20 real Palantir requirements; see "What the reading missed at first". | defect, `review/02`, `review/03` |
| rev 2 (`67ddba8`) | 86/86 after a test correction (`review/08`) | The perk is gone (0/685). But **about 37 real requirements vanish**: text after an unknown heading ("What We Require:", "Education and Experience:") or after an inline "preferred"/"a plus" was read as optional. | defect, `review/09`, `review/10`, `review/11` |
| **rev 3** (`ba0a5b0`) | **93/93, no test edited** | 0 verdict changes against v1, rev 1 and rev 2. No posting quotes the perk. Against v1: experience failures moved on 50 postings (8 dropped, all under "Preferred skills" or "Preferred experience"; 42 added, all real mandatory minimums), location on 53 (8 dropped where the state list includes Massachusetts; 45 added for state-limited remote or hybrid ads). | accepted, `review/14`, `review/15`, `review/16` |

**Against Shreyash's per-condition hand labels** (JS1 experiment 2, 20 Klaviyo postings), the failed-condition sets went from **18/20 (v1) to 19/20 (rev 3)**. The verdict stayed 20/20. The one remaining miss, 7809608003, turned out to be a hand-label slip: after reading the ad, Shreyash found it names only Python of Alex's skills, so the rule's condition-4 failure is right (`review/19`).

**What the reading missed at first.** Rev 1's diff was only sampled, so 20 Palantir postings it had silently stopped failing were not seen until rev 2's diff showed them coming back. From rev 2 on, every condition a revision stops failing was listed and read (`review/10`, `review/15`).

## 3. Did the change stay in scope?

Shreyash's own run on rev 3, `git diff 6f4ae08 ba0a5b0 --stat -- jsagent tests`, is in `review/17`:

- **Code:** only `jsagent/rule.py` (+102 / −6 lines, from `git diff --numstat`). The loop, the policy, the providers and the check were not touched.
- **One existing test changed on purpose.** In `tests/test_rule.py`, a JS1 test asserted that "Remote (Florida)" passes. Shreyash's 2026-10-31 decision reverses that, and the test says so in a comment.
- **One new test corrected after running.** In `tests/test_rule_v2_regression.py`, the first version said none of the 16 Linear postings fails experience. Two state real requirements ("8+ years in a Solutions Engineering…", "7+ years in a quota-carrying sales role"), so the test now asserts those two fail **with their own requirement quoted** (`review/08`). It has more assertions than before, not fewer.
- **Everything else is new tests and real fixtures.** Every test file's sha256 is recorded in `tests.frozen.sha256`; `shasum -a 256 -c tests.frozen.sha256` checks them.

## 4. Commands Shreyash ran

| When | Commands | Output | File |
|---|---|---|---|
| 2026-11-09, on rev 1 | the pre-patch test result; the full suite; the count of perk lines | `FAILED (failures=10)`; `Ran 84 tests … OK`; `16` | `review/04` |
| 2026-11-09, on rev 3 | the scope diff; the full suite; the behavior summary | 6 files, code only in rule.py; `Ran 93 tests … OK`; 0 verdict changes, 0 perk quotes, 19/20 | `review/17` |

## 5. Decisions, with the evidence

- **Rev 1: revise** (Shreyash, `review/05`): "I don't want to accept the patch just because the tests are green."
- **Rev 2: no separate decision by Shreyash.** Claude Code's reading of its diff (`review/11`) rejected it before Shreyash saw it, under the rev 1 instruction to "fix the perk misread, add regression tests … and rerun the tests before accepting it."
- **Rev 3: accept, with known limitations** (Shreyash, `review/18`).

## Cases the tests would still miss

1. **An office tag beats the ad.** Oscar's *Physician Reviewer – Utilization Management* has the office "Remote (Arizona)", but the ad says "reside in the United States". Rev 3 trusts the tag and fails condition 3. The verdict is unchanged because the title fails condition 1, but a software job written the same way would be wrongly rejected. No test has a state-tagged office with a nationwide ad.
2. **Location field against office list.** Klaviyo lists postings with location "San Francisco, CA" and office "Boston". Rev 3 reads the location field only. Shreyash has not decided which field wins.
3. **The reading is pattern-based.** A requirement written with no number ("several years"), or a preferred heading the cue list does not know ("Extra credit:"), is read wrong. The tests cover only the phrasings seen in these 685 postings.
