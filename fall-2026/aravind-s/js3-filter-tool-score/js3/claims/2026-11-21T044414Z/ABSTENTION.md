# The abstention rule on real postings

Computed by Claude Code on 2026-11-22 from the filter run `js3/filter-run/2026-11-21T044414Z/verdicts.json` (1,509
postings) and Aravind's frozen claim labels (LABELS.md, commit `1608a04`).

## The rule

FILTER.md Section 2 has three levels of "I cannot tell":
1. **The whole posting:** no title or no description. The filter makes no judgment about it.
2. **One rule:** R1, R2, R6 or R7 cannot settle its question (a missing employment type, an unclear location, an
   unclear start date, an unclear years sentence). The posting is not rejected for it; it loses 10 points.
3. **One claim:** a shortlist claim whose passages do not settle it is "insufficient", never "supported" (silence is
   never support).

## How often it fired

| Level | Fired | Where |
|---|---:|---|
| 1. The whole posting | 1 of 1,509 | the OpenAI posting with an empty title |
| 2. One rule | 69 times, all R7 | all on postings another rule rejected: 0 of the 99 kept postings, 0 on the shortlist |
| 3. One claim (Aravind's labels) | 30 of 105 claims | claims 5, 6 and 7 on 10, 10 and 9 of the 10 shortlisted postings (the postings are silent on status, start and years), and claim 8 once (09.8c) |

So the filter itself almost never abstained on the postings it kept: levels 1 and 2 fired on no kept posting. Every
one of the 10 shortlisted postings rests on at least one claim that Aravind found insufficient.

## Two counterexamples from real postings

- **It let a reason through that the posting does not support.** Shortlisted posting 09 (Software Engineer, Ads
  Integrity, score 65) has a title and a long description, so level 1 did not fire, and no rule was unclear, so level 2
  did not fire. Yet 5 of its points came from "build systems" in "...build systems that consume and operationalize
  ML-based signals", where "build" is a verb: Aravind labeled that claim insufficient (09.8c), and the checker, fooled
  the same way, labeled it supported. Section 5 predicted this kind of case before the build ("a case it wrongly lets
  through"); this is a real one.
- **It abstained where the text is clear.** On audit card 34 (Data Scientist, SMB Ads Growth), R7 said "cannot tell" for
  "5+ years of experience in data science or growth analytics ...", because the company word "growth" made the sentence
  look like it was about the company. The sentence plainly asks 5 years of the candidate. The posting was rejected by
  R4 anyway, but on a posting that passes every other rule, this abstention would keep a 5-year requirement for 10
  points off.

## What v1.1 changes because of this

The shortlist's reasons should say "the posting does not say" for claims 5, 6 and 7 when no passage settles them,
instead of stating them; and the two counterexamples are the changes X3 ("build systems") and X2 (the company words) in
`js3/score/CHANGES-TO-MEASURE.md`.
