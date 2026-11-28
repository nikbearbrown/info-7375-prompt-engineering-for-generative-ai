# Checks for replay `SEEDED-2-2026-11-24`

- Independent check (`python3 -I checks/independent_check.py replay/runs/SEEDED-2-2026-11-24 --earlier runs/2026-11-08-normal-1`): exit 0
- Planted 42/99 fixture: exit 1, rejected: True
- Stale-write fixture: refused True, bytes unchanged True
- Closure case on greenhouse/anthropic 5456619008: before "Listed as of the capture time" (2026-11-24T22:36:19Z); after "Closed in the seeded fixture as of the stated time" (2026-11-25T12:00:00Z); fresh is not true shown: True
- Instruction-like posting text kept as data: none

## Independent check output

```text
  report: status staged, state_advanced False
  greenhouse/anthropic: saved body is HTTP 200, 9545028 bytes, 631 jobs
  greenhouse/databricks: saved body is HTTP 200, 9748826 bytes, 890 jobs
  ashby/linear: saved body is HTTP 200, 418959 bytes, 30 jobs
  greenhouse/anthropic: against 1 earlier capture(s): 93 new, 137 missing from this list (liveness unresolved), 0 returned
  greenhouse/databricks: against 1 earlier capture(s): 99 new, 131 missing from this list (liveness unresolved), 0 returned
  ashby/linear: against 1 earlier capture(s): 1 new, 3 missing from this list (liveness unresolved), 0 returned
  state not checked (count-only mode: no --state-before or --state-after given)
PASS: no contradiction found between the trace, the report, its displays, the saved bodies and the earlier captures (state not checked)
```
