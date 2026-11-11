# Job-Search Agent 2 — The Loop, the Tools, and the Diff

INFO7375, Pavan Majji. Folder: `fall-2026/pavan-m/js2-loop-tools-diff/`

A bounded loop that watches several job boards, uses network and file tools under a permission policy enforced in code, and changes only through code I reviewed. Persona: **Alex Morgan, fictional** (`data/persona_alex.json`). My real résumé is not in this repo.

**Started from:** my own JS1 agent (`../js1-contract-and-watch`, submitted at `9b381ec`), copied unchanged into this folder (`9b66b8d`). I did not use the Reallocation Engine or Lectern.

## Language and toolchain
- Python 3.14.3 (Homebrew), in a project venv created with conda deactivated
- httpx 0.28.1 (all board requests), pytest 9.2.0; full list in `requirements.txt` (the anthropic SDK is installed from JS1's list but is not used by the loop)
- Claude Code (desktop app) wrote the implementation against my GATE.md and tests
- Timestamps are local time (EST, UTC−5)

## Boards
| Key | System | Purpose |
|---|---|---|
| `greenhouse:gleanwork` | Greenhouse | real board |
| `lever:palantir` | Lever | real board |
| `ashby:openai` | Ashby | real board |
| `greenhouse:pavan-js2-no-such-board` | Greenhouse | **deliberate failure** (bad name → HTTP 404) |

## Run it from a fresh clone
```bash
cd fall-2026/pavan-m/js2-loop-tools-diff
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v                 # 40 tests, no network
```
**Replay runs (no network, no state change):**
```bash
python -m agent.loop --config config/replay_nov9.json     # real Nov 9 captures
python -m agent.loop --config config/demo_boards.json     # finished-wrong demo (CONSTRUCTED)
python check_run.py out/runs/<run folder>                 # independent check
```
**Live run (calls the 3 allowed hosts):**
```bash
python -m agent.loop --config config/boards.json; echo "exit code: $?"
```
A live run updates `out/state/`. To put the committed state back afterwards: `git checkout -- out/state`.

Exit codes: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error (GATE.md §2). `check_run.py`: 0 clean, 1 problems found.

## What ran (past tense)
| When | Run | Result | Evidence |
|---|---|---|---|
| Nov 8, Nov 9 | Manual `curl` captures | OpenAI 816 → 825, Palantir 305 → 304, Glean 123, bad board 404 | `evidence/2026-11-0*_manual-capture_*.json` |
| Nov 10, 10:25 | **Real run 1, live** | incomplete; Glean baseline 123; bad board `bad_board` (404), postings null; **Palantir 304/304 and OpenAI 826/826 ids unusable (defect)** | `out/runs/2026-11-10T102543/` |
| Nov 10 | Replay before the fix (Nov 9 input) | Palantir 0/304, OpenAI 0/825 usable | `evidence/review/1_replay_BEFORE_patch.txt` |
| Nov 10 | Replay after the fix (same input) | Palantir 304/304, OpenAI 825/825 usable | `evidence/review/7_replay_AFTER_patch.txt` |
| Nov 10, 13:11 | I removed the 2 empty state files left by the bug | visible in commit `a249b3d` | FRICTIONAL Entry 10 |
| Nov 10, 13:12 | **Real run 2, live** | incomplete, exit code 1; **Glean: 2 real new postings** (125); Palantir baseline 304/304, OpenAI baseline 829/829 usable; bad board `bad_board` | `out/runs/2026-11-10T131257/` |
| Nov 10, 13:18 | **CONSTRUCTED** finished-wrong demo | loop `finished` (exit 0); checker flags Glean (exit 1) | `DEMO_FINISHED_WRONG.md` |
| Nov 10, 19:09 | **Real run 3, live** | incomplete, exit code 1; **OpenAI: 4 real new postings** (total still 829, so ids changed, not the count); Glean and Palantir 0 new; bad board `bad_board`; check_run.py: 0 problems | `out/runs/2026-11-10T190937/` |

**The agent trace with the deliberate failure:** `out/runs/2026-11-10T131257/trace.jsonl` (also run 1). Every request, response status, and board result is one line; the bad board's 404 is recorded with no retry and no invented value.

**Two real days:** my manual captures are from Nov 8 and Nov 9; all agent runs are on Nov 10. I missed my plan to run the agent before midnight on Nov 9 (FRICTIONAL Entry 7).

## Documents
- `GATE.md`: exits, budgets, repeat rule, error policy, permission policy, 12 wrong versions; committed before any code (`e9b38ea`), with a dated revision
- `BOUNDARY_TESTS.md`: 16 predictions (`9c5efe0`) plus actual results added afterwards (16/16 match)
- `REVIEW_PACKET.md`: the string-id fix, revised for scope and then accepted
- `DEMO_FINISHED_WRONG.md`: finished-wrong answer + independent check
- `SOURCES.md`, `FRICTIONAL.md`

## Sign-off — Job-Search Agent 2

**Checked**
- Exits: `test_all_boards_ok_is_finished`, `test_failed_board_makes_run_incomplete_not_finished` (no invented zero); live: runs 1 and 2 ended `incomplete`, exit code 1 verified in run 2
- Error policy: `test_no_retry_on_404`, `test_retry_once_on_5xx_then_fail` (exactly 2 requests, one 2-second wait); live: real 404 handled with 1 request
- Budgets: `test_request_budget_stops_before_sending`, `test_retry_not_sent_when_budget_runs_out`, `test_time_budget_stops_before_sending`
- Repeat rule: `test_duplicate_board_is_repeat_blocked`
- State: `test_state_not_advanced_for_failed_board`, `test_baseline_then_only_new_ids_and_no_collision_across_boards`; live: run 2 found 2 real new Glean postings
- Evidence: `test_raw_response_and_trace_are_saved`
- Independent check: `test_checker_flags_empty_board_that_loop_called_finished`, `test_checker_finds_nothing_on_normal_board`; demo run flagged, real run 2 clean
- Permission policy: 16 boundary tests B1–B16 (`tests/test_policy.py`), each predicted before running
- String ids: `test_string_ids_are_tracked_not_dropped`, `test_empty_or_missing_ids_are_still_unusable`; replay on identical input 0/1,129 → 1,129/1,129 usable

**How**
- Tests written by me before reading Claude's code: policy tests (`cbc3d7c`) and loop tests (`ad15913`) before the implementation (`7596cdf`); string-id test (`9684c62`) before the accepted fix (`e7ae2b0`). `git diff tests/ GATE.md BOUNDARY_TESTS.md` was empty after every Claude Code change.
- By hand: board captures with curl; reading both patch diffs; `git diff agent/watch.py` empty after the revision; agent exit codes; removing the two empty state files.
- By recomputation: the before/after usable-id counts on the same replay input; check_run.py counts postings itself from raw files instead of trusting the loop.
- With Claude's help: Claude Code wrote all new code in `agent/`, `check_run.py` and `config/boards.json`. Claude (chat) helped me break down the assignment, reviewed my GATE.md, drafted the boundary predictions and test skeletons (I wrote every assert), wrote the Claude Code prompts, and drafted the review packet, demo write-up, and this README from my results, which I checked against the evidence files.

**Not checked**  
1. Redirect hops count toward the request budget, but the budget is checked only before each attempt's first request, so a redirect chain could slightly exceed 10 requests (GATE.md revision).
2. A slow, trickling response can run past the 60-second budget; httpx timeouts apply per step, not to the whole request.
3. Two runs at the same time could clash on a state file.
4. The symlink check runs just before each write; a symlink swapped in between the check and the write isn't handled.
5. Whitespace-only ids (`" "`) are accepted, and string ids aren't checked to be well-formed UUIDs.
6. The checker flags only boards that drop to 0 postings, not a large drop to some other number, and it flags a genuinely empty board too.
7. Redirect and symlink refusals were tested only against a fake network and temporary folders, never live.
8. Pagination: each board was read as one response; I didn't check whether Lever or Ashby can split results across pages.

**Not claiming**
- That the loop finds every new job, or that any posting is a good fit for Alex. The JS1 rule and Claude judge are not part of this loop.
- That the permission policy stops a different agent with shell access (as JS1's Way 3 showed, an agent with `curl` can bypass my code's allow-list).
- That behavior generalizes beyond these 4 boards, 3 systems, and 3 live runs on one day.

**Signed or Withheld** Signed PAVAN JAYANT MAJJI - 11/10/2026

## Driver's seat
| Part | Claude did | I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| **Loop:** GATE.md | Reviewed my draft; found 3 gaps | Wrote it; decided exits, budgets, retries, permissions | It defines when the loop has succeeded or failed | `e9b38ea` before any code; FRICTIONAL Entry 3 |
| **Loop:** boundary predictions | Drafted the 16 rows from my GATE | Checked and committed them before tests | Predictions only mean something if made before running | `9c5efe0`; results appended, 0 deletions (`1fd82d6`) |
| **Loop:** tests | Gave skeletons with TODOs | Wrote every assert, before the code | Tests must not come from the code they test | `cbc3d7c`, `ad15913` before `7596cdf` |
| **Loop:** implementation | Claude Code wrote policy, adapters, loop, checker | Ran all tests myself; reviewed its 19 choices; recorded 2 as a GATE revision | Writing code is where Claude is strong | `7596cdf`; FRICTIONAL Entry 6 |
| **Loop:** live runs | Nothing | Ran them, checked exit codes, read results | Only real runs show real behavior | runs 1 and 2; FRICTIONAL Entries 7, 11 |
| **Review:** defect and test | Claude Code first spotted the id rule (read-only session) | Reproduced it live and on replay; wrote the failing test | The test defines what "fixed" means | `0763f21`, `9684c62` |
| **Review:** patch | Claude Code wrote v1, then v2 | Read v1 as behavior, rejected its scope, asked for v2 | Scope is a decision, not a code detail | `evidence/review/3_patch_v1.diff`, `5_patch_v2_revised.diff` |
| **Review:** decision | Reported side effects honestly | Accepted v2 on evidence (40 tests, before/after counts, watch.py unchanged) | Only I sign off on what goes in | `e7ae2b0`; `REVIEW_PACKET.md` |
| **Sign-off** | Drafted the wording | Chose what's "Not checked"; signed or withheld | Only I know what I didn't test | This section |