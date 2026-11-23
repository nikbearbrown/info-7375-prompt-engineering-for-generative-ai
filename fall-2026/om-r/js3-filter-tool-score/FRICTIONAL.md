# FRICTIONAL.md — what broke or changed during the JS3 build

A dated log of real events from this build, each traceable to a commit, a
log file, or a test name. Nothing here is reconstructed or dramatized; where
an event left no file behind, the entry says so.

"Source of fix" is one of: **Claude Code** (found and fixed without Om's
input), **Om** (Om's own decision or catch), or **Om accepting/modifying a
Claude Code proposal**.

---

## 1. FILTER.md's Lever content field yields 0 relevant postings from Palantir

- **Date:** 2026-11-21
- **What happened:** FILTER.md ("Expected sources") specifies Lever's
  `descriptionPlain` as the content field for Palantir. Palantir's real
  postings put their requirements in a separate Lever field, `lists`
  (sections such as "What We Require" and "What We Value"), plus
  `additionalPlain`. Following the spec literally, `descriptionPlain` alone
  rarely contains the six role/skill words. The result: **0 relevant
  postings from the entire Palantir board** (308 collected, 308 rejected) in
  the real filter run (`logs/05_filter_run.txt`,
  `logs/filter_run_20261121T132140Z.json`).
- **What was checked:** `js3/run_filter.py` re-classifies every Palantir
  posting with `lists` and `additionalPlain` appended to the content. This
  is a measurement only and never changes a reported bucket. **26 Palantir
  postings would move from rejected to relevant**, for example "Forward
  Deployed AI Engineer", "Software Engineer - Edge AI Systems" and "Senior
  Software Engineer - Autonomous Systems". The full list is in the
  `palantir_lists_sensitivity` block of the filter-run JSON.
- **What was changed:** Nothing. This is a documented limitation that was
  measured and not acted on. FILTER.md stays as written: Om decided not to
  amend it for now. The reported buckets use `descriptionPlain` exactly as
  specified. `js3/postings.py` keeps the extra Lever text as `lever_extra`
  so the measurement can be repeated.
- **Source:** found by Claude Code during the first filter run. Om decided
  to leave the spec unchanged.
- **Still unresolved:** Yes. As long as the spec stays this way, any
  Palantir result from this filter is a statement about `descriptionPlain`,
  not about the posting as a whole.

## 2. Blank-quote grounding test added after the first wrong-stub run

- **Date:** 2026-11-21
- **What happened:** After the wrong-version tests had been run against the
  stubs (`logs/01_tests_vs_wrong_stubs.txt`), but before
  `js3/grounding.py` existed, Claude Code noticed that `"" in text` is
  always true in Python. A grounding check built on substring matching
  would therefore label a claim with an empty quote `supported`.
- **What was changed:** Added
  `test_empty_or_blank_quote_is_not_supported` before writing
  `js3/grounding.py`, then re-ran the stubs
  (`logs/01b_tests_vs_wrong_stubs_rerun.txt`, failures 13 → 15) to show
  the new test fails against them.
- **Source of fix:** Claude Code.
- **Still unresolved:** No.

## 3. First real filter run crashed on a relative path

- **Date:** 2026-11-21
- **What happened:** `python3 -m js3.run_filter logs/run_<stamp>.json`
  raised `ValueError: ... is not in the subpath of ...`. The script called
  `relative_to(ROOT)` on the path exactly as typed, which was relative,
  without resolving it first. The crash is kept in
  `logs/05a_filter_run_crashed_relative_path.txt`.
- **What was changed:** The report path is now `.resolve()`d. Re-run:
  `logs/05_filter_run.txt`. The fix went in before `run_filter.py` was
  first committed, so there is no separate commit for it.
- **Source of fix:** Claude Code.
- **Still unresolved:** No.

## 4. Reject-audit group B cut from 156 near-threshold postings to a 40-posting subsample

- **Date:** 2026-11-21
- **What happened:** The first reject-audit draw (`logs/09_reject_audit_draw.txt`)
  took the whole near-threshold population into group B: all 154 rejected
  postings matching exactly 1 of the 6 skill words, plus the 2 Metronome
  postings that passed rule 1 and were excluded only by rule 2. That made 202
  distinct postings to hand-judge across groups A, B and C. Those worksheets
  were never committed or judged.
- **Why it was changed:** Time. Om could not hand-judge 202 full postings in
  the time available. This was a time constraint, not a methodological
  improvement.
- **What was changed:** Group B is now 40 postings:
  - the 2 rule-2-only Metronome postings as forced includes, not subject to
    the sample, because they are a distinct case and not just another
    near-miss;
  - plus `random.Random(20261121).sample(pool, 38)` over the 154
    exactly-1-word postings, sorted by (board, id).

  Groups A (30 random rejected) and C (all 20 relevant) are unchanged; this
  was verified against the first draw's manifest. 88 distinct postings remain
  to judge. Commits: the draw code before the change, then the change with
  `logs/10`–`12`, then the BLANK worksheets as their own commit.
- **Source:** Om's decision, including the forced includes and the sample
  size. Claude Code implemented it test-first (`logs/10` shows the new tests
  failing, `logs/11` passing).
- **Still unresolved / limitation:** **The near-threshold audit is now a
  sample of a sample.** B covers 38 of the 154 exactly-1-word postings, so:
  - any near-threshold miss rate estimated from B carries sampling error on
    top of the hand-judging itself;
  - the 116 undrawn postings were never hand-judged;
  - the rule-2 finding rests on just 2 postings.

  This must be stated explicitly in the reject-audit write-up. It is recorded
  in `draw_manifest.json` (`near_threshold_selection.limitation`) and in the
  header of the B worksheet.

  Smaller note: B uses the same seed as A, by Om's choice for consistency.
  Both draws start from the same random stream over pools sorted the same
  way, so the two samples are not statistically independent of each other,
  though each is individually a uniform random sample of its own pool. Two
  postings are in both (A09 = B034, A22 = B029). Each is judged once, in A.

## 5. The reject-audit draw says "wrote" for files it never writes

- **Date:** 2026-11-23
- **What happened:** While checking the README's reproduction commands in a
  fresh clone, `python3 -m js3.reject_audit logs/run_20261121T132140Z.json`
  printed `wrote logs/reject_audit/<file>` for **every** file in
  `logs/reject_audit/`. That included Om's hand-judged `*_draft.md`
  worksheets. The script never writes those files. It writes only the three
  `*_BLANK.md` worksheets and `draw_manifest.json`. After writing them, it
  loops over the whole directory and prints `wrote` for each entry
  (`js3/reject_audit.py:244`). The message looks as if the draw overwrote
  Om's judgments; it did not.
- **What was changed:** Nothing. Found, then left as is. Running the draw
  is harmless to the worksheets: after the draw command, `git status
  --short logs/reject_audit` was empty in the clone. So the `_draft.md`
  files were untouched, and the BLANK worksheets and the manifest came out
  byte-identical to `6af4411`. README.md states this next to the command.
- **Source:** Found by Claude Code during the README reproduction check;
  Om decided to leave it as is.
- **Still unresolved:** Yes. The message is still misleading. A fix would
  print only the files actually written.
