# Job-Search Agent 3 — The Filter, the Tool, and the Score

Ethan Gomes · INFO 7375 · 2026-11-25

This layer decides which collected postings reach me (Chapter 7), offers the agent to Claude as a tool through a protocol written from
scratch (Chapter 8), and accounts for every number in the score (Chapter 9). It works for the fictional persona Evan Gordon, a data
engineer with about 4 years of experience, Boston preferred, open to remote or relocating within the US.

**Started from:** my JS2 agent (commit `7404ffb`: the loop, the permission policy and the Greenhouse/Lever adapters, all 113 tests) and
my JS1 contract and persona (`CONTRACT.md`, `persona/`). JS2's `GATE.md`, `baseline/` and `config/` are carried over unchanged.
`CONTRACT.md` and `GATE.md` are copied as they were submitted, so their links to `evidence/…` (such as `evidence/RUNS.md` or
`evidence/crosscheck/`) point to my JS1 and JS2 submissions, not to this folder. JS3's own evidence is in `evidence/mcp/`, `audit/`,
`labels/` and `runs/`.

## Language and toolchain

- Python 3.9.6, standard library only (no third-party packages and no MCP SDK), tests with `unittest`, macOS, git
- The `fetch` evaluation only: Homebrew Python 3.11.14 in a throwaway virtual environment outside this folder, with
  `mcp-server-fetch==2026.11.18` (and `mcp` 2.3.0) from PyPI; Node.js 25.8.0 and npm 11.11.0 were on the PATH
- The agent uses the network only in `scripts/collect_snapshot.py`, through JS2's allow-listed, read-only GET fetcher. The `fetch`
  evaluation (`scripts/fetch_transcript.py`) also used the network: PyPI for the install, then the fetch server's own requests to
  Greenhouse and example.com, and npm
- Claude is not called by anything in JS3

## Exact commands (run from this folder)

```
python3 -m unittest discover -s tests          # 158 tests
python3 scripts/js3_sabotage_check.py          # plants 9 wrong versions; each must turn its test red
python3 scripts/collect_snapshot.py            # network: one GET per board -> snapshot/<date>/ (refuses to overwrite)
python3 scripts/make_label_sheet.py            # label sheet (already made; refuses to overwrite)
python3 scripts/label.py [--redo]              # hand labeling, blind to the filter
python3 scripts/run_filter.py                  # filter on the whole snapshot -> runs/filter-<version>/
python3 scripts/make_audit_sheet.py            # reject-audit sample -> audit/audit.csv
python3 scripts/audit.py                       # judge the sample by hand
python3 -B -m jsagent.mcp_server               # the tool server on stdin/stdout
python3 scripts/mcp_transcript.py --call samsara:8141959 --out <new folder>   # record a transcript plus an audit trace
# Claude Code as the client: open this folder in Claude Code; .mcp.json starts scripts/mcp_logged_server.py, which logs to evidence/mcp/claude_client/

# the fetch evaluation (network; installs into a throwaway environment, not this folder)
/opt/homebrew/bin/python3.11 -m venv <env> && <env>/bin/python -m pip install "mcp-server-fetch==2026.11.18"
python3 scripts/fetch_transcript.py --python <env>/bin/python --out <new folder>                  # default configuration
python3 scripts/fetch_transcript.py --python <env>/bin/python --out <new folder> -- \
    --allowed-hosts boards-api.greenhouse.io api.lever.co --no-readability-js                      # my restricted configuration
```

The held-out measurement is done in Python with `jsagent.measure.measure_heldout()`. It allows one look per change, and those looks
are already used (`labels/HELDOUT_LOG.jsonl`).

## What ran (2026-11-25)

| What | Result | Where |
|---|---|---|
| Snapshot of the 10 JS2 boards, with descriptions | 2,629 postings on 8 boards; Kraken "0 postings, needs review"; the 404 board "not observed" | `snapshot/2026-11-25/` (gzipped raw files, sha256 in `manifest.json`) |
| My hand labels, blind to the filter, two passes | 72 postings: 11 relevant, 61 not; 36 tuning / 36 held-out, held-out hash locked | `labels/` |
| Filter v1.2 on everything | 5 kept, 2,621 rejected, 3 cannot tell | `runs/filter-v1.2/` |
| Reject audit: 30 random rejects + 1 closest call + 5 kept, judged by me | 30/30 rejects right; 4/5 kept right | `audit/audit.csv`, `REJECT_AUDIT.md` |
| Changes A–E on tuning; baseline, A and D on held-out once | A: held-out recall 2/7 → 6/7 | `SCORE.md` |
| Filter v1.3 (A + "internship") on everything | 10 kept, 2,616 rejected, 3 cannot tell | `runs/filter-v1.3/`, `SHORTLIST.md` |
| Tool server: 3 dry runs, 2 transcripts from my client (v1.2, v1.3), 1 with Claude Code as the client | 31, 35 and 13 lines, both directions; 0 writes or network with `-B`. Claude found the stale "v1.2" in the description, now fixed | `evidence/mcp/`, `TOOL_SERVER.md` |
| The official `fetch` server, read at `c799c85` and run in two configurations | Default: the tool description tells the model to set aside earlier instructions; npm installed 33 packages despite `readOnlyHint`. Restricted: non-allowed hosts refused, nothing started | `evidence/mcp/fetch_reference/`, `evidence/mcp/fetch_run/` |
| Tests / sabotage check | 158 OK / 9 of 9 wrong versions caught | — |

## Files

| File | What it is |
|---|---|
| `FILTER.md` | The filter, evidence rules, expected sources and wrong versions (v1–v1.2 before the build; v1.3 after measuring) |
| `REJECT_AUDIT.md` | The audit, what the sample can show, the false friends |
| `SHORTLIST.md` | The shortlist, its claim labels, relevance vs. entailment, the abstention counterexample |
| `TOOL_SERVER.md` | The server, its transcripts, declared vs. actual, and the two evaluations with trust decisions |
| `SCORE.md` | The origin of every number, the one-change-at-a-time results, and what persistence is not proof of |
| `SIGNOFF.md` | The sign-off and the driver's seat |
| `SOURCES.md`, `FRICTIONAL.md` | Sources; the honest log |
| `jsagent/` | `filter.py`, `shortlist.py`, `snapshot.py`, `mcp_server.py`, `audithook.py`, `measure.py` (JS3), plus the JS1/JS2 modules |
| `tests/test_js3_*.py` | JS3 tests (filter, claims, server, measurement, snapshot) |

No credentials, caches or real résumé are included. The persona is fictional.
