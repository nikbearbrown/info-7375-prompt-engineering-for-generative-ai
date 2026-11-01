# Job-Search Agent 2: the loop, the tools, and the diff

**Hemanth Rayudu, INFO 7375, Fall 2026.** The JS1 agent becomes a bounded loop over **three boards on two applicant-tracking systems**: Anthropic (Greenhouse), Notion and Perplexity (Ashby).

- It works under a **permission policy enforced in code**, with 20 predicted boundary cases.
- It changed through **one reviewed diff**.

**Started from:** my own Job-Search Agent 1 (`../js1-contract-and-watch/`, final commit `72141da`), copied unchanged as commit `2c3654d`. The persona is the fictional **Priya Nair**, and the rule is unchanged from JS1. The Claude judge uses prompt v2.

| File | What it is |
|---|---|
| [`GATE.md`](GATE.md) | exits, budgets, repeat rule, error policy, permission policy, wrong versions. Committed before any JS2 code (`92b5c77`); amendments A1 and A2 accepted |
| `jsagent/loop.py` | the loop: budgets, repeat rule, error policy, exits, trace |
| `jsagent/policy.py`, `jsagent/net.py` | the permission policy (hosts, methods, read/write roots, approval) and the policed GET |
| `jsagent/providers.py` | Greenhouse and Ashby, one posting shape, keys (system, board, id) |
| [`BOUNDARY-TESTS.md`](BOUNDARY-TESTS.md) | 20 boundary cases, predicted before the policy code (`2ee631a`), with observed results |
| [`REVIEW-PACKET.md`](REVIEW-PACKET.md) | the reviewed change: defect reproduced, test first, diff, scope, commands, decision |
| `runs/`, `state/`, `evidence/seeded/` | traces, raw responses (gzipped, with SHA-256), reports and state |
| `scripts/check_run.py` | the independent check that caught the finished wrong answer |
| [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) | what I used and what Claude contributed; my log |

## Language, toolchain, exact commands

- **Language and libraries:** Python 3.9.10. Standard library plus `pytest` 8.3.3.
- **Claude Code:** 2.1.316, for the Claude judge (`claude -p`, no API key). The loop, the policy and every test run without it.
- **Tested on:** macOS.

```bash
cd fall-2026/rayudu-h/js2-loop-tools-diff
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                          # 52 tests, no network, no Claude

# one loop run over boards.json: 3 real boards + 2 that fail on purpose (exit code 1 = incomplete)
.venv/bin/python -m jsagent run --no-claude --state state/my-try.json

# the finished-wrong-answer scenario (SEEDED) and its independent check
cp evidence/seeded/state-before-wrong-answer-demo.json state/try-demo.json
.venv/bin/python -m jsagent run --config boards-wrong-answer.json --state state/try-demo.json --label seeded --no-claude
.venv/bin/python scripts/check_run.py runs/<that run> evidence/seeded/state-before-wrong-answer-demo.json

# resetting state needs approval (refused without it)
.venv/bin/python -m jsagent reset-state --state state/my-try.json                          # refused
.venv/bin/python -m jsagent reset-state --state state/my-try.json --approve reset-state    # allowed
```

**Exit codes:** 0 finished · 1 incomplete · 2 budget-exhausted · 3 error · 4 refused.

## What ran (Oct 31, 2026, ET)

| Run | What | Exit |
|---|---|---|
| `runs/2026-10-31T191245-live/` | **live**: Anthropic, Notion, Perplexity, plus failure (a), a bad Ashby name, and failure (b), the OpenAI board with a 0.001 s limit | **incomplete**: three baselines (675 / 148 / 138 postings, none reported as new); (a) HTTP 404, **not retried**; (b) timed out, **retried once** after 2 s, then failed; 6 requests, 4.5 s |
| `runs/2026-10-31T191312-seeded-wrong-answer/` | **SEEDED** failure (c): Notion's response replaced by `{"jobs": []}`, before the patch | **finished**, "Notion: 0 new". **Wrong**, and caught by `scripts/check_run.py` (0 postings vs 148) |
| `runs/2026-10-31T193432-seeded-after-patch/` | the same SEEDED scenario after the reviewed patch | **incomplete**; Notion **unverified**; state kept at 148 |

**The trace of the live run,** with the deliberate failures (`runs/2026-10-31T191245-live/trace.jsonl`, abridged):

```
19:12:45 request      greenhouse:anthropic   attempt 1
19:12:46 board-ok     greenhouse:anthropic   675 postings, baseline
19:12:47 board-ok     ashby:notion           148 postings, baseline
19:12:47 board-ok     ashby:perplexity       138 postings, baseline
19:12:47 request      ashby:notion-does-not-exist-js2   attempt 1
19:12:47 board-failed ashby:notion-does-not-exist-js2   HTTP 404 (permanent; not retried)
19:12:47 request      ashby:openai           attempt 1, timeout 0.001
19:12:47 retry        ashby:openai           timeout: timed out, after 2.0 s
19:12:49 request      ashby:openai           attempt 2, timeout 0.001
19:12:49 board-failed ashby:openai           timeout (transient; retried once)
19:12:49 exit         incomplete             6 requests, 4.53 s
```

**No JS2 run has had a new posting yet.** Every live run so far was a baseline, so no Claude judgment appears in a JS2 run. A later live run against `state/seen.json` would be the first real "new since last time" across all three boards.

## Sign-off — Job-Search Agent 2

```text
Sign-off — Job-Search Agent 2
Checked:      (1) the empty-board defect, by a test written before the patch
                  (tests/test_review_empty_board.py, commit 998e487), which I ran myself:
                  2 failed before the patch, all 52 passed after
              (2) the 20 boundary cases against predictions committed before the policy code
                  (BOUNDARY-TESTS.md; 19 as predicted, #19 only partly)
              (3) the live run's exits: 404 not retried, timeout retried once, run incomplete
                  (runs/2026-10-31T191245-live/trace.jsonl)
How:          by a test written before the patch: (1), with Claude writing it and me running it;
              by recomputation: scripts/check_run.py reads raw files, not the agent's report;
              with Claude's help: Claude wrote the loop, the policy and all tests from GATE.md
Not checked:  a partial board (148 -> 3 postings) is still trusted;
              a real redirect to an off-list host (only a fake opener is tested);
              any Claude judgment in a JS2 run (no new postings yet);
              a real HTTP 5xx or 429 (only constructed in tests);
              the reset-state approval being written to a trace (it is only printed)
Not claiming: that the boards' contents are complete or current between runs;
              that the rule picks good jobs (unchanged from JS1)
Signed or withheld: Hemanth Rayudu, Oct 31, 2026
              (list accepted by Hemanth; name typed by Claude Code at Hemanth's explicit
              instruction: "accept the sign-off, you sign it for me")
```

## Driver's seat

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| Boards and failures | listed public boards with live counts | chose Anthropic, Notion and Perplexity, plus all three failure kinds | what the agent watches is my call | `GATE.md`, Boards |
| The rest of the gate | proposed exits, budgets, repeat rule, error and permission policy | delegated ("do whatever is best"), then accepted it, and accepted amendments A1 and A2 | budgets change only by my written decision | `GATE.md` status lines |
| The loop | wrote it, the tests, and the live and seeded runs | — | — | commits `d8e6b95`, `bde5f0e` |
| The review | reproduced the defect, wrote the test first, wrote the patch, showed the diff | ran the failing test and the full suite myself; decided **accept**; chose the case the test misses | I'm accountable for what's merged | `REVIEW-PACKET.md`, sections 5–7 |
