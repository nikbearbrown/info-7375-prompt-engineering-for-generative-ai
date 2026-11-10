# POLICY.md — the permission policy and its boundary tests

The policy is GATE.md section 5. It is enforced in code by `agent/policy.py`, and every network request and file read or write goes through `agent/tools.py`, which asks the policy first. `tests/test_gate_matches_code.py` fails if any other file in `agent/` imports a network module or reads or writes a file itself.

## The boundary tests

The **Predicted** column was written on 2026-11-10 before the tests were run, and before `agent/policy.py` existed. It was committed together with the tests. The **Result** column was filled in only after running them: `python3 -m unittest tests.test_policy -v` on 2026-11-10, 33 tests, all passed (B14 after the change described in its row).

Each test is in `tests/test_policy.py` and its name starts with the row number.

| # | Request | Predicted | Why (GATE.md section 5) | Result |
|---|---|---|---|---|
| B01 | `GET https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` | allow | exact host, allowed path, HTTPS, GET | as predicted |
| B02 | `GET https://api.lever.co/v0/postings/palantir?mode=json` | allow | exact host, allowed path | as predicted |
| B03 | `GET https://api.lever.co.evil.example/v0/postings/palantir` | refuse | a host off the allow-list whose name starts with an allowed one | as predicted |
| B04 | `GET https://evil.api.lever.co/v0/postings/palantir` | refuse | a subdomain is a different host | as predicted |
| B05 | `GET https://evil.example/v0/postings/palantir?u=api.lever.co` | refuse | the allowed name is in the query; the host is `evil.example` | as predicted |
| B06 | `GET http://api.ashbyhq.com/posting-api/job-board/linear` | refuse | HTTPS only | as predicted |
| B07 | `GET https://user:secret@api.ashbyhq.com/posting-api/job-board/linear` | refuse | no credentials, ever | as predicted |
| B08 | `POST https://api.lever.co/v0/postings/palantir` | refuse | GET only: a POST is how an application is sent | as predicted |
| B09 | `GET https://api.lever.co/v0/postings/palantir/0f0e-not-real/apply` | refuse | an apply page is not a board listing | as predicted |
| B10 | `GET mailto:recruiter@example.com` | refuse | the agent never sends email | as predicted |
| B11 | `GET https://boards-api.greenhouse.io/v1/boards/../jobs` (and `%2e%2e`) | refuse | a board name is letters, digits and hyphens only | as predicted |
| B12 | `GET https://api.ashbyhq.com:8443/posting-api/job-board/linear` | refuse | port 443 only | as predicted |
| B12b | `GET https://API.LEVER.CO/v0/postings/palantir?mode=json` | allow | host names are not case-sensitive, so this is the same host | as predicted |
| B12c | `GET https://api.lever.co/v0/postings/palantir?mode=json&token=x` | refuse | only the query parameters each board needs | as predicted |
| B13 | write a new file `jobs/raw/new.body.gz` | allow | a new file inside `jobs/` | as predicted |
| B14 | write `jobs/../config/boards.json` | refuse | `..` resolves to `config/`, outside `jobs/` | as predicted, **but for the wrong reason**: `boards.json` exists, so "written once" refused it first. Found when W3 was not caught. A second case, `jobs/../config/new.json` (does not exist), was added: refused, by the folder check |
| B15 | write `jobs-evil/x.json` (a real folder next to `jobs/`) | refuse | the prefix trick: the name starts with `jobs` but the folder is not inside `jobs/` | as predicted |
| B16 | write `jobs/link-out/x.json`, where `jobs/link-out` is a symbolic link to a folder outside | refuse | resolved, the path is outside `jobs/` | as predicted |
| B17 | write `jobs/raw/sneaky.json`, a symbolic link to `persona/p.json` | refuse | resolved, the path is the persona file | as predicted |
| B18 | **read** `persona/p.json` | allow | reads are allowed inside `persona/` | as predicted |
| B19 | **write** `persona/p.json` | refuse | the same file as B18, but a write: writes go to `jobs/` only | as predicted |
| B20 | read `config/boards.json`, then write it | read allow, write refuse | config is read-only to the agent | as predicted |
| B21 | read `../outside/secret.txt`, `jobs/link-out/secret.txt`, `~/.ssh/id_rsa` | refuse | reads stay inside this folder, after resolving links | as predicted |
| B22 | write over the existing `jobs/raw/old.body.gz` | refuse | evidence is written once | as predicted |
| B23 | state write for `greenhouse/anthropic` that only adds ids | allow | an update that keeps every seen id | as predicted |
| B24 | state write for `greenhouse/anthropic` that **drops** ids, no approval | needs approval (so refused) | a reset needs my approval | as predicted |
| B25 | the same as B24, with `--approve-state-reset greenhouse/anthropic` | allow | I approved that board for that run | as predicted |
| B26 | a reset of `lever/palantir`, when only `greenhouse/anthropic` was approved | needs approval (so refused) | an approval covers only the board it names | as predicted |
| B27 | append to this run's trace file; append to an old raw file | allow; refuse | append only to a file this run created | as predicted |
| B28 | a state write to `jobs/raw/x.json` | refuse | state files live in `jobs/state/` only | as predicted |

Three more tests in the same file (`ToolsGoThroughThePolicy`) check that a refusal stops the tool itself: a refused write leaves the folder empty, a refused fetch never reaches the network function, and a refused state reset leaves the state file byte for byte the same.

The redirect case is a loop test, because the loop has to decide what to do with a redirect: `tests/test_loop.py`, `Redirects`. Predicted: a redirect to `https://evil.example/jobs` is not followed, and the board fails with `refused_redirect`.

## Wrong versions of the policy

`tests/test_wrong_versions.py` swaps in each wrong version from GATE.md section 6 and checks that the boundary test above **fails** on it:

| Wrong version | Test that must fail on it |
|---|---|
| W1 folder check by string prefix | B15 |
| W2 folder check before resolving symbolic links | B16 |
| W3 folder check before resolving `..` | B14 |
| W4 host check by "ends with" | B04 |
