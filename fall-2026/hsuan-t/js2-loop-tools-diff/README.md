# Job-Search Agent 2: The Loop, the Tools, and the Diff

The agent from Job-Search Agent 1 watched one board. This layer runs it as a **bounded loop over four boards on two applicant-tracking systems** (one board misspelled on purpose), under a **permission policy enforced in code**, and changes it through **one Claude Code patch I reviewed against a test I committed first**. The rules came first, in [`GATE.md`](GATE.md); when the code and GATE disagree, GATE wins.

## What I started from

My own Job-Search Agent 1, unchanged as submitted: course repo folder `fall-2026/hsuan-t/js1-contract-and-watch/` (course commits 1043b4a and aab4313). That is the contract ([`CONTRACT.md`](CONTRACT.md)), the Stripe Greenhouse watch, the rule judge and the Claude judge. I did not use the Reallocation Engine or Lectern code. Where JS2 changed a JS1 rule, CONTRACT.md has a dated note (for example, check 2 now reads every place a board lists).

## Language and toolchain

| | Version used |
|---|---|
| Language | Python 3.11 (tested on 3.11.10, macOS) |
| Agent | Python standard library only (watch, loop, policy, rule judge) |
| Claude judge (off by default) | [Claude Code](https://claude.com/claude-code) CLI `claude`, logged in (tested on 2.1.319), called as `claude -p`; or `anthropic==2.3.0` + `ANTHROPIC_API_KEY` with `--claude-via api` |
| Tests | `pytest==8.4.2` |
| Boards | Greenhouse Job Board API (`boards-api.greenhouse.io`): `stripe`, `cloudflare`, `striqe` (misspelled, answers 404). Ashby Posting API (`api.ashbyhq.com`): `openai`. List: [`data/boards.json`](data/boards.json) |

## Exact commands (fresh clone)

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/hsuan-t/js2-loop-tools-diff
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt      # pytest + anthropic (anthropic is only for --claude-via api)

# Tests: fake boards, fake Claude, fake clock. No network, no cost, never touches state/ or runs/
.venv/bin/python -m pytest

# The loop, live, every board in data/boards.json, Claude off (the default)
.venv/bin/python -m job_agent

# The same with the Claude judge (needs `claude` logged in): every new posting until 30 calls or 300 s
.venv/bin/python -m job_agent --claude

# Offline: replay a saved response for one board instead of fetching it
.venv/bin/python -m job_agent --board stripe --from-raw evidence/raw/2026-11-08T234257Z/stripe_content.json

# The independent check (imports nothing from job_agent): each saved list against the board's own meta.total
.venv/bin/python checks/total_check.py demo/finished_wrong/out/evidence/raw evidence/raw/2026-11-08T234257Z
```

Exit status: 0 `finished`, 1 `error`, 2 `incomplete` or `budget-exhausted`. Each run writes `runs/<UTC>/summary.md`, `verdicts.json`, `trace.jsonl` (one line per request, skipped repeat, board end, Claude call and run end), saves every response under `evidence/raw/<UTC>/`, and updates `state/<board>.state.json` only for boards that ended `ok`. Error codes: [`ERROR_CODES.md`](ERROR_CODES.md).

A live run now compares against the state my Step 6 run left (2026-11-08), so its "new" counts will differ from mine.

## What ran

Both are live runs of all four boards, run by me. Trace, verdicts and summary in `runs/<id>/`, the raw responses in `evidence/raw/<id>/`, the terminal output in `evidence/runs/`.

| | `2026-11-08T224911Z`, Claude off | `2026-11-08T234257Z`, `--claude` |
|---|---|---|
| Exit | `incomplete`, status 2 (one board failed) | `budget-exhausted`, status 2 (Claude calls 30/30) |
| stripe (Greenhouse) | ok, fetched 766, **86 new** since 10/31 | ok, 766, 86 new |
| cloudflare (Greenhouse) | ok, 464, 0 new (first run: baseline) | ok, 464, 0 new |
| openai (Ashby) | ok, 816, 0 new (first run: baseline) | ok, 816, 0 new |
| **striqe** (misspelled on purpose) | **failed `101`** (HTTP 404), fetched `—`, new `—` | same |
| Budget used | boards 4/4, requests 4/10, 1.9 s / 120 s | requests 4/10; Claude 30 calls, 127.3 s / 300 s |
| Verdicts | 86 rule, 0 relevant | 86 rule + 30 Claude, 0 disagreements; 56 postings `304` (not sent: Claude budget used up) |

The failing board keeps no count: `verdicts.json` has `null`, the summary shows `—`, there is no `state/striqe.state.json`, and the 404 page Greenhouse sent is saved as `striqe_attempt1_error.txt`. Before the second run I put Stripe's state back to its 10/31 file so the Claude run had the same 86 new postings to judge; the first run had already moved it to 11/08. The numbers above were recounted from the raw responses and the trace with a separate script, not the agent's code (with Claude's help); they match.

The summary of the second run shows `seconds 129.1/120`: 120 is the board-phase limit, and the Claude phase has its own 300 s. That display was fixed afterwards (commit bef8083); the run record is kept as it was printed.

## Where each part of the brief is

| Brief | Where |
|---|---|
| The gate | [`GATE.md`](GATE.md): exits, budgets, repeat rule, error policy, permission policy, wrong versions. Written and committed before any JS2 code (see Driver's seat) |
| The loop, budgets, exits, record of every observation | `job_agent/loop/` (`runner.py`, `budget.py`, `exits.py`, `trace.py`, `codes.py`); the runs above |
| One board that fails on purpose | `striqe` in `data/boards.json`; handled as above |
| A finished wrong answer + the independent check | [`demo/finished_wrong/README.md`](demo/finished_wrong/README.md), `checks/total_check.py` |
| Permission policy in code + boundary tests | `job_agent/common/policy.py`; table with expected outcomes in GATE.md §5; `tests/test_policy.py::test_gate_row_01` … `_10` (31 tests in the file) |
| The review packet | [`REVIEW_PACKET.md`](REVIEW_PACKET.md) |
| Sign-off and driver's seat | below |
| Saved raw responses | `evidence/raw/` (JS2: `2026-11-08T224911Z/`, `2026-11-08T234257Z/`; the others are JS1's) |
| Commit history of my working repo | `evidence/git-history.txt` (this folder is one commit in the course repo, so the ids cited here are from there) |

## Tests

`.venv/bin/python -m pytest` runs 279 test cases. My own runs are saved in `evidence/tests/` and `evidence/step8_test_{red,green}.txt`.

| GATE item | Test |
|---|---|
| Wrong version 1: dedupe by job id only | `tests/test_loop.py::test_wv1_same_job_id_on_different_boards_is_processed_separately` |
| Wrong version 2: state saved before the board finished | `test_loop.py::test_wv2_failed_board_does_not_mark_new_posting_seen` |
| Wrong version 3: empty list / no `jobs` key read as 0 | `test_loop.py::test_wv3_empty_or_missing_jobs_list_is_a_validation_error` |
| Wrong version 4: failed board shown with 0 jobs | `test_loop.py::test_wv4_failed_board_has_no_job_count` |
| Wrong version 5 (added in Step 8): list not compared with `meta.total` | `tests/test_meta_total.py` (committed failing before the patch) |
| Exits, in GATE's order | `test_loop.py::test_exit_follows_gate_precedence`, `::test_three_ok_boards_and_one_404_is_incomplete` |
| Boundary tests 1–10 | `tests/test_policy.py::test_gate_row_01_…` to `::test_gate_row_10_…` |
| Each adapter, on a real saved response | `tests/test_adapter_conformance.py` |
| Claude budget, off by default | `tests/test_claude_budget.py` |
| Known limit, pinned on purpose | `tests/test_known_limits.py` (a posting the rule wrongly cuts, with Claude off) |

JS1's tests (`test_wrong_version_*.py`, `test_refuses.py`, `test_claude_*.py`) still run. Every test file was also checked by planting the bug it guards against and watching it fail (done by Claude; counts in the review packet and the task notes).

## Sign-off — Job-Search Agent 2

**Checked**
1. The run ends with the exit GATE §1 gives, and a deliberately failing board makes it `incomplete`, not `finished`: `test_loop.py::test_exit_follows_gate_precedence`, `::test_three_ok_boards_and_one_404_is_incomplete`; the Step 6 Claude-off run.
2. A failed board never gets a number it didn't return: `test_loop.py::test_wv4_failed_board_has_no_job_count`, `::test_wv3_…`; `striqe` in both Step 6 runs (`null` / `—`, no state file).
3. The permission policy refuses what GATE §5 says and asks before overwriting: `test_policy.py::test_gate_row_01` … `_10`.
4. Step 6's counts (Stripe 766 fetched, 86 new since 10/31; 30 Claude verdicts and 56 × `304`; striqe 101 with no count) match the raw responses and the trace.
5. A Greenhouse list that disagrees with its own `meta.total` now fails that board (`203`) instead of ending `finished`: `tests/test_meta_total.py`; the Step 7 input re-run after the patch.

**How**
1–3. By tests whose expected outcomes I wrote first: the exit table, the wrong versions and the ten boundary rows are in GATE.md (commit 614afb8), before the first JS2 code (64193dd) and before the policy tests (a076b1c). Claude wrote the test code; I ran the suites myself (`evidence/tests/`).
4. By recomputation, with Claude's help: a separate script read only `evidence/raw/` and `trace.jsonl`; I ran both runs myself (`evidence/runs/`).
5. By a test I committed before reading Claude's patch: I chose the expected behaviour, Claude typed the test, I ran it red (`evidence/step8_test_red.txt`) and committed it (3c4aa5a) before the patch (ee3018e); then I read the diff and re-ran the Step 7 input myself (`evidence/step8_demo_after_patch.txt`). Details: `REVIEW_PACKET.md`.

**Not checked**
1. A list and its `meta.total` that are both short in the same way (a stale index): the check compares the board with itself, so it passes (`REVIEW_PACKET.md` §8).
2. Whether an Ashby list is complete: Ashby sends no total, so OpenAI's list is never checked.
3. The retry path against a real failure: timeouts, connection errors and 5xx/429 (codes 102–104) were only tested with scripted fakes; both real runs needed one request per board.
4. What a non-integer `meta.total` (`"766"`, `true`) should do: today it is silently not checked, and no test pins it.
5. Which hosts `claude -p` itself contacts: my program checks every request it makes, but with the CLI the call to Claude is made by Claude Code, outside my allow-list.

**Not claiming**
- That `finished` means a board's list was complete. It means every board answered, in the right shape, with a count that agrees with itself.
- That the rule's verdicts are right. A posting the rule wrongly cuts is flagged only when Claude also sees it; with Claude off, or when the Claude budget runs out before it (`304`), it is one quiet `not_relevant` row (`tests/test_known_limits.py`, CONTRACT Known limits).
- That Claude agreeing with the rule on 30 of 30 says much: they were all Stripe sales titles, and Claude used prompt v1, the default.
- That the budgets are tuned: 30 Claude calls are shared by the whole run, so the first board in the list can use them all.
- That the Step 7 demo was observed in the wild: Greenhouse was never seen sending a short list; the demo input is seeded from a real response.

**Signed:** Hsuan-Hung (Isaac) Tai, 2026-11-09

## Driver's seat

Commit ids are from my working repo (`evidence/git-history.txt`). Quotes are mine, from the session; the FRICTIONAL entry named holds the context. Labels like "JS2 D21" in code comments and GATE point to my private task decision log; the decisions themselves are written out in `FRICTIONAL.md` and GATE's dated notes.

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| **Loop:** the gate | Wrote GATE's question skeleton; reviewed my draft and pointed out three problems | Wrote GATE.md; chose `finished` only when every board is `ok` | The exits and the policy define when the agent may say it succeeded | 9722ada (my draft), 614afb8 (final) before the first JS2 code 64193dd; FRICTIONAL "GATE.md review": "你的建議蠻有道理. 那就選B" |
| **Loop:** what can fail | Sorted my cases into "knows it failed" and "finished but wrong", added more, checked boards live | Listed the failures (board missing, connection, empty data, slow download); accepted the boards and the misspelled one | The error policy is my judgment of what the loop must survive | FRICTIONAL "What can go wrong in the loop", "Picking the boards" |
| **Loop:** budgets | Implemented them; flagged where GATE was silent | Set Claude's budget: every new posting, 30 calls, 300 s in total; kept 30 per run after seeing Stripe take all of them | Budgets decide cost; only I may change them (GATE §2) | bc7af0f (GATE) before e445625 (code); "改成總 total 時間 300 秒，因為 300 秒應該就會花費不少 token。然後呼叫次數設為 30" |
| **Loop:** rules from JS1 | Measured what reading every listed place changes | Decided JS2 may change JS1's rules | The contract is mine to amend | 4d1a32c, CONTRACT dated note; "目標就是讓JS2跑的時候可以順利，而不是因為之前規則怎麼樣而限製它" |
| **Loop:** known limit | Showed that rule misses never reach Claude; wrote the pinning test | Decided to document it and fix it later, not now | What I claim the agent does is mine to say | 08e3c9d; FRICTIONAL "Rule misses as a known limit"; "我覺得這算是已知的 limit，現在可以先不提著修" |
| **Loop:** the real runs | Recounted every number from raw and the trace | Ran both runs; chose to restore Stripe's 10/31 state for the Claude run | The evidence has to come from my own runs | `evidence/runs/2026-11-08_js2_run_terminal.txt`, `…_claude_terminal.txt`; 4ce7442 |
| **Review:** which change | Found the `meta.total` gap; offered to leave it out of GATE so Step 7 could show it | Chose to leave it out and fix it as the review-packet change | Picking what to fix, and when, is mine | FRICTIONAL "Empty fetch vs zero new jobs"; "好選A" |
| **Review:** the test | Asked me the three questions; typed the test | Chose the expected behaviour; ran it red and committed it before the patch | The test is the standard the patch is judged by, so it can't come from the patch | 3c4aa5a before ee3018e; `evidence/step8_test_red.txt` |
| **Review:** the patch | Wrote it (5 files); planted bugs to check the test | Read the diff as behaviour, judged the scope, ran the suite and the Step 7 input, accepted | Accepting code into my agent is my decision | ee3018e; `REVIEW_PACKET.md` §4–7; "改完 agent 會去判斷 meta.total (if exist) 如果抓下來的數量不一樣就報錯" … "看起來是在 scope 內的" |
| **Sign-off** | Drafted the wording and the candidate items | Chose what to claim and signed it | My name is on it | This section |
