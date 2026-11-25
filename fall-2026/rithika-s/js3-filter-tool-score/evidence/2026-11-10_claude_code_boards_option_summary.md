Now the five tests, added to `tests/test_loop.py`.

The suite passes, but `agent/loop.py` and `tests/test_loop.py` are now tracked and an `out/` folder has appeared, so I'm checking whether my tests created it.

`python3 -m agent.loop` now accepts `--boards FILE`. Without the option it still reads `config/boards.json` and behaves as before. All 141 offline tests pass, 7 of them new. Nothing is committed and nothing went to the network.

**Files changed**
- [agent/loop.py](agent/loop.py) (+24 / −5):
  - Adds the `--boards` option.
  - The boards file goes through the same loader as before, so the same checks apply:
    - it is read through `policy.check_read`;
    - at most `max_boards` from `config/budgets.json`;
    - no duplicate names or URLs;
    - every URL must pass `policy.check_request`.
  - Any failure exits `error` (3) before a single request is sent.
  - The path is recorded in the trace `startup` line, in `summary.json` (`boards_file`) and in `report.md` ("Boards file: …").
- [config/boards_demo_3.json](config/boards_demo_3.json) (new): the scaleai, databricks and openai entries copied unchanged from `config/boards.json`, plus a `_comment` line. A test checks that they match the main file exactly.
- [tests/test_loop.py](tests/test_loop.py) (+108): a new `BoardsOptionTests` class covering your five cases. Every exit-3 test also checks that no request was sent and that only the trace was written. Two tests go beyond your list:
  - the demo file matches `config/boards.json` exactly;
  - a `--boards` file with more than `max_boards` boards also exits 3.

**Two judgement calls**
- `boards_file` is also on the `run_start` trace line. That's because a run that fails to load the file stops before the `startup` line is written, and without this its trace wouldn't say which file was used.
- A relative `--boards` path is taken from the project root, like `--replay`.

GATE.md, BOUNDARY_TESTS.md, JS1_CONTRACT.md, `data/` and `config/boards.json` show no diff against HEAD, and the zero-postings behaviour is unchanged. The `out/` folder in the project is from your live run 1 (commit 3749c43); the tests only write to temporary folders.

**Commands** (from `js2-loop-tools-diff/`)

Full suite:
```bash
python3 -m unittest discover -s tests
```
Only the new `--boards` tests:
```bash
python3 -m unittest discover -s tests -p 'test_loop.py' -k BoardsOption -v
```
Mutant check, which still runs `test_loop.py` against every W1–W11 mutant:
```bash
python3 -m unittest discover -s tests -p 'test_mutants.py' -v
```