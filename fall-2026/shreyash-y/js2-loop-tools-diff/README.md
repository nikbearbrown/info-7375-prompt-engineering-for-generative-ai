# Job-Search Agent 2: The Loop, the Tools, and the Diff

**Student:** Shreyash Yadav (`shreyash-y`) · INFO 7375 Prompt Engineering & Agentic AI, Fall 2026 · Professor Nik Bear Brown
**Assignment:** JS2, Chapters 4–6 · due 2026-11-10

**Starting point:** my own JS1 agent (`fall-2026/shreyash-y/js1-contract-and-watch`, submitted commit `bb193d9`). Its posting reader, rule v1, persona and validator were copied in unchanged in commit `4213c8c`. Neither the Reallocation Engine nor Lectern was used.

*Everything below the summary was drafted by Claude Code and checked against the files. The summary, GATE.md, the decisions in `review/` and the signature are Shreyash's.*

## Summary, in my own words

*Shreyash writes this section; Claude Code does not.*

> _To be written by Shreyash: what the loop does, what the live run and the seeded demo showed, what the review packet taught you, and what you would still not trust._

## Language and toolchain

- **Python 3**, standard library only, with nothing to install. Tested only on Python 3.14.6 (macOS); the code uses 3.9+ syntax.
- **Tests:** `unittest`.
- **Network:** only the three hosts in GATE.md section 6, and only in a live `run`. Every other command here runs offline.
- No model is called anywhere in JS2.

## Commands, from a fresh clone

```bash
git clone -b shreyash-y/js2-loop-tools-diff https://github.com/shreyashyadav1/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/shreyash-y/js2-loop-tools-diff
```

All tests, offline (93):

```bash
python3 -m unittest discover -s tests -t . -v
```

Check that no test file changed since it was written:

```bash
shasum -a 256 -c tests.frozen.sha256
```

Only the 20 predicted permission boundary cases:

```bash
python3 -m unittest tests.test_policy -v
```

A live run of all six boards in `boards.json`. It writes a new `runs/<UTC time>/`; exit codes are 0 finished, 2 incomplete, 3 budget-exhausted, 4 error:

```bash
python3 -m jsagent run
```

The independent check on any saved run:

```bash
python3 jsagent/check.py runs/20261110T002501Z
```

The **seeded** finished-wrong-answer demo, offline. It writes into a fresh `runs/seeded-finished-wrong/`, so move the committed one aside first:

```bash
mv runs/seeded-finished-wrong /tmp/seeded-finished-wrong-committed && PYTHONPATH=. python3 demo/make_finished_wrong.py runs/20261110T002501Z && python3 -m jsagent run --boards demo/boards-four-good.json --runs-dir runs/seeded-finished-wrong --replay runs/seeded-finished-wrong/input/map.json --run-id finished-wrong; python3 jsagent/check.py runs/seeded-finished-wrong/finished-wrong-SEEDED
```

## What ran

| When (EST) | What | Result | Evidence |
|---|---|---|---|
| 2026-11-09 19:22 | Tests run before any new code | 3 new test modules fail to import | `evidence/tests-before-new-code-2026-11-09.txt` |
| 2026-11-09 19:24 | Mutation check: break the code the way each wrong version would | 5 of 6 caught; the symlink-refusal line is untested on its own | `evidence/mutation-check-2026-11-09.txt` |
| 2026-11-09 19:25 | **Live run 1**: 6 boards, Greenhouse + Ashby + Lever | `incomplete`: 4 ok (199/150/32/304), the deliberate 404 failed after 1 request, WHOOP flagged `empty`; 6/12 requests, 3.4 s; check: no findings | [TRACE.md](TRACE.md) |
| 2026-11-09 | **Seeded finished wrong answer** | the agent says `finished`; the independent check flags `meta.total 199` vs 20 and 179 postings gone | [TRACE.md](TRACE.md), `evidence/finished-wrong-SEEDED-2026-11-09.txt` |
| 2026-11-09 | Boundary tests | 20 of 20 as predicted | [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md) |
| 2026-11-09 19:26–19:45 | Review packet: rule v2, three revisions | rev 1 revise, rev 2 rejected on reading, rev 3 accepted with known limitations | [REVIEW-PACKET.md](REVIEW-PACKET.md) |

## Folder map

- `GATE.md` (Shreyash's), `GATE-NOTES.md` (how it became code), `budgets.json`, `boards.json`
- `jsagent/`:
  - `policy.py`: hosts and paths, the permission policy in code.
  - `providers.py`: Greenhouse, Ashby and Lever.
  - `transport.py`: live HTTP, and replay for seeded runs.
  - `loop.py`: exits, budgets, repeat rule, error policy, trace.
  - `check.py`: the independent check. It imports nothing from the agent.
  - `rule.py`: rule v2 rev 3.
  - Also `posting.py`, `persona.py`, `validator.py`, copied from JS1.
- `tests/`, `tests.frozen.sha256`, `BOUNDARY-TESTS.md`
- `runs/`:
  - `20261110T002501Z/`: live run 1, with its raw responses, trace and summary.
  - `state/`
  - `seeded-finished-wrong/`: SEEDED.
- `review/`: every step of the review packet in order, with Shreyash's own runs and decisions. `REVIEW-PACKET.md` reads them in order.
- `evidence/`, `demo/`, `persona/` (fictional Alex Morgan, from JS1)

## Sign-off — Job-Search Agent 2

*Drafted by Claude Code for Shreyash to check, change and sign.*

```text
Checked:      - Exits, budgets, repeat rule and error policy: tests/test_loop.py (the five GATE.md
                wrong versions written as code and caught; 404 tried once; timeout/5xx once; budgets
                count retries); in live run 1 the deliberate 404 and the empty board were handled
                as GATE.md says (TRACE.md lines 14-19).
              - Permission policy in code: tests/test_policy.py, 20 cases predicted in
                BOUNDARY-TESTS.md before policy.py existed, 20 of 20 as predicted.
              - A finished wrong answer caught by a check that does not use the agent's code:
                tests/test_check.py and the seeded demo.
              - Rule v2 rev 3: tests/test_rule_v2*.py on real postings, plus my own runs of the
                tests and the behavior diff (review/04, review/17).
How:          The tests were written by Claude Code from GATE.md and committed before the code
              (cef009e before f4b553d; 6f4ae08 before the rule patch). I ran the review commands
              myself. The behavior diffs are recomputations over the 685 saved postings. The
              decisions in review/05 and review/18 are mine.
Not checked:  - A real timeout or 5xx: retries were only exercised with constructed responses.
              - A real redirect: the redirect guard was tested on a constructed redirect only.
              - A partial Ashby or Lever response: the check can only catch truncation on
                Greenhouse, which reports meta.total.
              - The symlink-refusal line alone (the mutation check left all tests green without it).
              - The rule's reading of experience and remote beyond the phrasings in these 685
                postings; the Physician Reviewer office-tag case and the location-vs-offices
                question are known and open.
Not claiming: That the agent finds good jobs, that rule v2 is correct in general (it is checked
              against 20 per-condition hand labels and my reading of the changed postings), that a
              clean exit means a right answer, or that the budgets are the right size for more
              than these six boards.
Signed or withheld: ____________ (name, date)
```

## Driver's seat

| Part | Claude should | Shreyash should | Why that part stays Shreyash's | Where the split shows |
|---|---|---|---|---|
| The exits, budgets and policy | turn GATE.md into code and tests; mark each choice the gate leaves open | write the gate first; decide what "finished" means and what needs approval | the limits on what an agent may do are the owner's decision, not the agent's | `9fbab0d` is GATE.md alone, in Shreyash's words; the choices are in GATE-NOTES.md |
| The loop's run | run it, save the trace and raw files, recount independently | choose the boards and the deliberate failures | which boards to watch and which failures to stage is a judgment about the search | GATE.md section 1; TRACE.md |
| The review: reading the diff | produce the behavior diff over real postings; list every condition that stops failing; find causes | run the commands; read the evidence; decide accept, revise or reject | a green test run is Claude's to produce; whether the change is right is the owner's call | `review/04` and `review/17` (Shreyash's runs); `review/05` "I don't want to accept the patch just because the tests are green"; `review/18` |
| What the rule should mean | point out cases the rule cannot settle | settle them, or leave them open on purpose | it decides which jobs are worth a day | Shreyash's JS1 decisions on experience and remote; the location-vs-offices case left open in `review/18` |
| The sign-off | draft the lines | check them, change them, sign or withhold | only the signer knows what they did not test | the signature line above |
