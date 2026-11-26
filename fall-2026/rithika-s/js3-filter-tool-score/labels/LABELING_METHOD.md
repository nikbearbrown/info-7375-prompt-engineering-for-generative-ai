# Labeling method: held-out (24) and audit (50)

Status on 2026-11-25: **every verdict in `heldout_verdicts.csv` and
`audit_verdicts.csv` is an automated suggestion by Claude Code
(claude-opus-5-5). No verdict has been reviewed by a human yet.** None of
them is a manual label by Rithika, and they must not be described as one
until the review in section 6 is done.

## 1. Who did what

| Step | Done by | When |
|---|---|---|
| Labeling rule (`LABELING_RULE.md`) | Rithika | 2026-11-25, committed f3bd1b24, before labeling |
| Request to switch to batch labeling by Claude | Rithika | 2026-11-25 |
| Rubric (`LABELING_RUBRIC.md`) refining the rule | Claude Code | 2026-11-25, written before any posting was read for labeling |
| Verdict suggestions, 74 postings in 10 batches | Claude Code | 2026-11-25 |
| Validation and CSV assembly (`js3/batch_label.py`) | script | 2026-11-25 |
| Review of every suggestion | **Rithika: not yet done** | — |

## 2. Criteria

The criteria are `LABELING_RULE.md` (Rithika's) and `LABELING_RUBRIC.md`
(Claude's refinement of it, same three verdicts: relevant / not / unsure).
The rubric's SHA-256 (`55829cfe…a2ec`) is stored in every batch file;
`python3 -m js3.batch_label check` fails if the rubric is edited after
labeling. The criteria were not changed after any verdict was written.

In short: **relevant** means an individual-contributor builder whose main
shown work is building, training, evaluating, deploying or serving ML/AI/LLM
models, or the ML/data platforms and pipelines they run on. **not** covers
sales, solutions/customer-facing (including forward-deployed), operations,
finance, legal, design, people management, non-ML software, and clearance.
**unsure** means the sheet text is not enough to tell. Location, seniority,
experience, degree, visa, salary and company were deliberately not used.

## 3. Batch procedure

1. `python3 -m js3.batch_label show --dataset <d> --batch <n>` prints one
   batch of 8 postings exactly as they appear on the blind sheet.
2. Claude read that batch and wrote `labels/suggestions/<d>_batch_<nn>.json`
   with, per posting: id, board, title, verdict, confidence
   (high/medium/low), a CSV reason (one short phrase without commas, as
   LABELING_RULE.md requires), a justification, verbatim evidence quotes,
   the uncertainty that affected the call, and a borderline flag with a note.
3. The held-out set (3 batches) was done first, then the audit set
   (7 batches), separately.
4. `python3 -m js3.batch_label assemble --dataset <d>` validated each set
   and wrote the CSV (`id,verdict,reason`, same ids and order as the
   sampler's template) plus `labels/suggestions/<d>_review.md`.

Validation (enforced by the script, covered by `tests/test_js3_batch_label.py`):
exactly one suggestion per sheet id, no unknown ids, board and title equal
to the sheet, verdict and confidence from the allowed sets, reason without
commas, non-empty justification and uncertainty, **every evidence quote
found verbatim in that posting's own sheet text**, every unsure or low
answer flagged borderline, rubric hash unchanged, and near-duplicate
justifications (≥ 85% similar) reported. The CSV is never overwritten if
it holds a verdict that differs from the suggestion (a human edit) unless
`--approve-overwrite` is given.

**Reproducibility.** Re-running the commands below rebuilds the CSVs and
review files exactly from the recorded batch files. The judgment step
itself is not reproducible by a script: asking Claude again might give
different suggestions. The batch files are the record of what was
suggested.

## 4. Evidence used and its limits

- Only the blind sheets (`heldout_sheet.md`, `audit_sheet.md`): board,
  title, location and the first 800 characters of body text.
- Not read: `audit_key.json`, `out/filter/`, the raw corpus, the URLs,
  anything outside this folder, or anyone else's labels.
- Many excerpts are company boilerplate and stop before the role's duties;
  those cases are marked as uncertain rather than filled in from general
  knowledge.
- Claude Code also wrote the filter code (from FILTER.md) and knows its
  keyword rules, though not its decision on any audit posting. Its
  suggestions may lean the same way as the filter for reasons a human
  labeler would not share. This is one reason the human review matters.

## 5. Suggested counts (before human review)

| Dataset | relevant | not | unsure | borderline |
|---|---|---|---|---|
| held-out (24) | 3 | 19 | 2 | 9 |
| audit (50) | 8 | 37 | 5 | 25 |

Recurring borderline questions, each answered the same way everywhere:
- **Customer-facing roles with real ML building** (forward-deployed
  engineers, Applied AI Engineers in advisory teams, ML specialist solutions
  architects): suggested *not*, as LABELING_RULE.md says, mostly with low
  confidence.
- **Data platforms**: ingestion connectors suggested *relevant* (the rule
  counts data pipelines); generic backend or database-engine work suggested
  *not*.
- **Experimentation platform**: the Software Engineer was suggested *not* and
  the Data Engineer on the same team *relevant*. Decide these two together.
- **Research engineer/scientist** roles that train models: *relevant*,
  medium.

## 6. Human review (to be completed by Rithika)

The suggestions become your verdicts only after you review them.

Review workflow (added 2026-11-25, `js3/review.py`):
1. Read `labels/REVIEW.md`: all 74 postings, held-out and audit separately,
   borderline cases grouped by role type, and the cases where title
   keywords and the suggested verdict point different ways.
2. Record each decision in `labels/review_decisions.csv` (status
   `pending` / `approved` / `corrected`; for `corrected`, a final verdict
   and reason). All 74 rows start as `pending`. Do not edit the verdict
   CSVs by hand.
3. `python3 -m js3.review apply --pending blank` writes the decisions into
   `heldout_verdicts.csv` and `audit_verdicts.csv`. With `--pending blank`
   unreviewed rows become unlabeled; with `--pending keep` they keep
   Claude's suggestion. Add `--dry-run` first to preview.
4. `python3 -m js3.batch_label check` then reports how many CSV rows
   differ from the suggestion.

`review_decisions.csv` records which rows you approved or corrected.
Please also fill in this table:

| Dataset | Reviewed by | Date | Rows reviewed | Rows changed | Notes |
|---|---|---|---|---|---|
| held-out | | | | | |
| audit | | | | | |

If you accept suggestions without reviewing each one, the measurement
compares the filter with Claude's judgment, not yours, and should be
reported that way.

## 7. Commands

```
python3 -m js3.batch_label show --dataset heldout --batch 1     # batches 1-3
python3 -m js3.batch_label show --dataset audit --batch 1       # batches 1-7
python3 -m js3.batch_label assemble --dataset heldout
python3 -m js3.batch_label assemble --dataset audit
python3 -m js3.batch_label check
```
