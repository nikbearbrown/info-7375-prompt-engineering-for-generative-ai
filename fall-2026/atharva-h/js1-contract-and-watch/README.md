# Job-Search Agent 1 — The Contract and the Watch

Atharva Hambir · INFO 7375 · Fall 2026

The agent watches one public job board, the Greenhouse board for Abacus Insights, and reports only postings that are new since its last run. Each new posting gets two verdicts:

- a **record** from my written rule, which anyone can recompute with `rule.py`
- a **judgment** from Claude under a fixed prompt contract, which a validator rejects unless it matches the format exactly

Every verdict cites the résumé fields and posting fields behind it. The résumé is a fictional persona. [CONTRACT.md](CONTRACT.md) was written and committed (`963f9f1`) before any code.

## Language and toolchain
- **Python 3, standard library only.** Nothing to install. Tested only with Python 3.14.7 on macOS (Darwin 25.5).
- **Network:** live runs fetch only `boards-api.greenhouse.io`. Every other host is refused in code, and so is any redirect to another host.
- **Claude, optional:** `python3 watch.py run --claude` calls `claude -p` with all tools disabled and needs a logged-in Claude Code CLI. **That path was not exercised for this submission.** The CLI on my machine wasn't logged in (see [FRICTIONAL.md](FRICTIONAL.md)), so every Claude verdict here came from fresh Claude Code subagents. Each subagent read one prompt file and wrote its raw answer to a file. `watch.py validate-claude` validates those files no matter how they were produced.

## Commands

Run everything from this folder:

```bash
cd fall-2026/atharva-h/js1-contract-and-watch
```

**Tests** (offline; expect `Ran 43 tests ... OK`):

```bash
python3 -m unittest discover -s tests
```

**Replay both runs offline** from the saved responses. This writes to `state/replay_seen_ids.json` and new folders in `runs/`, and leaves the submitted state alone.

First, the seeded baseline:

```bash
python3 watch.py run --state state/replay_seen_ids.json --from-file runs/seed/earlier_response_SEEDED.json --label REPLAY-SEEDED-baseline
```

Then the second run against run 2's saved live response:

```bash
python3 watch.py run --state state/replay_seen_ids.json --from-file runs/2026-10-31T175126Z/raw.json --label REPLAY-of-run2
```

To replay from scratch, remove `state/replay_seen_ids.json` first. Otherwise the first command isn't a baseline and reports 0 new against the submitted replay state.

**A live run** against the real board. It reports postings new since the submitted state.

```bash
python3 watch.py run
```

**Re-validate saved Claude outputs** for a run:

```bash
python3 watch.py validate-claude runs/2026-10-31T180105Z_REPLAY-of-run2-v2-prompt
```

**Recompute the experiment scores** from the saved raw outputs and the labels:

```bash
python3 experiments/experiment.py score --variant v2_path_syntax --set held_out
```

```bash
python3 experiments/experiment.py sampling
```

## What ran (2026-10-31)

| Run | Source | Postings | New | Rule (record) | Claude (judgment) |
|---|---|---|---|---|---|
| `runs/2026-10-31T174655Z_SEEDED-baseline` | **SEEDED** earlier response (`runs/seed/`) | 13 | 0 (baseline) | none | none |
| `runs/2026-10-31T175126Z` | live fetch | 18 | 5 | 5 × `not_relevant` | v1 prompt: **5/5 rejected** by the validator (path syntax) |
| `runs/2026-10-31T180105Z_REPLAY-of-run2-v2-prompt` | offline replay of run 2's raw response | 18 | 5 | 5 × `not_relevant` | v2 prompt: 5/5 valid, all `not_relevant` |

**Why the baseline is seeded.** No board response was saved before 10-31, so a real second calendar day would have fallen after the deadline. `seed.py` fetched the board once, saved that response, and removed the 5 most recently first-published postings. That copy is the "earlier" response. [runs/seed/SEED.json](runs/seed/SEED.json) lists exactly which postings were removed.

Separately, a real change did happen: "Senior Business Intelligence Analyst (Healthcare)" was first published 10-30 and wasn't on the board when I listed it on 10-28. Nothing from 10-28 was saved, so that isn't evidence.

## How the code reads my rule

The rule is in [CONTRACT.md](CONTRACT.md). The code needs a mechanical reading of three checks. Claude proposed these readings and I accepted them on 2026-10-31. They live in `rule.py`.

- **Location.** The code reads `location.name` and every `offices[]` name and location.
  - **US:** "United States", "USA", "U.S.", "US", "US Remote", "Remote - US", a "City, ST" with a US state code, or a US state name. US is checked before countries, so "New Mexico" isn't read as Mexico.
  - **Non-US:** any named country.
  - **Unknown:** "Remote" alone, or a city with no country.
  - **Combining:** within one field, one US place is enough. If one field is only US and another is only non-US, the fields conflict and the result is `needs_human`. "Georgia" is read as the US state.
- **Sponsorship.** The code matches fixed phrase lists against the description text, in this order:
  1. a denial or limit, which gives `not_relevant`
  2. "may", "might", or "case-by-case", which gives `needs_human`
  3. an explicit offer, which passes
  4. nothing found, which gives `needs_human`
- **Experience.** The code looks for "N+ years", "at least N", "minimum of N", "N or more", and "N–M years" (a range counts as its first number), only in sentences about experience.
  - **N ≤ 2:** passes.
  - **N > 2:**
    - If the sentence or its section heading says preferred, nice to have, bonus, ideally, or plus, the requirement is ignored.
    - If it says required, must, minimum, or qualifications, it gives `not_relevant`, unless the same sentence offers a master's degree instead.
    - Otherwise it gives `needs_human`.

## Where things are

| Path | What |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, wrong versions, failure sentence |
| `watch.py`, `rule.py`, `judge.py`, `persona.py`, `seed.py` | The agent |
| `persona/resume.json` | Fictional persona: `@example.com`, a 555 number, `"_fictional": true`, checked on every run |
| `prompts/` | v1 baseline and v2 (one sentence added) prompt contracts |
| `tests/` | 43 tests, including both wrong versions as mutants the tests catch |
| `runs/`, `state/` | Raw responses, verdicts, Claude raw outputs, per-run `report.md`, and the seen-ids state |
| `experiments/label_pool/` | The 20 postings, raw board responses, and labels (`LABELS.md`) |
| `experiments/sampling/`, `experiments/prompt/` | Every prompt sent and every raw answer |
| `experiments/action_surface/` | The three-ways comparison evidence |
| [SAMPLING.md](SAMPLING.md), [PROMPT_EXPERIMENT.md](PROMPT_EXPERIMENT.md), [ACTION_SURFACE.md](ACTION_SURFACE.md) | The three Chapter artifacts |
| [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) | Provenance and the honest log |

## Sign-off — Job-Search Agent 1

**Checked:**
- **Watch logic.** A previously seen posting is never reported as new; the first run is a baseline with 0 new; a posting that leaves and comes back isn't reported as new. Tests: `test_second_run_reports_only_unseen_ids`, `test_a_removed_posting_is_not_new_when_it_returns`, `test_first_run_is_a_baseline_that_reports_nothing_new`.
- **Allow-list.** Other hosts and redirects are refused. Tests: `AllowList`.
- **No `relevant` despite a clear exclusion.** Tests: `ExclusionsFirst`.
- **Fabricated quotes are rejected.** A Claude justification quoting a value that isn't in the posting or résumé fails validation. Tests: `test_quoted_value_absent_from_posting_is_rejected` and `..._resume_...`.
- **Both wrong versions are caught.** Tests: `test_the_broad_keyword_mutant_is_caught` and `test_the_silence_means_rejection_mutant_is_caught`.
- **Live run.** The live run reported exactly the 5 seeded-out postings.
- **Labels.** Claude's verdicts were compared against my 20 hand labels in `PROMPT_EXPERIMENT.md` and `SAMPLING.md`.
- None of the 20 selected postings explicitly offers H-1B sponsorship, so a `relevant` verdict has only been exercised in unit tests, never on a selected real posting.

**How:**
- The rule, the wrong versions, and the failure sentence were committed before any code (`963f9f1`). `SOURCES.md` records the drafting help.
- Claude wrote the code and the tests from that contract.
- I ran the test suite myself on 2026-10-31: `Ran 43 tests ... OK`. Python also emitted ResourceWarnings for unclosed files in `tests/test_watch.py`.
- I hand-labeled the 20 postings with my rule, from a sheet that showed no rule or Claude verdicts.
- Scores are recomputed by `experiments/experiment.py` from saved raw files.

**Not checked:**
- The sponsorship and experience phrase lists were tested on hand-written sentences and 20+ real postings. Phrasings outside those lists aren't recognized; for example, a city without a country reads as unknown.
- The subagent "fresh conversations" ran inside Claude Code with its own system prompt, and possibly this repository's instructions loaded. That isn't the same as a bare API call, and I didn't measure the effect.
- Greenhouse slugs were matched to employers on my H-1B list by name only; the legal entities weren't confirmed.
- Only one person labeled, so I don't know how noisy the labels are.

**Not claiming:**
- That Claude's verdicts are correct beyond the 20 labeled postings.
- That any posting is worth applying to.
- That silence about sponsorship means a company won't sponsor.
- That a day-over-day change was observed; run 2 compares against a seeded baseline.

**Signed or withheld:** **Signed** Atharva Hambir,(2026-10-31).

### Driver's seat

| Part of the task | Claude should | I should | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| The rule, wrong versions, failure sentence | Interview me, draft, and point out what a TA couldn't compute | Review and choose the rule | A TA predicts my verdicts from it, and I'm accountable for the choice | Commit `963f9f1`; `SOURCES.md`; FRICTIONAL 2026-10-31 "Contract finished" |
| Fixing the rule's title list | Point out the conflict with the persona | Decide which wins | It changes what counts as relevant | FRICTIONAL 2026-10-31 "Title edit" (Claude deleted two titles at my request) |
| Hand labels | Build a sheet with no verdicts on it | Label all 20 | Labels are what everything is scored against | `experiments/label_pool/LABELS.md`; FRICTIONAL "Labels and test check" |
| Code, tests, runs, validation | Write and run them | Run the tests myself and decide whether to sign | I sign for what ships | FRICTIONAL "Build, tests" and "Labels and test check" entries |
| The one prompt change | Show the failure pattern and recommend a change | Choose the change | The experiment tests my hypothesis, not Claude's | FRICTIONAL "v2, held-out" entry |
| Autonomy choice | Run the three surfaces and report what each could do | Choose and defend | I own what the agent is allowed to touch | `ACTION_SURFACE.md` "The autonomy I choose" |
| Sign-off | Draft from evidence | Signed | Only I know what I didn't check | This section |
