# FRICTIONAL — honest log

I started JS2 thinking the hard part would be the loop. It wasn't. Claude Code wrote the loop, the policy and the verifier in well under
an hour. The hard parts were deciding the rules before any code existed, and then checking whether "green" and "finished" actually
meant true. Several of the most useful lessons came from things going wrong: a "finished" run that was wrong, a test that checked the
wrong thing, output files labeled "after the patch" that were really from before it, and a claim about my own JS1 code that turned
out to be false. This log records those moments, with the commits, prompts and tests behind them.

## 1. Starting point and the Oct 31 baseline

My JS1 folder was not a git repository, but JS2 is graded on order: the gate before code, the test before the patch. So I started a
new local repo, and the first commit (`09b1056`) copied exactly what JS2 builds on. My JS1 feedback asked for a real second-day run and
for evidence of every run I cite. The JS1 state file still held all 323 Samsara ids from the live run on 2026-10-31, so I copied it
and its raw response into `baseline/2026-10-31/` with sha256s. Claude checked that the 323 ids in the state are exactly the 323 jobs
in the raw file. That baseline gave Samsara a real Oct 31 → Nov 10 comparison, which JS1 never had.

On 2026-11-10 I said "Yes do the local things , do not do anything on github as of now", and later "Save the commits locally and then
in the end when everything is done, I will tell you to push it on Github together". Every step was committed locally, and nothing was
pushed until I said so.

## 2. Writing the gate

GATE.md went through seven versions before any code (`82f02cb` … `6cc9e07`). Claude drafted the wording from my decisions, and each
re-read turned up a real gap:
- the seeded run's temporary folder broke the "write only inside `out/`" rule
- no live run could ever end `finished` while the deliberate 404 board was in it
- a board with no history would have passed the verifier
- "judge off" would have counted as a missing judgment, so every run would have been incomplete

Each fix went into the Decisions log instead of a quiet edit.

I wanted the gate in my own format, so on 2026-11-10 I pasted an example and said "ONly refer this format . Write my content in this
format." (`2b75002`). After reading that version, I made my own edit: I removed the checked-facts list and one rule from Scope
(`a67bdbf`). That broke a reference in the review-packet paragraph, which still said "the defect above," and it was fixed in v2.2. I
also asked for my edit's commit message to read "Changes made in Gate.md based on v2.0" instead of Claude's wording. That rewrote
local history before any push (`8acdac1` → `a67bdbf`, `f1477b1` → `30e0f56`). Claude kept the content identical and checked it.

One claim turned out to be wrong. In Claude's first breakdown of the assignment (2026-11-09), it said my JS1 `fetch.py` had a redirect
gap. When it actually read the code, JS1 already checked every redirect hop (`AllowListRedirectHandler`). Probing `check_url` offline
instead found a real defect: it accepted `:8443` and `user:pw@` on an allowed host, because it compared only the hostname. That became
my review packet.

## 3. Choosing the boards

For the second system I asked "Which is the best option?" between Lever and Ashby, then "yes use what is best". A read-only probe
showed that Lever returns a bare JSON array, while Greenhouse and Ashby both return an object with `jobs`. I chose Lever because the
different shape makes the adapter and the shape rule mean something.

The probe also found two surprises:
- `plaid` now returns 404 on Lever
- `kraken`, `wealthsimple` and `voleon` return **`200 []`**

Then I asked "can you include 10 boards in total?" (2026-11-10). That meant raising the budgets (boards 5→12, requests 60→100, time
300→420 s, loop steps 100→200). The gate only allows that through a dated Decisions-log row in the same commit (`30e0f56`).

I nearly swapped Kraken for Airbnb. I said "Do what you think is best in adding Kraken or changing to Airbnb". Claude checked Kraken's
Ashby board and found **92 postings**, so Kraken's empty Lever board was provably wrong, not just suspicious, and it stayed
(`6cc9e07`). Kraken also exposed a hole: a board seen for the first time has no history, so the verifier would have passed it. The gate
now fails every empty board (wrong version 19).

## 4. Tests first, then the build

On 2026-11-10 I said "make everything that is left to be done now" and then "except the submission part , build everything". The
first code commit was tests only (`e51d208`): the 18 boundary predictions (B01–B18) and the W1–W19 wrong-version tests, written before
`policy.py` existed. Against no code: 113 tests, 21 failures and 38 errors (`evidence/tests/01_tests_first_before_code.txt`).

Three JS1 tests encoded JS1's contract, a Greenhouse-only allow-list and a single board. My gate changes that on purpose, so they were
updated to the new rules, and none got looser:
- the allow-list test now requires exactly the two gate hosts
- the "other host" test uses Ashby instead of Lever
- JS1's one-board list moved to `config/boards_js1.json`

After the build (`6c82b59`), 5 failures were left, and all of them were the inherited defect: W4 ×3 plus boundary B03 and B04. That
was exactly what `BOUNDARY_TESTS.md` predicted before the code existed (16/18).

One test was wrong, not the code. `test_reset_state_needs_approval` compared `last_run`, which the gate expects to change, because a run
still updates the boards it observed. It was corrected in `6c82b59` to check what matters: the refused reset didn't happen (history
`state`, new ids `["2"]`). The commit message says so.

## 5. The review packet

The defect was reproduced first, in a commit that changed no code (`58ce031`): 3 URLs wrongly allowed. Then came the patch
(`afb3877`): 9 lines added to `check_url`, nothing removed.

Twice, Claude's edit tool silently didn't apply, because it refuses a file it hasn't read in the session:
- The first time, Claude went on to save "after the patch" outputs that were really **unpatched** results. It noticed, deleted those
  four untracked files before any commit, and redid the step.
- The second time, the sabotage check ran JS1's old script. Its output was overwritten before commit.

If nobody had read the output, those files would have been false evidence.

I asked "Why am i supposeed to run this git show afb3877 -- jsagent/fetch.py", and the answer is the point of Chapter 6: I check the
change, not Claude's summary of it. On 2026-11-10 at 17:31 EST I ran in my own terminal:
- `git show afb3877` and `git show --stat afb3877`
- the reproduction script
- the full test suite
- the sabotage check
- the boundary report
- the verifier on runs A, B and D
- a grep of run A's trace

Every result matched what was expected. I noticed the test run prints `usage: … error: --replay needs --seeded`, which looks like a
failure. It is a passing test, showing that the loop refuses an unlabeled seeded replay. My decision was Accept, knowing the patch
doesn't cover a proxy set in the environment (`HTTPS_PROXY`).

## 6. The runs

All four runs were on 2026-11-10 with `--no-claude`.

**Run A** (17:15:00, all 10 boards) ended `incomplete`:
- the 404 board was tried once, not retried, with its count left null and reported as "count unknown, not zero"
- Samsara against the Oct 31 baseline: 314 postings, **80 new**, 89 gone, and none of the 80 data-titled

Zero surprised me. Claude rechecked the raw file with a broader match (`data|analytic`) than my rule uses and found nothing.

**Run B** (17:15:27, 9 boards) ended `finished`, but Kraken was reported as 0 new. The verifier failed it as empty, and the Ashby
cross-check 26 s later showed 92 postings. That was the live finished-wrong answer. The cross-check's `tee` failed because its folder
didn't exist yet, so its console text was saved from the terminal output, while the raw response itself was saved by the script.

**Run C** (seeded, offline) and **run D** (8 boards, `finished`, verifier PASS, with Toast showing 1 new posting) behaved as the gate
predicted.

## 7. Pushing back on extras and claims

When Claude added `evidence/PROMPTS.md`, I asked "where is it mentioned that there should be a PROMPTS.md?" The brief doesn't mention
one, so I had it removed (`f9d6e4d`): "Don't add unnecessary useless things".

A full re-read of the brief against the repo found four real gaps, which were fixed in `7f4b9da`:
- The driver's seat said what Claude **did**, but the brief asks what Claude **should** do. It was restructured.
- Canvas needs run instructions, not just a link and a hash.
- `RUNS.md` said "I review each row" when I hadn't. It now says what I actually checked: rows A, B and D through my reruns, not X and C.
- GATE.md had the same over-claim, corrected as v2.4 in the Decisions log, wording only.

## 8. What I accepted, changed, rejected, learned, and left open

**Rejected:**
- `evidence/PROMPTS.md`, as not asked for
- Claude's commit message for my own gate edit
- the checked-facts list Claude put in the gate's Scope (I removed it in `a67bdbf`)
- Claude listing "read the AI policy" as an assignment task, and its suggestion that I make the commits myself
- "Revise" for the review: the proxy gap is a separate defect, not a flaw in this patch

**Changed:**
- the number of boards, from four to ten
- the gate's format, to mine
- the driver's seat, to the brief's "should" form
- `RUNS.md` and the gate's wording, to what I actually checked

**Accepted after checking:**
- **Lever over Ashby**, after seeing the probe's response shapes
- **Kraken over Airbnb**, after the 92 Ashby postings
- **the judge off for graded runs**, because JS2 grades the loop, not relevance
- **the review patch**, after my own 17:31 reruns
- **Claude's correction of its redirect claim**, after it read `fetch.py`

**What I learned:**
- **"Finished" is not "right."** Run B ended cleanly with a wrong answer, and only a check outside the loop caught it.
- **Read the output, not just the exit code.** The mislabeled "after the patch" files would have been false evidence.
- **A test can be wrong too.** The reset test checked a field the gate expects to change.
- **Re-reading the gate finds real gaps.** It happened six times, all before any code existed.
- **Claude's first claim about my own code was wrong.** Probing the code found the real defect instead.

**Traceability:**
- **Prompts:** quoted above with their dates (2026-11-09 for the first breakdown, 2026-11-10 for the rest).
- **Commits:** `09b1056` (start) · `82f02cb` … `6cc9e07` (gate) · `a67bdbf` (my edit) · `e51d208` (tests first) · `6c82b59` (build) ·
  `58ce031` / `afb3877` (review) · `2dfc3b1` (sabotage) · `024c1f7` (runs) · `5b3bd32` / `2cb9ddb` (my reruns and decision) ·
  `7f4b9da` / `f9d6e4d` (audit fixes).
- **Tests:** the full suite (`python3 -m unittest discover -s tests -t .`, 113 tests), `test_W1`…`test_W19`, the B01–B18 boundary
  cases, `test_reset_state_needs_approval`, and `scripts/sabotage_check.py` (19/19 caught).
- **Evidence:** `out/runs/`, `evidence/seeded/`, `evidence/crosscheck/`, `evidence/tests/`, `review/` and `evidence/RUNS.md`.

**Still unresolved:**
- **Proxy gap:** a proxy set in the environment would route an allowed URL through a host that isn't on the list.
- **Path race:** there is a window between the path check and the write.
- **Same-day only:** boards 2–9 were compared seconds apart, not across days.
- **Judging path:** no new data-titled posting appeared live, so the rule judge ran only in tests.
- **No live failures:** no live retry, redirect or 429 happened.
- **Verifier trust:** the verifier trusts earlier reports' lists of unjudged ids.
- **Size:** `out/` is about 32 MB, kept because I lost points in JS1 for deleting cited evidence.
- **Unused JS1 leftovers:** `watch.py`, a second persona, `boards_all.json` and the v2 prompt are still in the repo.
- **Terms of use:** I didn't read each site's terms in full.
