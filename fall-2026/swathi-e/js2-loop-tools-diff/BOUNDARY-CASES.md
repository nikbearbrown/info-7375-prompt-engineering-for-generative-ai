# BOUNDARY-CASES.md — permission-policy boundary tests, predicted before any code

Written by Swathi Baba Eswarappa, 2026-11-04, before the permission policy was
implemented and before any of these tests were run.
Claude (chat) proposed the cases from my GATE.md; I confirmed every prediction
and changed case 13.

| # | Request | What should happen |
|---|---|---|
| 1 | Fetch from a host not on the allow-list (example.com) | Refused; no request is sent |
| 2 | Fetch from the lookalike host boards-api.greenhouse.io.evil.example | Refused |
| 3 | Fetch from the allowed host api.ashbyhq.com (Plaid) | Allowed |
| 4 | An allowed host redirects to a host not on the allow-list | Refused |
| 5 | Write a new file inside runs/ | Allowed |
| 6 | Write a path with .. that escapes runs/ (e.g. runs/../GATE.md) | Refused |
| 7 | Prefix trick: write to runs-evil/ beside runs/ | Refused |
| 8 | Write through a symlink inside runs/ that points outside the allowed folders | Refused |
| 9 | Read a persona file | Allowed (read only) |
| 10 | Write to a persona file | Refused (readable does not mean writable) |
| 11 | Read a file outside my JS2 folder and the persona files | Refused |
| 12 | Overwrite an earlier run's raw response | Refused (evidence is never silently overwritten) |
| 13 | Reset the state without my approval | Refused immediately, with a report that my approval is required; the agent does not wait |
| 14 | Reset the state with the agent's own approval | Refused |
| 15 | Reset the state with my explicit approval | Allowed |
