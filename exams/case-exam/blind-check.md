# Blind check of the rubric (2026-11-08)

Cases tested: ch01, ch05, ch09, ch10, ch14. Four AI readers saw the **student page only** (no keys) and answered Q1 to Q4. I then scored each answer with the case key, as a TA would.

| Reader (instruction) | ch01 | ch05 | ch09 | ch10 | ch14 |
|---|---:|---:|---:|---:|---:|
| A: careful student (Sonnet) | 10 | 10 | 10 | 10 | 10 |
| B: rushed, few terms (Haiku) | 9 | 10 | 10 | 10 | 10 |
| C: fluent, jargon-heavy (Sonnet) | 10 | 10 | 10 | 10 | 10 |
| D: told to miss the flaw and write fluently about a neighbouring topic (Sonnet) | 2 | 1 | 2 | 2 | 1 |

## What the check found
1. **The key separates found-the-flaw from missed-the-flaw sharply.** Every genuine reading scored 9-10; every missed-flaw answer scored 1-2, far under the 5-point cap. D's answers were polished: a Wilson confidence interval (ch01, ch14), a TOCTOU symlink race (ch05), t-test normality (ch09), lock contention (ch10). None identified the planted flaw. The CAP RULE did its work, and the points D collected were only partial fix and plain-language points.
2. **Ceiling effect.** Readers A to C all caught every flaw, so 9-10 is what "caught it" earns. The 6 in each key (flaw seen in plain words, term vague, evidence vague) was not produced by any reader. The middle of the scale is therefore **untested with real answers**; the "typical ~6" samples are author-written. Pilot with real students and replace the samples.
3. **Strong models find these flaws easily**, helped by Q1 asking for "the exact term". Students may do worse; the key makes no assumption about that.
4. **Near-miss terms did what they should.** B's and A's "consistency vs accuracy" / "reliability vs validity" in ch01 scored Catch 3, Term 1 (one point lost), and the key now states this.

## Rubric fixes made
- **ch05 key inconsistency:** the Zero list said "TOCTOU" earns nothing but the fluent-but-wrong sample gave a term point for it. Sample reason now credits only "path traversal" (half) and the Zero list names TOCTOU/symlink race explicitly.
- **Decoy answers added to Zero lists** for the exact wrong answers D produced: ch01 (confidence interval, more runs), ch09 (t-test assumptions, effect size), ch10 (lock contention, isolation), ch14 (confidence interval, undercounting).
- **README Q4 rule:** the plain-language point now requires being accurate about the *planted* flaw, so a clear note about a different problem scores 0.

## Limits
- Four AI readers, five of sixteen cases; the other eleven cases were not blind-tested.
- Readers are not students: no second-language writing, no time limit, and A to C read carefully.
- D is a role-play told to miss the flaw; it shows the cap works on fluent decoys, not how often real students miss.
- Scoring was by one person (the author of the key), so inter-TA agreement is not measured. The calibration step in the README is meant to measure it.
