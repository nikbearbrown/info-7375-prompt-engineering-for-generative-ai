# Sources
- Greenhouse public Job Board API: `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` (public, no login). Raw responses saved in `runs/` as evidence.
- My own earlier code: `fetch-board.py` from my Reallocation Engine mode (anishagaikar0420/the-reallocation-engine, branch mode/anisha-bi-analyst-triage) — the HTML-to-text and slug check were reused.
- Claude (Anthropic), 2026-10-31: drafted CONTRACT.md wording from my decisions, wrote `agent.py`, `tests/test_agent.py`, both prompts, ACTION-SURFACES.md and the README/sign-off templates. I chose the board, the rule and the persona defaults, ran the tests and the live runs on my Mac, and wrote the 20 hand labels. Claude drafted the report conclusions, this file and FRICTIONAL.md from the real results; I reviewed them.
- Claude Code (`claude -p`): the JUDGMENT calls. My own Claude Code hit its spend limit on 2026-10-31, so the judge calls (60 at ~6:00 pm, rerun as 60 more with raw replies saved at ~6:17 pm, plus run 2's 3) were run by Claude in its workspace on my raw response and my labels (see FRICTIONAL.md).
- The action-surface runs (ways 1 and 2, `reports/action-surfaces/`): made with `claude -p` in Claude's workspace on 2026-10-31 at ~6:12 pm.
- `label.py`: helper written by Claude; the 20 labels it recorded are mine.
- Persona "Nadia Okafor": fictional, written for this assignment.
