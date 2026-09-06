# INFO 7375 — Prompt Engineering for Generative AI

**Required course access:** Students have Claude Code through Northeastern. Every exercise assumes an active Claude Code account. Begin at [Northeastern's Claude portal](https://claude.northeastern.edu/); see the [access summary](docs/neu-claude-access.md). Public readers need their own Claude Code-enabled account. Direct API calls are optional and explicit so students learn the Python mechanics before spending API credits; university Claude Code access is not treated as an API-key entitlement.

## Course information

Professor: Nik Bear Brown. Email: ni.brown@neu.edu. Office: 505A Dana Hall. Office hours: Zoom by appointment. Classes: on ground in Boston. Course delivery and assignment dates: Canvas. Prerequisites: a strong programming background and a commitment to independent research.

This instructional adaptation follows the supplied syllabus while reorganizing the practical work around a from-scratch Python curriculum and Claude-only model use. The [original supplied text](docs/original-syllabus.txt) remains the source record for administrative policies. Conflicts needing instructor resolution are listed in [instructor decisions](docs/instructor-decisions.md); this document does not silently resolve them.

## Course description

Students learn to construct, evaluate, and supervise generative AI workflows by implementing their underlying mechanisms in Python and applying them through Claude. Prompt design is treated as an experiment with held-out evaluation. Retrieval is built from lexical vectors before discussing neural embeddings. Agents are explicit loops with tool boundaries, state, evidence, and stop conditions. Training concepts are taught through an actual small parameter-learning example and distinguished from inference configuration.

All model-facing coursework uses Claude. Claude Code is the working environment for every exercise, including source-grounded knowledge work. Claude chat and Cowork provide comparison interfaces where specified; the same file-based task remains executable through Claude Code. The optional Messages API extension exposes the transport and tool protocol. Reference programs use only Python's standard library and run offline before students apply the mechanism with Claude Code. External integrations must remain within the instructor-approved data and action boundary.

## Learning outcomes

By the end of the course, students can:

1. Explain probabilistic generation and evaluate prompt changes with controlled experiments.
2. Build prompt contracts, lexical retrieval, and evidence checks in Python.
3. Distinguish parameter training from prompting, configuration, and retrieval.
4. Implement bounded tool-use loops and a minimal MCP teaching server.
5. Diagnose shared-memory and multi-agent failures with reproducible traces.
6. Design human approval gates tied to specific proposals and evidence.
7. Deliver and defend a supervised Claude project with reproducible artifacts.

## Teaching method

Before class, students prepare through 5–15 minute instructor videos and assigned reading. In class, they predict behavior, build a small mechanism, test it, use Claude to apply or critique it, and ship an artifact. Students must explain every submitted implementation, including AI-assisted portions. The reference code is an inspectable solution, not a substitute for the student's own attempt.

## Weekly schedule

| Week | Reading / theory alignment | In-class build | Ungraded Assessment artifact |
|---|---|---|---|
| 1 | Module 1 | [Randomness and first prompts](lessons/01-randomness-and-first-prompts/docs/en.md) | sampling report |
| 2 | Module 1; Module 2 video | [Prompt contracts and evaluation](lessons/02-prompt-contracts-and-evaluation/docs/en.md) | prompt experiment |
| 3 | Claude Agentic AI Ch. 1 | [Chat, assistant, and agent](lessons/03-chat-assistant-agent/docs/en.md) | action surface comparison |
| 4 | Claude Agentic AI Ch. 2 | [The agent loop](lessons/04-the-agent-loop/docs/en.md) | agent trace |
| 5 | Claude Agentic AI Ch. 3 | [Tools, permissions, and boundaries](lessons/05-tools-and-permissions/docs/en.md) | permission policy |
| 6 | Claude Agentic AI Ch. 4 | [Claude Code and evidence-based diff review](lessons/06-claude-code-and-diff-review/docs/en.md) | review packet |
| 7 | Claude Agentic AI Ch. 5; Module 3 video | [Context retrieval and Claude Cowork](lessons/07-context-retrieval-and-cowork/docs/en.md) | source grounded task packet |
| 8 | Claude Agentic AI Ch. 6 | [MCP from scratch](lessons/08-mcp-from-scratch/docs/en.md) | mcp evaluation and progress reel |
| 9 | Module 4 | [Training mechanics and Claude configuration](lessons/09-training-and-configuration/docs/en.md) | training versus context report |
| 10 | Module 5 video; Claude Agentic AI Ch. 7 | [Planning before acting](lessons/10-planning-before-acting/docs/en.md) | reviewed plan |
| 11 | Module 5 video; Claude Agentic AI Ch. 8 | [Claude tool use and verification](lessons/11-tool-use-and-verification/docs/en.md) | tool evidence matrix |
| 12 | Module 5 video; Claude Agentic AI Ch. 9 | [Memory and multiple agents](lessons/12-memory-and-multiple-agents/docs/en.md) | shared memory premortem |
| 13 | Module 5 video; Claude Agentic AI Ch. 10 | [Evaluation and human approval gates](lessons/13-evaluation-and-approval-gates/docs/en.md) | approval gate design |
| 14 | Module 5 video; Claude Agentic AI Ch. 11 | [Team governance and applied ethics](lessons/14-team-governance-and-ethics/docs/en.md) | team ai use register |
| 15 | Claude Agentic AI Ch. 12 | [Supervised agentic capstone](lessons/15-supervised-capstone/docs/en.md) | capstone packet |

Weeks 1–2 retain introductory prompting and randomness. Module 2 video theory covers persona, audience, question refinement, few-shot patterns, task decomposition, and verification; students test those patterns rather than assume they work. Concise explanations and evidence are assessed without requiring private model chain-of-thought.

Module 3 video theory accompanies Week 7: representations, vector similarity, chunking, indexing, retrieval evaluation, and context construction. Framework-specific implementation is replaced by transparent Python functions. The initial implementation uses lexical vectors; it is not described as neural semantic search.

Week 9 preserves pretraining, instruction tuning, and RLHF as theory topics. Its actual build trains a tiny logistic classifier to expose loss and gradients. Students compare parameter updates with Claude prompt/context changes. No assignment assumes access to Claude weights or a public fine-tuning endpoint.

Weeks 10–14 pair architecture theory with supervision practice: planning and ReAct; function calling and verification; memory and multiple agents; evaluation and approval gates; ethics and team responsibility. Week 15 integrates those components in a real, bounded project.

## NEU-only preparation for recorded work

Students taking INFO 7375 at Northeastern should read the [AI policy](prerequisites/ai-policy.md) and [Relative Quartile rubric (20/100)](prerequisites/relative-quartile.md) in the [course prerequisites](prerequisites/README.md). [Brutalist video setup](prerequisites/brutalist-video.md) is an optional workflow before the first optional recorded explanation, not a required tool. This preparation is separate from the numbered book lessons; it does not add a week or independent-reader requirement. Videos have no separate points and are not required; Canvas publishes Assignment deadlines.

Assignment mechanisms remain Python. Brutalist's separate checkout supplies the media toolchain (including Node/Remotion), with no requirement for students to learn a second programming stack. Course-related films are organized under [youtube/](youtube/README.md). Public uploading is not implied by a course submission.

## Materials

- Nik Bear Brown, Prompt Engineering for Generative AI, supplied course text for Weeks 1–2 and 9. Bibliographic details in the supplied syllabus include an unresolved ISBN placeholder.
- Nik Bear Brown, Claude Agentic AI, Bear Brown LLC, 2026; instructor-provided EPUB/PDF, Chapters 1–12 aligned above.
- This repository supplies the Module 5 Python lab companion. The original second theory text is unnamed; the instructor must supply its citation or formally designate the replacement.
- [Instructor YouTube channel](https://www.youtube.com/user/nikbearbrown) for assigned and supplemental videos. No lesson-specific video URLs have been invented.
- [Primary technical references](docs/references.md), checked during the adaptation.

## Assessments and Assignments

Existing lesson exercises and quizzes are **Assessments: ungraded practice**. Graded **Assignments are due every 10 days**, each worth **100 points: 60 implementation, 10 Frictional, 10 proper GitHub version posting, and 20 Relative Quartile**. Explainer videos, including the Week 8/15 Progress Reel ideas, are optional contributions to comparative quality, not separate requirements or point categories. See [ASSESSMENT.md](ASSESSMENT.md). Canvas publishes exact dates and the Assessments covered in each Assignment.

Use LastName_FirstName_INFO7375_Assignment_#.zip. Include author names, collaborators, Claude assistance disclosure, specific human/AI contribution descriptions, license, and style guide. Use Python and PEP 8. Do not submit secrets or restricted data. Students must be able to explain all submitted work.

Administrative rules, accommodations, attendance, academic integrity, student support, and other university policies remain in the original source record. The supplied late-penalty and grading conflicts require instructor clarification before this adaptation is distributed as a final syllabus.
