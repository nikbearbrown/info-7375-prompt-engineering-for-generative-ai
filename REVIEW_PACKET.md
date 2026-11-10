# Review packet: `check_url` accepted a non-443 port and user information

**The change I asked Claude Code to make:** close the gap in JS1's `fetch.check_url`, which JS2's `policy.check_url` reuses. It compared
only the hostname, so `https://boards-api.greenhouse.io:8443/…` and `https://user:pw@boards-api.greenhouse.io/…` passed. GATE.md
section 5 requires port 443 only and no user information. This is a real defect in my JS1 code, not one planted for the review.

**What Claude was asked, and what it replied (2026-11-10, Claude Code, model Opus 5.5).** I didn't write a separate prompt for this patch.
The instruction was my session message "make everything that is left to be done now" (later "except the submission part, build
everything"), on top of GATE.md's written plan ("My proposed Claude Code change fixes a real JS1 defect … Before the patch, I will save
the reproduction and commit a failing regression test"). Claude's reply for this step was the patch below and its commit message
(`afb3877`). That is a weakness in this packet: a narrower prompt would make the scope easier to judge.

## 1. The defect reproduced, before any patch

Commit `58ce031` changed no code. It ran [review/reproduce_port_userinfo.py](review/reproduce_port_userinfo.py) at the build commit
`6c82b59` ([review/01_reproduce_before_patch.txt](review/01_reproduce_before_patch.txt)):

```
expected deny   policy.check_url -> ALLOWED  <-- DEFECT  https://boards-api.greenhouse.io:8443/v1/boards/samsara/jobs
expected deny   policy.check_url -> ALLOWED  <-- DEFECT  https://user:pw@boards-api.greenhouse.io/v1/boards/samsara/jobs
expected deny   policy.check_url -> ALLOWED  <-- DEFECT  https://user@api.lever.co/v0/postings/palantir?mode=json
3 URL(s) decided against GATE.md section 5
```

## 2. The test written before the patch

- `test_W4_port_refused` and `test_W4_userinfo_refused`, plus boundary cases B03 and B04 with their predictions, were committed in
  `e51d208`, **before any JS2 code existed**.
- At the build commit they failed, and only they failed. See [evidence/tests/02_after_build.txt](evidence/tests/02_after_build.txt)
  (5 failures: W4 × 3 subtests, B03, B04) and
  [review/02_failing_tests_before_patch.txt](review/02_failing_tests_before_patch.txt).

## 3. The diff, read as a change in behavior

[review/03_patch.diff](review/03_patch.diff), commit `afb3877`, `jsagent/fetch.py` only, +9 lines, nothing removed:

```diff
+    if "@" in parts.netloc:
+        raise HostNotAllowed(f"refusing URL with user information (host {parts.hostname})")  # credentials kept out of logs
+    try:
+        port = parts.port
+    except ValueError:
+        raise HostNotAllowed(f"refusing URL with an invalid port (host {parts.hostname})") from None
+    if port not in (None, 443):
+        raise HostNotAllowed(f"refusing port {port}: only 443 is allowed (host {parts.hostname})")
```

**Before:** a URL passed if its scheme was `https` and its hostname was on the list.
**After:**
- Any URL whose network location contains `@` is refused, with or without a password.
- A port other than 443 is refused.
- A port that isn't a valid number (`:abc`) is refused instead of crashing.
- `:443` and no port still pass.
- The error message names the host but never echoes the credentials.

Because `AllowListRedirectHandler` and the JS2 `PolicyRedirectHandler` both call the same check, **redirect hops get the same rule**.
That's a second behavior change I need to accept knowingly.

## 4. Did it stay in scope?

- `git show --stat afb3877` lists only `jsagent/fetch.py` among the code (plus the review output files).
- No test was edited.
- No config, allow-list or budget changed.
- The `urlsplit` import already existed.
- The 75 JS1 tests still pass: the JS1 checks for plain HTTP, lookalike hosts and redirects are unchanged.

## 5. Commands run, and their results

Claude ran these on 2026-11-10 (outputs saved in `review/`):

| Command | Result |
|---|---|
| `python3 review/reproduce_port_userinfo.py` (before) | 3 URLs against the gate, exit 1 |
| `python3 -m unittest tests.test_js2_wrong_versions.TestNetworkWrongVersions -v` (before) | 3 of 4 failed |
| `python3 review/reproduce_port_userinfo.py` (after) | 0 URLs against the gate, exit 0 |
| `python3 -m unittest discover -s tests -t .` (after) | 113 tests OK |
| `python3 scripts/boundary_report.py` (after) | 18/18 match |
| `python3 scripts/sabotage_check.py` | W4 planted back means its tests turn RED |

**Commands I ran myself (Ethan):** *to fill in after running them: paste the date and the last line of each.*

```bash
git show afb3877 -- jsagent/fetch.py
python3 review/reproduce_port_userinfo.py
python3 -m unittest discover -s tests -t .
python3 scripts/sabotage_check.py
```

## 6. Decision

**Accept / revise / reject:** ____ *(Ethan's decision, with the evidence it rests on)*

The evidence points to **accept**:
- the defect was reproduced before the patch
- the tests were written first and failed for the right reason
- the patch touches one function
- every test passes after it
- putting W4 back turns its tests red again

## 7. One case my test would still miss

**A proxy.** `urllib`'s default opener reads `HTTPS_PROXY` from the environment. With it set, a URL that passes `check_url` is sent to the
proxy host, which is not on the allow-list. The tests check the URL string, not where the connection actually goes. The fix would be
to build the opener with an empty `ProxyHandler({})` and test it. I'm leaving that as a known gap, and it is in the sign-off's Not
checked list.
