# JS1 — The Contract and the Watch (Siddi Kommuri)

This agent watches **one public Greenhouse board** (Stripe, under contract v2). It reports only postings that are **new since the last run**. Each new posting gets two labelled verdicts for one **fictional** persona, Jordan Lee:
- the contract's deterministic **rule**, a *record* anyone can recompute;
- **Claude**, a *judgment*, under a fixed prompt contract with a strict output validator.

The specification is [CONTRACT.md](CONTRACT.md), written before any code.

## Language and toolchain

- **Python 3.13.2**, standard library only. It was developed and run on Windows 11 in Git Bash; it was not tested on macOS or Linux.
- **Claude Code CLI**, versions 2.1.304 and 2.1.309, only for the Claude calls. The model is pinned to `claude-sonnet-5-5` in [config/claude_cmd.txt](config/claude_cmd.txt).
- **Network:** `boards-api.greenhouse.io` only.

## Commands (run from this folder)

```bash
python tests/run_tests.py          # the 36 wrong-version tests; no network, no real claude (a stub stands in)
python tests/mutants.py            # puts each wrong version into the code; its own test must fail (37 mutants)
python -m agent run --mode live    # one watch run; needs `claude` on PATH and logged in
python -m agent check              # read-time validation of output/verdicts.jsonl
python -m agent select-labels --board raw/2026-10-31T10-48-38Z/board.json   # the contract's seed-42 label selection
python -m experiments.runner sample --ids 8333122,8113100,8333074,8224915,8194283 --repeats 4
python -m experiments.runner score --prompt judge_v1 --split dev
python tools/make_reports.py       # rebuilds the result tables in SAMPLING.md / PROMPT-EXPERIMENT.md
```

**Seeded mode** replays a saved board with no network call and keeps its own state file. These are the contract's two commands:

```bash
python -m agent run --mode seeded --seeded-from raw/2026-10-31T10-48-38Z/board.json
python -m agent run --mode seeded --seeded-from raw/2026-11-01T02-47-55Z/board.json
```

**Making `claude` callable:** live runs need it on PATH. On this machine that meant adding the folder of the desktop app's bundled `claude.exe`. The tests don't need it.

## What ran (all on 2026-10-31, ET)

| When | What | Evidence |
|---|---|---|
| 05:50 | Raw Databricks board saved with curl, before any code existed | `evidence/snapshot-morning/` |
| 06:35 | Contract v1 committed with the persona and frozen config | `be3b6c8` |
| 06:42 | Live baseline, Databricks: 901 postings, 0 reported new | `evidence/base-rate-databricks/` |
| 06:4x | Base-rate check: 4 postings pass title + seniority, **0 of 20** rule-relevant (< 3). The contract requires a slug change. | same folder |
| 06:48 | Contract v2 committed: board → Stripe (chosen from a 35-board count-only scan) | `b79c317` |
| 06:48 | **Live baseline, Stripe:** 746 postings, 0 reported new | `raw/2026-10-31T10-48-38Z/`, `state/state.json` |
| 06:48 | Base-rate check on the Stripe board: **3 of 20** rule-relevant; 20 postings selected (10 dev / 10 held-out) | `experiments/output/` |
| 06:57 | Tests 36/36 pass; mutation check 37/37 caught | `evidence/tests/`, `7494886` |
| 22:47 | **Second live run, Stripe:** 745 postings, **0 new**. Stripe posted nothing new between 06:48 and 22:47 on a Saturday; one posting was removed. The run id says 2026-11-01 because it is UTC. | `raw/2026-11-01T02-47-55Z/` |
| 22:50 | `judge_v2` (one change) committed before any experiment result | `a6e3aac` |
| 22:59 | Sampling: 5 dev postings × 4 fresh calls, all unanimous; the modal verdict matches the hand label on 3 of 5 | `SAMPLING.md` |
| 22:59 | Action surface, three ways on posting 8113100. The agent surface built about 650 of 745 ids and wrote no state. | `ACTION-SURFACE.md` |
| 23:07 | `LABELING.md` committed before any label | `45fd638` |
| 23:19 | 20 hand labels committed (3 relevant + 7 not, in each split) | `6bd2b52` |
| 23:20 | Prompt experiment: `judge_v1` 8/10 dev, `judge_v2` 8/10 dev (tie → v1 final), `judge_v1` 8/10 held-out (scored once) | `PROMPT-EXPERIMENT.md` |

**What the live runs did not show:** neither live run reported a new posting, so the agent never judged a real new posting live. "New since last run" is shown only by:
- the fixture tests wv19 and wv26–wv30;
- a seeded smoke test (not committed) in which 3 ids were removed from a saved board and came back as new.

## Reports

- [SAMPLING.md](SAMPLING.md): repeated verdicts on 5 postings (Chapter 1).
- [PROMPT-EXPERIMENT.md](PROMPT-EXPERIMENT.md): judge_v1 against judge_v2, dev then held-out (Chapter 2).
- [ACTION-SURFACE.md](ACTION-SURFACE.md): paste, file, or agent, and why the agent gives Claude the least (Chapter 3).
- [SOURCES.md](SOURCES.md) and [FRICTIONAL.md](FRICTIONAL.md).

## Folder

| Path | Contents |
|---|---|
| `agent/` | The watch: persona validator, text preparation, rule, allow-listed fetch, state, Claude judge, line validator, label selection |
| `config/`, `prompts/`, `data/` | Frozen config, prompts, and the fictional persona |
| `raw/`, `state/` | Live runs: raw boards byte for byte, plus state |
| `experiments/` | Runner and outputs (`experiments/output/`) |
| `labels/` | Hand labels |
| `tests/` | Wrong-version tests, stub `claude`, mutation check |
| `tools/` | One-off scripts (scan, reports, action surface) |
| `evidence/` | The morning snapshot, the Databricks base-rate record, test outputs, action-surface outputs |

No real résumé, credentials or transcripts are in this folder. `.gitignore` blocks `private/` and any `resume.json`.

## Sign-off — Job-Search Agent 1

> **DRAFT by Claude. Siddi edits every line, then signs or withholds.**

- **Checked:**
  - Each of the 36 contract wrong versions is caught by its own test (`tests/test_wrong_versions.py`, 36/36), and each test fails when its wrong version is put into the code (`tests/mutants.py`, 37/37).
  - The Appendix C strings appear in the real boards (counts in CONTRACT.md v2).
  - The persona validator rejects real-looking contacts (wv33, wv34).
  - The fetch refuses every host but `boards-api.greenhouse.io` and refuses redirects (wv31).
- **How:**
  - The tests and the mutation check were written by Claude *after* the contract and *after* reading its own code. They are not tests Siddi wrote before reading Claude's code.
  - The wrong versions they target are Siddi's, written before any code.
  - The board-string checks were run by Claude; Siddi decided on the results.
  - The base-rate counts are recomputations by the agent's own code.
- **Not checked:**
  1. New-posting detection against a *live* board change. Stripe posted 0 new postings between the two live runs, so it is shown only on fixtures and a seeded smoke test.
  2. The Claude judge inside a live run on a real new posting. That path ran only against the stub, plus the separate sampling and experiment calls.
  3. Any OS other than Windows 11, or any Python other than 3.13.2.
  4. Whether Greenhouse's `content` HTML keeps the structure that Appendix C v2 relies on. It was verified on one day only.
  5. The rule's verdicts against Siddi's own judgment beyond the 20 hand-labelled postings.
- **Not claiming:**
  - That "relevant" means "worth applying to".
  - That Claude's verdicts are correct.
  - That any of this generalises beyond one board, one persona and one day.
- **Signed or withheld:** ____________ (name, date)

## Driver's seat

| Task | Claude should | Siddi should | Why that part stays Siddi's | Where the split shows |
|---|---|---|---|---|
| The contract | Transcribe it, check its strings against real data, point out ambiguities | Write the rule, the wrong versions, the failure sentence; decide on every flagged ambiguity | The rule is the definition of "worth a day of your life"; only the job-seeker can own it | `be3b6c8` (Siddi's text, transcribed verbatim); the "or" and "about databricks" decisions recorded in that commit |
| The board | Measure base rates across boards | Choose the board when the contract's check fails | Choosing where to look is a judgment about the search, not a computation | `b79c317`; `evidence/base-rate-databricks/README.md` |
| The code and tests | Write them, then try to break them (mutation check) | Read the results, decide what counts as caught | Claude grading its own tests is not independent; the mutation check makes that visible but doesn't fix it | `7494886` (the wv09 miss and its fix) |
| Hand labels | Draw the 20 by seeded code; never show rule verdicts | Write `LABELING.md`, then label all 20 | Labels are the ground truth the experiment is scored against; a model-made label would score Claude against Claude | `LABELING.md` commit; `labels/hand_labels.jsonl` |
| The sign-off | Draft candidate "Not checked" items | Decide what is true, edit, sign or withhold | Signing is the accountable act | This section |
