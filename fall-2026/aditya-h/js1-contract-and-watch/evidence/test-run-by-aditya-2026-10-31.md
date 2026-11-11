# Test run by Aditya — 2026-10-31, about 22:50 EDT

Aditya ran these two commands in their own terminal (macOS zsh) at commit `4766715` and pasted the output into the Claude Code chat. The output is summarized below, not edited.

```bash
python3 -m unittest discover -s tests -v
python3 tests/wrong_versions.py
```

**Result as pasted:**
- `Ran 53 tests in 0.026s` — `OK`. All 53 tests passed, including the 13 validator tests, the 18 rule tests and the 22 watch tests.
- `correct code: 53 tests, 0 failing`
- `wrong version 1 (labels by position): 2 of 53 tests fail -> CAUGHT`. The failing tests were `Validator.test_wrong_posting_id_rejected` and `WrongVersion1_LabelsOnWrongPostings.test_verdicts_stay_with_ids_when_order_reversed`.
- `wrong version 2 (justification cites nothing): 15 of 53 tests fail -> CAUGHT`
- `wrong version 3 (loose substring match): 10 of 53 tests fail -> CAUGHT`

The full pasted transcript is kept locally in the chat session. It is not reproduced here.
