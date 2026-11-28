# The replay workspace (SEEDED)

Everything in this folder comes from offline replays of saved captures ([PLAN.md](../PLAN.md) v0.2). Nothing here was fetched. A replay makes 0 HTTP requests and 0 model calls, labels every run SEEDED and keeps the original capture times. Claude Code created this folder on 2026-11-28 and wrote `jobwatch/replay.py`, which fills it.

| Path | What it is |
| --- | --- |
| `state/state.json` | The replay's shared memory, `jobwatch-state/3` ([MEMORY-GATE.md](../MEMORY-GATE.md)). It starts empty at revision 0. Each new revision needs the student's approval for that run ID, this path, the starting revision and its SHA-256. |
| `runs/<RUN_ID>/` | One replay's evidence, steps 1 to 7 of the plan (below). |
| `premortem/state.json` | The disposable state file for the premortem trigger ([PREMORTEM.md](../PREMORTEM.md)). It also starts empty at revision 0. |
| `premortem/record.json`, `record.md` | Once the premortem is triggered: what each write did, and whether the refusal left the bytes unchanged. |

The two empty revision 0 files were created with `python3 -m jobwatch.replay init`. Their SHA-256 is `f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d`: both hold the same empty state. No approval has been used yet.

## Commands (run from the JS4 folder)

```bash
python3 -m jobwatch.replay receipt
```

```bash
python3 -m jobwatch.replay run --run-id RUN_ID --capture runs/CAPTURE [--earlier runs/EARLIER] [--approve RUN_ID:replay/state/state.json:REVISION:SHA256] [--closure fixtures/closure/2026-11-28-closure.json]
```

```bash
python3 -m jobwatch.replay premortem --capture runs/2026-11-08-normal-1 --approve-anthropic RUN_ID:replay/premortem/state.json:0:SHA256 --approve-databricks RUN_ID:replay/premortem/state.json:0:SHA256
```

Without `--approve`, a run still stages and checks everything, then stops as `incomplete` (exit 3) and leaves the state unchanged.

## What a run folder holds

| File | Plan step | What it shows |
| --- | --- | --- |
| `preflight.json`, `state-before.json` | 1 | The capture, the target's revision and SHA-256, the approval, the persona's hash; the exact state bytes the run started from |
| `verify.json` | 2 | Each saved body's recomputed SHA-256, its usable or unusable status and its job count |
| `notes.anthropic.json`, `notes.databricks.json` | 3 | Each watcher's own contribution: its board's new postings, scored by the pinned JS1 rule |
| `notes.json` | 4 | The coordinator's merge, Anthropic then Databricks |
| `proposal.json`, `diff.json`, `diff.md` | 4 | The staged update and the two-day diff: new, missing and returned keys per board |
| `checks.json`, `checks.md` | 5 | The independent checker on this run's report, the planted 42/99 fixture, a stale-write fixture, the closure case, instruction-like posting text |
| `publish.json`, `state-after.json` or `write-refused.json` | 6 | The committed revision, or the writer's refusal |
| `results.json`, `results.md`, `trace.json`, `trace.md` | 7 | The run's report in JS3's format, so `checks/independent_check.py` can audit it |
