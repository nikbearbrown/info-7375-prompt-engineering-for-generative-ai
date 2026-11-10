# Permission policy and boundary tests (Chapter 5)

**Where it's enforced:** `jobwatch2/policy.py`, in code.
- Every network request, file read, file write and state reset asks `Policy` first.
- There is **no model call in the loop at all**, so there is no prompt that could widen the policy.
- `check_run.py` asks the same policy for its cross-check request and its writes. Since the review packet, it also asks for every read.

**The policy itself** is in [GATE.md](GATE.md#permission-policy-enforced-in-code-jobwatch2policypy):
- GET over https only
- 3 hosts, each with only its board-listing path
- no credential headers
- writes only under `runs/`, judged on the resolved real path
- reads only inside this folder
- a board reset needs `--approve-reset <board>`

## Boundary-test table

- **Predicted:** written in `GATE.md`, committed in `2fbfc39` *before* `policy.py` existed.
- **Observed:** from `python3 -m unittest tests.test_policy -v` on 2026-11-10, where all 22 tests passed.

| # | request | predicted (before) | observed | test |
|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | allow | allow | `test_01_allowed_board_get` |
| 2 | GET `https://example.com/jobs` | deny: host | deny: host | `test_02_host_off_allow_list` |
| 3 | GET over `http://` | deny: scheme | deny: scheme | `test_03_http_scheme` |
| 4 | GET `…greenhouse.io.evil.com…` (suffix trick) | deny: host | deny: host | `test_04_host_suffix_trick` |
| 5 | POST Lever `/apply` | deny: method (never apply) | deny: method | `test_05_post_apply` |
| 6 | GET Lever `/<id>/apply` on an allowed host | deny: path | deny: path | `test_06_get_apply_path` |
| 7 | GET with `Authorization` / `Cookie` | deny: credential | deny: credential (3 header spellings) | `test_07_credential_headers` |
| 8 | write `runs/state/greenhouse__stripe.json` | allow | allow | `test_08_write_state_inside_runs` |
| 9 | write `runs/../GATE.md` | deny: escapes runs/ | deny | `test_09_write_dotdot_escape` |
| 10 | write `runs-evil/x.json` (prefix trick) | deny | deny (relative and absolute) | `test_10_write_prefix_trick` |
| 11 | write through the symlink `runs/link → outside` | deny | deny | `test_11_write_through_symlink` |
| 12 | write `/tmp/x.json` | deny | deny | `test_12_write_absolute_elsewhere` |
| 13 | **read** persona | allow | allow | `test_13_read_persona` |
| 14 | **write** persona (read vs write) | deny | deny | `test_14_write_persona` |
| 15 | read `~/.ssh/id_rsa`, `../../../../etc/passwd` | deny | deny | `test_15_read_outside_folder` |
| 16 | reset a board without approval | deny: needs-approval | deny | `test_16_reset_without_approval` |
| 17 | reset with `--approve-reset greenhouse/stripe` | allow | allow | `test_17_reset_with_approval` |
| 18 | reset `ashby/openai` with stripe's approval | deny | deny | `test_18_reset_other_board` |
| 19 | the same GET twice (no transient error) | deny: repeat-blocked | deny | `test_19_repeat_blocked` |

Every prediction matched. There was **no case where the prediction and the observation differed**, so nothing was learned from a surprise here. The surprise came later, in the review packet: a component that *bypassed* the policy, not a policy bug.

**Extra cases** (`OtherPolicyEdges`), predicted in the test file:
- Each system's listing URL is allowed, and four near-misses are denied: Lever without `mode=json`, a bad slug, a single-job path, an explicit port.
- The one sanctioned retry is allowed, and a second retry is denied.
- `runs2/` is not `runs/`.

## In real runs

- **Allowed:** every allowed action appears in the trace with `"decision": "allow"`. Example: `runs/20261110T184710Z-df53fd/trace.jsonl`, with 7 reads, 7 requests and 15 writes, all allowed (the writes are 7 raw files, 6 state files, the record and the report).
- **Denials:** no denial happened in a real run. Nothing tried to leave the policy, and the policy denials are shown by the tests above.
- **Approval:** the approval-gated reset was not used on real state.
