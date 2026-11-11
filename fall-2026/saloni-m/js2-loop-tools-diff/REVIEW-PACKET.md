# Review packet — the change: identify a job by board as well as id

**The change I asked Claude Code to make (2026-11-10):** catch GATE wrong version 3, in my words:
"If two different boards return the same job ID, the agent treats them as duplicates instead of
identifying jobs using both the board name and job ID."

**Where the defect came from.** JS1 stored bare posting ids, because it watched one board. JS2-2
(`83abeea8`) carried that over on purpose (`job_key` returned `job_id`), so the defect could be
reproduced before any patch, instead of being written correctly the first time and never tested.

## 1. The defect reproduced, and the test written before the patch

- **Real data first.** On live run 1's real responses, the three boards share **0** ids.
  Greenhouse uses 10-digit numbers and Ashby uses UUIDs. So today's real data does not trigger the
  defect, and the reproduction uses constructed test data. That is labelled in the test's docstring.
- **Test committed before the patch:** `tests/test_identity.py` in **`75a70e03`** (JS2-4).
  Board a has job 1001; on the next run board b posts a *different* job that also has id 1001. It
  must be reported new on board b.
- **Failed on the unpatched code, run by Claude Code** (`review/01-reproduce-before-patch.txt`):
  `board b's new job 1001 was hidden by board a's job 1001 (reported new: [])`.
- **Failed again when I ran it myself on the unpatched code** (`git stash`):
  `review/05-saloni-before-patch.txt`, `FAILED (failures=1)`.

## 2. Patch v1 — the diff read as a change in behaviour

Diff: `review/02-patch.diff` (read by me: `review/04-saloni-diff-read.txt`). Committed with my
decision in `08951265` (JS2-7).

| Line(s) | Behaviour before | Behaviour after |
|---|---|---|
| `job_key` | a job is its posting id; the same id on two boards is one job | a job is `system:board:id` |
| `STATE_SCHEMA = 2` | saved history has no format version | history says which key format it uses |
| `if state.get("schema", 1) < 2` block | — | history in the old format is **thrown away and re-baselined**: nothing is reported new on this run |

**Scope.** The key change is exactly what was asked for. The re-baseline was added because,
without it, all 1,649 jobs in run 1's history would have looked new after the key change. That
would break GATE §7 ("reports a job as new that has already been seen").

**Commands I ran myself** (outputs in `review/`):

| # | Command | Result |
|---|---|---|
| 04 | `git diff -- jsagent/loop.py tests/test_identity.py` | read the diff |
| 05 | `git stash && python3 -m unittest tests.test_identity -v; git stash pop` | defect reproduced on unpatched code: `FAILED (failures=1)` |
| 06 | `python3 -m unittest discover -s tests -t . -v` | 48/48 OK with patch v1 |
| 07 | `python3 -m jsagent.run --label live` | live run 2: `INCOMPLETE`, **0 new**, history went to pending (not approved) |

**What the live run showed.** Claude Code compared the raw responses of runs 1 and 2. OpenAI went
from 826 to 827 jobs: `76084eee-9186-4897-ae12-3445307e61be`, *Account Director, Mid-Market | Korea*,
was posted between 00:41 and 00:50 UTC. **Patch v1's re-baseline hid a real new job.** Every test
was green; only the live run showed it.

### My decision on v1: **REVISE** (my words, `review/08-saloni-decision-v1.md`)

> I would choose to revise the patch. The test results were convincing because they showed that
> the original defect was reproduced before the patch and all 48 tests passed afterward. However,
> the second live run revealed something important: OpenAI had added a new job, Account Director,
> Mid-Market | Korea, but the re-baselining process reported zero new jobs. I don't think we
> should lose track of a genuinely new job just to avoid false positives.

> I think handling the old state format was necessary because changing job identity from a bare
> ID to `system:board:id` would otherwise make all previously saved jobs appear new. However,
> simply discarding the old IDs and re-baselining everything goes a little too far because it can
> hide actual new jobs. I'd prefer rebuilding the old history using the raw responses from the
> previous run so we preserve existing records without missing newly posted jobs.

## 3. Patch v2 — test first again

- **Test written before the v2 code:** `tests/test_migration.py` in **`6a453ccf`** (JS2-8). It uses
  the **real** run-1 history, run-1 raw responses and run-2 raw responses, copied to a temp folder,
  and expects exactly one new job, the Korea posting. It failed on v1 (`review/09-migration-test-before-v2.txt`):
  `Lists differ: [] != ['ashby:openai:76084eee-…']`.
- **Diff:** `review/10-patch-v2.diff` (read by me: `review/11-saloni-diff-v2-read.txt`).

| Line(s) | Behaviour v1 | Behaviour v2 |
|---|---|---|
| old-format block | throw old history away; re-baseline every board | `migrate()`: rebuild each board's keys from the raw response saved in its last ok run. An old id becomes a key only if it was **both** in that raw response **and** in the old history |
| fallback | — | a board whose old raw can't be read is re-baselined **alone**, and the trace names it (`rebaselined_boards`) |
| reads | — | the migration reads old raw files through `policy.read_bytes` (inside the project only) |
| one existing test | asserted a `state_rebaselined` event | asserts one `state_migrated` event, **and** names the three re-baselined boards (stricter, not weaker) |

**Commands I ran myself:**

| # | Command | Result |
|---|---|---|
| 11 | `git diff HEAD -- jsagent/loop.py tests/test_identity.py` | read the v2 diff |
| 12 | `python3 -m unittest discover -s tests -t . -v` | 50/50 OK |
| 13 | `python3 -m jsagent.run --label live --approve-state` | live run 3: **1 new — the Korea job**; `state_migrated` 1,649 → 1,649, no board re-baselined; I approved the history |
| 14 | `python3 -m jsagent.run --label live` | live run 4: **0 new** (nothing new twice on real data); history to pending, not approved |

**A test bug found afterwards (by Claude Code, 2026-11-10 ~20:00 ET).** After live run 3 I
approved the history, so `out/state/seen_ids.json` changed to the new format. The real-data
migration test had been reading that live file, so it started failing (`2 != 1` on the schema
check). The code was not wrong; the test's input had changed under it. Fix: the test now reads a
pinned copy of run 1's history, taken from commit `61312028`
(`tests/fixtures/run1_seen_ids_schema1.json`). To show the fix did not weaken the test, it was
re-run with `loop.py` temporarily set back to patch v1: it still fails twice
(`review/15-fixture-test-still-fails-on-v1.txt`). On v2 the suite is 50/50.

### My decision on v2: _(Saloni to write)_

## 4. A case my tests would still miss (my words)

> If the same job is posted on two different boards but has different IDs on each board, the
> current identity logic would treat them as two separate jobs. The tests only check whether
> identical IDs across boards are handled separately, not whether the same underlying job with
> different IDs can be recognized.

Also not covered by any test: in `migrate()`, a board whose *last* saved attempt is a failed one
(for example a timeout, then a 200). The code then tries the earlier attempt files. No real run
had a retry, and no test builds that case.
