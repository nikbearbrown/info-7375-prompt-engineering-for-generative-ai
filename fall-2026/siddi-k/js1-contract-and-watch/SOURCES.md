# SOURCES

## What was used

| Source | How |
|---|---|
| Greenhouse public Job Board API, `boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true` | The only host the agent fetches. Databricks under contract v1, Stripe under v2. Raw responses saved in `raw/` and `evidence/`. |
| Python 3.13 standard library | All code. No third-party packages. |
| Claude Code CLI (`claude -p`), versions 2.1.304 / 2.1.309, model pinned to `claude-sonnet-5-5` | The agent's Claude judge, the sampling report, the prompt experiment and the action-surface runs. Flags come from `claude --help` (see `config/claude_cmd.txt`). |
| My earlier Reallocation Engine work (`fetch_pay_ranges.py`, Oct 21) | The *idea* of a host allow-list checked in code. No code copied. |

**Not used:**
- The instructor's `greenhouse-watch` skill and demo folder.
- Other students' JS1 folders. They exist on `origin/main` and were deliberately left unopened.

## What Siddi wrote or decided

- **CONTRACT.md v1, all of it:** In, the persona validator, State, Out, the line validator, the Claude judgment spec, Refuses, the rule, the hand-label selection, all 36 wrong versions, the dated failure sentence, the fictional persona Jordan Lee (Appendix A), the Appendix B excerpt and the Appendix C v1 strings. Pasted in chat on 2026-10-31 before any code existed, and transcribed verbatim by Claude (commit `be3b6c8`).
- **Decisions:**
  - Board, first Databricks, then Stripe when the base-rate check failed.
  - Split location on the whole word "or".
  - Drop "about databricks" from the cut headings.
  - Pin `claude-sonnet-5-5`.
  - Let Claude draft the vocab extension, `judge_v1`, the v2 note and `judge_v2`; approve each before commit.
  - Move the Databricks baseline into evidence.
- **Still to come from Siddi:** `LABELING.md`, the 20 hand labels, `FRICTIONAL.md`, and the sign-off in the README.

## What Claude contributed

- **The agent code:** `agent/`, written against the contract.
- **Testing:** the test harness, the stub `claude`, the 36 wrong-version tests and the mutation check (`tests/`).
- **Experiment tooling:** `experiments/runner.py`, `tools/make_reports.py` and `tools/action_surface.py`.
- **Drafts Siddi approved:**
  - the 14 added vocab entries
  - `prompts/judge_v1.md`
  - the one sentence that makes `judge_v2.md`
  - `config/claude_cmd.txt`
  - the dated "Contract v2" section and the v2 Appendix C strings
- **Measurements:** the Appendix C checks against real boards, and the 35-board base-rate scan (`tools/base_rate_scan.py`, output in `evidence/base-rate-databricks/README.md`).
- **Report text:** the prose in README, SAMPLING, PROMPT-EXPERIMENT and ACTION-SURFACE, and this file. The numbers in those files come from saved outputs via the scripts, not from Claude's prose.
- **Claude's mistakes, found and fixed:**
  - When transcribing the contract, Claude added subheadings and reformatted a lead-in in Siddi's text; it removed them before the first commit.
  - The first mutation run missed wv09 because of a weak fixture; fixed in `7494886`.
