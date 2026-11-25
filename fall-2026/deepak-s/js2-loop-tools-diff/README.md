# Job-Search Agent 2: The Loop, the Tools, and the Diff

INFO 7375, fall 2026. Student: Deepak Kumaran T S (GitHub DeepakKTS). Fictional persona on screen and in files: Riley Okafor, @example.com.

A bounded loop that watches several job boards across three applicant-tracking systems (Greenhouse, Lever, Ashby). It uses three tools under a permission policy enforced in code, ends in one of four written exits, and is checked by an independent verifier. The spec is `GATE.md`; the boundary predictions and results are in `POLICY.md`; the review packet is `REVIEW.md`; the sign-off and driver's seat are in `SIGNOFF.md`; the honest log is `FRICTIONAL.md`.

## Started from
- My JS1 agent, "The Contract and the Watch", personal repo commit b91c877 (graded). Its code, tests, persona, schema, labels, prompts and presubmit script were imported in commit d3ae571. Lectern and the Reallocation Engine were not used.
- One JS1 file was imported as evidence: evidence/manual/stripe_20261030T000804Z.raw (5,729,543 bytes) and its README, because 4 imported JS1 unit tests read it. It is unchanged from b91c877.
- The JS1 modules that touch disk or network outside the JS2 tools are named as legacy in GATE.md Amendments A-1. They are reachable only through the JS1 subcommands. A test checks they are byte-identical to b91c877 and that none is in the import closure of the loop path.

## Provenance of GATE.md
- The first draft of GATE.md was written in a claude.ai chat (Claude Opus 5.5, 2026-11-10) from my plan. At Gate 1, Claude Code reviewed it against the brief and listed 21 items. The revision that answers them was drafted in the same claude.ai chat. My decisions are recorded in GATE.md's Provenance line.
- The wording of Amendments A-1 to A-3 was drafted in the claude.ai chat. The decisions are mine (GATE.md, Amendments).
- POLICY.md's Expected column is my prediction, committed in 891446a before any .py file in this folder (presubmit checks the order).

## Language and toolchain
- Python 3.15.0, standard library urllib for HTTP. One entry point: `python -m jobwatch`.
- `requirements.txt` pins anthropic==2.3.0, jsonschema==4.26.0 and pytest==9.2.0. anthropic is used only by the JS1 judge, which the JS2 loop never imports or runs.
- Exact versions from `pip freeze` in the venv used for every run here: annotated-types==0.8.0, anthropic==2.3.0, anyio==4.16.0, attrs==26.1.0, docstring_parser==0.18.0, h11==0.16.0, httpcore2==2.16.0, httpx2==2.16.0, idna==3.20, iniconfig==2.3.1, jiter==0.19.0, jsonschema==4.26.0, jsonschema-specifications==2025.9.1, opentelemetry-api==1.45.2, packaging==26.3, pluggy==1.7.0, pydantic==2.14.3, pydantic_core==2.50.4, Pygments==2.21.0, pytest==9.2.0, referencing==0.37.0, rpds-py==2026.9.1, sniffio==1.3.1, truststore==0.10.5, typing-inspection==0.4.5, typing_extensions==4.16.0.

## Commands, from a fresh clone
The folder is `fall2026/deepak-kumaran-ts/js2-loop-tools-diff/` in the personal repo and `fall-2026/deepak-s/js2-loop-tools-diff/` in the class repo. Run everything from inside it.

```
git clone https://github.com/DeepakKTS/INFO-7375-Prompt-Engineering-Agentic-AI.git
cd INFO-7375-Prompt-Engineering-Agentic-AI/fall2026/deepak-kumaran-ts/js2-loop-tools-diff
python3.15 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q                                    # offline; no key; no network
.venv/bin/python -m jobwatch verify runs/20261110T200748Z        # independent check of the real run
.venv/bin/python -m jobwatch verify runs/20261110T200830Z        # the finished wrong answer: exits 2, SUSPECT
.venv/bin/python -m jobwatch replay runs/20261110T200748Z        # offline rebuild of the run's summary
.venv/bin/python -m jobwatch loop --config config/boards.json    # LIVE: 4 GET requests to public boards
```
- `loop` writes a new `runs/<UTC run id>/` and replaces `state/seen.json`, which is tracked, so a live run changes the working tree.
- Exit codes:
  - `loop`: 0 FINISHED, 3 INCOMPLETE, 4 BUDGET_EXHAUSTED, 1 ERROR (GATE.md section 1).
  - `verify`: 0 clean, 2 flagged (GATE.md section 7).
  - `replay`: 0 matches, 1 any difference.
- Presubmit, from inside the folder: `bash scripts/presubmit_check.sh`.

## What ran
Only runs committed in this folder are listed. Both loop runs are live runs, made by Claude Code in my session on 2026-11-10.

| What | When (ET) | Kind | Result | Files |
|---|---|---|---|---|
| Manual curl capture, 7 GETs | 13:40 | live, curl outside the program | stripe 776, stripe-js2-nonexistent 404, lever US 0 (`[]`), lever EU 6, palantir 304, linear 33, notion 152 | `evidence/manual-capture/CAPTURE.md` |
| Real run 20261110T200748Z, `config/boards.json` | 15:07:48 | live | INCOMPLETE (3); greenhouse:stripe OK 775; greenhouse:stripe-js2-nonexistent FAILED http_404, count null, no retry; lever:lever (api.eu.lever.co) OK 6; ashby:linear OK 33; all baseline, 0 new | `runs/20261110T200748Z/summary.json`, `trace.md` |
| verify and replay of 20261110T200748Z | 15:08 | offline | verify 0, CLEAN, 0 flags; replay 0, matches | `evidence/real-run/` |
| Finished-wrong-answer run 20261110T200830Z, `config/boards-fwa.json` | 15:08:30 | live | FINISHED (0); lever:lever on api.lever.co OK with 0 postings, 0 new; stripe 775; linear 33 | `runs/20261110T200830Z/summary.json` |
| verify of 20261110T200830Z | 15:08 | offline | exit 2: `SUSPECT lever:lever: 6 postings in prior run 20261110T200748Z, 0 now` | `evidence/finished-wrong-answer/` |
| My own curl check | 15:17:01 | live, my terminal | api.eu.lever.co 6, api.lever.co 0 | `evidence/finished-wrong-answer/deepak-curl-check.txt` |
| Full test suite | 15:46 | SEEDED (fake transport, temp folders; no network) | 445 passed | `evidence/review/full-suite-after-A3-20261110T204658Z.txt` |
| My review commands, run myself: the red test at 7309446 | 15:52:09 | SEEDED fault injection | 2 failed | `evidence/review/deepak-red-at-7309446.txt` (commit 7ebb3ba, 15:52 ET) |
| My review commands, run myself: green test, full suite, diff stat after 3a4c1fb | 15:52:10 | SEEDED fault injection / offline | 2 passed; 445 passed; jobwatch/loop.py 15 insertions, 10 deletions | `evidence/review/deepak-green-and-diff.txt` (commit 7ebb3ba, 15:52 ET) |
| Fresh-clone test at d092939 (`git clone --depth 1`, venv, install) | 15:57:20 | offline | pytest 445 passed; verify 20261110T200748Z exit 0; verify 20261110T200830Z exit 2 (SUSPECT); replay of both exit 0. The live loop was not rerun, to avoid 4 extra live GETs. | `evidence/fresh-clone/20261110T205719Z.txt` |

The test suite's loop runs are SEEDED: a fake transport serves the fixtures in `fixtures/seeded/` (each file named SEEDED_*) inside temporary folders, and the runs are labelled "SEEDED" in their summary and trace. None of them is committed.

## Contents
- `GATE.md`: the spec. It covers exits, budgets, the repeat rule, the error policy, the permission policy, wrong versions W01 to W14 with the tests that catch them, the independent check, and Amendments A-1 to A-3.
- `POLICY.md`: boundary cases B01 to B16, with my predictions and the pytest results.
- `REVIEW.md`: the review packet (candidate 1: an ERROR exit changed state).
- `SIGNOFF.md`: the sign-off and driver's seat.
- `FRICTIONAL.md`: my log.
- `SOURCES.md`: endpoints and docs.
- `config/`:
  - `budgets.json`: budget decision B-1.
  - `boards.json`: the real run.
  - `boards-fwa.json`: the finished-wrong-answer run.
- `jobwatch/`:
  - `loop.py`: the loop.
  - `tools.py`: the only network and disk tools: fetch_json, read_file, write_file.
  - `policy.py`: the permission policy.
  - `providers/`: greenhouse, lever, ashby.
  - `verify.py`: independent check, stdlib only.
  - `loop_replay.py`
  - `persona.py`: JS2 copy of JS1's persona checks.
  - `cli.py`
  - the JS1 modules (legacy, A-1).
- `tests/js2/`:
  - `test_boundary.py`
  - `test_loop.py`
  - `test_verify.py`
  - `test_wrong_versions.py`
  - `test_source_scan.py`
  - `test_persona.py`
  - `test_review_state_on_error.py`: my review test.
  - `test_review_state_replace_failure.py`
- `tests/acceptance`, `tests/spec`, `tests/unit`: the JS1 tests, unchanged.
- `fixtures/seeded/`: SEEDED fixtures and their README.
- `runs/`: the two real runs.
- `state/seen.json`: state after the two runs.
- `evidence/`:
  - `manual-capture/`: raw headers and bodies, sha256, CAPTURE.md.
  - `real-run/`
  - `finished-wrong-answer/`
  - `review/`: SEEDED repro scripts, red and green outputs.
  - `pytest/`: full-suite outputs.
  - `manual/`: the one JS1 capture.
- `scripts/presubmit_check.sh`

## Known limits
- The redirect refusal was tested in-process through a real urllib opener for 300, 301, 302, 303, 304, 307 and 308, but never against a real server. No real 3xx appeared in the capture.
- The loop accepts an empty 200 as a board with 0 postings (GATE.md section 4). Only verify, and a curl check outside the program, catch it.
- REVIEW.md section 5 lists the windows that remain after the patch, in which state and the run record can disagree.
- The JS2 guarantees in GATE.md section 5 are claimed for the loop path, not for the JS1 subcommands (A-1).
- Saved pytest outputs contain absolute paths of the machine they ran on.

## Credits
- Claude Code (claude-opus-5-5, Claude Opus 5.5), 2026-11-10, in my session, wrote:
  - the JS2 code and tests (except my review test);
  - the SEEDED fixtures;
  - this README, SOURCES.md, CAPTURE.md, the finished-wrong-answer README, the review evidence README, and REVIEW.md sections 2 to 5;
  - the wrong-version implementations used to show W01 to W14 are caught.
- Claude Code also ran:
  - the manual curl capture at my instruction;
  - both live loop runs.
- It did not write FRICTIONAL.md, SIGNOFF.md, POLICY.md's Expected column or my parts of REVIEW.md.
- Claude in a claude.ai chat (Claude Opus 5.5, 2026-11-10) drafted:
  - GATE.md and its revision;
  - the amendment wording;
  - my review test, `tests/js2/test_review_state_on_error.py`, which I ran red and committed (7309446) before the patch (3a4c1fb).
