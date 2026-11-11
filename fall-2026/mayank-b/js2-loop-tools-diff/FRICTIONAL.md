# FRICTIONAL — Job-Search Agent 2

## Executive summary

**What this is.** A dated log of what got in the way while building JS2: what was tried, what actually happened (with the commit, test or file that shows it), what was done instead, what I accepted, changed or rejected from Claude, and what is still unresolved. **Why it matters.** Several results below are not what was planned, and the record should show that. 2026-11-10

---

### 2026-11-05 · The course CI rejects my JS1 language
- **Tried:** to plan JS2 in Node, reusing JS1.
- **Happened:** the latest course CI run (commit `3e3fa86`) lists all 15 JS1 `.js` files as "Non-Python implementation" failures (`scripts/validate_course.py`). CI is red for the whole class.
- **Did instead:** chose Python standard library (gate answer 0).
- **From Claude:** I accepted its recommendation.
- **Unresolved:** whether the JS1 `.js` failures affect JS1's GitHub-posting points; not asked yet. And at my push (commit `f09a904`) course CI stopped on another student's Python 3.12 syntax before reaching my folder, so I checked my folder against the validator's rules myself.

### 2026-11-10 19:18 · Answered The Gates
- **Tried:** to answer the gate questions on Nov 5.
- **Happened:** I answered them on the due date (Nov 10). GATE.md is commit `1cc3602`, before any code.
- **From Claude:** accepted every ★ except 4b, where I chose A + B + C. I wrote the failure sentence and W9 myself.

### 2026-11-10 19:24 · Three failures on the first full test run
- **Tried:** the first full run of the new tests.
- **Happened:** 45/48 passed.
  1. The W6 test caught a real bug: a board stopped by the budget before its first request was still counted as done, so `never_attempted` was empty.
  2. The checker refused its own temp folder (`/var/…` vs resolved `/private/var/…`).
  3. My "checker doesn't import the agent" test matched a string in the checker's own output.
- **Did instead:** fixed all three before committing CP3 (`d725018`); 48/48.
- **From Claude:** Claude Code wrote the code and the tests, and made all three fixes; I accepted them after the 48/48 run.
- **Learned:** only the W6 test showed that my report would under-count the boards a budget stopped. I would not have noticed it by reading the output.

### 2026-11-10 19:25 · The planned finished-wrong trap had disappeared
- **Tried:** `greenhouse/hubspot`, which Lectern recorded on 2026-09-26 as a valid but empty board.
- **Happened:** the live API returned **404** (`runs/2026-11-11T00-24-41Z-finished-wrong/`), so my agent correctly reported an error. There was no finished-wrong answer to show.
- **Did instead:**
  1. A survey probe of 6 candidate slugs, run with curl on the two allowed hosts only, found Ashby `greenlight` returning `200 {"jobs":[]}`.
  2. Used it as the live demo (`runs/…-empty-board-live/`).
  3. Added a **labelled seeded replay** of the empty HubSpot board for a case that is provably wrong (`config/replay/finished-wrong.json`).
- **From Claude:** it proposed the probe and the seeded replay; I accepted both, on condition that the replay is labelled `SEEDED` in its run id and on the first line of its report.
- **Unresolved:** whose board `ashby/greenlight` is. The live case shows an *unsupported* "no new jobs", not a provably *wrong* one.

### 2026-11-10 19:26 · The repeat made my real run `incomplete`
- **Happened:** the deliberate `Notion` repeat made the real run end `incomplete`, as GATE §1 defines it, not `finished`.
- **Did:** kept it. It's what my gate says, and it shows the repeat rule. A run with one failed board and no repeat ending `finished` (my decision 1a) also happened live: in `runs/2026-11-11T00-24-41Z-finished-wrong/`, HubSpot returned 404 and the run still ended `finished` with that board flagged. `test_one_board_fails_run_still_finished_and_flagged` covers it too.
- **Unresolved:** none for the repeat rule itself.

### 2026-11-10 19:27 · Review packet: the test first, then the patch
- **Tried:** reproducing the JS1 symlink defect.
- **Happened:** B8 and B8b failed on the first version ("PolicyError not raised"; CP5 `6050272`, `review/01-reproduce-before-patch.txt`). After Claude's one-function patch, 50/50 and 9/9 (CP6 `3ab4582`).
- **Found:**
  - The patch also changed **reads**: a read through a link pointing outside was allowed before and refused after. I probed both versions to check this.
  - A probe shows that if `runs/` itself is a symlink, writes still escape.
- **From Claude:** Claude Code wrote the failing tests and the patch, and found the read-side change and the remaining escape.
- **Decision (mine):** ACCEPT. I ran the review commands myself and they matched (`REVIEW-PACKET.md`).
- **Evidence of my run:** `review/05-review-commands-run-by-mayank.txt` (my terminal, 22:37 EST, Python 3.9.6). My first attempt failed with "No such file or directory" because I wasn't in the JS2 folder; the script now works from any folder, and its exit codes now reflect the tests, not the last command in the pipe.
- **Unresolved:**
  - the `runs/`-is-a-symlink escape needs a new GATE rule (each resolved root must stay inside the resolved project folder);
  - no test yet for the read-side change;
  - a link swapped in between the check and the write (time-of-check/time-of-use) is untested.

### 2026-11-10 20:00 · I approved the first real state write
- **Did:** `python3 agent.py approve 2026-11-11T00-24-30Z-real --approve-state 2026-11-11T00-24-30Z-real`.
- **Happened:** applied 3 boards (anthropic 679, hubspotjobs 122, notion 156 ids). Nothing was held: the failed board had no proposed state to write, so its state stayed untouched as GATE §4 says (`runs/2026-11-11T00-24-30Z-real/approval.json`).
- **Later (2026-11-10, 21:24 ET):** `runs/2026-11-11T02-24-39Z-second-check/` used this state. HubSpot had **2 new postings** ("Lead Solutions Engineer", "Solutions Engineer", both "Remote - USA"); the rule judged both `not_relevant`.
- **Found:** my JS1 rule only treats remote work as US when the text says "United States". "ML Engineer / Remote - USA" comes out `not_relevant`, but "Remote - United States" comes out `relevant` (I ran `rule.judge` on both).
- **Unresolved:** that "USA" gap in the location rule, and a second calendar day: the second check ran on the same evening.

### 2026-11-10 · Smaller things
- **One wrong prediction:** B7 was refused as predicted, but with `approval-required`, not the `outside-write-root` I predicted (`BOUNDARY-TESTS.md`).
- **zsh quirks cost two attempts:**
  - `=====` in an `echo` was treated as a command;
  - `$v:f…` was read as a variable modifier.
  Transcripts were regenerated with the exact commands.
- **Repo size:** the raw responses are about 16 MB, mostly Notion's 2.9 MB board saved once per run (5 copies). Kept because the brief asks for saved raw responses.
