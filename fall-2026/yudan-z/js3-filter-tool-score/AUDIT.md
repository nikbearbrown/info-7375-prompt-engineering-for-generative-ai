# AUDIT — what filter v1 threw away, judged by hand

## Executive summary

Filter v1 rejected 1,594 of the 1,595 saved postings. I labelled 61 of them by hand, without seeing the filter's score or decision. My question for each one: is this posting worth Mira's time? (Mira is the fictional new-graduate persona who needs visa sponsorship.)

The result is that v1 is far too narrow for my own definition of relevant:
- **5 of 30** randomly drawn rejects are postings I would send Mira to.
- **10 of 14** close calls are postings I would send Mira to.

This sample does not give the share of all v1 rejects that are wrong. It gives a range (§3).

## 1. How the sample was drawn (before any label)

`audit/sample-key.json` was committed in `4469e7b`, before I wrote a single verdict. It uses seed 20261125.

| Group | Rows | How drawn |
|---|---|---|
| random-reject | 30 | uniform random from v1's 1,594 rejects |
| close-call | 14 | all 9 rejects with score 4 (one point below the threshold), plus 5 random rejects with score 3 |
| kept-or-cannot-tell | 1 | the only posting v1 did not reject |
| held-out | 16 | 8 random rejects with score ≥ 1, plus 8 random rejects; **reserved for measuring changes**, see `SCORE-CHANGES.md` |

The sheet I labelled is `audit/LABEL-ME.csv`. Its rows were shuffled, and it did not show the score or the decision. Each row showed:
- the company, title and location;
- the first 350 characters of the description, plus up to three sentences about years, sponsorship, visas, degrees or graduation;
- the link.

## 2. My labels, and how they changed

My rule for **Y** is: an entry-level job in the US that Mira can apply to. That means:
- the title is not senior;
- the posting does not require citizenship or a security clearance;
- the posting does not rule out sponsorship;
- the posting does not ask for a degree she does not have.

The job does **not** have to be an analyst role. This is broader than the five target role words in the persona file. I decided this on 2026-11-25, when Claude asked which rule my labels followed.

| Pass | What happened | Commit |
|---|---|---|
| 1 | I labelled all 61 rows: 30 Y, 31 N | `2ef8ac2` |
| 2 | Claude checked my Y rows against the full posting text. It found that the sheet's excerpt had **left out** the sentence that decides the row: a security-clearance requirement (7 rows), a high-school-only fellowship (1 row) and 2–4+ year minimums (6 rows). I re-read those 14 sentences. I changed 8 rows to N (clearance, education) and kept the six with year minimums as Y | `72a0b61` |
| final | Claude pointed out that row 39 (*Senior Associate*, 4+ years) was labelled Y while rows 5, 6 and 13 (senior titles) were labelled N. I changed row 39 to N for consistency | `labels-final.csv` |

**What the recheck did not cover.** Only my **Y** rows were rechecked against the full text. An N row could also be wrong because the excerpt hid something, and nobody looked. The correction was one-sided.

## 3. The reject audit

| Group | v1 said | I said Y | I said N |
|---|---|---|---|
| 30 random rejects | reject | **5** | 25 |
| 14 close calls | reject | **10** | 4 |
| the 1 posting v1 let through ("cannot tell") | cannot tell | 1 | 0 |
| 16 held-out | reject | 5 | 11 |

**What 30 random rejects can show.** 5 of the 30 are postings I would send Mira to. A 95% Wilson interval for that proportion is **7.3% to 33.6%**. Applied to v1's 1,594 rejects, the number of wrongly rejected postings is plausibly anywhere from about 115 to about 535. The sample cannot narrow this further.

This is an estimate from 30 postings, labelled by one person (me), under my own definition of Y. It is **not** a measured error rate for all postings. Pass 1, before the recheck, gave 8 of 30, so the number also depends on how carefully the excerpt was read.

**What the misses have in common.** None of the 15 missed Y rows in the random and close-call groups has one of the five role words in its title. Examples: *Deployment Strategist, New Grad*, *Master's Data Science Internship*, *Associate, Strategic Finance*, *Solutions Architect*. v1 needed a role word (+4) to reach the threshold of 5, so v1 **could not** keep any of them. The filter did not make a mistake here. It worked exactly as written, and what it was written to do was too narrow.

## 4. The false friend: "Excel"

Topic word F2 gives +1 for `Excel`. Whole-word matching (wrong version W1) stops "excellent", but matching ignores case, so it still matches the verb:
- Databricks' standard paragraph says "an inclusive culture where everyone can **excel**";
- **927 of the 958** postings that match `Excel` contain it only in lower case.

The claim "the posting asks for skills the persona has" then quotes Excel as evidence. I did not find this in my labelling. It surfaced in the real Claude session through my tool server (`mcp/session/`, 2026-11-25): the first posting Claude scored, *Associate Product Manager, New Grad*, listed `Excel` as a matched skill. Fixed in v3 (`SCORE-CHANGES.md`, step v2f).

A second false friend appears in the same session and is **not fixed**: `Manager` as a senior word. In "Associate Product Manager, New Grad", it marks an entry-level job as senior.

## 5. Every rule, after measuring

| Rule | Status | Evidence |
|---|---|---|
| `R` as a topic word | **rejected before measuring** | one letter; matches initials and list markers (FILTER.md §1) |
| role word required (threshold 5) | **cut** in v2a | 15 of 16 dev Y rows and 5 of 5 held-out Y rows missed |
| clearance phrases | **added** in v2b | 7 rows I labelled N for clearance |
| four no-sponsorship phrases | **added** in v2c | row 41 ("not eligible for immigration sponsorship"); two phrases found while checking the film, 2026-11-23 |
| PhD in the title | **added** in v2d | row 40 |
| drop the 3+ years penalty | **rejected after measuring** (v2e) | no gain on held-out; the number shown to Mira doubled (193 → 387) |
| `Excel` only when capitalised | **added** in v2f | the false friend above; my labels cannot measure it |
| senior −3 → −5, add `Sr` | **added** in v2g | Senior titles could still reach Mira on topic words alone; my labels cannot measure it |
| strict sponsorship evidence | **added** in v4 | under v3, all three keeps cited "sponsor you for relocation" or "executive sponsorship" |
| graduation-year mismatch (rows 21, 46) | **not built** | it needs dates compared with the persona's graduation date; row 46 is still shown to Mira |

Measurements are in `SCORE-CHANGES.md` and `runs/measure.txt`.
