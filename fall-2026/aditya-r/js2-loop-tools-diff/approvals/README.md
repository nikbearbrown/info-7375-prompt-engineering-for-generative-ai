# approvals/ — human approval records (read-only to the runtime)

The runtime may **read** `approvals/<run-id>.json`. It never creates or edits a file here (GATE.md §5; Addendum 1 §2; boundary cases B14 and B16–B18).

An approval record is written by Aditya, by hand, as a separate human action. It authorizes exactly one create-only export. It must match the proposal in `out/pending_approval/<run-id>.json` on all four fields:

```json
{"run_id": "...", "operation": "create-shortlist-export", "destination": "out/approved-shortlists/<run-id>.json", "sha256": "...",
 "approved_by": "...", "approved_at": "..."}
```

Then `python -m agent.loop --export <run-id>`, an export-only invocation with no board requests and no model calls, creates the export.
