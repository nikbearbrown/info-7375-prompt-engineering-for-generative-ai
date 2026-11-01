# Job-Search Agent 1: The Contract and the Watch

The agent watches one public Greenhouse board (Figma) for a fictional persona, **Jack Spencer** (a data engineer with 5 years of experience and a master's degree). For each posting that is new since the last run, it gives two verdicts:
- a **rule** verdict, which is a record anyone can recompute by hand from `CONTRACT.md`;
- a **Claude** verdict, which is a judgment, always labeled as model output.

The contract was written and committed before any code: `CONTRACT.md`, commit `5ca21ed` (2026-10-31 19:14 ET).

## Language and toolchain
- **Python 3.12.10**, standard library only. There's nothing to `pip install`.
- **Tests:** `unittest` (standard library).
- **Claude Code CLI 2.1.316** for the Claude judge (`npm install -g @anthropic-ai/claude-code`, then run `claude` once to log in). The judge model is fixed at `claude-opus-5-5`.
  - Every judge call is a fresh `claude -p` session with `--safe-mode --tools "" --no-session-persistence`, and the prompt contract replaces the system prompt.
  - Without the CLI, use `--no-claude` and everything else still runs.
- **Network:** only `https://boards-api.greenhouse.io` (the allow-list).
- Developed on Windows 11. The commands below work in PowerShell or bash from the repo root.

## Exact commands

```bash
# 1. Tests (no network, no Claude)
python -m unittest discover -s tests -t . -v

# 2. The watch, as it was run (see "What ran")
python -m agent.fetch --board figma                                    # live fetch, saved as evidence
python scripts/make_seeded_snapshot.py evidence/raw/<stamp>_figma_live.json --remove 10   # SEEDED earlier snapshot
python -m agent.run --board figma --resume data/resume_jack_spencer.json \
    --from-file evidence/raw/<stamp>_figma_SEEDED_earlier.json         # run 1: baseline (SEEDED input)
python -m agent.run --board figma --resume data/resume_jack_spencer.json   # run 2: live fetch, both judges

# 3. Chapter artifacts
python experiments/sampling.py run --raw evidence/raw/20261031T233955Z_figma_live.json \
    --ids 6201407004 5551686004 6233040004 5551532004 5552549004 --n 4
python experiments/sampling.py report experiments/results/sampling_20261031T234336Z.json
python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set dev
python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set dev
python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set heldout --final
python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set heldout --final
python experiments/action_surface.py --id 6233040004
```

**To rerun from a fresh clone without touching the committed evidence,** delete or move `state/seen_ids.json` first. Otherwise run 1 is not a baseline. You can also pass `--state` and `--runs-dir` to point at scratch locations.

## What ran (2026-10-31)

| Time (UTC) | What | Evidence |
|---|---|---|
| 23:38:58 | Live fetch of the Figma board: HTTP 200, 140 postings | `evidence/raw/20261031T233858Z_figma_live.json` (+ `.meta.json` with sha256) |
| 23:39 | **SEEDED** earlier snapshot: the same response minus its 10 highest-id (newest) postings, 130 left | `evidence/raw/20261031T233858Z_figma_SEEDED_earlier.json` (+ meta listing removed ids) |
| 23:39:44 | **Run 1, baseline, on the SEEDED file.** It reported 0 new and saved 130 ids | `runs/20261031T233944Z_figma_baseline.txt` |
| 23:39:55 | **Run 2, live fetch.** 140 postings, 10 new, both judges. All 10 Claude replies passed the validator, and Claude agreed with the rule on 10 of 10 | `runs/20261031T233955Z_figma_run.txt`, `evidence/raw/20261031T233955Z_figma_live.json`, `state/seen_ids.json` |
| 23:43 | Sampling: 5 postings × 4 fresh Claude sessions. 20 of 20 replies valid, 20 distinct sessions | `experiments/results/sampling_20261031T234336Z.json` |
| 23:45 | Action-surface runs: paste, file, agent | `experiments/results/action_surface_20261031T234559Z.json` |

**The change between runs is seeded, not a real change on the board.** The two live fetches (23:38:58 and 23:39:55) had identical id sets. Run 2's 10 new ids are exactly the 10 removed to make the seeded file. I checked this by script against the meta file and the run JSON.

Tests: `python -m unittest discover -s tests -t . -v` ran 32 tests, all passing. This includes the checks that catch the contract's wrong versions:
- **W1** (verdicts paired with the wrong postings) is caught for both judges, including when Claude's replies arrive out of order.
- **W2** (substring skill matching) is caught.

The wrong versions themselves live in `tests/wrong_versions.py`.

## Failure conditions from CONTRACT.md (written before running)

| # | Condition | Status |
|---|---|---|
| 1 | A rule verdict differs from the rule applied by hand | _to check by hand: ____ _ |
| 2 | Baseline reports any posting as new, or run 2 reports an already-seen id | **Did not happen.** Run 1 reported 0 new; run 2's 10 new ids equal the seeded removals |
| 3 | Figma's "Data Platform Engineer" comes out `not_relevant` | **Happened.** The rule says `not_relevant` for posting 6201407004: the title matches "Data Platform", but its content has only 1 of Jack's 8 skills (Python). The only "AWS" is inside "Washington", correctly not counted. |
| 4 | A Claude verdict lacks its judgment label, or an invalid answer is shown | Did not happen in run 2 (10/10 labeled and valid). No invalid answer occurred, so the rejection path ran only in tests. |
| 5 | Rule disagrees with my hand labels on more than 4 of 20 | _pending hand labels_ |

## Files
- `CONTRACT.md`: the contract.
- `agent/`: the code, with these modules:
  - `fetch.py`: allow-listed fetch and evidence.
  - `resume.py`: persona validator.
  - `rule.py`: the rule judge.
  - `claude_judge.py`: the Claude judge and its validator.
  - `watch.py`: state handling.
  - `run.py`: the driver.
- `prompts/judge_baseline.md`: the Claude prompt contract.
- `data/resume_jack_spencer.json`: the fictional persona (`@example.com`, 555 number).
- `evidence/raw/`: saved responses (live and SEEDED).
- `state/seen_ids.json`: the state file.
- `runs/`: run reports.
- `experiments/`: sampling, prompt experiment, labels, action-surface runs, and `results/`.
- `ACTION_SURFACE.md`, `SOURCES.md`, `FRICTIONAL.md`.

## Sampling report
_(after hand labels: paste the table from `sampling.py report` and my conclusion)_

## Prompt experiment
_(after hand labels: the labeling rule, the one change, the dev and held-out pass rates, and the limits)_

## Sign-off: Job-Search Agent 1

- **Checked:** ____
- **How:** ____
- **Not checked:** ____
- **Not claiming:** ____
- **Signed or withheld:** ____________ (name, date)

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Where it shows |
|---|---|---|---|---|
| The contract | asked one question per section and offered options | made every decision | ____ | commit `5ca21ed`; suggestions marked in CONTRACT.md |
| Code and tests | wrote them against the contract | ran the tests and checked them against the contract | ____ | ____ |
| Hand labels | built a blind sheet with no verdicts | labeled the postings | ____ | `experiments/labels.csv` |
| Is a posting worth Jack's time? | gives a labeled judgment | ____ | ____ | ____ |
| Sign-off | nothing | ____ | ____ | ____ |
