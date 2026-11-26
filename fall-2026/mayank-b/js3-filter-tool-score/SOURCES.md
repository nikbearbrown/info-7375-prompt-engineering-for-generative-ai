# SOURCES.md: what I started from, and who did what

## Started from
- **My JS2** (`../js2-loop-tools-diff`): the bounded loop, allow-list, permission policy, raw responses + SHA-256. Copied into `src/jsa/`; the only changes are the `content=true` flag and the posting-text field (`boards.py`, `loop.py`), and the user-agent string (`net.py`).
- **My JS1** (`../js1-contract-and-watch`): the title and location rule, inherited as filter v0.1, and the fictional persona Priya Nair (from the Reallocation Engine's examples).
- **The instructor's Lectern** (`fall-2026/nik-bear-brown/lectern/`): the model for FILTER.md (a filter as a document, keep rule with a threshold T = 3, per-company ignore list, every added/cut word recorded after measuring).
- **Chapter 8's teaching server**, `lessons/08-mcp-from-scratch/code/main.py` at commit `a8629ce1c437abee3a2c4f025bd8be3183b0f0af` (copied to `other-server/main.py` for the evaluation; not modified).

## Data
- One fetch on 2026-11-25 (Eastern; run id `2026-11-26T02-20-27Z-content`, UTC): Greenhouse `anthropic` and `hubspotjobs` with `?content=true`, Ashby `notion`, and the deliberate bad board. Public endpoints, GET only, two allow-listed hosts.

## Claude
- **Claude Code (Claude Opus 5.5, 2026-11-23 to 11-25)** wrote, at my request: the question sheet and build plan (`notes/`), the FILTER.md draft from my answers, all code and tests in `src/jsa3/`, `tests/`, `scripts/`, the tool server and its scripted client, the transcripts' runs, the drafts of `SCORE.md`, `EVAL-OWN-SERVER.md`, `EVAL-OTHER-SERVER.md`, `SIGNOFF.md` (structure only), this file, and the README. A Claude Code subagent built the tool server, its tests and the two evaluation drafts.
- **Claude Haiku 5.5 (`claude-haiku-5-5`)** wrote the 10 shortlist justifications and 3 re-runs on 2026-11-25 through the Claude Code CLI (`claude -p`, no tools); responses saved verbatim in `runs/2026-11-26T02-22-17Z-shortlist/responses/`.
- **Options for my writing:** at my request, Claude Code drafted two or three options for each line I write (the FILTER.md 1.4 reasons, both trust decisions, SIGNOFF.md, FRICTIONAL.md). I chose one for each and edited it; the choice and the edits are mine, but the first wording was Claude's. It drafted no options for my held-out labels, audit verdicts or claim labels.
- **What I did** : answered the question sheet; chose the topic words, the predictions and the rag cut; wrote the reasons in FILTER.md 1.4; labelled the held-out set blind; judged the reject audit and named the false friend; labelled every shortlist claim; made both trust decisions; ran the review commands; wrote FRICTIONAL.md and the sign-off.
