# evidence/review/: Phase 5a repro scripts (SEEDED fault injection)

Written and run by Claude Code (Claude Opus 5.5) on 2026-11-10 at Gate 5a, before any test or patch for the review packet. They were copied here unchanged from Claude Code's scratchpad; only the file names gained the SEEDED prefix. Each one uses the SEEDED fake transport from tests/js2/js2kit.py in a temporary folder, or edits a temporary copy of a committed run. None touches the network or a committed file.

At Gate 5a the scripts ran from the scratchpad as `<scratchpad>/<name>.py`. The commands below are the same commands with the paths of this folder, run from js2-loop-tools-diff/.

| Script | Candidate | Command | Output at Gate 5a |
|---|---|---|---|
| SEEDED_repro_state_then_error.py | 1: ERROR exit after state was replaced (jobwatch/loop.py:265-269, :391) | `.venv/bin/python -I evidence/review/SEEDED_repro_state_then_error.py $PWD` | `jobwatch: ERROR: could not write the run record: OSError: SEEDED: disk full` then `exit 1 \| state/seen.json exists: True \| summary.json exists: False` |
| SEEDED_tamper.py | 2: replay accepts forged failed-board records (jobwatch/loop_replay.py:38, :53) | `W=$(mktemp -d) && mkdir $W/runs && cp -R runs/20261110T200748Z $W/runs/ && python3 -I evidence/review/SEEDED_tamper.py $W/runs/20261110T200748Z/summary.json <case> && (cd $W && PYTHONPATH=$OLDPWD $OLDPWD/.venv/bin/python -m jobwatch replay runs/20261110T200748Z)` | case reason_http_500: exit 1; count_zero: exit 1; reason_budget: exit 0 ("matches"); reason_repeat: exit 0 ("matches"); unvisited_and_finished: exit 0 ("exit FINISHED (0); matches"). verify on the unvisited_and_finished copy: exit 0, CLEAN |
| SEEDED_repro_interrupt.py | 3: KeyboardInterrupt ends the run with no summary.json (jobwatch/loop.py:261) | `.venv/bin/python -I evidence/review/SEEDED_repro_interrupt.py $PWD` | `escaped: KeyboardInterrupt` then `summary.json exists: False \| trace lines: 9` |

Deepak picked candidate 1 for the review packet (REVIEW.md).

Not here: the redirect check from Gate 5a (b), which did not reproduce a defect.
