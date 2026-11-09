# Review gate — empty board responses

## 0. Which change?

I’m reviewing how the loop handles a board that answers HTTP 200 with an empty jobs list. In the seeded run at `8020acb`, Linear’s empty response was reported as usable with zero jobs, and the run finished and updated state. The independent check flagged that result.

## 1. The rule

Save the response and mark the board `unverified` with the reason “empty jobs list.” Leave its job count and new-posting count unknown. Keep checking the other boards within the run budget. If at least one other board is usable, the run should end `incomplete`, show those results as provisional, and leave the state untouched. If no board is usable, the run should end `error`.

## 2. The reproduction

Both cases use the normal three-board plan, simulated HTTP responses, and matching simulated approval for the run and state file.

| Input | Expected result |
| --- | --- |
| **Greenhouse, first run.** Start with no state file. Anthropic returns HTTP 200 with `{"jobs":[]}`. Databricks and Linear return valid, nonempty lists. | Save Anthropic’s raw response and report it as `unverified`, with its job count and new-posting count unknown. Databricks and Linear are still checked. The run ends `incomplete` and creates no state file. |
| **Ashby, later run.** Start from a valid saved baseline for all three boards. Linear returns HTTP 200 with `{"apiVersion":"1","jobs":[]}`. Anthropic stays nonempty and Databricks returns its previous postings plus one new posting. | Save Linear’s raw response and report it as `unverified`, with its job count and new-posting count unknown. Report the new Databricks posting as provisional. The run ends `incomplete` and the state file stays byte-for-byte identical. |

For comparison, replaying all three nonempty baseline responses with matching approval should still finish and report zero new postings for each board.

## 3. Allowed files

The patch may change only `jobwatch/loop.py`, in `classify_response`. Both parsers can still read an empty array. The loop decides whether the response is usable. The pre-patch regression tests go in `tests/test_review_empty_board.py` and stay fixed during the patch.

## 4. What a wrong patch would look like

November 8, 2026 — A patch is wrong if either system can still report an empty jobs list as a successful check or if a nonempty board with zero new postings gets marked unverified.
