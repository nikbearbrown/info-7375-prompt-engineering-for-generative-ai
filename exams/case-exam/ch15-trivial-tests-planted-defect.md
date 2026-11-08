# Case 15: Tests that catch defects

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Mei works in a university registrar's office. Late library and tuition fees follow a written rule: no fee up to and including 5 days late; from day 6, a fee of 2% of the balance; the fee is never more than $50. She asked you to have Claude write `late_fee(days_late, balance)` in Python with tests, and to show that the tests are good enough that she can trust the function without reading the code.

### The instruction (what you sent)
> Write `late_fee(days_late, balance)` for the rule: 0 for days_late <= 5; otherwise 2% of balance, capped at $50. Write tests, and show me that the tests are good enough to trust.

### Agent output
```
IMPLEMENTATION
def late_fee(days_late, balance):
    if days_late > 5:
        return min(balance * 0.02, 50)
    return 0

TESTS (6, all pass)
  (days=0,  balance=100) -> 0
  (days=3,  balance=100) -> 0
  (days=10, balance=100) -> 2.0
  (days=30, balance=100) -> 2.0
  (days=10, balance=200) -> 4.0
  (days=2,  balance=50)  -> 0
Line coverage: 100%.

TEST QUALITY CHECK
Planted one defect: changed 0.02 to 0.03. The suite failed, so the
tests catch defects. Planted defects detected: 1 of 1.

CONCLUSION
The function is correct and the tests are strong. Safe to rely on
without reading the code.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the claim that the tests are strong, and what are the exact terms for the missing test inputs and for what the single planted defect shows?
2. **(2 pts)** What single check would show how strong the tests are?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Mei what the report does and does not show.

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
**The flaw:** the test inputs are all ordinary: nothing at the day-5/day-6 boundary and no balance large enough to reach the $50 cap (max fee tested is $4); one planted defect that the tests caught shows almost nothing about defects they would miss; a boundary mutant (`> 5` to `>= 5`) or a removed cap would survive. 100% line coverage executes lines but does not check them.

**Full-credit terms (2):** adversarial / edge test case (boundary, cap); surviving mutant; planted defect (more than one, chosen to probe the boundary and cap); detection power; coverage is not detection.
**Half-credit (1):** "needs more tests"; "edge cases" with no example; "mutation testing" without saying which defects would survive; "tests too easy".
**Zero:** "overfitting", "hallucination", "stub" alone.

**Acceptable evidence requests (any two count):**
- Plant several defects: `>= 5`, `> 6`, remove the `min(..., 50)` cap, and show each makes the suite fail (killed); any that pass are surviving mutants.
- Add tests at days 5 and 6 and balance 5000 (expected $50) and show them passing on correct code and failing on the mutants.
- Write expected values from Mei's written rule before running the code (independent oracle).

**Unacceptable:** "get 100% branch coverage"; "run the tests again"; "plant the same 0.03 defect twice"; "ask Claude if the tests are strong".

**Traps:**
- "100% coverage" and "1 of 1 defects detected" sound like proof; this is the persuasive part of the case.
- Students may recompute the rule and say the function is fine; the planted flaw is the strength claim, not the code.
- A student who says "more tests" alone has not shown which tests.

**CAP RULE:** flaw missed (no statement that the tests do not cover the boundary or the cap, or that one detected defect proves little) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. Every test uses ordinary inputs: there is no day 5 or day 6 and no balance big enough to hit the $50 cap. A mutant like `>= 5` or no cap would survive. One planted defect (0.02 to 0.03) that the tests kill shows little; coverage only means lines ran. So the suite needs adversarial edge cases and more planted defects. 2. Plant defects at the boundary and cap and check which survive. 3. "Add tests for days 5 and 6 and balance 5000; plant `>= 5`, `> 6`, and no-cap mutants; report which survive; do not call the tests strong until all are killed." 4. "The tests only try easy fees. We do not yet know whether the day-six start or the $50 limit is right."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but uses "day-six start", partly technical and the account is not two sentences; scope point withheld.

**Typical (6/10).**
> 1. The tests do not try day 5 and day 6 or a big balance. 2. Add those tests. 3. Tell the agent to add boundary tests. 4. It only checks easy cases.

Score: C3 T1 E1 F1 P0 = **6**. Reason: names the missing boundary and cap in plain words (C3); no term such as surviving mutant (T1); "add those tests" is right but does not check detection (E1); correction is narrow (F1); Q4 is plain but does not say what the report does show (0).

**Fluent-but-wrong (3/10).**
> 1. The function should be written in a pure functional style, and floating point 0.02 will give rounding errors, so a decimal type is needed; coverage should be branch coverage. 2. Compare against a spreadsheet. 3. "Use Decimal and report branch coverage." 4. There might be rounding errors.

Score: C0 T1 E0 F1 P1 = **3**. Reason: questions the implementation (floating point) and ignores that the tests miss the boundary and cap (flaw missed); "coverage" is a near-miss term; a spreadsheet comparison could be reasonable but names no inputs; fix is partly relevant; Q4 is plain.
