# FRICTIONAL — honest log

I started JS2 thinking the hard part would be the loop. It wasn't. Claude Code wrote the loop, the policy and the verifier in well under
an hour. The hard parts were deciding the rules before any code existed, and then checking whether "green" and "finished" actually
meant true. Several of the most useful lessons came from things going wrong: a "finished" run that was wrong, a test that checked the
wrong thing, output files labeled "after the patch" that were really from before it, and a claim about my own JS1 code that turned
out to be false. This log records those moments, with the commits, prompts and tests behind them.

## 1. Starting point and the Oct 31 baseline

My JS1 folder was not a git repository, but JS2 is graded on order: the gate before code, the test before the patch. So I started a
new local repo, and the first commit (`09b1056`) copied exactly what JS2 builds on. My JS1 feedback asked for a real second-day run and
for evidence of every run I cite. The JS1 state file still held all 323 Samsara ids from the live run on 2026-10-31, so I copied it and
its raw response into `baseline/2026-10-31/` with sha256s. Claude Code checked that the 323 ids in the state are exactly the 323 jobs
in the raw file. That baseline gave Samsara a real Oct 31 → Nov 10 comparison, which JS1 never had. On 2026-11-10 I said "Yes do the
local things , do not do anything on github as of now", and later "Save the commits locally and then in the end when everything is
done, I will tell you to push it on Github together", so every step was committed locally and nothing was pushed until I said so.

## 2. Writing the gate before any code

GATE.md went through several versions before any code existed (`82f02cb` … `6cc9e07`). Claude Code drafted the wording from my
decisions, and each re-read turned up a real gap. The seeded run's temporary folder broke the "write only inside `out/`" rule. No live
run could ever end `finished` while the deliberate 404 board was in it. A board with no history would have passed the verifier. And
"judge off" would have counted as a missing judgment, which would have made every run incomplete. Each of these was fixed in the gate,
with a written reason, before the tests or the code were written.

## 3. Making the gate mine

I wanted the gate in my own format, so on 2026-11-10 I pasted an example and said "ONly refer this format . Write my content in this
format." (`2b75002`). After reading that version I made my own edit and removed the checked-facts list and one rule from Scope
(`a67bdbf`). That broke a reference in the review-packet paragraph, which still pointed to "the defect above", and it had to be fixed
in the next version. I also asked for that commit's message to read "Changes made in Gate.md based on v2.0" instead of Claude's
wording, which rewrote local history before any push; Claude kept the content identical and checked it. After the code existed, I went
through the gate again section by section and cut text that repeated other files or described implementation (`b30ee67`, "Minor
Changes made in Gate.md"). The tests that read the gate still passed, and no exit, budget, retry rule, permission rule or wrong version
changed, so I logged it as a wording-only version.

## 4. A claim about my own code that turned out wrong

In Claude's first breakdown of the assignment on 2026-11-09, it said my JS1 `fetch.py` had a redirect gap. When it actually read the
code, JS1 already checked every redirect hop with `AllowListRedirectHandler`. Probing `check_url` offline instead found a real defect:
it accepted `:8443` and `user:pw@` on an allowed host, because it compared only the hostname. That became my review packet. It also
taught me not to trust a confident description of code that nobody has opened yet.

## 5. Choosing the boards

For the second system I asked "Which is the best option?" between Lever and Ashby, and then "yes use what is best". A read-only probe
showed that Lever returns a bare JSON array, while Greenhouse and Ashby both return an object with `jobs`, so I chose Lever because the
different shape makes the adapter and the shape rule mean something. The same probe found that `plaid` now returns 404 on Lever, and
that `kraken`, `wealthsimple` and `voleon` return `200 []`. Then I asked "can you include 10 boards in total?", which meant raising the
budgets (boards 5→12, requests 60→100, time 300→420 s, loop steps 100→200) through a dated decision in the gate (`30e0f56`). I nearly
swapped Kraken for Airbnb and said "Do what you think is best in adding Kraken or changing to Airbnb". Claude Code checked Kraken's
Ashby board and found 92 postings, so Kraken's empty Lever board was provably wrong rather than just suspicious, and it stayed
(`6cc9e07`). Kraken also exposed a hole: a board seen for the first time has no history, so the verifier would have passed it. The gate
now fails every empty board, and wrong version 19 tests exactly that.

## 6. Tests first, then the build

On 2026-11-10 I said "make everything that is left to be done now" and then "except the submission part , build everything". The first
code commit was tests only (`e51d208`): the 18 boundary predictions and the 19 wrong-version tests, written before `policy.py` existed.
Against no code they gave 113 tests with 21 failures and 38 errors. Three JS1 tests encoded JS1's contract, a Greenhouse-only allow-list
and a single board, which my gate changes on purpose, so they were updated to the new rules without getting looser. After the build
(`6c82b59`), only 5 failures were left, and all of them were the inherited defect in wrong version 4 and boundary cases B03 and B04.
That was exactly what the boundary table predicted before any code existed.

## 7. A test that checked the wrong thing

One test was wrong, not the code. `test_reset_state_needs_approval` compared the board's `last_run` field, which the gate expects to
change, because a run still updates the boards it observed. It was corrected in `6c82b59` to check what actually matters: that the
refused reset didn't happen, so the board was still compared with the old state and reported only the one new id. The commit message
says the test was corrected and why. It was a reminder that a red test is not automatically right, any more than a green one is.

## 8. The review packet

The defect was reproduced first, in a commit that changed no code (`58ce031`), showing three URLs wrongly allowed. The patch came after
it (`afb3877`): nine lines added to `check_url` and nothing removed. I asked "Why am i supposeed to run this git show afb3877 --
jsagent/fetch.py", and the answer is the point of Chapter 6: I check the change itself, not Claude's summary of it. On 2026-11-10 at
17:31 EST I ran `git show` and `git show --stat` on the patch, the reproduction script, the full test suite, the sabotage check, the
boundary report, the verifier on runs A, B and D, and a search of run A's trace, and every result matched (`5b3bd32`). I noticed that
the test run prints a `usage: … error:` message that looks like a failure, but it is a passing test showing that the loop refuses an
unlabeled seeded replay. My decision was Accept (`2cb9ddb`), knowing the patch does not cover a proxy set in the environment.

## 9. Output that would have been false evidence

Twice, Claude's edit tool silently didn't apply, because it refuses to change a file it hasn't read in the session. The first time,
Claude went on to save "after the patch" outputs that were really unpatched results. It noticed, deleted those four untracked files
before any commit, and redid the step. The second time, the sabotage check ran JS1's old script, and that output was overwritten before
it was committed. If nobody had read the output, those files would have been false evidence in the review packet. The lesson I take
from it is to read the output, not just the exit code.

## 10. The runs and the finished-wrong answer

All four runs were on 2026-11-10 with `--no-claude`, and Claude Code ran them. Run A, with all ten boards, ended `incomplete`: the 404
board was tried once, not retried, and its count was left null instead of zero. Samsara had 314 postings against 323 on Oct 31, with 80
new and 89 gone, and none of the 80 had a data title. That surprised me, so Claude Code rechecked the raw file with a broader match than
my rule uses and still found none. Run B, with nine boards, ended `finished`, but Kraken was reported as 0 new; the verifier failed it
as empty, and the Ashby cross-check, run by Claude Code outside the agent 26 seconds later, showed 92 postings. That was the live
finished-wrong answer. Run C, the seeded replay, and run D, the clean eight-board run that ended `finished` with the verifier passing,
both behaved as the gate predicted.

## 11. What I accepted, changed and rejected

I rejected `evidence/PROMPTS.md` when I asked "where is it mentioned that there should be a PROMPTS.md?" and had it removed (`f9d6e4d`)
with "Don't add unnecessary useless things". I also rejected Claude's commit message for my own gate edit, the checked-facts list it had
put in the gate's Scope, its listing of the AI policy as an assignment task, its suggestion that I make the commits myself, and the
option to "Revise" the review, since the proxy gap is a separate defect rather than a flaw in this patch. I changed the number of boards
from four to ten, put the gate in my own format, had the driver's seat rewritten in the brief's "should" form, and had RUNS.md, the
sign-off and the gate reworded where they claimed I had done something I hadn't. I accepted Lever over Ashby after seeing the response
shapes, Kraken over Airbnb after the 92 Ashby postings, the judge being off for graded runs because JS2 grades the loop rather than
relevance, and the review patch after my own reruns.

## 12. What I learned, traceability, and what is still open

The biggest lesson is that "finished" is not "right": run B ended cleanly with a wrong answer, and only a check outside the loop caught
it. I also learned to read output instead of trusting exit codes, that a test can be wrong as easily as code, and that re-reading the
gate before any code is cheaper than finding the same gaps later. The prompts I quoted above are from 2026-11-09 for the first breakdown
and 2026-11-10 for the rest. The commits run from `09b1056` (start) through `6cc9e07` (the final gate), `e51d208` (tests first),
`6c82b59` (build), `58ce031` and `afb3877` (the review), `2dfc3b1` (sabotage), `024c1f7` (runs), and my own `5b3bd32`, `2cb9ddb`,
`75c7368` and `b30ee67`. The tests are the full suite of 113, `test_W1` to `test_W19`, the boundary cases B01 to B18, and
`scripts/sabotage_check.py`, which catches all 19 wrong versions. Still open: a proxy set in the environment would route an allowed URL
through a host that isn't on the list; there is a window between the path check and the write; boards 2–9 were only compared on the same
day; the rule judge never ran on a live posting; no live retry, redirect or 429 happened; the verifier trusts earlier reports' lists of
unjudged ids; and I didn't read each site's terms of use in full.
