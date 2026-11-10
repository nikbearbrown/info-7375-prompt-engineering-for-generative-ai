# Review packet: one change I asked Claude Code to make

> Facts sections were organized by Claude Code. Every `TODO(Ashwin)` is mine to write; nothing there is
> filled in for me.

## 1. The change and why I chose it

TODO(Ashwin): which change, and why this one. (GATE.md proposed "empty board reported as no new jobs", but
the real loop does not have that defect; GATE.md says to choose another reproduced defect in that case.)

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

`tests/test_review_interrupt.py`, drafted by Codex from the reproduction and test helpers, added by me and
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

Sent by Ashwin to Claude Code on 2026-11-10 (quoted exactly):

> Fix the interrupted-request accounting bug in jobloop/loop.py. A request sent before KeyboardInterrupt
> must count toward attempts_used and appear as one attempt in that board's report. Keep the run
> incomplete and leave persistent state unchanged.
>
> Limit the patch to jobloop/loop.py. Don't change the tests, gate, or independent checker. Run the
> regression test and full suite on both Python versions, then show me the diff and results before
> acceptance.

The patch Claude Code produced is saved as `review-packet/patch.diff` (uncommitted until my decision).

## 5. The diff, read as a change in behavior

TODO(Ashwin): commit of the patch; for each hunk, what the program now does differently, in which case.

## 6. Did it stay in scope?

TODO(Ashwin): files touched versus files needed; anything changed that I did not ask for.

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

TODO(Ashwin): anything I re-ran myself afterwards, with its output.

## 8. Decision: accept, revise, or reject

**Accept**, Ashwin's decision on 2026-11-10 (my one-word answer to Claude Code: "Accept"). The patch was
then committed on its own.

TODO(Ashwin): the evidence I based it on, in my words.

## 9. One case my test would still miss

TODO(Ashwin)
