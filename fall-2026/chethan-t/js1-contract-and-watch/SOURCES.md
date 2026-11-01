# Sources — Job-Search Agent 1

Draft, 2026-10-31.

## What I used
- Greenhouse public Job Board API, `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`
  (fetched once, 2026-10-31 17:51 EDT; saved as `raw/klaviyo_20261031T175121.json`)
- Python 3.13.9 standard library; pytest 8.4.2
- Claude Code CLI 2.1.316 (`claude -p --output-format json`), my existing login
- claude.ai chat (contract questions, persona draft, way 1 of the action surface)
- INFO 7375 assignment brief: ____ (add link)

## What I wrote or decided
- Contract decisions in `CONTRACT.md` (`046b749`, v2.1 `5893443`)
- Labeling rule and all hand labels (`experiment/LABELING_RULE.md`; `d91854d`, `0531149`)
- The rebalance option and the one prompt change (no code fences)
- Conclusions in `experiment/SAMPLING_REPORT.md` and `experiment/PROMPT_EXPERIMENT.md` (`4f62e57`)
- Final review and sign-off of this README

## What Claude contributed
- Contract wording from my answers (claude.ai; see `FRICTIONAL.md`)
- Persona draft (Arjun Mehta; claude.ai; I accepted it, see `FRICTIONAL.md`)
- Agent code (`agent/`), tests (`tests/`), experiment scripts (`experiment/*.py`)
- Drafts of reports and docs: README, `seeded_run/SEEDED.md`,
  `experiment/ACTION_SURFACE.md`, this file, `FRICTIONAL.md` entries after 2026-10-31 17:18
- Drafts of conclusions, which I edited
- The verdicts labeled `judgment` (Claude's opinion, not fact)
