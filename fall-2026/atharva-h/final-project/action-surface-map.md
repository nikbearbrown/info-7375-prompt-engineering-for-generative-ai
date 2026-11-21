# Action-surface map

Packet document 3 of 10. Previous: [data-boundary.md](data-boundary.md) · Next: [plan.md](plan.md)

What SponsorSQL can **read**, **write** and **send**, what authority each needs, and the code that enforces it. Checked against the code on 2026-11-21.

| Action | Kind | Who can trigger it | Authority needed | Enforced by |
|---|---|---|---|---|
| Read the `lca` table | Read | The model's SQL, after checks | None beyond the policy | `policy.check_text()` + SQLite authorizer (`policy.authorizer`, allows only table `lca`) + read-only connection (`mode=ro`, `query_only`) |
| Read `metadata` (source checksum) | Read | The system only (`policy.read_metadata`), on a separate connection | None | The model's connection denies `metadata` (test `test_other_tables_are_denied_by_authorizer`, failure case F3) |
| Read any other table, `sqlite_master`, `pragma_*` | Read | Nobody | Not grantable | Authorizer denies |
| Write, delete, alter, attach, pragma, vacuum, load extension | Write | Nobody | Not grantable | Text check, authorizer and read-only file, three independent layers (tests 1–3, F1–F2) |
| Run model text as code | Execute | Nobody | Not grantable | Model output is parsed as JSON (`proposal.parse`); only `sql` and `rows_sql` strings are used. No `eval`, no shell. |
| Write run state (`state/runs/*.json`, `state/ledger.jsonl`) | Write (local) | The system, every run | None (internal record) | `state.RunState.save` |
| Export an answer report (`outputs/answers/<run>.md`) | Write (local) | **A human at the gate** | **Approval bound to the SHA-256 of the exact view shown** | `gate.decide` + `gate.export_report`, which raises `PermissionError` unless the approval hash matches (tests 8, F9) |
| Send a prompt to Claude | Send (network) | The system, live adapter only | The owner's Claude Code login on the machine | `adapters.ClaudeCLIAdapter`. Not run live in this submission: the CLI reported "Not logged in" on 2026-11-21. The recorded adapter sends nothing. |
| Send email, messages, posts, or any external write | Send | Nobody | Not present | There is no code for it |
| Change the answer keys or the source data | Write | A human, outside the agent | Owner review | The agent has no write path to `evals/`. Keys are frozen by hash (`evals/FREEZE.md`) and checked by `evaluate.run_set`. |
| Download the workbook | Read (network) | A human, once, by hand | None (public data) | Not automated. The loader only verifies the checksum. |

## Things it must never do

These are taken from [CONTRACT.md](CONTRACT.md):
- write to the data
- run model text as code
- reveal contact data
- predict immigration outcomes
- treat "the model said it's done" as a stop
- export without a matching human approval

Each one maps to a row above and to a test or failure case in [evidence.md](evidence.md).
