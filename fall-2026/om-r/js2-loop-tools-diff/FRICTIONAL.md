# FRICTIONAL.md — what broke or changed during the JS2 build

A dated log of real events from this build, each traceable to a commit, a
log file, or a test name. Nothing here is reconstructed or dramatized; where
an event left no file behind, the entry says so.

Commit hashes are the ones in the current history. All commits were
rewritten once (entry 4), so any hash quoted from before that rewrite no
longer exists.

"Source of fix" is one of: **Claude Code** (found and fixed without Om's
input), **Om** (Om's own decision or catch), or **Om accepting/modifying a
Claude Code proposal**.

---

## 1. Retry requests before a budget hit were not counted toward the board

- **Date:** 2026-11-09
- **What happened:** In the first draft of `agent/loop.py`, a board's request
  count came from successful pages only. If a page was retried (timeout or
  5xx) and the request budget ran out mid-retry, those retry requests were
  not attributed to the board. The board would then have been reported as
  "never attempted" even though requests had been made for it, instead of
  `interrupted`.
- **What was checked:** Claude Code found this while re-reading its own
  `loop.py`, before running the wrong-version tests against the real loop
  (`logs/03_tests_vs_real_loop.txt`) and before any live run.
- **What was changed:** Per-board requests are now the difference in the
  meter's request count before and after the board
  (`board_requests = meter.requests - before`). The fix went in before the
  first commit of `loop.py`, so it is part of `cabde37`, not a separate
  commit.
- **Still unresolved:** Resolved 2026-11-09 (`f3ca8d6`). Originally there
  was no committed test for the retry-then-budget-hit case; the scratch
  checks covered only a Lever pagination case that was interrupted by the
  budget. `tests/test_loop_retry_budget.py` now covers it with a timeout and
  with a 503. It checks the fake fetcher's own call log (2 requests, both
  for gitlab), status `interrupted`, the state file byte-for-byte unchanged,
  and exit `budget-exhausted`.
  - It fails against a scratch copy with the fix reverted
    (`logs/11_retry_budget_test_vs_reverted_fix.txt`: gitlab missing from the
    report even though it made 2 requests).
  - It passes against the real loop
    (`logs/12_retry_budget_test_vs_real_loop.txt`).
  - The pre-fix code was never committed, so the revert was rebuilt from the
    patch applied at the time. Log 11 includes the exact diff.
- **Source of fix:** Claude Code.

## 2. GATE.md's `incomplete` example contradicted wrong-version test 1

- **Date:** 2026-11-09
- **What happened:** GATE.md gave "a budget limit hit mid-run" as an example
  of `incomplete`. Its own wrong-version-1 test requires `budget-exhausted`
  for exactly that situation.
- **What was checked:** Claude Code implemented `budget-exhausted` for any
  budget hit, used `incomplete` only for boards refused without
  `--approve-new-board`, and listed this as open choice 1 in its report.
- **What was changed:** Om decided to keep the code and amend GATE.md
  (`8dc2ef4`). That commit also:
  - added the per-board status list, including `interrupted`, which the code
    already had (Om's decision, open choice 3);
  - added the exit precedence line
    (`error` > `budget-exhausted` > `incomplete` > `finished`). Om didn't ask
    for this line. Claude Code added it while writing the amendment, to
    match what the code already did.
- **Still unresolved:** Nothing.
- **Source of fix:** Om accepting a Claude Code proposal. The precedence line
  was added by Claude Code.

## 3. `api.anthropic.com` was allow-listed but unused

- **Date:** 2026-11-09
- **What happened:** GATE.md and the first `agent/permissions.py`
  (`b598406`) allowed `api.anthropic.com`. Nothing in JS2 calls it, and the
  Anthropic SDK makes its own HTTP calls without going through `check_url`,
  so the allow-list entry enforced nothing.
- **What was checked:** Claude Code flagged it as open choice 7.
- **What was changed:** Om decided to remove it until judgment code exists.
  The GATE.md amendment is in `8dc2ef4` and the code change in `64d947d`.
  After the change, `https://api.anthropic.com/...` was confirmed refused,
  and the wrong-version tests still passed
  (`logs/04_tests_vs_real_loop_after_amendments.txt`). The test
  `test_api_anthropic_com_is_refused_until_judgment_code_exists` now pins
  the removal.
- **Still unresolved:** When judgment code is added, the host comes back.
  That code must also make sure its HTTP calls are actually checked, because
  the SDK skips `check_url`.
- **Source of fix:** Om.

## 4. Commits made with a personal gmail identity on a course repo

- **Date:** 2026-11-09
- **What happened:** The repo-local identity was set to a personal gmail
  address, per Om's own instruction when the repo was created, and the first
  12 commits used it.
- **What was checked:** Om caught it and pointed to the JS1 repo. Claude Code
  read JS1's identity
  (`git -C ~/Desktop/js1-contract-and-watch config user.email` returned
  `raut.om@northeastern.edu`; all 12 JS1 commits use it).
- **What was changed:**
  - The repo-local `user.email` was set to `raut.om@northeastern.edu`.
  - Author and committer were rewritten on all 12 commits with
    `git filter-branch --env-filter`. Original dates were kept, and every
    hash changed.
  - Nothing had been pushed.
  - The `refs/original` backup refs were deleted, the reflog expired, and
    unreachable objects pruned with `git gc --prune=now`.
  - Author and committer emails, all 59 remaining objects, and the local
    config were searched: 0 gmail matches.
    **Correction (2026-11-09):** the "all 59 objects" part was wrong. The
    search piped `git rev-list --all --objects` (which prints `<id> <path>`
    for trees and blobs) straight into `git cat-file --batch`, which read
    those lines as missing objects, so only the 12 commit objects were
    searched. The author/committer result still stood, because those fields
    live in commit objects, but the files were never searched. Claude Code
    found this when the same command returned 0 after FRICTIONAL.md, which
    contains the word "gmail", had been committed.
- **Still unresolved:** Resolved 2026-11-09 (`4c26d96`). Originally the
  verification output existed only in the session transcript, not in
  `logs/`, and the object search it pointed to was broken (see the
  correction above). `logs/14_identity_rewrite_evidence.txt` now records:
  - all 18 commits have `raut.om@northeastern.edu` as author and committer;
  - the broken search, kept for the record (72 of 90 objects read as
    missing);
  - the corrected search over all 90 objects at HEAD `3076f5c`: 0 missing
    and 0 gmail addresses. At that point the word "gmail" appeared only in
    the FRICTIONAL.md blob; log 14 and later versions of this file also
    contain the word, and neither contains an address;
  - no `refs/original` backups;
  - the 3 unreachable objects all come from amending the FRICTIONAL.md
    commit after the rewrite.
- **Source of fix:** Om (the catch and the decision). Claude Code carried out
  the rewrite.

## 5. First attempt at the real runs executed nothing

- **Date:** 2026-11-09
- **What happened:** Claude Code stored each run command in a shell variable
  and ran it as `$C1`. zsh does not split an unquoted variable into words,
  so the shell looked for a single command named
  `python3 -m agent.loop --boards ...`. The failure was not silent: both
  logs recorded `command not found` and `# exit code: 127`. Nothing ran, and
  no state or evidence was created (`ls` showed no `evidence/` or `state/`).
- **What was checked:** Claude Code read the two log files immediately after
  the attempt.
- **What was changed:** The two bad logs
  (`logs/07_first_real_run_baseline.txt`,
  `logs/08_second_real_run_no_approval.txt`) were deleted before any commit,
  and both runs were redone with the commands written out in full. Only the
  good logs were committed (`2e6fc19`).
- **Still unresolved:** Nothing. The bad logs were never committed, so this
  entry is the only record.
- **Source of fix:** Claude Code (its own mistake).

## 6. A permission mutation survived the first version of the boundary tests

- **Date:** 2026-11-09
- **What happened:** `tests/test_permissions.py` passed fully on its first
  run (30 tests). To check that the tests could fail at all, Claude Code
  broke `agent/permissions.py` five ways on a scratch copy:
  - added `api.anthropic.com` back
  - dropped the port check
  - disabled new-board approval
  - swapped `realpath` for `abspath`
  - swapped the containment check for a string-prefix match

  Four were caught. The string-prefix mutation survived:
  `test_sibling_prefix_state_evil_is_refused` still passed because
  `state_evil/gitlab_seen.json` was refused by a different rule (state files
  must sit directly in `state/`), not by containment.
- **What was checked:** The same mutation was re-run after the new test was
  added. It failed both subtests, while the real code passed all 31 tests
  (`logs/09_permission_boundary_tests.txt`).
- **What was changed:** Added
  `test_sibling_prefix_evidence_evil_and_logs2_are_refused`, which only the
  path-component containment check can pass (`481d9ba`).
- **Still unresolved:** Resolved 2026-11-09 (`3076f5c`). Originally the
  mutation runs were done in the scratchpad, and their output was not saved
  in `logs/`. `tests/mutation_check.py` now does the same five mutations as
  a committed script:
  - it copies `agent/` and `tests/` to a temp directory and never touches
    the project tree;
  - it requires the unmutated copy to pass first;
  - it aborts if any mutation's text no longer matches exactly once.

  Result: 5/5 caught, 0 survived
  (`logs/13_permission_mutation_check.txt`).
- **Source of fix:** Claude Code.

## 7. A failed board leaves no evidence file (known limitation)

- **Date:** 2026-11-09
- **What happened:** In the live deliberate-failure run, `badslug-gitlab-typo`
  was correctly `FAILED` with `HTTPError: HTTP Error 404: Not Found` (1
  attempt, not retried), and the exit was `finished`
  (`logs/10_deliberate_board_failure_live.txt`,
  `logs/run_20261109T232631Z.json`, `1dabae3`). No evidence file is written
  for a failed board, so the 404 response body is not kept anywhere. A
  curl probe earlier in the session showed it as a 38-byte JSON object with
  `status` and `error` keys; the message text itself was not recorded.
  Only the error string is recorded in the run log.
- **What was checked:** `ls evidence | grep -c badslug` returned 0, and
  `state/` held only the three original state files.
- **What was changed:** Nothing. GATE.md does not require evidence for failed
  boards.
- **Still unresolved:** Yes. If failed-board evidence is wanted, GATE.md
  must say so first, then `loop.py` would save the error body through
  `WritePolicy`.
- **Source of fix:** None yet (observation by Claude Code).

## 8. Live boards drift between runs

- **Date:** 2026-11-09
- **What happened:** Stripe returned 770 postings in Claude Code's scratch
  live run at 23:15:53 UTC (also 770 in the curl probe a few minutes
  earlier). It returned 771 in the real baseline at 23:23:00 UTC
  (`logs/07_first_real_run_baseline.txt`).
- **What was checked:** gitlab (251) and palantir (304) were unchanged across
  the same runs.
- **What was changed:** Nothing. The project's baseline is the real run in
  `logs/07_first_real_run_baseline.txt`. The scratch run used a separate
  scratch root, and its state was never used.
- **Still unresolved:** The 770 figure lives only in the session transcript;
  the scratch root was temporary and is not in `logs/`. Any count in these
  logs is a snapshot of a board that changes.
- **Source of fix:** Not applicable (observation).

## 9. `tools/replay_from_file.py` only worked the way Claude Code ran it

- **Date:** 2026-11-10
- **What happened:** Om ran
  `python3 tools/replay_from_file.py gitlab evidence/gitlab_SEEDED_minus_one_20261110T000619Z.json`
  from the project root and got
  `ModuleNotFoundError: No module named 'agent'` (line 29). Every logged
  run (logs 15, `review_packet_01`, `review_packet_05`) had used
  `python3 -m tools.replay_from_file`. The two modes put different
  directories first on Python's import path (`sys.path[0]`):
  - script mode: `tools/`, which has no `agent/` package;
  - `-m` mode: the current directory, the project root.

  `PYTHONPATH` was unset in Claude Code's shell and the directory was the
  same, so the only difference was the invocation. The script never set
  `sys.path` itself, and its docstring showed only the `-m` form.
  Separately, the script takes `--board`/`--from-file` flags, so Om's
  positional arguments would have hit an argparse usage error even without
  the import bug.
- **What was checked:** Claude Code reproduced Om's exact error and printed
  `sys.path[0]` in each mode. It then ran every `tools/` and `tests/`
  script in script mode, from the project root and from `/tmp`, with
  `PYTHONPATH` removed. That turned up a second, related flaw:
  `tools/weak_patch_check.py` took its root as a required positional
  relative to the current directory and had no `--help`.
- **What was changed (`94522fc`):**
  - `replay_from_file.py` puts the project root on `sys.path` before
    importing `agent`;
  - `weak_patch_check.py` defaults to its own project root;
  - `tests/test_tool_invocation.py` was added. It starts each tool in
    script and `-m` mode, from the project root and from another
    directory, without `PYTHONPATH`. It fails on the pre-fix scripts with
    Om's exact error (`logs/17_tool_invocation_test_before_fix.txt`) and
    passes after the fix (`logs/18_tool_invocation_test_after_fix.txt`).
  - Claude Code's script-mode replay after the fix:
    `logs/19_replay_script_mode_after_fix.txt`.
- **Still unresolved:** Resolved 2026-11-10 (`46493e8`). Originally this
  entry listed Om's own re-run of the fixed script as outstanding, because
  Claude Code could not do it for him. Om then re-ran
  `python3 tools/replay_from_file.py --board gitlab --from-file evidence/gitlab_SEEDED_minus_one_20261110T000619Z.json`
  himself and saw `250 postings in response, 0 new, 1 removed` and
  `real state/gitlab_seen.json unchanged: True` (his run at
  `2026-11-10T00:42:14+00:00`). His account is in REVIEW-PACKET.md,
  "Step 5 — Commands Om ran himself". The command-line interface was
  deliberately not changed to accept positional arguments.
- **Source of fix:** Om found it. Claude Code diagnosed and fixed it.

## 10. GATE.md defined removal detection only after the code existed

- **Date:** 2026-11-10
- **What happened:** The project's rule (GATE.md) is that the spec comes
  first and code is implemented against it. Every earlier GATE.md section
  held to that. Removal detection did not:
  - It was built as the review packet's chosen non-trivial change, from the
    task request.
  - Claude Code wrote the failing test (`8bb6a17`) and then the patch
    (`d3e2e8a`) without first amending GATE.md.
  - The patch added a report field (`removed`), a state-file field
    (`last_fetch_ids`, with a `seen_ids` fallback) and a once-only reporting
    rule, none of which GATE.md mentioned.

  Test-first held; spec-first did not.
- **What was checked:** The gap was not found proactively. It surfaced in
  the review packet's own Step 4 scope review, written by Claude Code as the
  patch's author. That review listed GATE.md as untouched and recorded
  "**Process gap:** GATE.md says code is implemented against it, but GATE.md
  defines neither "removed" nor `last_fetch_ids`" (REVIEW-PACKET.md, Step
  4). It then named a GATE.md amendment as the required follow-up in
  Step 6.
- **What was changed:** Om made the amendment part of his ACCEPT decision
  (REVIEW-PACKET.md, Step 6, `46493e8`), and GATE.md was amended in
  `1a1e07f`, "Amendment 2026-11-10: removal detection". It defines:
  - `removed`;
  - `last_fetch_ids` and how long the fallback lasts;
  - once-only reporting.

  The amendment says plainly that it was written after the code, and why.
  The gap was fixed in the spec, not left silent, and not hidden by
  back-dating.
- **Still unresolved:** Nothing for removal detection. As a process point,
  nothing stopped this from happening: no check makes a behavior change
  touch GATE.md first, so the scope review was the only safeguard, and it
  worked only because it was asked for.
- **Source of fix:** Om accepting a Claude Code proposal. Claude Code
  flagged the gap in its own scope review and proposed the amendment; Om
  decided it was required and set its content.

