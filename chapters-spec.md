# Chapter specifications — Prompt Engineering for Generative AI

AI+1 Blueprint, Chapter Specifications step. Drafted 2026-09-06 following the author's conversational approval of Vision and Architecture. Awaiting review; these are writing specifications, not chapter manuscripts or verified research.

## Common writing contract

One chapter per lesson, same numeric slug, 5,000–8,000 words in the approved narrative Teardown voice. The capability and outcomes below are requirements for the future text, not assertions about reader achievement. Each five-block sequence should become a connected explanation, not a listicle. Start from a labeled hypothetical or an observed, source-recorded result. Introduce notation before using it. Show reasoning through the worked example without inventing measurements, quotations, or authorial experiences.

Each chapter includes a prediction before the worked explanation, concise objectives and prerequisites, a fully worked and reproducible example, misconceptions tested with counterexamples, integration, ungraded Assessments, a capabilities summary, and a bridge. The four Assessment seeds below cover warm-up, application, synthesis, and challenge; expand during drafting to 2–3 warm-up, 3–4 application, 2–3 synthesis, and 1–2 challenge prompts, with named objectives and no inline solutions. Reuse the existing lesson knowledge check; do not create a competing quiz bank.

Research inputs for every chapter are the matching lesson's docs/en.md, code/main.py, code/tests/test_main.py, and outputs/artifact-brief.md. This planning pass inspected the architecture and the implementation interfaces/artifact requirements; full source review and execution belong in Research before drafting. Reject a planned example if the actual implementation does not support it; document the revision instead of inventing behavior.

Figure entries are candidate explanatory jobs for later Cajal review, not generated assets or mandatory quotas. Read the complete Cajal and design instructions before production. Preserve selective closing source notes in the established order; determine their exact citations during Research, not from topic similarity alone. No NEU grading logistics, required explainer videos, new model providers, or paid calls are introduced.

## Chapter 1 — Randomness and first prompts

**Manuscript:** `chapters/01-randomness-and-first-prompts.md`  
**Paired source:** [Lesson 1](lessons/01-randomness-and-first-prompts/docs/en.md)  
**Capability:** Calculate and inspect a sampling distribution without mistaking it for evidence of truth.  
**Prerequisites:** Python functions, exponentials, and basic probability.

**Opening tension:** Suppose the same prompt produces two different answers. Which moving part changed? Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Scores are not probabilities.
2. Normalization and numerical stability.
3. Temperature changes the distribution.
4. Seeded sampling and finite counts.
5. Consistency versus factual support.

**Fully worked example:** Use three explicitly chosen toy logits. Predict their ordering, calculate normalized probabilities, sample with a fixed seed, and compare empirical counts at two temperatures. Recompute every printed number from the lesson implementation.

**Outcomes and ungraded Assessment seeds:**

1. Calculate probabilities for three scores (Apply).
2. Change temperature and predict the ordering before running (Apply).
3. Compare two sample sizes and explain deviations from expected counts (Analyze).
4. Design a check that can reject a consistently false answer (Evaluate).

**Cajal candidate:** A probability transformation beside observed sample counts; label constructed inputs and sampled observations separately.

**Bridge:** A distribution can explain variation. What specifies an acceptable answer?

## Chapter 2 — Prompt contracts and evaluation

**Manuscript:** `chapters/02-prompt-contracts-and-evaluation.md`  
**Paired source:** [Lesson 2](lessons/02-prompt-contracts-and-evaluation/docs/en.md)  
**Capability:** Build and evaluate a contract that separates structural validity from supported claims.  
**Prerequisites:** Chapter 1; Python dictionaries and JSON.

**Opening tension:** Suppose a perfectly formatted JSON answer contains a false statement. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Shape, types, and missing fields.
2. Source identifiers versus source support.
3. Development and held-out cases.
4. Baseline and revised prompts.
5. What a pass rate leaves out.

**Fully worked example:** Construct a tiny labeled response set containing malformed JSON, an unknown source ID, and a structurally valid unsupported claim. Trace validate and pass_rate, then explain which semantic checks are outside that validator.

**Outcomes and ungraded Assessment seeds:**

1. Classify malformed and well-formed responses (Analyze).
2. Implement one contract boundary test (Apply).
3. Compare revisions on held-out cases without changing the test after inspection (Evaluate).
4. Construct a semantic counterexample to the validator (Create).

**Cajal candidate:** Two independent checks: format contract and claim support, with a response that passes only one.

**Bridge:** What changes when an answer can trigger an action?

## Chapter 3 — Chat, assistant, and agent

**Manuscript:** `chapters/03-chat-assistant-agent.md`  
**Paired source:** [Lesson 3](lessons/03-chat-assistant-agent/docs/en.md)  
**Capability:** Choose an interface by tracing capabilities and consequences rather than product labels.  
**Prerequisites:** Chapters 1–2; lists and event records.

**Opening tension:** Suppose summarizing a folder becomes editing one of its files. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Responses versus persistent work.
2. Event traces and capabilities.
3. The action surface.
4. Authority separate from capability.
5. Choosing sufficient autonomy.

**Fully worked example:** Use one source-grounded folder task and three explicitly constructed event traces. Apply missing and classify, then compare what each trace establishes about actions and what still requires permission evidence.

**Outcomes and ungraded Assessment seeds:**

1. Identify the action-bearing events (Analyze).
2. Run the capability comparison on a new task (Apply).
3. Choose the least capable sufficient interface and justify it (Evaluate).
4. Design a trace where the interface name is misleading (Create).

**Cajal candidate:** The same task across three action surfaces; mark read and write boundaries.

**Bridge:** A tool-capable interface still needs something to run its next step.

## Chapter 4 — The agent loop

**Manuscript:** `chapters/04-the-agent-loop.md`  
**Paired source:** [Lesson 4](lessons/04-the-agent-loop/docs/en.md)  
**Capability:** Implement and diagnose an explicit bounded controller.  
**Prerequisites:** Chapter 3; loops, state, and functions.

**Opening tension:** Suppose the system repeats the same search and calls the repetition progress. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Policy and controller are different pieces.
2. Actions become observations.
3. Updating state.
4. Completion and budget exhaustion.
5. Failure traces worth keeping.

**Fully worked example:** Trace run with a deterministic policy through records and a bounded turn count. Compare a supported stop with a repeated-action policy that exhausts its budget. Never label the fixture a live Claude run.

**Outcomes and ungraded Assessment seeds:**

1. Trace one turn by hand (Apply).
2. Add a boundary test for the turn budget (Apply).
3. Explain why stopping is not always success (Analyze).
4. Propose a repeated-action detector and test a false-positive case (Evaluate).

**Cajal candidate:** Controller state sequence with distinct success and exhausted-budget exits.

**Bridge:** A bounded loop can still do an unauthorized thing once.

## Chapter 5 — Tools, permissions, and boundaries

**Manuscript:** `chapters/05-tools-and-permissions.md`  
**Paired source:** [Lesson 5](lessons/05-tools-and-permissions/docs/en.md)  
**Capability:** Enforce a file-action boundary and describe the limits of the enforcement.  
**Prerequisites:** Chapter 4; filesystem paths and exceptions.

**Opening tension:** Suppose a harmless-looking relative path points outside the approved folder. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Names versus resolved targets.
2. Approved roots and operations.
3. Read versus write authority.
4. Traversal and denied proposals.
5. What the toy boundary cannot guarantee.

**Fully worked example:** Trace authorize for an in-root read, a traversal attempt, and a write with and without approval. Use a temporary sandbox and inspect the actual path-resolution behavior before stating its guarantees.

**Outcomes and ungraded Assessment seeds:**

1. Identify an escaping path (Analyze).
2. Implement and run traversal rejection tests (Apply).
3. Explain the difference between a valid path and an approved write (Analyze).
4. Evaluate a symlink or concurrent-change case without claiming the toy check is a complete sandbox (Evaluate).

**Cajal candidate:** Resolved path destinations on either side of one explicit authorization boundary.

**Bridge:** An authorized change still needs review of what changed.

## Chapter 6 — Claude Code and evidence-based diff review

**Manuscript:** `chapters/06-claude-code-and-diff-review.md`  
**Paired source:** [Lesson 6](lessons/06-claude-code-and-diff-review/docs/en.md)  
**Capability:** Reach an evidence-backed decision about a proposed code change.  
**Prerequisites:** Chapter 5; diffs and unit tests.

**Opening tension:** Suppose a short patch passes the old tests but changes an unstated assumption. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Reproduction before the proposed fix.
2. Reading the diff as behavior.
3. Scope and allowed files.
4. Targeted checks and gaps.
5. Accept, revise, or reject.

**Fully worked example:** Use a small before/after Python change within the lesson's review model. Record a prediction before running targeted tests, inspect diff and review, and distinguish passing checks from human approval.

**Outcomes and ungraded Assessment seeds:**

1. Explain one changed line's behavior (Analyze).
2. Write a test aimed at the proposed change (Apply).
3. Defend a review verdict using actual checks (Evaluate).
4. Design a case old tests miss without fabricating a real defect (Create).

**Cajal candidate:** Changed behavior mapped to the tests and unanswered review questions.

**Bridge:** Code can be inspected. Which source material reached the model?

## Chapter 7 — Context retrieval and Claude Cowork

**Manuscript:** `chapters/07-context-retrieval-and-cowork.md`  
**Paired source:** [Lesson 7](lessons/07-context-retrieval-and-cowork/docs/en.md)  
**Capability:** Trace lexical retrieval and evaluate whether selected evidence supports an answer.  
**Prerequisites:** Chapters 2 and 6; vectors and basic arithmetic.

**Opening tension:** Suppose the most similar document answers a different question. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Token counts as a representation.
2. Cosine similarity step by step.
3. Ranking and top-k omissions.
4. Source-grounded task construction.
5. Relevance is not entailment.

**Fully worked example:** Build a small declared corpus, hand-compute one cosine score, reproduce retrieve ordering, and inspect an answer against exact source passages. Include a relevant-looking but insufficient document.

**Outcomes and ungraded Assessment seeds:**

1. Calculate a vector overlap (Apply).
2. Change the query and predict the new ranking (Apply).
3. Identify a claim unsupported by the selected passages (Evaluate).
4. Design an abstention rule and test a counterexample (Create).

**Cajal candidate:** Query, ranked candidates, selected context, and omitted evidence in one bounded flow.

**Bridge:** Retrieval selects information. A protocol connects capabilities.

## Chapter 8 — MCP from scratch

**Manuscript:** `chapters/08-mcp-from-scratch.md`  
**Paired source:** [Lesson 8](lessons/08-mcp-from-scratch/docs/en.md)  
**Capability:** Trace a minimal tool protocol while separating interoperability from trust.  
**Prerequisites:** Chapters 4–7; JSON messages and state.

**Opening tension:** Suppose a server introduces its tools perfectly but offers an unsafe action. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Initialization as a state transition.
2. Capability discovery.
3. Requests, identifiers, and results.
4. Malformed and out-of-order messages.
5. Protocol compatibility versus authorization.

**Fully worked example:** Inspect the teaching Server and its supported lifecycle. Trace initialization, discovery, and a bounded tool request, then an invalid transition. Research must confirm how this subset differs from the current MCP specification.

**Outcomes and ungraded Assessment seeds:**

1. Identify a request and its matching response (Analyze).
2. Exercise an out-of-order message against the teaching server (Apply).
3. Compare two advertised tools under the same permission policy (Evaluate).
4. Propose a compatibility test that does not claim to certify trust (Create).

**Cajal candidate:** A message sequence with legal and rejected transitions; no implied full-standard coverage.

**Bridge:** Connecting a tool is not training a model.

## Chapter 9 — Training mechanics and Claude configuration

**Manuscript:** `chapters/09-training-and-configuration.md`  
**Paired source:** [Lesson 9](lessons/09-training-and-configuration/docs/en.md)  
**Capability:** Distinguish actual parameter learning from changes to prompts, context, or settings.  
**Prerequisites:** Chapters 1–2 and 7–8; algebra and introductory derivatives explained as needed.

**Opening tension:** Suppose someone calls a revised system prompt training. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. A tiny predictor and its parameters.
2. Loss as an explicit objective.
3. Gradient updates.
4. Held-out behavior.
5. Where the analogy to Claude ends.

**Fully worked example:** Walk one logistic-model update from a small declared dataset, then run train and record loss and parameters. Contrast it with changed prompts and retrieved text; make no claim of access to Claude weights.

**Outcomes and ungraded Assessment seeds:**

1. Calculate a prediction with stated parameters (Apply).
2. Trace one parameter update (Apply).
3. Classify four proposed system changes by what they modify (Analyze).
4. Evaluate whether lower training loss supports a held-out claim (Evaluate).

**Cajal candidate:** Parameter-update path versus input/configuration changes, with different mutable objects labeled.

**Bridge:** Once we know what changes, we can specify what should change.

## Chapter 10 — Planning before acting

**Manuscript:** `chapters/10-planning-before-acting.md`  
**Paired source:** [Lesson 10](lessons/10-planning-before-acting/docs/en.md)  
**Capability:** Write a plan that constrains scope, dependencies, evidence, and stopping.  
**Prerequisites:** Chapters 4–9; dependency graphs introduced here.

**Opening tension:** Suppose a fluent plan never says what would count as finished. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Objectives and exclusions.
2. Required fields versus meaningful fields.
3. Dependencies and ordering.
4. Evidence and stop conditions.
5. Human revision before action.

**Fully worked example:** Construct a bounded plan, trace missing_fields and order, and test a missing field and a dependency cycle. Compare structural validity with an executable plan whose individual steps have checks.

**Outcomes and ungraded Assessment seeds:**

1. Find an untestable completion claim (Analyze).
2. Order a small dependency graph (Apply).
3. Revise one step to name evidence and authority (Create).
4. Reject a structurally valid but unsafe plan with reasons (Evaluate).

**Cajal candidate:** A dependency chain with evidence attached to each state-changing step.

**Bridge:** A plan predicts action; a tool result must show what happened.

## Chapter 11 — Claude tool use and verification

**Manuscript:** `chapters/11-tool-use-and-verification.md`  
**Paired source:** [Lesson 11](lessons/11-tool-use-and-verification/docs/en.md)  
**Capability:** Connect a tool request, execution, result message, and independently checked claim.  
**Prerequisites:** Chapters 4–5, 8, and 10.

**Opening tension:** Suppose the final answer says a tool succeeded, but the trace contains only a request. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Tool schema and argument validation.
2. Dispatch as an application responsibility.
3. tool_use and tool_result association.
4. Bounded continuation and failure.
5. Evidence beyond the final sentence.

**Fully worked example:** Use the existing offline tool loop and transport fixtures to trace a valid call and an invalid request. Inspect IDs and results. Keep any optional direct API demonstration separately labeled and explicitly authorized.

**Outcomes and ungraded Assessment seeds:**

1. Match requests to results by ID (Apply).
2. Test a rejected argument or duplicate ID (Apply).
3. Audit a final claim against the trace (Evaluate).
4. Design an independent check that does not simply ask the same model again (Create).

**Cajal candidate:** Request, validated dispatch, execution evidence, result message, final claim; show the unsupported shortcut.

**Bridge:** A verified result today can become stale shared memory tomorrow.

## Chapter 12 — Memory and multiple agents

**Manuscript:** `chapters/12-memory-and-multiple-agents.md`  
**Paired source:** [Lesson 12](lessons/12-memory-and-multiple-agents/docs/en.md)  
**Capability:** Diagnose stale shared state and assign work without multiplying unchecked claims.  
**Prerequisites:** Chapters 4, 7, and 11; versioned records.

**Opening tension:** Suppose two workers act on different versions of the same note. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. What a memory record actually stores.
2. Freshness and revision boundaries.
3. Conflicting updates.
4. Untrusted text in shared notes.
5. Division of labor and incident replay.

**Fully worked example:** Inspect Memory and construct a deterministic stale-read or conflicting-update scenario supported by its actual interface. Reconstruct the sequence from records and evaluate a proposed mitigation; no fictitious agent conversation.

**Outcomes and ungraded Assessment seeds:**

1. Identify which state a worker read (Analyze).
2. Reproduce a supported conflict in the teaching model (Apply).
3. Assign independent checks to roles and explain their limits (Evaluate).
4. Design a retention or replay policy with a privacy boundary (Create).

**Cajal candidate:** Two readers and one versioned record across an update; show when assumptions diverge.

**Bridge:** More records are not enough. Which evidence authorizes the next step?

## Chapter 13 — Evaluation and human approval gates

**Manuscript:** `chapters/13-evaluation-and-approval-gates.md`  
**Paired source:** [Lesson 13](lessons/13-evaluation-and-approval-gates/docs/en.md)  
**Capability:** Bind a decision to a specific proposal and evaluate the evidence behind it.  
**Prerequisites:** Chapters 5, 10–12; hashes explained from their role, not cryptographic internals.

**Opening tension:** Suppose an approval is reused after the proposal changes. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. Evaluation sets and their exclusions.
2. Fingerprinting the actual proposal.
3. Decision scope and expiry assumptions.
4. Changed proposals and rejected approvals.
5. Human judgment beyond matching fields.

**Fully worked example:** Trace fingerprint and approved for a proposal and a modified version using clearly labeled simulated decisions. Demonstrate the mismatch; do not imply the fixture authenticates a real person.

**Outcomes and ungraded Assessment seeds:**

1. Compare two proposal representations (Analyze).
2. Test an approval against a changed proposal (Apply).
3. Build a small evaluation set with a refusal case (Create).
4. Explain what a matching fingerprint does not prove about identity or informed consent (Evaluate).

**Cajal candidate:** Approval linked to one proposal version, with the changed-version route denied.

**Bridge:** A decision record needs a responsible person and an escalation path.

## Chapter 14 — Team governance and applied ethics

**Manuscript:** `chapters/14-team-governance-and-ethics.md`  
**Paired source:** [Lesson 14](lessons/14-team-governance-and-ethics/docs/en.md)  
**Capability:** Make responsibilities, harms, retention, and escalation inspectable.  
**Prerequisites:** Chapters 5, 12–13.

**Opening tension:** Suppose every required governance field is filled, but nobody owns the response to failure. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. A register is not a responsible team.
2. Affected people and concrete harms.
3. Mitigation owners and thresholds.
4. Data retention and escalation.
5. When to defer instead of automate.

**Fully worked example:** Use a hypothetical register entry, run assess, and compare a missing-field failure with a complete but substantively weak record. Distinguish structural checks from actual agreement by named people.

**Outcomes and ungraded Assessment seeds:**

1. Locate the owner of a proposed mitigation (Analyze).
2. Test a missing retention or escalation field (Apply).
3. Rewrite a vague threshold as an observable trigger (Create).
4. Evaluate a complete register whose proposed mitigation does not address its harm (Evaluate).

**Cajal candidate:** Incident signal to accountable owner to bounded response, with unresolved authority visible.

**Bridge:** Governance must survive contact with the system being handed over.

## Chapter 15 — Supervised agentic capstone

**Manuscript:** `chapters/15-supervised-capstone.md`  
**Paired source:** [Lesson 15](lessons/15-supervised-capstone/docs/en.md)  
**Capability:** Deliver and defend a bounded workflow whose evidence another person can inspect.  
**Prerequisites:** Chapters 1–14.

**Opening tension:** Suppose a polished packet passes validation but cannot reproduce its central result. Treat this as a labeled hypothetical unless later research supplies an actual documented run.

**Content blocks:**

1. The need and consenting owner.
2. Ten artifacts as one connected argument.
3. Implementation, tests, and controlled failure.
4. Recovery and independent checks.
5. Handoff, exclusions, and transfer.

**Fully worked example:** Trace the ten-artifact packet validator against a complete fixture and an incomplete or escaping packet. Then specify how a real bounded workflow supplies substantive evidence that file presence cannot establish. Actual stakeholder consent is never synthesized.

**Outcomes and ungraded Assessment seeds:**

1. Map one claim to its supporting packet artifact (Analyze).
2. Run a structural rejection case (Apply).
3. Integrate a failure, reviewed recovery, and independent check into a bounded demonstration (Create).
4. Defend ship, defer, or reduce scope from evidence rather than presentation quality (Evaluate).

**Cajal candidate:** Need to boundary to action to evidence to human decision to handoff, with one unsupported link exposed.

**Bridge:** The closing question: which part can you now explain, and which part still needs a person to decide?

## Research and review boundary

High-aging claims requiring dated primary sources include Claude product behavior, the Messages API, MCP lifecycle details, and account entitlements. Mathematical examples require recalculation; code claims require inspection and actual tests. Companion-book empirical claims require their underlying sources rather than repetition of manuscript assertions. Do not turn a toy controller, permission check, fingerprint, or packet validator into a production security guarantee.

The structurally hardest chapters are 8 (protocol scope without overstating conformance), 9 (training without implying Claude fine-tuning), 12 (multi-agent coordination without invented dialogue), and 15 (substantive evidence without fictional stakeholder approval). Their worked examples must be resolved during Research before prose drafting.

After author review of these specifications, prepare the Blueprint risk assessment, then reconcile the final outline. Gate 0 remains open until the complete Blueprint is reviewed; research, prose drafting, images, and EPUB are later phases.
