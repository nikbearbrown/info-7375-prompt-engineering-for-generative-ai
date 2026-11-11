# Finished-wrong answer and the independent check
The full write-up is in [TRACE.md §2](TRACE.md#2-a-finished-wrong-answer-and-the-independent-check-that-catches-it). In short, two deliberately wrong versions each ran **cleanly to `finished`** on the live boards (2026-11-10 ~9:31 pm), and each was **wrong**:

| Demo | Wrong answer | Caught by | Log |
|---|---|---|---|
| A `empty_as_zero` | the 404 board `no-such-board-7375` shown as "ok, 0 jobs" | `watch.py check`: "the raw response was HTTP 404" | `logs/14`, `logs/15` |
| B `lever_reads_nothing` | Palantir (304 jobs) shown as "ok, 0 jobs, no new jobs" | `watch.py check --live`: "a live recount now finds 304" and "the raw response contains 304" | `logs/16`, `logs/17` |

The check is independent of the agent's report:
- **It ignores the agent's verdicts.** It recounts the jobs from the saved raw bytes with its own parser.
- **With `--live`, it asks the board again with `curl`.**
