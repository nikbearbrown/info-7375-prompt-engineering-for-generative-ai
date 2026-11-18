# SOURCES

## Executive Summary

This document explains the sources, references, development process, and contributions involved in building Job-Search Agent 3.

I developed this project as an extension of my previous Job-Search Agent assignments. My goal was to design, implement, test, and evaluate a job-filtering system that could identify relevant software engineering opportunities, explain its decisions, and provide evidence supporting those decisions.

I was responsible for the overall technical direction, system requirements, filtering decisions, manual evaluations, implementation review, debugging decisions, and interpretation of results.

I used Claude Code (Opus 5.5) as an AI-assisted development tool to help implement components, generate tests, run experiments, and prepare documentation.

I reviewed the implementation to understand how the different components worked together, including the collection pipeline, filtering rules, audit process, shortlist generation, claim verification, tool-server communication, and evaluation experiments.

I did not rely solely on the generated outputs. I examined the logic, reviewed the results, investigated incorrect behavior, compared alternatives, and determined which changes were appropriate.

The project reflects my technical decisions, evaluation work, and understanding of the implementation, supported by AI-assisted coding and experimentation.

## 1. Sources and References Used

The following resources provided background information, starting requirements, technical references, or external data.

| Source | How I Used It |
|---|---|
| Job-Search Agent 1 (`fall-2026/smit-p/js1-contract-and-watch`) | I reused the fictional candidate résumé, the original two-skill matching requirement, and the manual-labeling criteria. |
| Job-Search Agent 2 (`fall-2026/smit-p/js2-loop-tools-diff`) | I reused the job-board selection: Figma, Spotify, and Linear. I developed a new, smaller collection pipeline for this assignment rather than copying the earlier collector. |
| The Reallocation Engine (`github.com/nikbearbrown/the-reallocation-engine`) | The original source of the fictional Aarav Patel persona used in my earlier assignment. |
| Instructor's Lectern (`fall-2026/nik-bear-brown/lectern`) | I used the reject-audit concept and the approach of documenting accepted, modified, and rejected filtering rules. I did not copy its implementation code. |
| Greenhouse, Lever, and Ashby public job-board APIs | I used these APIs to collect actual job postings on November 14, 2026. |
| Microsoft Learn MCP server (`https://learn.microsoft.com/api/mcp`) | I evaluated this external server to understand tool discovery, communication, and trust boundaries. |
| Model Context Protocol (`https://modelcontextprotocol.io`) | I used MCP message structures and verified their behavior through actual client-server interactions. I did not independently reread the complete published specification for this assignment. |
| Clopper–Pearson exact binomial interval | I used this statistical method to express uncertainty in the reject-audit results. |
| Python 3.12 standard library | I used Python's built-in modules for collection, filtering, testing, JSON processing, and server communication. |
| Claude Code CLI 2.1.323 | I used Claude Code to assist with implementation, debugging, testing, experiments, and documentation. |

## 2. My Contributions and Responsibilities

### 2.1 Project Design and Planning

I established the objectives and requirements for Job-Search Agent 3.

I wanted to build a system that would not simply collect postings but also determine which opportunities were relevant to the fictional candidate.

I defined the core tasks:

- Collect job postings from selected public job boards.
- Filter postings using explicit and explainable rules.
- Identify why each posting was accepted or rejected.
- Evaluate the filter against manual judgments.
- Generate a shortlist of relevant postings.
- Verify claims against the original job descriptions.
- Expose the filtering functionality through a tool server.
- Evaluate how Claude performed under different configurations.
- Document failures, limitations, and opportunities for improvement.

I selected the evaluation objectives and made the final decisions about the system's behavior.

### 2.2 Filtering Rules and Requirements

I made the filtering decisions documented in `FILTER.md`.

These included:

- Which job boards to collect from.
- Which role words should be accepted.
- Which seniority terms should be excluded.
- How location should affect relevance.
- What experience threshold should be applied.
- How many résumé skills should match.
- When the filter should reject a posting.
- When the filter should return `cannot_tell`.
- Which scoring method to use.
- Which deliberately incorrect versions to test.

I reviewed the technical definitions needed to implement these rules, including whole-word matching, experience extraction, and rule ordering.

I also reviewed how the rules were translated into Python conditions and how the final verdict was generated.

### 2.3 Understanding the Filtering Code

I examined the filtering implementation in `src/filter.py` and its integration with `src/run_filter.py`.

I focused on understanding the complete decision-making process.

**Title matching:** I reviewed how the filter checks accepted role words and why whole-word matching is necessary. For example, Java should not automatically match JavaScript, and lead should not match leadership.

**Seniority filtering:** I examined how excluded terms such as Senior, Staff, Principal, Manager, and Director affect the final classification.

**Location handling:** I reviewed how the system distinguishes acceptable locations, unacceptable locations, and missing location information.

**Experience extraction:** I investigated how years-of-experience requirements are extracted from descriptions and how multiple requirements can produce incorrect results.

**Skill matching:** I reviewed how résumé skills are compared with posting descriptions and how the required number of matching skills affects filtering performance.

**Decision explanations:** I examined how the implementation records the rule responsible for a verdict and attaches supporting evidence from the posting.

This helped me understand how individual rules influence the overall behavior of the system.

### 2.4 Debugging the Experience-Filtering Problem

One of the most important problems I investigated involved the years-of-experience rule.

The initial implementation selected the smallest years requirement mentioned in a posting.

For example:

"5+ years of software engineering experience, including 3+ years with Ruby."

The filter interpreted this as a three-year requirement even though the posting required five years overall.

I identified the impact of this behavior during the audit.

Three of the six initially retained postings were affected by the rule.

I evaluated an alternative that used the largest applicable experience requirement and selected that change for version 1.1.

I reviewed the updated results to understand how the change affected the retained postings and overall classification performance.

This demonstrated why understanding the underlying implementation is important even when automated tests pass.

### 2.5 Manual Evaluation of 71 Job Postings

I personally evaluated 71 postings for the reject audit.

The postings were presented through fact cards without displaying the filter's prediction.

I used the candidate's requirements and my written evaluation criteria to determine whether each posting was relevant.

I also reviewed ambiguous or inconsistent labels.

During this process, I corrected three judgments and retained two Engineering Manager positions as relevant after reviewing their requirements.

The final manual verdicts are stored in:

`audit/hand-verdicts.json`

These labels were my evaluation judgments, not automatically generated ground truth.

### 2.6 Shortlist Claim Evaluation

I manually evaluated 18 claims generated for the shortlist.

I compared each claim against the quoted text from the corresponding job description.

The automated claim checker agreed with my judgments on 10 claims and disagreed on eight.

I examined the disagreements, particularly cases where experience requirements were missing or the seniority level would be determined later.

I retained my manual judgments while preserving the checker's classifications for comparison.

The labels are stored in:

`audit/shortlist-hand-labels.json`

This evaluation helped me understand the difference between a job appearing relevant and a claim being explicitly supported by the posting.

### 2.7 Filter Version 1.1 Decisions

I evaluated the proposed rule changes and selected which modifications should become part of version 1.1.

I reviewed the performance of individual changes before deciding which combination to adopt.

One important decision involved reducing the skill-match threshold to one skill.

This change increased held-out errors from three to four when evaluated independently.

However, I considered missing potentially relevant jobs a greater concern than reviewing additional irrelevant postings.

I therefore retained the change.

When combined with the experience-rule improvement, the held-out error count remained at three.

I documented the reasoning and limitations of this decision in `FILTER.md`.

### 2.8 Understanding the Collection Pipeline

I reviewed the collection process implemented in `src/collect.py` and the posting-processing logic in `src/postings.py`.

I examined how the collector:

- Sends requests to the selected public job-board APIs.
- Restricts requests to approved hosts.
- Handles HTTP responses and failures.
- Preserves raw responses.
- Extracts posting information.
- Normalizes data for the filtering process.
- Records collection metadata in the manifest.

The live collection produced 473 postings from Airbnb, Figma, Spotify, and Linear.

I reviewed the collection results and verified that the saved data could be reused for offline evaluation.

### 2.9 Understanding the Audit and Statistical Evaluation

I reviewed the evaluation implementation in `src/audit.py` and `src/measure_filter.py`.

I examined how the code compares automated predictions against manual labels and calculates disagreement counts.

I also reviewed the sampling design, including the development and held-out subsets.

The original filter disagreed with my judgments on 10 of the 71 evaluated postings.

In the random reject sample, two of 30 postings were manually judged relevant.

I reviewed how the Clopper–Pearson method was used to calculate an uncertainty interval.

This helped me understand why the observed 6.7% proportion should not be treated as the exact miss rate for every rejected posting.

### 2.10 Understanding the Shortlist and Claim Checker

I reviewed `src/shortlist.py` and `src/entailment_example.py`.

I examined how the system:

- Selects retained postings.
- Produces ranking information.
- Extracts evidence from descriptions.
- Generates claims about matching requirements.
- Checks claims against the source text.
- Compares automated classifications with manual labels.

I also investigated an issue involving the regular expression used to recognize "e.g." in technology lists.

The original expression did not correctly handle certain punctuation boundaries.

I reviewed the correction and the associated test coverage.

This reinforced the importance of checking text-processing edge cases.

### 2.11 Understanding the MCP Tool Server

I reviewed the tool-server implementation in `src/mcp_server.py` and the client implementation in `src/mcp_client.py`.

I focused on understanding the communication between the client and server.

I examined:

- Initialization requests.
- Tool discovery.
- Tool-call requests.
- JSON-RPC message handling.
- Input validation.
- Error responses.
- Read-only tool behavior.
- Transcript generation.
- File-system restrictions.

I tested the server using a custom Python client and Claude Code.

I also examined the recorded transcripts to understand the messages exchanged between the client and server.

The server exposes the `score_posting` tool, which evaluates a saved posting and returns a rule-based verdict with evidence.

I reviewed the security limitations and decided that the server should be trusted for local use only.

### 2.12 Testing and Debugging

I reviewed the tests in `tests/test_filter.py` and `tests/test_parts.py`.

I examined how the tests validate filtering behavior, collection restrictions, tool-server responses, and error handling.

The first 27 filter tests were generated from the written specification and committed before the filter implementation.

I reviewed the resulting test suite and its coverage.

I also used mutation testing to investigate whether the tests could detect deliberate implementation errors.

The final mutation results caught 12 of 13 mutants.

One mutant, M7, survived and remains documented.

I also reviewed the server-isolation test after an independent review identified that the original version did not execute the server process.

The strengthened test starts the server and checks file hashes to identify unintended writes.

I examined why mutant M11 survived earlier versions of the test and how the corrected test detected it.

These investigations improved my understanding of unit testing, integration testing, mutation testing, and test reliability.

### 2.13 Claude Evaluation Experiments

I established the evaluation goals and reviewed the experiment configurations implemented through `experiments/run_claude.py`.

The experiments evaluated Claude's classification behavior across five configurations and 33 held-out postings.

A total of 165 model calls were recorded.

I reviewed the saved responses, evaluation scores, and differences between configurations.

I also examined the effect of individual changes rather than assuming that a modified prompt was automatically better.

One prompt change converted a wrong answer into an abstention.

I recognized that this represented a change in behavior rather than proof of improved accuracy.

I also examined two identical configuration runs that disagreed on one of 33 postings.

These results helped me understand the limitations of model consistency and the importance of controlled evaluation.

### 2.14 Documentation and Technical Reporting

I prepared and reviewed the project documentation to explain the implementation, results, decisions, and limitations.

The main documents are:

| Document | Purpose |
|---|---|
| `README.md` | Project overview, execution instructions, results, and limitations |
| `FILTER.md` | Filtering rules, specifications, and version changes |
| `AUDIT.md` | Manual evaluation, sampling, and disagreement analysis |
| `SHORTLIST.md` | Shortlist generation, claim verification, and evidence |
| `TOOL-SERVER.md` | Tool-server implementation, testing, and trust evaluation |
| `WHAT-MOVES-THE-SCORE.md` | Claude evaluation experiments and score comparisons |
| `FRICTIONAL.md` | Development challenges, debugging, decisions, and unresolved issues |
| `SOURCES.md` | Sources, contributions, and development provenance |

I reviewed the reported findings against the saved results and revised the explanations to reflect my understanding of the system.

## 3. How I Used Claude Code

I used Claude Code (Opus 5.5) during the development process.

Its role was to assist with implementation, testing, debugging, experimentation, and documentation.

### Code Implementation Assistance

Claude Code generated implementation code in `src/` and `experiments/` based on the project requirements and development instructions.

I reviewed the implementation to understand the algorithms, conditions, data flow, and interactions between components.

I remained responsible for determining whether the behavior matched the requirements.

### Test Generation Assistance

Claude Code helped generate tests for the filtering rules, collector, claim checker, and tool server.

I reviewed the tests and investigated their effectiveness using mutation testing and evaluation results.

The test-generation process did not replace the need for my own technical understanding and validation.

### Experiment Execution Assistance

Claude Code assisted with running collection, tool-server, and model-evaluation experiments.

I examined the recorded outputs and used the results to make decisions about the final system.

The Claude model responses saved in `experiments/results/` are experimental data, not independent evidence that the generated answers are correct.

### Independent Review Assistance

I used a separate read-only Claude review to inspect the project and identify possible problems.

The review reproduced the reported numbers and identified weaknesses in testing, documentation, and transcript handling.

I reviewed these findings and incorporated corrections into the project.

### Documentation Assistance

Claude Code assisted with preparing initial drafts of the project documentation.

I reviewed the technical explanations, corrected attribution and wording, and revised the documents to reflect my understanding and decisions.

The use of AI assistance does not change the fact that I was responsible for validating the submitted work.

## 4. Development Challenges and How I Addressed Them

I encountered several challenges while building and evaluating the system.

**Incorrect years-of-experience interpretation:** I investigated the extraction logic, measured an alternative rule, and adopted the improved version.

**Incomplete evaluation evidence:** I identified that fact cards did not display every years requirement and corrected the presentation before manual judging.

**Overly optimistic test results:** I used mutation testing to identify weaknesses that ordinary passing tests did not reveal.

**Manual-label disagreements:** I reviewed inconsistent labels and recorded my final judgments.

**Claim-checker disagreements:** I compared automated classifications against the original posting text and preserved disagreements rather than forcing agreement.

**Incomplete tool evidence:** I examined cases where the tool output omitted descriptions and caused Claude to abstain.

**Inconsistent model responses:** I compared repeated runs and documented differences between identical configurations.

**Tool-server isolation weaknesses:** I reviewed and strengthened the process-based file-writing test.

**Transcript privacy:** I addressed the exposure of unnecessary Microsoft content by using redacted transcripts and hashes.

The detailed sequence of these issues is documented in `FRICTIONAL.md`.

## 5. Understanding and Verification of the Code

I reviewed the project as a connected software system rather than treating each generated file as an isolated component.

My understanding of the main execution flow is:

1. The collector retrieves postings from the selected public job boards.
2. The posting processor normalizes the saved data.
3. The filter evaluates each posting using rules R1–R6.
4. The filtering runner records the verdicts and supporting evidence.
5. The audit compares the filter's decisions against my manual labels.
6. The measurement process evaluates proposed rule changes.
7. The shortlist generator ranks retained postings and checks claims.
8. The tool server exposes the scoring functionality to external clients.
9. The experiment runner evaluates Claude under different configurations.
10. The reporting scripts recompute the metrics from saved artifacts.

I used the tests, transcripts, audit results, and experiment outputs to understand the behavior of these components.

I also examined important failure cases to understand why the implementation produced certain results.

My ability to explain the rules, identify limitations, and evaluate alternative solutions was an important part of the development process.

## 6. Work Reused Versus New Work

### Reused From Earlier Work

I reused the fictional candidate persona, the initial skill-matching requirement, the manual-labeling criteria, and the original selection of three job boards.

I also used the instructor's Lectern as a methodological reference for documenting filter changes.

### Developed for This Assignment

The new work included:

- The collection pipeline for this iteration.
- The complete filtering implementation.
- The updated experience and skill-matching rules.
- The manual reject audit.
- The filter measurement process.
- The shortlist and claim-verification system.
- The local MCP-compatible tool server.
- The custom client and integration tests.
- The Claude evaluation experiments.
- The mutation-testing workflow.
- The evaluation reports and development documentation.

The implementation was developed for this assignment with AI-assisted coding support.

No implementation code was copied from the earlier agents or the instructor's Lectern.

## 7. Evidence of My Work

My contributions and technical decisions can be traced through the following artifacts.

| Contribution | Evidence |
|---|---|
| Filtering requirements and decisions | `FILTER.md` |
| Manual evaluation of 71 postings | `audit/hand-verdicts.json` |
| Manual evaluation of 18 claims | `audit/shortlist-hand-labels.json` |
| Version 1.1 decisions | `FILTER.md` change log |
| Filtering implementation and tests | `src/filter.py`, `tests/test_filter.py` |
| Audit and measurement results | `AUDIT.md`, `src/measure_filter.py` |
| Shortlist evaluation | `SHORTLIST.md` |
| Tool-server integration | `TOOL-SERVER.md`, `transcripts/` |
| Claude experiments | `experiments/results/` |
| Mutation-testing findings | `tests/mutation-log.md` |
| Development challenges | `FRICTIONAL.md` |
| Final project overview | `README.md` |

These files provide evidence of the project's implementation, evaluation, and documented decisions.

## 8. Final Reflection

Building Job-Search Agent 3 gave me practical experience in designing and evaluating a software system that makes decisions using structured rules and external data.

I learned how small implementation details can affect the reliability of an entire pipeline.

The years-of-experience bug demonstrated the importance of understanding the requirements behind a rule rather than relying only on whether the code executes successfully.

The manual audit helped me evaluate the system against independent judgments.

The claim-verification process showed me why relevance and explicit textual support must be treated separately.

The tool-server integration improved my understanding of client-server communication, structured tool calls, input validation, and trust boundaries.

The Claude experiments helped me understand model inconsistency, abstention behavior, and the limitations of prompt-based evaluation.

I also learned the importance of mutation testing and independent review for identifying problems that ordinary testing may miss.

I used Claude Code to assist with development, but I reviewed the implementation, investigated the results, and made the final technical decisions.

The most important part of my work was not simply producing a working system. It was understanding why the system behaved as it did, identifying where it failed, and making evidence-based improvements.

## 9. Authorship and Responsibility Statement

I was responsible for the design direction, requirements, evaluation criteria, manual judgments, technical decisions, implementation review, and final deliverables of Job-Search Agent 3.

I used Claude Code (Opus 5.5) as an AI-assisted development tool for code generation, test generation, experimentation, debugging, and documentation.

The initial code, tests, prompts, and document drafts were produced with Claude Code assistance. I reviewed the implementation and results to understand the system, verify its behavior, and decide which changes to adopt.

I personally completed the 71 manual posting verdicts and 18 shortlist claim labels, selected the version 1.1 rule changes, and made the final trust decisions for the tool servers.

I take responsibility for the accuracy of the submitted results, the documented limitations, and the final project decisions.

**Student:** Smit P.

**Course:** INFO 7375 — Fall 2026

**Project:** Job-Search Agent 3

**Date:** November 16, 2026