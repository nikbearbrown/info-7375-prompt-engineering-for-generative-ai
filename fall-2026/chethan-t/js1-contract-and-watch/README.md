# Job-Search Agent 1 — Contract and Watch

INFO7375, fall 2026 · Chethan T

An agent that watches one public Greenhouse job board, finds postings new
since the last run, and judges each one against a fictional persona's résumé,
with a rule verdict (record) and a Claude verdict (judgment).

## Status (2026-10-31)
Rule verdict implemented; all tests pass. Claude verdict not wired in yet.
Not yet run against the real board.

## Files so far
- `CONTRACT.md` — the contract (v2), written before any code
- `CONTRACT_v1.md` — first draft, kept for reference
- `persona_arjun_mehta.json` — fictional persona résumé (@example.com, 555 phone)
- `FRICTIONAL.md` — honest log of what I tried and changed
- `config.json` — default board and résumé path
- `agent/main.py` — entry point: fetch, find new postings, judge, save
- `agent/fetch.py` — Greenhouse fetch; refuses any host but `boards-api.greenhouse.io`
- `agent/resume.py` — loads the résumé; refuses non-`@example.com` email or non-555 phone
- `agent/watch.py` — new-posting detection; baseline run reports 0 new
- `agent/rule.py` — the rule verdict (`record`) and work-authorization flags
- `agent/claude_judge.py` — validates a Claude verdict (`judgment`); no Claude call yet
- `tests/` — pytest suite with fake Greenhouse postings in `tests/fixtures/`

Created by runs (inside this folder only):
- `raw/<board>_<timestamp>.json` — raw Greenhouse response, untouched
- `state/seen_ids.json` — seen posting ids, per board
- `results/<date>.json` — every run that day, with results for new postings

## Run
From this folder:

```bash
python3 -m pytest tests                 # tests, offline
python3 -m agent.main                   # defaults from config.json
python3 -m agent.main --board klaviyo --resume persona_arjun_mehta.json
```

The first run for a board is the baseline: it saves every posting id and
reports 0 new.

## Planned toolchain
- Language: Python
- Job board: Greenhouse public API (`boards-api.greenhouse.io`), Klaviyo board
- Claude verdict: Claude Code CLI in headless mode (`claude -p`)

Exact commands, run results, and the sign-off will be added once the code
exists and has run.
