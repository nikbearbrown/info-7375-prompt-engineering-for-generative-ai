# FACTCHECK.md — why-subtract-the-max

Every factual claim that reaches the screen or the narration, with its verdict
and its source. Sources are one of two kinds only:

- **PRINTED** — emitted by `python3 main.py` on this machine.
- **DERIVED** — produced by importing `main.py` and calling its own
  `probabilities()`, with each recomputed stage checked against that function's
  return value.

No claim below is sourced from the chapter prose or from recall.

Environment: Python 3.13.5, Windows 11.
Source: `lessons/01-randomness-and-first-prompts/code/main.py`, repo HEAD `8f590fa`.

---

| # | Claim (as it appears) | Verdict | Source |
|---|---|---|---|
| 1 | `main.py` calls `max(logits)` and subtracts it before exponentiating | TRUE | Read of main.py lines 14–15 |
| 2 | softmax output is positive and sums to 1 | TRUE, with caveat — see #11 | DERIVED |
| 3 | `probabilities([1,2,3])` = `0.09003057317038046, 0.24472847105479764, 0.6652409557748218` | TRUE | **PRINTED** |
| 4 | peak = `3`; shifted scores = `-2, -1, 0` | TRUE | DERIVED |
| 5 | `exp` of shifted = `0.1353352832366127, 0.36787944117144233, 1.0` | TRUE | DERIVED |
| 6 | sum of shifted weights = `1.5032147244080551` | TRUE | DERIVED |
| 7 | direct `exp` of raw = `2.718281828459045, 7.38905609893065, 20.085536923187668` | TRUE | DERIVED |
| 8 | direct total = `30.192874850577365` | TRUE | DERIVED |
| 9 | direct probabilities = `0.09003057317038045, 0.24472847105479764, 0.6652409557748219` | TRUE | DERIVED |
| 10 | shifted and direct are **NOT** bit-identical; max abs diff = `1.1102230246251565e-16` | TRUE | DERIVED |
| 11 | `sum(probabilities)` = `0.9999999999999999`, not exactly `1.0` | TRUE | DERIVED |
| 12 | `probabilities([1000,1000])` = `0.5, 0.5` exactly | TRUE | DERIVED |
| 13 | `math.exp(1000)` raises `OverflowError: math range error` | TRUE | DERIVED (exception caught and printed) |
| 14 | largest representable float = `1.7976931348623157e+308` | TRUE | `sys.float_info.max`, printed |

---

## Corrections made to the original brief

**The brief asked for an "identity check … produce identical final
probabilities." That is false on this input and was not built as specified.**

The measured result:

```
index 0: shifted=0.09003057317038046  direct=0.09003057317038045  diff=1.3877787807814457e-17
index 1: shifted=0.24472847105479764  direct=0.24472847105479764  diff=0.0
index 2: shifted=0.6652409557748218   direct=0.6652409557748219   diff=1.1102230246251565e-16
all exactly equal: False
```

B03 therefore states **"agreement, not identity"** and shows the per-component
differences. Putting "identical" on screen would have contradicted the run.

## Claims deliberately NOT made

- That the implementation is "numerically stable" in general. B05 exists to
  refuse exactly this generalisation.
- That the `[1000,1000]` overflow behaviour is representative of every large
  input — only that this input overflows, here, on this interpreter.
- Nothing is claimed about `temperature` values other than the default `1.0`.
- `sample()`'s counts (`{"1": 268, "2": 630, "0": 102}`) are printed by main.py
  but are **not used in any beat** — the reel is about the distribution, not
  the sampler. Recorded in SOURCES.md for completeness only.
