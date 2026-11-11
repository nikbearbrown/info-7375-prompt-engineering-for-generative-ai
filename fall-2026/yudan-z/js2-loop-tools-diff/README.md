# Job-Search Agent 2 — The Loop, the Tools, and the Diff

## Executive summary

This is the second layer of my job-search agent. The JS1 agent watched one board; this one is a **bounded loop** over five boards on **three applicant-tracking systems**.
- **Policy:** every network request and file write goes through a permission policy enforced in code.
- **Exits and budgets:** every run ends with one of four exit statuses, inside written budgets.
- **Change control:** the agent's code changes only through a reviewed diff.

I wrote the rules first (`GATE.md`, commit `a78bea8`). The tests were committed before the loop code (`ff7a40c`), and everything after that is traceable in the commit history, printed in `review/git-log.txt`.

> **About the commit history.** The zip and the GitHub folder do not contain my local `.git` folder: GitHub's web upload does not carry it, and its old file versions still hold the local details removed in FRICTIONAL #17. `review/git-log.txt` is a printed copy of the full history (every hash, time, message and changed file), made from the repository on my machine, which I can show on request. Nothing in the README commands needs git.
- **Real run 1** read 1,561 postings from 4 boards; the deliberate failing board gave a 404, so the run ended `incomplete`, as GATE requires.
- **Real run 2**, the next day, found 34 new postings and judged each one; the failing board again made it `incomplete`.
- **A separate real run** ended `finished` with a wrong answer (Ramp read on the wrong system), and an independent check caught it.
- **The reviewed change** fixed R3, which had been rejecting **364 real US postings**.

- **Student:** Yudan Zhou
- **Started from:** my own Job-Search Agent 1 code, copied unchanged (`317d931`). Not the Reallocation Engine and not Lectern. I read Lectern on 2026-11-09 and took one idea from it (refuse redirects), recorded as a GATE revision.
- **Persona:** fictional, `persona/resume.json` (`@example.com`, `555`), the same one as in JS1.
- **Language:** Python 3, standard library only.

## Toolchain

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.14.2 (3.9+ should work; nothing to `pip install`) | everything |
| Git | 2.x | `git diff` in the review |
| Claude Code CLI | 2.1.314 (`npm install -g @anthropic-ai/claude-code`, then log in once) | only to repeat the review session; the agent itself never calls Claude |
| OS | Windows 11, PowerShell and Git Bash | — |

Network access is needed only to `boards-api.greenhouse.io`, `api.ashbyhq.com` and `api.lever.co` (`config/allowlist.json`).

## Exact commands (run from this folder)

```bash
# 1. offline tests: 87 tests, no network
python -m unittest discover -s tests -v

# 2. one bounded run over config/boards.json (4 real boards + 1 that fails on purpose)
python -m agent.cli --workdir runs/try          # a new folder starts with a baseline (0 new per board)
#    exit codes: 0 finished · 2 error · 3 incomplete · 4 budget-exhausted
#    budgets may be lowered, never raised:  --max-requests 3  --max-seconds 30  --max-boards 2

# 3. the finished-wrong-answer demonstration and its independent check
python -m agent.cli --workdir runs/try-wrong --boards config/boards-wrong-ats.json
python check/crosscheck.py runs/try-wrong/run-<stamp>.json

# 4. an approval-gated write: resetting one board's seen ids
python -m agent.cli --workdir runs/try --reset-state greenhouse/pinterest                                        # refused
python -m agent.cli --workdir runs/try --approve reset-state:greenhouse/pinterest --reset-state greenhouse/pinterest  # allowed

# 5. the review packet's evidence, re-derived from run 1's saved responses
python review/reproduce_r3.py
python review/compare_behaviour.py               # the rule before the R3 change (review/rule_before_r3.py) vs agent/rule.py: 364 changed, 0 verdicts
python review/run2_old_vs_new.py runs/live/run-20261110T234346Z.json   # run 2's new postings: JS1 rule vs now
```

On Windows, set `PYTHONUTF8=1` if the console shows encoding errors. Use a new `--workdir` to avoid changing the submitted runs.

## What ran

| Date | What | Result | Evidence |
|---|---|---|---|
| 2026-11-09 | Tests, run by me in my own PowerShell | 86/86 OK | `review/07-yudan-ran-tests.txt` |
| 2026-11-09 21:11 UTC | **Run 1, real**, `config/boards.json` | Pinterest 167 · Databricks 918 · Ramp 172 · Palantir 304, all baselines; `no-such-board-js2` **HTTP 404, not retried, no count reported**. Exit **`incomplete`** (code 3), 5/12 requests, 3.1 s | `runs/live/` (trace, raw responses, state, `run-*.md`, `terminal-run1.txt`) |
| 2026-11-09 21:11 UTC | **Finished wrong answer, real**, Ramp under Greenhouse | exit `finished`, Ramp = 1 posting. **The crosscheck flagged it: Ashby lists 176** | `FINISHED-WRONG.md`, `runs/wrong-ats/` |
| 2026-11-09 | **Review**: R3 and state names written in full | revised once, then accepted | `REVIEW-PACKET.md`, `review/` |
| 2026-11-10 23:43 UTC | **Run 2, real**, second calendar day, same `runs/live/` state | **34 new postings**: Pinterest 6 (165 listed) · Databricks 16 (920) · Ramp 9 (177) · Palantir 3 (304). All 34 judged `not_relevant` for the persona, each with its failed checks. `no-such-board-js2` 404 again, not retried. Exit **`incomplete`** (code 3), 5/12 requests, 3.0 s. On 2 of the new postings the accepted R3 change gave a different R3 result from the JS1 rule (fail → pass), with no verdict changed | `runs/live/run-20261110T234346Z.md`, `terminal-run2.txt`, `review/14-run2-js1-rule-vs-now.txt` |

### How to read the trace

`runs/live/trace-<stamp>.jsonl` has one line per tool call, in order. A line looks like this:

```
{"t": 3.052, "tool": "fetch", "target": "https://boards-api.greenhouse.io/v1/boards/no-such-board-js2/jobs?content=true", "outcome": "http-404", "retry": false, "bytes": 38}
```

- `t` is seconds since the run started.
- Every request, every write and every refusal is a line.
- A 404 has no `retry: true` line after it, because GATE §5 says a missing board is not retried.

## Folder map

- `GATE.md`: exits, budgets, repeat rule, error and permission policy, written first.
- `POLICY.md`: the policy and the boundary-test table, predicted then observed.
- `FINISHED-WRONG.md`, `REVIEW-PACKET.md`.
- `agent/`: `loop.py`, `tools.py`, `policy.py`, `ats.py`, `cli.py`, plus the JS1 `rule.py`, `persona.py` and others.
- `check/crosscheck.py`: the independent check.
- `tests/`, `config/`, `runs/`, `review/`, `CONTRACT.md` (from JS1, with a new dated revision), `SOURCES.md`, `FRICTIONAL.md`.

---

## Sign-off — Job-Search Agent 2

**Checked**, and by which of my own tests:
- **Exits.**
  - A failed board makes the run `incomplete`, never `finished`, and reports no count and no "0 new" (`test_404_not_retried_and_run_is_incomplete`).
  - A bad response shape stops the run with `error` (`test_bad_shape_stops_with_error`).
  - A policy refusal stops the run with `error` before any request (`test_policy_refusal_stops_with_error`).
  - Each exit has its own exit code. Real run 1 ended `incomplete` because of the deliberate 404.
- **Budgets.**
  - Retries count against the request budget (`test_retries_count_against_request_budget`, W4).
  - There are budgets on seconds and boards (`test_seconds_budget`, `test_board_budget`).
  - A budget can be lowered but not raised (`test_budget_can_be_lowered_not_raised`).
- **Repeat rule.**
  - A board listed twice is fetched once (`test_board_listed_twice_fetched_once`).
  - Evidence is never written twice (`test_evidence_write_twice_is_refused`).
- **Error policy.**
  - No retry on 404 (W2).
  - One retry on a timeout or 5xx (`test_timeout_retried_once_then_ok`, `test_timeout_twice_fails_after_two_requests`, `test_5xx_retried_once_only`).
  - A failed board keeps its seen ids (`test_failed_board_keeps_its_seen_ids`, W5).
- **Workdir outside `runs/`:** refused with `error` before any request (`test_workdir_outside_runs_refused_before_any_request`, added after Claude found the gap while trying the README commands).
- **Permission policy.** 19 boundary cases, predicted before running, all as predicted in my own test run (`POLICY.md`), including the prefix trick (W3), a directory-junction escape and a redirect.
- **The reviewed change.** My predictions became `tests/test_r3_full_state_names.py` before the patch. The behaviour change was measured on 1,561 real postings.

**How:**
- By tests written from GATE before the loop code existed. Claude wrote them; the commit order is `ff7a40c` → `14909bd`.
- By commands I ran myself: the full test suite and the behaviour comparison (`review/07`, `review/08`). I also read `git diff agent/rule.py` on my screen.
- By an independent check that does not import the agent (`check/crosscheck.py`).
- With Claude's help: all code, the tests, the predictions in `POLICY.md` (drafted from rules I approved), and reading all 88 changed locations in the review.

**Not checked:**
1. A real timeout, 5xx or budget exhaustion against the live APIs. Those paths are tested only with a fake fetcher and a fake clock. The only real failure was the 404.
2. A real **relevant** posting. Run 2 found 34 real new postings, but none was relevant for the persona, so the path that reports a relevant job has run only in tests.
3. A true symbolic link. This Windows account cannot create one (WinError 1314), so B09 used a directory junction.
4. Whether the 4-city list stops other cities of the country Georgia from reading as the US state (for example `Gori, Georgia`).
5. Boards on SmartRecruiters, Workday or any system other than the three. A company that is on none of them is invisible to this agent.
6. macOS/Linux.

**Not claiming:**
- That `finished` means right: `FINISHED-WRONG.md` shows the opposite.
- That the crosscheck catches a wrong board name on the right system (the HubSpot `hubspot` / `hubspotjobs` case in Lectern's notes).
- That the R3 fix changes which jobs I should apply to: no final verdict changed on run 1's data.

**Signed or withheld:** Signed — Yudan Zhou, 2026-11-10

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| **Loop rules** (boards, budgets, retries, approvals) | proposed options, and drafted the exits, repeat rule and W1–W5 | **chose** the four boards, 6/12/120, retry once only for temporary errors, and approval for both risky writes; approved the whole GATE | a budget or a retry rule is a promise about my time and other sites' servers | `GATE.md` (`a78bea8`), FRICTIONAL #2 |
| **Policy change** | found the redirect gap while reading Lectern | **decided** to close it, as a dated GATE revision | the policy is mine to change, and only in writing | GATE Revisions, `30a3ac7` → `eedf18d` |
| **Review: expected answers** | listed the hard locations | **predicted** each one (D.C., `Remote - California`, `California` alone pass; `Tbilisi, Georgia` fails) | the test is the spec, and the spec is my judgment | `tests/test_r3_full_state_names.py` (`20799aa`) |
| **Review: the patch** | a separate Claude Code session wrote it, then revised it | **chose to revise** (Georgia, and the unapproved "Revision" wording), then **accepted** | accepting code I can't explain would be signing for it blind | `REVIEW-PACKET.md` §6; `review/10-revision-prompt.txt`; `59e9c5c` |
| **Verification** | wrote the reproduce and compare scripts | **ran** the tests and the comparison in my own terminal | "the commands you ran yourself" can't be delegated | `review/07-yudan-ran-tests.txt`, `review/08-yudan-ran-compare.txt` |
| Code, tests, drafts | wrote them | read the results and decided what to keep | — | `review/git-log.txt` |
