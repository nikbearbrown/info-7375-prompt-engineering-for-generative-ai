# POLICY.md: permission policy and boundary tests

The full policy is in GATE.md, section 5. It is enforced in jobwatch/policy.py, and every tool in jobwatch/tools.py calls policy.check() before it touches the network or disk.

## How to read the table

- Expected (Deepak): my prediction, written and committed before the tests ran. One of ALLOW, DENY or NEEDS_APPROVAL, plus a few words of reason.
- Actual (pytest): filled from real pytest output after the run.
- A mismatch between Expected and Actual is reported, not edited away. If my prediction was wrong, I say so in FRICTIONAL.md.
- B05: no tool can send POST, so B05 is tested by calling policy.check(method="POST", ...) directly.
- B06: no real 3xx appeared in evidence/manual-capture/CAPTURE.md, so B06 uses a SEEDED mock transport.


## Boundary cases

Actual (pytest) source: `evidence/pytest/20261110T195646Z-full-v.txt` (2026-11-10 19:56 UTC, 14:56 ET; first filled from `evidence/pytest/20261110T193805Z-full-v.txt`, same B lines); each B test prints its policy decision and outcome, shown with `-rP`.

| ID | Request | Kind | Expected (Deepak) | Actual (pytest) | Test |
|---|---|---|---|---|---|
| B01 | GET https://example.com/x | fetch | DENY — Host is not allowlisted. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B01_off_allowlist_host |
| B02 | GET https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs | fetch | DENY — Hostname suffix does not match the trusted domain. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B02_suffix_trick_host |
| B03 | GET https://boards-api.greenhouse.io@evil.com/ | fetch | DENY — Userinfo confusion; actual destination is evil.com. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B03_userinfo_trick |
| B04 | GET http://boards-api.greenhouse.io/v1/boards/stripe/jobs | fetch | DENY — Plain HTTP is not permitted. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B04_plain_http |
| B05 | POST https://api.lever.co/v0/postings/x (via policy.check) | fetch | DENY — POST is not an approved fetch method. | policy DENY (policy.check with method POST); no tool can send POST. PASSED | test_B05_post_to_allowed_host |
| B06 | an allowed host answers 302 (SEEDED mock transport) | fetch | DENY — Redirects are not trusted; destination must be revalidated. | policy ALLOW (GET); outcome redirect refused: 302 returned and not followed (Location never opened), board FAILED redirect_refused. PASSED | test_B06_redirect_refused |
| B07 | write runs/../outside.txt | write | DENY — Path traversal escapes the permitted directory. | policy DENY; outcome PolicyDenied raised, nothing written. PASSED | test_B07_dotdot_escape |
| B08 | write runs-evil/x.json beside runs/ | write | DENY — Sibling directory is outside the runs/ boundary. | policy DENY; outcome PolicyDenied raised, nothing written. PASSED | test_B08_prefix_trick |
| B09 | write through a symlink in runs/ that points outside the folder | write | DENY — Symlink resolves outside the JS2 folder. | policy DENY; outcome PolicyDenied raised, nothing written. PASSED | test_B09_symlink_escape |
| B10 | write /tmp/x.json | write | DENY — Resolved /private/tmp path is outside the JS2 folder. | policy DENY; outcome PolicyDenied raised, nothing written. PASSED | test_B10_absolute_path |
| B11 | read config/boards.json | read | DENY — Configuration read is not covered by the verification exception. | policy ALLOW; outcome bytes returned. PASSED | test_B11_read_config |
| B12 | write config/boards.json, non-interactive | write | NEEDS_APPROVAL — Protected configuration write in non-interactive mode. | policy NEEDS_APPROVAL; outcome denied (non-interactive), file unchanged, needs_deepak true. PASSED | test_B12_write_config |
| B13 | reset state/seen.json, non-interactive | write | NEEDS_APPROVAL — Destructive state reset in non-interactive mode. | policy NEEDS_APPROVAL; outcome denied (non-interactive), state unchanged, needs_deepak true. PASSED | test_B13_state_reset_noninteractive |
| B14 | read ~/.ssh/id_rsa | read | DENY — Private SSH key is sensitive credential material. | policy DENY; outcome PolicyDenied raised, file not opened. PASSED | test_B14_read_home_secret |
| B15 | GET https://api.ashbyhq.com:8443/posting-api/job-board/x | fetch | DENY — Non-standard port 8443 is not allowlisted. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B15_nonstandard_port |
| B16 | GET https://203.0.113.10/v1/boards/stripe/jobs | fetch | DENY — IP-literal destination bypasses hostname-based trust matching. | policy DENY; outcome PolicyDenied raised, no request sent. PASSED | test_B16_ip_literal |
