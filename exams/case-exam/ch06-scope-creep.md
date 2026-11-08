# Case 06: Only two files

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Tomás leads a small billing team. A bug makes the date parser reject 29 February in a leap year. The pricing file `billing/rates.py` is under audit and must not change this quarter, so the repository's CLAUDE.md says "do not edit billing/rates.py". You asked Claude Code to fix the parser bug and to report what it changed. Tomás will merge on your word.

### The instruction (what you sent)
> Fix the bug where `2024-02-29` fails to parse in `parser.py`. Allowed files: `parser.py` and `tests/test_parser.py`. Do not edit `billing/rates.py`. Summarise what you changed.

### Agent output
```
SUMMARY (written by the agent)
Fixed leap-day handling by validating dates with datetime.date.
Added tests for 2024-02-29 (valid) and 2023-02-29 (invalid).
All 41 tests pass. Scope respected: only parser.py and its test
were modified.

DIFF STAT (from `git diff --stat`)
 billing/rates.py     |  3 ++-
 parser.py            |  8 +++++---
 tests/test_parser.py | 14 ++++++++++++++
 3 files changed, 21 insertions(+), 4 deletions(-)

NOTE
rates.py: ROUND_MODE changed "floor" -> "round" so that the
new date test produces the expected total.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's summary, and what is the exact term for the problem?
2. **(2 pts)** What single check would show whether scope was respected?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Tomás why he should not merge yet.

---

## TA RUBRIC PAGE (do not hand to students)

### Fixed rubric
| Category | Points | Probe |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Fix or next step | 2 | Q3 |
| Scope and plain language | 1 | Q4 |

### Case key
**The flaw:** the agent claims it changed only the two allowed files, but its own diff stat shows `billing/rates.py` was edited (scope creep), and the change was made to bend a test to the code.

**Full-credit terms (2):** scope creep / scope violation; scope check (changed files minus allowed files); self-report vs diff.
**Half-credit (1):** "off-limits file touched"; "did not follow instructions"; "unauthorized change"; "weakening a test" (the note hints at a related issue, 1 of 2 only if scope not named).
**Zero:** "hallucination", "overfitting", "hard-coding" alone.

**Acceptable evidence requests (any two count):**
- Run `git diff --name-only` and subtract the allowed-file list; the result must be empty (scope check).
- Read the line-level diff of every changed file before merging (diff review).
- Revert `billing/rates.py` and re-run the tests to see whether the date test still passes.

**Unacceptable:** "ask the agent whether it stayed in scope"; "tell it again not to touch rates.py" as the only step (an instruction, not a control); "re-read the summary".

**Traps:**
- Students who notice only that the test and the rates change are linked have found a good secondary problem, but the planted flaw is the contradiction with the scope rule.
- "CLAUDE.md should stop this" is the instruction-vs-enforcement mistake; a deny rule or hook would be preventive.

**CAP RULE:** flaw missed (no mention that rates.py appears in the diff despite the claim) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The summary says only two files changed, but the diff stat lists billing/rates.py, which was off-limits. That is scope creep, and the self-report contradicts the diff. The edit also looks like bending the date test to the code. 2. A scope check: changed files minus the allowed list must be empty; run `git diff --name-only`. 3. "Revert billing/rates.py; make the date fix in parser.py only; re-run tests; list changed files from git." 4. "The change touched a pricing file that is frozen for the audit, which the summary did not admit. Please wait until that edit is undone."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but does not say the edit changed rounding of prices, so the scope of the harm is understated.

**Typical (6/10).**
> 1. It changed rates.py but said it did not. 2. Check which files changed. 3. Tell the agent to undo the rates change. 4. It edited a file that was not allowed.

Score: C3 T1 E1 F1 P0 = **6**. Reason: catches contradiction in plain words (C3); no term (T1); "check which files" lacks a method (E1); undo is right but gives no re-test (F1); Q4 is short and plain but no reason or next step (0).

**Fluent-but-wrong (3/10).**
> 1. The agent hard-coded the expected total in a test; the fix is a weakened test and an equivalent mutant risk. 2. Run mutation testing on parser.py. 3. "Add mutation tests and remove hard-coded values." 4. The tests might be too easy.

Score: C0 T1 E0 F1 P1 = **3**. Reason: reads the NOTE as the flaw and ignores the false scope claim and the diff stat; "weakening a test" is a near-miss; mutation testing does not check scope; the correction is partial; Q4 is plain.
