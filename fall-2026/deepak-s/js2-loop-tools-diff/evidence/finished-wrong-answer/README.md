# Finished wrong answer: lever:lever on api.lever.co

Live runs, not SEEDED. Both runs were made by Claude Code (Claude Opus 5.5) in Deepak's session on 2026-11-10. Every value below comes from the files named.

## The run
- Command: `python -m jobwatch loop --config config/boards-fwa.json` at 15:08:30 ET, run id 20261110T200830Z, folder `runs/20261110T200830Z/` (commit b568846). The config is `config/boards-fwa.json` (Gate 0 decision 5): stripe, linear, and lever pointed at api.lever.co.
- It ran after the Phase 3 run `runs/20261110T200748Z/`, against the state that run wrote (`state/seen.json`, sha256 starting 8c20660665f1 before this run).
- A byte copy of its summary is in this folder: `run-20261110T200830Z-summary.json`.

## What the agent reported
- Exit FINISHED, code 0 (`runs/20261110T200830Z/summary.json`, `"exit": "FINISHED"`, `"exit_code": 0`).
- lever:lever: status OK, HTTP 200, count 0, new_ids [], baseline false.
- The raw body it saved is `[]` (`runs/20261110T200830Z/raw/lever_lever_attempt1.body`, sha256 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945).

## Why it is wrong
- The same board, lever:lever, on the EU host returned 6 postings 40.5 seconds earlier in the Phase 3 run (fetch at 2026-11-10T20:07:50.835208Z in `runs/20261110T200748Z/trace.jsonl`, against 2026-11-10T20:08:31.376195Z for the US host in `runs/20261110T200830Z/trace.jsonl`): `runs/20261110T200748Z/raw/lever_lever_attempt1.body`, a JSON list of 6, sha256 5179dcd2ca0165aeabc34f43670a1403874c19448e09d70fd7d281a6de3a4b92.
- The manual curl capture at 13:40 ET (Phase 0) shows the same pair. Row 03 of `evidence/manual-capture/CAPTURE.md` is api.lever.co with `[]`, and its sha256 equals this run's body. Row 04 is api.eu.lever.co with 6 postings, and its sha256 equals the Phase 3 body.
- "0 postings, 0 new" is therefore an answer about the US host, not about the board. The loop accepted an empty 200 as a valid board (GATE.md section 4, "HTTP 200, JSON, valid shape, zero postings: OK with count 0").
- The loop was not changed to catch this.

## What verify flagged
- `python -m jobwatch verify runs/20261110T200830Z` exited 2 with one flag (`verify-20261110T200830Z.txt` in this folder):
  `SUSPECT  lever:lever: 6 postings in prior run 20261110T200748Z, 0 now`
- verify recounted every board from the saved raw bytes, not from the loop's summary. It imports only the Python standard library (GATE.md section 7; `tests/js2/test_source_scan.py::test_verify_imports_only_the_standard_library`).
- On the Phase 3 run, verify exited 0 with no flags (`evidence/real-run/20261110T200748Z-verify.txt`).
- `python -m jobwatch replay runs/20261110T200830Z` exited 0 (`replay-20261110T200830Z.txt`). Replay re-derives the loop's own result and agrees with it; it is not the independent check.

## The second independent check
The manual curl capture that Deepak specified, made with curl outside the program before any JS2 code existed. Claude Code ran the curl commands in Deepak's session at his instruction (CAPTURE.md says so): `evidence/manual-capture/20261110T184001Z/` and its table `evidence/manual-capture/CAPTURE.md` (rows 03 and 04).

## A check Deepak ran himself
- `evidence/finished-wrong-answer/deepak-curl-check.txt`, run by Deepak in his own terminal: "Tue Nov 10 15:17:01 EST 2026", api.eu.lever.co 6, api.lever.co 0.
- Command (added to this README afterward; the .txt file was not edited):

```
{ date; for h in api.eu.lever.co api.lever.co; do printf '%s ' "$h"; curl -sS "https://$h/v0/postings/lever?mode=json" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'; done; } | tee evidence/finished-wrong-answer/deepak-curl-check.txt
```
