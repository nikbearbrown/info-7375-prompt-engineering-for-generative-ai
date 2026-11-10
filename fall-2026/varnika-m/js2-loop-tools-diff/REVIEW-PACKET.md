# Review packet — one change I asked Claude Code to make

**The change:** make the agent's only network tool, `tools.http_transport`, keep its timeout while it reads a response body.
**Patch:** commit `91bfbda` (one file, `agent/tools.py`, +17 −2). **Test written before it:** commit `8ddfec0`.

## 1. The defect, reproduced first

GATE.md section 2 gives each request "30 s, or the seconds left in the run if fewer", and wrong version W12 says a request is never given more seconds than are left. The loop passes the right timeout: `test_a_request_never_gets_more_seconds_than_are_left` checks that. But that test uses a fake network, so it only proves the loop *asks* for the right timeout. It cannot show what the real network code does with it.

The real code set a socket timeout and then read the body with `response.read(65536)`. That call waits until it has 65,536 bytes, or the whole `Content-Length`, and the deadline was checked only **between** reads. A server that sends a byte every 0.25 s never trips a 1 s socket timeout, and the deadline check never runs.

**Reproduction.** `tests/test_transport_deadline.py` starts a server on `127.0.0.1` (no outside network) that sends a 200-byte body one byte every 0.25 s, which takes 50 s, and calls `http_transport(url, timeout=1.0, ...)` in a thread.

- **Predicted, before running:** the call is still running after 6 s, so the test fails.
- **Claude Code ran it** at 21:31 UTC, before the test was committed: 1 FAIL, 2 ok, `Ran 3 tests in 6.025s` ([review/1-before-patch-claude-run.txt](review/1-before-patch-claude-run.txt)).
- **I ran it myself** in my own terminal, at `8ddfec0`, before the patch existed: the same 1 FAIL, `AssertionError: True is not false : http_transport was still reading after 6 s with timeout=1.0`, `Ran 3 tests in 6.027s` ([review/2-before-patch-varnika-run.txt](review/2-before-patch-varnika-run.txt)).

The test file has three tests. Only `test_slow_trickle_body_stops_at_the_timeout` is about the defect. The other two, a quick 5,000-posting body returned byte for byte and the byte budget on a real socket, were predicted to pass before and after. They are there so a patch cannot "fix" the timeout by breaking normal reads.

**Order in git:** the test commit `8ddfec0` (16:31:46 −0500) comes before the patch commit `91bfbda`. Nothing in `tests/` changed in the patch commit.

## 2. The diff, read as a change in behavior

`git diff 8ddfec0 91bfbda -- agent/tools.py`:

| | Before | After |
|---|---|---|
| How the body is read | `response.read(65536)`: waits for 65,536 bytes or the whole body | `read1(65536)`: returns after **one** read from the socket, with whatever has arrived |
| When the deadline is checked | between reads, which a slow body never reaches | before **every** read, and each read happens at least once per arriving packet |
| The socket timeout during the body | the full per-request timeout, every read | **the time left before the deadline**, reset before each read |
| Slow-trickle body, `timeout=1.0` | read for 6+ s (50 s in total) and was then accepted | `FetchError("timeout")` after about 1 s |
| A normal body | returned | returned, byte for byte (test 2) |
| A body over the byte budget | `too_large` | `too_large` (test 3) |
| An error status (404) | body returned | body returned. Checked by hand on a local 404 server: `_socket_of` found the socket inside the `HTTPError` |

The new helper `_socket_of` reaches the socket through `response.fp.raw._sock`. That attribute is **private** to Python's `http.client`. If a future Python renames it, `_socket_of` returns `None` and the code silently falls back to the old per-read socket timeout. `read1` still makes the deadline check run, but one read could again last a full timeout past the deadline. No test fails in that case.

## 3. Did the change stay in scope?

Yes, by `git diff --stat 8ddfec0 91bfbda`: one file, `agent/tools.py`, 17 insertions and 2 deletions, all inside `http_transport` plus the new `_socket_of` helper above it. No test, no policy, no loop code, and no GATE.md budget changed. The policy check in `tools.fetch` is untouched, and so is the full suite: 96 tests, OK.

It does **not** fix the slow headers case (section 5). That is outside what I asked for.

## 4. Commands

**Run by me (Varnika), in my own terminal:**

| When | Command | Result |
|---|---|---|
| before the patch, at `8ddfec0` | `python3 -m unittest tests.test_transport_deadline -v` | 1 FAIL, 2 ok, 6.027 s |
| after the patch, at `91bfbda` | `python3 -m unittest discover -s tests -t .` | `Ran 96 tests … OK` |
| after the patch | `git diff 8ddfec0 91bfbda -- agent/tools.py` | read the diff (section 2) |
| after the patch (HEAD `a852e45`) | `python3 -m agent.loop`: live run 2, `2026-11-10T214509Z` | `exit incomplete`. All three real boards `ok` over **HTTPS** through the patched code, which the test does not cover. The deliberate 404 was not retried ([review/6-after-patch-varnika-run.txt](review/6-after-patch-varnika-run.txt)). This run's Anthropic `gone: 78` is wrong, from a separate bug (REVIEW-FINDINGS.md row 7b), not from this patch |

**Run by Claude Code** (outputs saved in `review/`):

| Command | Result |
|---|---|
| `python3 -m unittest tests.test_transport_deadline -v`, before the patch | 1 FAIL, 2 ok |
| the same, after the patch | 3 ok, 1.028 s ([review/3-after-patch-claude-run.txt](review/3-after-patch-claude-run.txt)) |
| `python3 -m unittest discover -s tests -t .`, after the patch | 96 tests, OK |
| a local 404 server through the patched `http_transport` | `404 b'{"status":404,"error":"Job not found"}'`, socket found |
| `python3 review/slow_headers_experiment.py "$PWD"`, on the patched code | slow headers: still running after 5 s, finished after 21.0 s ([review/4-still-missed-slow-headers.txt](review/4-still-missed-slow-headers.txt)) |

## 5. One case my test still misses

**Slow headers.** The new test only slows the **body**. A server that sends the status line and headers one byte every 0.3 s keeps `opener.open()` busy until the headers end, because each byte arrives inside the socket timeout, and the deadline is checked only after the headers. On the patched code, a request with `timeout=1.0` ran for **21.0 s** before it failed with `timeout` ([review/4-still-missed-slow-headers.txt](review/4-still-missed-slow-headers.txt)). The same goes for a slow DNS lookup and a slow TLS handshake, which `urllib`'s timeout does not bound as a whole. I did not try those.

Also not exercised by the test: HTTPS. The test server is plain HTTP on `127.0.0.1`, so the `_sock` path under an SSL socket was not tested by it.

## 6. My decision

*(For me to fill in: ACCEPT, REVISE or REJECT, and the evidence for it.)*

**Evidence to weigh:**

- **For accepting:**
  - The defect reproduced on my machine, before the patch, by a test committed before the patch.
  - That test passes after it, and the two guard tests still pass.
  - The suite is 96/96.
  - The change is one function.
- **Against, or for revising:**
  - It depends on a private attribute, with a silent fallback.
  - It is not tested over HTTPS.
  - The slow-headers gap remains: 21 s for a 1 s timeout.

**Decision:** ____________  **Why:** ____________  **Signed:** ____________ (name, date)
