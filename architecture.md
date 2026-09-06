# Book architecture — Prompt Engineering for Generative AI

AI+1 Blueprint, Architecture step. Proposed 2026-09-06 following the author's conversational approval of the Vision and 5,000–8,000-word chapter depth. Awaiting architecture review. This document does not approve sources or authorize skipping later gates.

## The spine: inspect, construct, supervise

Use a cumulative mechanism-first sequence, locked to the existing fifteen lessons. Readers first distinguish an output from evidence, then construct the machinery that retrieves context and takes actions, then combine those parts into a supervised system. Do not reorder lessons to make an easier story; use explicit bridges to explain the existing order.

The book is an optional reading path, not fifteen rewritten lab sheets. A reader should be able to follow the argument without a terminal, and then move to the paired lesson to test it. Small numerical examples, short Python excerpts, and explicit state traces carry the explanations. Long reference implementations stay in lessons/.

### Act I — Establish what an answer can prove (chapters 1–3)

Start with a generated answer that varies. Separate probability from truth, a contract from correctness, and an answer from an authorized action. The movement is from inspecting output to recognizing the consequences of giving a system tools.

### Act II — Build and inspect the machinery (chapters 4–9)

Open the controller, expose the permission boundary, inspect code changes, trace retrieval, and examine the protocol connecting tools. Chapter 9 then draws a necessary boundary: changing context is not changing model parameters. The tiny learning implementation is a contrast case, not a claim to train Claude.

### Act III — Supervise a system that can affect others (chapters 10–15)

Turn objectives into plans, actions into evidence, memory into an inspectable record, and evaluations into bounded decisions. Team governance assigns responsibility. The capstone integrates the components into a handoff whose claims another person can check.

## Chapter outcomes and evidence

Bloom levels describe the observable task, not a grade. All chapter practice is ungraded. These are architecture-level outcomes; detailed blocks and Assessment prompts belong in the next planning step.

| Chapter and paired lesson | Measurable outcomes | Evidence of capability |
|---|---|---|
| 01 — Randomness and first prompts | Calculate a small normalized sampling distribution (Apply); predict and compare temperature changes (Analyze); distinguish variation from factual reliability (Evaluate). | A hand-worked example and a sampling report with a stated limit. |
| 02 — Prompt contracts and evaluation | Implement a response contract (Apply); construct an example that passes structure but fails meaning (Create); compare prompt revisions on held-out cases (Evaluate). | A contract, counterexample, and reproducible prompt comparison. |
| 03 — Chat, assistant, and agent | Trace how the same task changes across interfaces (Analyze); classify proposed actions by consequence and authority (Analyze); justify the least capable interface sufficient for the task (Evaluate). | An action-surface comparison with concrete boundaries. |
| 04 — The agent loop | Trace state and observations through a bounded controller (Analyze); implement stop and budget conditions (Apply); diagnose a repeated-action failure (Evaluate). | A state trace showing a successful stop and a refusal or exhausted budget. |
| 05 — Tools, permissions, and boundaries | Implement input and action checks (Apply); distinguish tool availability from authorization (Analyze); test an out-of-scope proposal (Evaluate). | A permission policy and boundary tests. |
| 06 — Claude Code and evidence-based diff review | Explain a proposed diff before accepting it (Analyze); choose tests tied to the change (Evaluate); justify acceptance, revision, or rejection (Evaluate). | A review packet connecting claims to inspected code and actual checks. |
| 07 — Context retrieval and Claude Cowork | Calculate a lexical retrieval score on a small corpus (Apply); trace chunk selection and omissions (Analyze); evaluate whether the selected sources support an answer (Evaluate). | A source-grounded packet with selected context and an unsupported-answer case. |
| 08 — MCP from scratch | Trace the teaching server's initialization and tool lifecycle (Analyze); implement the lesson's bounded protocol example (Apply); distinguish interoperability from trust (Evaluate). | A protocol transcript, capability inventory, and trust decision. |
| 09 — Training mechanics and Claude configuration | Calculate and explain a tiny parameter update (Apply); compare training, prompting, configuration, and retrieval (Analyze); identify which claims the toy model cannot establish about Claude (Evaluate). | A training-versus-context report anchored to a real toy-model run. |
| 10 — Planning before acting | Convert a bounded objective into an executable plan (Create); connect steps to evidence and permissions (Analyze); reject an underspecified action (Evaluate). | A reviewed plan with constraints, verification, and stop conditions. |
| 11 — Claude tool use and verification | Trace tool_use and tool_result messages through the controller (Analyze); connect each reported result to a check (Apply); identify unsupported success claims (Evaluate). | A tool-evidence matrix distinguishing proposals, executions, and verified outcomes. |
| 12 — Memory and multiple agents | Reconstruct a shared-memory failure from records (Analyze); test stale or conflicting context (Apply); justify a division of work and review responsibilities (Evaluate). | A shared-memory premortem with an inspectable failure and proposed mitigation. |
| 13 — Evaluation and human approval gates | Design a bounded evaluation set (Create); associate approvals with specific proposals and evidence (Apply); decide whether evidence supports proceeding (Evaluate). | A gate design including an adversarial case and a documented refusal condition. |
| 14 — Team governance and applied ethics | Map responsibilities and affected people (Analyze); create a team AI-use register (Create); justify escalation and consent boundaries (Evaluate). | A register naming accountable people without inventing their approval. |
| 15 — Supervised agentic capstone | Integrate the mechanisms into a bounded workflow (Create); demonstrate a recovery and independently checked outcome (Evaluate); defend a reproducible handoff and its exclusions (Evaluate). | The existing capstone packet, implementation, tests, and honest evidence. |

## Narrative chapter anatomy

Each chapter opens with one concrete tension that the reader can inspect. Use a documented result from the matching lesson or an explicitly labeled hypothetical; never invent an anecdote, observation, person, or authorial memory.

After the opening, state the capabilities and prerequisites briefly. Develop two or three connected mechanisms through the same cycle: pose the problem, expose the moving parts, work a small example, and judge the trade-off. Use a counterexample to test the explanation rather than merely announcing a limitation.

An integration passage returns to the opening tension. It should identify what is now explainable and what remains unproved. End the main argument with capabilities gained and a specific question that motivates the next chapter. Use descriptive headings rather than repeating an identical lab template fifteen times.

Preserve the from-scratch learning sequence: ask for a prediction or small attempt before revealing the worked derivation or reference behavior. Worked examples may explain their reasoning; graduated Assessments do not expose inline answers. Do not request private model chain-of-thought.

The approved target is 5,000–8,000 words per chapter, approximately 75,000–120,000 words overall. Depth comes from explanation and worked examples, not repeated definitions or decorative stories. This is a planning range, not a claim about an existing manuscript.

## Assessment plan

| Apparatus | Status | Scope and placement |
|---|---|---|
| Graduated ungraded Assessments | Needed | All 15 chapters: warm-up, application, synthesis, and challenge. Reuse the lesson's capability and avoid turning the reading path into a second graded course. |
| Existing six-question lesson quizzes | Needed as linked companion | All 15 chapters link to the corresponding lesson knowledge check. Keep these ungraded; do not generate a competing answer key. |
| Fully worked examples | Needed | All chapters, embedded in the explanation; later specifications identify the exact example and its verification method. |
| Separate worked-solutions edition | Out of scope | No new solutions volume in this book request. Existing reference implementations remain available after the reader's first attempt. |
| Anki / flashcards | Out of scope | No generation or build configuration now. |
| Exam bank | Out of scope | No graded book exams. |
| Canvas module export | Out of scope | The existing NEU Assignment schedule stays in the course documents; no new LMS package. |
| Optional videos | Optional existing course practice | No book production requirement, no separate points, and no prerequisite for reading. |

NEU's 60/10/10/20 Assignment rubric and ten-day cadence remain in prerequisites/ and the submission guide, not the chapter narrative or EPUB's core teaching material.

## Cross-book notes and evidence

Keep the closing sections selective and in the established order: Anthropics, Computational Skepticism, Conducting AI, Irreducibly Human. Read and cite the relevant source passages during research; do not infer relevance from titles or copy unresolved claims. Where included, Irreducibly Human must name concrete AI tasks and human responsibilities. The reader must not need another local checkout to understand a note.

Use the existing lesson code and tests as inspectable teaching sources, not proof of production behavior. Verify changing Claude and protocol details against primary documentation during Research. Keep numerical examples reproducible and distinguish toy mechanisms, offline fixtures, simulations, and actual live calls.

## Cajal and reading-format architecture

Reserve figures for relationships that prose cannot explain as efficiently: sampling transformations, controller states, authorization boundaries, retrieval selections, message lifecycles, and evidence-to-decision mappings. A figure count is not a chapter-completeness metric. Cajal selection and full specifications follow approved text; no illustrations are generated in this phase.

Plan static, captioned figures with meaningful alt text and grayscale-readable encodings. Each important relationship must also be stated in prose so the argument survives a small e-reader screen or an unavailable image. Separate geometry/layout checks from domain-accuracy review.

The canonical manuscript files will be chapters/NN-lesson-slug.md, with exactly one numbered chapter per lesson. Use an explicit ordered list for the EPUB rather than including chapters/README.md through a wildcard. Keep source records and sidecars out of the reading edition. Use EPUB3 navigation and embedded static assets; no interactive D3 or network access is necessary to read the book. Build tooling must stay separate from the Python lesson runtime. EPUB construction and Kindle preview are later, distinct checks.

## Review boundary

Approve or revise the three-act sequence, outcomes, and Assessment plan. Then produce chapter specifications with 4–6 blocks, a fully worked example, and assessable practice per chapter. Approval here does not sign Gate 0 as a whole; chapter specifications, risks, and the reconciled outline still require review.
