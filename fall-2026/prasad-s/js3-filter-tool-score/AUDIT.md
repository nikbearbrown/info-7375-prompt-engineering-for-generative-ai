# AUDIT.md — Job-Search Agent 3: the reject audit

**Author:** Prasad Shinde
**Written:** 2026-11-18, before the audit draw and before any audit verdict
**Version:** v1 — 2026-11-18
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
(Written after the comparison.)

## 8. False friends found
(Written after the comparison.)

## Changelog
- **v1 — 2026-11-18.** Written and committed before the audit draw. Claude (Claude.ai) proposed the design (A1–A5) and typed this text at my request; the decisions are mine.