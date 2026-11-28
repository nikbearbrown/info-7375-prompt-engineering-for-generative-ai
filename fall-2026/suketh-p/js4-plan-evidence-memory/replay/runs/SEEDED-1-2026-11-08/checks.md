# Checks for replay `SEEDED-1-2026-11-08`

- Independent check (`python3 -I checks/independent_check.py replay/runs/SEEDED-1-2026-11-08`): exit 0
- Planted 42/99 fixture: exit 1, rejected: True
- Stale-write fixture: refused True, bytes unchanged True
- Instruction-like posting text kept as data: none

## Independent check output

```text
  report: status staged, state_advanced False
  greenhouse/anthropic: saved body is HTTP 200, 10279433 bytes, 675 jobs
  greenhouse/databricks: saved body is HTTP 200, 10058900 bytes, 922 jobs
  ashby/linear: saved body is HTTP 200, 452742 bytes, 32 jobs
  state not checked (count-only mode: no --state-before or --state-after given)
  new postings not checked (no --earlier capture and no state files)
PASS: no contradiction found between the trace, the report, its displays, the saved bodies (state not checked)
```
