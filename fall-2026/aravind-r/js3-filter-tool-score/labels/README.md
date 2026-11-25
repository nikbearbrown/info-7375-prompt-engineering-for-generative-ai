# Label sheet (Phase 5 evaluation)

**Sheet:** `label-sheet.csv`, 40 rows: 20 `dev`, 20 `heldout`. Drawn by `tools/make-samples.mjs` with seed 7375; method in `sample.json`.

**The sample is enriched.** 8 of each 20 come from PM- or product-titled postings (149 of 1,009 in the pool; the 55 audit postings are excluded). Precision and recall on this sheet are **not** population rates.

**Held-out is frozen.** `heldout.frozen.json` holds the 20 held-out ids and the SHA-256 of their sorted list. It was committed before any rule change. Held-out results are not computed or shown during tuning.

Like the audit, the sheet is blind: no decision or score is shown. Fill in:
- `my_label`: `relevant`, `not_relevant`, or `cannot_tell`
- `my_note`: optional

## Filling it in (2026-11-25)

```bash
~/.nvm/versions/node/v20.20.2/bin/node tools/judge-audit.mjs --sheet labels/label-sheet.csv
```

The same tool as the audit, in label mode: the same keys, an optional note, and the CSV is saved after every row with only `my_label` and `my_note` changing. Held-out rows come first; the split, the score, and the decision are never shown.

**Definition to label by:** FILTER.md v1.1.0-e §1. That means mostly roles requiring at most 4 years, sometimes 5+ or 6+, never 7+; a location on Maya's list; no refusal to sponsor; and a TPM role counts only if it owns product direction.

**If only held-out is labeled,** dev stays empty and is declared unlabeled. No dev figure is reported.
