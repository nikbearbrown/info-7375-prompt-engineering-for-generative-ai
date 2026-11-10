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

TODO(Ashwin): the test file name, the commit that adds it, and its failing output before the patch.

```bash
cd fall-2026/ashwin-t/js2-loop-tools-diff && python3 -m unittest tests.test_review_interrupt -v
```

## 4. What I asked Claude Code to do

TODO(Ashwin): the prompt, quoted exactly, with the date.

## 5. The diff, read as a change in behavior

TODO(Ashwin): commit of the patch; for each hunk, what the program now does differently, in which case.

## 6. Did it stay in scope?

TODO(Ashwin): files touched versus files needed; anything changed that I did not ask for.

## 7. Commands I ran myself, and what they printed

TODO(Ashwin): exact commands and exit codes, run by me in my terminal after the patch.

## 8. Decision: accept, revise, or reject

TODO(Ashwin): the decision and the evidence for it.

## 9. One case my test would still miss

TODO(Ashwin)
