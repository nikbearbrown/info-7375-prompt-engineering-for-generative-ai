# Sources and contributions — JS3

## Data
- Job postings: public Greenhouse (Databricks, Scale AI) and Ashby (OpenAI) board APIs, fetched by my JS2 agent on 2026-11-10 and frozen here (`out/raw/`, CORPUS.sha256).
- Persona: Priya Nair, the fictional course persona from the JS1 "Reallocation Engine" (`data/target.example.json`).

## Course material used
- Starting code: my own JS2 submission (commit 4109698); JS2 documents kept in `js2-inherited/`.
- Third-party MCP server evaluated: `lessons/08-mcp-from-scratch/code/main.py` from the course repository, run unmodified.
- I did not open or use any other student's folder.

## AI contributions (Claude, Anthropic)
- **Claude Code** wrote the JS3 code and tests (`js3/`, `mcp/`, `tests/test_js3_*`, `tests/test_mcp_*`) from my prompts. I reviewed each build's ambiguity list, ran the tests myself and committed.
- **Claude Code** suggested all 74 audit and held-out verdicts (`js3/batch_label.py`); I reviewed each and corrected 9. It also drafted the 25 claim labels (in auto mode); I reviewed the flagged ones.
- **Claude (`claude -p`)** wrote the 5 shortlist justifications (`out/shortlist/claude_raw/`).
- **Claude Code** acted as the MCP client in `transcripts/claude-code-client-attempt*.txt`.
- **Claude (chat)** proposed the FILTER.md rules for me to confirm, planned the steps, wrote the terminal commands, and drafted AUDIT.md, SCORE.md, TOOLSERVER.md, SHORTLIST.md, SIGNOFF.md, this file, README.md and a first draft of FRICTIONAL.md from my notes and terminal output. I reviewed and edited them; the trust decisions and reflections are mine.

## My contributions
All decisions in SIGNOFF.md's driver's-seat table; running every command and test; reviewing and correcting labels; catching that the first committed verdicts were still Claude's suggestions; choosing to report the held-out result as inconclusive rather than as an improvement.
