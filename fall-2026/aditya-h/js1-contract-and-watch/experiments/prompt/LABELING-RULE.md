# Labeling rule for the hand labels

**Written:** 2026-10-31, before any posting was labeled and before any Claude call was made.
**Chosen by:** Aditya Hasija, in the Claude Code chat on 2026-10-31. Aditya picked "the contract rule" over "would Maya apply?". The text below was drafted by Claude Code.

## The rule

Each of the 20 postings in `labels.csv` gets the label `relevant` or `not_relevant`, decided by applying **CONTRACT.md → The rule (`title-us-v1`)** by hand, using only the columns shown in `labels.csv` (`title`, `location_name`, `offices`).

1. **Title check:** does the lowercased title contain `product manager`, `product analyst`, `product strategy`, `product operations` or `product owner`, as a phrase rather than as separate words?
2. **US check:** is any office exactly `US` or starting with `US-`, or does `location_name` contain a US marker from the contract's list?
3. `relevant` only if both checks pass. Otherwise `not_relevant`.

The labeler writes a one-line `note` for any posting where applying the rule felt unclear.

## What the labels are, and are not

- They are **my reading of my own rule, applied by hand**. They are the reference that Claude's verdicts are scored against.
- They are **not** a claim that a posting is a good job for Maya. That would be a different and harder labeling rule.
- The labeler does not see the code's rule verdicts while labeling. Afterwards, the hand labels are also compared with the code's rule verdicts. A mismatch there counts as a failure under the CONTRACT's failure sentence.
