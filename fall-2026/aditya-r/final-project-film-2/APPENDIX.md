# DayThread — Methods and Evaluation Appendix (plan, 2026-11-23)

This is the detail behind parts 3 and 4 of the film. **Everything below is a plan.** The only
part of DayThread that has run is the minimal two-day replay of 2026-10-25
(`../final-project-film/replay/RESULTS.md`). Nothing here has been built, trained or measured.

## 1. What changed since the October pitch

| | October pitch | This plan |
|---|---|---|
| Separate check | "a separate check of the raw transcript" (method unspecified) | a **fine-tuned open model** (DistilRoBERTa), trained by Aditya |
| Handoffs | permissions listed in prose | a **delegation contract**: one testable condition per handoff, enforced in code, written with its tests before implementation |
| Main risk | the summary drops the tumble | the replay showed summaries **kept** the fall (10/10) but changed its meaning (9/10); omission will now be **forced** for the controlled failure, and meaning drift is a stated limit |

## 2. The delegation contract (to be written first, with tests)

Each step must hand the next one something a person who didn't build it can check. If the
check fails, the work stops; it never proceeds on "looks good". Source of the idea: course
chapter 10, "Evidence belongs on the edges".

| # | Handoff | Must be handed over (testable) | Who produces the evidence | If it fails |
|---|---|---|---|---|
| H1 | check-in → transcript store | the raw transcript, append-only, with its SHA-256 | the store (code) | stop; no summary is made |
| H2 | transcript → summary/memory | every memory claim carries a quote; the quote appears verbatim in the transcript | a string-match check (code) | claim rejected, not stored |
| H3 | transcript → checker → review item | the checker reads the raw transcript only; output = flagged sentence, score, model version | the fine-tuned model + code | review item marked "check failed"; nothing proceeds |
| H4 | review item → coordinator | the page shows the excerpt and the proposed action; the decision records a hash of both | the review page (code) | no decision = defer |
| H5 | coordinator → executor | the executor recomputes the hash before acting | the executor (code) | mismatch = refuse; delivery is simulated |

**Delegated to the agent:** reading check-in history, adding quoted observations, creating
internal review items. **Kept by the coordinator:** every outbound action. **Never:** overwrite
records, change agency-owned data, contact anyone, give clinical advice.
**Kept by Aditya (the driver's seat):** the contract, the tests, the labelling rules, the
held-out set, the pass marks and the sign-off. Claude may implement against them.

## 3. The loop

Observe (client message) → decide → act (one tool: look up memory, add an observation, or
create a review item) → record → stop. Exits: **completion** (the check-in ends), **halt** (a
contract check fails), **defer** (the turn budget runs out; status = incomplete, never a
fabricated result). The model saying "done" is not an exit.

## 4. The fine-tuned checker

- **Task:** flag concerning sentences in a raw check-in transcript (falls, missed medication,
  confusion, not eating). Binary label per sentence.
- **Base model:** `distilbert/distilroberta-base` on Hugging Face, licence Apache-2.0 (checked via
  the Hugging Face API on 2026-11-23). Small enough to fine-tune on a laptop.
- **Why a trained model and not another Claude call:** a check should fail differently from the
  thing it checks. Claude checking a Claude summary is the same opinion twice. The model runs
  locally, so no data leaves the machine, and it gives the same answer every run.
- **Training data:** synthetic sentences written by Claude under labelling rules Aditya writes,
  with a sample spot-checked by Aditya before training.
- **Held-out data:** sentences Aditya writes by hand **before any training**; the file's SHA-256
  is logged in FRICTIONAL.md and the file is not opened again until the single final run.
- **Toolchain:** Python, PyTorch, Hugging Face `transformers`, SQLite; MacBook Pro (Apple M3 Pro,
  18 GB). PyTorch is not installed yet. The machine's default `python3` is an Intel build, so the
  work will use an arm64 Python environment.

## 5. Evaluation

| What | How | Worked if | Didn't work if |
|---|---|---|---|
| Checker | recall and false alarms on the held-out set, against (a) a keyword list and (b) the untrained model | it beats the keyword list on the pass mark Aditya writes down **before** looking | it doesn't beat the keyword list; that is reported as the result |
| Contract | one test per handoff (H1–H5), plus a deliberately broken input for each | every broken input is refused | any broken input gets through |
| Gate binding | change the evidence after approval | the executor refuses | the executor acts |
| Deliberate failures (≥ 5) | "took a spill", "my legs gave out" (unfamiliar wording); "I didn't fall" (negation); "my neighbour fell" (someone else); "I fell asleep" (false alarm) | each outcome recorded, pass or fail | — (a failure here is a finding, not hidden) |
| Controlled failure | force a summary that drops the tumble | the checker flags it from the raw transcript and a coordinator reviews it | the tumble never reaches review |

**What the sample can't show:** anything about real clients or real care; other wording,
languages or models; whether a changed meaning is caught. The checker flags concerning
sentences; it does not judge meaning. That is why the coordinator sees the original words next
to every claim.

## 6. Resources

| Need | Have it? |
|---|---|
| Claude | Claude Code through Aditya's existing claude.ai login (used for the replay); no API credits |
| Base model | public download from Hugging Face; no account needed |
| Compute | MacBook Pro, Apple M3 Pro, 18 GB |
| Data | synthetic only; fictional clients |

## 7. Order of work (before 20 December)

1. Delegation contract and its tests.
2. Held-out test set, written and sealed.
3. Training data (Claude, under Aditya's rules), spot-checked.
4. Fine-tune and compare the checker on development data.
5. Loop, SQLite memory, local review page, executor with simulated delivery.
6. One run on the held-out set; evaluation report; sign-off.
