# Predicted permission boundary results

Tushar Patel · Job-Search Agent 2 · November 9, 2026

Predictions recorded before implementation. Test results are pending.

The test setup will use a temporary output root named `out` and a transport spy. For a denied request, the spy should record zero forbidden outbound calls. For a denied write, the destination should stay absent or retain its original contents. For a denied local read, check that the file is never opened. The approval cases exercise the write operation with a specific destination, payload, and run.

| ID | Test input | Predicted result |
|---|---|---|
| P01 | HTTPS `GET` to Stripe's configured Greenhouse listing endpoint | Allow one request. |
| P02 | HTTPS `GET` to Notion's configured Ashby listing endpoint | Allow one request. |
| P03 | HTTPS `GET` to `example.com` | Deny before transport. |
| P04 | Host `boards-api.greenhouse.io.example.com` | Deny before transport. |
| P05 | URL `https://boards-api.greenhouse.io@example.com/` | Deny before transport. |
| P06 | Plain HTTP to the Greenhouse API host | Deny before transport. |
| P07 | HTTPS `GET` to an allowed host on port `8443` | Deny before transport. |
| P08 | `POST` to the same URL allowed in P01 | Deny before transport. |
| P09 | HTTPS `GET` to an unconfigured route on an allowed host, or to P01's exact route with `?content=true` | Deny both before transport. |
| P10 | Allowed request redirects to `example.com` | Record the redirect response. The transport spy shows exactly one request to the original URL. |
| P11 | Write a regular summary to `out/runs/<run_id>/summary.json` | Allow. The file has the exact supplied bytes. |
| P12 | Write to `out/../escape.json` | Deny. The outside path is untouched. |
| P13 | Write to sibling `out-evil/summary.json` | Deny. The sibling path is untouched. |
| P14 | Write through `out/link/`, first with an outside target and then with an inside target | Deny both. The linked targets are untouched. |
| P15 | Write to `out/protected/shortlist.json` without approval | Deny. The protected path is untouched. |
| P16 | Write to `out/protected/shortlist.json` with approval for the exact path and payload in this run | Allow. The file has the approved bytes. |
| P17 | Reuse the approval from P16 after changing the payload | Deny. The previously approved bytes remain. |
| P18 | Read `out/state.json` with valid saved state | Allow. Return the saved state. |
| P19 | Read an existing, unapproved fixture outside `out/` | Deny before opening the file. |
| P20 | In a new run, reuse P16's approval with the same destination and payload | Deny before opening the file for writing. The previously approved bytes remain. |

For P10, the HTTP client must surface the redirect response without following it automatically. Configure the standard-library client accordingly and verify the call count.

After running the tests, save the observed results and the exact test command here. Attach raw test output separately.
