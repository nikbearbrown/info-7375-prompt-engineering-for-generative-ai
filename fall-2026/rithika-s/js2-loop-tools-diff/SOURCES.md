# SOURCES — JS2 Loop, Tools, and Diff

Rithika Sankar Rajeswari, INFO 7375, Fall 2026.

## Starting code

- My own JS1 submission: `fall-2026/rithika-s/js1-contract-and-watch`, commit
  `aa7c870`. Copied unchanged into this folder in `b9ede94` (42 tests passed).

## Data sources

- Greenhouse public job board API (`boards-api.greenhouse.io`): boards
  `scaleai` and `databricks`, plus a deliberately missing board
  `rithika-js2-no-such-board` used to test the 404 path.
- Ashby public job board API (`api.ashbyhq.com`): board `openai`.
- Exact URLs are in `config/boards.json`. Only unauthenticated GET requests
  were made. Raw responses are saved in `out/raw/`.
- `data/seeded_demo/day2/scaleai.json` is SEEDED: written by hand, not a real
  response (see `data/seeded_demo/README.md`).

## Course materials

- INFO 7375 course repository and assignment guidance for JS2:
  https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
- Course book: *Prompt Engineering for Generative AI*, Nik Bear Brown.

## AI assistance

- **Claude Code (Northeastern access):** wrote `agent/loop.py`,
  `agent/policy.py`, `agent/adapters.py`, `agent/transport.py`,
  `checks/independent_check.py`, the JS2 tests, `tests/mutants.py` (W1–W11),
  the `--boards` option, and the `empty_after_nonempty` patch. Its build
  summary is saved verbatim in `evidence/2026-11-10_claude_code_build_summary.md`.
- **Claude (claude.ai chat):** proposed wording for GATE.md sections, the
  boundary-test table, the review test, the review packet, README, this file.
- **Me:** every decision in GATE.md (including withdrawing the known limit),
  the boundary-test predictions, running every test suite, the live run and
  the SEEDED demo, reading the diff, approving the one out-of-scope test
  change, the accept decision, and reviewing and editing every document.

## Collaborators

- None. Classmates' JS2 folders arrived with `git pull`; I did not open them.
