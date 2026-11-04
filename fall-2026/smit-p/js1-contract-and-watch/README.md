# Job-Search Agent 1 — The Contract and the Watch

**Smit Patel · INFO 7375 · Fall 2026 · Chapters 1–3**

## Executive Summary

For this assignment, I built the first part of a job-search agent that monitors Airbnb's public job board and identifies newly posted jobs. The system keeps track of jobs it has already seen and reports only new postings when it runs again.

For each new job, the system checks whether it matches a fictional candidate's résumé using two approaches. The first is a rule-based approach where the decision can be verified manually. The second uses Claude to evaluate the job based on a prompt. Both approaches provide explanations using information from the résumé and job posting.

During the first run on October 24, 2026, the system found 191 job postings on Airbnb's job board. Out of these, only 3 were considered relevant based on my rule.

One important issue I noticed was that my rule did not consider job location. For example, it marked some Software Engineer positions in Brazil as relevant even though the fictional candidate is a student in the United States on OPT.

Claude also made the same mistake consistently. This showed me that getting consistent results does not necessarily mean the results are correct.

I tried improving the prompt by adding a US-location requirement. This improved the relevance decisions, but it also created a formatting issue because the original output format did not include a way to cite job locations. I have not fixed this issue yet.

For the overall design, I kept the job fetching and tracking logic in Python, while Claude was only responsible for evaluating the job information provided to it.

## Requirements and Tools

| Component | Details |
|---|---|
| Programming Language | Python 3.10+ (tested using Python 3.12.7) |
| Dependencies | Python standard library only; no additional packages required |
| AI Tool | Claude Code CLI 2.1.305 |
| Job Board | Airbnb through the Greenhouse Job Board API |
| Allowed API Domain | `boards-api.greenhouse.io` |
| Candidate | Aarav Patel (fictional résumé stored in `persona/aarav-patel.resume.json`) |
| Model Used | `claude-sonnet-5-5` |
| API Access | Public Greenhouse API using one GET request per run |

I used Claude Code to run the AI-based evaluations. It is only required when using the `--claude` option or running the experiments.

For the experiments, all 60 model calls and the 10 seeded-run calls recorded `claude-sonnet-5-5`.

During the October 28 live run, 7 out of 17 calls also recorded `claude-haiku-5-5`. Since the CLI can use internal models, the earlier implementation only saved the first model name returned. Because of this, I cannot confirm which model generated those 7 responses. I updated the code to save all reported model names using `models_used`.

The system only reads publicly available job information. It does not log in, submit applications, or contact employers.

## How to Run the Project

All commands should be executed from the main project folder.

### 1. Run the Tests

```bash
python3 -m unittest discover -s tests -v
```

This command runs the 27 contract tests and 2 additional hand-check tests.

I also included a mutation check to see whether the tests can detect errors introduced into the code.

```bash
python3 tests/mutation_check.py
```

The mutation check introduces 13 different changes to the code and records which ones are detected by the tests. The results are saved in `tests/mutation-log.md`.

### 2. Run the Job Watcher

```bash
python3 src/watch.py --board airbnb --resume persona/aarav-patel.resume.json --state runs/state.json --out runs/ --label live --claude
```

This command fetches the latest jobs from Airbnb and compares them with previously saved jobs.

When the system runs for the first time with a new state file, it saves the current postings as a baseline and does not report any new jobs.

When it runs again, it compares the job IDs with the saved state and reports only the newly added postings.

### 3. Run the Seeded Tests

I also created a seeded run so the job-tracking behavior can be tested without making additional API requests.

First, run the baseline:

```bash
python3 src/watch.py --board airbnb --resume persona/aarav-patel.resume.json --state /tmp/js1-seeded-state.json --out /tmp/js1-seeded --fixture runs/seeded/earlier-snapshot-SEEDED.json --label seeded-baseline
```

Then run the second snapshot:

```bash
python3 src/watch.py --board airbnb --resume persona/aarav-patel.resume.json --state /tmp/js1-seeded-state.json --out /tmp/js1-seeded --fixture runs/raw-20261024T192545-live.json --label seeded-run2
```

The seeded baseline contains 181 postings. I used a modified version of the original response where the 10 most recently published jobs were removed.

The second run uses the complete response containing 191 postings.

This allows me to verify whether the system correctly identifies those 10 jobs as new.

### 4. Recalculate Experiment Results

```bash
python3 experiments/score.py
```

This command recalculates the experiment results using the saved data. It does not require internet access or additional Claude calls.

### 5. Run the Claude Experiments

```bash
python3 experiments/run_claude.py --set sampling --prompt baseline --repeats 4 --out experiments/results/rerun-sampling.jsonl
```

This command runs the sampling experiment using Claude.

The full set of experiments makes 60 model calls and costs approximately $1.

For the prompt experiments, I can use `--set dev` or `--set held_out` and select either `--prompt baseline` or `--prompt revision`.

## Job Watcher Results

I ran the job watcher using both live API responses and seeded data to check whether it correctly detects newly added postings.

| Run | Date | Total Jobs | New Jobs | Results |
|---|---|---:|---:|---|
| Live Baseline | October 24, 2026 | 191 | 0 | Saved the initial state |
| Seeded Baseline | October 24, 2026 | 181 | 0 | Saved the synthetic baseline |
| Seeded Run 2 | October 24, 2026 | 191 | 10 | Rule: 0 relevant; Claude: 0 relevant |
| Live Run 2 | October 28, 2026 | 194 | 17 | Rule: 0 relevant; Claude: 0 relevant |

### Live Baseline — October 24

During the first live run, the system fetched 191 jobs from Airbnb.

Since this was the first run, all jobs were saved as the baseline. No jobs were reported as new.

The raw API response was saved in:

`runs/raw-20261024T192545-live.json`

### Seeded Run — October 24

For this test, I used a modified snapshot containing 181 jobs as the baseline.

The second snapshot contained all 191 jobs.

The system correctly detected 10 new jobs.

Both the rule-based evaluator and Claude marked all 10 jobs as not relevant. Claude returned 10 valid responses.

### Live Run — October 28

I ran the job watcher again on October 28, 2026.

This time, Airbnb's job board contained 194 postings.

The system identified 17 new job IDs compared with the October 24 baseline. It also found that 14 previously recorded jobs were no longer on the board.

Both the rule-based approach and Claude classified all 17 new jobs as not relevant.

Claude returned 17 valid responses.

The results were saved in:

- `runs/raw-20261028T153510-live.json`
- `runs/run-…-live.json`
- `runs/report-20261028T153510-live.md`
- `runs/state.json`

Additional experiment results and explanations are available in `SAMPLING-REPORT.md`, `PROMPT-EXPERIMENT.md`, `ACTION-SURFACES.md`, `DECISIONS.md`, `SOURCES.md`, and `FRICTIONAL.md`.

## How the Relevance Rule Works

I created a simple rule to decide whether a job is relevant to the fictional candidate.

The rule checks three things:

1. The job title must contain "Software Engineer".
2. The title must not contain senior-level terms such as "Senior", "Sr", "Staff", "Principal", or "Manager".
3. The job description must contain at least two distinct skills listed in the candidate's résumé.

For skill matching, the system uses the résumé's `skills` lists and does not count skills under `familiar_with_not_shipped`.

It also uses whole-word matching to avoid incorrect matches.

For example, Java should not match JavaScript, SQL should not match PostgreSQL, and Go should not match Google.

A job is marked relevant only when all three conditions are satisfied.

For each job, the report includes the matched résumé fields, the corresponding job description text, and the first condition that failed.

This makes it possible to review the decision manually instead of relying only on Claude's response.

## Project Submission

**GitHub Repository:**

`https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/tree/main/fall-2026/smit-p/js1-contract-and-watch`

I submitted the assignment through a pull request from my fork. The folder link will work once the pull request is merged.

The final commit hash is provided separately in Canvas because a commit cannot include its own hash.

## Project Structure

```text
CONTRACT.md
    Project requirements and relevance rules.
    Written before implementation.

src/
    rule.py
    claude_judge.py
    watch.py

tests/
    test_contract.py
    test_hand_check.py
    mutation_check.py
    mutation-log.md

prompts/
    baseline.md
    revision.md

experiments/
    run_claude.py
    score.py
    results/
    labeling files and experiment data

hand-check/
    predictions.json

runs/
    Raw API responses
    Saved state
    Run records
    Generated reports
```

The `CONTRACT.md` file was committed first (`c29d163`), before the implementation.

The `src/` folder contains the relevance rule, Claude evaluation, and job-monitoring logic.

The `tests/` folder contains the contract tests, hand-check tests, and mutation testing.

The `prompts/` folder contains the original and revised prompts.

The `experiments/` folder contains the experiment scripts, labels, model responses, and calculated results.

The `runs/` folder contains the saved API responses, state files, and job reports.

## Final Sign-Off — Job-Search Agent 1

### What I Checked

I reviewed the project results and ran the tests to verify the main functionality.

| What Was Checked | Test or Evidence |
|---|---|
| Rule-based decisions for 7 test postings | `TheRule.test_hand_worked_verdicts` |
| Whole-word skill matching | `TheRule.test_whole_word_matching` |
| Detection of labels assigned to incorrect postings | `WrongVersion1_*` |
| Detection of missing or incorrect citations | `WrongVersion2_*` |
| Baseline and new-job detection | `TheWatch.*` |
| Failed API requests do not modify saved state | `TheWatch.test_failed_fetch_leaves_state_alone` |
| Raw API response is saved without changes | `test_raw_response_saved_untouched` |
| Invalid hosts, URLs, board names, and résumés are rejected | `Refuses.*` |
| Invalid Claude responses are rejected | `ClaudeReplyValidator.*` |
| Tests detect intentionally introduced bugs | `tests/mutation_check.py` |
| Report calculations match saved experiment results | `experiments/score.py` |
| Rule results match predictions for 3 real postings | `tests/test_hand_check.py` |

### Testing Results

I ran the complete test suite myself on October 28, 2026.

At that time, the results were:

```text
Ran 29 tests
OK (skipped=2)
```

The two skipped tests were the hand-check tests because the predictions had not been added yet.

On October 30, I asked Claude to prepare the predictions for three real job postings.

After adding those predictions, the full test suite completed successfully:

```text
Ran 29 tests
OK
```


I also ran the mutation test, which intentionally introduced 13 bugs.

The tests detected 12 of those 13 changes.

The remaining mutation (M1) removed a guard that was already covered by another check, so it did not cause a test failure.

Claude generated the test cases after implementing the code, based on `CONTRACT.md`. I did not independently calculate all the expected test results.

For the experiment reports, I used `experiments/score.py` to recalculate the results from the saved data.

During this process, two incorrect claims in the initial report drafts were identified and corrected.

I also personally provided the 20 hand labels used in the experiments. Three labels were initially inferred by Claude from my rule, but I explicitly confirmed them on October 28.

### What I Have Not Checked

There are still some parts of the project that I have not fully verified.

1. **Duplicate job postings:** The system identifies new jobs using job IDs. On October 28, job ID `7826337`, "Machine Learning Engineer, Assistance Engineering", was marked as new even though another posting with the same title already existed under ID `7716341`. I have not checked whether these represent different positions or duplicate postings.

2. **Expected test results:** Claude calculated the expected results for the contract tests and the three hand-check predictions. I checked the three hand-check predictions by hand; I have not re-derived the contract tests' expected results.

3. **Other job boards:** I tested the system using Airbnb's Greenhouse board. I have not tested it on other companies, non-Greenhouse platforms, or different HTML structures.

4. **Model consistency:** I have not tested Claude's decisions using different temperatures, different models, or across multiple days.

5. **Actual job suitability:** The rule identified 3 relevant jobs, but I have not verified whether those positions are actually suitable for the candidate based on location, sponsorship, or required experience.

6. **Pagination:** I have not tested how the system behaves when a job board returns multiple pages of results.

### Limitations

The current system is designed to apply a predefined relevance rule. It does not guarantee that the jobs it identifies are good opportunities for the candidate.

One limitation is that the rule does not consider job location, which caused some jobs outside the United States to be marked as relevant.

The experiment results also have limitations. For example, a score of 9 out of 10 is not enough to establish strong performance when the test set contains only one positive example.

I also do not treat Claude's decisions as automatically correct. The model can give consistent answers while still making mistakes.

Although the revised prompt improved the location-based decisions, it introduced an output-format problem. Because of this, I cannot conclude that the revised prompt is better overall.

## My Role and Claude's Role

I used Claude Code to help with implementation, testing, and documentation, but I made the main decisions about what the system should do.

| Part | Claude's Contribution | My Contribution |
|---|---|---|
| Contract | Suggested options, prepared documentation, and implemented the requirements | Selected the job board, persona, relevance rule, incorrect versions, and failure condition |
| Hand Labels | Presented job information and initially inferred three labels | Provided and confirmed all 20 labels |
| Labeling Rule | Identified inconsistencies between the rule and labels | Decided how to update the rule |
| Code and Testing | Generated the code, tests, and experiment scripts | Ran the tests, reviewed results, and performed the live day-2 run |
| Job Decisions | Evaluated jobs and provided supporting evidence | Decided how to interpret the results and whether a job was worth considering |
| Final Review | Helped prepare the documentation and sign-off | Reviewed the final work and signed it |

I kept the contract decisions and labeling process under my control because these define how the system is evaluated.

Claude helped with implementation and experimentation, but I was responsible for understanding the results and checking whether the project followed my requirements.

The decisions are documented in `DECISIONS.md`, and the complete breakdown of contributions is available in `SOURCES.md`.

## Final Confirmation

I reviewed the assignment requirements, test results, experiment outputs, and project documentation.

I understand that the system has limitations, especially with job location, duplicate postings, and the independence of the tests.

I used Claude Code for implementation, testing, and drafting documentation. The main project decisions, labeling rules, and hand labels were provided by me.

I ran the tests and the live job watcher, reviewed the results, and confirmed the final submission.

**Signed:** Smit Patel  
**Date:** October 30, 2026