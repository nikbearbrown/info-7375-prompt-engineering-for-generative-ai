# SIMULATED: the finished wrong answer

Everything in this folder comes from a SIMULATED demonstration, not a live run.

- `SIMULATED-databricks-empty-200.json` is SIMULATED: a constructed Greenhouse response, HTTP 200
  with zero postings. No board returned it.
- The one REAL input is `runs/2026-11-05T23-11-48-228373-0500/001-databricks-request.json`, the Nov 5
  live Databricks response, used by path (not copied).
- `js1-watch-output.txt`, `js1-watch-report.json`, `js1-watch-state-before.json`,
  `js1-watch-state-after.json`: the naive JS1 watch (watch.py, unchanged) replaying
  the real response and then the SIMULATED one. watch.py prints "SEEDED RUN"
  because all it knows is that it replayed a file; the second file is SIMULATED.
- `independent-check-output.txt`: independent_check.py on the two raw files.
- `js2-loop-result.json`: the JS2 loop's trace for the same SIMULATED response,
  served by a fake transport.

Reproduce: `python3 demo_finished_wrong_answer.py` (refuses if this folder exists).
