# Job-Search Agent 1 — The Contract and the Watch (nishant-u)

<!-- data/resume.example.json is copied unchanged from the Reallocation Engine,
     search/examples/priya-nair/resume.example.json (repo commit d08afddc, 2026-08-17).
     sha256 a4fdbc960457ba911b9d3b8593400d17ea77f35a33ce2a508128c1694c4493c1.
     Priya Nair is a FICTIONAL persona (@example.com, 555 phone). -->

One board (Faire on Greenhouse), one fictional résumé (Priya Nair), new postings only, every verdict
justified. The contract came first: see `CONTRACT.md` and its commit.

## Toolchain

- Python 3 standard library only, no installs. Tested on Python 3.12.10, Windows 11.
- Tests: `unittest`.
- Optional: the Claude Code CLI (`claude`), logged in, for `--claude`. Without it, the Claude judge
  records "not run" and everything else still works.

## Commands

Run from this folder. Use `python3` on macOS/Linux, `py` or `python` on Windows.

```bash
python3 -m unittest discover -s tests -t .        # all tests, offline
python3 -m agent.run                              # live run against the Faire board
python3 -m agent.run --replay runs/<run>/raw.json --state /tmp/js1/seen_ids.json --runs /tmp/js1/runs
                                                  # re-run from a saved response, no network
python3 -m agent.run --replay <edited.json> --seeded   # a run labeled seeded
python3 -m agent.run --claude                     # also ask Claude (judgment) about new postings
```

A TA re-running a replay should point `--state` and `--runs` at a scratch directory, as above, so
the committed state file is left alone.

On macOS with a python.org install, HTTPS may fail until the bundled "Install Certificates" script is
run (untested here).

## Layout

| Path | What |
|---|---|
| `CONTRACT.md` | the gate, written and committed before any code |
| `data/` | the fictional résumé and `requirements.json` |
| `agent/` | `watch`, `rules` (record), `claude_judge` (judgment), `validator`, `resume`, `run` |
| `prompts/baseline.md` | the Claude prompt contract |
| `tests/` | tests written from the contract, constructed fixtures, and the three mutants |
| `runs/<date>-<n>/` | `raw.json` (verbatim), `meta.json` (time, sha256), `report.md`, `report.json` |
| `state/seen_ids.json` | posting ids seen so far |
