# Sources — Job-Search Agent 3

Tushar Patel · INFO 7375 · Fall 2026 · 2026-11-25

## What I used

- **My JS1 work** (`../js1-contract-and-watch/`, last JS1 commit `cb4333e0`):
  - the fictional persona Cole Palmer ([persona file](../js1-contract-and-watch/persona/cole-palmer.example.json)), whose target titles, years, sponsorship need, country and skills the filter reads;
  - the US location lists from JS1 `CONTRACT.md` R3, reused in G3;
  - the model and SDK pin (`claude-sonnet-5-5`, `anthropic==2.3.0`), checked by `tests/test_claims.py::test_model_and_sdk_pin_are_inherited_from_js1`.
- **My JS2 agent** (`../js2-loop-tools-diff/`, last JS2 commit `80be6cb9`). It was copied into [agent/](agent/) with its tests in `6cc68807`. The one change to its fetch surface allowed `content=true` on the Greenhouse listing route only (dated 2026-11-21 in FILTER.md "Expected sources").
- **Public job-board endpoints**, read without authentication:
  - Greenhouse `boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`;
  - Ashby `api.ashbyhq.com/posting-api/job-board/notion` and `.../linear`.

  The saved responses are in [evidence/runs/live-text-1/](evidence/runs/live-text-1/) (fetched 2026-11-22T04:28Z).
- **The Model Context Protocol specification, revision 2025-11-25**: `schema/2025-11-25/schema.ts` (ToolAnnotations, lines 1168-1222) and `modelcontextprotocol.io/specification/2025-11-25/server/tools`, both fetched 2026-11-25. They are cited in [EVAL-FACTS.md](evidence/mcp/EVAL-FACTS.md). My server follows the message shapes; it uses no MCP SDK.
- **The MCP reference "filesystem" server**, `github.com/modelcontextprotocol/servers` at commit `c799c8552b0f27b7a33a7b9233773da144dddcf5`. It was cloned read-only into `/tmp` (never into this repo), read for the second evaluation, and not built or run.
- **The assignment brief**, `assignments/assignment-js3-the-filter-the-tool-and-the-score.md`, for the sign-off format and the deliverables.

## What I wrote or decided

- **The filter rules.** FILTER.md v0.1 (`821ddee3`): gates, word lists, threshold, evidence rules, expected sources and wrong versions. FILTER.md v0.2 (`d74ca782`, erratum and C4 amendment `f3edf998`): C1–C6, the three rejected variants, the false friend "platform", and freezing it before the held-out comparison.
- **The two readings of FILTER.md v0.1** that I confirmed on 2026-11-21, before the filter code was written (recorded in the `agent/filter.py` docstring).
- **Every hand label, all blind:**
  - audit 48 rows and held-out 30 rows (`f97f528a`);
  - post-unblinding corrections on audit rows 19, 29, 40 and 45 (`9ed99ceb`);
  - the changed set, 16 rows (`8d8e92f9`);
  - all 96 claims (`aaf850a0`).
- **The featured shortlist cases** (`eaed4d92`).
- **The trust decisions on both MCP servers** and the declaration fixes I required ([EVALUATIONS.md](evidence/mcp/EVALUATIONS.md), `cd745787`). That includes removing `idempotentHint` on 2026-11-25.
- **What to run, and when to stop:** the boards, the one-change-at-a-time design, and when to unseal the held-out set.

## What Claude contributed

- **Claude Code** (Claude Code 2.1.332; the commits name Claude Opus 5.5):
  - **Code:** all code under `agent/` that is new in JS3 (filter, postings, text, sheets, claims), the labelers in `tools/`, the MCP server, the report scripts in `audit/` and `checks/`, and every test in `tests/`.
  - **Proposals:** the C4 heading definition, from a survey of the text of all 979 postings, which I accepted into v0.2.
  - **Drafts:** the prose of AUDIT-RESULTS*.md, SCORE-REPORT.md, SHORTLIST.md (between the script-generated blocks) and EVAL-FACTS.md, plus this README, SIGNOFF.md draft and SOURCES.md.
  - **Runs:** both `claude -p` MCP client sessions, on my instruction. [Tushar: confirm who ran the live fetch (2026-11-22T04:28Z) and the live claim run (2026-11-23).]
- **Claude through the API** (`claude-sonnet-5-5`, live and billed, 2026-11-23 23:33–23:34 ET): the 96 shortlist claims, each with a quote and a proposed label ([evidence/claims/claims-v1.jsonl](evidence/claims/claims-v1.jsonl)). These are model output, not labels. My labels are the reference.
- **Claude Code as the MCP client** (2026-11-24): the two replies saved verbatim with their dates in `evidence/mcp/`.
- **Claude chat:** [Tushar: describe what Claude chat contributed, if anything. Claude Code has no record of chat sessions.]

## Co-Authored-By trailers

All JS3 commits were authored by the git user `Tushar-Patel28`, and every JS3 commit from `821ddee3` through `cd745787` carries `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. The commit that adds this file carries it too.

## Dependency licenses

| Package | Version | License | Checked in |
|---|---|---|---|
| pytest | 9.2.0 | MIT | `.venv/.../pytest-9.2.0.dist-info/METADATA` (`License-Expression: MIT`) |
| anthropic (Python SDK) | 2.3.0 | Apache-2.0 | `.venv/.../anthropic-2.3.0.dist-info/METADATA` and `licenses/LICENSE`. Its `LICENSE-MIT` says the SDK moved from MIT to Apache-2.0 in version 2.0.0, so 2.3.0 is Apache-2.0. |

The runtime itself uses only the Python 3.12.10 standard library.
