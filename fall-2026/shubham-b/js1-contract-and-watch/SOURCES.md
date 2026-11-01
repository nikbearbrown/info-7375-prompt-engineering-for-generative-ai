# Sources

What this submission used, what I wrote, and what Claude contributed. The day-by-day record, with commit hashes, is [`docs/BUILD_LOG.md`](docs/BUILD_LOG.md).

## External sources

| Source | Used for |
|---|---|
| [JS1 assignment](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/assignments/assignment-js1-the-contract-and-the-watch.md), course AI policy, Frictional and GitHub-submission guides | I used these to identify the assignment requirements. |
| Stripe's public Greenhouse board, `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | The agent fetched this job data. Saved responses are in `evidence/` and `data/`. |
| Claude Code docs (`https://code.claude.com/docs/en/`: network-config, cli-reference, permissions, headless, data-usage, env-vars, legal-and-compliance), read 2026-10-29 | I consulted these for CLI and network behavior; Claude-assisted analysis used them to document judge flags, permissions, and hosts: [`docs/claude-code-network-facts.md`](docs/claude-code-network-facts.md). |
| A local `career-ops` board list (`portals.yml`) | I used this as a source of candidate boards when choosing one. |
| Python libraries: `httpx`, `pydantic` (runtime); `pytest`, `ruff`, `mypy`, `hatchling`; `uv` | I used these as the project toolchain (see README). |
| Model: `claude-sonnet-5-5` via the `claude` CLI (Claude Code 2.1.314), on my subscription | Claude generated every recorded model judgment and experiment call. |

I did not copy code from other projects.

## What I wrote

- **`CONTRACT.md` (commits `053fda0`, `c1bd530`, `7aa5d0f`):** I chose the target role families, level targets, skill categories, the switch to Stripe on Greenhouse, and the hard US-only location rule after inspecting the initial hand-check candidates (including evaluating `8249901`, `7543868`, `8175099`, and `8234357`). I edited the contract text across drafts.
- **Chapter 1 (`experiments/sampling/hand_labels.json`, `data/experiments/sampling/SAMPLING.tables.md`, `docs/experiments/SAMPLING.md`):** I confirmed the five `CONTRACT.md` §13 hand labels (`f5fb431`), supplied the pre-run prediction before `jsa exp sampling run` executed, and wrote the `## Conclusion` section, updating it after Claude Code verified the 20-call reasons on `8234357` and `8127182`.
- **Chapter 2 (`experiments/prompt/labels/{dev,heldout}.labels.json`, `prompts/CHANGELOG.md`, `prompts/judge.v2.md`, `data/experiments/prompt/PROMPT_EXPERIMENT.tables.md`, `docs/experiments/PROMPT_EXPERIMENT.md`):** I decided each of the 20 dev and held-out hand labels and sealed them (`14e51f9`). I chose Candidate 1 (the `label_definition` replacement) after seeing the `7/10` v1 dev run (`c2e5599`). I directed Claude Code to replace held-out-derived examples in the v2 draft with the `CONTRACT.md` §6 lists before freeze, and I wrote the `## Rule-vs-hand decisions` and `## Conclusion` sections (`6f5dc0a`).
- **Chapter 3 (`data/experiments/surfaces/ACTION_SURFACES.tables.md`, `docs/experiments/ACTION_SURFACES.md`):** I wrote the three `What could go wrong` risk cells and the `## Least autonomy that suffices` defense selecting Surface (a) (`--tools ""`).
- **`FRICTIONAL.md`, README.md sign-off and driver's-seat table, and SOURCES.md student sections:** I wrote these student-owned sections. I used `docs/BUILD_LOG.md` and `docs/FACTS_FOR_SIGNOFF.md` to trace timestamps, commit hashes, and run counts; Claude assisted with fact-checking against repository artifacts.

## What Claude contributed

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

## AI assistance in my own parts

- **Contract review and §6.4 / §13 data extraction (`CONTRACT.md`, Oct 29):** As recorded in `docs/BUILD_LOG.md` (18:10–19:15 ET), Claude reviewed my contract drafts, converted my US-only location requirement into finite US and non-US signal lists across the 294 distinct `location.name` strings in the October 29 Stripe response (§6.4), computed skill path lists for the §13 hand-check postings, and identified `8127182` as the fewer-than-two-skills hand-check case. I made the policy decisions and edited the contract.
- **Chapter 2 hand-label JSON formatting (`dev.labels.json`, `heldout.labels.json`):** I decided each of the 20 labels by applying the §6 criteria. Claude did **not** decide or assign the labels; Claude only formatted my decisions as JSON and helped format the associated notes (`14e51f9`). Before freezing `judge.v2.md` (`c2e5599`), Claude checked the v2 text against `CONTRACT.md` §6, flagged that several examples came from held-out postings, and replaced those examples with the full contract lists at my direction so the held-out set stayed clean. The earlier v2 draft's held-out-example exposure remains an experiment limitation and is disclosed in `docs/experiments/PROMPT_EXPERIMENT.md`.
- **Reference logs and fact-checking against repo artifacts (`BUILD_LOG.md`, `FACTS_FOR_SIGNOFF.md`, Chapters 1–3, `README.md`, `FRICTIONAL.md`):** Claude maintained the dated factual timeline in `docs/BUILD_LOG.md` and candidate sign-off items in `docs/FACTS_FOR_SIGNOFF.md`. Claude verified cited counts, costs, commit hashes, and run reasons in my sections against committed repository files before each commit (for example, the `3/1` split reason on `8234357` in Chapter 1 and test/run counts in `README.md` and `FRICTIONAL.md`).
