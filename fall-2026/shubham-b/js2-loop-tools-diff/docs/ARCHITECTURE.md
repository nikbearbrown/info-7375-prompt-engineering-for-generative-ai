# Architecture

One run (`jsa run`) is one pass of `pipeline.run_once`:

```text
config/agent.toml ─► config ─► resume gate ──────────────► VerifiedResume (fictional, pinned SHA-256)
                                                              │
boards-api.greenhouse.io ─► http (allow-list) ─► raw bytes + sha256 saved ─► providers/greenhouse ─► postings
                                                              │
state.json (seen IDs) ─► state.advance ─► new IDs ────────────┤
                                                              ▼
                                      for each new posting:  rule  (deterministic record, CONTRACT §6)
                                                             judge (claude -p opinion, validated, §8)
                                                              │
                         records.json, report.json/.md, model/ raw logs, state.json (atomic)
```

| Module (`src/job_search_agent/`) | Job |
|---|---|
| `cli` | `jsa` commands: `run`, `doctor`, `pending`, `rule`, `verify-evidence`, `audit-privacy`, `docs`, `exp` |
| `config` | Loads and validates `config/agent.toml`; refuses unknown keys and paths outside the project |
| `resume` | Résumé gate: fictional flag, reserved contacts, structure, pinned digest. Only it can make a `VerifiedResume` |
| `http` | `AllowListTransport`: HTTPS, allow-listed hosts, redirects re-checked, size and time limits |
| `providers/greenhouse` | Validates the board response; reports missing, duplicate or invalid IDs instead of inventing them |
| `text`, `jsonpath` | HTML decoding and cleanup; the minimal JSONPath used for evidence |
| `rule/` | `title`, `skills`, `exclusions`, `location`, `verdict`: the four §6 gates and the record |
| `evidence_validator` | Checks every rule record's evidence against the real inputs |
| `judge/` | `payload` (what Claude sees), `prompt` (sections of `prompts/judge.v1.md`), `backend` (the `claude` subprocess), `validator` (§8), `rawlog`, `judge` (retry once, statuses) |
| `state` | Seen IDs, pending judgments; pure `advance`, written atomically by the caller |
| `fsio` | `OutputRoot`: every write stays inside the data dir, no-follow, atomic (`os.replace`) |
| `status`, `report` | The seven run statuses and exit codes; `report.json`/`report.md`; `docs/RUNS.md` |
| `privacy` | `audit-privacy`: résumé values, absolute paths, credentials in outputs |
| `experiments/` | Chapter 1–3 harnesses: `sampling`, `selection` + `prompt_experiment` + `metrics`, `surfaces` |

Design rules:
- The rule and Claude never see each other's output.
- Python owns all network, file and state work. Claude only judges text it is given on stdin, with no tools.
- A failed fetch or a bad response never overwrites the last good state.

## JS2: the watch loop (`jsa watch run`)

```text
config/watch.toml ─► watch.load_plan ─► policy.PermissionPolicy (hosts, data/watch/, approvals)
                         │
                         ▼ for each planned board, in order (repeat rule, budget check first)
      watch.LoopFetcher ─ policy.check_request ─ budget ─ one retry if transient ─► http (allow-list)
                         │
                         ▼
      pipeline.run_once (the JS1 pass, unchanged) on data/watch/boards/<provider>-<token>/
                         │                       provider: greenhouse | ashby (FlooredProvider if A2 floor)
                         ▼
      watch.board_ok ─► watch.decide_exit ─► data/watch/loops/<loop_id>/{trace.jsonl,report.json,report.md}
```

| Module | Job |
|---|---|
| `watch` | Plan model, `BudgetMeter`, `LoopFetcher` (policy, budget, repeat, retry), `board_ok`, `decide_exit`, `FlooredProvider`, `run_loop`, `reset_board` |
| `watch_cli` | `jsa watch run` and `jsa watch reset` (exit codes 8–10) |
| `policy` | `PermissionPolicy`: `check_request`, `check_read`, `check_write`, `check_delete`, `check_action`; `settle` asks for approval |
| `providers/ashby` | Ashby posting API; maps fields onto the rule's names (GATE §9) |
| `checks/check_watch.py` (outside the package) | The independent check; standard library only |

The JS1 pipeline is reused unchanged: each board is one `run_once` with its own data folder and a
loop fetcher in place of the plain one.
