# A fresh held-out set, filter run 2026-11-21T044414Z

Made by `tools/heldout_kit.py` (Claude Code, at Aravind's request) from `js3/filter-run/2026-11-21T044414Z/`, before any change to the filter was measured. It is for JS3's one-change experiments: each change to one object is measured on these 30 postings against Aravind's verdicts.

## The rule this set keeps (the book, chapter 9)

A held-out set is touched once. Once it guides a choice (a word list, a weight, the cutoff, a decision to keep going), it has become development data, and its next use is no longer independent.

- The verdicts in VERDICTS.md are committed before any change is measured on this set.
- The audit's verdicts (`js3/audit/2026-11-21T044414Z/`) are development data: they will be used to change the filter. They never go into this set, and none of the audit's 55 postings is in it, nor any copy of one.
- If a result on this set leads to a change of the filter, this set becomes development data from then on. That is written here with the date, and a later claim about a change needs a new held-out set.

## How it was drawn

Seed **2026112103**, a new one (the audit used 20261121 and 20261122), and the card order shuffled with seed 2026112104. The rule is in the tool's docstring:

1. The pools: the run's kept postings and its rejected postings (its 1 "I cannot tell" posting is in neither).
2. Left out: the 55 audit postings (only their board and posting id were read from `js3/audit/2026-11-21T044414Z/sealed/answers.json`), the 10 shortlisted postings, and every other posting with the same board and normalized title as one of those (a copy of the same job in another place).
3. From what is left, sorted by board and posting id, a uniform random sample: 15 kept postings, then 15 rejected postings.

| Pool | In the run | Audit or shortlist | Same-title copies | Left to draw from | Drawn |
|---|---:|---:|---:|---:|---:|
| kept | 99 | 28 | 2 | 69 | 15 |
| rejected | 1409 | 37 | 22 | 1350 | 15 |

Which card came from which pool, and what the filter decided, is in `sealed/answers.json` (SHA-256 `9d9b062acb945d5d847e47f4fa8da804a450ae97c58c849e532ff2f7a397356a`). It is opened only after VERDICTS.md is committed; the hash shows it was not changed.

## What this set may claim

Two separate random samples from one day's saved answers of three boards: 15 of 69 kept postings and 15 of 1350 rejected postings. Agreement is stated for each pool on its own, with its bound. The pools are drawn equally, not in proportion to the run (99 kept, 1409 rejected), so one rate over all postings would have to weight them, and the postings left out (the audit's, the shortlist's and their copies) are not covered.
