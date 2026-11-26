# Reject audit: filter v1 on the 2026-11-25 snapshot

**What ran.** `python3 run_filter.py --version v1` ran on 1,088 postings fetched live on 2026-11-25: Stripe 772,
Figma 142 and Notion 174 ([log](evidence/logs/02-run-v1.txt); raw responses in `data/raw/2026-11-25/`). v1 kept
**25** and rejected **1,063**:

| reject reason | count |
|---|---|
| no role word in title | 981 |
| topic score 0 | 35 |
| topic score 1 | 31 |
| level excluded (Senior/Staff/Principal/Lead/Sr.) | 16 |

**Sample (seeded, seed 7375, commit `a2a4f120`).** It has three strata, shuffled together. The judging sheet
[audit/to-judge.md](audit/to-judge.md) hid the filter's verdict:

- 32 random rejects, drawn from the rejects that were not close calls
- 12 close calls, from the 46 postings with a role match, not level-excluded, and topic score 1 or 2
- 10 random keeps, drawn from keeps that were not close calls

**Hand verdicts.** Arundhati typed all 54 in chat on 2026-11-25, without seeing the filter's verdicts. They are stored
verbatim in [audit/my-verdicts-2026-11-25.txt](audit/my-verdicts-2026-11-25.txt) and merged into
[audit/sample.csv](audit/sample.csv). One verdict was **changed after the results were seen**: #26 went from Y to N,
because "Both explicitly ask for 5+ years… apply the same experience rule consistently"
([decisions](audit/my-decisions-2026-11-25.txt)). The table below uses the original blind verdicts, and the
revised one is noted.

## Results (blind verdicts)

| stratum | n | filter agreed with me | filter wrong | 95% interval for this stratum's error rate (exact binomial) |
|---|---|---|---|---|
| random rejects | 32 | 32 | **0** | 0%–10.9% (two-sided); one-sided upper bound 8.9% |
| close calls | 12 | 9 | 3 (#13 and #54 were rejected but I said Y; #51 was kept but I said N) | 5.5%–57% |
| random keeps | 10 | 2 | **8** were kept but I said N | 44%–97% |

### What a sample this size can honestly say

- **0 wrong out of 32 random rejects does not mean the rejects are clean.** A sample of 32 is consistent with up to
  about 9% of the non-close-call rejects being wrong, and those rejects number 1,063 − 31 = 1,032. That could be as
  many as about 90 relevant postings I never see. The data only shows the miss rate is probably not large. It
  doesn't show it is zero.
- **Most random rejects were easy.** 29 of the 32 had no role word in the title (sales, HR, account management); the other 3 were #1 and #14 (topic score 0) and #6 (Staff), so
  the sample mostly tested the role-word rule on easy cases. The rejects that are hard to judge are the 66 with a
  role title and a topic score of 0–1, and a uniform random sample barely touches them. That is why the close calls
  were sampled separately.
- **The keep side is where v1 was clearly wrong.** 8 of 10 keeps were postings I would skip. Even at the low end of
  the interval (44%), the v1 shortlist is mostly noise. This is a sample estimate for the 25 keeps. It is not a
  measured rate for all postings.
- The 12 close calls are a sample of 12 out of 46, so 3/12 says very little (5.5%–57%).

## Why v1 was wrong (from my notes on each disagreement)

| # | posting | filter | me | my note | cause |
|---|---|---|---|---|---|
| 15 | Software Engineer, Payin (Bengaluru) | keep | N | Bengaluru location | location only *preferred* in v1 |
| 43 | Software Engineer, Financial Business Insights (Bengaluru) | keep | N | Bengaluru location | same |
| 20 | Software Engineer, Data Orchestration (N/A) | keep | N | location unclear, data platform role | location unknown + false friend (below) |
| 28 | Software Engineer, Secrets Infrastructure (na) | keep | N | location unclear, infrastructure role | same |
| 21 | Software Engineer – Distributed Systems (Figma) | keep | N | 5+ years required | no years rule in v1 |
| 33 | Software Engineer, HA and Disaster Recovery | keep | N | experience requirement exceeds early-career target | no years rule ("five (5) years") |
| 45 | Software Engineer, Data Warehouse Analytics | keep | N | 4 years required | no years rule ("four (4) years") |
| 35 | Software Engineer – Application Platform (Figma) | keep | N | Ruby-focused backend platform | topic words matched; no stack rule |
| 51 | Software Engineer, Collections Infra (Notion) | keep (close) | N | TypeScript-focused, not Java backend | false friend (below) |
| 13 | Software Engineer, New Grad (Stripe US) | reject (close, score 1) | Y | (none) | new-grad postings are short on stack words |
| 54 | Backend Engineer, Developer & End-user Experience Platform | reject (close, score 1) | Y | backend role, US; seniority unclear | same |

## False friends: words that matched for the wrong reason

My expected false friend in FILTER.md was "training". It is not one of my topic words, so it couldn't fire. The
audit found these instead:

1. **"distributed systems" (T8)** matched team-description prose rather than a requirement. In #28 it was in
   "We build foundational security infrastructure at scale…", and in #21 in "At Figma, infrastructure is at the heart
   of everything we build…". In #51 it was a *curiosity* line: "Curiosity about distributed systems,
   microservices, and data-layer trade-offs; experience in these areas is helpful". T8 fired in 12 of the 13 keeps in
   the sample (10 random keeps plus 3 close-call keeps).
2. **"Java" (T1)** matched Stripe's company-wide sentence that appears in every Stripe new-grad and intern posting:
   "We work mostly in Java, Ruby, JavaScript, Scala, and Go. We believe new programming languages can be learned…"
   (#13, #24, #36). It tells you about Stripe, not about the role. In #20 and #28, "Java" was in the team "About"
   paragraph.

## Rules added, cut, and rejected after measuring (FILTER.md v1.1)

These are measured on the 54 audit verdicts, which are the dev set
([log](evidence/logs/06-filter-heldout.txt), after both parser fixes). Arundhati made the decisions, and her reasons
are in [FILTER.md § Revisions](FILTER.md#revisions).

| change | audit agree (v1: 42/54) | kept of 1,088 (v1: 25) | decision |
|---|---|---|---|
| A: require US | 46/54 | 16 | **rejected**: "The US should be a preference, not a hard requirement." |
| B: reject if 3+ years explicitly required | 50/54 | 13 | **added** |
| C: threshold 2 → 1 | 37/54 | 56 | **rejected**: "would let too many loosely related jobs through" |
| D: topic words only in requirement/responsibility sections | 44/54 | 12 | **added** (aimed at the false friends above) |
| v1.1 = B + D | 49/54 | **4** | current |

The "audit agree" column for v1 is 42, not 43, because #26 was revised to N. For comparison, rejecting everything
would agree on 48/54 of the audit set, so agreement alone overstates v1.1. See [SCORE-CHANGES.md](SCORE-CHANGES.md).

**Two code defects were found during the audit and fixed test-first.** Neither is a rule change:

1. Headings with a curly apostrophe ("What you’ll do") were not recognised as requirement sections. Test
   `CurlyApostrophe`; logs 07 → 08; commit after `8c02746e`.
2. "four (4) years" was not read as a years requirement, and a sub-skill line ("one (1) year in each of…") hid the
   base requirement. Tests `SpelledYears` and `StrictestYearsWins`; logs 10 → 11.
