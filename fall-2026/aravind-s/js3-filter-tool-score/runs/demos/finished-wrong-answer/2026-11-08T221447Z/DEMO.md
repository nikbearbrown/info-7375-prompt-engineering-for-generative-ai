# The finished wrong answer, on the saved answers of run 2026-11-08T221447Z

Made by `python3 tools/wrong_answer_demo.py runs/2026-11-08T221447Z` at 2026-11-08T22:20:26Z. Both runs below are labeled
replays of that run's saved answers, with fresh state, not live runs. Nothing was fetched.

## 1. The planted wrong version

Wrong version 1a from GATE.md, planted in a temporary copy of the code (job_agent/providers.py):

```diff
-    if status != 200:
-        raise Unverified(f"the board answered HTTP {status}, not 200")
+    if status == 404:
+        return []  # PLANTED: wrong version 1a
+    if status != 200:
+        raise Unverified(f"the board answered HTTP {status}, not 200")
```

The planted replay's screen (exit code 0):

    Exit: finished (code 0). Every board on the list was read.
    4 boards: 4 read, 0 unverified, 0 not visited. 1464 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 0 waiting for Claude.
    BOARD ashby-openai: read, 816 postings, 0 new, 0 gone
    BOARD greenhouse-verkada: read, 343 postings, 0 new, 0 gone
    BOARD lever-palantir: read, 305 postings, 0 new, 0 gone
    BOARD greenhouse-no-such-board-js2-test: read, 0 postings, 0 new, 0 gone

It ends cleanly, and it is wrong: the made-up board answered HTTP 404, and the run reports it read.

## 2. The independent check (`tools/check_run.py`, exit code 1)

It reads only the saved answers and report.json, never the agent's code:

    Independent check of planted-replay (reads the saved answers and report.json only)
    
    | Board | Reported | From the saved answer | Postings reported / saved |
    |---|---|---|---|
    | ashby-openai | read | read: readable | 816 / 816 |
    | greenhouse-verkada | read | read: readable | 343 / 343 |
    | lever-palantir | read | read: readable | 305 / 305 |
    | greenhouse-no-such-board-js2-test | read | unverified: the saved answer is HTTP 404 | 0 / none |
    
    Report's exit: finished (code 0)
    
    Disagreements:
    - greenhouse-no-such-board-js2-test: the report says 'read', but the saved answer is HTTP 404, so it should be 'unverified'
    - exit: the report says finished, but greenhouse-no-such-board-js2-test could not have been read

## 3. The same answers through the unchanged code (exit code 1)

    Exit: incomplete (code 1). greenhouse-no-such-board-js2-test unverified: the board answered HTTP 404, not 200.
    4 boards: 3 read, 1 unverified, 0 not visited. 1464 postings in the answers read, 0 new since the last run, 0 gone since the last run, 0 new and relevant by the rule, 0 new and relevant in Claude's judgment, 0 waiting for Claude.
    BOARD ashby-openai: read, 816 postings, 0 new, 0 gone
    BOARD greenhouse-verkada: read, 343 postings, 0 new, 0 gone
    BOARD lever-palantir: read, 305 postings, 0 new, 0 gone
    BOARD greenhouse-no-such-board-js2-test: unverified (the board answered HTTP 404, not 200)

The check on that replay (exit code 0):

    Independent check of unchanged-replay (reads the saved answers and report.json only)
    
    | Board | Reported | From the saved answer | Postings reported / saved |
    |---|---|---|---|
    | ashby-openai | read | read: readable | 816 / 816 |
    | greenhouse-verkada | read | read: readable | 343 / 343 |
    | lever-palantir | read | read: readable | 305 / 305 |
    | greenhouse-no-such-board-js2-test | unverified | unverified: the saved answer is HTTP 404 | None / none |
    
    Report's exit: incomplete (code 1)
    
    No disagreement between the report and the saved answers.
