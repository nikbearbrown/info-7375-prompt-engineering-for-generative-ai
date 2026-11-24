# AUDIT.md — Job-Search Agent 3: the reject audit

**Author:** Prasad Shinde
**Written:** 2026-11-18, before the audit draw and before any audit verdict
**Version:** v1.3 — 2026-11-20
**Rests on:** FILTER.md v1.1 (JS3-CP5a) and its first run, output/filter_v1_2026-11-17T210612Z/ (JS3-CP5d). Hand verdicts follow FILTER.md §5. The 50 sealed postings (SEAL.md) are not in this audit: the run never judged them.

## 1. What the audit is for
(Brief: "Run your filter on everything your agent collected. Then audit it.")

FILTER v1 judged 1,248 postings and kept none: every one is not_relevant (summary.txt). The audit asks how many of those rejects were wrong — postings worth Alex's time under FILTER.md §5 — and which words matched for the wrong reason.

## 2. What is audited
Three groups, all taken from output/filter_v1_2026-11-17T210612Z/verdicts.tsv:

- **(A) Random rejects:** 30 postings, a uniform random sample of all 1,248 rejects. It is the only group that supports a rate.
- **(B) Closest calls:** all 42 in closest_calls.tsv. 38 have a non-target title, a workable location and 2 or 3 skills; 4 have a target title, a workable location and 1 skill.
- **(C) Both gates pass:** all 27 postings with a target title and a workable location (23 with no skill, 4 with one). The 4 with one skill are also in (B).

A posting in more than one group is labeled once and counted in each group it belongs to.

**Kept sample:** none from v1, because FILTER v1 kept no posting. The kept sample is taken from FILTER v2's kept set instead: every kept posting if there are 30 or fewer, otherwise the 30 lowest ranks under §3's seed. A kept posting already labeled in this audit keeps its verdict.

## 3. The draw for group (A)
The seed is js3-audit-2026-11-18, fixed here before the draw. Each reject's rank is the SHA-256 of `js3-audit-2026-11-18:<board key>:<id>`, in lowercase hex, and the 30 lowest ranks form group (A). No draw had been computed with this or any other seed when this file was committed. A rerun after a bug fix uses the same seed, and both outputs are kept.

## 4. Labeling
- Every audited posting gets a hand verdict under FILTER.md §5 (worth / not_worth / unclear, with parts and evidence), the same as the held-out labels.
- **Blind:** the viewer shows only the posting's own text (FILTER.md §2), in an order shuffled by the same seed, with no group, rule verdict, condition, score or matched term. The rule's details appear only in the comparison, after the hand verdicts are committed.
- Any of the 30 exposed postings (SEAL.md §8) that fall in the audit are labeled fresh, and the overlap is counted.
- Hand verdicts are development data. They live in audit/ in this folder, and they are committed before the comparison runs.

## 5. What counts as wrong, and what can be said
- A reject is wrong when the hand verdict is worth. not_worth confirms the reject. unclear is counted separately, as neither right nor wrong.
- Group (A) gives a rate: k wrong out of 30, with an exact (Clopper–Pearson) 95% interval. With 30 postings, even 0 wrong leaves an interval of 0% to about 11.6%, so the audit reports the interval, not only k.
- Groups (B) and (C) are chosen, not random. They give counts, never a rate for the corpus.

## 6. False friends
A false friend is a word the rule matched for the wrong reason. After the hand verdicts are committed, the comparison lists every audited posting where a condition passed but the hand verdict failed that part: C1 passed, but role or level failed by hand; or C2 passed, but location failed by hand. It also shows each matched skill in its sentence. At least one false friend is named in §8, taken from those rows, specific to PM/APM roles, with the posting and the matched word.

## 7. Results

The audit ran in three passes, all on the same 94 postings and the same run, and every pass is committed.

| Pass | Hand verdicts | When | What changed |
|---|---|---|---|
| 1 | audit/hand_verdicts.tsv (JS3-CP6d) | Blind, before any comparison | — |
| 2 | audit/hand_verdicts_r2.tsv (JS3-CP6f) | After the first comparison (JS3-CP6e) | 19 rows, under §5 as written: 12 Staff and 1 Senior title with no years of 3 or less stated; 3 rows whose text asks for more than 3 years; 2 unclear rows decided; and 1 edit that landed on row 31 when it was meant for row 32 |
| 3 | audit/hand_verdicts_r3.tsv (JS3-CP6i) | After the second comparison (JS3-CP6g) | 4 slips from pass 2 corrected: rows 31 and 32 (the off-by-one), and rows 45 and 60, where skills or a Product Operations title had rescued a role §5 rules out |

Every change is in audit/recheck_notes.txt, with the §5 sentence that decides it. Passes 2 and 3 were not blind: I made them after seeing the comparisons. Every change in them moved a verdict toward not_worth, which makes FILTER v1 look better, so all of them are listed. The cause of most of pass 2: I read Staff PM as an ordinary PM title, when on most PM ladders it sits above Senior.

Wrong rejects (a reject whose hand verdict is worth), by pass:

| Group | n | Pass 1 | Pass 2 | Pass 3 |
|---|---|---|---|---|
| (A) random rejects | 30 | 0 | 0 | 0 |
| (B) closest calls | 42 | 4 | 3 | 1 |
| (C) both gates pass | 27 | 21 | 4 | 3 |
| All audited | 94 | 22 | 6 | 3 |

Pass 1 also had 2 unclear verdicts; passes 2 and 3 have none. Pass 3 follows §5 as written, and it is the pass the rule changes are measured on (audit/compare_2026-11-19T030012Z/).

What the numbers can say:
- **Group (A):** 0 wrong rejects out of 30, with an exact 95% interval of 0% to 11.6%. A sample this size cannot rule out that up to about 1 reject in 9 across the corpus is wrong. It says the rejects are mostly right; it does not say they are all right.
- **Groups (B) and (C)** were chosen, not drawn at random, so their counts are not corpus rates. They show where the wrong rejects are: all 3 are product-management postings with a target title and a workable location, rejected by C3 with scores of 0, 0 and 1 (positions 8, 58 and 62).
- **Kept sample:** none could be audited, because FILTER v1 kept no posting.
**Pass 4 and the kept sample, 2026-11-19.** Measuring FILTER v2's candidate rules found one more slip: row 62's text states "Minimum requirements 7+ years of product management experience", and my pass-3 verdict had marked it worth. Pass 4 (audit/hand_verdicts_r4.tsv, JS3-CP7e) corrects that one row. Its comparison (audit/compare_2026-11-19T194307Z/, JS3-CP7f) gives group (A) 0 wrong of 30 (0% to 11.6%), group (B) 0 of 42 and group (C) 2 of 27: 2 wrong of 94 in all (rows 8 and 58), both killed by C3 with a score of 0. The correction was found by the rule, not by re-reading, and it makes the filter look better, so it is recorded as found by the rule (audit/recheck_notes.txt). FILTER v2 was measured on pass 4 (FILTER.md §6).

**The kept sample** (§2): FILTER v2 keeps 2 development postings (output/filter_v2_2026-11-19T201210Z/), so both are the kept sample. Both were already audited and keep their verdicts: both worth (rows 8 and 58). Two of two kept postings are worth; a sample of 2 supports no rate. SHORTLIST.md labels every claim the agent makes about them.

**Pass 5, 2026-11-20.** FILTER.md §5 v2.1, decided during the held-out re-check, says years stated only under preferred qualifications do not fail level. Rows 31, 57, 71 and 72 were re-read for it: 57, 71 and 72 state minimum requirements and are unchanged; row 31 states "Preferred Qualifications 6–10+ years" only, so it became worth (audit/hand_verdicts_r5.tsv, JS3-CP11c). Pass 5's comparison (audit/compare_2026-11-20T205044Z/) gives 3 wrong rejects of 94 (rows 8, 31 and 58), all in group (C); group (A) is still 0 of 30. Against pass 5, FILTER v2 keeps 2 of the 3 and misses row 31, because F10 counts preferred years (FILTER.md §6).

## 8. False friends found

**"Product Manager", matched inside "Staff Product Manager" and "Senior Product Manager".** F3 passes a title that contains a target title, and "Product Manager" is a target title, so a Staff or Senior title passes C1. The word is right; the level is not. In pass 3, 25 audited postings passed C1 while my verdict failed them on level (audit/compare_2026-11-19T030012Z/false_friend_candidates.tsv):
- 20 are Staff (12) or Senior (8) Product Manager titles. The title word matched for the wrong reason: the seniority word in front of it puts the role above Alex's 3 years.
- 5 are plain Product Manager titles whose text asks for more than 3 years ("5+ years", "8+ years", "6–10+ years"). Here the title word matched for the right reason. What fails is the level, which no v1 rule reads (CONTRACT §4 leaves max_years_required out).

Why it is specific to PM roles: PM ladders put the level in front of the role word (APM, PM, Senior PM, Staff PM, Principal or Group PM), so a role-word match cannot see the level. I made the same mistake myself in pass 1, and the audit caught it (§7). CONTRACT §4 already listed Senior, Staff and Lead Product Manager passing C1 as a known consequence; the audit turns that note into a measured count.

In FILTER v1 this false friend causes no wrong keep, because C3 rejects all 25 of these postings anyway. It turns into 25 wrong keeps the moment C3 is loosened, which is what the 3 wrong rejects call for. So a change to C3 is measured together with a change for level (FILTER.md v2).

## Changelog
- **v1 — 2026-11-18.** Written and committed before the audit draw. Claude (Claude.ai) proposed the design (A1–A5) and typed this text at my request; the decisions are mine.
- **v1.1 — 2026-11-19.** §7 and §8 written, after all three passes and their comparisons. Claude (Claude.ai) typed them at my request from the committed files; the facts and decisions are mine.
- **v1.2 — 2026-11-19.** Pass 4 and the kept sample added to §7. Claude (Claude.ai) typed them at my request from the committed files; the facts and decisions are mine.
- **v1.3 — 2026-11-20.** Pass 5 added to §7. Claude (Claude.ai) typed it at my request; the facts and decisions are mine.