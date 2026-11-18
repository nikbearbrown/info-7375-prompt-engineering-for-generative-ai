# Job-Search Agent 3 — The Filter, the Tool, and the Score

**Smit P. · INFO 7375 · Fall 2026 · Chapters 7–9**

## Executive Summary

I developed Job-Search Agent 3 to build and evaluate a reliable job-filtering system that identifies potentially relevant software engineering opportunities, explains its decisions, and provides evidence for each result.

This project extends my previous work on Job-Search Agent 1 and Job-Search Agent 2. My objective was to move beyond collecting job postings and develop a system that could filter, evaluate, rank, and explain them using clearly defined rules and measurable evidence.

On November 14, 2026, I collected 473 job postings from four public job boards: Airbnb, Figma, Spotify, and Linear. I evaluated these postings against a fictional new-graduate software engineer persona, Aarav Patel.

My initial filtering implementation retained six postings and rejected 467. To evaluate the accuracy of these decisions, I manually reviewed 71 postings and compared my judgments against the filter's output.

The initial filter disagreed with my judgments on 10 of the 71 postings. Four of the six retained postings were incorrectly classified as relevant.

During my investigation, I identified a significant issue in how the filter interpreted years-of-experience requirements. For example, a posting requiring "5+ years of experience, including 3+ years with Ruby" was incorrectly interpreted as requiring only three years.

I investigated the issue, evaluated alternative filtering rules, and updated the implementation to version 1.1.

The updated filter retained three postings, all of which I had manually judged relevant.

I also implemented a claim-verification process to compare shortlist explanations against the actual job descriptions. This helped me identify cases where a posting appeared relevant but did not explicitly support the claims made about it.

To make the filtering functionality accessible to an AI assistant, I developed a tool-server integration and tested it using both a custom client and Claude Code.

Finally, I designed experiments to evaluate Claude's job-classification behavior across different configurations. I compared 165 responses across five configurations, examined the impact of individual changes, and investigated inconsistent outputs.

Throughout the project, I was responsible for the technical direction, evaluation criteria, implementation review, testing decisions, analysis, and final conclusions. I used Claude Code as an AI-assisted development and review tool, while retaining responsibility for the project's design, validation, and results.

The project demonstrates how I approached building an explainable, testable, and evidence-based job-search system rather than relying on automated predictions without verification.

## Project Background

This project builds on two earlier assignments.

### Job-Search Agent 1

I reused the fictional candidate persona, the original two-skill matching requirement, and the manual-labeling criteria.

These provided the initial requirements for the filtering system.

### Job-Search Agent 2

I reused the job-board collection approach for Figma, Spotify, and Linear.

I also included Airbnb as an additional source, based on my earlier work.

### New Work in Job-Search Agent 3

For this iteration, I developed and evaluated:

- A rule-based job-filtering system.
- An updated experience-requirement extraction process.
- An automated collection and filtering pipeline.
- A manually labeled evaluation dataset.
- A reject-audit process.
- A shortlist generation and ranking system.
- A claim-verification mechanism.
- A custom tool server and client.
- Claude-based evaluation experiments.
- Unit tests, integration tests, and mutation tests.
- Reproducible evaluation reports and supporting transcripts.

I used the instructor's Lectern example as a reference for the reject-audit methodology, particularly the idea of recording added, removed, and rejected words.

I did not copy implementation code from the previous agents or Lectern.

## Development Environment

I developed and tested the project using the following environment:

| Component | Technology |
|---|---|
| Programming language | Python 3 |
| Tested Python version | 3.12.7 |
| Operating system | macOS |
| Dependencies | Python standard library only |
| AI development assistance | Claude Code |
| Claude Code version | 2.1.323 |
| Tool integration | MCP-compatible tool server |
| Testing framework | Python `unittest` |
| Evaluation | Manual labeling, rule-based checks, Claude experiments |
| Data storage | JSON, JSONL, Markdown |

The project does not require third-party Python packages.

No `pip install` is necessary.

All commands should be executed from the project root directory.

## Installation and Execution

### 1. Run the unit and integration tests

```bash
python3 -m unittest discover -s tests -v
```

This executes 43 offline tests, including a test that starts the tool server as a separate process.

### 2. Run mutation testing

```bash
python3 tests/mutation_check.py
```

This deliberately introduces implementation errors and checks whether the tests detect them.

The results are recorded in:

`tests/mutation-log.md`

### 3. Run the job filter

```bash
python3 src/run_filter.py --run-id live-20261114
```

This processes the saved job postings using the current filtering configuration.

To reproduce the original audited version:

```bash
python3 src/run_filter.py --run-id live-20261114 --version 1.0
```

### 4. Recompute the reject audit

```bash
python3 src/audit.py score --run-id live-20261114
```

This compares the automated filter predictions against my manually labeled evaluation data.

### 5. Measure filter changes

```bash
python3 src/measure_filter.py --run-id live-20261114
```

This evaluates the individual rule changes and their impact on classification performance.

### 6. Generate and evaluate the shortlist

```bash
python3 src/shortlist.py
python3 src/shortlist.py --compare
python3 src/entailment_example.py
```

These commands generate the shortlist, compare claim-verification results, and demonstrate the distinction between relevance and textual evidence.

### 7. Recompute Claude evaluation scores

```bash
python3 experiments/run_claude.py --score
```

This recalculates evaluation metrics using the previously saved model responses.

It does not require additional model calls.

### 8. Run the custom tool-server client

```bash
python3 src/mcp_client.py stdio-session --name my-session-1
```

This starts a local client session and communicates with the tool server.

Use a unique session name for each run.

## Live Collection and Model Commands

The following commands require network access or an authenticated Claude Code environment.

### Collect new job postings

```bash
python3 src/collect.py --run-id live-YYYYMMDD
```

This collects a new set of postings and saves the corresponding raw responses and metadata.

### Run Claude evaluation experiments

```bash
python3 experiments/run_claude.py --config baseline
```

This executes 33 Claude calls for the baseline configuration.

The recorded approximate cost was $0.50.

The runner prevents overwriting previously saved experiment results.

### Connect Claude Code to the tool server

Replace `/ABS/PATH` with the absolute path to the project directory.

```bash
claude -p "Use the score_posting tool to score board figma, posting_id 5691911004. Report the verdict and quote the evidence." --model sonnet --mcp-config '{"mcpServers":{"js3":{"command":"python3","args":["/ABS/PATH/src/mcp_server.py","--transcript-name","my-claude-try"]}}}' --strict-mcp-config --allowedTools mcp__js3__score_posting --setting-sources "" --no-session-persistence
```

This allows Claude Code to call my local `score_posting` tool and receive a rule-based verdict with supporting evidence.

## Experiments and Results

All primary experiments were conducted on November 14, 2026, in US Eastern time.

The stored timestamps use UTC, so some records extend into November 15.

| Experiment | Execution | Result | Evidence |
|---|---|---|---|
| Job collection | Live | 473 postings across four boards, zero collection failures | `runs/live-20261114/manifest.json` |
| Filter v1.0 | Offline | 6 kept, 467 rejected, 0 cannot_tell | `verdicts-v1.0.json` |
| Manual reject audit | Manual + offline | 71 postings evaluated; 10 disagreements | `AUDIT.md` |
| Filter v1.1 | Offline | 3 kept, all manually judged relevant | `FILTER.md`, `verdicts-v1.1.json` |
| Shortlist claim verification | Manual + automated | 18 claims evaluated; 10 agreements | `SHORTLIST.md` |
| Custom tool server | Real local sessions | Tool requests processed or rejected according to the server contract | `TOOL-SERVER.md` |
| Microsoft Learn MCP | Live integration | 3 tools discovered; prompts and resources empty | `transcripts/mslearn-*.jsonl` |
| Claude evaluation | Live | 5 configurations, 33 postings each, 165 calls | `WHAT-MOVES-THE-SCORE.md` |
| Mutation testing | Offline | 12 of 13 deliberate bugs detected | `tests/mutation-log.md` |

The recorded total cost of the 165 Claude evaluation calls was approximately $1.46.

All reported collection and model experiments used actual saved responses.

The job postings constructed specifically for automated tests are separate from the live dataset and are identified as test fixtures.

## Job Collection

I collected postings from four public job boards.

| Job board | Postings |
|---|---:|
| Airbnb | 214 |
| Figma | 139 |
| Spotify | 87 |
| Linear | 33 |
| **Total** | **473** |

The collection process used four HTTP GET requests across three allow-listed hosts.

I preserved the raw responses so the filtering and evaluation results could be reproduced without collecting the data again.

The collection completed without recorded failures.

I also verified that the collector restricted requests to approved hosts and refused unsupported URLs.

## Filter Design

I designed the filtering process around explicit rules rather than relying entirely on model-generated judgments.

Each rule checks a specific property of the posting.

### Rule R1 — Job Title

I check whether the title contains an accepted software engineering role term.

Postings without an accepted role term are rejected.

### Rule R2 — Seniority

I reject titles containing excluded seniority or position terms, including:

- Senior, Sr., Staff, Principal, Lead.
- Manager, Director, Head.
- Intern, Internship.
- PhD.

These exclusions reflect the initial filtering criteria for the fictional new-graduate candidate.

### Rule R3 — Job Description

I check whether the posting contains a usable description.

A missing description prevents the filter from evaluating the remaining requirements reliably.

### Rule R4 — Location

I check whether the posting satisfies the US-location requirement.

If the location is missing or cannot be determined, the filter can return `cannot_tell`.

### Rule R5 — Years of Experience

I extract years-of-experience requirements from the description.

In version 1.1, I use the largest applicable numeric requirement rather than the smallest.

A requirement of four or more years results in rejection.

An ambiguous range crossing the threshold, or a missing numeric requirement, is intended to produce `cannot_tell`.

The actual observed abstention behavior remains a known limitation.

### Rule R6 — Skill Matching

I compare the job description against the fictional candidate's résumé skills using whole-word matching.

In version 1.1, I require at least one matching skill.

I selected this threshold to reduce the risk of excluding potentially relevant opportunities.

## Filter Version Comparison

### Version 1.0

My initial filtering configuration retained six postings.

The manual audit revealed that four of those six postings were not relevant according to my judgments.

The most important issue was the experience-requirement rule, which selected the smallest number of years.

### Version 1.1

I evaluated three candidate rule changes and compared their effects.

I adopted the improved years-of-experience rule and the updated skill-matching configuration as part of the final changes.

The resulting version retained three postings.

All three were marked relevant in my manual evaluation.

| Metric | Version 1.0 | Version 1.1 |
|---|---:|---:|
| Total postings | 473 | 473 |
| Kept postings | 6 | 3 |
| Manually relevant among keeps | 2 | 3 |
| Manually irrelevant among keeps | 4 | 0 |

These results describe the observed dataset and manual labels.

They do not prove that the filter will perform equally well on unseen job postings.

The held-out results were also examined during rule selection, which limits their independence as a final evaluation.

## Manual Evaluation and Reject Audit

I manually evaluated 71 postings to compare the automated filter against human judgment.

I used fact cards containing posting details without showing the filter's verdict.

This reduced the chance that the automated classification would influence my labels.

The original filter disagreed with my judgments on 10 of the 71 postings.

In the random reject sample, two of 30 rejected postings were manually judged relevant.

The observed proportion was approximately 6.7%, but the reported uncertainty interval was much wider, approximately 0.8%–22%.

I therefore do not treat 6.7% as a precise estimate of the overall miss rate.

During the audit, I also reviewed inconsistent labels and corrected three judgments.

I retained two Engineering Manager positions as relevant after reviewing their requirements.

The complete audit methodology, labels, and results are documented in `AUDIT.md`.

## Shortlist Generation and Claim Verification

After filtering, I generated a shortlist of the retained postings.

For each posting, I evaluated whether the explanation was supported by the job description.

I separated the concepts of relevance and evidence.

A posting may appear relevant without explicitly supporting every claim made about it.

I manually labeled 18 shortlist claims.

The automated checker agreed with my judgments on 10 claims and disagreed on eight.

I reviewed the disagreements and retained my labels while preserving the checker's output.

One important example was the top-ranked posting.

It contained three matching skills, but those skills appeared only inside example lists.

The posting also did not explicitly specify a seniority level or years-of-experience requirement.

This demonstrated that a high relevance score does not necessarily mean every claim is supported by explicit evidence.

The complete analysis is documented in `SHORTLIST.md`.

## Tool Server Implementation

I developed a local tool-server integration to expose the filtering functionality to external clients.

The server provides a read-only `score_posting` tool.

The tool accepts a board and posting identifier, retrieves the corresponding saved posting, applies the filter, and returns the verdict with supporting evidence.

I implemented and tested the integration using:

1. A custom Python client.
2. Claude Code as an MCP client.

I also tested invalid inputs and unsupported operations.

The server rejects unexpected arguments, invalid paths, undeclared tools, and unsupported methods.

I verified the server's file-writing behavior using a process-based test.

The server is intended for local use over standard input/output.

It does not provide authentication and is not intended to be exposed directly over a network.

The implementation details and real session transcripts are documented in `TOOL-SERVER.md`.

## Microsoft Learn MCP Evaluation

I also evaluated the Microsoft Learn MCP server as an external tool integration.

I discovered three available tools.

The server declared no prompts or resources.

During testing, I observed that a session identifier could be decoded into readable JSON containing a `userIdClaim`.

I documented the observation without attempting to probe unrelated external URLs.

I decided to treat Microsoft Learn MCP as a read-only documentation source.

I did not integrate it into the job-search agent or connect it in a session containing private project files.

The recorded interaction is available in `transcripts/mslearn-20261114.jsonl`.

## Claude Evaluation Experiments

I designed experiments to evaluate how Claude classified job postings under different configurations.

I used five configurations and 33 held-out postings per configuration.

This produced 165 recorded model calls.

I compared the effects of individual changes rather than combining multiple modifications without measurement.

One prompt modification changed a wrong answer into an abstention.

This did not necessarily mean that the model became more accurate; it changed the type of outcome.

I also repeated the same configuration twice and found that one of the 33 postings received a different answer.

This demonstrated that identical configurations do not guarantee identical model responses.

Another experiment provided Claude with the tool output instead of the original posting.

Claude abstained six times because some tool responses did not contain the job description needed for independent classification.

The experiment design, saved responses, costs, and metrics are documented in `WHAT-MOVES-THE-SCORE.md` and `experiments/results/`.

## Testing Strategy

I used several testing approaches to validate the system.

### Unit Testing

I tested the individual filtering rules, including title matching, seniority exclusions, location handling, years-of-experience extraction, and skill matching.

### Integration Testing

I tested the collector, filtering pipeline, tool server, and client communication.

### Wrong-Version Testing

I included deliberately incorrect implementations to verify that the tests could detect common mistakes.

The first wrong version used unsafe substring matching, creating problems such as:

- Java matching JavaScript.
- SQL matching PostgreSQL.
- Lead matching leadership.
- US matching Russia.

The second wrong version ignored location requirements.

I verified that the tests detected both categories of error.

### Mutation Testing

I deliberately introduced implementation bugs to evaluate the test suite.

The final mutation results detected 12 of 13 mutants.

The surviving mutant M7 is documented in `tests/mutation-log.md`.

I also strengthened the server-isolation test after identifying that the original version did not execute the server process.

The updated test detects unintended file writes, including mutant M11.

### Reproducibility Testing

I recomputed the reported evaluation numbers from saved artifacts.

This allowed me to verify the calculations without making additional network or model requests.

## Project Structure

```text
Job-Search-Agent-3/
│
├── README.md
├── FILTER.md
├── AUDIT.md
├── SHORTLIST.md
├── TOOL-SERVER.md
├── WHAT-MOVES-THE-SCORE.md
├── FRICTIONAL.md
├── SOURCES.md
│
├── src/
│   ├── collect.py
│   ├── postings.py
│   ├── filter.py
│   ├── run_filter.py
│   ├── audit.py
│   ├── measure_filter.py
│   ├── shortlist.py
│   ├── entailment_example.py
│   ├── mcp_server.py
│   └── mcp_client.py
│
├── tests/
│   ├── test_filter.py
│   ├── test_parts.py
│   ├── mutation_check.py
│   └── mutation-log.md
│
├── experiments/
│   ├── run_claude.py
│   └── results/
│       └── SCORES.md
│
├── prompts/
│
├── runs/
│   └── live-20261114/
│       ├── manifest.json
│       ├── raw/
│       ├── verdicts-v1.0.json
│       └── verdicts-v1.1.json
│
├── audit/
│   ├── hand-verdicts.json
│   └── shortlist-hand-labels.json
│
├── transcripts/
│
└── persona/
```

### Important Files

| File | Purpose |
|---|---|
| `FILTER.md` | Filtering rules, versions, and change history |
| `AUDIT.md` | Manual evaluation and reject-audit results |
| `SHORTLIST.md` | Shortlist generation, claim checking, and evidence analysis |
| `TOOL-SERVER.md` | Tool-server design, tests, and integration |
| `WHAT-MOVES-THE-SCORE.md` | Claude experiments and score analysis |
| `FRICTIONAL.md` | Development challenges, decisions, and unresolved issues |
| `SOURCES.md` | Source references and development provenance |

## Verification Checklist

| Property | Verification |
|---|---|
| Filtering rules R1–R6 | `tests/test_filter.py` |
| Original and updated configurations | Filter tests and saved verdicts |
| Incorrect substring matching | `WrongVersion1_*` |
| Location handling | `WrongVersion2_*` |
| Collector host restrictions | `test_parts.py` |
| Raw response preservation | Collector tests |
| Tool-server input validation | `ToolServer` tests |
| Tool-server file isolation | `ToolServerWrites` tests |
| Mutation-test effectiveness | `tests/mutation-log.md` |
| Manual filter evaluation | 71 hand-labeled postings |
| Shortlist claim evaluation | 18 manually labeled claims |
| Reproducible metrics | Audit, measurement, and score commands |
| Claude integration | Saved client and server transcripts |

## Limitations and Work Not Completed

I documented the following limitations to avoid overstating the system's reliability.

### 1. Shortlist Quality

The three retained postings were manually judged relevant, but that does not guarantee that they are suitable applications.

Two did not explicitly state the required seniority level or years of experience.

### 2. Incomplete Reject Evaluation

I manually evaluated 71 postings, not all 473.

The random reject sample contained 30 postings.

Therefore, I cannot claim to know the exact number of relevant opportunities missed by the filter.

### 3. Manual Label Consistency

Each posting was evaluated once by one person.

I did not conduct a separate repeated-labeling experiment to measure the consistency of my judgments over time.

### 4. Limited Job-Board Coverage

I tested the filter using four job boards and one live collection period.

I did not evaluate its performance on additional boards or a second collection day.

### 5. Incomplete Claude Comparisons

I did not complete a Claude-judge evaluation on the development postings or a held-out experiment measuring the effect of the tool-list change.

### 6. External Tool Boundaries

I did not test Microsoft Learn's `microsoft_docs_fetch` against unrelated external URLs because that would go beyond the intended scope of the integration.

### 7. Abstention Behavior

The filter returned `cannot_tell` zero times across 473 postings.

I identified this as an important limitation that requires further investigation.

### 8. Independent Test Design

Although I reviewed and strengthened the tests, I did not create an additional independent test suite before inspecting the AI-assisted implementation.

This remains an opportunity to improve the independence of future validation.

## What I Am Not Claiming

I am not claiming that:

- The filter reliably identifies every worthwhile job opportunity.
- The observed two misses in 30 random rejects represent the exact miss rate across all rejected postings.
- The prompt revision necessarily improved Claude's overall accuracy.
- The system learned or trained itself from the evaluation results.
- The automated claim checker is always correct when it disagrees with my manual judgments.
- The tool server is secure for unrestricted public network access.
- The results from one collection day will generalize to all future job postings.

My conclusions are limited to the experiments and evidence recorded in this repository.

## Trust Decisions

I evaluated the two tool-server integrations separately.

### My Local Tool Server

**Decision: Trust for local use only.**

I designed the server to operate over standard input/output with a fixed data directory.

I tested its declared functionality, input validation, and file-writing behavior.

Because it does not implement network authentication, I would not expose it directly to untrusted network clients.

### Microsoft Learn MCP Server

**Decision: Use only as a read-only documentation source.**

I treat its returned content as untrusted external data.

I did not integrate it into the job-search agent or connect it to a session containing private project files.

These decisions were made on November 16, 2026.

## My Role and Development Process

I was responsible for the overall development and evaluation of Job-Search Agent 3.

My responsibilities included defining the problem, establishing the filtering requirements, directing implementation, evaluating results, investigating failures, reviewing tests, and deciding which modifications to adopt.

I used Claude Code as an AI-assisted development tool for implementation support, test generation, experimentation, debugging, and documentation.

I did not treat AI-generated code or explanations as automatically correct. I reviewed the outputs, compared them against the project requirements, tested their behavior, and made the final decisions based on the evidence.

My contributions and responsibilities included:

- Defining the filtering criteria for the fictional candidate.
- Establishing the project architecture and evaluation objectives.
- Directing the implementation of the filtering and tool-server components.
- Reviewing and validating the implementation.
- Manually evaluating 71 job postings.
- Manually labeling 18 shortlist claims.
- Identifying and investigating the experience-filtering issue.
- Selecting the version 1.1 rule changes.
- Evaluating the tradeoff between missed opportunities and irrelevant results.
- Reviewing the automated tests and mutation-test outcomes.
- Investigating tool-server integration behavior.
- Analyzing Claude's evaluation results.
- Reviewing and correcting the project reports.
- Documenting limitations and future improvements.

I retained responsibility for the technical decisions and the final project deliverables.

## Driver's Seat — Responsibilities and Decisions

| Project Component | My Responsibility | How I Used Claude | Evidence |
|---|---|---|---|
| Filter design | Defined the requirements, exclusions, thresholds, and intended behavior | Assisted with implementation and rule review | `FILTER.md` |
| Job collection | Established the sources and evaluated collection results | Assisted with collection code and debugging | `runs/live-20261114/` |
| Manual evaluation | Personally judged 71 postings | Helped prepare fact cards and identify inconsistent responses | `audit/hand-verdicts.json` |
| Claim verification | Personally labeled 18 claims | Assisted with automated checking and comparison | `audit/shortlist-hand-labels.json` |
| Filter improvements | Selected the final changes after examining results | Assisted with implementing and measuring alternatives | `FILTER.md` v1.1 |
| Testing | Reviewed test coverage, investigated weaknesses, and validated outcomes | Assisted with test implementation and mutation testing | `tests/` |
| Tool server | Directed the integration, evaluated behavior, and made trust decisions | Assisted with implementation and client testing | `TOOL-SERVER.md` |
| Claude experiments | Established the evaluation goals and analyzed results | Generated responses under the experiment configurations | `experiments/results/` |
| Documentation | Reviewed the evidence, verified findings, and finalized the reports | Assisted with drafting and editing | Project Markdown files |
| Final relevance decisions | Determined whether postings were relevant to the candidate | Provided filtering and supporting evidence | `SHORTLIST.md`, `AUDIT.md` |

## What I Learned

This project helped me strengthen my understanding of software engineering, testing, evaluation, and AI-assisted development.

The most important lesson was that passing tests does not guarantee correct system behavior.

I discovered that a small mistake in the experience-filtering rule could significantly affect which jobs reached the candidate.

I also learned that automated evaluation requires independent validation.

By manually judging postings and checking claims against the original descriptions, I identified problems that would not have been obvious from the filter's output alone.

Mutation testing helped me understand the limitations of my test suite and the importance of designing tests that can detect actual failures.

The Claude experiments showed me that model behavior can vary between identical runs and that providing a tool does not automatically guarantee better decisions.

I also gained practical experience in evaluating trust boundaries when integrating external tools.

Overall, I learned to treat AI-assisted development as an engineering process that requires careful specification, validation, debugging, and evidence-based decision-making.

## Future Improvements

Based on my findings, I would prioritize:

1. Improving years-of-experience extraction for complex requirements.
2. Strengthening abstention behavior when information is incomplete.
3. Supporting related skills and transferable technologies.
4. Creating a fresh, independent held-out evaluation dataset.
5. Evaluating the filter on additional job boards and collection days.
6. Measuring Claude's performance with and without tool access.
7. Improving claim-verification categories to distinguish explicit support from inference.
8. Expanding mutation testing and independent test coverage.

## Final Reflection

Job-Search Agent 3 represents my work on designing, implementing, testing, and evaluating an explainable job-search filtering system.

The project required more than writing filtering logic. I had to define the rules, investigate unexpected results, compare alternatives, validate claims, examine model behavior, and determine whether the system's outputs could be trusted.

I used Claude Code as a supporting development tool, but the project's technical direction, evaluation judgments, decisions, and final conclusions remained my responsibility.

I consider the most important outcome to be the evaluation process itself.

Rather than assuming the system was reliable because it produced results, I tested its assumptions, identified failures, documented tradeoffs, and preserved evidence for the conclusions.

This approach reflects how I aim to build software: with clear requirements, reproducible testing, measurable results, and an understanding of the limitations.

---

## Project Sign-Off

**Project:** Job-Search Agent 3 — The Filter, the Tool, and the Score

**Course:** INFO 7375 — Fall 2026

**Student:** Smit P.

**Date:** November 16, 2026

**Development approach:** Student-directed software engineering with AI-assisted implementation, testing, and documentation.

**Responsibility:** I reviewed the project deliverables, evaluated the technical results, made the final decisions, and documented the known limitations.

**Signed:** Smit P.