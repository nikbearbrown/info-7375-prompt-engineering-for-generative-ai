# SOURCES — what I used, what I wrote, what Claude contributed

The initial inventory was drafted from the git history and session record. I checked the entries below and corrected the description of the labels and my own review.

## Tools and references used

- **Claude Code** (desktop app, model `claude-opus-5-5`): implementation, tests, tooling, report drafts, and commits. Session transcript kept on my machine, not submitted.
- **A separate AI assistant (not Claude Code):** drafted the first five-check labeling rule and the initial 20 CSV rows. I reviewed and revised the rule, then, after the rows were committed at 01:35 and before the split at 02:02, read all 20 full postings and checked each label. No label changed.
- **Claude API** (`claude-opus-5-5`, effort `medium`): the second judge. 62 completed API calls: 2 in live run 2 and 60 in sampling and the experiment. 4 of the 60 returned output the validator rejected.
- **claude.ai** (Opus 5.5): three new conversations on 2026-10-31 for action surfaces 1 and 2, run by me; replies saved in `experiment/action_surface/`.
- **Greenhouse Job Board API**, public endpoint `boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` ([documentation](https://docs.greenhouse.io/job-board)).
- **SEVP STEM OPT overview** ([PDF](https://studyinthestates.dhs.gov/assets/SEVP_PracticalTrainingOverview_1-pager.pdf)), cited in CONTRACT.md for the E-Verify requirement.
- **Fictional persona Aarav Patel,** from the supplied Reallocation Engine example. Its header mentions a Summer 2026 authorization fix (PR #37), which I did not independently verify.
- **Python 3.14.5, `anthropic` 2.3.0, `jsonschema` 4.26.0, `pytest` 9.2.0.**

## What I wrote or decided

| Item | Where |
|---|---|
| CONTRACT.md v1 | `2091127` |
| CONTRACT.md v2, revised after checking live board data | `021999d` |
| Résumé fields added to match the contract | `994646d` |
| Review of the first implementation: accept / modify / reject list (see FRICTIONAL.md) | applied in `87f68dd` |
| The labeling rule: I reviewed and revised an assisted first draft, adding the posting selection and split seed before labeling | `a6b6e62`, `ba2a709` |
| Prompt revision 1, the one added sentence | `ba3a9b8` |
| Choice of posting selection and split seed 7375 | `ba2a709` |
| The seeded response: I ran the command that removed two postings | `37d77e4` |
| The 20 labels: assisted draft rows that I checked against all 20 full postings and adopted, then committed | `2edbefa` |
| Accepting the one-note correction to the labels | `335d280` |
| Running watch runs 1 and 2, sampling, and the experiment in my terminal | `5fc0b68`, `30e722c` |
| Review and edits to the reports, sign-off, and this file | the commit that adds this line |

## What Claude contributed

| Item | Where | My check |
|---|---|---|
| Review of contract v1 against the live board, including probing 13 Greenhouse boards | before `021999d` | I checked all 13 board probes and confirmed why the first board would have no Boston or remote matches and why Klaviyo was chosen. |
| Tests from the contract, written before any implementation existed | `5cef19a` | I ran the original tests but did not read their assertions closely or edit them. |
| All of `jsagent/`, `resume.schema.json`, `prompts/baseline.txt`, `tools/check_wrong_versions.py` | `1397a6f` | I reviewed these and requested changes in `87f68dd` |
| Changes from my review, plus `tests/test_review_fixes.py` | `87f68dd` | I read the changed behavior and new tests, and checked that the new tests failed on the old version and passed after the fixes. |
| Experiment tooling (`experiment/*.py`) and its tests | `0fbaaad`, `721935a` | I read the scripts and tests, ran the sampling and experiment commands, and checked raw outputs against their summaries. |
| Credential check, added after run 2 first crashed | `b1aa320` | I read the guard and its test, checked that a missing key is refused before fetching, and reran the live watch successfully. |
| Consistency check of my labels against the objective parts of my rule; it found one wrong note and changed no labels | `335d280` | I accepted the correction |
| Drafts of SAMPLING_REPORT.md, EXPERIMENT_REPORT.md, ACTION_SURFACES.md, this file, FRICTIONAL.md, and the sign-off | `144b089`, `262067e`, `bc111c4` | I reviewed the reports against saved results, corrected their conclusions and attribution wording, and filled the reflections and check notes. The signature remains mine to decide. |
| Commit attribution and trailers through `0a373a2` | git log through `0a373a2` | I inspected the git log and checked author and co-author details for the existing commits. |

## Commit history note

Before the first push, on 2026-10-31, I had the commit messages reworded and one correction folded into the commit it corrected, which changed every hash. The files at the final commit did not change. The run summaries in `experiment/results/` and `experiment/sampling/` record the prompt's last commit as it was when they ran, so they show the earlier hashes:

| Recorded in the run summaries | Same commit now |
|---|---|
| `b348e255c7cc…` (baseline prompt) | `87f68dd` |
| `e628727305aa…` (revision 1 prompt) | `ba3a9b8` |

The prompt files' sha256 values in those summaries are unaffected.
