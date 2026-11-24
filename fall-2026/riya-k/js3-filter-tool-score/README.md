# Job-Search Agent 3: The Filter, the Tool, and the Score

Riya Kapadnis · INFO 7375 · Fall 2026 · Assignment JS3 · 2026-11-24

**Started from:** my JS2 agent (`../js2-loop-tools-diff/`, final commit `6a800a2`). I reused its rules (JS1 + amendments
1–4), its Greenhouse/Ashby parser (`js3/ats.py`, copied unchanged) and its fictional persona Arya Sahni. The corpus is
the 2,576 postings JS2 saved in its live day-2 run (2026-11-10 19:45 UTC; read in place from
`../js2-loop-tools-diff/runs/raw/`, never re-fetched). No Lectern or Reallocation Engine code. Who did what: `SOURCES.md`.

## Where each deliverable is

| The brief asks for | Here |
|---|---|
| FILTER.md written first: filter + reasons, evidence rules, expected sources, ≥2 wrong versions, versioned | `FILTER.md`, commit `27646b2`, **before any JS3 code**; v1.1 added in §6 (`810ee17`) |
| The filter run on everything collected | `out/v1/` (55 kept / 2,212 rejected / 309 cannot_tell), `out/v1.1/` (46 / 2,505 / 25) |
| Reject audit: ≥30 random rejects judged by hand, closest calls, kept sample, what the sample can show, a false friend, rules added/cut/rejected | `AUDIT.md`; every row with my verdict and reason in `audit/audit-table.md`; labels `audit/hand-labels.json` (frozen, sha256), reasons `audit/hand-reasons.json`, corrections `audit/hand-label-corrections.json` |
| Source-grounded shortlist, every claim labeled; relevance ≠ entailment; abstention rule + counterexample | `SHORTLIST.md`; `shortlist/shortlist-v1.md`, `shortlist-v1.1.md` (+ `.json`) |
| Tool server from scratch (initialize, list tools, call a tool), real transcripts both directions, two evaluations | `js3/mcp_server.py`; `transcripts/`; `TOOLSERVER.md` (my server + `@modelcontextprotocol/server-filesystem` 2.2.0) |
| What moves the score: origin of every number, one change at a time, held-out measurement, persistence ≠ training | `SCORE.md`; `out/score-table.md`; raw Claude responses `runs/claude/` |
| Sign-off and driver's seat | `SIGNOFF.md` |
| SOURCES.md, FRICTIONAL.md | here |

## Language and toolchain

- **Python 3.13.7**, standard library only (json, re, html, hashlib, random, subprocess, argparse, unittest, threading).
- **Claude Code CLI 2.1.331**, headless (`claude -p`), on my Claude Code plan. Used for the tool-server sessions and the
  scoring runs. Model as reported in every saved response: `claude-opus-5-5` (default) and `claude-haiku-5-5` (E5).
- **Node 24.10.0 + npm**, only to run the *other* tool server I evaluated (`@modelcontextprotocol/server-filesystem@2.2.0`,
  installed in a scratch folder with `--ignore-scripts`; not part of this folder).
- Tests, the filter, the audit, the shortlist and all measurement are **offline**. They need the JS2 folder next to this one.

## Exact commands (from a fresh clone)

```bash
cd fall-2026/riya-k/js3-filter-tool-score

# offline
python3 -m unittest discover -s tests -v                 # 35 tests, under 1 s
python3 tools/check_wrong_versions.py                    # plants W1, W2, W3, W4a, W4b; all must be CAUGHT
python3 tools/run_filter.py                              # filter v1 on the 2,576 postings -> out/v1/
python3 tools/run_filter.py --filter filters/filter-v1.1.json
python3 tools/make_shortlist.py --filter filters/filter-v1.1.json   # + verbatim-quote recompute check
python3 tools/measure.py audit                           # the reject audit (blind labels); add --corrected
python3 tools/measure.py heldout                         # every filter + Claude run on the held-out 20; add --corrected
python3 tools/make_tables.py                             # regenerate audit/audit-table.md, out/score-table.md
python3 tools/make_sheets.py                             # rebuild the blind label sheet (same seed, same 78 items)

# the tool server by hand (offline)
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"score_posting","arguments":{"board":"greenhouse:databricks","id":"8933544002"}}}' \
  | python3 -m js3.mcp_server

# live: needs a logged-in Claude Code CLI
python3 tools/claude_mcp_session.py --label s1 --prompt-file prompts/mcp-session-s1.md
python3 tools/claude_score.py --label B1 --split heldout                 # see the file for E2-E5 flags
```

## What ran (all 2026-11-24, UTC)

| Run | When | Who ran it | Kind | Result |
|---|---|---|---|---|
| Filter v1 on the corpus | ~21:15 | Claude Code, in my session | offline, on saved real postings | 55 / 2,212 / 309 |
| My blind labels | ~21:15–21:41 (sheet opened after the 21:15 sample commit; downloaded 21:41) | **me** | by hand | 78 labels, frozen `fe8f7e5` |
| Tool-server sessions s1, s2 | 21:27 | Claude Code CLI as the client | **live** Claude | `transcripts/20261124T2127*` |
| Filesystem server probes P1–P4 | ~21:30 | Claude Code, in my session | live, local sandbox | `transcripts/20261124-fs-*` |
| Claude scoring B1, B2, E3, E4, E5 (held-out) | 21:31–21:35 (before my labels were downloaded) |
| Claude dev run and E2 (prompt v2) | 22:45–22:47 | Claude Code, in my session | **live** Claude | `runs/claude/*/` (each file has its UTC time) |
| Filter v1.1 committed, then held-out measurement | 22:44–22:47 | Claude Code, in my session | offline | `out/heldout-*.json` |

Nothing here is seeded or simulated except the sample draw (seed 7375, recorded). Every Claude response shown is one
actually received, saved with its date.

## Folder map

| Path | What |
|---|---|
| `FILTER.md` | the filter as a document (my decisions), v1 + v1.1 log |
| `filters/` | `filter-v1.json`, `filter-v1.1.json`, and the four one-change candidates `filter-c*.json` |
| `js3/` | `filter.py`, `evidence.py`, `text.py`, `corpus.py`, `ats.py` (from JS2), `mcp_server.py` |
| `tools/` | run/measure/shortlist/sheet/tables scripts, `claude_score.py`, `claude_mcp_session.py`, `mcp_client.py`, `check_wrong_versions.py` |
| `tests/` | `test_filter.py`, `test_mcp_server.py`, `test_heldout.py` |
| `audit/` | sample, blind sheet, my labels + hash, reasons, corrections, generated table |
| `shortlist/`, `out/`, `runs/claude/`, `transcripts/`, `evals/`, `prompts/` | outputs, raw Claude responses, transcripts, probe scripts, prompts |
| `persona/arya-sahni.json` | fictional persona (`@example.com`, 555 phone) |

No credentials, caches or real résumé are in this folder.
