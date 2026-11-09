# Frictional

<!-- Dated entries, in my own words, written the same day. -->

## Nov 8, 2026

* **What I got wrong at first:** I initially defined `finished` in a way that would have counted runs that returned suspicious results, zero jobs, or even applied to jobs as successes. My early drafts were full of bracketed alternatives and invented details—like paginating endpoints and retrying 429 rate limits—which the review flagged for not reflecting the actual agent.
* **What I changed and why:** In commit `777cef4`, I locked down `GATE.md` before writing code in `agent/`. I narrowed `finished` to require at least one job so empty boards trigger `incomplete`, since an empty response cannot distinguish an empty board from an archived one or a broken API. I rewrote the explanation for the 15-request budget to match reality, dropping the pagination and 429 claims so it strictly reflects 1 request per board, up to 1 retry, and spare capacity. I also specified that only I change these limits by committing edits to `GATE.md`.
* **What Claude did / what I accepted:** I made all the core operational decisions: the two systems (Greenhouse + Lever), the budget numbers, the single-retry rule, treating empty boards as incomplete, requiring `--approve`, and going with Option A for `out/seen.json`. Claude asked the guiding questions, caught inconsistencies and padded text in my drafts, and synthesized a few sentences directly from my choices, which I kept as written (including the other-4xx bullet, the out/seen.json sentence, the `--approve` sentences, and the exception in the error exit). Claude also caught the contradiction between the strict "writes only in out/" rule and modifying protected files, which led me to add the explicit `--approve` exception.
* **What’s still open:** Selecting and verifying 3 real boards plus 1 deliberately bad board to test the 404 path, and writing tests for the 2-second retry wait, which hasn't been tested yet.
* **Reference commit:** `777cef4`
