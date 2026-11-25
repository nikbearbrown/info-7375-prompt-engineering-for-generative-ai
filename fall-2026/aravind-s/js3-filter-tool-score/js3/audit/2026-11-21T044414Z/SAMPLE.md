# The audit sample, filter run 2026-11-21T044414Z

Drawn by `tools/audit_kit.py` with seed **20261121** (card order shuffled with seed 20261122), before any verdict existed. The rule is in the tool's docstring:

1. Random rejects: a uniform random sample of the rejected postings (the only part that supports a rate).
2. Close calls: kept postings scoring 55 or 60 (one topic group either side of the 60 cutoff), drawn at random; then rejected postings that failed exactly one hard rule, one at random for each rule that has such postings, then more at random from all of them.
3. Kept sample: a uniform random sample of the other kept postings.

| Group | Cards |
|---|---:|
| random reject | 30 |
| kept sample | 10 |
| close call: kept near the cutoff | 8 |
| close call: failed one rule | 7 |
| total | 55 |

Which card belongs to which group, and what the filter decided, is in `sealed/answers.json` (SHA-256 `b812a56034ab763ce429eeef5ff2de40e9d688dc454bcc4a2709709b6b107e86`). It is opened only after the verdicts in VERDICTS.md are committed; the hash shows it was not changed.
