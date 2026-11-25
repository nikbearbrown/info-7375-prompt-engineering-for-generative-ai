# How the labels reached `review/LABEL_SHEET.csv`

- **Labeler:** Aditya Raj, the 63-row blind sheet from `e6a3d24`. He filled in a separate CSV of his own, then sent Claude Code **two screenshots** of it on 2026-11-25:
  - rows S01–S41;
  - rows S23–S63.
  - The overlapping rows agree.
- **Transcribed by:** Claude Code, 2026-11-25. Only the `label` and `reason` columns were written. Aditya's wording was kept, with typography normalized: en dashes and mojibake appear only in his titles, which were not copied.
- **Check made:** for each sheet_id, the title in the screenshot was compared with the committed sheet's title (prefix match), and all 63 matched. Labels: 9 yes, 44 no, 10 unsure.
- **Not yet checked:** Aditya has not yet compared the transcription with his own CSV. Until he does, a misread label or reason is possible.
- **The originals stay local:** `../../../../local/label_screenshots/`. They are not published.

## Disclosure: Claude saw the held-out labels before the freeze

The plan (FILTER.md §5) was that the held-out labels would stay unread until the dev revisions were frozen. Transcribing from screenshots meant **Claude Code read all 63 labels, the 23 held-out rows included, on 2026-11-25, before any revision was chosen or frozen.**

The tooling seal (`js3.labels`) still records the sheet hash and opens `labels/heldout_labels.csv` only after `FREEZE.json` is committed. But that gate now protects the files, not Claude's knowledge.

What this means for the held-out numbers is decided by Aditya (see README → "Held-out status").
