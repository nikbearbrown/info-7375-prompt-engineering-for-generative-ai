# Gates

Packet document 5 of 10. Previous: [plan.md](plan.md) · Next: [pre-mortem.md](pre-mortem.md)

The human approvals, each tied to what the approver saw.

## Gate 1: release an answer (in code)

| | |
|---|---|
| **When** | After an answer and its matching rows have been computed (`agent.py`, the "gate" step) |
| **Who** | The person running `python3 -m sponsorsql ask` (interactive), or a decision file written by that person (`--gate file`) |
| **What they see** | The full view built by `gate.build_view()`: the question, the source checksum, the model's interpretation and limits, the answer table, the SQL, the matching-row count, the first 20 matching rows, the evidence SQL, the count-versus-rows check, and the line "An LCA filing is not a job offer, a visa approval, or a promise of sponsorship." Then the view's SHA-256. |
| **Choices** | approve, refuse, or defer |
| **Bound to the view** | The decision records the view hash. `export_report()` writes the report only if the decision is *approve* **and** its hash equals the hash of the view now on screen. An approval file written for a different view becomes a deferral and writes nothing (test 8, failure case F9). |
| **What approval allows** | One local Markdown report in `outputs/answers/`. It contains the exact view, the approver, the note and the hash. Nothing is sent anywhere. |
| **Evaluation runs** | `--gate none`: answers are scored but never released. The stop reason is `answered_not_released`, so evaluation can't bypass the gate to export. |
| **Known limits** (independent review, finding 6) | The view includes SHA-256 values of the full answer and evidence rows, so rows past the display limit still bind the approval. But a file-mode approval is a JSON file anyone can write, isn't tied to a run id or a named person, and in file mode SponsorSQL doesn't display the view. Only the interactive mode shows the view to the approver. With the live adapter, a second run rarely reproduces the same view, so file mode is mainly useful with recorded replies. |

**Human observation evidence:** an interactive approve, refuse and defer by the owner hasn't been recorded yet. The commands to run it are in [README.md](README.md) (section "See the human gate"). This row moves to [evidence.md](evidence.md) once the owner runs it. Until then, the gate is shown by tests and fixture runs only, and is labelled that way.

## Gate 2: change the prompt contract or the answer keys (owner review, outside the agent)

| | |
|---|---|
| **When** | Before a new contract version is used for scoring, or before any change to a frozen key |
| **Who** | The owner |
| **What they see** | The diff between contract versions, and the development results before and after ([evidence.md](evidence.md)) |
| **Bound to** | The SHA-256 of each contract file, recorded in every results file (`contract_sha256`), and the key hashes in [evals/FREEZE.md](evals/FREEZE.md) |
| **Status** | **This gate was not followed.** Contract v2 was used for development round 2 and for the one-shot held-out run before the owner reviewed it (independent review, finding 1). The held-out set is therefore spent on a contract nobody approved. If the owner rejects or changes v2, a new held-out set must be frozen and scored. v2 and the controlled-failure recovery are still **awaiting owner review** ([SIGNOFF.md](SIGNOFF.md)). |

## Gate 3: ship, narrow, defer or stop (owner)

The final decision is the owner's, in [transfer-reflection.md](transfer-reflection.md) and [SIGNOFF.md](SIGNOFF.md). It's made from the evidence, not from a model's summary.
