# Review packet: the `src/state.mjs` id fix (GATE.md wrong version 10)

The change under review is commit `c04d1ecf` ("Fix state.mjs id handling: canonical string ids, legacy Greenhouse normalization, STATE_INTEGRITY (reviewed, revised twice)"), written by Claude Code and committed by me. Its diff is saved as `evidence/state-patch.diff`, which is byte-identical to `git diff ce33fd8d c04d1ecf -- src/state.mjs`.

## The defect, reproduced

JS1's `src/state.mjs` passed every id through `Number(...)` before saving and comparing (the removed lines in `evidence/state-patch.diff`: `ids.map(Number)` in `saveState`, `state.ids.map(Number)` and `Number(j.id)` in `diffNew`). A Lever id is a UUID string, so `Number(uuid)` is `NaN`, which JSON writes as `null`.

Two real snapshots show it:

- `out/snapshots/20261110T215021538Z-prefix-lever-baseline/lv-spotify.after.json` holds `"count": 1, "ids": [null]`, written by run `20261110T215021538Z-prefix-lever-baseline`. That run's `board_result` reports 86 raw jobs and 86 new (`out/traces/20261110T215021538Z-prefix-lever-baseline.jsonl`). 86 distinct UUIDs were saved as one `null`.
- `out/snapshots/20261110T215313703Z-prefix-lever-replay-2/lv-spotify.before.json` holds `"count": 2, "ids": [0, null]`, with `"updated_by_run": "20261110T215039330Z-normal"`. The normal run loaded `[null]` (so `Number(null)` gave `0`) and added the 86 UUIDs again (`NaN`, saved as `null`).

The visible effect: run `20261110T215313703Z-prefix-lever-replay-2`, a **replay** of the baseline's saved raw response (`out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json`), reported 86 new and ended `finished`, exit 0. The correct count was 0, because all 86 UUIDs had been observed in the baseline. The independent checker catches it with rule 3, not rule 2 (output in `TRACE.md`).

## Test written before the patch

- `test/state-regression.test.mjs` was committed in `17c9225a` at 17:35 (−0500), eleven minutes before the patch commit `c04d1ecf` at 17:46.
- Before the test existed, the suite passed 114 of 114 (`evidence/node-test-pre-patch.txt`, committed in `4b1336cf`).
- With the test and the unpatched `src/state.mjs`, the suite ran 119 tests: 114 passed, 5 failed (`evidence/regression-failing.txt`, committed in `17c9225a`). The five failures:

| Test | Case | Failure in `evidence/regression-failing.txt` |
|---|---|---|
| 104 | 1. fresh Lever UUIDs: save, then load returns exactly those strings | expected the three UUID strings, actual `[null]` |
| 105 | 2. second cycle: load, add one new UUID, save, load returns exact strings | expected the three UUID strings, actual `[null]` |
| 106 | 3. repeat: the same UUIDs observed again yield 0 new ids | expected `0`, actual `3` |
| 107 | 4. legacy state: numeric Greenhouse ids load as decimal strings | expected `'5416444', '5601879', '5895430'`, actual the numbers `5416444, 5601879, 5895430` |
| 108 | 5. corrupt state: a Lever state file holding `[0, null]` makes load throw `STATE_INTEGRITY` | `Missing expected exception.` |

- After the patch, the suite passed 119 of 119, including tests 104–108 (`evidence/node-test-post-patch.txt`, committed in `c04d1ecf`).

## The diff as a change in behavior

From `evidence/state-patch.diff`:

| Input | Before (`ce33fd8d`) | After (`c04d1ecf`) |
|---|---|---|
| `saveState` with Lever UUIDs | saved as `[null]` | saved as the exact UUID strings |
| `saveState` with Greenhouse numbers | saved as numbers | saved as decimal strings, in numeric order |
| `loadState` of legacy numeric Greenhouse ids | returned the numbers | returns decimal strings |
| `loadState` of an `lv-` board with any non-UUID id (`null`, `0`, a number) | returned as stored | throws an `Error` with `code: 'STATE_INTEGRITY'` |
| `loadState` of a `gh-` board with `0`, a negative, `"007"` or an unsafe integer | returned as stored | throws `STATE_INTEGRITY` |
| `loadState` of any other board with `null`, `NaN`, `""`, an object, an array or a boolean | returned as stored | throws `STATE_INTEGRITY` |
| `loadState` of a file with duplicate ids after normalizing | returned as stored | throws `STATE_INTEGRITY` |
| `saveState` with an invalid id | wrote it (after `Number`) | throws `STATE_INTEGRITY` before writing anything |
| `diffNew` | compared ids with `Number(...)` | compares ids as exact strings |

Unchanged: the three exported functions and their signatures, the state file's fields (`board`, `updated_by_run`, `count`, `ids`), "no file means first run", the plain error for a file with no `ids` list, and `saveState` merging overlapping ids (its input is prior state merged with a new response; GATE.md Decision committed in `a0dc494a`).

The rule for each board comes from the board id prefix: `lv-` requires UUID strings; `gh-` requires positive safe integers or their canonical decimal strings; any other board takes non-empty strings or safe integers (GATE.md Decisions committed in `3aae3352` and `a0dc494a`).

## Scope

- `c04d1ecf` changed one code file, `src/state.mjs`, and added two evidence files (`evidence/state-patch.diff`, `evidence/node-test-post-patch.txt`). No test changed in that commit.
- **First attempt:** a stricter rule threw `STATE_INTEGRITY` for any board id without a `gh-` or `lv-` prefix. That broke two JS1 tests, which save state for boards named `fixture` and `stripe`: test 20 ("Wrong version 4 (seen-id bug)…") and test 25 ("watch CLI end to end on the constructed fixture…"), numbered as in `evidence/node-test-post-patch.txt`. The GATE.md Decision committed in `3aae3352` records this: "the stricter rule broke JS1's tests for boards `fixture` and `stripe`".
- **Revision 1** (`3aae3352`): any other prefix gets generic validation instead of an error, with no test changes.
- **Revision 2** (`a0dc494a`): duplicates are an integrity error on load only, and `gh-` ids must be positive.
- **Follow-up changes outside `src/state.mjs`,** each in its own commit after the patch:
  - `15ae4789`: the checker also rejects Greenhouse id 0.
  - `377fd51c`: the loop catches a `saveState` error and ends the run `error`, exit 12, with `run_end` written.
  - `0310af25`: a Decision recording that an invalid raw id ends the whole run, not just that board.

## Commands and their saved output

| File in `evidence/` | Added in | What it holds |
|---|---|---|
| `node-test-pre-patch.txt` | `4b1336cf` | `node --test` output (TAP): 114 tests, 114 pass |
| `mutants-pre-patch.txt` | `4b1336cf` | `node tools/mutate-policy.mjs` output: control 0 failed of 77; 19 mutants, 19 killed, 0 survived |
| `regression-failing.txt` | `17c9225a` | `node --test` output: 119 tests, 114 pass, 5 fail |
| `state-patch.diff` | `c04d1ecf` | `git diff` of `src/state.mjs`, identical to `ce33fd8d..c04d1ecf` |
| `node-test-post-patch.txt` | `c04d1ecf` | `node --test` output: 119 tests, 119 pass |

The run commands are recorded in each trace's `run_start` event (`argv`), for example `["--config","boards.json","--label","post-patch-1"]` in `out/traces/20261110T225022146Z-post-patch-1.jsonl`.

## Live runs after the patch

All four steps are on 2026-11-10, after `c04d1ecf` (17:46 −0500, 22:46 UTC) and `377fd51c` (22:48 UTC).

1. **`20261110T224942910Z-post-patch-integrity`** (`--config boards.json`):
   - gh-stripe was observed (776 jobs, 1 new). Its legacy numeric state (776 numbers in `gh-stripe.before.json`) was rewritten as 777 strings (`gh-stripe.after.json`).
   - gh-airbnb was unchanged (203 jobs, 0 new), its 203 numbers rewritten as strings.
   - Request 3 to lv-spotify returned 200. Loading `out/state/lv-spotify.json` (`[0, null]`) then threw: "2 invalid lever id(s), e.g. 0".
   - The run ended `error`, exit 12, after 3 requests. gh-broken was never attempted; `run_end` lists `unattempted: []`, and the trace has no `failures_written` event.
2. **`c4f9b555`:** the corrupt file was moved by hand from `out/state/lv-spotify.json` to `out/quarantine/lv-spotify.corrupt.json` (a 100% rename in that commit). It still holds `[0, null]`, `"updated_by_run": "20261110T220108098Z-normal"`.
3. **`20261110T225022146Z-post-patch-1`** (`--config boards.json`):
   - lv-spotify had no prior state (`state_before: null`) and was observed: 85 jobs, 85 new. `lv-spotify.after.json` holds 85 strings.
   - gh-stripe and gh-airbnb were unchanged.
   - gh-broken got `error: not found` with `escalate: true`.
   - The run ended `incomplete`, exit 10, after 4 requests.
4. **`20261110T225032086Z-post-patch-2`** (`--config boards.json`): lv-spotify had 85 jobs and 0 new, its state 85 strings before and after. gh-broken got `error: not found`, escalate. The run ended `incomplete`, exit 10, after 4 requests. `out/failures.json` now holds gh-broken `consecutive: 4`, `escalate: true`, and 0 for the three real boards.

**Checker output.** No checker output for these runs is saved in `evidence/`; the message of commit `0326b046` reads "checker passes". The output below came from running the checker while drafting this file on 2026-11-10. The checker reads `out/` only and makes no network requests.

```bash
node src/check.mjs --trace out/traces/20261110T224942910Z-post-patch-integrity.jsonl --trace out/traces/20261110T225022146Z-post-patch-1.jsonl --trace out/traces/20261110T225032086Z-post-patch-2.jsonl
```

```
# 20261110T224942910Z-post-patch-integrity (mode: live) — out/traces/20261110T224942910Z-post-patch-integrity.jsonl
gh-stripe rule 1: PASS — 776 raw job(s), 776 unique valid id(s)
gh-stripe rule 2: PASS — expected 1 new, claimed 1
gh-stripe rule 3: FAIL — pre-run state has 776 invalid id(s), e.g. 5416444
gh-airbnb rule 1: PASS — 203 raw job(s), 203 unique valid id(s)
gh-airbnb rule 2: PASS — expected 0 new, claimed 0
gh-airbnb rule 3: FAIL — pre-run state has 203 invalid id(s), e.g. 6757302
20261110T224942910Z-post-patch-integrity: FAIL
# 20261110T225022146Z-post-patch-1 (mode: live) — out/traces/20261110T225022146Z-post-patch-1.jsonl
gh-stripe rule 1: PASS — 776 raw job(s), 776 unique valid id(s)
gh-stripe rule 2: PASS — expected 0 new, claimed 0
gh-stripe rule 3: PASS — 777 persisted id(s), all valid
gh-airbnb rule 1: PASS — 203 raw job(s), 203 unique valid id(s)
gh-airbnb rule 2: PASS — expected 0 new, claimed 0
gh-airbnb rule 3: PASS — 203 persisted id(s), all valid
lv-spotify rule 1: PASS — 85 raw job(s), 85 unique valid id(s)
lv-spotify rule 2: PASS — expected 85 new, claimed 85
lv-spotify rule 3: PASS — 85 persisted id(s), all valid
gh-broken rule 1: PASS — no jobs array
gh-broken rule 2: PASS — failed board, no new-id claim
gh-broken rule 3: PASS — 0 persisted id(s), all valid
20261110T225022146Z-post-patch-1: PASS
# 20261110T225032086Z-post-patch-2 (mode: live) — out/traces/20261110T225032086Z-post-patch-2.jsonl
gh-stripe rule 1: PASS — 776 raw job(s), 776 unique valid id(s)
gh-stripe rule 2: PASS — expected 0 new, claimed 0
gh-stripe rule 3: PASS — 777 persisted id(s), all valid
gh-airbnb rule 1: PASS — 203 raw job(s), 203 unique valid id(s)
gh-airbnb rule 2: PASS — expected 0 new, claimed 0
gh-airbnb rule 3: PASS — 203 persisted id(s), all valid
lv-spotify rule 1: PASS — 85 raw job(s), 85 unique valid id(s)
lv-spotify rule 2: PASS — expected 0 new, claimed 0
lv-spotify rule 3: PASS — 85 persisted id(s), all valid
gh-broken rule 1: PASS — no jobs array
gh-broken rule 2: PASS — failed board, no new-id claim
gh-broken rule 3: PASS — 0 persisted id(s), all valid
20261110T225032086Z-post-patch-2: PASS
```

The command exited 1, because the integrity trace failed.

- **Post-patch-1 and post-patch-2:** every rule passed for every board.
- **The integrity run:** rule 3 failed for gh-stripe and gh-airbnb. Their pre-run snapshots (`out/snapshots/20261110T224942910Z-post-patch-integrity/gh-*.before.json`) held the legacy numeric ids. The checker requires persisted ids to be strings, while the patched `src/state.mjs` normalizes numbers on load.

## Decision: accept, after two revisions

First attempt: all 5 regression cases passed, but JS1 tests 20 and 25 failed with
STATE_INTEGRITY because the prefix rule threw on unprefixed board ids ("fixture",
"stripe"). Claude Code offered three options: edit the JS1 tests, retire JS1, or scope
the rule. I rejected editing tests (it would make the code pass by changing the
evidence) and retiring JS1 (it would lose my starting point's coverage). Instead I
revised the rule in GATE.md first: lv- strict UUID, gh- canonical decimal, any other
board generic validation. That kept the patch in src/state.mjs with no test changes.

Second revision: state.mjs accepted negative Greenhouse ids while check.mjs rejected
them. I required positive safe integers so the two validators agree (check.mjs then
aligned on 0 in 15ae4789, a separate commit outside this packet).

Evidence for accepting: my own run, 119/119 (evidence/node-test-post-patch.txt); the
diff is byte-identical to ce33fd8d..c04d1ecf; the live sequence: integrity error on
the real corrupted file, manual quarantine, then Spotify 85 new → 0 new with the
checker passing all three rules on every board (evidence/check-post-patch.txt).

## One case the test would still miss

UUID case variants. The Lever check is case-insensitive, but ids are compared as exact
strings, so "2A55…" and "2a55…" would be stored as two different ids. Lever returns
lowercase today, so it hasn't happened, and no test covers it. A second gap:
loadState decides the validation rule from the file's own "board" field, not its path,
so a Lever file with that field missing would get generic validation and accept [0].
