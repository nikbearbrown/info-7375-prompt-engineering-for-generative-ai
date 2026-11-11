# Permission boundary tests: predictions first

## Executive summary

**What this is.** Sixteen cases at the edge of what my agent may do: hosts it may call, paths it may read or write, and writes that need my approval. Each case has a **prediction written and committed before any test ran**, then the result actually observed.

**Why it matters.** The permission policy is in code (`src/jsa/policy.py`, `src/jsa/net.py`), not in a prompt. These tests are how I know the code enforces what GATE.md §6 says. A test I can't predict, I don't yet understand.

**What it found.** See the "Observed" column, filled in only after running. Row B8 is the review-packet defect (GATE §8). It is **predicted to be refused by a correct policy**, and **expected to fail on the first version**, which ports JS1's `safeWrite` (no symlink resolution) on purpose.

Predictions committed in JS2-CP2 (before code). Test names refer to `tests/test_policy.py`.

| # | Case | Request | Predicted (correct policy) | Wrong version it catches | Observed |
|---|---|---|---|---|---|
| B1 | host off the allow-list | GET `https://example.com/jobs` | **refused**: `host-not-allowed` | — | |
| B2 | allowed host as a substring | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs` | **refused**: `host-not-allowed` | W8 | |
| B3 | allowed host, plain http | GET `http://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | **refused**: `scheme-not-https` | — | |
| B4 | allowed host, https, GET | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | **allowed** | — | |
| B5 | allowed host, non-GET | POST `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | **refused**: `method-not-allowed` | — | |
| B6 | redirect from an allowed host | a 301 from an allowed host to `https://evil.example/` | **refused, not followed**: `redirect-refused` | — | |
| B7 | `..` escape on write | write `runs/<id>/../../state/seen-ids.json` | **refused**: `outside-write-root` (it resolves to `state/`, which needs approval, and isn't the run folder) | — | |
| B8 | symlink escape on write | write `runs/<id>/link/x.json`, where `link` → a folder outside the project | **refused**: `outside-write-root` | W2 (**review-packet defect: the first version is expected to allow it**) | |
| B9 | prefix trick | write `runs-evil/x.json`, a sibling of `runs/` | **refused**: `outside-write-root` | W1 | |
| B10 | read inside a read root | read `config/boards.json` | **allowed** | — | |
| B11 | read outside every read root | read `../js1-contract-and-watch/.env` | **refused**: `outside-read-roots` | — | |
| B12 | read allowed but write not | write `config/boards.json` | **refused**: `outside-write-root` | — | |
| B13 | approval-needed write, no approval | write `state/seen-ids.json`, approval absent | **refused**: `approval-required` | — | |
| B14 | approval-needed write, truthy approval | write `state/seen-ids.json` with approval `"yes"`, then `True` | **refused** both: `approval-invalid` | W3 | |
| B15 | approval for a different run | write `state/seen-ids.json` with approval = another run's id | **refused**: `approval-invalid` | — | |
| B16 | approval exactly matching | write `state/seen-ids.json` with approval == this run id | **allowed** | — | |
