# Evaluation freeze — 2026-11-21 13:17 EST

Recorded and committed **before** any model proposal was requested for either question set. Later files must match these SHA-256 values; `sponsorsql/evaluate.py` refuses to score against a key whose hash differs.

| File | SHA-256 | Meaning |
|---|---|---|
| `dev-questions.json` | `49e1948274ef325a669f026331cf30268ac68ca08656be7cda508c096fc7fc98` | Ten development questions (meaning fixed in ANSWER-KEY.md, 2026-11-21) |
| `answer-key-results.json` | `db93d4dc65f6e54523fb46383c24770b212755d8873818654f97053f9eb47da0` | Development key; reproduced byte-for-byte from a fresh load today |
| `heldout-questions.json` | `2f9890891fb7ee5bf633f756e323ce2ee03214cfdf86853c3cc63008c932350e` | Five held-out questions |
| `heldout-key.json` | `5fd8c4e7b9b87b0309ac5e146a627a6526334680226acab2ab0add1f5a8ed4f6` | Held-out key, counted row by row in Python by `build_heldout_key.py` |

## Rules

- The development set may be used to revise the prompt contract. Every revision is a new file (`PROMPT-CONTRACT-v2.md`, ...) and the development score is reported for each version.
- The held-out set is scored **once**, with the final contract version, and its result is reported whatever it is. If the held-out score is used to change anything afterwards, that later score is labelled as no longer held-out.
- The SQL writer (a Claude instance receiving only the prompt text from `python3 -m sponsorsql prompts`) is not given these key files.
