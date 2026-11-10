# Step 2 — Patch v1 reviewed by Aditya: decision **REVISE** (2026-11-10)

**What Aditya ran** (in their own terminal, output pasted into the Claude Code chat):

| command | result (verbatim) |
|---|---|
| `git diff check_run.py` | read the whole diff: 1 file, +16/−5 (the `_read()` helper; checks.json, record.json and raw files all read through the policy) |
| `python3 -m unittest discover -s tests -v` | `Ran 51 tests in 0.138s` / `OK` |
| `python3 review/repro_check_reads_outside.py` | `OK: check refused the read: ... is outside the assignment folder` |
| `python3 tests/wrong_versions.py` | `correct code: 51 tests, 0 failing`; wrong versions 1/2/3 all `CAUGHT` (4, 1 and 1 failing tests) |

**Decision, in Aditya's words:** "I feel we should revise our approach". The reason is the case Claude Code named as still missed:

> A record whose `raw_path` points *inside* the assignment folder but at the wrong file — e.g. another run's raw file or `personas/maya-sehgal.resume.json`. The policy allows any read inside the folder, so the check would read it and recompute from the wrong data.

**What patch v1 did correctly:**
- It closed reads outside the folder, and Aditya's first test passes on it.

**What patch v1 still gets wrong:**
- The policy answers "may the agent read this?", but the check needs to know "is this *this run's* raw response for *this board*?". Those are different questions.

**What the revision must do (Aditya's decision):**
- Refuse and stop, as before, unless each `raw_path` is inside **this run's** `raw/` folder **and** is a file for **that board**: `raw/<ats>__<slug>.attempt<N>.json`.
- A new test goes in first.

Patch v1 is committed as-is so the history shows it, then superseded by v2.
