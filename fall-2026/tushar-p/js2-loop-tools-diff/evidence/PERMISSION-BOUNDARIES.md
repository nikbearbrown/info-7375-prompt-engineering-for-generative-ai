# Permission boundary results

Tushar Patel · Job-Search Agent 2 · November 9, 2026

I recorded the predictions before implementation. All 20 cases matched them in the baseline run.

The tests use a temporary output root named `out` and a transport spy. For a denied request, the spy should record zero forbidden outbound calls. For a denied write, the destination should stay absent or retain its original contents. For a denied local read, check that the file is never opened. The approval cases exercise the write operation with a specific destination, payload, and run.

| ID | Test input | Predicted result | Observed |
|---|---|---|---|
| P01 | HTTPS `GET` to Stripe's configured Greenhouse listing endpoint | Allow one request. | Pass |
| P02 | HTTPS `GET` to Notion's configured Ashby listing endpoint | Allow one request. | Pass |
| P03 | HTTPS `GET` to `example.com` | Deny before transport. | Pass |
| P04 | Host `boards-api.greenhouse.io.example.com` | Deny before transport. | Pass |
| P05 | URL `https://boards-api.greenhouse.io@example.com/` | Deny before transport. | Pass |
| P06 | Plain HTTP to the Greenhouse API host | Deny before transport. | Pass |
| P07 | HTTPS `GET` to an allowed host on port `8443` | Deny before transport. | Pass |
| P08 | `POST` to the same URL allowed in P01 | Deny before transport. | Pass |
| P09 | HTTPS `GET` to an unconfigured route on an allowed host, or to P01's exact route with `?content=true` | Deny both before transport. | Pass |
| P10 | Allowed request redirects to `example.com` | Record the redirect response. The transport spy shows exactly one request to the original URL. | Pass |
| P11 | Write a regular summary to `out/runs/<run_id>/summary.json` | Allow. The file has the exact supplied bytes. | Pass |
| P12 | Write to `out/../escape.json` | Deny. The outside path is untouched. | Pass |
| P13 | Write to sibling `out-evil/summary.json` | Deny. The sibling path is untouched. | Pass |
| P14 | Write through `out/link/`, first with an outside target and then with an inside target | Deny both. The linked targets are untouched. | Pass |
| P15 | Write to `out/protected/shortlist.json` without approval | Deny. The protected path is untouched. | Pass |
| P16 | Write to `out/protected/shortlist.json` with approval for the exact path and payload in this run | Allow. The file has the approved bytes. | Pass |
| P17 | Reuse the approval from P16 after changing the payload | Deny. The previously approved bytes remain. | Pass |
| P18 | Read `out/state.json` with valid saved state | Allow. Return the saved state. | Pass |
| P19 | Read an existing, unapproved fixture outside `out/` | Deny before opening the file. | Pass |
| P20 | In a new run, reuse P16's approval with the same destination and payload | Deny before opening the file for writing. The previously approved bytes remain. | Pass |

For P10, the HTTP client must surface the redirect response without following it automatically. Configure the standard-library client accordingly and verify the call count.

## Baseline run

From the JS2 folder, I ran:

```bash
.venv/bin/python -m pytest tests/test_permissions.py -v | tee evidence/test-runs/permissions-run1.txt
```

See the [raw baseline output](test-runs/permissions-run1.txt) for the result of each case.

## Mutation check

I ran these three variants on November 9 to see which check blocks the P13 sibling write.

| Variant | Temporary change | P13 result | Evidence |
|---|---|---|---|
| M1 | Used a string-prefix containment check and kept the parent real-path check. | Pass. The parent check blocked the write. | [Diff](test-runs/mutation-M1.diff) · [Output](test-runs/mutation-M1.txt) |
| M2 | Used the string-prefix check and disabled the parent real-path check. | Fail. No `WriteDenied` was raised, and `out-evil/summary.json` contained `overwritten`. | [Diff](test-runs/mutation-M2.diff) · [Output](test-runs/mutation-M2.txt) |
| M3 | Kept the original containment check and disabled the parent real-path check. | Pass. The containment check blocked the write. | [Diff](test-runs/mutation-M3.diff) · [Output](test-runs/mutation-M3.txt) |

Either check was enough to stop this sibling write on its own. P13 checks the final denial, so it passes if either check still works.

The recorded suite has no case for F19's rejection of a symlinked output root or its acceptance of an ancestor alias such as `/var` → `/private/var`. Both remain untested here.
