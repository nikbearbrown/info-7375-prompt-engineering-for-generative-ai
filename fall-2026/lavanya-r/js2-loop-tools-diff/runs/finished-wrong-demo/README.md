# Finished-wrong-answer demonstration (SEEDED, labeled)

Not a live run. Inputs:
- `../../../js1-contract-and-watch/evidence/raw/databricks-2026-10-30T204649Z.json.gz`: a REAL Databricks response saved by JS1 on 2026-10-30 (903 jobs), replayed.
- `inputs/greenhouse-databricks-EMPTY-constructed.json`: CONSTRUCTED by Claude, `{"jobs": []}`. It stands for a board that answers HTTP 200 with nothing, e.g. a broken feed.

See `../../logs/04-finished-wrong-demo.txt` for the exact commands and output.
