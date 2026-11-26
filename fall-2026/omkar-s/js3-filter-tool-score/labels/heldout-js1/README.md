# Held-out labels (copied from JS1, unchanged)

These three files are byte-identical copies of `../../js1-contract-and-watch/experiments/prompt/`
(`labels.csv`, `postings-20.json`, `LABELING-RULE.md`). Omkar labelled the 20 postings by hand on
2026-10-27 under the labeling rule he chose on 2026-10-26, before any Claude run in JS1.

**Why they are held out for JS3:** no JS3 number (weight, threshold, word list, prompt) was set by
looking at these labels. They are read only by `js3/experiments.py`, which scores each
one-change-at-a-time variant against them. The `split` column (dev / heldout) is JS1's; JS3 uses
all 20 rows as held-out. One exception, disclosed in FILTER.md: Claude Code saw the first 4 rows
of `labels.csv` before writing FILTER.md v1.0.

The postings are Klaviyo, saved 2026-10-25. They are older than the JS3 corpus (2026-11-17).
