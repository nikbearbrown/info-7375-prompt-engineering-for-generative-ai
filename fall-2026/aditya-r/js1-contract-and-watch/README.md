# Job-Search Agent 1 — The Contract and the Watch

**Student:** Aditya Raj · **Course:** INFO 7375 · **Assignment:** JS1 (Chapters 1–3)
**GitHub folder:** `fall-2026/aditya-r/js1-contract-and-watch/` in [nikbearbrown/info-7375-prompt-engineering-for-generative-ai](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai)

This agent watches one public job board (Databricks on Greenhouse). It reports only postings that are new since the last run, and gives every new posting two labelled verdicts against one fictional résumé (Priya Nair):
- **RECORD:** from a deterministic written rule that anyone can recompute.
- **JUDGMENT:** Claude's opinion under a prompt contract. A strict validator checks it, but the validator can't make it correct.

The agent never applies, emails, messages anyone, or logs in. It fetches only from `boards-api.greenhouse.io`.

## Contents

| Path | What it is |
|---|---|
| `CONTRACT.md` | Aditya's contract: the original text (commit `710b152`) plus the author-approved revisions R1–R5 |
| `agent/` | `rules.py` (the RECORD), `judge.py` (isolated Claude CLI call), `validate.py` (JUDGMENT validator), `board.py` (allow-listed fetch), `state.py`, `resume.py` (R3 guard), `watch.py` (the CLI) |
| `prompts/` | `judge_v1.md` (baseline), `judge_v2.md` (one change), and `FROZEN.json` (hashes of both, recorded before the held-out run) |
| `resume/priya-nair.resume.example.json` | Fictional persona, unchanged from the Reallocation Engine |
| `tests/` | 72 pytest tests, `faulty_variants.py` (the two wrong versions) and `mutation_check.py` |
| `evidence/snapshots/` | Raw board responses with metadata: the live 2026-10-30 snapshot and the Internet Archive capture of 2026-09-22 |
| `evidence/runs/` | Both watch runs: raw response, metadata, every Claude attempt, `report.md`/`report.json`, and state after the run |
| `state/seen.json` | The agent's state after run 2 |
| `experiments/` | Sample procedure and manifest, raw sampling responses, raw prompt-experiment responses, scorers, results |
| `labeling/` | The labelling sheets and **Aditya's hand labels** |
| `SAMPLING_REPORT.md`, `PROMPT_EXPERIMENT.md`, `ACTION_SURFACE.md` | The three Chapter artifacts |
| `scripts/verify_evidence.py` | Offline re-check of all saved evidence (no network, no Claude) |
| `SOURCES.md`, `FRICTIONAL.md` | Attribution and the process log |
| `evidence/local_commit_history.txt` | Timeline of the local development repository. Commit hashes cited in these documents (e.g. `710b152`, `469d0a2`) come from that repository, whose history was not pushed. |
| `SUBMISSION_CHECKLIST.md` | Rubric → evidence audit |

## Toolchain

- **Language and test runner:** Python **3.12.8** (python.org build, `/usr/local/bin/python3`). The standard library covers everything except tests, which use **pytest 8.3.3**.
- **Model calls:** Claude Code CLI **2.1.310** (`claude -p`), logged in with Aditya's account, model **`claude-opus-5-5`**, effort **`medium`**. **Temperature cannot be set** through the CLI, so it isn't set. Each call is a fresh session:
  - an empty temp working directory, `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--disable-slash-commands`, `--no-session-persistence`, and our own `--system-prompt`;
  - the CLI still adds its own environment block (account email, working directory, platform);
  - each response's `modelUsage` lists a small `claude-haiku-5-5` entry, which we assume is CLI housekeeping (not verified).
- **Platform:** macOS (Apple Silicon), zsh.

## Commands (from a fresh clone)

```bash
cd fall-2026/aditya-r/js1-contract-and-watch
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Offline: no network, no Claude needed
.venv/bin/python -m pytest -q                    # 72 tests
.venv/bin/python tests/mutation_check.py          # plants each wrong version; all must be CAUGHT
.venv/bin/python scripts/verify_evidence.py       # recomputes new ids, RECORDs; re-validates saved JUDGMENTs
.venv/bin/python experiments/score.py sampling    # recompute the sampling table from saved responses
.venv/bin/python experiments/score.py prompt      # recompute pass rates from saved responses + labels
.venv/bin/python scripts/check_labels.py          # label files: ids, missing or invalid values (read-only)
.venv/bin/python scripts/privacy_scan.py          # LIMITED pattern scan of tracked files (not proof)
.venv/bin/python scripts/handcheck.py show|reveal # hand-recompute one RECORD, answer hidden until reveal

# Live: needs network, and Claude Code CLI logged in for the judgments
.venv/bin/python -m agent.watch --board databricks --resume resume/priya-nair.resume.example.json \
    --state /tmp/js1-state.json --runs-dir /tmp/js1-runs --label baseline   # first run = baseline, 0 new
.venv/bin/python -m agent.watch --board databricks --resume resume/priya-nair.resume.example.json \
    --state /tmp/js1-state.json --runs-dir /tmp/js1-runs --label later      # reports only new ids
```

To repeat the seeded baseline exactly, add `--from-file evidence/snapshots/databricks_20260922T181913Z_wayback.json.gz --seeded-note "..."` to the first command. Point `--state` at a new path so the committed evidence isn't modified.

**Exit codes:**
- `0`: complete.
- `2`: refused or invalid input; state is unchanged.
- `3`: incomplete; some judgments are invalid, and those ids stay `pending` for retry.

## What ran (2026-10-30, all times real)

1. **Run 1, the SEEDED baseline.** The agent replayed an **authentic earlier response**: the Internet Archive's capture of this exact endpoint, taken on **2026-09-22T18:19:13Z** by a third party and downloaded today. It recorded 883 ids and reported **0 new**.
   - The agent did not run on Sep 22.
   - The capture has no descriptions, which the baseline doesn't need.
   - The original server ETag matches the start of our SHA-256 of the body.
2. **Run 2, LIVE** (2026-10-30T21:38:23Z). The agent fetched `boards-api.greenhouse.io` and got 902 postings, **258 new** since the baseline. It judged all 258 with both judges, in 259 Claude attempts. One attempt was rejected for citing `spark` from `skills.languages`, and its retry was valid. RECORD and JUDGMENT agreed on 258/258, with 3 relevant.
   - **What this demonstrates:** detection by id of a real change in Databricks' postings over 38 days.
   - **What it does not:** day-to-day monitoring, scheduling, or a baseline the agent captured itself.
3. **Experiments.** Sampling used 20 calls; the prompt experiment used 40, as v1 and v2 on dev and held-out.
4. **Action-surface modes.** Modes 2 and 3 were real CLI runs. Mode 1 was done by Aditya in claude.ai.

## The contract, applied

**The rule (CONTRACT.md §4).** A posting is relevant only when all three conditions hold:
- **A.** The title contains an eligible role phrase.
- **B.** The title contains no seniority or management term.
- **C.** At least 2 target skills (python, sql, spark, databricks, langgraph) appear both in one entry of Priya's four skill arrays and in the posting's title or description.

**Documented effects of the rule:**
- "databricks" is in **every** description (it's the employer's name), so condition C really requires only one of python, sql or langgraph (R2).
- "spark" never counts, because it isn't on Priya's résumé.
- Titles with no ASCII letters (for example, Japanese-only titles) become empty after normalization and are treated as missing.
- Location, seniority beyond the title, work authorization and degree are deliberately ignored, even though they matter in a real job search.

**The wrong versions** (CONTRACT.md §5) are tested three ways:
- as standalone faulty variants (`tests/faulty_variants.py`);
- by planting each into the real code (`tests/mutation_check.py`; all CAUGHT, `evidence/mutation_check_output.txt`);
- once in real use, when the live validator rejected an unsupported résumé citation (see run 2).

**The failure prediction** (approved 2026-10-30 17:30 EDT): *"If the agent reports baseline postings as new, attaches a verdict to the wrong posting, or accepts an explanation supported by neither the résumé nor the posting, I will consider this version to have failed its contract."* Against that prediction:
- baseline ids reported as new: 0;
- JUDGMENTs that fail to re-validate against their own posting: 0 of 258;
- unsupported explanations accepted: 0 found by the validator. The validator checks quotes and fields, not every claim in free-text explanations.

## Results of the Chapter artifacts

- **Sampling (Chapter 1):** see `SAMPLING_REPORT.md`. 5 postings × 4 fresh calls: 20/20 valid, and the verdict was identical within every posting. All 20 agree with Aditya's hand labels. The wording and quoted evidence varied; the verdicts did not.
- **Prompt experiment (Chapter 2):** see `PROMPT_EXPERIMENT.md`. v1 and v2 both scored 10/10 on format and 10/10 on hand-label agreement, on dev and on held-out. The "always not_relevant" baseline scores 7/10 (dev) and 8/10 (held-out). **The one change made no measurable difference.** Ten selected cases with a ceiling result can't show whether it fixes the rare failure it targets.
- **Action surface (Chapter 3):** see `ACTION_SURFACE.md`. The chosen design is code-driven fetching and state plus a **tool-less** Claude session.

## Driver's seat

| Task | Claude did | Aditya did | Why that part stays Aditya's | Evidence that the split happened |
|---|---|---|---|---|
| Relevance rule and contract | Found the conflicts (5/903 relevant; "databricks" in 903/903); proposed options | Wrote the contract; chose the options, changed the proposed split proportions, required the R3 exact-domain match and the R4 evidence check | What counts as "worth a day of your life" is a value judgment, and the rule is accountable to him | `710b152` (verbatim draft) → `22d2b42` (his revisions R1–R5) |
| Code, tests, faulty variants | Wrote them | Specified what must be caught (§5); ran the tests and mutation check himself (screenshot received 17:54 EDT; the run time isn't shown) | Tests written by the code's author share its blind spots | `69210f0`; `evidence/mutation_check_output.txt` |
| Hand labels | Generated blank sheets with no groups or verdicts; later repaired CSV quoting only | **Labelled all 20**, with a reason for each | The labels are the reference the model is measured against | `83c0b7e` (as received), `4d6322a` (quoting repair, labels unchanged) |
| Prompt revision | Found the failure; proposed, wrote and ran the single change | Accepted the stated rationale (he didn't find the issue himself or review the diff) | It is his experiment, and he decides whether a change is acceptable | `469d0a2` (freeze); FRICTIONAL entry 17:44–17:50 |
| Sign-off | Drafted wording | Decides whether to sign | His name, his liability | below |

## Sign-off — Job-Search Agent 1

_Wording drafted by Claude from the recorded evidence. Signed at Aditya's explicit instruction: Claude entered his name and the time on his behalf._

- **Checked:**
  - Baseline reports 0 new; run 2 reports exactly the ids absent from the baseline (`verify_evidence.py`).
  - Every RECORD recomputes; every JUDGMENT re-validates against its own posting (`verify_evidence.py`).
  - Allow-list, including redirects, and the R3 résumé guard (`tests/test_inputs.py`).
  - Both wrong versions are caught (`tests/test_wrong_versions.py`, `tests/mutation_check.py`).
  - Aditya ran `pytest` (72 passed) and `tests/mutation_check.py` (3 caught) himself. The screenshot was received 2026-10-30 17:54 EDT, and the run time isn't shown.
  - Aditya recomputed one RECORD by hand (posting 8864368002) before revealing it, and his verdict matched (`not_relevant`).
  - Aditya ran `scripts/verify_evidence.py` (all 16 checks passed) and `scripts/privacy_scan.py` (6 findings, all synthetic test values) himself. The screenshot was received 2026-10-31 16:14 EDT, and the run time isn't shown.
  - Aditya confirmed he saw no model output, groups or RECORDs before or while labelling.
- **How:**
  - **With Claude's help:** Claude wrote all the tests, the faulty variants, the mutation check and the verifier from the contract. None of them is a test Aditya wrote before reading Claude's code.
  - **By running them himself:** Aditya ran pytest, the mutation check, the evidence verifier and the privacy scan in his own Terminal (screenshots received 2026-10-30 17:54 and 2026-10-31 16:14 EDT; the exact run times aren't shown).
  - **By hand:** Aditya made the 20 labels himself, without seeing model output; Claude only prepared the sheets and rule reminders. He also recomputed one RECORD before revealing it.
  - **By recomputation:** `scripts/verify_evidence.py` recomputes every RECORD and the new-id set from the saved raw responses.
- **Not checked:**
  1. That any posting is actually a good fit for a real person. The rule ignores location (3 of 5 rule-relevant postings are outside the US), visa status and years of experience.
  2. Behaviour on other boards (Lever, Ashby), other personas, or a Greenhouse schema change.
  3. A real redirect from the live host. The redirect refusal is tested only by calling the handler directly.
  4. Prompt injection in posting text. No adversarial postings were tested.
  5. Whether Claude's free-text `explanation` sentences are true. Only the structured citations are validated.
  6. Whether the `claude-haiku-5-5` entry in CLI usage affects the answer.
  7. Stability of the verdicts over days, or across model versions.
- **Not claiming:**
  - The 20-posting sample is selected and **not representative**; it gives no estimate of how common relevant postings are.
  - Repeated identical verdicts show repeatability, not correctness.
  - The seeded baseline was not captured by this agent.
  - A JUDGMENT is an opinion even when it passes validation.
- **Signed or withheld:** **SIGNED** — Aditya Raj, 2026-10-31 16:28 EDT _(entered by Claude at Aditya's explicit instruction)_
