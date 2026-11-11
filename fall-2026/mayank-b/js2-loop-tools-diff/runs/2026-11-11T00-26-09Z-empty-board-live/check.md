NEEDS MAYANK: ashby/greenlight

# Independent check of run 2026-11-11T00-26-09Z-empty-board-live

The agent's own exit was `finished`. That says how its loop ended, not whether it was right. This table is computed from the saved raw responses and my floors, not from the agent's report.

| Board | Checker verdict | Why | Agent claimed | Floor (source) |
|---|---|---|---|---|
| greenhouse/anthropic | **ok** | 679 postings, floor 100 | ok, 679 postings, 0 new (baseline) | 100 (Lectern ATS.md 2026-09-26: 618 postings; my JS1 run 2026-10-30: 670 postings. A floor far below any count seen.) |
| ashby/greenlight | **suspect** | 0 postings in the raw response (an empty board is not 'no new jobs') | ok, 0 postings, 0 new (baseline) | None (unknown: no posting count exists for this slug; the checker's 0-postings rule applies regardless of floor) |
| ashby/notion | **ok** | 156 postings, floor 20 | ok, 156 postings, 0 new (baseline) | 20 (Lectern ATS.md 2026-09-26: 128 postings) |
