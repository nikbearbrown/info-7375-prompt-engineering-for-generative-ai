# Review packet (Chapter 6) — `check_run.py` read files the permission policy forbids

**The change I asked Claude Code to make:** make the independent check obey the gate's read policy.

**Outcome:** patch v1 → **revise** → patch v2 → **accept**. Every step is a separate commit, so the order can be verified.

| step | commit | who | what |
|---|---|---|---|
| defect found | — | Claude Code, reading its own code, 2026-11-09 | `check_run.py` opened whatever `raw_path` a run record named, never asking `Policy.read` |
| **1. reproduce** | `aae20af` | Claude Code wrote it; Aditya ran it | `review/repro_check_reads_outside.py` printed `DEFECT: check read a file outside the folder`, and the check said **consistent** about a file the policy denies |
| **2. test before patch** | `5293ca4` | Aditya decided the behavior ("refuse and stop"); Claude Code drafted the text; Aditya created and ran it | `test_record_pointing_outside_folder_is_refused` → **FAIL** `PermissionError not raised` ([01](01-test-fails-before-patch.md)) |
| 3. patch v1 | `1567edd` | Claude Code | all reads in `check_run.py` go through a `_read()` helper that asks the policy |
| **4. review v1** | — | **Aditya**: read `git diff`, ran 51 tests, the repro, and the wrong-version harness | everything green, but the decision was **REVISE**: v1 still accepts a wrong file *inside* the folder ([02](02-patch-v1-decision-revise.md)) |
| **5. test before v2** | `ca8725e` | Aditya's decision; Claude Code drafted the text; Aditya appended and ran it | 3 new tests **FAIL** on v1 (another run's raw, another board's raw, a persona file) ([03](03-new-tests-fail-on-v1.md)) |
| 6. patch v2 | `a5dc929` | Claude Code | `_raw_for()`: the resolved path must be directly in **this run's** `raw/` folder and named for **that board** |
| **7. review v2 → ACCEPT** | `a5dc929` | **Aditya**: read `git diff check_run.py`, ran `unittest discover` (**55 OK**) and `wrong_versions.py` (3/3 caught) | "accept it" (2026-11-10) |

## The diff, read as a change in behavior

| `raw_path` in the record points at… | before | after v1 | after v2 |
|---|---|---|---|
| a file outside the assignment folder | **read**, and the verdict came from it | refused, check stops | refused, check stops |
| another run's raw file | read | **read** | refused |
| another board's raw file in this run | read | **read** | refused |
| a non-raw file in the folder (e.g. `personas/`) | read | **read** | refused |
| this run's raw file for this board | read | read | read |

"Refused" means a `PermissionError` is raised before any flag is computed and before `check.json` is written, so no verdict exists. All raw reads now happen up front for this reason.

## Did the change stay in scope?

**Yes.** Both patches touch only `check_run.py`: v1 was +16/−5 and v2 +16/−1.
- The loop, `policy.py`, `GATE.md` and the existing 50 tests are unchanged (`git diff 9ff7b87 a5dc929 -- jobwatch2 GATE.md tests/test_loop.py tests/test_policy.py` is empty).
- Five tests were added; none were removed or weakened.
- I re-ran the check on both real Nov 9 runs with v2. Both still flag `greenhouse/ramp` `finished-wrong`, so the change didn't break the real use.

## Commands I ran myself (Aditya, own terminal, outputs pasted into chat)

```bash
python3 review/repro_check_reads_outside.py                 # before the patch: DEFECT; after v1/v2: OK refused
python3 -m unittest tests.test_review_check_reads -v        # FAIL before v1; 3 FAIL on v1
git diff check_run.py                                       # read v1, then v2
python3 -m unittest discover -s tests -v                    # 51 OK on v1; 55 OK on v2
python3 tests/wrong_versions.py                             # 3/3 wrong versions CAUGHT, on v1 and v2
```

## Decision, with evidence

- **v1: REVISE.** Green tests were not enough. The case Claude Code named as still missed (a wrong file *inside* the folder) means the check can still compute a verdict from the wrong data. The policy answers "may I read this?", but the check needs "is this the right file?".
- **v2: ACCEPT.** My three new tests fail on v1 and pass on v2. The original test still passes, nothing else changed, and the real runs still check the same way.

## One case my tests would still miss

The record can still point at the **wrong attempt** of the right board. For example, it could cite `greenhouse__stripe.attempt1.json` (a 503 body) when attempt 2 was the 200 the loop used. The name check accepts any attempt number, and no test covers it. Possible fix, not done: the record should store the attempt number, or a hash of the body it used.
