# Sampling report (Chapter 1) — Job-Search Agent 1

**Date of runs:** 2026-10-31 (UTC timestamps for every call are in `trials.jsonl`).
**Interface:** Claude Code CLI, `claude -p`, Northeastern Claude Enterprise login.
The CLI version is recorded in `trials.md`; the Claude Code header showed Opus 5.5.
**Prompt:** `reports/prompt_experiment/prompts/baseline.txt` (my prompt contract).
**Runner:** `tools/claude_trials.py sample`.

## What I did
I asked Claude the same prompt contract about 5 postings, 4 times each, for 20 calls.
Each call was a fresh conversation: a new `claude -p` process with no tools, run
from a temporary directory so no project files were loaded. Every raw reply was
saved and passed through a validator (exact JSON keys, known verdict, matching
`posting_id`, non-empty field lists).

The 5 postings come from my development set and were chosen to cover different
cases under my labeling rule: the one posting I labeled relevant, plus four I
labeled not relevant for different reasons (location, clearance, experience ×2).

## Results (actual runs)

| posting | my hand label | Claude verdicts, runs 1–4 | matches my label |
|---|---|---|---|
| 4730836005 Software Engineer – New Grad | relevant | not_relevant ×4 | 0/4 |
| 4674863005 DevOps Engineer, Infrastructure & Security | not_relevant (2: clearance) | not_relevant ×4 | 4/4 |
| 4665557005 Infrastructure Software Engineer, Enterprise GenAI | not_relevant (4: experience) | not_relevant ×4 | 4/4 |
| 4694861005 Frontier Agents Engineer (Forward Deployed) | not_relevant (4: experience) | not_relevant ×4 | 4/4 |
| 4536653005 Software Engineer, Enterprise | not_relevant (5: London) | not_relevant ×4 | 4/4 |

- **Spread:** none. Every posting got the same verdict on all 4 runs.
  20/20 replies passed the validator; 0 were rejected.
- **Agreement with my hand labels:** 16/20.

## What I can conclude
- For these 5 postings and this prompt, Claude's verdicts were repeatable.
- Repeatability is not correctness. The clearest case is the New Grad posting:
  Claude said not_relevant on all 4 runs, against my label. Repeating the same
  answer told me nothing about who was right. I had to check the raw posting text.
- I read the reasons for the New Grad runs. All 4 cited the same decisive fact:
  the posting requires a graduation date in Fall 2026 or Spring 2027, and the
  persona finished her MS in December 2025. I confirmed this sentence in the
  saved raw response (`reports/prompt_experiment/label_audit_evidence.txt`).
  My labeling rule has no graduation-window condition, so my label followed my
  rule but was wrong about real eligibility. Post-hoc, Claude was right on all 20.

## What I cannot conclude
- That Claude is reliable in general. These are 5 postings from one board and
  one persona, run within minutes of each other on one day.
- Anything about borderline postings. None of these 5 produced a split verdict,
  so this sample does not show how Claude behaves when a case is truly unclear.
- Anything about sampling settings. `claude -p` does not expose temperature, so
  I cannot say which settings produced this stability.
- Reason-level consistency in general. I compared reasons only for the New Grad
  posting; for the other four I compared verdicts only.
