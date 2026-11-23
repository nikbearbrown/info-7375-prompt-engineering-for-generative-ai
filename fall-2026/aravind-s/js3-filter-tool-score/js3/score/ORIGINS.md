# Where every number in the score comes from (FILTER.md v1.0)

The brief, step 2 item 4: "Your scorer has numbers in it: weights, thresholds, a Claude prompt. For each, say where it
came from: hand-set, fitted on your labels, or inherited." Written by Claude Code on 2026-11-22 from FILTER.md,
Aravind's four drafts (`filter-drafts/`) and contract v0.2.

**In short.** Every weight and threshold was hand-set by Aravind in FILTER.md Section 1, most of them in his second
draft. The status phrase lists were inherited from contract v0.2. A few word lists were hand-set by Claude Code in
Section 6. Jane's facts come from her profile. **Nothing was fitted on labels:** the audit, held-out and claim labels
were only used to measure. **The score has no Claude prompt:** FILTER.md v1.0 is rules only, and no model is called to
score a posting (the Claude judge from JS2 is still in the agent, but it is not part of this score).

## Weights and thresholds

| Number | Value | What it does | Origin | Where it was set |
|---|---|---|---|---|
| Starting score | 50 | every posting that passes the hard rules starts here | hand-set by Aravind | his draft 2, kept in drafts 3 and 4 |
| Per topic group | +5 | each different topic group named with an action word | hand-set by Aravind | draft 2 |
| Topic cap | 25 | at most five groups count | hand-set by Aravind | draft 2 |
| Another US place | -15 | a US location outside Jane's areas (R2) | hand-set by Aravind | draft 2 |
| Location "cannot tell" | -10 | a missing or unclear location (R2) | hand-set by Aravind | draft 2 |
| Employment type "cannot tell" | -10 | a missing employment type (R1) | hand-set by Aravind | draft 2 |
| Start "cannot tell" | -10 | an unclear start date (R6) | hand-set by Aravind | draft 4 |
| Years "cannot tell" | -10 | an unclear years sentence that asks more than 3 years (R7) | hand-set by Aravind | draft 4 |
| Shortlist cutoff | 60 | the shortlist's minimum score | hand-set by Aravind | draft 2; his reason in draft 4: "a posting needs at least two different technical topic groups to reach the cutoff when there are no penalties" |
| Shortlist size | 10 | the shortlist's length | hand-set by Aravind | draft 2 |

## Facts about the person

| Number | Value | What it does | Origin |
|---|---|---|---|
| Jane's years of full-time experience | 3 | R7's limit | a fact in `persona/jane-doe.json`; also copied into Section 7 as `years_max` (FILTER-CHANGES-PENDING.md, item 3, moves it back to the persona only) |
| Jane's earliest full-time start | May 2027 | R6 | a fact in `persona/jane-doe.json` |

## Word lists (counts)

| List | Count | Rule | Origin |
|---|---|---|---|
| Level words | 15 | R3 | inherited from contract v0.2, kept by Aravind (his drafts made them hard rejects again) |
| Role phrases | 12 included, 17 excluded | R4 | inherited from contract v0.2 (10 and 19), changed by Aravind in draft 4: Machine Learning Engineer and ML Engineer added (his reason: "genuine engineering roles involving building software and technical systems"), ML and Machine Learning no longer excluded |
| U.S.-person and sponsorship phrases | 9 and 9 | R5 | inherited unchanged from contract v0.2, check 5 (Section 6, item 4) |
| "export control" | 1 phrase, 0 points | R5 caution | inherited: Aravind's choice of 2026-10-20 in JS2 to show it as a caution, not a reason to reject |
| Start phrases | 5 | R6 | hand-set by Aravind (Section 1) |
| Optional-years phrases | 8 | R7 | hand-set by Aravind (Section 1) |
| Topic groups, and the action words | 7 groups; 24 action words | the score | hand-set by Aravind (Section 1) |
| Annotation titles and phrases | 8 titles; 4 and 6 phrases | R8 | hand-set by Aravind (Section 1) |
| Company words | 7 | R7: a years sentence about the company | hand-set by Claude Code (Section 6, item 3); measured to misfire on real requirements (FILTER-CHANGES-PENDING.md, item 1) |
| Season, quarter and early/mid/late words | 12 | R6 "cannot tell" | hand-set by Claude Code (Section 6, item 2) |
| Number words | one to ten | R7 | hand-set by Claude Code (Section 6, item 3) |

## What the labels say about these numbers (measured, not fitted)

In the audit, Aravind kept every kept posting he judged, whatever its score: 6 of 6 at 50, 5 of 5 at 55 (2 more were
"?"), and 5 of 5 at 60. So on this sample the score does not separate the postings he would keep from the ones he
would not; the hard rules did that work (0 wrong keeps). The 60 cutoff therefore leaves out 11 of the 16 kept postings
he judged worth Jane's time. That is why the cutoff is one of the changes measured on the held-out set
(`CHANGES-TO-MEASURE.md`). No number was changed to fit these labels.
