NEEDS MAYANK: greenhouse/hubspot

# Independent check of run 2026-11-11T00-24-41Z-finished-wrong

The agent's own exit was `finished`. That says how its loop ended, not whether it was right. This table is computed from the saved raw responses and my floors, not from the agent's report.

| Board | Checker verdict | Why | Agent claimed | Floor (source) |
|---|---|---|---|---|
| greenhouse/anthropic | **ok** | 679 postings, floor 100 | ok, 679 postings, 0 new (baseline) | 100 (Lectern ATS.md 2026-09-26: 618 postings; my JS1 run 2026-10-30: 670 postings. A floor far below any count seen.) |
| greenhouse/hubspot | **error-response** | HTTP 404, body is not a job list | error: http-4xx | 20 (This slug stands for HubSpot, which posted 133 jobs at hubspotjobs (Lectern ATS.md 2026-09-26). Any 'HubSpot' board under 20 is implausible.) |
| ashby/notion | **ok** | 156 postings, floor 20 | ok, 156 postings, 0 new (baseline) | 20 (Lectern ATS.md 2026-09-26: 128 postings) |
