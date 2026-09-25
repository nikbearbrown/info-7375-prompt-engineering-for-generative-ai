# FACTCHECK — Claude, Seeded?

Status: Gate F closed after independent execution of the source script.

| Beat | Claim | Verdict | Source / derivation |
|---|---|---|---|
| B00 | The question is whether two random runs differ. | PASS | User-supplied teaching point. |
| B02 | Three outcomes have probabilities 9%, 24.5%, and 66.5%; the script simulates 1000 draws with a seed. | PASS | Executed `main.py`; probabilities are `[0.0900, 0.2447, 0.6652]`. |
| B03 | Running unmodified `main.py` with seed 7 twice gives counts `{0: 102, 1: 268, 2: 630}` both times. | PASS | Executed source twice; outputs matched. |
| B04 | `sample([1,2,3], seed=99)` gives `{0: 93, 1: 267, 2: 640}`. | PASS | Executed source function with seed 99. |
| B05 | Repeatable does not mean true; the wrong-answer example is constructed. | PASS | Conceptual illustration supplied by the user; labeled on screen as constructed, not source output. |
| B06 | The evidence shows repeatability, not correctness, safety, or quality. | PASS | Explicit boundary supplied by the user. |
| B07 | Viewer should run seeded code twice, then change only the seed and compare. | PASS | Required handoff supplied by the user. |

No additional numeric claims were added.