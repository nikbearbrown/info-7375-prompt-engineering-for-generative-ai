# JS3 - The filter, the tool, and the score (Early Bird)

Fictional persona (Rohan Desai) throughout. Real resume, contacts and conversation transcripts are not in this folder.
**Built on my JS2** (`js2-loop-tools-diff/`, commit `3bd808f`); see SOURCES.md for what was copied and what Claude contributed.

## Language and toolchain
Python 3.13.3 on Windows 11, **standard library only** (no pip install needed to run or test anything here). Claude Code 2.1.332 with
`claude-sonnet-5-5` for the real MCP transcript and the one-change experiment. `mcp-server-fetch` 2026.11.18 was installed in a
throwaway virtual environment outside this folder, only for its evaluation.

## Exact commands (run from this folder)
```
python -m unittest discover -s tests                       # 51 tests, ~10 s
python scripts/run_filter.py data/snapshot-2026-11-01 results/filter-v2.json   # filter on all 3,068 postings
python scripts/make_shortlist.py                           # claim labels for the relevant postings -> results/shortlist.*
python scripts/audit_summary.py                            # every number in review/AUDIT.md
python -m earlybird.mcp_server                             # the MCP server on stdio (one tool: score_posting)
python scripts/mcp_demo_client.py transcripts/scripted-client.jsonl   # scripted client incl. error paths
python scripts/eval_own_server.py evaluations/earlybird-score/results.json
python scripts/eval_fetch_server.py <venv python with mcp-server-fetch> evaluations/fetch-server
python scripts/onechange.py sample | run | sheet           # the one-change experiment (run makes 40 Claude calls)
```
Claude Code calls the server through `transcripts/mcp-config.json` (`claude -p ... --mcp-config transcripts/mcp-config.json
--strict-mcp-config --allowedTools mcp__earlybird-score__score_posting`).

## What ran (all on 2026-11-25 unless noted)
- **Filter v1 then v2** on the snapshot: v1 kept 99 of 3,068; v2 kept 86 (`results/filter-v1-summary.txt`, `filter-v2-summary.txt`).
- **Reject audit**: 62 postings judged by hand (35 random rejects, 12 close calls, 15 kept): `review/AUDIT.md`.
- **Source-grounded shortlist**: 86 postings, every claim labelled supported, contradicted or insufficient with a quote:
  `results/shortlist.md`. 24 (posting, claim) pairs hand-checked against the labeler: 21 of 24 agreed, 23 of 24 after one fix.
- **MCP server** written from scratch; a real Claude Code run (`transcripts/claude-code-session-2026-11-25.md`, sanitized) and a scripted
  client run (`transcripts/scripted-client-2026-11-25.jsonl`); both directions logged.
- **Two evaluations**: the official fetch server (`evaluations/EVAL-fetch-server.md`) and my own (`evaluations/EVAL-earlybird-score.md`).
- **One change on held-out labels**: `REPORT-one-change.md` (origin of every number; 20 held-out pairs; 3 misleading without the
  claim statement, 0 with it; p = 0.25, so weak evidence). Variant B is the default.

## Where things are
| File | What it is |
|---|---|
| `FILTER.md` | the filter as a versioned document, written before the code (`63e249b`); version log for v2 |
| `earlybird/rule.py`, `claims.py`, `mcp_server.py` | the filter, the claim labeler, the tool server |
| `tests/` | `cases.py` (27 constructed cases), `wrong_filters.py` (W1-W3), `test_filter.py`, `test_claims.py`, `test_mcp.py` |
| `review/` | blind sheets, my hand labels, keys, and every red/green test output (`1-...` to `19-...`) |
| `review/AUDIT.md` | the reject audit with counts and what the sample can show |
| `results/` | filter runs, shortlist, one-change outputs |
| `evaluations/`, `transcripts/` | the two server evaluations and the MCP message logs (the raw Claude run log is kept private and git-ignored) |
| `REPORT-one-change.md` | what moves the score |
| `SOURCES.md` | what I started from, what Claude contributed |

`earlybird/` also holds JS2's loop, policy and fetch code, copied but **not used** by JS3 (`loop.py`, `tools.py`, `gate.py`, `policy.py`,
`check.py`, `report.py`, `watch.py`, `validate.py`); its JS2 tests were not carried over, so that code is untested here.

## What this does not show
- The filter and labeler were checked on small hand-labelled samples (62 and 24 items); the v2 filter changes were tuned on the audit
  sample and have no held-out measurement. The one-change result is weak (p = 0.25).
- `cannot_tell` never fired on a real posting; it is tested on constructed postings.
- The agent was not run on a real resume or on any live board in JS3.

## Still to add (will be written, not yet done)
`FRICTIONAL.md` and the sign-off with the driver's seat table (in my own words), my two trust decisions and my reasons for variant B,
and the GitHub folder link and final commit hash for Canvas.
