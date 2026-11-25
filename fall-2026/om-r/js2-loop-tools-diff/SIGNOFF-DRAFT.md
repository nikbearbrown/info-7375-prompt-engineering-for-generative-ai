# SIGNOFF-DRAFT.md: skeletons for Om to fill in

> Everything in `[[ ]]` is Om's to write. Lines starting `HINT:` are
> evidence that exists in this repository. They are pointers, not entries:
> delete each one once used or rejected. Nothing here is a claim that Om
> checked anything.

## Sign-off — Job-Search Agent 2

```text
Sign-off — Job-Search Agent 2
Checked:      [[which properties, by which tests or runs — name them]]
How:          [[for each item above: by hand / by a test I wrote myself / by a
              test I specified and ran myself / by reading the diff / with
              Claude's help — say which]]
Not checked:  [[at least three real items]]
Not claiming: [[what this agent does not show]]
Signed or withheld: Om Raut, [[date]]
```

### HINT: evidence available for "Checked" (you decide what you checked)

- HINT: GATE.md wrong version 1, "budget silently ignored" →
  `tests/test_wrong_versions.py::WrongVersion1BudgetSilentlyIgnored`. It
  counts requests from the fake fetcher's own call log, not from the loop's
  report.
  - It failed against `agent/wrong_stub_budget.py` (`3 != 2`,
    `logs/01_tests_vs_wrong_stub_budget.txt`, re-run in `logs/05_*`).
  - It passed against the real loop (`logs/03_tests_vs_real_loop.txt`,
    `logs/04_*`).
  - Commits: `879756c` (tests + stubs), `cabde37` (loop).
- HINT: GATE.md wrong version 2, "failed board reported as no new jobs" →
  `tests/test_wrong_versions.py::WrongVersion2FailedBoardReportedAsNoNewJobs`.
  - It failed against `agent/wrong_stub_failed_board.py`
    (`'ok' != 'failed'`, `logs/02_*`, re-run in `logs/06_*`).
  - It passed against the real loop (`logs/03_*`, `logs/04_*`).
  - Each stub fails only its own test.
  - Before any loop existed: `logs/00_tests_before_impl_exists.txt`
    (`ModuleNotFoundError`).
- HINT: Permission policy → `tests/test_permissions.py`, 31 tests: host
  allow-list, redirects, write containment, new-board approval. Result:
  `logs/09_permission_boundary_tests.txt` (`481d9ba`).
  - `tests/mutation_check.py` reports 5/5 mutations caught
    (`logs/13_permission_mutation_check.txt`, `3076f5c`).
  - The string-prefix mutation survived the first version of the tests;
    see FRICTIONAL.md entry 6.
- HINT: Retry-then-budget-hit → `tests/test_loop_retry_budget.py`, 2 tests
  (`f3ca8d6`).
  - It failed on a scratch copy with the fix reverted
    (`logs/11_retry_budget_test_vs_reverted_fix.txt`).
  - It passed against the real loop (`logs/12_*`).
  - The reverted code is a reconstruction, not original code; the diff is
    in log 11 (FRICTIONAL.md entry 1).
- HINT: Deliberate 404, live: `badslug-gitlab-typo` reported `FAILED`, not
  retried, never "0 new", exit `finished`, no state written
  (`logs/10_deliberate_board_failure_live.txt`,
  `logs/run_20261109T232631Z.json`, `1dabae3`).
- HINT: Finished-wrong-answer → `FINISHED-WRONG-ANSWER.md` (`b908dbf`).
  - The SEEDED empty Stripe replay gives a clean `finished`
    (`logs/15_finished_wrong_answer_seeded_replay.txt`).
  - The independent check flags `771 -> 0` as SUSPICIOUS, and its control
    on two real responses says OK (`logs/16_independent_count_check.txt`).
- HINT: Removal detection, test-first:
  - defect reproduced (`logs/review_packet_01_defect_reproduced.txt`);
  - test failing before the patch (`logs/review_packet_02_*`, `8bb6a17`);
  - passing after (`logs/review_packet_03_*`), full suite
    (`logs/review_packet_04_*`), `d3e2e8a`;
  - three plausible wrong patches caught
    (`logs/review_packet_06_wrong_patch_check.txt`).
- HINT: Tool-invocation bug you found: `tests/test_tool_invocation.py`.
  - It failed on the pre-fix scripts with your exact error
    (`logs/17_tool_invocation_test_before_fix.txt`).
  - It passed after the fix (`logs/18_*`), `94522fc`.
  - Claude's own script-mode run: `logs/19_*`.
  - Your own re-run: REVIEW-PACKET.md, Step 5.
- HINT: Things you ran or read yourself, by your own account:
  REVIEW-PACKET.md Step 5 covers the full suite, the replay,
  `tools/count_drift_check.py`, and `git diff 8bb6a17 d3e2e8a`.
- HINT: Full suite today: 46 tests, OK
  (`python3 -m unittest discover -v -s tests -t .`).

### HINT: for "How", one fact to get right

Every test file and script above was **written by Claude**: the wrong-version
tests and stubs, the permission tests, the mutation check, the retry-budget
test, the removal tests, the wrong-patch check, the tool-invocation test, and
the replay and count-check tools.

- "By a test I wrote myself" applies only to a test you wrote. It does not
  cover tests you *specified*, such as GATE.md's two wrong versions, the
  boundary cases you listed, or the removal-test requirements.
- Tests you specified and then *ran yourself* are a different category, and
  still a legitimate one.
- Running the full suite (Step 5) checks that the tests pass. It does not
  check that they test the right thing. Reading the tests or the diff
  yourself is a separate "How".

Say which one each item is.

### HINT: candidates for "Not checked" (real gaps found in this build; pick and word your own)

- HINT: A posting removed and re-added with the same id between runs is
  never seen as a removal (REVIEW-PACKET.md, Step 7, item 1).
- HINT: An ATS that reuses ids would mask a real removal (REVIEW-PACKET.md,
  Step 7, item 2).
- HINT: A broken board (200 OK, empty list) looks like a mass removal: 771
  `removed`, still `ok`/`finished`. No test distinguishes the two
  (REVIEW-PACKET.md, Step 7, item 3; `logs/review_packet_05_*`, part b).
- HINT: Lever is untested for removals: string ids, multi-page fetches
  (REVIEW-PACKET.md, Step 7, item 4).
- HINT: Nothing makes a behavior change update GATE.md first. The scope
  review was the only safeguard, and it worked only because you asked for
  one (FRICTIONAL.md, entry 10).
- HINT: Also on record:
  - A failed board saves no evidence, so the 404 body is not kept
    (FRICTIONAL.md, entry 7).
  - The Anthropic SDK skips `check_url`, which matters when judgment code
    comes back (FRICTIONAL.md, entry 3).
  - The retry-budget test's "reverted fix" is a reconstruction
    (FRICTIONAL.md, entry 1).
  - Live boards drift between runs (FRICTIONAL.md, entry 8).

### HINT: candidates for "Not claiming"

- HINT: The finished-wrong-answer and removal demonstrations use **SEEDED**
  inputs, not a real outage or a real removal. All three real gitlab
  responses were byte-identical (REVIEW-PACKET.md, Step 1), so no live
  removal was ever observed.
- HINT: `tools/count_drift_check.py` uses a fixed threshold (drop > 50%, or
  to 0). It is a heuristic, not a detector of every quiet failure, and it is
  not part of the loop.
- HINT: Removal detection was written into GATE.md only after the code
  existed (GATE.md, "Amendment 2026-11-10"; FRICTIONAL.md, entry 10).
- HINT: JS2 has no judgment step. `api.anthropic.com` was removed from the
  allow-list until judgment code exists (`64d947d`).

## Driver's seat

> Fill or correct every `[[ ]]` cell. The "Claude did" cells are drafted
> from the record and are checkable; edit any you disagree with. "Om did"
> and "Why that part stayed mine" are yours alone. The last two rows (git
> identity, FRICTIONAL.md) were not in your list; delete them if you don't
> count them as major tasks.

| Task | Claude did | Om did | Why that part stayed mine | Evidence |
|---|---|---|---|---|
| GATE.md | Implemented against it. Listed 7 places where the spec left a choice open. Wrote the 2026-11-09 amendments from Om's decisions on those 7, plus an exit-precedence line Om had not asked for. Wrote the 2026-11-10 removal amendment to Om's content, making the fallback and reappearance rules more precise. | I wrote the original spec before there was any code. I defined the four exits, the three budgets, the two wrong versions, and the permission policy. I made the decisions on the seven open questions Claude flagged. | I wanted to decide what the agent should do while I could still look at the requirements on their own. Once there's working code in front of you, it's easy to start treating whatever it does as the spec. | The session's first listing showed a folder containing only `GATE.md` (2026-11-09 18:10 local). Commits `7c2640b` (original), `8dc2ef4` and `1a1e07f` (amendments). FRICTIONAL.md entries 2 and 10 |
| The loop implementation | Wrote `agent/loop.py`, `agent/boards.py` and `agent/fetch.py`. Found and fixed, before the first test run, a bug where retry requests weren't counted toward the board. Ran the first real runs. Its first attempt ran nothing because of a zsh quirk, and it redid them. | I set the rules the loop had to follow and ran the full suite myself during review. Claude wrote the loop and ran the first real runs. | I had to decide what counted as finishing, when the loop should stop, and what a failed board should look like in the report. Those choices affect what I can take away from a run. | `cabde37`, `061a0b2`, `7d2aad0`. `logs/03`, `logs/07`, `logs/08`, `2e6fc19`. FRICTIONAL.md entries 1 and 5 |
| Permission policy + boundary tests | Wrote `agent/permissions.py` and 31 boundary tests. Ran a mutation check, found a mutation that survived, and added a test that catches it. Turned the mutation check into a committed script. Removed `api.anthropic.com` on Om's decision. | I defined the boundaries and the cases I wanted tested. I also decided to take api.anthropic.com off the allow-list while there was no judgment step. | Every host and write location is access I'm giving the agent. I wanted a reason for each one. | `b598406`, `64d947d`, `481d9ba`, `3076f5c`. `logs/09`, `logs/13`. FRICTIONAL.md entries 3 and 6 |
| Deliberate 404 failure | Confirmed `badslug-gitlab-typo` was registered, ran the live command, and checked that no state or evidence was written for it. Noted the limitation that no evidence is saved for a failed board. | I defined the failure case I cared about in GATE.md: a board that fails has to show up as failed. Claude ran the live 404, and I'm using its recorded result here. | If I see zero new jobs, I need to know the board was actually checked. Otherwise I could miss postings and have no reason to look again. | `logs/10_deliberate_board_failure_live.txt`, `logs/run_20261109T232631Z.json`, `1dabae3`. FRICTIONAL.md entry 7 |
| Finished-wrong-answer demo | Built the SEEDED empty Stripe fixture, `tools/replay_from_file.py` and `tools/count_drift_check.py`. Chose a separate replay script instead of a `--from-file` flag, citing the write policy. Added a control run on real data. Wrote FINISHED-WRONG-ANSWER.md. | I ran the replay and the separate count check myself. I saw the loop report finished and the other script flag the drop from 771 to zero. | I wanted to see what I'd have in front of me if I only looked at the run status. That's the part I could easily miss when using it. | `b908dbf`, `logs/15`, `logs/16`, FINISHED-WRONG-ANSWER.md |
| Removal detection: test-first steps (1–2) | Found that the real gitlab responses were identical and built the SEEDED minus-one fixture. Reproduced the defect. Wrote 8 tests, including two edge rules Om had not specified: report once, and a reappearing id is not new. Showed all 8 failing before any patch. | I gave Claude the removal requirements and asked for the defect to be reproduced and tested before the patch. Claude made the seeded fixture and wrote the eight tests, including the extra cases for reporting a removal once and handling a reappearing id. | I wanted the expected behavior on record before we had a patch to judge. That gave me something concrete to compare the patch against. | `8bb6a17`, `logs/review_packet_01`, `logs/review_packet_02`, `tests/test_removal_detection.py` |
| Removal detection: the patch (3) and review (4–7) | Wrote the patch, including `last_fetch_ids`, which goes beyond the literal spec. Ran the full suite. Wrote the wrong-patch check. Drafted REVIEW-PACKET.md steps 4, 6 (as the author's recommendation) and 7, and flagged that GATE.md was never updated. | I ran the full suite, read git diff 8bb6a17 d3e2e8a, and asked for the scope review. I gave Claude the content for the removal amendment to GATE.md after the gap came up. | The tests could pass and I'd still have to decide whether the patch did what I asked. Reading the diff and asking for the scope review were how I checked that. | `d3e2e8a`, `94262e3`, `46493e8`. `logs/review_packet_03`–`06`. REVIEW-PACKET.md |
| Tool-invocation bug | Diagnosed the cause: `sys.path[0]` depends on how a script is started, and it had only ever run the script with `-m`. Found a related flaw in `weak_patch_check.py`. Fixed both, added a regression test, and showed it failing before the fix and passing after. | I found the bug by running the command myself and hitting an import error. I reran it after Claude's fix and confirmed it worked on my machine. | That's how I actually ran the tool. Claude's earlier -m run used a different invocation, so it hadn't hit the same failure. | `94522fc`, `38b0ba8`, `bd6a252`. `logs/17`, `logs/18`, `logs/19`. FRICTIONAL.md entry 9. REVIEW-PACKET.md Step 5 |
| This sign-off | Drafted this skeleton and its hints only. | I separated what I ran, what I read, what I specified, and what I'm taking from Claude's logs. | My name goes on it. I need to be able to say what I actually did if someone asks. | this file |
| Git identity fix | Set the email Om gave at first. Later read JS1's identity, rewrote all 12 commits, and verified the result. Found that its own first object search was broken, logged both the broken and the corrected search, and corrected FRICTIONAL.md. | I gave Claude the original email, then asked for the history to use the identity from JS1. Claude rewrote the commits and verified the result. | The commits are attributed to me, so which identity they use is my call. | `logs/14_identity_rewrite_evidence.txt`, `4c26d96`. FRICTIONAL.md entry 4 |
| FRICTIONAL.md | Wrote the entries from Om's list. Corrected four inaccuracies in that list before committing. Removed two statements it had not actually observed. Later resolved entries 1, 4, 6 and 9 and added entry 10. | I gave Claude my list of things that went wrong or took extra work. Claude checked the details against the record, corrected parts of the list, and kept the entries updated. | I wanted the write-up to capture what I actually got stuck on and had to go back to check. | `0a64676`, `dff8673`, `38b0ba8`, `bd6a252` |
