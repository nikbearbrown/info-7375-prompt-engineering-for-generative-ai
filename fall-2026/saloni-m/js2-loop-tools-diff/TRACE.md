# Trace of one real run, including the deliberate failure

**Live run 1**, `20261111T004140Z-live`, 2026-11-11 00:41:40 UTC (2026-11-10 19:41 ET), run by
Claude Code with `python3 -m jsagent.run --label live` on commit `83abeea8` (JS2-2).
Not simulated. Full machine trace: [`out/runs/20261111T004140Z-live/trace.jsonl`](out/runs/20261111T004140Z-live/trace.jsonl);
report: [`report.json`](out/runs/20261111T004140Z-live/report.json); raw responses: `raw/`.

| # | Event | What happened | Budget after |
|---|---|---|---|
| 0 | `start` | planned 4 boards (≤ 5); budgets 5 boards / 10 requests / 60 s / 10 s per request | 0 requests |
| 1 | `request` → `response` | GET Greenhouse `anthropic` → **200**, 486,535 bytes, saved `raw/greenhouse-anthropic-a1.json.gz` | 1 |
| 2 | `board_result` | ok, **679 jobs**, baseline (no saved history for this board) → 0 reported new | 1 |
| 3 | `request` → `response` | GET Greenhouse `figma` → **200**, 91,239 bytes | 2 |
| 4 | `board_result` | ok, **144 jobs**, baseline | 2 |
| 5 | `request` → `response` | GET Ashby `openai` → **200**, 13,824,104 bytes (0.76 s) | 3 |
| 6 | `board_result` | ok, **826 jobs**, baseline | 3 |
| 7 | `request` → `response` | GET Greenhouse **`anthropic-doesnotexist`** → **404**, 38 bytes, body saved | 4 |
| 8 | `board_result` | **failed, "HTTP 404"**, attempts 1, `count_seen: null`, `count_new: null` | 4 |
| 9 | `exit` | **`incomplete`**, 4 requests, 1.386 s, 0 new | — |

**How the error policy handled the deliberate failure** (GATE §4, choice 4A):
- **Not retried.** A 404 won't fix itself, so there is exactly one request for it (event 7).
- **No invented value.** The board's counts are `null`, not `0`. A TA can't mistake it for an
  empty board.
- **History kept.** The board never enters saved state (`out/state/`).
- **Status.** The run is `incomplete`, never `finished`, because one board failed (GATE §7).

**What the trace does not show:** a retry (no timeout or 5xx happened in any real run; retries
are shown only in the offline tests `test_timeout_then_success_is_retried_once`,
`test_5xx_retried_once`), a repeat, or a budget stop (offline tests only, `TestBudgetsAndRepeats`).

Later real runs (2, 3 and 4) have the same shape and are in `out/runs/`. Run 3's trace also has a
`state_migrated` event (1,649 old ids → 1,649 keys, no board re-baselined) and reports 1 new job.
