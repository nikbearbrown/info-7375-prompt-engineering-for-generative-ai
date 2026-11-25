# Persistence is not training

Nothing in this project trains a model. When the agent improves from one version to the next, it is because a human-readable, version-controlled file in this repository changed—not because any model weights were updated.

## What persists, and where

| Artifact | Location | Who updates it |
| :--- | :--- | :--- |
| **Filter rules and weights** | `FILTER.md`, `agent/filter.py` (versioned in git `v1.0 → v1.3`) | Claude drafts updates; I approve each change, backed by a changelog row and a git commit. |
| **Ground-truth labels and audit judgments** | `labels/*.csv`, `audit/filter-v1.0/*.csv` | Only me, by hand. |
| **Collected job postings** | `evidence/run-20261123-185425Z/` | Written once by the JS2 collection loop and never modified. |
| **MCP tool call history** | `out/mcp-calls.jsonl`; copies in `evidence/mcp/` | Written by `agent/mcp_server.py` (append-only). |
| **Claude Code session note** | A local memory note on my machine outside this repo noting the Nov 25 JS3 deadline | Written by Claude Code; kept outside git and contains no posting data. |

## What does not persist

- **Fresh model context:** Every new Claude session starts with zero built-in memory of this repository and reconstructs state strictly by reading project files, git history, and its local deadline note.
- **Stateless MCP client sessions:** The live `claude -p` session against `js3-job-filter` (`evidence/mcp/claude-code-transcript.md`) learned nothing that carries over. Claude Code keeps its own transcript of the session on my machine, but no later session reads it unless asked; the copy in `evidence/mcp/` exists because I saved it.
- **No weight updates from human feedback:** Hand-labeling 90 postings and judging 53 audit rows updated CSV files in this repository, not Claude's parameters.

## Why this distinction matters

- **Full auditability and reversibility:** Every behavioral change maps to an inspectable file diff. The `v1.2` improvement (`dev` false positives dropping from `6` to `0`) traces directly to a single `R2` scoring change in `agent/filter.py` (`3` lines in `6dc9c6a`) and a corresponding changelog row in `FILTER.md`—meaning any reviewer can check out, diff, revert, or re-run it. A model whose weights changed implicitly could not be inspected or rolled back that way.
- **Staleness of persisted state:** Because state lives in static files rather than a live database, the collected postings remain a fixed snapshot from Nov 23, 2026. Nothing automatically refreshes them, which is why `search_postings` explicitly discloses the snapshot date and why adding that same notice to every MCP tool description is listed as finding 4 in `mcp/EVALUATIONS.md`.
