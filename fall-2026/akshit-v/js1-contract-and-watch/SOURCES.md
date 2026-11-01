# SOURCES

## What I used
- **Greenhouse Job Board API** (public, no login): `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true`. Read-only; one host on the allow-list.
- **Python 3.12.10**, standard library only. Tests use `unittest`.
- **Claude Code CLI 2.1.316** (`npm install -g @anthropic-ai/claude-code`), logged in with my Claude account. The judge model is `claude-opus-5-5`.
- **Claude Code in VS Code** (also `claude-opus-5-5`) as my coding assistant for this assignment, on 2026-10-31.

## What I wrote or decided
- Every decision in `CONTRACT.md`: board, persona, résumé fields, output, refusals, the rule, the choice of wrong versions, and the failure conditions. Claude asked one question per section; where I adopted one of its suggestions, the contract says so on that line. The contract was committed alone, before any code (commit `5ca21ed`, 2026-10-31 19:14 ET).
- Every hand label in `experiments/labels.csv` and `experiments/sampling_hand_labels.csv`.
- Review of `experiments/LABELING_RULE.md`, and the choices marked [confirm] in it.
- `FRICTIONAL.md`, the sign-off and the driver's seat table in `README.md`.
- My views and corrections, given in chat and inserted in my words: the hand-check result, "I stand by my labels", "My prediction was wrong on Data Platform Engineer", and my reflections in FRICTIONAL.md. I did not edit Claude's drafts directly.
- The hand check of the rule on 5 postings.

## What Claude contributed
- **Code:** everything in `agent/`, `scripts/`, `experiments/*.py`, and `tests/`, written against my contract. Claude ran the tests during the session on 2026-10-31 (32 tests, OK). I did not run them separately.
- **The prompt contract** `prompts/judge_baseline.md` (wording by Claude; its output format follows my contract's Out section).
- **The revision prompt** `prompts/judge_revision.md`. I chose the one change from three options Claude offered: replace the definition of "relevant" with my labeling rule's criteria. Claude wrote the wording.
- **First drafts** of the sampling-report and prompt-experiment write-ups in `README.md`, built from the result files, plus the README sign-off wording, the driver's-seat "why" column, and the Agent 2 suggestions in FRICTIONAL.md.
- **The fictional persona résumé** `data/resume_jack_spencer.json`, built from my persona description (fictional employers and school).
- **Methods:** the seeded-baseline method (remove the 10 highest-id postings), the stratified draw for the 20 labels, and the choice of the 5 sampling postings. I accepted these.
- **The labeling rule** `experiments/LABELING_RULE.md`, drafted at my request before any labeling. I reviewed it.
- **First drafts** of `README.md` (except the sign-off and driver's seat), `ACTION_SURFACE.md`, `FRICTIONAL.md` (the factual log), and this file.
- **Suggestions I accepted** are marked in `CONTRACT.md`: the two verdict values, the Claude label format, Jack's titles and skills, whole-word matching, and W1 and W2 as the wrong versions.

## What Claude did not contribute
- Hand labels and the sign-off.
- Any posting, result or metric. Every posting is real and from the saved responses. The test postings are marked CONSTRUCTED. The seeded file is marked SEEDED.
