# Job-Search Agent 2 — The Loop, the Tools, and the Diff (nishant-u)

## What this is

A bounded loop that watches five public job boards across two applicant-tracking systems, Greenhouse
and Ashby, for one fictional résumé (Priya Nair). It works under a permission policy enforced in code,
and it changed only through a reviewed diff.

- **Gate first.** The exits, budgets, repeat rule, error policy and permission policy were written in
  `GATE.md` before any code.
- **The loop** (`agent2/loop.py`) ends in exactly one of `finished`, `incomplete`, `budget-exhausted` or
  `error`. It saves every raw response verbatim with its sha256, writes a trace line per observation,
  and reports only postings new since the last run, judged by my JS1 rule.
- **The outcome check** (`agent2/check.py`) is separate from the loop and reads only the saved raw
  responses.
- **What the agent never does:** apply, email, message anyone, log in, POST or delete anything. It only
  sends GET requests to `boards-api.greenhouse.io` and `api.ashbyhq.com`.

| # | System | Board | Why it's in the plan |
|---|---|---|---|
| 1 | Greenhouse | `faire` | Wholesale e-commerce; my JS1 board |
| 2 | Greenhouse | `instacart` | Grocery e-commerce |
| 3 | Ashby | `poshmark` | Resale e-commerce, the second system |
| 4 | Greenhouse | `poshmark` | A real board that returns HTTP 200 with 0 jobs: the finished-wrong-answer case |
| 5 | Greenhouse | `no-such-board-js2-test` | Fails on purpose (HTTP 404) |

Profiles: `full` runs boards 1–5 and ends `incomplete` because of board 5. `demo` runs boards 1–4.

## What I started from

- **My JS1**, branch `nishant-u-js1`, final commit `d63ee48`. It was copied unchanged into this folder
  in `ca43940`. JS1's files (`agent/`, `CONTRACT.md`, `experiment/`, `runs/`, `seeded/`, `state/` and
  JS1's tests) are kept as they were. JS2 reuses JS1's rule judge (`agent/rules.py`), validator, résumé
  check and the optional Claude judge.
- **Endpoint formats** checked against the instructor's collector Lectern
  (`fall-2026/nik-bear-brown/lectern/collect.py`) and the Reallocation Engine's providers
  (`scripts/ats/providers/*.mjs` and `.claude/skills/greenhouse-watch/`). The Greenhouse URL is
  `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true`. The Ashby URL is
  `https://api.ashbyhq.com/posting-api/job-board/<board>`.
- I wrote no code from Lectern or the Reallocation Engine. `agent2/` is new.

## Language and toolchain

- **Python 3.12, standard library only.** Nothing to install. Tested on Python 3.12.10.
- **Tests:** `unittest`. No test touches the network: they use fakes and constructed fixtures.
- **Tested on:** Windows 11 with Git Bash. The commands below use `python`; in Git Bash `python3` also
  worked for JS1.
- **Windows clone:** other folders in this course repository have paths longer than Windows' default
  limit. Clone with `git clone -c core.longpaths=true ...`, or checkout fails before this folder is
  reached.
- **Optional:** the Claude Code CLI (`claude`), logged in, only for `--claude`. Without it the Claude
  judge records "not run".
- **macOS:** with a python.org install, HTTPS may need the bundled "Install Certificates.command" before
  live runs. This hasn't been tested here.

## Commands

Run everything from this folder (`fall-2026/nishant-u/js2-loop-tools-diff/`).

**Tests** (offline; JS1's 66 and JS2's 65):

```bash
python -m unittest discover -s tests -t . -v
```

Expected: `Ran 131 tests`, `OK (skipped=1)`. The skip is boundary case 8 if your OS refuses to create a
symlink (see `POLICY.md`).

**Replay a saved run, no network.** Use a scratch `--out` so the committed runs and states are left alone:

```bash
python -m agent2.loop --profile full --replay-dir out/full/runs/2026-11-10-1 --out /tmp/js2-replay
python -m agent2.check /tmp/js2-replay/runs/<run printed above>
```

Expected: `exit incomplete; 5 requests` (board 5 fails with 404 and board 4 is `unverified-empty`), and
the check flags `zero-postings greenhouse:poshmark` and `cross-system poshmark`. In PowerShell, use a
path such as `$env:TEMP\js2-replay`.

**Live runs** (GET only, 5 requests at most per run):

```bash
python -m agent2.loop --profile full --out out/full     # boards 1-5; ends incomplete (the 404 board)
python -m agent2.loop --profile demo --out out/demo     # boards 1-4
python -m agent2.check out/full/runs/<run>              # the outcome check, separate from the loop
```

Each output root holds its own `state/seen_ids.json`. The CLI has no state-path flag, so separate states
mean separate `--out` roots.

## What actually ran

| Commit | What it is |
|---|---|
| `ca43940` | JS1 `d63ee48` copied unchanged into this folder |
| `58d6431` | `GATE.md`, written before any code |
| `c5ee0fe` | Gate amendment before code: the two profiles, `read_file`, merge-only `update_state` (Claude Code found the 3 gaps) |
| `e666f6e` | 62 JS2 tests written from the gate before any implementation; all failed (`ModuleNotFoundError: agent2`) |
| `5e3e3d0` | The implementation: loop, providers, policy, outcome check; 128 tests OK, 1 skip |
| `d5640de` | Gate amendment after implementation: the 8 decisions Claude Code made, accepted by me |
| `6399099` | Live runs: `out/demo/runs/2026-11-10-1` (finished) and `out/full/runs/2026-11-10-1` (incomplete, the 404 board), plus `FINISHED-WRONG.md` |
| `c050acd` | Second live demo run, `out/demo/runs/2026-11-10-2`: finished, "0 new" on the empty board |
| `4ba8bd3` | Review packet: gate amendment, reproduction, regression test failing before the patch |
| `bccbc41` | Review packet: scope widened before the patch (4 planned test changes) |
| `cd15d19` | The accepted patch: an empty 200 board is `unverified-empty` and the run is `incomplete` |
| `c51b1af` | Post-patch live demo run, `out/demo-postpatch/runs/2026-11-10-1`: incomplete |
| `98ae593` | Second live full run, `out/full/runs/2026-11-10-2`: incomplete, 4 real new Instacart postings |
| this commit | Final docs: README, POLICY, SOURCES, FRICTIONAL, sign-off and driver's seat |

**The finished-wrong-answer evidence** is the two pre-patch live demo runs, `out/demo/runs/2026-11-10-1`
and `out/demo/runs/2026-11-10-2`, made by the code at `5e3e3d0`. Both ended `finished`. The second
reported Greenhouse poshmark as "0 postings, 0 new", while the independent check flagged it from the raw
responses (`FINISHED-WRONG.md`). The post-patch run `out/demo-postpatch/runs/2026-11-10-1` shows the
fix: the same live boards end `incomplete`, with Greenhouse poshmark `unverified-empty`. After the
patch, the demo profile no longer reproduces the wrong answer.

**The live runs, all on 2026-11-10:**

| Run | Code | Exit | Notes |
|---|---|---|---|
| `out/demo/runs/2026-11-10-1` | pre-patch | `finished` | fresh state; every board a baseline |
| `out/full/runs/2026-11-10-1` | pre-patch | `incomplete` | the 404 board failed, not retried, "unknown", not "0 new" |
| `out/demo/runs/2026-11-10-2` | pre-patch | `finished` | the wrong answer: Greenhouse poshmark "0 postings, 0 new" |
| `out/demo-postpatch/runs/2026-11-10-1` | post-patch | `incomplete` | Greenhouse poshmark `unverified-empty` |
| `out/full/runs/2026-11-10-2` | post-patch | `incomplete` | Instacart 88 → 92: 4 new ids, all judged `not_relevant` by the rule (R1 or R3) |

Every live run contacted only `boards-api.greenhouse.io` and `api.ashbyhq.com` (the trace's `host`
column and the raw sidecars' URLs).

## Where each required artifact is

| Required | Where |
|---|---|
| README (language, toolchain, commands, what ran) | this file |
| `GATE.md` | `GATE.md`, with all amendments, dated |
| The code and tests | `agent2/` (`loop.py`, `providers.py`, `policy.py`, `check.py`); `tests/test_js2_*.py`, `tests/js2_helpers.py`, `tests/js2_mutants.py` |
| The agent trace of a real run, with the deliberate failure | `out/full/runs/2026-11-10-2/trace.jsonl` and `report.md` (post-patch); `out/full/runs/2026-11-10-1/` (pre-patch) |
| The finished-wrong-answer demonstration | `FINISHED-WRONG.md` |
| The permission policy and boundary-test table | `POLICY.md` |
| The review packet | `REVIEW-PACKET.md` |
| The sign-off and driver's seat | below |
| Saved raw responses | `out/*/runs/*/raw/` (each `.body` verbatim, with a `.meta.json` holding the URL, HTTP status, time and sha256); check outputs `out/*/check-*.json`; states `out/*/state/seen_ids.json` |
| `SOURCES.md`, `FRICTIONAL.md` | `SOURCES.md`, `FRICTIONAL.md` |

## Sign-off

```text
Sign-off — Job-Search Agent 2
Checked: the gate came before code (58d6431; amendment c5ee0fe before the tests in e666f6e); the four exits (test_js2_loop Exits); budgets, including a retry blocked by the budget (test_js2_loop); the repeat rule and the error policy per HTTP outcome (test_js2_loop ErrorPolicy); no invented value for a failed board (the live full run: the 404 board shows "unknown", not "0 new"); all 15 boundary cases, predicted in GATE.md before code (test_js2_policy); the six wrong versions are caught (test_js2_mutants); the outcome check reads only the raw responses (test_js2_check, plus the live runs); the review fix (test_js2_review).
How: by hand: none. Commands I ran myself: the regression test before the patch (2 failures on bccbc41) and after (3 ok), the full suite (131 tests, 1 skip), and git diff --stat. Tests written before Claude's code existed: e666f6e (62 tests, written by Claude Code from my gate, all failing before the implementation) and the regression test 4ba8bd3 (before the patch). With Claude's help: the boundary-case table was checked against GATE.md by Claude in claude.ai and reviewed by me; the code, the tests and the doc drafts were written by Claude Code.
Not checked: boundary case 8 (a real symlink) on this machine, which was skipped (a junction was refused, but that isn't a committed test); an empty Ashby board (every empty-board test uses Greenhouse); telling a company that truly isn't hiring from a wrong board (both now end incomplete); the Claude judge on Ashby postings (not run); redirect hops counted against the budget (they aren't); macOS and Linux; each host's terms beyond its API docs, and any rate limit.
Not claiming: that the outcome check catches every wrong answer (it catches only zero-posting boards and cross-system zero vs non-zero); that the policy is a sandbox (it's a preflight, and JS1's claude_judge writes inside an approved folder without going through policy.py); that "finished" means correct.
Signed: Nishant U, 2026-11-10.
```

## Driver's seat

| Task | Claude did | I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| Gate (exits, budgets, policy) | Drafted it; Claude Code found 3 gaps | Approved it and its amendments before code | The loop's limits are commitments I'm accountable for | 58d6431, c5ee0fe, d5640de |
| Boundary predictions | Drafted the 15 cases | Approved them before any code; checked the test table against them | A prediction only counts if it comes before the result | GATE.md; POLICY.md |
| Loop, tests and code | Claude Code wrote the tests, then the code | Set the order; chose the boards and the deliberate failure | What runs against real hosts is my responsibility | e666f6e then 5e3e3d0 |
| The review | Claude Code wrote the regression test and the patch | Widened the scope before the patch, ran the tests myself before and after, decided to accept | Accepting a change is a judgment on evidence | bccbc41 run; REVIEW-PACKET.md Decision; cd15d19 |
| Live runs | Claude Code ran them | Set limits: no push, separate states, each run reported verbatim | Authority over my repo and over live requests stays with me | out/ runs; FRICTIONAL |
