# A finished wrong answer, and the check that catches it

**Every run here is SEEDED: no network was used.** The Linear response in runs B and C is **CONSTRUCTED**. Run B is **wrong version W5, run on purpose**. Claude Code ran all three on 2026-11-10 at my request, with `python3 scripts/finished_wrong_demo.py` (commit `3f9c1c0`).

## The wrong answer

Wrong version W5 (GATE.md section 6) treats a `200` with zero postings as a good board with nothing new. It is plausible: the board answered, the JSON parsed, and "no ids I haven't seen" really is "no new ids".

Run B gave it Linear's real live response from 2026-11-10 with only the `jobs` list emptied (`fixtures/linear-CONSTRUCTED-empty.json`, keys `apiVersion` and `jobs`, SHA-256 `5e344d1d…`). That is what an outage, a renamed board or an API change can look like. The run ended cleanly and was wrong:

| | Run B: wrong version W5 | Run C: the real agent, same responses |
|---|---|---|
| Exit | **`finished`**, code 0 | `incomplete`, code 2 |
| Linear | `ok`: 0 postings, 0 new | `suspect: empty`, no counts |
| Linear's state | updated, with a run of 0 postings | not touched |
| Report says | "No new ids since the last good run of this board." | "A 200 with zero postings is not proof of no jobs. Check the board's public page by hand." |

Its own report gives one hint, which is easy to miss: the Gone column says Linear lost all 33 postings. Nothing in the loop's own logic treats that as a problem, so W5's exit is still `finished`.

## The independent check

`check_run.py` does not import the agent and does not believe its report. It reads the trace, the saved raw responses, the board's state history and GATE.md, and recomputes things itself. On run B (`finished-wrong/jobs/runs/demo-B-WRONG-VERSION-W5-linear-empty.check.txt`, re-run with `check_run.py` at commit `c47736c`, after the review fixes added the `gone_recomputed` and `boards_match_config` checks; the verdict is the same as at `3f9c1c0`):

```text
Independent check of run demo-B-WRONG-VERSION-W5-linear-empty (the loop said: finished)
  PASS  raw_sha256                               3 raw responses match the trace
  PASS  independent_count                        every ok board's count matches my own count of its raw response
  FAIL  finished_needs_postings_on_every_board   ashby/linear has 0 postings in its raw response
  FAIL  no_drop_to_zero                          ashby/linear reported ok with 0 postings (last good run had 33)
  PASS  new_ids_recomputed                       every ok board's new ids match a recomputation from the earlier raw responses
  PASS  gone_recomputed                          every ok board's gone count matches its last good run's raw response (or is unknown)
  PASS  budgets_and_hosts                        3 requests, all to GATE.md hosts, within budget
  PASS  boards_match_config                      the record's boards are config/boards.json's, and each was fetched or truly a repeat
  PASS  exit_consistent                          exit finished agrees with the boards and the trace
Verdict: the run's claim is NOT SUPPORTED.
```

On run C, the real agent on the same bytes, every check passes and the verdict is SUPPORTED, because the real agent claimed `incomplete`, which is true.

Seven of the nine checks **pass** on the wrong run. The hashes match, the counts are counted right, and the exit agrees with the statuses the loop wrote. A check that only re-did the loop's own arithmetic would have said yes. Only the two checks that compare against the outside (the raw bytes and the board's own history) catch it.

## The three runs

| Run | Responses | Loop exit | `check_run.py` |
|---|---|---|---|
| A `demo-A-baseline` | live run 2026-11-10T212848Z's saved bytes for Anthropic, Palantir, Linear | `finished` (baseline for all three) | SUPPORTED |
| C `demo-C-real-agent-linear-empty` | the same, with Linear's replaced by the constructed empty one | `incomplete`, Linear `suspect: empty` | SUPPORTED |
| B `demo-B-WRONG-VERSION-W5-linear-empty` | the same as C | **`finished`**, Linear `ok`, 0 postings | **NOT SUPPORTED** |

C ran before B so that both started from the same state: C does not write Linear's state, and B does. The records, reports, traces and check outputs are in `finished-wrong/jobs/runs/`. The demonstration has its own `config/`, `persona/` (a copy), `fixtures/` and `jobs/`, so it never touches the live state in `jobs/`.

The same wrong version is also caught by the tests: `tests/test_wrong_versions.py::test_w5_empty_board_as_no_new_jobs_is_caught_twice` runs `test_empty_board_is_suspect_not_no_new_jobs` and `test_the_real_agent_on_the_same_responses_passes` against W5, and both fail on it.

## What this does not show

- Linear never really went empty. The empty response is constructed.
- `no_drop_to_zero` needs history. On a board's **first** observation there is no earlier count, so the check can only say "no earlier run to compare". The real agent still calls that board suspect.
- A board that drops from 33 to 3 postings because of a partial response would pass every check here. Only zero is caught.
