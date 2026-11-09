# A finished wrong answer (JS2 brief, "A finished wrong answer")

A run of the real agent that **ends `finished` and is wrong**, and the independent check that catches it.

## The case: a board list that is complete in form but missing postings

A board can answer HTTP 200 with valid JSON and a non-empty `jobs` list that still leaves out postings
(for example a stale cache or index behind the API; not observed, see below). Every GATE check passes:
the request is 200, the JSON parses, the list is not empty (201) and has its `jobs` key (202). The agent
reports `ok` / `finished`, and its own summary can't show the gap, because it is built from the same
short list.

This is **not** a transfer cut off midway: there the body is half a JSON document, parsing fails, and
the board ends `failed` with 202 (an error the agent knows about).

Greenhouse sends its own count, `meta.total`, beside the list. The agent does not compare the two.
That gap was known when GATE.md was written and left out on purpose (JS2 decision D6), so it could be
shown here and fixed in the review packet (Step 8).

## Seeded, not observed

Greenhouse has never been seen doing this (11/07 check: Stripe 765 = 765). The response is built from
a real one:

| | Value |
|---|---|
| Source | `evidence/raw/2026-11-08T234257Z/stripe_content.json` (the Step 6 run, committed): 766 jobs, `meta.total` 766 |
| State | `input/stripe.state.2026-10-31.json`: the Stripe state from 10/31 (757 ids, git `08e3c9d`) |
| Change | the 86 postings not in that state (the ones new since 10/31) are removed; `meta.total` is left at 766 |
| Seeded file | `out/evidence/raw/seeded/stripe_missing_new_postings.json`: 680 jobs, `meta.total` 766 |

Removing exactly the new postings is chosen so the wrong answer is the brief's own example: "no new
jobs" when there are some. A real partial list would more likely lose postings at random or at the end.

## Commands (from the repo root)

```bash
.venv/bin/python demo/finished_wrong/run_demo.py 2>&1 | tee demo/finished_wrong/run_demo_output.txt
.venv/bin/python checks/total_check.py demo/finished_wrong/out/evidence/raw evidence/raw/2026-11-08T234257Z 2>&1 | tee demo/finished_wrong/total_check_output.txt
```

`run_demo.py` builds the seeded input and then runs the agent's own command line
(`python -m job_agent --board stripe --from-raw <seeded file>`) with its output moved to
`demo/finished_wrong/out/`, so the repo's real `runs/` and `state/` are not touched.

`checks/total_check.py` is the independent check: it imports nothing from `job_agent`, reads only
the saved responses, and compares `meta.total` with the length of `jobs`. Ashby responses have no
total, so they are reported as "can't check", not as passing. Its own tests: `tests/test_total_check.py`.

## Expected, written before running

| | Expected |
|---|---|
| Agent exit | `finished`, exit status 0 |
| Agent summary, Stripe | fetched 680, new **0** |
| The truth | 86 new postings since 10/31 (Step 6 run 234257Z, recomputed from raw) |
| `total_check.py` on the seeded file | 680 vs 766 → **MISMATCH**, exit status 1 |
| `total_check.py` on the real Step 6 responses | Stripe 766 = 766 OK, Cloudflare 464 = 464 OK, OpenAI "can't check" (no false alarm) |

## Result (Isaac's run, 2026-11-09T00:13:54Z)

Outputs: `run_demo_output.txt`, `total_check_output.txt`, and the run record in `out/runs/2026-11-09T001354Z/`.

| | Expected | Got |
|---|---|---|
| Agent exit | `finished`, status 0 | `finished` (summary + `verdicts.json`); trace: one `board_end` ok / seeded, no request (replay), `run_end` |
| Agent summary, Stripe | fetched 680, new 0 | fetched 680, new **0**, 0 verdicts |
| The truth | 86 new | 86 new (Step 6, recomputed from raw) |
| Check, seeded file | 680 vs 766 MISMATCH, status 1 | 680 vs 766 **MISMATCH**, "1 mismatch(es)" |
| Check, real Step 6 responses | Stripe OK, Cloudflare OK, OpenAI can't check | Stripe 766 = 766 OK, Cloudflare 464 = 464 OK, OpenAI can't check |

The agent's report says nothing is wrong: every board ok, exit `finished`, nothing new. Only the check,
reading the response itself, shows that 86 postings the board claims to have are not in the list.

Exit statuses are not in the tee'd files (the pipe hides them). From the code, `finished` maps to 0
(`job_agent/__main__.py` STATUS), and Claude re-ran the check on `out/evidence/raw` afterwards: status 1.

## A second finished-wrong case, real this time

`tests/test_known_limits.py` (JS2 D19) pins one the agent really has: a posting whose location is only
`Seattle, WA` is cut by the rule's location check (it reads text literally and finds no "US"), the run
ends `finished`, and with Claude off nothing flags it. The independent check there is a hand label
(Seattle is in the US). With `--claude` and budget left, the Claude judge disagrees and the summary
counts it (D20). See CONTRACT.md "Known limits".

## After the Step 8 patch (2026-11-09)

The gap shown above is fixed in the review packet (`REVIEW_PACKET.md`, JS2 D21): a Greenhouse list whose
length differs from its own `meta.total` now fails that board with code `203`. The Result above is the
agent **before** the patch and is kept as it was.

Isaac re-ran the same seeded file with the patched agent (output: `evidence/step8_demo_after_patch.txt`,
run record `out/runs/2026-11-09T004354Z/`):

| | Before (001354Z) | After (004354Z) |
|---|---|---|
| Stripe | `ok`, fetched 680, new 0 | `failed`, `203`, fetched —, new — |
| Reason | — | "the job list has 680 jobs but the board's meta.total says 766" |
| Run exit | `finished`, status 0 | `error` ("no board ended ok": only Stripe was run), status 1 |
| `out/state/stripe.state.json` | updated | unchanged |

`run_demo.py` still refuses to run while `out/` exists, so the before-record can't be overwritten.
