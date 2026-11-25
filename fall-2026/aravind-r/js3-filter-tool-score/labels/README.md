# Label sheet (Phase 5 evaluation)

**Sheet:** `label-sheet.csv`, 40 rows: 20 `dev`, 20 `heldout`. Drawn by `tools/make-samples.mjs` with seed 7375; method in `sample.json`.

**The sample is enriched.** 8 of each 20 come from PM- or product-titled postings (149 of 1,009 in the pool; the 55 audit postings are excluded). Precision and recall on this sheet are **not** population rates.

**Held-out is frozen.** `heldout.frozen.json` holds the 20 held-out ids and the SHA-256 of their sorted list. It was committed before any rule change. Held-out results are not computed or shown during tuning.

Like the audit, the sheet is blind: no decision or score is shown. Fill in:
- `my_label`: `relevant`, `not_relevant`, or `cannot_tell`
- `my_note`: optional
