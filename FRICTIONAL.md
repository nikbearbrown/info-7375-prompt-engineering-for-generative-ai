# FRICTIONAL: Job-Search Agent 2

## What was hard, and what I did about it

**1. My JS1 folder had no git history.** JS2 is graded on order: the gate before code, the test before the patch. I started a new repo
and copied JS1 in one commit (`09b1056`), with sha256s for the Oct 31 Samsara state and raw response. I checked that the 323 ids in the
state are exactly the 323 jobs in the raw file. That baseline turned out to be the most valuable thing JS1 left me, because it gave
Samsara a real Oct 31 → Nov 10 comparison: 80 new postings, and 89 gone.

**2. The gate went through seven versions before any code** (`82f02cb` … `6cc9e07`). Re-reading it kept turning up real gaps:
- the seeded run's temporary folder broke the "write only in `out/`" rule
- no live run could ever end `finished` while the 404 board was in it
- a board with no history would have passed the verifier
- the review-packet paragraph pointed to a section my own edit (`a67bdbf`) had deleted

Each fix went into the Decisions log.

**3. Choosing the second system.** A read-only probe showed Lever returns a bare JSON array, while Greenhouse and Ashby return an
object with `jobs`. I picked Lever because the different shape makes the adapter and the shape rule mean something. The same probe
found two surprises:
- `plaid` now returns 404 on Lever
- `kraken`, `wealthsimple` and `voleon` return **`200 []`**

I almost swapped Kraken for Airbnb. Then a check found **92 Kraken postings on Ashby**, which made Kraken a real finished-wrong
answer instead of a guess.

**4. Three JS1 tests encoded JS1's contract** (Greenhouse-only, one board). JS2's gate deliberately changes that, so I updated them
in `e51d208` to assert the new rules. The allow-list test now requires exactly the two gate hosts. The "other host" test uses Ashby.
The one-board list moved to `config/boards_js1.json`. None of them got looser.

**5. One test was wrong, not the code.** `test_reset_state_needs_approval` compared `last_run`, which the gate expects to change. I
corrected it in `6c82b59` to assert what matters: the refused reset didn't happen (history `state`, new ids `["2"]`). The commit
message says so.

**6. Two of Claude's edits silently didn't apply.** Its edit tool refuses a file it hasn't read in the session.
- The first time, Claude went on to save "after the patch" outputs that were really **unpatched** results. It noticed, deleted those
  four untracked files before any commit, and redid the step properly.
- The second time, the sabotage check ran JS1's old script. Its output was overwritten before committing.

**Lesson:** read the output, not just the exit code. The mislabeled files would have been false evidence.

**7. The live data didn't exercise everything.** None of Samsara's 80 new postings is data-titled. I checked by hand with a broader
match than the rule uses. So the rule judge never ran on a live posting in JS2, and no live retry, redirect or 429 happened. Those paths
are tested only offline, and SIGNOFF.md says so.

## What I accepted, modified or rejected from Claude

- **Accepted:**
  - Lever over Ashby
  - Kraken with an Ashby cross-check
  - the judge off for graded runs
  - plausibility checks in the verifier, not the loop
  - the review-packet defect (W4)
- **Modified:**
  - I asked for ten boards instead of four
  - I asked for the gate in my own format (`2b75002`)
  - I removed the checked-facts list from the gate myself (`a67bdbf`)
  - I had commit messages reworded, which rewrote local history before any push (`8acdac1` → `a67bdbf`, `f1477b1` → `30e0f56`,
    `d7a6228` → `2b75002`)
- **Rejected:** *Ethan: anything you turned down. Be honest if the answer is nothing.*

## Unresolved

- The review decision (REVIEW_PACKET.md section 6) and my own command reruns are still mine to do.
- A proxy in the environment would bypass the host check (the review packet's "still missed" case).
- Boards 2–9 have only same-day comparisons. A real second day would need another run tomorrow, after the deadline.
- `out/` is about 32 MB of raw responses (three runs of ten boards; Zoox alone is 2.3 MB per run). I kept it all, because I
  was graded down in JS1 for deleting cited evidence.
- Every commit shows my git identity, but Claude made most of them. The `Co-Authored-By` lines and the driver's seat say who did what.
