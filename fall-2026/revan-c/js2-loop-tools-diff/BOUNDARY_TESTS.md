# Permission policy and boundary tests — Job-Search Agent 2

The policy is [GATE.md](GATE.md), "Permission policy". It is enforced in code, not in a prompt:

| Boundary | Where it is enforced | How |
|---|---|---|
| Network | `jsloop/policy.py` `check_request`, called in preflight, again before each request, and again inside the tool `jsloop/fetch.py` `http_get` | Method must be `GET`; scheme `https`; no credentials; hostname exactly `boards-api.greenhouse.io` or `api.lever.co`; no explicit port; the whole URL must equal one of GATE.md's four URLs; the fourth only in demonstration mode |
| Redirects | `jsloop/fetch.py` | `http.client` sends one request and never follows a redirect; a 3xx is recorded as a failed board |
| File reads | `jsloop/policy.py` `Workspace.check_read` | Only `resumes/aarav-patel.json`, `state/js2/`, and `fixtures/js2/` |
| File writes | `jsloop/policy.py` `Workspace.check_write` | Only `evidence/js2/` and `runs/js2/`; `state/js2/` only with `--approve-state-write`. Paths are resolved with `os.path.realpath` (symlinks followed) and compared by path components (`Path.is_relative_to`), never by string prefix. New files open with `O_EXCL | O_NOFOLLOW` |
| Never | by construction | There is no tool that sends anything but a GET to the four URLs: no POST, no form, no login, no email or message |

## Predicted cases and results

**Predictions** are copied from GATE.md, written by Revan and committed in `f3072e5` before any JS2 code existed.
**Tests** were written by Claude Code from those predictions and committed in `e7493d7`, before the implementation (`ac2827a`).
**Results:** run by Claude Code with `.venv/bin/python -m pytest -v tests/test_js2_boundary.py` on 2026-11-10 at 06:09Z: every case below passed. Revan’s own run: 2026-11-10, between 06:46 and 07:03 UTC, .venv/bin/python -m pytest -q: 110 passed, which includes every boundary test above. Output in review_evidence/post_patch_commands.txt.

| ID | Attempt | Predicted (GATE.md) | Test | Result | Agrees? |
|---|---|---|---|---|---|
| B01 | GET the exact Klaviyo URL | Allow and count one request | `test_B01_klaviyo_get_allowed_and_counted` | Allowed; 1 request counted | yes |
| B02 | GET the exact Patch My PC Lever URL | Allow and count one request | `test_B02_lever_get_allowed_and_counted` | Allowed; 1 request counted | yes |
| B03 | GET `https://example.com/jobs` | Deny: host off the allow-list | `test_B03_host_off_allow_list_denied` | Denied, rule `host` | yes |
| B03a | GET `https://boards-api.greenhouse.io.evil.com/...` | Deny: look-alike host | `test_B03a_look_alike_host_denied` (+2 EXTRA variants: `evil-boards-api.greenhouse.io`, `api.lever.co.evil.com`) | Denied, rule `host`, all 3 | yes |
| B04 | GET the Greenhouse host with an unlisted slug | Deny: endpoint off the exact allow-list | `test_B04_unlisted_endpoint_on_allowed_host_denied` (+3 EXTRA: query dropped, fragment added, an `/apply` path) | Denied, rule `endpoint`, all 4 | yes |
| B05 | POST to an allowed URL | Deny: method is not GET | `test_B05_non_get_method_denied` (also PUT, PATCH, DELETE) | Denied, rule `method`, all 4 | yes |
| B06 | Allowed path over HTTP, or with a nonstandard port | Deny: scheme or port differs | `test_B06_scheme_port_or_credentials_differ_denied` (+1 EXTRA: `user:pw@` in the URL) | Denied: `scheme`, `port`, `credentials` | yes |
| B07 | An allowed URL redirects elsewhere | Deny the redirect; make no second request | `test_B07_redirect_is_refused_and_not_followed` | 302 recorded as failure; one connection, one request; run `incomplete` | yes |
| B08 | Write `runs/js2/../outside.json` | Deny: escapes the output folder | `test_B08_dotdot_escape_denied` | Denied, rule `outside-write-roots`; no file created | yes |
| B09 | Write `runs/js2-evil/result.json` | Deny: sibling prefix is not containment | `test_B09_sibling_prefix_denied` | Denied, rule `outside-write-roots`; no folder created | yes |
| B10 | Write through a symlink in `runs/js2/` pointing outside | Deny: resolved path escapes | `test_B10_symlink_escape_denied` (directory link and file link) | Denied, rule `outside-write-roots`; outside folder still empty | yes |
| B11 | Read an approved seeded fixture | Allow read only; do not grant write | `test_B11_seeded_fixture_read_allowed_but_not_write` (+EXTRA `test_B11_read_outside_read_roots_denied`) | Read returned the bytes; write check denied | yes |
| B12 | Write to that fixture | Deny: read permission is not write permission | `test_B12_write_to_seeded_fixture_denied` | Denied, rule `read-only`, even with the state flag; bytes unchanged | yes |
| B13 | Run without `--approve-state-write` | Allow observation and trace; deny any state write; `state_updated: false` | `test_B13_run_without_approval_observes_but_never_writes_state` | 3 requests, trace saved, no state file; direct state write denied, rule `needs-approval` | yes |
| B14 | Write `state/js2/seen_ids.json` with the flag | Allow if the resolved path stays in `state/js2/` | `test_B14_state_write_with_approval_allowed_inside_state` | Written; `state/js2/../escaped.json` still denied with the flag | yes |
| B15 | Select the deliberate-failure URL without demonstration mode | Deny at preflight | `test_B15_deliberate_failure_board_needs_demo_mode` | Denied, rule `demo-only`; run `error`; 0 requests | yes |
| B16 | Start an 8 s request at second 40 | Do not send it; `budget-exhausted` (under 10 s left) | `test_B16_request_not_started_with_under_10_seconds_left` | Not sent; `budget-exhausted`, limit `seconds`; the two remaining boards `not_attempted` | yes |

EXTRA cases were added by Claude Code while writing the tests. They are not in GATE.md's predictions, and they are labeled EXTRA in the test file.
One more EXTRA test sits in `tests/test_js2_loop.py`: `test_output_root_symlinked_outside_repository_is_preflight_error`. If `runs/` itself links outside the repository, the run stops at preflight and fetches nothing.

## Each wrong version is caught

`.venv/bin/python tools/check_wrong_versions_js2.py` builds 17 mutant copies, each with one of GATE.md's wrong versions (or a boundary wrong version) planted, and checks that the named test fails.
Claude Code ran it on 2026-11-10: **17 of 17 caught**. Revan’s own run: 2026-11-10, between 06:46 and 07:03 UTC: 17 of 17 caught. Output in review_evidence/post_patch_commands.txt.

## You can ask the policy directly

These commands only check; they do nothing. Quote URLs: in zsh an unquoted `?` is a filename pattern and the command fails before Python starts.

```bash
.venv/bin/python -m jsloop policy --request GET "https://boards-api.greenhouse.io.evil.com/v1/boards/klaviyo/jobs?content=true"
```

```bash
.venv/bin/python -m jsloop policy --write runs/js2-evil/x.json
```

```bash
.venv/bin/python -m jsloop policy --write state/js2/seen_ids.json
```

Each prints `DENIED (<rule>): ...` and exits 1, or `ALLOW ...` and exits 0.
