# SOURCES

## Executive Summary

This document explains the sources and tools I used for this assignment, along with what I worked on myself and what was generated using Claude Code.

I used Claude Code (Opus 5.5) to help with coding, testing, and writing the documentation. Claude generated the code and initial drafts of the documents, while I made the main decisions about the project, including the contract requirements, relevance rules, and all 20 hand labels.

For the job monitoring implementation, I referred to the design used in *The Reallocation Engine* and built a smaller version for this assignment.

## Sources Used

| Source                                                                                                                         | How I Used It                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *The Reallocation Engine* (github.com/nikbearbrown/the-reallocation-engine), `search/examples/aarav-patel/resume.example.json` | Used the fictional persona résumé without making any changes and placed it in the `persona/` folder.                                                                                                                                              |
| *The Reallocation Engine*, `.claude/skills/greenhouse-watch/`                                                                  | Used the overall design for fetching job data, saving raw responses, comparing job IDs, handling the first run as a baseline, and updating state at the end. I implemented a smaller version in `src/watch.py` without copying the original code. |
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true`                                | Used to fetch live job postings on October 24, 2026.                                                                                                                                                                                              |
| Course Chapters 1–3 and assignment instructions                                                                                | Followed these for the report structure and final sign-off requirements.                                                                                                                                                                          |
| Python 3.12 and Claude Code CLI 2.1.305                                                                                        | Tools used to develop and run the project.                                                                                                                                                                                                        |

## My Contributions (Smit Patel)

I was responsible for making the main decisions for the assignment and reviewing the results.

- I decided the requirements in `CONTRACT.md`, including the job board, persona, relevance rule, two incorrect versions, and failure sentence. These decisions are recorded in `DECISIONS.md` (D1–D6). Claude helped convert my decisions into written documentation.
- I defined the hand-labeling rule and later made an amendment to it (D7 and D10).
- I provided all 20 hand labels (D8, D9, and D11). Initially, Claude inferred three labels based on the rule I provided, but I explicitly confirmed those labels myself on October 28, 2026 (D12).
- I completed the live day-2 run on October 28, 2026 (D14).
- I reviewed the final README sign-off and signed it on October 30, 2026.
- I asked Claude to generate the hand-check predictions on October 30, 2026, and then checked each one by hand myself. This is also recorded in `hand-check/predictions.json` under the `by` field.
- Wrote the Frictional.md file.

## Claude Code Contributions

I used Claude Code (Opus 5.5) during the development process, starting on October 24, 2026. It helped me implement the project, run experiments, and prepare the documentation.

Claude generated the following parts:

- **Implementation:** All Python code in `src/rule.py`, `src/watch.py`, `src/claude_judge.py`, `experiments/run_claude.py`, and `experiments/score.py`.
- **Testing:** The tests in `tests/test_contract.py` and the two test fixtures. Claude also calculated the expected test results based on `CONTRACT.md`. I have not independently verified all those expected results by hand.
- **Prompt experiments:** Both prompt contracts in the `prompts/` folder, including the selected revision.
- **Mutation testing:** The `tests/mutation_check.py` script, which intentionally introduces errors to check whether the tests can detect them.
- **Project review:** On October 28, I used a separate Claude subagent to review the project from a TA's perspective. It reviewed the assignment instructions and project folder and identified 15 findings. The findings and the changes made are documented in `FRICTIONAL.md` (F15–F24).
- **Experiment execution:** Claude Code ran the live fetches, seeded runs, and 60 + 3 Claude model calls.
- **Documentation:** Claude prepared the initial drafts of `README.md`, `SAMPLING-REPORT.md`, `PROMPT-EXPERIMENT.md`, `ACTION-SURFACES.md`, `DECISIONS.md` and `SOURCES.md`.

For the experiments, I used the `claude-sonnet-5-5` model. Its responses are saved in `experiments/results/*.jsonl` and were used as experimental data.

Overall, I used Claude Code mainly for implementation, testing, experiments, and documentation. My contributions were defining the project requirements, making the important decisions, providing the hand labels, and reviewing the final work.
