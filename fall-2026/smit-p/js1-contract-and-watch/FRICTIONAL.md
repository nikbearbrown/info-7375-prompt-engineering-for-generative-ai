# FRICTIONAL — What Happened During the Project

## Executive Summary

This document explains the challenges I faced while working on Job-Search Agent 1, how I approached them, what changes I made, and what I learned during the process.

I worked on the initial implementation and experiments on October 24, 2026, and continued testing and improving the project on October 28 and October 30.

During development, I encountered several issues related to relevance rules, job classification, test coverage, API responses, and prompt consistency.

I made the main project decisions, defined the relevance criteria, reviewed the results, and decided how to address the issues. I used Claude Code to help implement changes, execute tests, and prepare documentation.

Some issues were resolved, while others remain limitations of the current implementation.

## Challenges and Changes

| # | Problem I Encountered | What I Did | Result |
|---|---|---|---|
| F1 | Initially, I had defined only one incorrect version, but the assignment required two. | I reviewed the requirements and selected "Empty justification" as the second incorrect version. | Resolved. Both incorrect versions were included in the contract. |
| F2 | All 23 tests passed during the first run, but I wanted to check whether they could detect actual bugs. | I used mutation testing to introduce errors into the implementation and evaluate the tests. | The initial tests detected 5 of 7 mutations. I strengthened the tests to catch shifted labels. |
| F3 | The first random sample contained 19 senior-level jobs out of 20, which would make the experiment unbalanced. | The sample was redrawn using seniority-based stratification before labeling. | The revised sample provided better coverage, although the selection change was made by Claude. |
| F4 | Airbnb had only 6 non-senior engineering jobs out of 52 engineering postings. | I included all 6 non-senior positions in the sample and reviewed the classification results. | Only 1 of the 20 sampled jobs was relevant. The board was not ideal for a new-graduate candidate. |
| F5 | While labeling the held-out data, I realized that my intended relevance criteria were narrower than the original rule. | I clarified the criteria to focus on Software Engineering, Cloud, and Full-Stack positions with approximately 3–4 years of experience or less. | I updated the labeling rule to version 2 and documented the amendment. |
| F6 | One job label was initially recorded as "No preference". | I reviewed the posting and explicitly selected "Relevant". | The label was finalized. |
| F7 | My original rule considered some Brazil-based jobs relevant even though the candidate was a US student on OPT. | I examined the issue and evaluated a revised prompt with a US-location requirement. | The revised prompt improved location-based decisions, but the original contract rule remained unchanged. |
| F8 | The revised prompt generated correct location-based decisions but failed the required response format for 3 cases. | I reviewed the rejected responses and identified that the output format did not support location citations. | The issue remains unresolved because changing the output format would require another modification. |
| F9 | One sampling response referenced `devops_cicd[0]` instead of the required `skills.devops_cicd[0]`. | I checked the validation behavior and kept the strict citation requirement. | The response was correctly rejected. |
| F10 | The agent with fetch and write tools made an incomplete API request and produced a wrong decision that passed validation. | I reviewed the tool behavior and compared it with the restricted implementation. | I decided to keep fetching and state management in Python rather than giving Claude full control. |
| F11 | A shell command failed because of how zsh interpreted part of the command. | I ran the affected command separately. | The command completed successfully. |
| F12 | I needed to demonstrate two different runs, but a real second calendar day was not possible during the initial session. | I used a clearly labeled seeded run and later performed a real second live run on October 28. | The live run detected 17 new jobs, with 0 relevant under both evaluators. |
| F13 | Some job titles displayed `&amp;` instead of `&`, which initially looked like an encoding issue. | I checked the saved raw API response to identify the source of the difference. | The raw data was correct. The issue was only in the displayed output. |
| F14 | A job was marked as new even though another posting with the same title already existed. | I compared the job IDs and reviewed the contract definition of a new posting. | The behavior was correct under the ID-based rule, but duplicate detection remains unverified. |

## Additional Review Before Submission

On October 28, I wanted to make sure the project satisfied the assignment requirements.

I requested a detailed review of the project against the grading rubric because I wanted to identify missing requirements or weak areas before submission.

I used a separate Claude reviewer to examine the assignment instructions and project files. The review identified 15 issues, which I then used to guide further corrections and improvements.

### Issues Identified During Review

| # | Issue | Action Taken |
|---|---|---|
| F15 | The assignment required abbreviated names, but some files contained my full name. | I updated the affected files to use "Smit P." and documented the change to `CONTRACT.md`. |
| F16 | Three held-out labels had been inferred from my rule instead of being explicitly selected by me. | I reviewed those postings and confirmed all three labels myself. The provenance correction was documented. |
| F17 | The prompt experiment report did not accurately describe when the revised prompt was selected. | I checked the experiment timestamps and updated the report to reflect the actual sequence. |
| F18 | The action-surfaces report incorrectly attributed all five permission denials to agent mistakes. | I reviewed the recorded tool calls and corrected the explanation of each denial. |
| F19 | Seven day-2 records showed `claude-haiku-5-5` because only the first model listed by the CLI was saved. | I updated the implementation to record all reported model names using `models_used`. |
| F20 | Some tests for the first incorrect version were too weak to detect shifted labels. | I strengthened the tests to check every shifted label, same-title postings, and end-to-end behavior. |
| F21 | An earlier mutation-testing claim was not supported by a saved log. | I added a reproducible mutation-testing script and saved the results. |
| F22 | The validators accepted incomplete citations and some invalid references. | I improved the validation checks and revalidated the saved Claude responses. |
| F23 | Some descriptions in the contract and selection files did not fully match the implementation. | I documented the differences using errata instead of silently changing the original records. |
| F24 | Some report descriptions did not accurately distinguish between my actions and automated execution. | I corrected the wording to make the project workflow clearer. |

### Mutation Testing Issue — F25

On October 30, I noticed an unexpected result during mutation testing.

Previously, the mutation test detected 12 out of 13 intentionally introduced changes.

After adding the hand-check tests, the result unexpectedly increased to 13 out of 13.

I investigated this result because the remaining mutation should not have been detected.

The issue was in the mutation-testing setup. It copied the `src/`, `tests/`, and `persona/` folders but did not copy the `hand-check/` folder.

Because of this, the new hand-check test failed due to a missing file. The mutation-testing script incorrectly counted that failure as a successfully detected mutation.

I corrected the testing setup so that all required files were included. I also added a check to make sure the unmodified project passed before running the mutations.

After the correction, the result returned to 12 out of 13 mutations detected.

This helped me understand why test results should be verified instead of assuming that a higher score always means better testing.

### Hand-Check Testing — F26

On October 30, I added an additional verification step to compare the rule's decisions with predictions for three real job postings.

I used Claude to generate the predictions from the posting text and saved them in `hand-check/predictions.json`.

The file records that Claude generated the predictions.

When I ran the tests, both hand-check tests passed.

I also found that the original test command did not work because the `tests/` directory was not configured as a Python package.

I corrected the command to use test discovery.

Although the tests passed, I recognize that this was not a fully independent verification because Claude generated both the implementation and the predictions.

## What I Learned

### 1. Consistent Results Are Not Always Correct

One of the most interesting things I noticed was how consistently Claude classified a Software Engineer position in São Paulo as relevant.

Every time I tested the original prompt, Claude made the same decision.

However, the fictional candidate was a US student on OPT, so a position in Brazil was not necessarily a suitable opportunity.

This showed me that consistent AI responses do not automatically mean the decisions are correct.

It also showed me why it is important to define the evaluation criteria carefully before running experiments.

### 2. Choosing the Right Data Matters

Another challenge was the job board itself.

I selected Airbnb because it had a publicly accessible Greenhouse API, which made it suitable for implementing the job watcher.

However, I later found that Airbnb had very few non-senior engineering positions.

Out of the 52 engineering postings, only 6 were non-senior roles.

This made it difficult to create a balanced sample for a new-graduate candidate.

I learned that the choice of dataset can significantly affect the usefulness of an experiment.

### 3. Passing Tests Does Not Mean the Code Is Fully Verified

Initially, all 23 tests passed.

At first, this suggested that the implementation was working correctly.

However, mutation testing showed that some tests were not strong enough to detect certain errors.

After identifying these weaknesses, I improved the test coverage.

The final mutation-testing result was 12 out of 13 detected changes.

This experience helped me understand the difference between having passing tests and having tests that can actually detect incorrect behavior.

### 4. Output Validation and Correct Decisions Are Different

During the action-surfaces experiment, I observed that an agent could produce a response that followed the required format but still made an incorrect decision.

This was an important observation because the validator only checked whether the response satisfied the contract's structure.

It did not guarantee that the job classification was correct.

I learned that validating the format and evaluating the correctness of a response are two different responsibilities.

### 5. Small Changes Can Create New Problems

When I added the US-location condition to the revised prompt, the job relevance decisions improved.

However, the revision caused three responses to fail validation because the existing output format did not support location citations.

This showed me that even a small prompt change can affect other parts of a system.

For future improvements, I would update the output contract to support location evidence and test the change separately.

## What I Verified Myself

During the project, I personally worked on reviewing the requirements, defining the relevance criteria, labeling the sample data, and checking the results.

Some of the main things I verified were:

- I reviewed and labeled all 20 sampled job postings.
- I clarified the labeling criteria when I found inconsistencies.
- I explicitly confirmed the three labels that had initially been inferred by Claude.
- I ran the live job watcher on October 28 and verified that it reported 17 new postings.
- I ran the full test suite and checked the results.
- I reviewed the mutation-testing results and the issues identified during the project review.
- I checked the experiment outputs and documented the limitations I found.

I used Claude Code to assist with implementation, test generation, experiment execution, and documentation, but I was responsible for the main decisions and reviewing the results.

## What I Would Improve Next

There are a few areas I would improve if I continued developing this project.

**First, I would improve the relevance rule.** The current rule mainly checks job titles and technical skills. I would add location, required experience, and work authorization requirements to make the results more useful.

**Second, I would improve duplicate detection.** Currently, the system identifies new postings using job IDs. I would investigate whether postings with different IDs but identical titles and similar descriptions represent the same job.

**Third, I would improve the evaluation dataset.** Airbnb had very few suitable new-graduate positions. I would consider using additional job boards to get a more balanced sample.

**Fourth, I would strengthen independent testing.** I would manually verify more expected results before comparing them with the implementation.

**Finally, I would improve the prompt output format.** I would add a dedicated field for location evidence so the revised prompt could provide explanations without violating the response contract.

## Final Reflection

This assignment helped me understand how to design and evaluate a job-search agent instead of simply relying on AI-generated decisions.

The most important part for me was defining the contract, deciding how relevance should be measured, and checking whether the implementation followed those requirements.

I also learned that testing needs to go beyond checking whether code runs successfully. The tests should be able to detect incorrect behavior, and the experiment results should be supported by saved evidence.

I used Claude Code as a development tool to help with implementation, experiments, and documentation. I made the main project decisions, provided the hand labels, reviewed the outputs, and worked through the problems identified during testing.

Overall, this project gave me practical experience with rule-based evaluation, prompt experiments, API integration, state management, validation, and testing.

**Smit Patel**  
**October 30, 2026**