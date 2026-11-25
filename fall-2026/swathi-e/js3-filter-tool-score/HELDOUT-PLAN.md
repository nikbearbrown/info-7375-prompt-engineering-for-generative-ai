# HELDOUT-PLAN.md — held-out set for the Chapter 9 experiment

Written 2026-11-19, before any postings are collected for it. Decisions by
Swathi Baba Eswarappa; drafted by Claude Code from them. Committed alone,
before the collection run.

## Purpose
Measure ONE pre-registered change: the shortlist threshold 5 -> 6. FILTER.md
("Revision (2026-11-17, before any JS3 filter code): topic words and the
threshold") names this as the candidate one-change experiment. It is
measured with filter v1.1 (code at `2c3ef12`) on postings that were not used to
build v1.1. Nothing else changes between the two conditions: the same code,
weights, rules and postings, with only the threshold differing.

## Data
- **One fresh LIVE collection** with the existing `collect.py`, unchanged:
  the same boards, budgets, permission policy and transport as the Nov 17 run.
- **Baseline run, so no verdicts are produced.** `collect.py` calls the JS2
  loop, which applies the old JS1 title rule (`rule.judge`) to every posting
  absent from `state/seen_ids.json`. It prints that verdict and saves it in
  `trace.json`. To keep any relevance verdict away from the postings I will
  label blind:
  1. `state/seen_ids.json` is copied outside the repository, its SHA-256 is
     recorded, and it is removed for the run.
  2. Every board is then a baseline (0 "new" by the loop's own state), and
     no judgments are computed.
  3. After the run, the original `state/seen_ids.json` is restored and its
     SHA-256 is checked against the committed version. The state rewritten by
     the baseline run is not committed.

  The trace will therefore say `"baseline": true` for each board.
- **"New" posting:** a posting whose (board, posting id) is absent from the
  Nov 17 raw responses (`runs/2026-11-17T21-47-06-167440-0500/`), not merely
  absent from the JS2 state. Only new postings are eligible.
- **Privacy check:** the new raw responses are checked for named recruiters,
  personal emails and phone numbers before they are committed. The run is
  committed unchanged if nothing new is found.
- **Not run:** the filter, the JS1 rule and any scoring, on the new postings
  until my labels are committed.

## Sample
Each pool is sorted by (board, posting id) before drawing, so the draw does
not depend on file order. Draws use Python's `random.Random(seed).sample`.

- **Group A, "likely relevant."**
  - **Eligible:** a new posting whose title contains, as a whole word or
    phrase (case-insensitive; a space or hyphen between the words of a
    phrase), any of: new grad, graduate, early career, entry level, junior,
    AI, machine learning, ML, data.
  - **Interns excluded:** a title containing intern, interns, internship or
    internships.
  - **Draw:** all eligible postings if there are 10 or fewer; otherwise 10
    drawn with seed **20261119**.
  - **Stop condition:** if fewer than 5 are eligible, stop and report before
    sampling.
- **Group B:** 10 drawn with seed **20261120** from the remaining new postings
  (every new posting not selected for Group A, interns included).
- **Rows:** Group A then Group B, shuffled together with seed **20261121**.

## Files
- **`heldout/HELDOUT.csv`**, with columns `row, board, posting_id, title,
  location, reading_file, my_verdict, my_reason, how_judged`.
  `reading_file` gives the relative path; the last three columns are left
  empty.
- **`heldout/read/<board>-<posting id>.txt`**: title, location, board, id,
  URL, the source raw file and its SHA-256, then the full description as plain
  text, nothing removed or summarized. No filter output.
- **`heldout/selection.json`**: group assignment, seeds, pool sizes and method.
  Not opened by me until my labels are committed.
- **`make_heldout_sample.py`**: the script that draws the sample,
  reproducibly. It reads the new raw responses and never the filter.

## Blind labeling
- **Who and how:** I judge every row myself with `AUDIT-RULE.md`, with no AI
  draft and before any filter output exists for these postings.
- **Recording:** `my_verdict` is one of relevant / not relevant / can't tell.
  `my_reason` is my own words, and `how_judged` = "independent, no AI draft".
- **Commit:** my labels are committed before any filter is run on these
  postings.

## Measurement (only after my labels are committed)
- **Conditions:** filter v1.1 at threshold 5 (as committed) and at threshold 6.
  Only the threshold differs.
- **Reporting:** per group, **A and B never pooled**, as counts:
  - shortlisted and relevant;
  - shortlisted and not relevant;
  - relevant but not shortlisted.
- **Reported separately:** my "can't tell" rows and the filter's "I cannot
  tell" rows.
- These are sample counts for this held-out set, **not rates for all
  postings**. Group A was selected by title words, so its counts are not
  representative of the boards.
