# SOURCES

## What I used
- **My Job-Search Agent 1:** the rule (`agent3/rule.py`, used only for the JS2-style run report), the persona `data/resume_jack_spencer.json`, the Claude caller (`agent3/claude.py`), the judge and its validator (`agent3/judge.py`), the labeling rule (`labels/LABELING_RULE.md`, inherited, plus a dated entry), and the judge prompt (`prompts/judge_v1.md`, byte for byte from JS1 `prompts/judge_revision.md`).
- **My Job-Search Agent 2:** the loop, providers, fetch, permission policy, config and run driver (`agent3/`), its tests (`tests/test_loop.py`, `test_policy_boundaries.py`, `test_review_time_budget.py`, `fakes.py`), its saved Nov 10 responses and run record (`out/evidence/20261111T011106Z/`, `out/runs/20261111T011106Z.*`), and its seen-id state.
- **Public job-board APIs** (read-only): Greenhouse `figma`, Lever `spotify`, Ashby `snowflake`, and the deliberately missing Greenhouse board `no-such-board-js2`.
- **The Model Context Protocol** message shapes (JSON-RPC 2.0 over stdio: initialize, tools/list, tools/call), implemented from scratch in `agent3/mcp_server.py` with no MCP library.
- **`@modelcontextprotocol/server-filesystem@2.2.0`** from npm (integrity `sha512-mNLj/qhV+P4kj1qP8VzgQ2fjSmWcKDQ3Q+KpZEA+WahCDWHw5zJBRQUNSPZ6Ai2/ZGGUjzNzsFpz958a1+4T9A==`; repository github.com/modelcontextprotocol/servers), evaluated, not used by the agent. Its resolved dependency tree is in `mcp/fs_server_installed_tree.txt`.
- **Claude Code CLI 2.1.316** with `claude-opus-5-5`, both as a component (judge, justify, check) and as the real MCP client in the transcripts.
- **Claude Code in VS Code** (`claude-opus-5-5`) as my coding assistant, 2026-11-24 to 11-25.
- **Python 3.12.10** standard library; **Node.js 24.19.0** only for the filesystem server.

## What I wrote or decided
- Every decision in FILTER.md v1.0 (approving Claude's numbered proposals F1–F9, E1–E5, A1–A3; choosing WV1–WV4 and the label sizes), committed alone before any code.
- All 80 posting labels (`labels/hand_labels.csv`) and all 69 claim labels (`labels/claim_checks_v1.0.csv`).
- The choice, after Claude's flags, to change the definition of "relevant" rather than my labels, and accepting Claude's drafted wording as is.
- Which candidate rules to add (C2) or reject (C1, C3, C4); adopting the fitted threshold (v1.2); approving the 150 + 30 held-out Claude sessions; asking for the definition-prompt run.
- Choosing to let E4 apply to my claim check.
- The trust decisions in mcp/EVALUATION.md, the "My view" lines, my reflections in FRICTIONAL.md, and the signature on the sign-off.

## What Claude Code contributed
- **All code** in `agent3/`, `scripts/`, `experiments/`, and `tests/`, including the four wrong versions (`tests/wrong_versions.py`), the MCP server, the probe client, the two labeling pages, and the second-method recompute.
- **The proposals** behind FILTER.md v1.0, and its wording; the measurement of the JS1 rule that found the `Snowflake` false friend before v1.0.
- **The prompts** `justify_v1.md`, `check_v1.md`, `judge_v2_abstain.md`, `judge_v3_definition.md` (v3's definition is the wording I accepted). `persistence_note.md`.
- **The label flags** (`labels/label_flags.md`) and the known-noise list (`labels/label_noise.md`, Claude's reading, not checked by me), and the wording of the new definition.
- **The candidate rules** C1–C4 and their measurement; the threshold fit and its tie-break rule.
- **The design and running** of every probe, every Claude run, and the persistence demonstration.
- **Drafts** of README.md (including the sign-off wording and the driver's-seat "why" column), AUDIT.md, SHORTLIST.md, WHAT_MOVES_THE_SCORE.md, mcp/EVALUATION.md, this file, and the factual log in FRICTIONAL.md.

## What Claude did not contribute
- Any hand label, or any posting. Every posting is from the saved board responses. Test postings and the filesystem sandbox are marked CONSTRUCTED.
- The trust decisions, the "My view" lines, and the signature.
