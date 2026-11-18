# Failures

Drafted by Claude Code from Tushar's review of the 40 held-out PASS diffs (docs/07-evidence.md, "Review of the 40 held-out PASS diffs (T5.2)")
Date: Nov 18, 2026
Status: started in T5.2 with three entries. T6.2 extends it.

Each entry is a failure the frozen checks did not catch: every run named here was a PASS, and stays one. The evaluation results in docs/07-evidence.md are unchanged. The review sheet with every diff is `results/t5-held-out-diffs.md`.

## F1. Leftover files in passing diffs

**What happened.** Three passing diffs on 008-config-parser contain files the fix did not need:
- a repair script the agent wrote and ran
- two placeholder files

The check does not look at extra files, so each run passed. The files are in the pending patches, and they would be in an exported patch if someone approved it as it stands. Tushar judged them leftovers, not attempts to manipulate the verdict.

**Evidence** (human code inspection, Tushar, Nov 18, 2026):

| Contract and round | Run | Extra file |
|---|---|---|
| A, round 1 | `20261118T034129Z-1d6b2b17` | `fix.py`: a 27-line repair script that rewrites `confparse/parser.py` (with an unused `import re`) |
| A, round 3 | `20261118T034859Z-7753441a` | `x`: the text `placeholder` |
| B, round 3 | `20261118T035050Z-27b9b6b8` | `confparse/_placeholder_check.txt`: the text `PLACEHOLDER` |

The traces show all three as allowed `write_file` calls inside /workspace.

**Not fixed:** the checks stay frozen so the held-out results stay comparable.

## F2. Passing fixes that miss documented behaviour the tests don't cover (011)

**What happened.** The 011-shared-default docstring says tags are stored lower case and compared case-insensitively. The tests check this only with an existing tag that is already lower case. Every one of the ten 011 diffs fixed the shared default and the mutation of the input list. But 7 of 10 keep existing mixed-case tags in their original case: 3 under A and 4 under B. One of those seven (B round 3) also compares the new tag case-sensitively against existing tags. All ten passed.

**Evidence:**
- **Keep the original case, compare case-insensitively:** A rounds 1, 2, 4 (`20261118T034148Z-84370d4f`, `20261118T034539Z-4b874abb`, `20261118T035304Z-4d9194b0`) and B rounds 1, 2, 5 (`20261118T034349Z-f4fd8d09`, `20261118T034733Z-ba456078`, `20261118T035846Z-39b1ae2a`).
- **Keep the original case, compare case-sensitively:** B round 3 (`20261118T035113Z-99cf4d75`).
- **Meet the documented behaviour (lower-case existing tags):** A rounds 3, 5 (`20261118T034926Z-1c3cf574`, `20261118T035644Z-82177778`) and B round 4 (`20261118T035451Z-696a98ef`).
- **Executed check** (human observation, executed, Tushar, Nov 18, 2026). Tushar copied the original repo to a temporary directory and applied B round 3's pending patch. There, `add_tag('x', ['X'])` printed `['X', 'x']`. The docstring calls for `['x']`.
- The other results above are human code inspection.

**Not fixed:** the checks stay frozen so the held-out results stay comparable.

## F3. The reference patch itself is incomplete or ambiguous (011 and 008)

**What happened.** The reference patches pass their checks (tasks/README.md), but in two tasks they do not settle the documented behaviour.
- **011-shared-default:** `tasks/011-shared-default/reference.patch` lowercases the new tag, but it keeps existing tags as given and compares against them as given. It has both shortcomings from F2: an existing `X` stays `X`, and it is not matched by `x`.
- **008-config-parser:** inside quotes, `tasks/008-config-parser/reference.patch` skips any character that follows a backslash. The agent patches skip only a backslash followed by a quote. The two differ when several backslashes come before a quote, and no test covers that case. The docstring describes only backslash-quote escaping, and `_unquote()` replaces only that sequence. So Tushar records this as a discrepancy that needs a clearer rule and another test. He does not treat every agent patch as wrong for differing from the reference.

**Evidence** (human code inspection, Tushar, Nov 18, 2026):
- the two reference patches named above
- for 008, all ten agent diffs in `results/t5-held-out-diffs.md`
- for 011, the runs listed in F2

**Not fixed:** the checks stay frozen so the held-out results stay comparable.
