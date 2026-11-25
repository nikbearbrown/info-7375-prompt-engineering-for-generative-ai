# Boundary predictions — permission policy (JS2)

Committed before any policy code or test existed. The commit that adds this file shows the time.

- **The cases:** listed by Claude Code on 2026-11-08 from [GATE.md](../GATE.md) (the permission policy and wrong versions 5–6) and the brief's required cases. The student received them as a sheet with empty prediction columns.
- **The predictions:** the student's, pasted in chat on 2026-11-08 and reproduced verbatim under "The student's predictions".
- **In the tests,** every request is simulated (nothing is sent) and every file is a stand-in inside a temporary folder.

Setup for every file case: the project folder is `js2-loop-tools-diff/`, the current run is `R2`, and `R1` is an earlier run.

## The cases (Claude Code's list)

| # | The agent tries to… |
|---|---|
| N1 | GET `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` (one of the student's boards) |
| N2 | POST to that same Greenhouse address |
| N3 | GET `https://example.com/jobs` (a host that isn't on the list) |
| N4 | GET `http://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` (http instead of https) |
| N5 | Follow a redirect: the address in N1 answers "moved to `https://example.com/jobs`" |
| N6 | GET an Ashby posting's own link, `https://jobs.ashbyhq.com/linear/d3bc1ced-3ce4-4086-a050-555055dbb1ff` (a link found inside a posting) |
| N7 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` (right host and path shape, but Stripe isn't one of the boards) |
| F1 | Read `persona/alex_morgan.json` |
| F2 | Read `state/state.json` |
| F3 | Read a file outside the project folder, `~/Documents/resume.pdf` |
| F4 | Write `runs/R2/trace.json` (the current run's folder), with no approval |
| F5 | Write `runs/R1/trace.json` (an earlier run's folder), with no approval |
| F6 | Write `runs/R2/../R1/trace.json` (goes through `..`) |
| F7 | Write `runs-evil/R2/trace.json` (a look-alike folder next to `runs`) |
| F8 | Write `runs/R2/out/trace.json`, where `runs/R2/out` is a symlink to a folder outside the project |
| F9 | Write `runs/R2/link/trace.json`, where `runs/R2/link` is a symlink to `runs/R2/sub` (it points back inside) |
| F10 | Write `state/state.json` with no approval |
| F11 | Write `state/state.json` with an approval for run `R1` (the wrong run) |
| F12 | Write `state/state.json` with an approval for run `R2` that names `state/other.json` (the wrong file) |
| F13 | Write `state/state.json` with an approval for run `R2` that names `state/state.json` |
| F14 | Write the temporary file `state/.state.json.tmp` with the approval from F13 |

## The student's predictions (verbatim)

Requests

* N1 allow — Exact HTTPS GET for the configured Anthropic board.
* N2 refuse — Only GET is allowed.
* N3 refuse — `example.com` is off the allow-list.
* N4 refuse — HTTPS is required.
* N5 refuse — Redirects aren’t followed.
* N6 refuse — Links found inside postings aren’t fetched.
* N7 refuse — Stripe isn’t a configured board.

Files

* F1 allow — Reading the fictional persona is permitted.
* F2 allow — Reading saved state is permitted.
* F3 refuse — The résumé is outside the approved read paths.
* F4 allow — A new trace in the current run’s folder needs no approval.
* F5 refuse — R1 belongs to an earlier run.
* F6 refuse — `..` is blocked and leads out of R2.
* F7 refuse — `runs-evil/` is outside the allowed `runs/` folder.
* F8 refuse — The symlink points outside the project.
* F9 refuse — Symlinks are blocked even when they point inside R2.
* F10 refuse — The state write has no approval.
* F11 refuse — The approval is for R1.
* F12 refuse — The approval names a different file.
* F13 allow — The approval matches R2 and `state/state.json`.
* F14 allow — The same approval covers the temporary file for the atomic state update.
