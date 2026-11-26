# JS3 — The Filter, the Tool, and the Score

Rithika Sankar Rajeswari · INFO 7375 · Fall 2026 · built on my JS2 agent (4109698).

## Start here
| File | What it holds |
|---|---|
| FILTER.md | Filter v1.0 (written before any code), evidence rules, expected sources, wrong versions, change log to v1.1 |
| AUDIT.md | Reject audit of 50 rows, false friend, v1.0 vs v1.1 |
| SHORTLIST.md | 5 Claude justifications, quote check, claim labels, relevance vs entailment |
| TOOLSERVER.md | My MCP server and the course teaching server, both evaluated |
| SCORE.md | Origin of every number; one change at a time on held-out labels |
| SIGNOFF.md | What I checked, what I did not, driver's seat |
| SOURCES.md, FRICTIONAL.md | Sources and AI contributions; my log |

## Setup and run (Python 3.11+, standard library only, offline)
```bash
python3 -m unittest discover -s tests
python3 -m js3.run_filter --config config/filter-v1.1.json --out out/filter/v1.1
python3 -m js3.measure --decisions out/filter/v1.1/decisions.jsonl --verdicts labels/audit_verdicts.csv --key labels/audit_key.json
python3 -m mcp.client
python3 mcp/probe_other.py
```
The shortlist step (`python3 -m js3.shortlist ... --run-claude`) calls Claude and is not needed to reproduce the results; its raw outputs are committed.

## Notes
- `transcripts/` also holds three server logs from Claude Code sessions that connected while I was registering the server; the evaluated runs are named in TOOLSERVER.md.
- Labels are Claude-suggested and human-reviewed (see `labels/LABELING_METHOD.md`).

License: MIT.
