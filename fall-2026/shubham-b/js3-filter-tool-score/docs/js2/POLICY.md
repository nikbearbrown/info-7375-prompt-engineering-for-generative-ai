# The permission policy, in code, and its boundary tests

## Where it is enforced

The policy is `GATE.md` §6. It is enforced by the program, not by a prompt: the loop has no
model in it at all (backend `none`), so no text in a job posting can ask it to do anything.

| Tool | Asks the policy | Code |
|---|---|---|
| Fetch | `check_request("GET", url)` before every attempt; then the JS1 `AllowListTransport` checks the URL again at every redirect hop | `watch.LoopFetcher.get`, `http.AllowListTransport` |
| Plan load | The plan file must pass `check_read` *before* it is parsed and must not be anywhere the agent can write; the plan's hosts must be a subset of `policy.HOST_CEILING` and its write root inside `policy.WRITE_CEILING` (`data/watch`), so a plan can narrow the policy but never widen it (A3) | `watch.load_checked_plan`, `watch.build_policy` |
| Plan check | Every planned board's URL and its write folder, before the first request; any refusal ends the loop as `ERROR` with nothing fetched | `watch._Loop.plan_boards` |
| Résumé read | The résumé path must pass `check_read` at loop start (never `private/`), or the loop ends `ERROR` with nothing fetched (A3) | `watch._Loop.run` |
| Write | The loop folder and each board folder must pass `check_write`; inside them, every file goes through `fsio.OutputRoot` (no `..`, no symlinks, atomic) | `watch.run_loop`, `watch.board_config`, `fsio.OutputRoot` |
| Delete | `check_delete` says `NEEDS_APPROVAL`; `settle` asks Shubham on a terminal and treats "no terminal" as no | `watch.reset_board`, `policy.settle`, `watch_cli.cmd_watch_reset` |
| Never-actions | Enforced by the agent **having no tool** that could apply, email, message or log in, and by `check_request` refusing every method but GET (B06), so no form can be submitted even on an allowed host. `check_action` is the name-level refusal list (B19); no current tool calls it (stated precisely after the review, A3) | `policy.check_request`; `policy.check_action` |

"Inside" means one thing everywhere: `policy.inside` calls the project's single containment
check, `fsio.relative_within`, which resolves symlinks and compares path components, never
string prefixes. Host checks call the JS1 `http.check_url` (exact host, HTTPS, port 443, no
userinfo).

## Boundary tests: predicted before running, then run

Predictions are GATE §7, committed in `f524c91` before any JS2 code existed. Results are from
the run saved in [`evidence/boundary-tests.txt`](evidence/boundary-tests.txt) (run by Claude,
2026-11-09). All 38 test cases passed, so every result matched its prediction.

| # | Request | Predicted (GATE §7) | Result | Test |
|---|---|---|---|---|
| B01 | GET Greenhouse Stripe jobs URL | ALLOW | ALLOW | `test_b01_greenhouse_get_allowed` |
| B02 | GET Ashby Ramp board URL | ALLOW | ALLOW | `test_b02_ashby_get_allowed` |
| B03 | GET `https://jobs.lever.co/palantir` | DENY `host` | DENY `host` | `test_b03_host_off_the_allow_list` |
| B04 | GET `boards-api.greenhouse.io.evil.example` (and two substring variants) | DENY `host` | DENY `host` (all 3) | `test_b04_allowed_name_as_prefix_or_substring` |
| B05 | GET over plain `http://` | DENY `scheme` | DENY `scheme` | `test_b05_plain_http` |
| B05+ | userinfo in the URL; port 8443 | (not predicted separately) | DENY `userinfo`; DENY `port` | `test_b05_userinfo_and_port` |
| B06 | POST/PUT/DELETE/PATCH to the Greenhouse apply endpoint | DENY `method` | DENY `method` (all 4) | `test_b06_apply_endpoint_on_allowed_host` |
| B07 | Allowed host redirects to `https://evil.example/` | Refused at the hop; board `FETCH_FAILED` (`REDIRECT_REJECTED`) | As predicted; only the two allowed hosts were ever requested | `test_b07_redirect_off_the_allow_list_fails_the_board` |
| B08 | Write `data/watch/loops/x/trace.jsonl` | ALLOW | ALLOW | `test_b08_write_inside_watch` |
| B09 | Write `data/watch/../live/state.json` | DENY `outside_write_root` | DENY `outside_write_root` | `test_b09_dotdot_escape` |
| B10 | Write `data/watch-evil/x.json` | DENY `outside_write_root` | DENY `outside_write_root` | `test_b10_prefix_trick_sibling` |
| B11 | Write through `data/watch/link` → a folder outside the project | DENY `outside_write_root` | DENY `outside_write_root` | `test_b11_symlink_pointing_out` |
| B11+ | A symlink that stays inside `data/watch`; an absolute `/etc/x.json` | (not predicted separately) | ALLOW; DENY | `test_b11_symlink_inside_watch_is_still_allowed`, `test_b11_absolute_path_outside` |
| B12 | Read `config/watch.toml` | ALLOW | ALLOW | `test_b12_read_the_plan` |
| B13 | Write `config/watch.toml` (same file as B12) | DENY `outside_write_root` | DENY; also `GATE.md`, `data/live/state.json`, source | `test_b13_write_the_plan`, `test_b13_write_gate_and_js1_state` |
| B14 | Read `private/real.resume.json`; `.env` | DENY `private` | DENY `private`; also through a symlink in `data/watch` | `test_b14_read_private_resume`, `test_b14_read_private_through_a_symlink` |
| B15 | Read `/etc/hosts`; `../outside.txt` | DENY `outside_project` | DENY `outside_project` | `test_b15_read_outside_the_project` |
| B16 | Delete a board's `state.json` | NEEDS_APPROVAL | NEEDS_APPROVAL; a delete outside `data/watch` is DENY, not asked | `test_b16_delete_needs_approval`, `test_b16_delete_outside_is_denied_not_asked` |
| B17 | B16 with no terminal, or approval refused | Nothing deleted; DENY `not_approved` | As predicted; the question names the board | `test_b17_no_terminal_means_no`, `test_b17_refused_approval` |
| B18 | B16 with Shubham typing the board key | ALLOW; file deleted | ALLOW `approved`; file gone | `test_b18_approved_delete` |
| B19 | `apply`, `email`, `message`, `login` | DENY `never`, even with approval | As predicted; an unknown action is DENY `unknown_action` | `test_b19_never_actions`, `test_b19_tools_and_unknown_actions` |
| B20 | Third GET of one URL in one loop run | DENY `repeat` | `POLICY_REFUSED` `repeat`; 2 requests reached the transport | `test_b20_third_get_of_one_url_is_refused` |

Added after the independent review (predictions in GATE A3, commit `e1e41b5`, before the tests in
`0c48e2e`; run output [`evidence/boundary-tests-a3.txt`](evidence/boundary-tests-a3.txt), 8 of 8
passed):

| # | Request | Predicted (GATE A3) | Result | Test |
|---|---|---|---|---|
| B21 | A plan allowing `jobs.lever.co` | Refused before any request | `ConfigError` (hosts outside GATE §6) | `test_b21_plan_cannot_add_a_host` |
| B22 | A plan with `write_root = "data"` | Refused | `ConfigError` (inside `data/watch`) | `test_b22_plan_cannot_widen_the_write_root` |
| B23 | A plan file inside `data/watch/` | Refused before parsing | `ConfigError` (agent could write it) | `test_b23_plan_inside_the_write_folder_is_refused` |
| B24 | A plan file in `private/` (not even valid TOML) | Refused before parsing | `ConfigError` (`private`); never parsed | `test_b24_private_plan_is_refused_before_parsing` |
| B25 | A narrower plan (one host, `data/watch/sub`) | Allowed | Allowed, with the narrower hosts and folder | `test_b25_narrowing_is_allowed` |
| B26 | Résumé path in `private/` | Loop `ERROR`, 0 requests | `resume_read_refused:private`, 0 requests | `test_b26_resume_in_private_stops_the_loop` |
| B27 | `reset greenhouse/x/../ashby-ramp` | Refused, nothing asked or deleted | `ConfigError`; approver never called; file intact | `test_b27_reset_refuses_an_unsafe_token` |

Before A3, B21–B23 would have been **allowed**: the independent reviewer showed that a plan
passed with `--plan` could set any host or `write_root = "data"` and so write JS1's
`data/live/state.json`. That is why these cases exist.

The plain CLI path was also tried by hand once: `uv run jsa watch reset greenhouse/ramp
</dev/null` (no terminal) printed `greenhouse/ramp: DENY (not_approved); deleted=False` and
exited 5 (run by Claude, 2026-11-09).

## The wrong versions these tests kill

`tests/meta/test_js2_wrong_versions_caught.py` swaps in each GATE §8 wrong version
(`tests/wrong_versions/js2.py`) and requires `tests/watch` to fail, naming the test that must
catch it. The policy ones: W5 (string-prefix containment) is killed by
`test_b10_prefix_trick_sibling`; W6 (no symlink resolution) by `test_b11_symlink_pointing_out`;
W7 (substring host match) by `test_b04_allowed_name_as_prefix_or_substring`; W9 (delete
without asking) by `test_b17_no_terminal_means_no`.

## Limits

- The policy governs the agent's own requests and files. JS1's `jsa run` still launches the
  `claude` executable for judgments, and this program cannot see or limit that process's own
  network use (`docs/NETWORK.md`). The watch loop does not launch it.
- Approval is "Shubham types the board key at a terminal". The program cannot tell who is
  typing.
- A time-of-check/time-of-use race (a symlink swapped in after `check_write`) is covered by
  `OutputRoot` opening every path component with `O_NOFOLLOW`, not by the policy check itself.
