# FRICTIONAL — What Actually Happened

## Executive Summary

This document records the challenges, mistakes, debugging steps, decisions, and lessons learned while I was building Job-Search Agent 3 on November 14, 2026.

I was responsible for developing, testing, evaluating, and refining the system. I used Claude Code as a development assistant during the process, but I reviewed the implementation, evaluated the results, made the final decisions, and determined which changes to accept or reject.

My goal was not simply to build a working job-search filter. I wanted to understand how reliable it was, identify where it failed, and determine whether the results could be trusted.

Throughout development, I encountered problems involving incomplete job descriptions, incorrect filtering rules, misleading test results, inconsistent model responses, and unsupported claims.

I documented these issues, investigated their causes, evaluated possible solutions, and recorded the remaining limitations.

Each issue below is connected to the relevant source file, test, experiment, or Git commit so that the work can be verified.

## Log of Events

| # | What Happened | What I Did | Outcome | Evidence |
|---|---|---|---|---|
| F1 | I discovered that the saved Figma responses from Job-Search Agent 2 did not contain job descriptions because the original requests did not use `content=true`. Without descriptions, I could not properly evaluate job requirements or verify claims. | I collected a fresh set of live job postings with complete descriptions, using the same job boards and adding Airbnb. | Resolved. I had the job-description data needed for evaluation. | `runs/live-20261114/manifest.json`, `ace3d80c` |
| F2 | All 27 filter tests passed on the first run. Based on my earlier experience with Job-Search Agent 1, I knew that passing tests alone did not prove the implementation was correct. | I used mutation testing to deliberately introduce bugs and check whether the tests detected them. The final results showed that 12 of 13 mutants were caught. | Partially resolved. I documented the surviving mutant M7 rather than hiding it. | `tests/mutation-log.md` |
| F3 | While preparing fact cards for manual evaluation, I noticed that the cards displayed only the years requirement selected by the filter. For example, a posting requiring "5+ years" overall and "3+ years with Ruby" displayed only the 3-year requirement. | I corrected the fact-card generation so every relevant years sentence appeared. I also checked that the sampled postings remained unchanged. | Resolved before manual evaluation. | `de37311d` |
| F4 | During my audit, I found that rule R5 used the smallest number of years mentioned in a job description. This incorrectly allowed jobs requiring more experience than the filter recognized. Three of the six initially accepted postings were affected. | I evaluated an alternative rule using the largest years requirement, measured its performance independently, and adopted the change. | Modified R5 in FILTER.md v1.1. | `FILTER.md`, `02b326be` |
| F5 | Two Engineering Manager positions appeared in my manual labels as relevant, even though they did not perfectly match my original written criteria. | I reviewed those decisions and chose to keep both positions marked as relevant. | Accepted my original judgments. | `audit/hand-verdicts.json` |
| F6 | Three other manual labels were inconsistent with my criteria, including two Stockholm positions and a job requiring five years of experience. | I reviewed the questionable labels and changed all three to not relevant. I retained the separate Stockholm Backstage verdict. | Corrected three manual labels. | `audit/hand-verdicts.json` |
| F7 | One manual evaluation accidentally selected both a job posting and "None of these 3." | I reviewed the conflicting response and confirmed that the posting should be labeled relevant. | Resolved the conflicting label. | `audit/hand-verdicts.json` |
| F8 | I tested change C, which reduced the skill-match requirement to one matching skill. On its own, this increased held-out errors from three to four. | I compared the results and decided to keep the change because missing potentially good jobs was a greater concern for my use case. When combined with change A, held-out errors remained at three. | Accepted change C despite its weaker standalone performance. | `FILTER.md` v1.1 |
| F9 | I examined the held-out results for candidate rule changes before selecting the final configuration. This meant the held-out set was no longer completely independent of the tuning process. | I documented the limitation in the evaluation reports rather than presenting the held-out results as fully untouched evidence. | Unresolved evaluation limitation. | `FILTER.md`, `WHAT-MOVES-THE-SCORE.md` |
| F10 | The filter never returned "I cannot tell" across 473 postings. This raised concerns about how it handled incomplete or ambiguous job descriptions. | I examined examples, including a posting without a clear years requirement that mentioned varying seniority levels but still ranked first. | Unresolved. The abstention rule needs improvement. | `SHORTLIST.md` |
| F11 | During tool-server integration, the first Claude Code client request used `server/discover` with protocol `2026-07-28`, which the server did not recognize. | I examined the server transcript and confirmed that the server returned error `-32601`. The client then initialized using protocol `2025-11-25`, allowing the session to continue. | No implementation change required. | `transcripts/claude-code-client-20261114-server-side.jsonl` |
| F12 | I found that some evidence quotes were cut off at abbreviations such as "e.g.", producing incomplete sentences in the tool output. | I corrected the `sentence_around` display logic and added a regression test. I checked that the filtering rules, verdicts, and scores were unchanged. | Resolved. The original transcript was retained as evidence. | `28019a49`, `tests/test_filter.py` |
| F13 | The claim checker incorrectly treated some technology examples as supported claims. The regular expression `\be\.g\.\b` failed to recognize "e.g.," correctly. | I corrected the matching logic and subsequently added test coverage for the claim checker. | Resolved before the checker labels were committed. | `src/shortlist.py`, `e45695e4`, `cb9ec66d` |
| F14 | I manually labeled all 18 shortlist claims as supported, while the automated checker classified eight as insufficient. | I reviewed the disagreements, particularly the five claims where the evidence did not explicitly state years or deferred the seniority decision. I decided to retain my supported labels while preserving the automated results for comparison. | Accepted my manual judgments and documented the disagreement. | `audit/shortlist-hand-labels.json` |
| F15 | During Microsoft Learn integration testing, I found that the session identifier decoded into readable JSON containing a `userIdClaim`. The advertised prompts and resources were empty. | I documented the observation and kept testing within the intended scope of the tool. I did not test `microsoft_docs_fetch` against unrelated external URLs. | Documented the behavior without unnecessary probing. | `transcripts/mslearn-session-20261114.jsonl` |
| F16 | Two runs using the same Claude configuration produced different answers for one of 33 postings. | I compared the outputs and used the difference to evaluate the reliability of repeated model responses. | Documented that identical configurations do not guarantee identical outputs. | `experiments/results/SCORES.md` |
| F17 | When I provided Claude with the filter's tool output instead of the original posting, it abstained six times. | I investigated the missing information and found that title-rejected postings did not include descriptions in the tool output. | Explained the abstentions as an information limitation. | `WHAT-MOVES-THE-SCORE.md` |
| F18 | I used a separate read-only Claude review to independently inspect the project. The review reproduced the reported numbers but identified weaknesses in testing, documentation, privacy handling, and evaluation reporting. | I addressed the findings by strengthening the server-isolation test, adding file-hash checks, improving mutation testing, correcting inaccurate wording, redacting transcript content, and documenting manual-labeling time. | Accepted and addressed the findings while retaining the evidence of earlier failures. | `tests/mutation-log.md`, `TOOL-SERVER.md`, `AUDIT.md` |

## Problems I Investigated in More Detail

### 1. Incorrect experience filtering

One of the most important issues I discovered was how the filter interpreted years of experience.

For example, a job description could require:

- 5+ years of overall software engineering experience.
- 3+ years of experience with Ruby.

The original filtering rule selected the smallest number, which was three years.

This was a problem because a candidate with three years of experience would still fail the posting's five-year overall requirement.

During my audit, I found that this rule affected three of the six initially accepted postings.

I tested an alternative that used the largest years requirement and adopted it after reviewing the results.

**What I learned:** A rule can be implemented correctly according to its specification while the specification itself is wrong. Testing the code is not enough; I also need to validate the assumptions behind the rules.

### 2. Passing tests did not guarantee correctness

When I first ran the filter tests, all 27 passed.

Initially, this looked encouraging. However, I had seen a similar situation in Job-Search Agent 1, where passing tests did not necessarily mean that the system handled important edge cases.

I used mutation testing to evaluate the strength of the tests.

The idea was to introduce deliberate mistakes and determine whether the existing tests could identify them.

The final mutation results caught 12 out of 13 deliberate bugs.

One mutant, M7, survived because it involved a second guard in the tool server.

I also investigated a weakness in the test intended to verify that the server wrote only its transcript.

The original test did not actually execute the server process, so it could not detect unintended file writes.

I strengthened the test by running the server as a process and checking file hashes.

During this process, mutant M11 survived twice:

- The first version took its initial snapshot after setup had already created server-related files.
- The second version compared file contents in a way that failed to identify a rewrite containing identical bytes.

I revised the test until it could detect the unwanted write.

**What I learned:** Test quality matters more than the number of passing tests. Mutation testing helped me identify weaknesses that ordinary unit testing had missed.

### 3. Manual evaluation exposed filtering errors

I manually evaluated 71 job postings using fact cards that did not display the filter's verdict.

I used this approach to avoid allowing the automated prediction to influence my judgment.

Before evaluating the postings, I discovered that the fact cards did not always display all experience requirements.

I corrected that issue so the evaluation included the relevant evidence.

During labeling, I also reviewed inconsistent or ambiguous judgments.

I changed three labels after reviewing their requirements and kept two Engineering Manager roles marked relevant because I considered them relevant to my search.

I also resolved a conflicting response where both a posting and "None of these 3" had been selected.

These decisions were based on my interpretation of the job requirements and my intended use of the system.

**What I learned:** Human evaluation is useful for identifying problems in automated rules, but manual labels can also contain inconsistencies. Both need careful review.

### 4. Choosing between precision and recall

Another important decision involved the number of matching skills required to consider a posting relevant.

I tested a change that allowed a job to pass with only one matching skill.

The standalone results were worse on the held-out set, increasing errors from three to four.

However, I was concerned that stricter skill matching would exclude potentially relevant opportunities.

For my job-search use case, missing a good opportunity could be more costly than reviewing an extra irrelevant posting.

I therefore chose to retain the one-skill rule.

When combined with the improved years-of-experience rule, the held-out error count remained at three.

I documented this tradeoff instead of presenting the change as an unconditional improvement.

**What I learned:** The best filtering rule depends on the purpose of the system. Accuracy alone does not fully describe the cost of false positives and false negatives.

### 5. Differences between manual and automated claim checking

I manually evaluated 18 claims in the generated shortlist.

My labels marked all 18 as supported.

The automated checker disagreed with eight of them, classifying those claims as having insufficient evidence.

I examined the disagreements and reviewed the relevant quoted job descriptions.

Five claims were especially ambiguous because the descriptions did not explicitly provide years of experience or stated that the level would be determined later.

I chose to retain my manual labels while keeping the automated checker results visible.

I did not change the checker merely to make it agree with my judgments.

**What I learned:** A disagreement between human and automated evaluation should be investigated and documented. Agreement is not necessarily evidence that either evaluation is correct.

### 6. Model consistency and missing information

I ran the same Claude configuration twice across 33 postings.

One posting received a different answer between runs.

This showed that repeated execution with the same configuration did not guarantee identical behavior.

I also tested how Claude responded when it received the filter's tool output instead of the original job description.

In that experiment, Claude abstained six times.

After examining the outputs, I found that title-rejected jobs did not include their descriptions, leaving insufficient information for an independent judgment.

**What I learned:** Model reliability depends on both the model's behavior and the information available to it. Tool outputs can limit downstream reasoning when important context is omitted.

### 7. Independent review and documentation corrections

After completing the initial implementation and evaluation, I used a separate read-only Claude review to inspect the project.

The review independently reproduced the reported numbers and identified several issues that needed attention.

These included:

- A test that could not detect the behavior it claimed to test.
- An impossible ratio in the written explanation.
- A cost comparison that did not account for caching.
- Two past-tense statements without supporting commits.
- Approximately 53 KB of Microsoft content included in a public transcript.
- The fact that 71 manual verdicts were completed in approximately eight minutes.

I reviewed these findings and made the necessary corrections.

I improved the test implementation, corrected misleading descriptions, redacted the transcript using hashes, and disclosed the labeling time in the audit documentation.

**What I learned:** Independent review is valuable because it can identify mistakes in both implementation and reporting. I also learned that reproducible numbers do not automatically mean that every interpretation or claim is justified.

## My Reflections

### What surprised me

The biggest surprise was how much impact one small filtering rule could have.

Using the smallest years-of-experience number seemed like a simple implementation choice, but it caused three of the six initially accepted postings to be incorrectly kept.

I was also surprised that two runs with the same Claude configuration produced different results for one posting.

These findings showed me that small assumptions and nondeterministic behavior can affect the reliability of the entire system.

### What I checked myself

I reviewed the implementation, the evaluation outputs, and the supporting reports to understand the behavior of the system.

My main validation activities included:

- Manually evaluating 71 job postings without seeing the filter's predictions.
- Labeling 18 shortlist claims against their quoted job descriptions.
- Reviewing the filtering rules and comparing alternative configurations.
- Investigating failed and surviving mutation tests.
- Examining tool-server transcripts and integration behavior.
- Comparing repeated model runs.
- Reviewing the code and reports over two days so I could explain the results and limitations.

I used these checks to decide which changes were justified and which findings needed further investigation.

### What I would not have caught without the audit

Without the audit, I could have trusted the filter's initial results simply because the tests passed.

The audit revealed that the original years-of-experience rule caused incorrect decisions.

It also helped me identify weaknesses in the claim evidence, including the top-ranked posting, where some listed skills appeared only as examples.

Another important finding involved the uncertainty around the estimated miss rate.

A result of two misses in 30 examples gives a point estimate of approximately 6.7%, but that does not mean the true miss rate is known precisely.

The reported uncertainty interval was approximately 1% to 22%.

This changed how I interpreted the evaluation results.

### Decisions I made

I made several important decisions while developing and evaluating the system.

First, I changed the years-of-experience rule after discovering that the original definition incorrectly accepted some jobs.

Second, I kept the one-skill matching rule even though its standalone held-out performance was worse. I prioritized reducing missed opportunities for my particular use case.

Third, I retained two Engineering Manager positions as relevant after reviewing their requirements.

Fourth, I corrected three manual labels that did not match my criteria.

Finally, I retained my manual supported labels for the shortlist claims while preserving the automated checker's disagreements.

These decisions reflect my evaluation criteria and the tradeoffs I considered during development.

## What Is Still Unresolved

Although I improved the system, several limitations remain.

### 1. Abstention behavior

The filter returned "I cannot tell" zero times across 473 postings.

This suggests that the current rules may be too aggressive when handling incomplete job descriptions.

A future improvement would be to distinguish between requirements that are explicitly satisfied and requirements that are simply missing.

### 2. Missing skills in the résumé

Some potentially relevant web and Android development positions are rejected because the résumé skills do not explicitly include technologies such as JavaScript, React, or Kotlin.

I need to improve how the filter handles related skills and alternative technologies without making unsupported assumptions about candidate qualifications.

### 3. Held-out evaluation contamination

I reviewed the held-out results before selecting the final v1.1 rule changes.

Because of this, the held-out set is no longer an entirely independent evaluation of the final configuration.

A fresh evaluation dataset would be needed to measure generalization more reliably.

### 4. Tool-assisted model performance

I demonstrated that Claude could use the tool server, but I did not complete a controlled held-out comparison measuring whether access to the tool improved Claude's decisions.

That remains an important future experiment.

### 5. Evaluation across multiple collection days

The project used one live collection period.

I did not repeat the complete evaluation using job postings collected on a second day.

Additional collection periods would help determine whether the findings remain consistent as job listings change.

### 6. Additional independent testing

I used mutation testing and independent review to strengthen the project.

However, I did not write a separate set of tests before inspecting the assistant-generated implementation.

A future improvement would be to develop tests directly from the specification before examining the implementation, reducing the risk of reproducing the same assumptions in both the code and its tests.

## What I Would Improve Next

Based on the results, I would prioritize the following improvements:

1. **Improve experience extraction:** Handle multiple years-of-experience requirements more accurately, including distinctions between overall experience and technology-specific experience.

2. **Improve abstention rules:** Return "I cannot tell" when the available description does not provide enough information to make a reliable decision.

3. **Expand skill matching:** Support related technologies and transferable skills while maintaining clear evidence requirements.

4. **Strengthen evaluation independence:** Create a new held-out dataset that has not been used during rule selection.

5. **Improve claim verification:** Separate explicit evidence, reasonable inference, and unsupported claims so disagreements can be analyzed more consistently.

6. **Measure tool effectiveness:** Compare model decisions with and without tool access using the same independently labeled evaluation set.

7. **Continue mutation testing:** Add deliberate failure cases for file isolation, malformed descriptions, missing requirements, and integration behavior.

## Work Not Completed

For transparency, the following work was not completed as part of this iteration:

- A measured held-out comparison of Claude with and without the tool server.
- A separate Claude-judge evaluation on the development set.
- A second full collection of live job postings on another day.
- An independently written test suite created before reviewing the assistant-generated code.

These limitations are also recorded in the project README.

## Final Reflection

Building Job-Search Agent 3 helped me understand that developing an automated decision system involves much more than implementing rules and getting tests to pass.

The most valuable part of the project was investigating situations where the system appeared correct but produced misleading results.

I identified problems in experience extraction, improved the evaluation process, tested the strength of the test suite, investigated inconsistent model behavior, and reviewed disagreements between manual and automated judgments.

I also learned the importance of documenting negative results. Some changes improved performance, some made it worse, and some introduced tradeoffs that could not be resolved by a single accuracy metric.

I used Claude Code to assist with development and review, but I remained responsible for evaluating the results, making the decisions, and determining which changes were appropriate for the project.

My main takeaway is that a system should not be considered reliable simply because it runs successfully or produces convincing outputs. Its assumptions, evidence, tests, and limitations all need to be examined.

This project strengthened my understanding of software testing, evaluation design, debugging, model-assisted development, and the importance of making technical decisions based on evidence rather than relying only on automated results.