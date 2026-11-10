# Review packet: one change I asked Claude Code to make

> Evidence and analysis were drafted with assistance; contributions are recorded in SOURCES.md.
> The acceptance recorded below is separate from final submission sign-off.

## 1. The change and why I chose it

The selected change fixes interrupted-request accounting. The original candidate, an empty board
reported as no new jobs, was not a defect in the normal implementation. This alternative had a saved
reproduction: two sent requests became one budgeted attempt, and the interrupted board lost its attempt
record. It directly tests the gate requirement that every attempt counts, including failures.

## 2. The defect, reproduced before any patch

Found by Claude Code on 2026-11-09 while reading its own code at commit `e270605`. Reproduction:
`review-packet/reproduce_interrupt.py` (committed at `fb35380`). Output before any patch
(`reproduce-before-patch.txt`, exit 1):

```text
requests sent: 2
report attempts_used: 1
trace attempt events: 2
ashby/beta attempts in report: 0 (outcome not-observed)
independent check [C7] run: report says 1 attempts used; the trace shows 2
independent check [C2] ashby/beta: report lists 0 attempts; the trace shows 1
DEFECT PRESENT
```

In words: if a request is interrupted (Ctrl-C) while it is in flight, the request was sent, but the budget
does not count it and the board's report shows no attempt. That is GATE.md wrong version 5 ("failed
attempts omitted from the request budget") happening for real on one path.

## 3. My test, written before the patch

`tests/test_review_interrupt.py`, drafted by Codex from the reproduction and test helpers, saved in the project and
committed on its own at `279c10f`, before any loop code changed. Against the unpatched loop it failed 3 of 3,
exit 1 (`review-packet/test-review-interrupt-before-patch.txt`; Claude Code re-ran it and got the same):

```text
AssertionError: 1 != 2 : An interrupted request still consumes one attempt.
AssertionError: 0 != 1 : The board report must retain the request sent before interruption.
AssertionError: Lists differ: [C7 ..., C2 ...] != [] : The saved report must agree with its trace.
FAILED (failures=3)
```

After the patch (`be7a54a`): 3 of 3 OK, exit 0.

```bash
cd fall-2026/ashwin-t/js2-loop-tools-diff && python3 -m unittest tests.test_review_interrupt -v
```

## 4. What I asked Claude Code to do

Drafted by Codex and sent by Ashwin to Claude Code on 2026-11-10 (quoted exactly):

> Fix the interrupted-request accounting bug in jobloop/loop.py. A request sent before KeyboardInterrupt
> must count toward attempts_used and appear as one attempt in that board's report. Keep the run
> incomplete and leave persistent state unchanged.
>
> Limit the patch to jobloop/loop.py. Don't change the tests, gate, or independent checker. Run the
> regression test and full suite on both Python versions, then show me the diff and results before
> acceptance.

The patch Claude Code produced is saved as `review-packet/patch.diff` (committed with the accepted patch at `be7a54a`).

## 5. The diff, read as a change in behavior

At `be7a54a`, three changes alter the interrupted-request path:

1. `BoardInterrupted` carries the attempts already made while remaining a `KeyboardInterrupt`.
2. When interruption occurs inside the request call, the handler counts that attempt, records an
   interrupted result without inventing a response body, updates the ledger and trace, and raises the
   exception with the accumulated attempts. Previously these steps were skipped.
3. The outer run handler retains those attempts instead of replacing them with an empty list. The
   board remains not-observed, the run remains incomplete, and the existing state-write restriction
   remains in effect.

## 6. Did it stay in scope?

The executable patch changes only `jobloop/loop.py` (+22, -2). The same commit includes
`review-packet/patch.diff` as evidence. Tests, GATE.md, and the independent checker are unchanged by
this patch. Documentation updates record provenance and results separately from the code behavior.
The change stays within the requested in-flight interruption fix.

## 7. Commands I ran myself, and what they printed

**What actually happened, honestly:** on 2026-11-10 I tried to run the checks myself several times, but
each command ran from the main checkout (`info-7375-prompt-engineering-for-generative-ai/`), not from this
JS2 worktree, so none of them tested the patch: `ModuleNotFoundError: No module named
'tests.test_review_interrupt'`, `ImportError: Start directory is not importable: .../tests` (exit 1) and
`can't open file .../review-packet/reproduce_interrupt.py` (exit 2). These were working-directory errors,
not test results.

Because of the deadline, I then asked Claude Code to run the checks for me. **These commands were run by
Claude Code at my request, not by me**, via `sh review-packet/run-checks.sh` (output saved in
`review-packet/checks-run-by-claude-code.txt`, exit 0):

| Command (from `js2-loop-tools-diff/`) | Result |
|---|---|
| `git --no-pager diff --stat -- jobloop/loop.py` | 1 file, 22 insertions, 2 deletions |
| `python3 -m unittest tests.test_review_interrupt -v` | 3 tests OK, exit 0 |
| `/opt/homebrew/bin/python3.12 -m unittest discover -s tests -t .` | 54 tests OK, exit 0 |
| `python3 -m unittest discover -s tests -t .` | 54 tests OK, exit 0 |
| `python3 review-packet/reproduce_interrupt.py` | "defect not present", exit 0 |

**Later, run by me personally** (2026-11-10 20:20:36 UTC, at `89013cf`, after the two gate-gap fixes),
with `sh review-packet/run-checks-ashwin.sh` from my own terminal; output in
`review-packet/checks-run-by-ashwin.txt`:

| Command (from `js2-loop-tools-diff/`) | Result |
|---|---|
| `python3 -m unittest tests.test_review_interrupt tests.test_gate_gaps -v` | 9 tests OK, exit 0 |
| `python3 -m unittest discover -s tests -t .` | 60 tests OK, exit 0 |
| `/opt/homebrew/bin/python3.12 -m unittest discover -s tests -t .` | 60 tests OK, exit 0 |
| `python3 review-packet/reproduce_interrupt.py` | "defect not present", exit 0 |
| `python3 independent_check.py runs/2026-11-09T20-21-52Z-live` | PASS, exit 0 |

This personal run was after acceptance and after a later fix to the same file, so it confirms the
current code, not the state of the code at the moment I accepted.

## 8. Decision: accept, revise, or reject

**Accept**, Ashwin's decision on 2026-11-10 (my one-word answer to Claude Code: "Accept"). The patch was
then committed on its own.

Evidence supporting acceptance: the unchanged regression test failed all three checks before the
patch and passed afterward; the original reproduction now reports two sent requests, two budgeted
attempts, and one attempt on the interrupted board. The full 54-test suite passed on both Python
versions. The executable change is limited to the requested file. This is acceptance of the reproduced
path, not a claim that every possible interruption point has been verified.

## 9. One case my test would still miss

An interrupt during the one-second retry wait is not exercised by this test. The handler added by
this patch wraps the request call, so an interruption during the wait can still lose the board
attempts collected before the wait. The test also does not exercise real OS signal timing; it raises
KeyboardInterrupt from a fake transport after recording a simulated sent request.
