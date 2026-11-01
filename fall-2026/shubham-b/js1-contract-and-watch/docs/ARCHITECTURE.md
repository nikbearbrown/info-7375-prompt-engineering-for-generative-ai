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
