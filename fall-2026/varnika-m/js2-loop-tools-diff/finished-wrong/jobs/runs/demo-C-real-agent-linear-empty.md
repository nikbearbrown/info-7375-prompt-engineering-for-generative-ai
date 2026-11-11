# Run demo-C-real-agent-linear-empty

- **Source:** SEEDED from saved responses (no network)
- **Exit:** `incomplete` (code 2): ashby/linear suspect empty
- **What that means:** Every board was attempted within budget, but at least one board failed or is suspect. Those boards have no counts (not 0) and their state was not changed.
- **Budget used:** 3 of 5 boards, 3 of 8 requests, 0.2 of 120 seconds
- **Rules:** GATE.md of 2026-11-10
- **Note:** SEEDED; Linear's response is CONSTRUCTED (the real one with an empty jobs list). The real agent.

| Board | Status | HTTP | Requests | Postings | New | Gone |
|---|---|---:|---:|---:|---:|---:|
| greenhouse/anthropic | ok | 200 | 1 | 677 | 0 | 0 |
| lever/palantir | ok | 200 | 1 | 304 | 0 | 0 |
| ashby/linear | suspect: empty | 200 | 1 | — | — | — |

A dash means no value: a failed, suspect or skipped board has no counts, never 0.

**ashby/linear: empty.** A 200 with zero postings is not proof of no jobs. Check the board's public page by hand.

## greenhouse/anthropic (watch)

No new ids since the last good run of this board.

## lever/palantir (watch)

No new ids since the last good run of this board.
