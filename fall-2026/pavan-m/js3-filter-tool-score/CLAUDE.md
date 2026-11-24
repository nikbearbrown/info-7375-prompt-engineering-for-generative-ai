# CLAUDE.md — Job-Search Agent 3 (Pavan Majji, INFO7375)

## What this is
Assignment brief: ASSIGNMENT.md. This builds on my JS2 agent (../js2-loop-tools-diff),
copied here unchanged: a bounded loop over Glean (Greenhouse), Palantir (Lever) and
OpenAI (Ashby) plus one deliberately bad board, with a permission policy in agent/policy.py.
Fictional persona: data/persona_alex.json (Alex Morgan).

## Hard rules
- Never modify ../js1-contract-and-watch/ or ../js2-loop-tools-diff/ (submitted).
- Never read other students' folders in fall-2026/.
- Do not write or edit FILTER.md. I write it; you may review it.
- Do not write code until I say FILTER.md is committed.
- I write the test asserts before implementation. Never modify files in tests/.
  If a test looks wrong, stop and tell me.
- No network requests unless I ask, and only to hosts in agent/policy.py.
- Only write inside this folder. Never git commit or push; I do that.
- No real résumé, ever.
- Label anything seeded, simulated or constructed.

## How I work
- Python venv in .venv; tests: python -m pytest -v
- When you make a choice my instructions didn't cover, list it at the end of your reply.
- Tell me the exact commands to verify your work myself.
