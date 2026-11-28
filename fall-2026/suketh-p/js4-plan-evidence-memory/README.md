# Job-Search Agent 4 · The plan, the evidence and the memory

INFO 7375, Assignment 9 (Chapters 10–12), due Tuesday, December 1, 2026, 11:59 pm ET. Student: Suketh Reddy Produtoor.

The agent plans before it acts ([PLAN.md](PLAN.md)), checks what it claims ([EVIDENCE-MATRIX.md](EVIDENCE-MATRIX.md)), and remembers across two days without fooling itself ([MEMORY-GATE.md](MEMORY-GATE.md), [PREMORTEM.md](PREMORTEM.md), [replay/](replay/)). Claude Code drafted this README on 2026-11-28, and the student checks it. [SOURCES.md](SOURCES.md) says who wrote what.

## What it starts from

- **JS3 at `ae850602`**, the student's Job-Search Agent 3. Its code, its tests and the files those tests read were copied unchanged in `a470a831` (121 files). JS3's own README, SOURCES, FRICTIONAL and run record were left out.
- **Two saved captures:**
  - `runs/2026-11-08-normal-1`, from JS2 at `9c1db18`, copied unchanged in `184081d0`;
  - JS3's `runs/2026-11-24-js3-corpus`.
- **The student's JS2 `GATE.md`**, as PLAN.md names it.

## Language and toolchain

- Python 3.12.7, standard library only, with tests in `unittest`. No third-party package.
- macOS, zsh and git. The student used `shasum` for their own hash check.
- No network requests and no model calls in anything JS4 ran: every run read saved captures. The persona, `persona/alex_morgan.json`, is fictional.

## Exact commands

Run everything from this folder. `-B` writes no bytecode cache, and `-W error` turns every warning into an error.

Run all 376 tests:

```bash
python3 -B -W error -m unittest
```

The checker on a saved run: the count check alone, then with an earlier capture for new and missing postings. On the planted fixture it must exit 1.

```bash
python3 -I checks/independent_check.py runs/2026-11-24-js3-corpus --earlier runs/2026-11-08-normal-1
```

```bash
python3 -I checks/independent_check.py fixtures/count-42-planted-99
```

Rebuild the count fixtures:

```bash
python3 -I fixtures/make_count_fixtures.py
```

Show the revision and SHA-256 that the next approval for the replay state must name:

```bash
python3 -B -W error -m jobwatch.replay receipt
```

The replays, the premortem trigger and its resume are below, exactly as they ran. Each approval was single-use. Running one again is refused, because the run ID is used or the approval no longer matches the state. To replay from scratch, work in a copy of this folder. Delete the copy's `replay/state/state.json`, which `init` never replaces, then run `python3 -m jobwatch.replay init` and use new run IDs.

```bash
python3 -B -W error -m jobwatch.replay run --run-id SEEDED-1-2026-11-08 --capture runs/2026-11-08-normal-1 --approve SEEDED-1-2026-11-08:replay/state/state.json:0:f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d
```

```bash
python3 -B -W error -m jobwatch.replay premortem --capture runs/2026-11-08-normal-1 --approve-anthropic PREMORTEM-anthropic:replay/premortem/state.json:0:f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d --approve-databricks PREMORTEM-databricks:replay/premortem/state.json:0:f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d
```

```bash
python3 -B -W error -m jobwatch.replay run --run-id SEEDED-2-2026-11-24 --capture runs/2026-11-24-js3-corpus --earlier runs/2026-11-08-normal-1 --approve SEEDED-2-2026-11-24:replay/state/state.json:1:3539364075cf9f1304f73b9604936ce8bd057a051f03c26feba7ed299b4f31e5 --closure fixtures/closure/2026-11-28-closure.json
```

```bash
python3 -B -W error -m jobwatch.replay premortem-resume --capture runs/2026-11-08-normal-1 --watcher databricks --approve PREMORTEM-databricks-2:replay/premortem/state.json:1:72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9
```

## What ran

| When (UTC) | What | Result | Evidence |
| --- | --- | --- | --- |
| 2026-11-25 16:48 | The count check on both captures and the two count fixtures | Both captures passed (675 / 922 / 32 and 631 / 890 / 30). The 42-key fixture passed; the planted 99 was rejected | [evidence/checks/2026-11-25-count-check.txt](evidence/checks/2026-11-25-count-check.txt) |
| 2026-11-25 17:52 | The new-key check, Nov 24 against Nov 8 | Passed: 93 / 99 / 1 new, 137 / 131 / 3 missing, 0 returned | [evidence/checks/2026-11-25-new-key-check.txt](evidence/checks/2026-11-25-new-key-check.txt) |
| 2026-11-28 13:44 | Replay `SEEDED-1-2026-11-08`, approved | Finished. Revision 0 → 1. Baselines 675 / 922 / 32. Every check in step 5 passed | [replay/runs/SEEDED-1-2026-11-08/](replay/runs/SEEDED-1-2026-11-08/) |
| 2026-11-28 13:44 | The premortem trigger, both writes approved | Anthropic committed revision 1. Databricks was refused as stale (expected revision 0, found 1); the bytes did not change | [replay/premortem/record.md](replay/premortem/record.md) |
| 2026-11-28 13:50 | Replay `SEEDED-2-2026-11-24`, approved | Finished. Revision 1 → 2. The two-day diff: 93 / 99 / 1 new, 137 / 131 / 3 missing. Both watchers' notes merged (93 + 99). The closure fixture showed "fresh is not true" | [replay/runs/SEEDED-2-2026-11-24/](replay/runs/SEEDED-2-2026-11-24/) |
| 2026-11-28 13:52 | The premortem resume, approved after the student's line-5 decision | Databricks rebuilt on revision 1 and committed as revision 2. The 1,350 Anthropic facts are unchanged | [replay/premortem/resume-PREMORTEM-databricks-2.md](replay/premortem/resume-PREMORTEM-databricks-2.md) |
| 2026-11-28, by 13:58 | The student's own check: `shasum` on both state files, and the checker on `SEEDED-2` | The hashes match the receipts; the checker passed | [evidence/student-checks/](evidence/student-checks/) |

Every approval is quoted word for word in [replay/APPROVALS.md](replay/APPROVALS.md). Each test run, failing before the code and passing after, is in [evidence/test-runs/](evidence/test-runs/).

## Where things are

| Path | What it holds |
| --- | --- |
| [PLAN.md](PLAN.md), [PLAN-v0.1.md](PLAN-v0.1.md), [evidence/plan-review/](evidence/plan-review/) | The reviewed, approved plan; the first draft; the review record |
| [MEMORY-GATE.md](MEMORY-GATE.md) | The student's gate for the memory: the record, the revision boundary and the triggers |
| [PREMORTEM.md](PREMORTEM.md) | The student's prediction, then what the trigger and the resume did |
| [EVIDENCE-MATRIX.md](EVIDENCE-MATRIX.md) | Every claim, its check, the failure it catches, and whether it ran |
| [replay/](replay/) | The replay state and its versions, the two runs, the premortem's disposable state and records, and the approvals |
| `jobwatch/memory.py`, `jobwatch/watchers.py`, `jobwatch/replay.py` | JS4's code: the memory, the two watchers with the notes coordinator, and the replay |
| `checks/independent_check.py` | The checker: count mode and `--earlier` |
| `tests/` | JS3's tests and JS4's: `test_count_check.py`, `test_new_key_check.py`, `test_memory.py`, `test_watchers.py`, `test_replay.py` |
| [fixtures/](fixtures/) | The labelled count fixtures (42 and the planted 99) and the closure fixture |
| [FRICTIONAL.md](FRICTIONAL.md), [SOURCES.md](SOURCES.md) | The student's log, and who wrote what |
| Everything else | JS3's code and record, copied unchanged |

## The sign-off and the driver's seat

The student writes these. They will go here.
