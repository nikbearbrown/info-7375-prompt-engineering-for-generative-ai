# Review packet: reading a range of years by its lowest number

The change I asked Claude Code to make, reviewed on evidence. My JS1 TA asked for it: "Add a test for the year-range reading that your record and Claude disagreed on."

## 1. The defect, reproduced

The relevance rule (`agent/rule.py`, carried from JS1) reads the years a posting asks for. For a range it read only the last number:

| Text in a posting | Years read before the fix | Experience part |
|---|---|---|
| "2–12+ years of industry software engineering experience" (Stripe 6176758, a real posting from JS1 experiment 2, line 32) | 12 | not met |
| "Minimum 2-3+ years of hands-on experience" (Twilio 7661919, a real posting from JS1) | 3 | not met |

Rohan has about 2 years, so both were wrongly rejected. In JS1 experiment 2, Claude read 6176758 as 2 years and the record read it as 12.

## 2. My test, written before the patch

`tests/test_year_ranges.py`, committed in `a5fc261` before any change to the rule. The four phrases and the expected answers are mine; Claude Code typed them as code.

| Case | My expected answer | Before the fix |
|---|---|---|
| a. "2–12+ years of industry software engineering experience" | passes | FAIL |
| b. "Minimum 2-3+ years of hands-on experience" | passes | FAIL |
| c. "3-5 years in backend" | fails | ok |
| d. "5+ years of experience" | fails | ok |

Output: `evidence/review/1-test-before-fix.txt` (2 of 4 fail).

## 3. The request

My words to Claude Code (2026-11-10): "Fix experience ranges so they use the lowest number, for example, `2–12+` should count as 2 years, and don't change anything else." `GATE.md` says a change to the relevance rule needs my approval; this request was that approval.

## 4. The diff, read as a change in behaviour

Commit `0ecb3d5`, saved as `evidence/review/2-patch.diff`. One file, `agent/rule.py`, 3 lines added and 2 removed:

* `YEARS` now also matches a second number joined by `-`, `–` or `—` before "years".
* Each match becomes `min(low, high)` instead of the single number it found. A phrase without a range still gives its one number, so "5+ years" stays 5 and "1.5+ years" stays 1.5.

In behaviour: a posting that asks for a range now passes the experience part when its lowest number is under 3, and fails it when the lowest number is 3 or more. Nothing else in the rule changes: role, skills, location and the title words are untouched.

On real data (`evidence/review/compare_rule_versions.py`, the rule before and after on all 567 jobs of run 1, output in `evidence/review/5-behaviour-change.txt`): 6 jobs changed, all from Ramp. They ask for "1–4", "2–4", "1-3", "2–3", "2-6" and "1–3 years". Their experience part went from not met to met. Their final verdict stayed Not Relevant, because none of them is an engineering role (finance, sales, operations, legal). No verdict changed.

## 5. Did the change stay in scope?

Yes. `git diff --stat a5fc261 0ecb3d5 -- agent tests` shows only `agent/rule.py`. No other code file, no test and no budget, host or board file changed. All 68 tests passed after it (`evidence/review/4-all-tests-after-fix.txt`), so no earlier test had to change.

## 6. The commands I ran myself

In my own terminal, after the fix (output pasted in `evidence/review/6-commands-i-ran.txt`):

```bash
python3 -m unittest tests.test_year_ranges -v && python3 -m unittest discover -s tests && python3 evidence/review/compare_rule_versions.py && git diff --stat a5fc261 0ecb3d5 -- agent tests
```

Result: my test 4 of 4, all 68 tests OK, 6 jobs with a changed experience part and no changed verdict, one file changed.

The written rule records the change too: a dated JS2 note at the end of `CONTRACT-JS1.md`, added with my approval, with the JS1 rule above it left unchanged. `GATE.md` makes the written rule the truth, so the rule and the code now say the same thing.

## 7. My decision

Accept. The evidence: my test went from 2 failures to 4 passes, the diff touches only the rule file, every other test still passes, and on 567 real jobs no final verdict changed.

## 8. A case my test would still miss

"2 to 4 years", a range written with "to" instead of a dash: the rule still reads it as 4 and rejects it. "3 yrs" is not read at all, because the rule looks only for the word "years". Neither appears in run 1's 567 jobs. I did not widen the fix to cover them, because my request was to change nothing else.
