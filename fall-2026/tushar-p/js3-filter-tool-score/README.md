# Job-Search Agent 3: the filter, the tool, and the score

Tushar Patel · INFO 7375 · Fall 2026 · README written 2026-11-25

JS3 adds a layer on top of my Job-Search Agent 2 (JS2) that decides what reaches the job seeker, and why. It has four parts:

- **A filter written as a document** ([FILTER.md](FILTER.md)), plus the code that applies it.
- **A reject audit and a source-grounded shortlist**, each checked against my blind hand labels.
- **The filter offered to Claude as one MCP tool**, through a server written from scratch.
- **A report on what moves the score.**

The job seeker is **Cole Palmer, a fictional persona** from JS1 ([persona file](../js1-contract-and-watch/persona/cole-palmer.example.json)). No real résumé or personal data is used.

**Starting point.** The JS2 agent (`../js2-loop-tools-diff/`, last JS2 commit `80be6cb9`) was copied into [agent/](agent/) in `6cc68807`. The only change to its fetch surface was one allowed query, `content=true`, on the Greenhouse listing route, so Stripe postings arrive with their text (`agent/providers.py`, `tests/test_content_query.py`). Everything else under `agent/` that is new in JS3 is the filter (`filter.py`, `postings.py`, `text.py`), the label sheets (`sheets.py`) and the claim run (`claims.py`).

## Language and toolchain

| Item | Version | Use |
|---|---|---|
| Python | 3.12.10 | Everything. The runtime uses the standard library only; the MCP server uses no MCP SDK. |
| pytest | 9.2.0 | Tests (pinned in [requirements.txt](requirements.txt)). |
| anthropic (Python SDK) | 2.3.0 | Only the live claim run (`agent/claims.py`). Pinned, and inherited from JS1. |
| Claude model (API) | `claude-sonnet-5-5` | The live claim run; `evidence/claims/run-summary.json` records it as both requested and returned. |
| Claude Code | 2.1.332 | Development, and the MCP client in the two `claude -p` runs. |

On models: every JS3 commit carries the trailer `Co-Authored-By: Claude Opus 5.5`, the model of the Claude Code development sessions. The `claude -p` client runs did not record which model answered.

## Commands

Run everything from `fall-2026/tushar-p/js3-filter-tool-score/`.

```bash
# setup
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt

# tests (offline; any socket use fails a test)
.venv/bin/python -m pytest -q

# live fetch: public Greenhouse/Ashby listing routes only, allow-listed in agent/policy.py
.venv/bin/python -m agent --config config/js3-boards.json
.venv/bin/python checks/independent_count.py evidence/runs/live-text-1   # separate count check

# filter, one mode at a time (writes results.jsonl + summary.json under the git-ignored out/)
.venv/bin/python -m agent.filter --run evidence/runs/live-text-1 --out out/filter-v0.1 --rules v0.1
.venv/bin/python -m agent.filter --run evidence/runs/live-text-1 --out out/filter-v0.2 --rules v0.2
for c in C1 C2 C3 C4 C5 C6; do
  .venv/bin/python -m agent.filter --run evidence/runs/live-text-1 --out "out/filter-v0.1+$c" --rules "v0.1+$c"
done

# blind sheets and labelers (labelers are interactive; a label is write-once, --correct keeps history)
.venv/bin/python -m agent.sheets --run evidence/runs/live-text-1 --results out/filter-v0.1/results.jsonl
.venv/bin/python tools/changed_sheet.py
.venv/bin/python tools/label.py audit/audit-sheet.csv
.venv/bin/python tools/label.py labels/heldout-sheet.csv
.venv/bin/python tools/label.py labels/changed-sheet.csv
.venv/bin/python tools/label_claims.py labels/claims-sheet.csv

# claims: LIVE, billed Claude API calls on every v0.2 keep (needs ANTHROPIC_API_KEY), then the blind sheet
.venv/bin/python -m agent.claims run --live
.venv/bin/python -m agent.claims sheet

# report scripts: each prints the blocks that its test compares verbatim with the committed report
.venv/bin/python audit/audit_v01.py                          # audit/AUDIT-RESULTS.md
.venv/bin/python audit/audit_v02.py                          # audit/AUDIT-RESULTS-v0.2.md
.venv/bin/python checks/score_report.py --section 2          # SCORE-REPORT.md section 2
.venv/bin/python checks/score_report.py --section 2b         # SCORE-REPORT.md section 2b
.venv/bin/python checks/shortlist_report.py --section a      # SHORTLIST.md sections a–e (also b, c, d, e)

# MCP server (stdio; normally started by the client, not by hand)
.venv/bin/python tools/mcp_server.py
```

Tests and the filter read two files from the sibling JS1 folder: ../js1-contract-and-watch/persona/cole-palmer.example.json (fictional persona) and ../js1-contract-and-watch/config.json. Both are in the course repo, and both are included in the Canvas zip at the same relative paths.

The MCP client command was run exactly as follows, both times, with [mcp-config.json](mcp-config.json):

```bash
claude -p --mcp-config mcp-config.json --strict-mcp-config --tools "" --allowedTools "mcp__js3_filter__score_posting" --no-session-persistence "Use the score_posting tool to score ashby/notion posting 85947779-6b87-466a-98bc-30a640448c28 and greenhouse/stripe posting 8144196, then tell me in two sentences why each got its verdict."
```

## What ran

Dates are US Eastern unless marked Z (UTC).

| When | What ran | Result | Commit |
|---|---|---|---|
| 2026-11-21 | FILTER.md v0.1 written, before any JS3 code | gates G1–G5, score, evidence rules, expected sources, wrong versions | `821ddee3` |
| 2026-11-21 23:28 (2026-11-22T04:28Z) | Live fetch `run-20261122T042828Z-07c6f0`, saved as [evidence/runs/live-text-1](evidence/runs/live-text-1/) | 979 postings: Stripe 777, Notion 170, Linear 32. [independent_count.py](evidence/test-runs/live-text-1-independent-count.txt) matched all three boards. | `6cc68807` |
| 2026-11-23 | Filter v0.1 on the 979 postings; blind sheets built; I labeled them | v0.1: 8 keep, 951 reject, 20 cannot_tell. My labels: audit 48 rows, held-out 30 rows. | `6cc68807`, `7e35a098`, `f97f528a` |
| 2026-11-23 | Reject audit, v0.1 against my blind labels | 28/48 agree. Random rejects: I judged 6/30 should not be rejected (estimate 20.0%, Wilson 95% 9.5%–37.3%); this is a sample estimate, not a rate for all 951 rejects. False friend named: "platform". | `0df210f7`, then corrections in `9ed99ceb` |
| 2026-11-23 | FILTER.md v0.2 (C1–C6) frozen; filter v0.2 built; development measurement on the audit sheet | Audit agreement 28/48 → 34/48. This is development data, because C1–C6 were chosen after reading these rows. | `d74ca782`, `4c5e8c63`, `f3edf998` |
| 2026-11-23 | Held-out comparison, unsealed once; rules frozen at `f3edf99` | Every mode scored 24/30 (Wilson 62.7%–90.5%). No held-out row was one that any change could move. | `4c6754dc` |
| 2026-11-23 | Changed-postings sheet: 8 changed + 8 controls, labeled blind | Changed rows: v0.1 1/8 → v0.2 6/8 agree. This shows the direction of each change only, not a rate. | `685f22df`, `8d8e92f9`, `2e4ee3ae` |
| 2026-11-23 23:33–23:34 | Live claim run, `claude-sonnet-5-5`, on the 17 v0.2 keeps. An earlier attempt at 23:13 stopped on HTTP 401 and is kept under [evidence/claims/aborted/](evidence/claims/aborted/). | 17/17 ok, 96 claims, 0 quotes not found, estimated $0.24 | `65c97a2e` |
| 2026-11-24 | My blind claim labels; source-grounded shortlist; featured cases chosen by me | My labels and Claude's agreed on 85/96 claims. The abstention rule abstained on all 17 postings. | `aaf850a0`, `d78f5666`, `eaed4d92` |
| 2026-11-24 23:01 (04:01Z) | MCP server; first Claude Code client run | 6 messages client→server, 5 server→client; Notion keep, Stripe reject at G4 | `47282e94` |
| 2026-11-24 23:41 (04:41Z) | Declaration fix; second client run | `tools/list` showed the new description and annotations; verdicts unchanged | `cd745787` |
| 2026-11-25 | `idempotentHint` removed from the annotations (no client run after this change); final suite | see [js3-final.txt](evidence/test-runs/js3-final.txt) | this README's commit |

Since `f3edf99`, FILTER.md and the filter code (`agent/filter.py`, `postings.py`, `text.py`) have not changed. The only file added under `agent/` since then is `agent/claims.py` (`65c97a2e`). The `out/` folder is git-ignored: the filter commands above regenerate it.

## Assignment requirement → file

| Requirement | Files |
|---|---|
| Filter as a versioned document with reasons, written before the build; evidence rules; expected sources; wrong versions | [FILTER.md](FILTER.md) (v0.1 `821ddee3`, v0.2 frozen `f3edf998`) |
| Code and tests | [agent/](agent/), [tools/](tools/), [checks/](checks/), [audit/](audit/), [tests/](tests/); final run [evidence/test-runs/js3-final.txt](evidence/test-runs/js3-final.txt) |
| Reject audit with hand verdicts, honest sample statement, false friend, rules added/cut/rejected | [audit/AUDIT-RESULTS.md](audit/AUDIT-RESULTS.md), [audit/AUDIT-RESULTS-v0.2.md](audit/AUDIT-RESULTS-v0.2.md); my blind labels in [audit/audit-sheet.csv](audit/audit-sheet.csv), [labels/heldout-sheet.csv](labels/heldout-sheet.csv), [labels/changed-sheet.csv](labels/changed-sheet.csv); false friend and changelog in [FILTER.md](FILTER.md) |
| Source-grounded shortlist, every claim labeled, relevance vs entailment, abstention rule and counterexample | [SHORTLIST.md](SHORTLIST.md), my claim labels in [labels/claims-sheet.csv](labels/claims-sheet.csv), Claude's claims in [evidence/claims/claims-v1.jsonl](evidence/claims/claims-v1.jsonl), prompt [prompts/claims-v1.txt](prompts/claims-v1.txt) |
| Tool server from scratch, real transcripts both ways, two evaluations, trust decisions | [tools/mcp_server.py](tools/mcp_server.py), [tests/test_mcp_server.py](tests/test_mcp_server.py), [mcp-config.json](mcp-config.json); transcripts [pre-fix](evidence/mcp/transcript-run-20261125T040140Z-bfa84e.jsonl) and [post-fix](evidence/mcp/transcript-run-20261125T044128Z-5fd246.jsonl); replies [pre-fix](evidence/mcp/claude-client-reply-2026-11-24.txt) and [post-fix](evidence/mcp/claude-client-reply-2026-11-24-postfix.txt); [EVAL-FACTS.md](evidence/mcp/EVAL-FACTS.md); [EVALUATIONS.md](evidence/mcp/EVALUATIONS.md) |
| What moves the score: origin of every number, one change at a time, held-out measurement | [SCORE-REPORT.md](SCORE-REPORT.md) |
| Sign-off and driver's seat | [SIGNOFF.md](SIGNOFF.md) |
| Sources and AI contribution | [SOURCES.md](SOURCES.md) |
| Frictional log | [FRICTIONAL.md](FRICTIONAL.md) |

## Boundaries

- The agent reads public listing endpoints only: Greenhouse `stripe`, and Ashby `notion` and `linear`. It never applies, emails, messages or logs in.
- The MCP server reads saved files only and writes only its own transcript, under `evidence/mcp/` (shown by `tests/test_mcp_server.py`).
- No credentials are committed. Saved API requests are stored without the key (`tests/test_claims.py::test_raw_request_is_saved_with_timestamp_and_no_key`).
