# Job-Search Agent 3 — filter, tool, score

- **Language:** Python 3.13
- **Toolchain:** pytest, plus the Python standard library only (json, re, html, random, subprocess, sys, pathlib, collections). No third-party runtime dependencies.
- **Persona:** Priya Nair (fictional, from the Reallocation Engine `search/examples/`)
- **GitHub folder:** `fall-2026/sreevarshan-s/js3-filter-tool-score/`
- **Built on JS2 output:** `/Users/sreevarshansathiyamurthy/eng_job 2/output/raw/` (three files, run 2026-11-06): Databricks and Stripe (Greenhouse), Spotify (Lever). Read-only; never modified.
- **Final commit:** 333c12022cd8eaa38766c9c0d5c62b2262b98312

## What ran

- **Filter** on 1779 postings (Databricks 929, Stripe 765, Spotify 85) using the rules in `FILTER.md`. 47 passed, 1732 rejected. → `output/filter_results.json`
- **Reject audit:** 40 hand-judged rejects (30 random + 10 closest calls, seed 42). 38 correct, 2 can't tell, 0 false rejects. → `output/audit_sheet.md`, `output/REJECT_AUDIT.md`
- **MCP server** (`js3/mcp_server.py`) driven by a real client subprocess. → `output/mcp_transcript.txt`, evaluated in `output/MCP_EVALUATION.md`
- **Scorer** (`js3/scorer.py`) with a one-change-at-a-time report. → `output/SCORE_REPORT.md`
- **Shortlist evidence packet** for the 47 passed postings (AI-prepared claim labels, reviewed by me). → `output/shortlist_packet.md`, `output/shortlist_abstention_example.md`

## Exact commands

Run from the repo root:

```bash
python3 -m js3.run_filter
```

```bash
python3 -m js3.mcp_client
```

```bash
pytest
```

Other scripts:
- `python3 -m js3.scorer` prints the scored shortlist.
- `python3 -m js3.sample_for_audit` and `python3 -m js3.build_shortlist_packet` regenerate their outputs. Both refuse to overwrite files that have been edited.

`pytest.ini` puts the repo root on the import path so plain `pytest` works.

## Other files

- `FILTER.md`: filter rules, written before any code
- `SOURCES.md`: data sources and what Claude did vs. what I did
- `FRICTIONAL.md`: what went wrong, what I accepted or changed, what is unresolved
- `SIGN_OFF.md`: what I checked, didn't check, and don't claim, plus the driver's seat table
