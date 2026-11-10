# The trace of one real run, with the deliberate failure

Run 1, `python3 -m agent watch`, in my own terminal on 2026-11-10 at 13:30:54Z. Full trace: `runs/20261110T133054Z/trace.jsonl` (one JSON line per observation); report: `runs/20261110T133054Z/report.md`; every response body: `evidence/raw/20261110T133054Z-*.json`.

| Step | Time (s) | Board | Attempt | Answer | Bytes | Jobs | Decision |
|---|---|---|---|---|---|---|---|
| 1 | 0.46 | greenhouse:pinterest | 1 | HTTP 200 | 2,009,055 | 167 | checked |
| 2 | 0.78 | greenhouse:figma | 1 | HTTP 200 | 1,660,655 | 143 | checked |
| 3 | 1.96 | lever:spotify | 1 | HTTP 200 | 807,304 | 85 | checked |
| 4 | 2.33 | ashby:ramp | 1 | HTTP 200 | 2,890,460 | 172 | checked |
| 5 | 2.73 | lever:no-such-board | 1 | HTTP 404 | 41 | — | failed: HTTP 404, not retried (permanent) |
| 6 | 2.73 | — | — | — | — | — | exit: `incomplete` |

**The deliberate failure:** `no-such-board` does not exist on Lever. Lever answered HTTP 404 with `{"ok": false, "error": "Document not found"}`, saved as `evidence/raw/20261110T133054Z-lever-no-such-board-a1.json`. Following `GATE.md`, a 404 is a wrong name, so the loop did not retry it, recorded the board as failed with its reason, gave it no job count, and went on. Because one board failed, the run ended `incomplete`, not `finished`.

**Budgets used:** 5 of 5 boards, 5 of 10 requests, 2.7 of 60 seconds. No retry was needed.

**What the run found:** 567 jobs. Pinterest had 17 new jobs since my last JS1 run on 2026-10-31 (its seen IDs were carried over from JS1); none is relevant by my rule (all are senior, staff, intern or non-engineering roles). Figma, Spotify and Ramp were seen for the first time, so they are baselines with 0 new. By my rule, 7 of the 567 jobs are relevant.

**The independent check on this run:** `python3 -m agent check runs/20261110T133054Z` passed. It could not recompute the new IDs yet, because these were the first saved responses from these boards in this folder; it said so in four notes.
