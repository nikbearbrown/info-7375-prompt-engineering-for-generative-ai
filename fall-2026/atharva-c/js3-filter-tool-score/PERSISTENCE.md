# Persistence is not training

DRAFT (Claude, Nov 24, 2026), to be checked and rewritten by me.

Nothing in this project trains a model. When the agent "does better" from one version to the next, it is because a file I can read and diff changed. The model's weights did not change.

## What persists, and where

| What | Where | Who changes it |
|---|---|---|
| The filter's rules and numbers | `FILTER.md`, `agent/filter.py`, versioned in git (v1.0 → v1.3) | Claude drafts it; I approve each change. Every change has a changelog row and a commit. |
| What counts as a good posting for Sam | `labels/*.csv`, `audit/filter-v1.0/*.csv` | Only me, by hand |
| The saved job data | `evidence/run-20261123-185425Z/` | Written once by the JS2 loop and never edited |
| What the MCP server was asked | `out/mcp-calls.jsonl`; copies in `evidence/mcp/` | Written by the server, appended only |
| Claude Code's memory about this project | A note on my machine outside this folder, saying the JS3 deadline is Nov 25 | Claude Code wrote it. It is not in this repo and holds no posting data. |

## What does not persist

- **Each Claude session starts without knowing this project.** It knows the work only from the files and git history it reads, plus Claude Code's own memory notes.
- **The `claude -p` session against my MCP server** (`evidence/mcp/claude-code-transcript.md`) learned nothing that carries over. Its answer exists only because I saved it.
- **The model is not trained on my labels.** Labeling 90 postings and judging 53 changed my files, not Claude.

## Why it matters here

- **Every improvement can be traced to a change in a file.** The v1.2 gain (dev false positives 6 → 0) comes from one line in `agent/filter.py` and one row in FILTER.md. You can check it out, revert it, or re-run it.
- **A model that "learned" the change could not be shown or undone that way.**
- **The persisted state is also what can go stale.** The data is a snapshot from Nov 23, 2026. Nothing refreshes it, and the MCP tools say so (`search_postings`) or should (finding 4 in `mcp/EVALUATIONS.md`).
