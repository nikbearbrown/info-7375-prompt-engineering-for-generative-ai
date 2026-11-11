# Sources

## Job-Search Agent 2 — the loop, the tools, and the diff

**Started from:** my own Job-Search Agent 1 (this repository, through commit `4b6c80f`). I did
not use the Reallocation Engine or Lectern code. The dated record for JS2 is
[`docs/js2/BUILD_LOG.md`](docs/js2/BUILD_LOG.md).

### External sources (JS2)

| Source | Used for |
|---|---|
| [JS2 assignment](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/assignments/assignment-js2-the-loop-the-tools-and-the-diff.md) and the course AI policy | The requirements |
| Greenhouse Job Board API: `boards-api.greenhouse.io/v1/boards/{stripe,figma,ramp}/jobs?content=true` | Job data. Raw responses are saved byte for byte under `data/watch/boards/*/live/runs/*/raw/` |
| Ashby posting API: `api.ashbyhq.com/posting-api/job-board/{ramp,linear,linearapp}` | Job data, and the deliberate 404 (`linearapp`) |
| `ramp.com/careers`, `stripe.com/jobs/search`, `figma.com/careers`, `linear.app/careers`, read 2026-11-09 outside the agent | Which job system each company links to, for `checks/expectations.toml` |
| Python libraries: as in JS1 (`httpx`, `pydantic`; `pytest`, `ruff`, `mypy`; `uv`). No new dependency | Toolchain |

No model call was made by the JS2 loop. I did not copy code from other projects or classmates.

### What I wrote (JS2)

- **`GATE.md` adoption (`f23fc78`):** Reviewed each budget (6 boards, 10 requests, 180 s), retry backoff, 429 refusal, empty-board failure status, and amendments A1–A4; adopted the specification unchanged as v1.0.
- **Career portal manual verification (`checks/expectations.toml`):** Inspected `ramp.com/careers`, `stripe.com/jobs/search`, `figma.com/careers`, and `linear.app/careers` directly in the browser; confirmed board systems and conservative posting floors.
- **Review packet decision (`docs/js2/review/REVIEW_PACKET.md`):** Executed the five verification commands, evaluated the diff for the A2 floor patch (`8259d8b`), and recorded the decision to **Revise** based on the hidden ordering dependency in `FlooredProvider`.
- **Test authoring (`tests/watch/test_floor.py`):** Wrote `test_pending_retry_from_an_old_raw_below_the_floor` to exercise a 3-run scenario catching mutation `m2` (flooring every parse call during pending retries).
- **`FRICTIONAL.md` (`f32ac92`):** Authored all six contemporaneous reflection entries for JS2 detailing real debugging episodes, verified numbers, and accepted/rejected Claude contributions.
- **`README.md`:** Authored the driver's-seat "Why that part stays mine" rationales and the formal JS2 sign-off block.

### What Claude contributed (JS2)

Claude Code (Opus 5.5):

- **Probing and board choice.** Claude probed Greenhouse, Ashby and Lever boards, chose the four
  real boards and the deliberate bad name, and found the two wrong-but-200 boards
  (`ashby/vercel` empty, `greenhouse/ramp` stale).
- **`GATE.md`.** Claude drafted v0.1 from my `CONTRACT.md` and committed it before any JS2 code (`f524c91`), and drafted amendments A1–A4. I reviewed the choices, accepted the amendments, and adopted the draft unchanged as v1.0  in commit `f23fc78`.
- **Code and tests.** Claude wrote `providers/ashby.py`, `policy.py`, `watch.py`,
  `watch_cli.py`, the UUID-ID and exit-code changes in `models.py`, the shared-helper renames in
  `providers/greenhouse.py`, the tests in `tests/watch/` and `tests/providers/test_ashby.py`, the
  wrong versions W1–W9 (`tests/wrong_versions/js2.py`) and their meta-test, and the independent
  check `checks/check_watch.py` with `checks/expectations.toml`.
- **The reviewed change.** Claude wrote the A2 test (`affcbdd`) before the patch. A separate,
  fresh Claude Code subagent wrote the patch from the request in
  `docs/js2/review/PROMPT.md`. The orchestrating Claude session read the diff and recorded the
  evidence in `docs/js2/review/REVIEW_PACKET.md`. The accept/revise/reject decision there is
  mine.
- **Runs.** Claude ran the live loop runs and the wrong-board runs recorded in
  `docs/js2/TRACE.md` and `docs/js2/FINISHED_WRONG.md`, and the boundary tests in
  `docs/js2/evidence/boundary-tests.txt`.
- **Docs.** Claude drafted `README.md`, `docs/js2/*.md` and the facts for the sign-off. The
  sign-off itself, the driver's-seat reasons and `FRICTIONAL.md` are mine.
- **Review.** A fresh Claude reviewer agent checked code quality and the assignment fit at the
  end; its report is `docs/js2/REVIEW_BY_AGENT.md`.
- **Second audit (2026-11-09, at my request).** Claude audited the whole repo and fixed four
  issues, each with a test seen failing first: an I/O error left no loop report, the board that
  stopped the loop was listed `NOT_ATTEMPTED`, the checker counted only jobs with an ID, and
  Ctrl-D at the reset prompt crashed. Claude drafted GATE A4 for them (`c001ae0`).
- **Transcripts.** Claude untracked and git-ignored the three JS1 session transcripts, per the
  JS1 TA note (`fcae71e`).
- **The revision (2026-11-10, after my decision to revise).** Claude wrote the order test
  (`tests/watch/test_floor_live_body.py`) before the change, then made the floor apply to the
  live response by its bytes, ran four mutations (all caught), ran the live wrong-board loop
  `2026-11-11T01-14-05Z`, and recorded the facts in review packet §8 (`707ecea`). I reviewed it
  and accepted it (`d9d63a4`).
- **Third live run (2026-11-10).** Claude ran the main-plan loop `2026-11-11T01-26-35Z` and saved
  the independent check (`95d0961`).
- **Commits.** Claude committed and pushed my edits when I asked, and updated the test counts in
  the docs (for example `595a87e`).

## Job-Search Agent 1 — the contract and the watch

What this submission used, what I wrote, and what Claude contributed. The day-by-day record, with commit hashes, is [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md).

### External sources

| Source | Used for |
|---|---|
| [JS1 assignment](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/assignments/assignment-js1-the-contract-and-the-watch.md), course AI policy, Frictional and GitHub-submission guides | I used these to identify the assignment requirements. |
| Stripe's public Greenhouse board, `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | The agent fetched this job data. Saved responses are in `evidence/` and `data/`. |
| Claude Code docs (`https://code.claude.com/docs/en/`: network-config, cli-reference, permissions, headless, data-usage, env-vars, legal-and-compliance), read 2026-10-29 | I consulted these for CLI and network behavior; Claude-assisted analysis used them to document judge flags, permissions, and hosts: [`docs/claude-code-network-facts.md`](docs/claude-code-network-facts.md). |
| A local `career-ops` board list (`portals.yml`) | I used this as a source of candidate boards when choosing one. |
| Python libraries: `httpx`, `pydantic` (runtime); `pytest`, `ruff`, `mypy`, `hatchling`; `uv` | I used these as the project toolchain (see README). |
| Model: `claude-sonnet-5-5` via the `claude` CLI (Claude Code 2.1.314), on my subscription | Claude generated every recorded model judgment and experiment call. |

I did not copy code from other projects.

### What I wrote

- **`CONTRACT.md` (commits `053fda0`, `c1bd530`, `7aa5d0f`):** I chose the target role families, level targets, skill categories, the switch to Stripe on Greenhouse, and the hard US-only location rule after inspecting the initial hand-check candidates (including evaluating `8249901`, `7543868`, `8175099`, and `8234357`). I edited the contract text across drafts.
- **Chapter 1 (`experiments/sampling/hand_labels.json`, `data/experiments/sampling/SAMPLING.tables.md`, `docs/experiments/SAMPLING.md`):** I confirmed the five `CONTRACT.md` §13 hand labels (`f5fb431`), supplied the pre-run prediction before `jsa exp sampling run` executed, and wrote the `## Conclusion` section, updating it after Claude Code verified the 20-call reasons on `8234357` and `8127182`.
- **Chapter 2 (`experiments/prompt/labels/{dev,heldout}.labels.json`, `prompts/CHANGELOG.md`, `prompts/judge.v2.md`, `data/experiments/prompt/PROMPT_EXPERIMENT.tables.md`, `docs/experiments/PROMPT_EXPERIMENT.md`):** I decided each of the 20 dev and held-out hand labels and sealed them (`14e51f9`). I chose Candidate 1 (the `label_definition` replacement) after seeing the `7/10` v1 dev run (`c2e5599`). I directed Claude Code to replace held-out-derived examples in the v2 draft with the `CONTRACT.md` §6 lists before freeze, and I wrote the `## Rule-vs-hand decisions` and `## Conclusion` sections (`6f5dc0a`).
- **Chapter 3 (`data/experiments/surfaces/ACTION_SURFACES.tables.md`, `docs/experiments/ACTION_SURFACES.md`):** I wrote the three `What could go wrong` risk cells and the `## Least autonomy that suffices` defense selecting Surface (a) (`--tools ""`).
- **`FRICTIONAL.md`, README.md sign-off and driver's-seat table, and SOURCES.md student sections:** I wrote these student-owned sections. I used `docs/BUILD_LOG.md` and `docs/FACTS_FOR_SIGNOFF.md` to trace timestamps, commit hashes, and run counts; Claude assisted with fact-checking against repository artifacts.

### What Claude contributed

Claude Code (Opus 5.5 orchestrating; coding agents in separate worktrees) contributed:

- **Contract support, not the contract.** Claude declined to ghostwrite `CONTRACT.md`. Claude reviewed my drafts, verified §13 hand-check claims against the raw file (finding one wrong path), and built the §6.4 US and non-US location signal lists from all 294 distinct `location.name` values at my request. Claude also computed skill lists for the hand-check postings and found `8127182` as the fewer-than-two-skills hand-check case.
- **Board choice.** Claude first recommended Datadog, which did not satisfy my title rule (0 of 397 postings passed). Claude then probed boards and suggested Stripe; I chose Stripe.
- **Persona.** Claude helped me draft the fictional `persona/kiran-joshi.resume.example.json` (`@example.com`, 555 phone), modeled only on my target roles and skill areas.
- **Evidence capture.** Claude saved the hand-check raw response (`evidence/handcheck/`), byte for byte with its SHA-256.
- **Plan.** A Claude planning agent wrote [`docs/PLAN.md`](docs/PLAN.md); Claude asked me to review it and added amendments R1–R10.
- **Code and tests.** Claude coding agents wrote the code in `src/` and tests in `tests/`, test-first. Claude also wrote the two wrong implementations (`tests/wrong_versions/`) and the meta-test that proves the suite catches them.
- **Reviews.** Fresh Claude agents performed a Google-style code review and a ponytail audit; Claude implemented the resulting fixes (see `BUILD_LOG.md`, 2026-10-30).
- **Prompt v1.** Claude drafted `prompts/judge.v1.md`; Claude also prepared the pre-registered v2 candidates in `prompts/CHANGELOG.md`. I reviewed the prompt before the v1 dev run.
- **Prompt v2 lists.** At my direction, Claude copied the lists from `CONTRACT.md` §6 into `label_definition` in `prompts/judge.v2.md`, replacing examples in my draft that came from held-out postings.
- **Generated docs.** Code generated the tables in the three experiment docs. Claude drafted `README.md` except for the sign-off and driver's-seat sections, and drafted `docs/NETWORK.md`, `TRACEABILITY.md`, `ARCHITECTURE.md`, `RUNS.md`, `FACTS_FOR_SIGNOFF.md`, and `BUILD_LOG.md`. I reviewed and edited the student-owned material.

### AI assistance in my own parts

- **Contract review and §6.4 / §13 data extraction (`CONTRACT.md`, Oct 29):** As recorded in `docs/BUILD_LOG.md` (18:10–19:15 ET), Claude reviewed my contract drafts, converted my US-only location requirement into finite US and non-US signal lists across the 294 distinct `location.name` strings in the October 29 Stripe response (§6.4), computed skill path lists for the §13 hand-check postings, and identified `8127182` as the fewer-than-two-skills hand-check case. I made the policy decisions and edited the contract.
- **Chapter 2 hand-label JSON formatting (`dev.labels.json`, `heldout.labels.json`):** I decided each of the 20 labels by applying the §6 criteria. Claude did **not** decide or assign the labels; Claude only formatted my decisions as JSON and helped format the associated notes (`14e51f9`). Before freezing `judge.v2.md` (`c2e5599`), Claude checked the v2 text against `CONTRACT.md` §6, flagged that several examples came from held-out postings, and replaced those examples with the full contract lists at my direction so the held-out set stayed clean. The earlier v2 draft's held-out-example exposure remains an experiment limitation and is disclosed in `docs/experiments/PROMPT_EXPERIMENT.md`.
- **Reference logs and fact-checking against repo artifacts (`BUILD_LOG.md`, `FACTS_FOR_SIGNOFF.md`, Chapters 1–3, `README.md`, `FRICTIONAL.md`):** Claude maintained the dated factual timeline in `docs/BUILD_LOG.md` and candidate sign-off items in `docs/FACTS_FOR_SIGNOFF.md`. Claude verified cited counts, costs, commit hashes, and run reasons in my sections against committed repository files before each commit (for example, the `3/1` split reason on `8234357` in Chapter 1 and test/run counts in `README.md` and `FRICTIONAL.md`).
