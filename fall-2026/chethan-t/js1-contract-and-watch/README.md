# Job-Search Agent 1 — Contract and Watch

INFO7375, fall 2026 · Chethan T

An agent that watches one public Greenhouse job board, finds postings new
since the last run, and judges each one against a fictional persona's résumé,
with a rule verdict (record) and a Claude verdict (judgment).

## Status (2026-10-31)
Tests and empty function stubs written. Agent not implemented yet; no runs.

## Files so far
- `CONTRACT.md` — the contract (v2), written before any code
- `CONTRACT_v1.md` — first draft, kept for reference
- `persona_arjun_mehta.json` — fictional persona résumé (@example.com, 555 phone)
- `FRICTIONAL.md` — honest log of what I tried and changed

## Planned toolchain
- Language: Python
- Job board: Greenhouse public API (`boards-api.greenhouse.io`), Klaviyo board
- Claude verdict: Claude Code CLI in headless mode (`claude -p`)

Exact commands, run results, and the sign-off will be added once the code
exists and has run.
