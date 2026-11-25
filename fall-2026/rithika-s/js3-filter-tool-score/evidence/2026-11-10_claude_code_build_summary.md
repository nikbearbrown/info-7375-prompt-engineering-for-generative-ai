Read the gate docs and all the JS1 code; the 42 JS1 tests pass. Now I'm writing the JS2 config and `policy.py`.

Policy, adapters and transport are written. Next up is the loop itself, the largest piece.

Fixing three issues I spotted on review: redirected final bodies weren't saved, bad replay manifests could crash, and replay-missing was logged as a connection error.

Checker done. Now the tests: a shared offline harness first, then policy, loop, budgets-config and checker tests.

Policy tests pass (19 boundary cases + 12 extras). Writing the loop tests now.

All 46 loop tests pass. Now the budgets-vs-GATE test (W11) and checker tests.

129 tests pass (42 JS1 + 87 new). Now the W1–W11 mutants.

Moving those imports to the top of the file for PEP 8, then writing the mutant tests.

The no-symlink mutants failed every test for the wrong reason, since macOS temp paths run through /var → /private/var. I'm making the mutant naive on both sides instead.

Every mutant is now caught by the test it targets. W7 "ends with" is caught only by an extra test I added, not by B01–B19. Next: CLI tests, then the full suite and a style check.

JS2 is built as GATE.md and BOUNDARY_TESTS.md specify. All 134 offline tests pass: the 42 from JS1 plus 92 new. The suite fails on every mutant from W1 to W11. I didn't commit or make any network request, and I didn't touch GATE.md, BOUNDARY_TESTS.md, JS1_CONTRACT.md or `data/`. No `out/` folder was created in the project, because every test uses a temporary folder.

## Files

**Created**
- [config/boards.json](config/boards.json), [config/budgets.json](config/budgets.json)
- [agent/policy.py](agent/policy.py): `check_request`, `check_redirect`, `check_read`, `check_write`, `request_state_reset`, plus the read/write helpers the loop uses for all file access
- [agent/adapters.py](agent/adapters.py): Greenhouse and Ashby parsers
- [agent/transport.py](agent/transport.py): the real network transport, which does not follow redirects itself, and the replay transport
- [agent/loop.py](agent/loop.py): the loop and the command line
- [checks/__init__.py](checks/__init__.py), [checks/independent_check.py](checks/independent_check.py): imports nothing from `agent/`, and a test checks that
- [tests/js2_harness.py](tests/js2_harness.py) (fake transport, fake clock, made-up responses), [tests/test_policy.py](tests/test_policy.py), [tests/test_loop.py](tests/test_loop.py), [tests/test_budgets_config.py](tests/test_budgets_config.py), [tests/test_independent_check.py](tests/test_independent_check.py)

**Changed**
- [tests/mutants.py](tests/mutants.py), [tests/test_mutants.py](tests/test_mutants.py): the JS1 mutants are unchanged. W1–W11 are added, and each one patches one decision for the length of a test only.

## One gap in your boundary tests
B04 catches a host check by "contains", but **not one by "ends with"**. `boards-api.greenhouse.io.evil.com` doesn't end with an allowed host, so an "ends with" check refuses it anyway. I added `test_extra_host_suffix_trick_refused` (e.g. `evilboards-api.greenhouse.io`), and it is the only test that catches the "ends with" mutant. You may want to add it as B20. I didn't edit the file.

## Ambiguities and the interpretation I chose
1. **Write area:** all of `out/`, not only `out/raw`, `out/state` and `out/runs`. With the narrower reading, B12 (`out/link/x.json`) would be refused by location alone and would no longer test symlinks.
2. **Overwriting vs. updating state:** every file is write-once (`would_overwrite`), except a state file under `out/state/`. That one may be replaced, atomically through a temporary file.
3. **Relative paths,** including `--replay DIR`, are taken from the project root, not the current folder.
4. **"Would exceed" for time:** a request starts only if elapsed time, plus 2 s when it's a retry, plus 20 s fits within 90 s. If every request took the full 20 s, a fifth one (a retry) wouldn't fit. That slightly contradicts the reasoning in §2; in practice the check uses actual elapsed time.
5. **Budget hit while a retry is pending:** the exit is `budget_exhausted` (2), not `incomplete`. That board is reported failed, with new jobs unknown.
6. **More than 4 boards in config** stops the run at startup with `error`, as §2 says. A runtime board check stays as a backstop.
7. **"Nothing written except the trace":** response bodies are held in memory and written only when the run ends without `error`. A run that ends in error therefore keeps no raw bodies, only their size and SHA-256 in the trace.
8. **Redirects:**
   - The target is checked by policy before it is followed.
   - Each hop counts as a request and goes through the repeat rule. At most 3 hops.
   - A target off the allow-list is refused with `redirect_off_allowlist`, which counts as a permission violation, so the whole run ends in `error`.
   - A redirect to `http://` keeps the `not_https` code.
   - Hop bodies are saved as `_a<n>_r<k>.json`.
   - A 3xx with no Location header fails the board with no retry.
9. **A retry goes to the same URL that failed.**
10. **Posting IDs are stored as strings,** since Greenhouse uses integers and Ashby uses UUIDs. A posting without a usable id makes the whole response `malformed_response`.
11. **Carried over from JS1:**
    - The first run with no state file is a baseline: new = 0 and every id is recorded.
    - The state update adds the new ids to the old ones.
    - The résumé is checked at startup, and the report is checked for résumé contact details before it is written.
    - The target file isn't loaded and there are no rule verdicts, because you didn't ask for them.
12. **SEEDED runs use their own state folder, `out/state/seeded/`,** so a replay can never change what a later live run counts as already seen. This is a deliberate departure from `out/state/<board>.json`, and only for replays. To undo it, change the one constant in `loop.py`.
13. **Replay format:** every run writes `out/runs/<id>/replay.json`, so `--replay out/runs/<id>` replays that run, including timeouts and 404s. A folder of `<board>.json` files also works; each one is served as a 200.
    - The replay folder must be inside `data/`, `config/` or `out/`, because policy blocks reads anywhere else.
    - A missing file fails that board as `replay_missing`, with no retry.
14. **Approval:** only `True` or `"yes"` counts as yes (any capitalisation, spaces trimmed). `None`, any other answer, or an exception counts as no. After a yes, `request_state_reset` deletes the file. I added no command-line option for it.
15. **Network rules:**
    - The method must be exactly `GET`, so lowercase `get` is refused.
    - Refused credentials: `Proxy-Authorization` as well as `Authorization` and `Cookie`, and a username or password in the URL.
    - A port other than 443 is refused as `host_not_allowed`.
16. **The checker needs the state from before the run,** because the run updates the state files. The loop saves copies to `out/runs/<id>/state_before/`. Beyond the three required flags, the checker also flags:
    - a recomputed count or new-job count that differs from the summary,
    - a Greenhouse response with no `meta.total`,
    - a succeeded board with no raw file.
17. **Known limit left alone:** a test (`test_known_limit_zero_postings_accepted_as_empty_board`) keeps the agent accepting a 200 with zero postings and ending `finished`. The checker flags that case. The report only restates the limit in a fixed note and doesn't try to detect it.
18. **Extra mutants:** W8 also has "prefix only" and "symlinks only" versions, and W7 has both "ends with" and "contains" versions. W11 is a mutant too, made by pointing the budgets test at a modified copy of the file.

## Commands (from `js2-loop-tools-diff/`)
Full suite:
```bash
python3 -m unittest discover -s tests
```
Mutant check, which shows every W1–W11 mutant failing the suite:
```bash
python3 -m unittest discover -s tests -p 'test_mutants.py' -v
```
Boundary tests B01–B19 one by one, for your "Actual" column:
```bash
python3 -m unittest discover -s tests -p 'test_policy.py' -v
```
When you choose to run it live, then check it and replay it:
```bash
python3 -m agent.loop
```
```bash
python3 -m checks.independent_check out/runs/<run_id>
```
```bash
python3 -m agent.loop --replay out/runs/<run_id>
```