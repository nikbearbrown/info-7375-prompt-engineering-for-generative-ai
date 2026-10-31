# Sources

_Atharva: check every line of this file; it must be true as written._

## What I used
- **Greenhouse Job Board API.** The public, no-login endpoint `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`, fetched on 2026-10-31. Every response used is saved in this folder:
  - Abacus Insights, for the watch: `runs/`
  - 19 employer boards, for the label pool: `experiments/label_pool/raw/`
  - Point72, for action surface 3: `experiments/action_surface/3_agent_fetch/`
- **My own spreadsheet** `h1b_entry_level_data_employers.xlsx`, used to choose which employers' boards to read. It stays on my machine and isn't submitted.
- **The Reallocation Engine's example personas** (`search/examples/`). I looked only at their target roles. None was a Data Analyst, so the persona here is invented.
- **Course material:** the JS1 brief (Canvas) and the Chapter 1–3 specifications in `chapters-spec.md`.
- **Claude Code** (desktop app; this session's model was Claude Opus 5.5). It was used to interview me for the contract, write the code, and provide every Claude verdict through subagents.
- **AI chat tool.** It helped draft the rule, wrong versions, and failure sentence, filled the 20-label table, ran the requested test suite, recomputed the experiment scores, and drafted the final reports and edits.

## What I wrote or decided
- I requested and reviewed the rule draft, edited the title list, and chose the four analyst titles in `CONTRACT.md`.
- Decisions:
  - the persona's titles, seniority, location, and sponsorship need
  - the board (Abacus Insights)
  - verdict values, including `needs_human`
  - justification requirements
  - how `needs_human` is scored
  - the label pool
  - removing the engineering titles
  - leaving out "Analytics Analyst"
  - the one v2 change
  - choosing subagents over logging in to the CLI
- I reviewed the table of 20 labels and deciding checks in chat and replied "looks good."

## What Claude contributed
- **Contract interview:** the questions, the option wording I picked from for In, Out, and Refuses, the copy of the AI-assisted rule draft, and the deletion of two titles at my request.
- **Code and tests:** all of it (`watch.py`, `rule.py`, `judge.py`, `persona.py`, `seed.py`, `experiments/*.py`, `tests/`).
- **Persona:** the fictional `persona/resume.json` (Riley Navarro).
- **Prompts:** the v1 prompt contract, and the v2 sentence, which I chose as the one change.
- **Mechanical readings** of my location, sponsorship, and experience checks, which I accepted.
- **Board work:** probing Greenhouse for H-1B-list employers and picking the label pool by title tier.
- **Every Claude verdict**, from fresh subagents.
- **Drafts:** the initial README, `ACTION_SURFACE.md`, sign-off, and earlier FRICTIONAL entries, written from the build session for me to review.
