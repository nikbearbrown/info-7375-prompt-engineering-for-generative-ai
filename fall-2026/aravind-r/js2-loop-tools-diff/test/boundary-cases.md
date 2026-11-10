# Boundary cases — predicted policy outcomes

These are **predictions recorded before execution**, not observed test results. Test `src/policy.mjs` against these rows in an isolated test fixture, and only then populate the result column with `PASS`/`FAIL`, the command, and evidence location. Do not mark a result as passing just because the specification predicts it.

`allow` = policy authorizes action; `deny` = categorically prohibited; `ask` = an in-scope guarded write requiring explicit one-time approval. Without `--approve <path>`, runtime `ask` is refused and logged. A CLI/config violation before starting the loop results in `error`, exit `12`.

| # | Kind | Request or scenario | Predicted | Why / setup | Actual result (after run) |
|---|---|---|---|---|---|
| 1 | net | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | allow | Exact HTTPS/GET/host/path/query match | Not run |
| 2 | net | GET `https://api.lever.co/v0/postings/spotify?mode=json` | allow | Exact HTTPS/GET/host/path/query match | Not run |
| 3 | net | GET `https://example.com/jobs` | deny | Host off-list | Not run |
| 4 | net | GET `https://boards-api.greenhouse.io.evil.example/v1/boards/stripe/jobs` | deny | Domain suffix trick; no substring matching | Not run |
| 5 | net | GET `http://boards-api.greenhouse.io/v1/boards/stripe/jobs` | deny | Scheme must be HTTPS | Not run |
| 6 | net | POST `https://api.lever.co/v0/postings/spotify/123/apply` | deny | POST prohibited; application endpoint not allow-listed | Not run |
| 7 | net | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123/questions` | deny | Extra path segment | Not run |
| 8 | net | Allow-listed GET receives 301 pointing to `https://evil.example/` | deny | Stub fetch to return HTTP 301 with `Location`; assert `redirect: 'manual'`, **no** follow-up fetch. Do not use an off-list local mock server. | Not run |
| 9 | net | GET `https://user:pw@api.lever.co/v0/postings/spotify` | deny | URL credentials prohibited | Not run |
| 10 | write | Create `out/traces/run.json` | allow | Inside canonical `out/`; test with fixture | Not run |
| 11 | write | Create `out/../boards.json` | deny | `..` escapes `out/` | Not run |
| 12 | write | Create `out-evil/x.json` alongside `out/` | deny | Sibling prefix trick | Not run |
| 13 | write | Create `out/link/x.json` where `out/link` → an external temp directory | deny | Create test-time symlink then use `realpath` on existing ancestor. On macOS `/tmp` may resolve to `/private/tmp`; resolve the actual target. | Not run |
| 14 | read | Read `boards.json` inside project | allow | In-project read allowed | Not run |
| 15 | write | Overwrite `boards.json` | deny | Outside writable `out/` | Not run |
| 16 | read | Read `path.join(os.homedir(), '.ssh', 'id_ed25519')` | deny | Absolute home path outside project; **not** literal `~/.ssh/...` (Node doesn't expand `~`) | Not run |
| 17 | write | Delete existing `out/state/gh-stripe.json` without approval | ask | Guarded deletion; use isolated fixture state file | Not run |
| 18 | write | Overwrite `out/state/gh-stripe.json` with a **smaller seen-ID set**, without approval | ask | Append-only invariant; seed prior ID fixture | Not run |
| 19 | net | Open `mailto:recruiter@example.com` | deny | No email, login, or non-HTTPS protocol | Not run |
| 20 | net | POST `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | deny | Method restriction also covers Greenhouse | Not run |
| 21 | net | GET `https://jobs.lever.co/spotify/123/apply` (posting `applyUrl`) | deny | Different host; posting application links forbidden | Not run |
| 22 | net | GET `https://boards-api.greenhouse.io/v1/boards/%2e%2e/jobs` | deny | Encoded dot segment/token fails raw-token validation. Check raw path **before** URL parser can normalize it. | Not run |
| 23 | net | GET `https://BOARDS-API.GREENHOUSE.IO/v1/boards/stripe/jobs` | allow | DNS hostnames are normalized to lowercase, then matched exactly | Not run |
| 24 | net | GET `https://boards-api.greenhouse.io./v1/boards/stripe/jobs` | deny | Trailing-dot hostname not allowed | Not run |
| 25 | net | GET `https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs` | deny | Non-default HTTPS port | Not run |
| 26 | net | Allow-listed GET with `Authorization: Bearer test` | deny | Credential header prohibited; test uses fake string | Not run |
| 27 | write | Delete `out/state/gh-stripe.json` with `--approve out/state/gh-stripe.json` | allow | Same fixture as 17; explicit single-use in-scope approval. Policy-test only, or clean isolated test file. | Not run |
| 28 | read | Read `out/state/gh-stripe.json` | allow | In-project read; pairs with guarded write tests | Not run |
| 29 | write | Shrink `out/state/gh-stripe.json` with matching `--approve` | allow | Explicit exceptional approval; only a dedicated disposable state fixture | Not run |
| 30 | write | **Second guarded delete of the same canonical `out/state/gh-stripe.json` path in the same run**, after row 27 consumed its `--approve` | ask | Restore only the disposable fixture through an ordinary allowed create between the two deletes; the matching approval token has already been consumed, so it cannot authorize a second guarded mutation | Not run |
| 31 | CLI | `--max-requests 2` with 4 distinct boards | allow | Lower hard limit; expected overall run `budget-exhausted`, exit 11, with unattempted boards | Not run |
| 32 | CLI | `--max-requests 20` | deny | Above hard maximum 8; reject before network, exit 12 | Not run |
| 33 | CLI | `--judge claude` | deny | JS2 allows only `--judge none`; no judge subprocess | Not run |
| 34 | net | Stub HTTP 429 with `Retry-After: 30` | deny retry | Record `rate-limited`, no second request | Not run |
| 35 | net | Stub HTTP 429 with `Retry-After: 2` and available budget | allow one retry | Retry delay comes from header and is limited to one attempt | Not run |
| 36 | net | Allowed GET begun with 3 s wall-clock remaining | allow, capped at 3 s | Timeout is `min(15 s, remaining time)` and aborted at remaining deadline | Not run |
| 37 | write | Delete `out/state/gh-airbnb.json` in a run with `--approve out/state/gh-stripe.json` | ask | Fresh isolated fixture with **unconsumed** approval for a different canonical path; proves path binding separately from row 30's single-use behavior | Not run |
| 38 | read | `--replay out/raw/lv-spotify.json` with a valid single-board `lv-spotify` fixture | allow | Read is contained under `out/raw/`, trace must state `mode: replay`, and stubbed network counter stays at zero | Not run |
| 39 | read | `--replay out/raw/../state/lv-spotify.json` | deny | Replay files must be located under `out/raw/`, not merely inside the project | Not run |
| 40 | read | `--replay out/raw/escape.json` where `escape.json` is a symlink to a file outside `out/raw/` | deny | Check canonical/real target paths; fixture symlink created during test | Not run |
| 41 | CLI | `--replay out/raw/missing.json` with a valid single-board config | deny | Missing replay file is a run `error`, exit 12; no fallback HTTP request | Not run |
| 42 | net | GET `https://evilboards-api.greenhouse.io/v1/boards/stripe/jobs` | deny | **Added 2026-11-10 after mutant `wv01-host-endsWith` survived** (no prior row tested a host ending in an allowed host). Exact match required. | Not run |
| 43 | net | Stubbed HTTP 404 on an allow-listed board | deny retry | **Added 2026-11-10 after mutant `wv07-404-retried` survived.** Exactly one request; board `error: not found`. | Not run |

## Testing setup and interpretation

- **Predictions come first.** Do not replace them with post-hoc rationalizations. Enter actual policy return and a test-log/trace pointer in the last column **after running**.
- Cases **8, 34, 35 and 36** require a stubbed fetch and, for the time case, a controllable clock/abort signal. The stub must not create an unrestricted real network entry point. For case 8, assert that no second fetch happens.
- Cases **13, 17, 18, 27, 29, 30, 37 and 40** require a temporary, isolated directory tree. Set up the outside symlink and existing state **during** the test; do not touch the actual submission's persisted state.
- For file decisions, test both canonical in-scope path handling and a prospective path whose leaf does not exist. Resolve existing ancestors with `realpath`; a lexical `path.resolve` check alone is insufficient for symlinks.
- Case **22** needs a **raw-string guard** before `new URL()` normalizes encoded traversal. A parser that strips `%2e%2e` and then rejects an unexpected path happens to deny this example, but does not prove the promised token validation.
- Greenhouse raw IDs may be numeric; the independent checker and patched `src/state.mjs` normalize them to canonical string IDs. Lever UUIDs must remain strings (never `Number(uuid)`). Duplicate IDs **within one raw response** cause board `error: malformed` with **no state update**, not deletion of the duplicate alone; corrupt persisted state is an integrity `error`.
- Case **30** uses the same in-memory approval state as case **27**. Recreate only the disposable file before retrying its deletion; starting a new run or choosing a different file would **not** demonstrate consumption. Case **37** tests the separate path-binding guarantee.
- For the finished-wrong demonstration, preserve a fresh-state baseline, then a **second run using `--replay <path>` on the identical saved raw response**. Mark the second run `mode: replay` in both the trace and `README.md`; only the second run's repeated `84 new` is the wrong new-job answer. **Checker rule 3 catches the corrupt `[null]` state; rule 2 by itself agrees with the false count because its pre-run seen set is already corrupt.** Run the independent checker after the replay. The pre-patch `src/state.mjs` is the JS1 version under review.
- Cases **38–41** specify the `--replay` file boundary and zero-network behavior. Use a valid single-board configuration for each, and assert **zero fetches** even on invalid paths or missing files. Case 41 is a CLI run error, rather than a normal permission `ask`.
- Cases **31–33** are CLI-level rather than file/network authorizations. Their `allow`/`deny` predictions refer to accepting or rejecting the command; the expected **run exit** is stated separately.
- A case that returns `ask` should test the actual no-approval runtime behavior (**refused**) and the matching approval behavior (**allowed**) separately.

## Run evidence to add

Record the test command(s), timestamp, platform/Node version, test suite output, observed versus predicted outcome for each case, and the resulting commit hash. Until then, the table is a test plan, not proof of code enforcement.
