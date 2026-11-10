# Review packet — the User-Agent defect

Tushar Patel · INFO 7375 · November 9, 2026

## Reproduce the failure

My first live run exited `incomplete`, as expected for the deliberate Greenhouse 404. Looking at the board results showed an additional failure. Stripe succeeded, but Notion and Linear each returned HTTP 403 even though both had returned 200 in preflight. The saved Ashby bodies contained `error code: 1010`. [Live run 1 summary](evidence/runs/live-1-ashby-403/summary.json) · [Raw responses](evidence/runs/live-1-ashby-403/raw/ashby/)

I varied the User-Agent with curl. The default curl header got 200, `Python-urllib/3.12` got 403, and `info7375-js2-watch/0.1 (student project; tushar-js2@example.com)` got 200. The pre-patch transport built the Request without an explicit User-Agent. The curl comparison gave me a concrete behavior to change. I added the student-project header to the gate in `20d46dd`, before the patch. [Curl results](evidence/review-packet-ua-repro.txt) · [Gate](GATE.md)

## Run the regression test before the patch

I added `test_ua01_request_sends_agent_user_agent` with help from Claude chat. It runs the transport through a fake HTTPS handler and reads the header from the Request handed to that handler. The exact student-project string was the expected value. Before the patch, the handler saw `None` and the test failed. I saved the failing output and committed the test as `346c2f8` before asking Claude Code for the fix. [Failing test output](evidence/test-runs/ua01-before-patch.txt)

## Read the diff and check scope

Claude Code added `AGENT_USER_AGENT` in `agent/transport.py` and passed it in the Request's headers. The change means the Request carries the student-project identifier before it reaches the opener. The explicit value takes the place of urllib's default in the live client.

I checked the patch against the rule I wrote. It touches only the transport module and leaves the allow-list, redirect handling, deadlines, and error handling alone. The constant sits above two local imports. I accepted that layout to keep the diff focused. [Patch](evidence/review-packet/ua-patch.diff)

## Commands I ran after the patch

From the JS2 folder:

```bash
.venv/bin/python -m pytest tests/test_permissions.py -v -k ua01
.venv/bin/python -m pytest -q
.venv/bin/python -m agent --config config/boards.json --out out
```

The focused test passed and the suite at that commit passed 124 tests. In live run 2, Notion returned 153 postings, Linear returned 32, and Stripe also succeeded. The invalid token returned 404 once, so the exit remained `incomplete` with three successes and one failure. [Focused output](evidence/review-packet/ua01-after-patch.txt) · [Suite output](evidence/review-packet/after-patch-full-suite.txt) · [Live run 2 summary](evidence/runs/live-2-after-ua-patch/summary.json)

**Decision — Accept.** The test went from red to green, the diff stayed within the requested header change, and both Ashby boards succeeded in the follow-up live run. I recorded the decision in `9d8e012`.

## What the test misses

The fake handler checks the Request object before any network traffic. It skips the standard HTTPS handler's default-header processing, which explains the pre-patch `None`. A change that only configures the opener's default headers could send the intended header live and still fail this test. The live rerun establishes that Ashby accepted the requests on November 9.
