# Boundary-test predictions — written before the tests run

**Author:** Lavanya R. **Written:** 2026-11-10, before any policy code existed.

**Provenance:** Claude listed the inputs (the case categories are the ones the
brief requires). On 2026-11-10 I picked every "What should happen" from
multiple-choice cards (Allow / Refuse / Ask me), before any policy code existed.
Claude then pointed out that 4 of my picks disagreed with my own GATE.md. I changed
3 of them (cases 4, 8, 12) and kept case 3; my first picks are noted in the row and in
FRICTIONAL.md. The "Why" column was written by Claude, pointing to the GATE.md rule
behind each pick. After the tests ran, the "Actual" column was
filled from the test output. A prediction that turned out wrong stays as written,
and is explained below the table.

Output folder for these cases: `runs/` inside this JS2 folder.

| # | Kind | Request | What should happen (allow / refuse / ask me) | Why (which GATE.md rule) | Actual |
|---|---|---|---|---|---|
| 1 | host | GET `https://boards-api.greenhouse.io/v1/boards/databricks/jobs` | **Allow** | host is exactly `boards-api.greenhouse.io`, https (GATE 5, hosts) | allow |
| 2 | host | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs` (look-alike) | **Refuse** | the real host is `...evil.example`, not on my list of 3 (GATE 5; wrong version 2) | refuse |
| 3 | host | GET `http://api.lever.co/v0/postings/palantir` (plain http) | **Allow** | (no reason given) I kept Allow after Claude pointed out that GATE 5 says https only | **refuse** (prediction wrong) |
| 4 | host | GET `https://www.linkedin.com/jobs/` (off the allow-list) | **Refuse** | not one of my 3 hosts (GATE 5) — first pick was Allow, changed | refuse |
| 5 | path | write `runs/trace.json` | **Allow** | inside `runs/` (GATE 5, writes) | allow |
| 6 | path | write `runs/../GATE.md` (`..` escape) | **Refuse** | `..` resolves to the JS2 folder itself, outside `runs/` and `state/` (GATE 5) | refuse |
| 7 | path | write `runs-evil/x.json` (prefix trick: starts with "runs") | **Refuse** | `runs-evil/` is a different folder; it only starts with `runs` (GATE 5) | refuse |
| 8 | path | write `runs/link/x.json` where `runs/link` is a symlink to `/tmp` | **Refuse** | the real path is in `/tmp`; symlinks are followed (GATE 5) — first pick was Allow, changed | refuse |
| 9 | path | write `/tmp/x.json` (absolute path outside) | **Refuse** | outside my folders (GATE 5, writes) | refuse |
| 10 | read vs write | READ `../js1-contract-and-watch/state/databricks-seen_ids.json` | **Allow** | reads are allowed inside my JS1 folder (GATE 5, reads) | allow |
| 11 | read vs write | WRITE `../js1-contract-and-watch/state/databricks-seen_ids.json` | **Refuse** | writes only in JS2 `runs/` and `state/`; JS1 must not change (GATE 5) | refuse |
| 12 | approval | overwrite an existing `state/<board>-seen_ids.json` | **Ask me** | overwriting state needs my approval (GATE 5) — first pick was Allow, changed | ask |
| 13 | approval | same as 12, but with no approval given (non-interactive run) | **Refuse** | no approval given, so the state file is not written and the report says so (GATE 5) | refuse |
| 14 | never | an action named `apply` / `email` / `message` / `login` | **Refuse** | not one of `fetch_board`, `read_file`, `write_file`; on the never list (GATE 5) | refuse |

## Predictions I got wrong

Actual outcomes come from `python3 -B review/boundary_table.py` (output in `logs/08-boundary-predicted-vs-actual.txt`), which runs these 14 cases in a throwaway copy of the folder layout. The same cases are asserted in `tests/test_policy_boundary.py`, which also checks enforcement: refused writes leave no file, and refused URLs never open a socket.

**13 of 14 matched.**

- **Case 3, plain `http://api.lever.co/...`: I predicted Allow, and it was refused.** The host is on my list, but my own GATE.md section 5 says "https only". The code follows GATE.md. Claude pointed out the conflict before the run, and I kept my prediction anyway. Claude's reading, not mine: the host check and the scheme check are two separate rules, and the prediction looks only at the host.
