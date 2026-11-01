# Job-Search Agent 1 — The Contract and the Watch

**Student:** Shubham Bagwe · **Course:** INFO 7375 — Prompt Engineering for Generative AI (Northeastern University) · **Instructor:** Nik Bear Brown · **Assignment:** JS1, due 2026-10-31

A discovery-only agent. It watches one public job board (Stripe on Greenhouse), remembers the posting IDs it has seen, and reports only postings that are new since the last run. Each new posting gets two separate verdicts:
- **Record:** a deterministic rule anyone can recompute (`CONTRACT.md` §6).
- **Judgment:** Claude's opinion under a prompt contract, validated against a fixed schema and labelled as an opinion (§8).

The résumé is a **fictional persona**, Kiran Joshi ([`persona/kiran-joshi.resume.example.json`](persona/kiran-joshi.resume.example.json)). The agent never applies, contacts anyone or logs in.

**Start here:** [`CONTRACT.md`](CONTRACT.md) was written and committed first (`053fda0`, before any code).

## Language and toolchain

| | |
|---|---|
| Language | Python ≥ 3.12 (developed and run on 3.14.5) |
| Package manager | [`uv`](https://docs.astral.sh/uv/) (0.11.0); dependencies pinned in `uv.lock` |
| Runtime libraries | `httpx`, `pydantic` |
| Dev tools | `pytest`, `ruff`, `mypy --strict` |
| Model | `claude-sonnet-5-5` through the `claude` CLI (Claude Code 2.1.314 for every recorded call), signed in with a Claude subscription. No API key is used or needed |
| Platform | macOS (darwin); nothing is macOS-specific |

## Commands (from a fresh clone)

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

## What ran

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

## The three chapter artifacts

| Chapter | Report | Headline |
|---|---|---|
| 1. Sampling | [`docs/experiments/SAMPLING.md`](docs/experiments/SAMPLING.md) | 5 postings × 4 fresh calls: 20/20 valid; 15/20 agree with my labels; 8249901 is unanimous and wrong |
| 2. Prompt experiment | [`docs/experiments/PROMPT_EXPERIMENT.md`](docs/experiments/PROMPT_EXPERIMENT.md) | v1 → v2 (only `label_definition` changed): dev 7/10 → 10/10, held-out 6/10 → 10/10 |
| 3. Action surfaces | [`docs/experiments/ACTION_SURFACES.md`](docs/experiments/ACTION_SURFACES.md) | Chosen: surface (a), stdin with no tools |

## Repository map

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

## Sign-off

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

## Driver's seat

| Task | What Claude should do / did | What I should do / did | Why that part stays mine | Pointer |
|---|---|---|---|---|
| Persona and contract boundary | Flag assignment constraints, review drafts, and help validate rule mechanics; Claude declined to ghostwrite the student-owned contract/reflection. | Choose the fictional persona, define target roles and skill scope, and author the contract decisions. | The persona boundary, scope, and contract are the student's accountable design choices; delegating authorship would obscure who made them. | `FRICTIONAL.md` §1; `CONTRACT.md`; `053fda0` |
| Board selection and US-only rule | Evaluate board data under the supplied title rule; enumerate location strings and propose finite signal lists when asked. | Decide whether a board fits, reject Datadog, choose Stripe, and decide that ambiguous/non-US locations fail the US-only gate. | The target market and acceptable location policy are project requirements, not model preferences. | `FRICTIONAL.md` §§2–3; `053fda0`, `c1bd530`, `7aa5d0f` |
| Chapter 1 hand labels and prediction | Check evidence paths and summarize model-call reasons after the run. | Set the pre-run prediction and decide each of the five hand labels before model sampling. | Labels and predictions are the human reference used to evaluate the model; the model cannot independently author its own ground truth. | `experiments/sampling/hand_labels.json`; `f5fb431`, `7545af9`; `docs/experiments/SAMPLING.md` |
| Chapter 2 labels and prompt choice | Format JSON only if directed, review the prompt against the contract, and flag held-out examples before freeze. | Decide each dev/held-out label, seal labels before calls, choose the v2 candidate, and own the interpretation of results. | Ground truth, experimental design, and conclusions must remain the student's decisions to avoid circular evaluation and hidden leakage. | `experiments/prompt/labels/`; `data/experiments/prompt/SEAL.json`; `c2e5599`, `ed2c64c`, `6f5dc0a` |
| Chapter 3 action-surface decision | Run or analyze the compared surfaces and report cost, truncation, and operational risks. | Choose the least-autonomous surface and decide that Python retains fetch, hashing, and state updates. | The autonomy boundary determines the system's risk and accountability; evidence can inform it, but the design decision is mine. | `data/experiments/surfaces/ACTION_SURFACES.tables.md`; `docs/experiments/ACTION_SURFACES.md`; `8fea85b` |
| Final sign-off and student reflection | Run automated checks, verify artifacts, and flag inconsistencies or limitations. | Perform the §13 hand checks, decide what claims are justified, disclose limitations, and sign the submission. | The final claims and academic sign-off are mine even when tools execute checks or help inspect evidence. | This sign-off; `CONTRACT.md` §13; `docs/FACTS_FOR_SIGNOFF.md` |
