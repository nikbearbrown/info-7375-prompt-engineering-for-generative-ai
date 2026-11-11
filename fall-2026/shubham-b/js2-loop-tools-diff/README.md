# Job-Search Agent 2 — The Loop, the Tools, and the Diff

**Student:** Shubham Bagwe · **Course:** INFO 7375 — Prompt Engineering for Generative AI (Northeastern University) · **Instructor:** Nik Bear Brown · **Assignment:** JS2, due 2026-11-10

The JS1 agent watched one board. This layer runs it as a **bounded loop over several boards on
two job systems** (Greenhouse and Ashby), with a budget, one exit status per run, a trace of
every observation, a **permission policy enforced in code**, and one change made by Claude Code
and reviewed on evidence. It is still discovery only: the agent never applies, emails, messages
or logs in. The résumé is still the fictional persona Kiran Joshi.

**Started from:** my own JS1 agent (this repository through `4b6c80f`), not the Reallocation
Engine or Lectern. **Start here:** [`GATE.md`](GATE.md), committed in `f524c91` before any JS2
code.

| Deliverable | Where |
|---|---|
| The gate: exits, budgets, repeat rule, error policy, permission policy, wrong versions | [`GATE.md`](GATE.md) (v0.1 + amendments A1, A2, A3) |
| The loop | [`src/job_search_agent/watch.py`](src/job_search_agent/watch.py), plan [`config/watch.toml`](config/watch.toml) |
| The permission policy in code | [`src/job_search_agent/policy.py`](src/job_search_agent/policy.py) |
| The second job system | [`src/job_search_agent/providers/ashby.py`](src/job_search_agent/providers/ashby.py) |
| Agent trace of a real run, with the deliberate failure | [`docs/js2/TRACE.md`](docs/js2/TRACE.md) → `data/watch/loops/2026-11-09T08-14-22Z/trace.jsonl` |
| A finished wrong answer and the independent check | [`docs/js2/FINISHED_WRONG.md`](docs/js2/FINISHED_WRONG.md), [`checks/check_watch.py`](checks/check_watch.py) |
| Permission policy and boundary-test table (B01–B27) | [`docs/js2/POLICY.md`](docs/js2/POLICY.md) |
| The review packet | [`docs/js2/review/REVIEW_PACKET.md`](docs/js2/review/REVIEW_PACKET.md) |
| Saved raw responses | `data/watch/boards/*/live/runs/*/raw/` (byte for byte, with SHA-256 in `.meta.json`) |
| Sign-off and driver's seat | [below](#sign-off--job-search-agent-2) |
| Sources, Frictional | [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) |
| Independent review of this work, and the fixes | [`docs/js2/REVIEW_BY_AGENT.md`](docs/js2/REVIEW_BY_AGENT.md) |

## Language and toolchain

| | |
|---|---|
| Language | Python ≥ 3.12 (run on 3.14.5) |
| Package manager | `uv` 0.11.0; dependencies pinned in `uv.lock` |
| Runtime libraries | `httpx`, `pydantic` (no new dependency in JS2) |
| Dev tools | `pytest`, `ruff`, `mypy --strict` |
| Model | None in the JS2 loop (backend `none`). JS1's `jsa run` still uses `claude-sonnet-5-5` through the `claude` CLI |
| Platform | macOS (darwin); nothing is macOS-specific |

## Commands (from a fresh clone)

```bash
uv sync                                   # create .venv from uv.lock
uv run pytest -q                          # full suite, offline (network blocked in tests); 1099 passed
uv run ruff check . && uv run mypy src    # lint and strict types

uv run jsa watch run                      # the loop over config/watch.toml (live; ~11 MB of downloads)
uv run jsa watch run --plan config/watch-wrong-board.toml    # the finished-wrong-answer plan
uv run python checks/check_watch.py data/watch/loops/<loop_id>   # the independent check
uv run jsa watch reset greenhouse/ramp    # the one write that needs approval: asks at a terminal
uv run jsa audit-privacy data/watch       # résumé values, credentials, absolute paths in outputs
```

`jsa watch run` exits 0 `FINISHED`, 8 `INCOMPLETE`, 9 `BUDGET_EXHAUSTED`, 10 `ERROR` (GATE §2).
It writes only under `data/watch/`: the loop's `trace.jsonl`, `report.json` and `report.md` in
`data/watch/loops/<loop_id>/`, and each board's JS1 run folder and state in
`data/watch/boards/<provider>-<token>/live/`. A run from a fresh clone continues from the
committed state, so its boards are no longer baselines; the write folder is fixed by the plan's
`[policy]` section.

The wrong-version meta-test (`tests/meta/test_js2_wrong_versions_caught.py`) runs `tests/watch`
once per wrong version W1–W9 in a child pytest and checks that the named test kills each one.

## What ran

All live, run by Claude: five on 2026-11-09 and two on 2026-11-10 ET (loop IDs are UTC; ET is UTC−5).

| Loop | Plan | Code | Exit | Boards | Requests | Independent check |
|---|---|---|---|---|---:|---|
| [`08-14-22Z`](data/watch/loops/2026-11-09T08-14-22Z/report.md) run 1 | `watch.toml` | `e955298` | `INCOMPLETE` (8) | Stripe 768, Figma 144, Ramp 169, Linear 32: `BASELINE`; `ashby/linearapp`: 404, `FETCH_FAILED`, not retried | 5 | 21 pass, 0 fail |
| [`08-16-13Z`](data/watch/loops/2026-11-09T08-16-13Z/report.md) | `watch-wrong-board.toml` | `e54a26d` | `FINISHED` (0) — wrong | `greenhouse/ramp` 1 stale posting, `BASELINE` | 1 | 3 fail |
| [`08-16-16Z`](data/watch/loops/2026-11-09T08-16-16Z/report.md) | `watch-wrong-board.toml` | `e54a26d` | `FINISHED` (0) — wrong, "no new jobs" | `greenhouse/ramp` `SUCCESS_NO_NEW` | 1 | 3 fail |
| [`08-23-46Z`](data/watch/loops/2026-11-09T08-23-46Z/report.md) after the patch | `watch-wrong-board.toml` | `8259d8b` | `ERROR` (10) | `greenhouse/ramp` `INVALID_RESPONSE`, `below_floor`; state untouched | 1 | 6 pass, 0 fail (7/7 with the checker as it was then) |
| [`08-27-13Z`](data/watch/loops/2026-11-09T08-27-13Z/report.md) run 2 | `watch.toml` (with A2 floors) | `127bf82` | `INCOMPLETE` (8) | Stripe 768, Figma 144, Ramp 169, Linear 32: `SUCCESS_NO_NEW`, no floor tripped; `ashby/linearapp`: 404 again | 5 | 25 pass, 0 fail |
| [`2026-11-11T01-14-05Z`](data/watch/loops/2026-11-11T01-14-05Z/report.md) after the revision | `watch-wrong-board.toml` | `b8097f1` + the revision, committed as `707ecea` | `ERROR` (10) | `greenhouse/ramp` `INVALID_RESPONSE`, `below_floor`; state untouched | 1 | 6 pass, 0 fail |
| [`2026-11-11T01-26-35Z`](data/watch/loops/2026-11-11T01-26-35Z/report.md) run 3 | `watch.toml` | `595a87e` | `INCOMPLETE` (8) | 48 new postings: Stripe 29 (of 779), Figma 6 (144), Ramp 12 (176), Linear 1 (33), all judgments deferred; one rule `MATCH` (Ramp, "Software Engineer, Security, Stablecoin"); `ashby/linearapp`: 404 | 5 | 25 pass, 0 fail |

Not run live: a retry (timeout or 5xx), and a budget stop. Both are shown only by constructed
tests (`tests/watch/test_loop.py`).

## Repository map (JS2 additions)

| Path | Contents |
|---|---|
| `GATE.md` | The gate, written before the code |
| `config/watch.toml`, `config/watch-wrong-board.toml` | The watch plan; the deliberate wrong-board plan |
| `src/job_search_agent/{watch,watch_cli,policy}.py`, `providers/ashby.py` | Loop, CLI, policy, Ashby |
| `tests/watch/` | Loop, budget, retry, repeat, policy boundary and floor tests; harness |
| `tests/wrong_versions/js2.py`, `tests/meta/test_js2_wrong_versions_caught.py` | W1–W9 and the meta-test |
| `checks/` | The independent check and the hand expectations it reads |
| `data/watch/` | Every loop run, every board's runs, raw responses and state |
| `docs/js2/` | Trace, finished wrong answer, policy, review packet, build log, evidence outputs |

## Sign-off — Job-Search Agent 2

```text
Sign-off — Job-Search Agent 2
Checked:       The wrong board by hand (Ramp on careers page vs Greenhouse endpoint); career portal links and min_postings floors for Stripe, Figma, Ramp, and Linear; the A2 patch diff (8259d8b) and pre-patch red tests (affcbdd); the live loop run 2026-11-09T08-23-46Z via check_watch.py (6 passed, 0 failed); test_pending_retry_from_an_old_raw_below_the_floor in tests/watch/test_floor.py catching mutation m2.
How:           By hand (checking ramp.com/careers and Greenhouse endpoint); by reading diffs and test logs myself; by a test I wrote before revising Claude's code (closing mutation m2); with Claude's help for running headless suites, collecting trace evidence, and drafting candidate limits.
Not checked:   (1) No live retry occurred in any live run; retry handling is verified only via constructed unit tests. (2) Ashby secondary locations are not evaluated; postings in SF and Toronto are treated as US-only. (3) Redirect hops inside one attempt are bounded by max_redirects rather than the request budget (GATE A1).
Not claiming:  That a FINISHED loop guarantees a board is the company's real hiring portal (only external checks verify that); that the floor catches stale boards that remain above min_postings; that any posting suits Kiran Joshi (judgments were deferred with model backend none).
Signed or withheld: Signed, Shubham Bagwe, November 10, 2026
```

## Driver's seat — Job-Search Agent 2

The "what Claude did" and evidence columns are facts from this build. The "what I should do"
column is Claude's draft for Shubham to edit; the last column is his to write.

| Part | What Claude should do (and did) | What I should do (Claude's draft; Shubham edits) | Evidence | Why that part stays mine |
|---|---|---|---|---|
| The loop's exits and budgets | Draft `GATE.md` from my contract; implement the exits, budgets and repeat rule exactly as written; flag when the code cannot do what the gate says (it did: amendment A1) | Decide what counts as finished, the budget numbers, and who may change them; adopt or change the gate | `f524c91` (gate before code), `0afcf05`, `e955298` (A1) | A machine will happily loop indefinitely or claim success on partial fetches; setting strict termination criteria and resource ceilings is an operational policy decision that belongs to the human engineer. |
| The error policy and the deliberate failure | Implement retry-once-for-transient; run the loop with a bad board name and show no value was invented | Decide which failures deserve a retry and which must escalate to me; read the trace | `docs/js2/TRACE.md`, events 18–22 | Distinguishing permanent faults (404s, invalid tokens) and rate-limit backoffs (429s) from transient network blips requires policy judgment to avoid spamming endpoints or obscuring genuine failures. |
| The permission policy | Implement the policy in code; write the boundary predictions before running the tests | Choose the hosts, the write folder, what needs my approval and what is never allowed; approve the one reset | `GATE.md` §6–7, `docs/js2/POLICY.md`, `tests/watch/test_policy.py` | Restricting network hosts, sandboxing filesystem writes, and requiring terminal confirmations for destructive resets constitutes the core security boundary of the agent. |
| The finished wrong answer | Find a natural wrong board, run it, write a checker that does not trust the agent | Confirm the careers-page facts and floors by hand | `docs/js2/FINISHED_WRONG.md`, `checks/expectations.toml` | The agent cannot know if an API response is semantically obsolete (e.g. Ramp returning 1 stale Dublin job on Greenhouse); only an external human check against live career portals can establish ground truth. |
| The review | Write the test before the patch; have a separate session write the patch; read the diff as behaviour; mutate it; recommend | Run the commands myself, read the diff myself, and decide accept, revise or reject | `docs/js2/review/REVIEW_PACKET.md`, `affcbdd` → `8259d8b` | Automated agents will readily approve green test suites that conceal brittle architectural dependencies; only a human review catches hidden ordering assumptions like FlooredProvider's first-parse coupling. |
| The sign-off | Collect facts and candidate limits | Decide what I can honestly claim, and sign or withhold | `docs/js2/FACTS_FOR_SIGNOFF.md` | Legal and engineering accountability for the code's behavior, unverified assumptions, and operational risks rests with me as the developer, never an automated assistant. |

---

## Job-Search Agent 1 — The Contract and the Watch (previous layer)

**Student:** Shubham Bagwe · **Course:** INFO 7375 — Prompt Engineering for Generative AI (Northeastern University) · **Instructor:** Nik Bear Brown · **Assignment:** JS1, due 2026-10-31

A discovery-only agent. It watches one public job board (Stripe on Greenhouse), remembers the posting IDs it has seen, and reports only postings that are new since the last run. Each new posting gets two separate verdicts:
- **Record:** a deterministic rule anyone can recompute (`CONTRACT.md` §6).
- **Judgment:** Claude's opinion under a prompt contract, validated against a fixed schema and labelled as an opinion (§8).

The résumé is a **fictional persona**, Kiran Joshi ([`persona/kiran-joshi.resume.example.json`](persona/kiran-joshi.resume.example.json)). The agent never applies, contacts anyone or logs in.

**Start here:** [`CONTRACT.md`](CONTRACT.md) was written and committed first (`053fda0`, before any code).

### Language and toolchain

| | |
|---|---|
| Language | Python ≥ 3.12 (developed and run on 3.14.5) |
| Package manager | [`uv`](https://docs.astral.sh/uv/) (0.11.0); dependencies pinned in `uv.lock` |
| Runtime libraries | `httpx`, `pydantic` |
| Dev tools | `pytest`, `ruff`, `mypy --strict` |
| Model | `claude-sonnet-5-5` through the `claude` CLI (Claude Code 2.1.314 for every recorded call), signed in with a Claude subscription. No API key is used or needed |
| Platform | macOS (darwin); nothing is macOS-specific |

### Commands (from a fresh clone)

```bash
uv sync                          # create .venv and install pinned dependencies
uv run jsa doctor                # offline checks: config, résumé gate, claude on PATH, data dir
uv run pytest                    # full suite: 973 tests, offline (the network is blocked in tests)
uv run ruff check . && uv run mypy src
```

Reproduce the seeded pair offline, without touching the graded `data/` folder:

```bash
uv run jsa --data-dir data/scratch run --replay evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json --model-backend none
uv run jsa --data-dir data/scratch run --replay data/live/runs/2026-10-30T01-52-15Z/raw/greenhouse-stripe.json --model-backend none
```

The first prints `BASELINE` (734 IDs). The second finds 3 new postings. With `--model-backend none` their judgments are `UNAVAILABLE`, so it reports `PARTIAL_FAILURE`. With `--model-backend claude-cli` (the committed pair) it reports `SUCCESS_WITH_NEW`.

Other commands:

| Command | What it does |
|---|---|
| `uv run jsa run` | Live run: fetch the board once, rule and judge each new posting |
| `uv run jsa rule <posting-id>` | Print the rule record for one posting |
| `uv run jsa verify-evidence` | Recompute every saved raw file's SHA-256 against its `.meta.json` |
| `uv run jsa audit-privacy` | Scan outputs for résumé values, credentials and absolute paths |
| `uv run jsa pending` | Inspect or drop judgments left pending |

A live run needs network access and a signed-in `claude`. Without `claude`, judgments are `UNAVAILABLE` and stay pending; the agent never falls back to an API key.

### What ran

All runs below are real and committed. Full tables: [`docs/RUNS.md`](docs/RUNS.md).

| Run | When (ET) | Status | Fetched | New |
|---|---|---|---:|---:|
| Live 1, baseline | 2026-10-29 21:52 | `BASELINE` | 736 | 0 |
| Live 2, second calendar day | 2026-10-30 23:03 | `SUCCESS_WITH_NEW` | 746 | 21 |
| Live 3, third calendar day | 2026-10-31 15:22 | `SUCCESS_NO_NEW` | 745 | 0 |
| Seeded 1 (replay of the 18:41 hand-check response) | 2026-10-29 22:21 | `BASELINE` | 734 | 0 |
| Seeded 2 (replay of live 1) | 2026-10-29 22:21 | `SUCCESS_WITH_NEW` | 736 | 3 |

- **Live 2:** both judges ran on all 21 new postings. The rule gave `NO_MATCH` on all 21. Claude's 21 replies were all valid and all `NOT_RELEVANT`.
- **Live 3:** no posting was new. The board had shrunk to 745, and the 757 IDs seen so far are kept: a disappeared ID is never forgotten (CONTRACT §10).
- **Evidence:** raw responses are saved byte for byte with their SHA-256 (`data/live/runs/*/raw/`); state is in `data/live/state.json`. `verify-evidence` passes on every file.

### The three chapter artifacts

| Chapter | Report | Headline |
|---|---|---|
| 1. Sampling | [`docs/experiments/SAMPLING.md`](docs/experiments/SAMPLING.md) | 5 postings × 4 fresh calls: 20/20 valid; 15/20 agree with my labels; 8249901 is unanimous and wrong |
| 2. Prompt experiment | [`docs/experiments/PROMPT_EXPERIMENT.md`](docs/experiments/PROMPT_EXPERIMENT.md) | v1 → v2 (only `label_definition` changed): dev 7/10 → 10/10, held-out 6/10 → 10/10 |
| 3. Action surfaces | [`docs/experiments/ACTION_SURFACES.md`](docs/experiments/ACTION_SURFACES.md) | Chosen: surface (a), stdin with no tools |

### Repository map

| Path | Contents |
|---|---|
| `CONTRACT.md` | The contract (written first) |
| `src/job_search_agent/` | The agent ([`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) |
| `tests/` | Unit, contract and meta tests. CONTRACT → code → test map: [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) |
| `prompts/` | `judge.v1.md`, `judge.v2.md`, `CHANGELOG.md` |
| `persona/` | The fictional résumé |
| `evidence/` | The hand-check raw response (2026-10-29 18:41 ET) |
| `data/live/`, `data/seeded/` | Run outputs and state files |
| `data/experiments/`, `experiments/` | Experiment calls and results; labels, prediction and procedure |
| `docs/` | Plan, network notes ([`docs/NETWORK.md`](docs/NETWORK.md)), build log, sign-off facts |
| `SOURCES.md`, `FRICTIONAL.md` | Sources and AI use; my Frictional log |

Left out on purpose: caches, `.venv`, credentials, `data/tmp/`, `data/scratch/`, and my real résumé (it stays in the gitignored `private/`).

### Sign-off

Candidate facts for "Not checked" and "Not claiming": [`docs/FACTS_FOR_SIGNOFF.md`](docs/FACTS_FOR_SIGNOFF.md).

- **Checked:**
  - I personally performed the five `CONTRACT.md §13` hand checks (`8249901`, `7543868`, `8175099`, `8127182`, `8234357`) against `evidence/handcheck/stripe-jobs-2026-10-29T22-41-31Z.json`, checking each exact verdict, failed gate, and skill-evidence path. These are my substantive manual checks.
  - Claude's generated test suite kills both wrong implementations required by `CONTRACT.md §14` (`wrong_versions/title_only.py` caught by 9 tests; `wrong_versions/substring_count.py` caught by 12 tests). Claude ran the automated test and static-check commands listed under **How**; the recorded results were `973 passed`, with `ruff` and `mypy --strict` passing.
  - The three live runs on three different calendar days (October 29–31, 2026 ET), one seeded replay pair (`data/seeded/runs/`), and all three experiment harnesses (Chapters 1–3) have saved raw evidence with SHA-256 digests. Claude ran `uv run jsa verify-evidence` and `uv run jsa audit-privacy data/`. The privacy audit reports **62 known persona-payload findings**; therefore I do not claim zero privacy findings or zero privacy leaks.
- **How:**
  - **I did:** the five §13 hand checks listed above, comparing the hand-check postings with the raw October 29 response and checking verdicts, failed gates, and evidence paths.
  - **Claude ran:** `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy --strict src tests`, `uv run jsa verify-evidence`, and `uv run jsa audit-privacy data/`; Claude also inspected generated `report.json`, `spread.json`, `metrics.json`, and `facts.json` against `CONTRACT.md`. These are Claude-run checks, not checks I independently executed.
  - **My check:** the five §13 hand-check cases are the explicitly student-performed test/check; the automated suite and audit results above are attributed to Claude.
  - **Sentence-initial `React` and `React Native` false positives (`CONTRACT.md §6.2`):** Because the `React` rule checks capitalization without grammar parsing, sentence-initial plain-English `"React"` or `"React Native"` counts as the `React` frontend skill; false-positive frequency across live boards was not measured beyond the October 29 snapshot.
  - **Senior roles without a title marker (`CONTRACT.md §2`, `§6.1`):** Stripe postings titled simply `Software Engineer` or `Full Stack Engineer` that demand `5+` or `8+` years of experience in `$.content` pass the deterministic title gate (as seen in `8197135`, `8197891`, `8198280`, `8206731`, and `8039548`).
  - **Explicit exclusion phrases (§6.3) and description rescue phrases (§6.4) on live Stripe data:** Zero postings on the October 29, 2026 Stripe board contained any of the 11 §6.3 exclusion phrases or 12 §6.4 location-rescue phrases, and `REST` never matched because the board wrote plural `"RESTful APIs"` (`docs/PLAN.md` data facts), so those branches were tested only on constructed fixtures.
  - **Outbound network destinations inside the external `claude` CLI binary (`CONTRACT.md §11`):** Python's `AllowListTransport` enforces `boards-api.greenhouse.io` for the agent's own HTTP requests, but cannot inspect or restrict the hosts contacted internally by the separate `claude` subprocess.
  - **Generalization beyond one board, one model, and three days:** All live and experimental data comes from a single Greenhouse board (`stripe`) between October 29 and October 31, 2026 using `claude-sonnet-5-5`.
- **Not claiming:**
  - I am not claiming that a `MATCH` or `RELEVANT` label means Kiran Joshi (or any candidate) is qualified for the job, will pass recruiting screens, or has verified visa sponsorship, nor that the 10-posting cells in Chapter 2 (`10/10 [0.72, 1.00]`) prove a statistically narrow error rate or generalize to unstratified board traffic.
- **Signed:** Shubham Bagwe — 2026-10-31

### Driver's seat

| Task | What Claude should do / did | What I should do / did | Why that part stays mine | Pointer |
|---|---|---|---|---|
| Persona and contract boundary | Flag assignment constraints, review drafts, and help validate rule mechanics; Claude declined to ghostwrite the student-owned contract/reflection. | Choose the fictional persona, define target roles and skill scope, and author the contract decisions. | The persona boundary, scope, and contract are the student's accountable design choices; delegating authorship would obscure who made them. | `FRICTIONAL.md` §1; `CONTRACT.md`; `053fda0` |
| Board selection and US-only rule | Evaluate board data under the supplied title rule; enumerate location strings and propose finite signal lists when asked. | Decide whether a board fits, reject Datadog, choose Stripe, and decide that ambiguous/non-US locations fail the US-only gate. | The target market and acceptable location policy are project requirements, not model preferences. | `FRICTIONAL.md` §§2–3; `053fda0`, `c1bd530`, `7aa5d0f` |
| Chapter 1 hand labels and prediction | Check evidence paths and summarize model-call reasons after the run. | Set the pre-run prediction and decide each of the five hand labels before model sampling. | Labels and predictions are the human reference used to evaluate the model; the model cannot independently author its own ground truth. | `experiments/sampling/hand_labels.json`; `f5fb431`, `7545af9`; `docs/experiments/SAMPLING.md` |
| Chapter 2 labels and prompt choice | Format JSON only if directed, review the prompt against the contract, and flag held-out examples before freeze. | Decide each dev/held-out label, seal labels before calls, choose the v2 candidate, and own the interpretation of results. | Ground truth, experimental design, and conclusions must remain the student's decisions to avoid circular evaluation and hidden leakage. | `experiments/prompt/labels/`; `data/experiments/prompt/SEAL.json`; `c2e5599`, `ed2c64c`, `6f5dc0a` |
| Chapter 3 action-surface decision | Run or analyze the compared surfaces and report cost, truncation, and operational risks. | Choose the least-autonomous surface and decide that Python retains fetch, hashing, and state updates. | The autonomy boundary determines the system's risk and accountability; evidence can inform it, but the design decision is mine. | `data/experiments/surfaces/ACTION_SURFACES.tables.md`; `docs/experiments/ACTION_SURFACES.md`; `8fea85b` |
| Final sign-off and student reflection | Run automated checks, verify artifacts, and flag inconsistencies or limitations. | Perform the §13 hand checks, decide what claims are justified, disclose limitations, and sign the submission. | The final claims and academic sign-off are mine even when tools execute checks or help inspect evidence. | This sign-off; `CONTRACT.md` §13; `docs/FACTS_FOR_SIGNOFF.md` |
