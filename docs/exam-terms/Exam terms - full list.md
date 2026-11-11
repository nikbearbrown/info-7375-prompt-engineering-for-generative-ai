# Prompt engineering: exam terms, full list (core terms with definitions)

Every core term, grouped by theme, with the book's own sentence and its chapter and line, a plain definition, an example and a look-alike. Quotes are verbatim from the chapters.

# prompting (65)

**gate**  *(also: stop-condition contract)*
*prompting · core · chapters 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 · kind: pattern*

> The gate returns, this time as a stop-condition contract rather than an experiment. Before you ask Claude for any implementation, and before you run anything, write the following in your learner workspace. It is the part of this chapter no tool can write for you without defeating its purpose, and it is what you will hold Claude's controller against.
> — *the book, Ch 4 line 153*

In plain words: A written specification of the stop conditions made before any implementation: every exit, the unit of the budget, what must never be fabricated, and the separate check that decides whether a finished answer moves on. You then hold Claude's controller against it.

Example: The exit table, the contract, the outcome check, and the list of wrong versions.

**contract**  *(also: no fabricated answer)*
*prompting · core · chapters 1, 2, 4, 11 · kind: component*

> No exit fabricates an answer. A finish is a request to stop, and the result says only that one arrived. The configured budget and the status travel with the trace.
> — *the book, Ch 4 line 167*

In plain words: The rules fixed before the run: no exit invents an answer, a finish only means a request to stop arrived, and the budget and status are reported with the trace. A budget that is not a positive integer is rejected before the policy is touched.

**complete specification**  *(also: incomplete specification)*
*prompting · core · chapters 1, 2, 3, 10 · kind: concept*

> Claude implements well against a complete specification and badly against an incomplete one, and it will not tell you which kind you gave it. The decisions that determine whether a build goes well are made before the build: which problem, which boundary, which order, which evidence between steps, which point to stop.
> — *the book, Ch 10 line 10*

In plain words: Claude builds well from a thorough statement of the work and poorly from a thin one, and it will not warn you which you gave it. So the key decisions must be settled and written down before building.

**context**
*prompting · core · chapters 1, 9 · kind: component*

> Which documents, passages, or records are supplied this turn
> — *the book, Ch 9 line 34*

In plain words: Whatever documents, passages, or records are put into the model's input for this turn. The change lives in the corpus or store and in the step that selects from it.

Example: A new document added to a workspace.

Not to be confused with: weights (training)

**prompt**  *(also: prompting; instruction text and examples)*
*prompting · core · chapters 2, 9 · kind: component*

> If it was a prompt, it lives in a text file you can diff and copy into another project.
> — *the book, Ch 9 line 4*

In plain words: The instruction text and examples you give the model as input; it lives in a file or message you can compare, copy, and revert. Changing it changes what the model is given, not the model.

Example: Revising a system prompt can change behavior dramatically while the stored parameters stay untouched.

Not to be confused with: weights (training)

**system prompt**  *(also: preamble)*
*prompting · core · chapters 1, 5, 9 · kind: component*

> First, a system prompt is a request, not a gate. It is a paragraph near the top of a document, competing for influence with every other paragraph, including ones a user may paste in later. If a rule matters, enforcement belongs in the runtime that wraps the model, which is why Chapter 5 builds permissions in code and treats the preamble as a hope.
> — *the book, Ch 1 line 103*

In plain words: A paragraph near the top of the text the model continues, which asks for behavior but competes for influence with every other paragraph. It is a request, so it cannot enforce a rule.

Example: System: You are a careful assistant. Cite the provided source or say you do not know.

Not to be confused with: gate

**roles**  *(also: role markers; message role)*
*prompting · core · chapters 1 · kind: concept*

> The model's job is to continue that string, and the most plausible continuation of a string ending in Assistant: is an assistant-sounding reply. Roles are not modes the software switches into. They are text in a document that the machine is completing.
> — *the book, Ch 1 line 101*

In plain words: System, User and Assistant labels are just text inside the document the machine is completing, not modes the software switches into.

Example: A string ending in Assistant: is most plausibly continued by an assistant-sounding reply.

Not to be confused with: modes the software switches into

**give Claude the gate, not your implementation**
*prompting · core · chapters 4, 14 · kind: technique*

> Give Claude the gate, meaning the contract and your test list (including your two added tests), and not your implementation. Ask for an implementation that satisfies the contract and passes your tests, then run your tests on what it returns, yourself. A failing test is often a gap in your gate, which Claude cannot see because it has only what you wrote.
> — *the book, Ch 14 line 286*

In plain words: Give Claude the contract and your test list, not your own code, and then run your tests on what it returns. A failing test often shows a gap in your gate, because Claude sees only what you wrote.

**brief**  *(also: brief.md)*
*prompting · core · chapters 15 · kind: component*

> The `brief` states the need, consenting owner, affected people, success condition, non-purpose, and decision scope, and what would make the workflow inappropriate.
> — *the book, Ch 15 line 122; explained across several passages, no single defining sentence*

In plain words: The first artifact: it records the real need, the consenting owner, who is affected, what success looks like, what the workflow is not for, and when it would be inappropriate.

Example: A workflow that summarizes public course notes and does not evaluate students.

**refusals**  *(also: input checks; boundary checks)*
*prompting · core · chapters 1 · kind: pattern*

> A function is partly defined by what it refuses to compute. This is the first appearance of a pattern that recurs through the book: the refusals are where a human's decisions live, because Claude writes the happy path unprompted and the boundary only if your gate demands it.
> — *the book, Ch 1 line 299*

In plain words: Input checks that make a function reject invalid input instead of inventing a result. They are where a human's decisions live, because Claude writes the happy path unprompted and the boundary only if your gate demands it.

Example: Reject an empty list, a nonfinite score, and a temperature that is zero, negative, or nonfinite.

**reproduction**
*prompting · core · chapters 6 · kind: technique*

> The first useful artifact is a reproduction: the smallest legitimate case that shows the gap between intended and current behavior.
> — *the book, Ch 6 line 28*

In plain words: The smallest legitimate case that shows the gap between intended and current behavior, with a named input, expected result and observed result.

Example: Input 2 should give 3 but old returns 1; input 5 should give 6 but old returns 4.

Not to be confused with: proving the cause of the defect

**contract (part of the gate)**
*prompting · core · chapters 6, 15 · kind: technique*

> Contract. What the workflow must do. What it must refuse: to publish, to read outside the approved sources, to count a retrieved passage as support when it does not entail the claim.
> — *the book, Ch 15 line 140; explained across several passages, no single defining sentence*

In plain words: The part of the gate that says what the workflow must do and what it must refuse, plus the observable state that means done and the conditions that make the result unacceptable.

Example: Refuse to publish, to read outside the approved sources, and to count a passage as support when it does not entail the claim.

**persona**  *(also: You are an expert)*
*prompting · core · chapters 2 · kind: technique*

> A persona is a hypothesis to test. “You are an expert” is part of a prompt; it adds no supporting passage to the source collection and changes none of the validator's checks.
> — *the book, Ch 2 line 185*

In plain words: A role line such as 'You are an expert' is a part of the prompt to be tested, not a guarantee. It adds no support to the sources and does not change what the validator checks.

Example: You are an expert.

Not to be confused with: a role label that certifies the answer

**non-purpose**
*prompting · core · chapters 15 · kind: technique*

> Write a non-purpose. If the workflow summarizes public course notes, it does not evaluate students, ingest private submissions, or publish without review. Non-purposes give reviewers concrete misuse and scope-drift checks.
> — *the book, Ch 15 line 53*

In plain words: A written statement of what the workflow is not for. It gives reviewers a concrete way to spot misuse and scope drift.

Example: A workflow that summarizes public course notes does not evaluate students, ingest private submissions, or publish without review.

**output contract**  *(also: evidence intention)*
*prompting · core · chapters 2 · kind: concept*

> It states an output contract and an evidence intention. The executable function will enforce only part of that intention. It knows which identifiers are allowed; it does not understand whether the answer follows from their contents.
> — *the book, Ch 2 line 48*

In plain words: What the prompt says the answer must look like (here a JSON object with answer and sources), alongside the intention that the answer rest on the sources. The code enforces the format and the allowed identifiers but not the intention.

Example: answer must be a nonblank string; sources must be a nonempty list of identifiers from the supplied sources.

**exit table**
*prompting · core · chapters 4 · kind: component*

> The exits, as a table. These are my choices; no model produced them, and the reference happens to make the same ones. Mark every line with who decided it: you, the lesson's tests, or Claude.
> — *the book, Ch 4 line 155*

In plain words: A table written before any code listing each reason the run ends, with its status, its answer and its trace, and who decided each line. At this stage Claude has decided none of them.

Example: The policy has no next action: incomplete, answer none, trace every completed turn.

**a system prompt is a request, not a gate**  *(also: system prompt)*
*prompting · core · chapters 8 · kind: concept*

> In Chapter 1 you saw that a system prompt is a request, not a gate.
> — *the book, Ch 8 line 99*

In plain words: Text in a system prompt asks Claude to behave a certain way but does not force it, and tool descriptions in context work the same way.

Not to be confused with: runtime check

**role contract**  *(also: bounded role)*
*prompting · core · chapters 12 · kind: technique*

> Bound each role by inputs, outputs, tools, budget, and escalation. “Review the work” is not a role contract.
> — *the book, Ch 12 line 219*

In plain words: A written spec of what one worker may do, naming its inputs, task, tools, output, budget and where it escalates. A vague instruction like "review the work" does not bound a role, and role labels like researcher and reviewer do not make workers independent.

Example: Reviewer: inputs claims C1-C9 and passages P1-P4; read-only tools; verdict supported, unsupported or cannot tell; budget one pass; "cannot tell" goes to the coordinator.

Not to be confused with: role label

**few-shot examples**  *(also: prompt-context sensitivity; few-shot prompt)*
*prompting · core · chapters 9 · kind: technique*

> Few-shot examples are input too. They demonstrate a pattern inside the current context, so if you change an example and the answer changes, the evidence supports prompt-context sensitivity under the recorded interaction, not a claim that Claude was retrained.
> — *the book, Ch 9 line 40*

In plain words: Examples placed in the input that show the model a pattern for the current interaction. If changing an example changes the answer, that shows sensitivity to the prompt context, not that Claude was retrained.

Example: A few-shot prompt is one of the three conditions compared against a baseline prompt and a retrieved-context condition.

Not to be confused with: training

**acceptance statement**  *(also: requirement and boundary)*
*prompting · core · chapters 3 · kind: technique*

> For the folder task, write the acceptance statement with both a requirement and a boundary: inspect the specified source, return a source-grounded summary, and leave the source files unchanged. Reading is needed. Writing the originals is not.
> — *the book, Ch 3 line 38*

In plain words: A statement of what counts as done that says both what the system must do and what it must not touch. It makes the task specific enough that a helpful extra step is visibly out of bounds.

Example: Inspect the specified source, return a source-grounded summary, and leave the source files unchanged.

**state the rule in plain language**
*prompting · core · chapters 6 · kind: technique*

> For our constructed function, state the rule in plain language: return the input plus one. Choose at least two inputs before seeing a patch. With two and five, the expected results are three and six.
> — *the book, Ch 6 line 30*

In plain words: Write the intended behavior in plain words and pick at least two inputs with their expected outputs before you see any patch.

Example: Return the input plus one; inputs 2 and 5 should give 3 and 6.

**give Claude Code the gate**
*prompting · core · chapters 6 · kind: technique*

> In a disposable Python repository, put your gate where Claude Code can read it: the issue, the reproduction, the failing regression test, and the allowed-file list. Do not hand it your implementation. Then work in this order, and keep each artifact.
> — *the book, Ch 6 line 223*

In plain words: Put your issue, reproduction, failing regression test and allowed-file list where Claude Code can read them, and do not hand it your implementation. Then work in a fixed order, keeping each artifact.

**invalid requirement**
*prompting · core · chapters 6 · kind: failure mode*

> Plus one can be implemented perfectly and still be wrong, and testing cannot repair an invalid requirement. This is where the last line of the audit record earns its place: when the requirement is in doubt, reopen the gate instead of treating an exact implementation of the wrong rule as success.
> — *the book, Ch 6 line 261*

In plain words: Testing cannot repair an invalid requirement: a patch can implement the wrong rule perfectly and still be wrong. When the requirement is in doubt, reopen the gate.

Example: The diff is in scope and the tests pass, but the real task needed something else.

**contract for the state machine**
*prompting · core · chapters 8 · kind: technique*

> Tool operations are refused until initialize and then the initialized notification have both arrived, in that order. A notification never produces a response. Every response carries the id of the request it answers.
> — *the book, Ch 8 line 185*

In plain words: A short written spec of the rules the server must obey, which you give to Claude and use as the basis for your tests.

Example: A tool-level negative is a result with isError; a protocol-level problem is an error with a code.

**design by contract**
*prompting · core · chapters 10 · kind: concept*

> The appendix on The Pragmatic Conductor reaches the same idea through design by contract: you write the contract, the agent writes the implementation, and assertions or tests derived from your contract check it. A plan, in this chapter's sense, is that contract for a whole piece of work.
> — *the book, Ch 10 line 36*

In plain words: The human writes the contract, the agent writes the implementation, and assertions or tests derived from the contract check it. A plan is that contract for a whole piece of work.

**a field that has a job**  *(also: challengeable entry)*
*prompting · core · chapters 10 · kind: concept*

> Every entry in the third column would pass missing_fields. Every entry in the fourth is something a person can disagree with. That is the difference between a field that is present and a field that has a job.
> — *the book, Ch 10 line 91*

In plain words: A plan field is useful only if its entry is concrete enough that a person can disagree with it, such as an exact command or named file paths. Filler entries like Improve the code or Be careful merely fill the box.

Example: Verification: Review the result (fills the field) versus an exact command, an expected invariant, or a source comparison (has a job).

Not to be confused with: a field that is present

**facts are not instructions**
*prompting · core · chapters 12 · kind: technique*

> Facts are not instructions: render {"due_day": "Monday"} into context as a quoted claim with provenance, never into the system instruction channel.
> — *the book, Ch 12 line 289*

In plain words: Stored facts go into the model's context as quoted claims with their provenance, never into the channel that carries the system's instructions. This keeps data from being mistaken for a command.

Example: Render {"due_day": "Monday"} as a quoted claim with provenance.

Not to be confused with: instruction

**a prompt is a request, not a boundary**  *(also: prompt versus boundary)*
*prompting · core · chapters 15 · kind: concept*

> A prompt is a request, not a boundary. Telling Claude “do not publish” is useful task context, but the publication boundary is an application that lacks, or gates, that capability. A prompt-injected source should not be able to grant itself tools.
> — *the book, Ch 15 line 150*

In plain words: Telling Claude not to do something helps as context but does not stop it. A real boundary is the application lacking or gating the capability.

Example: Telling Claude “do not publish” versus an application that has no publish capability.

Not to be confused with: boundary

**recovery by repetition**
*prompting · core · chapters 15 · kind: failure mode*

> Recovery by repetition (check). The same prompt is rerun until a desired answer appears, with no reviewed change.
> — *the book, Ch 15 line 338*

In plain words: A failure of the check job: rerunning the same prompt until the wanted answer appears, with no reviewed change to the plan or mechanism.

Not to be confused with: reviewed recovery

**constrained output format**  *(also: shrink the distribution)*
*prompting · core · chapters 1 · kind: technique*

> Compare the spread against prompt 1's. A constrained format leaves fewer high-probability continuations to choose among, so the answers converge. It is the closest thing you have to lowering temperature without a temperature control, and it made the answer more repeatable and no more true.
> — *the book, Ch 1 line 388*

In plain words: Asking for a tightly constrained answer leaves fewer high-probability continuations, so repeated answers converge. It makes the answer more repeatable, not more true.

Example: Answer with one word only, no punctuation and no explanation. What is the capital of Australia?

Not to be confused with: lowering temperature

**ask for the boundary case, not the verdict**  *(also: Claude as a reviewer of your reasoning)*
*prompting · core · chapters 1 · kind: technique*

> Withholding the verdict is deliberate: you want the boundary case, not the grade. This is the use of Claude that sits comfortably inside your own thinking. It challenges; you decide.
> — *the book, Ch 1 line 408*

In plain words: After you have reasoned, ask Claude not whether you are right but for the one assumption your reasoning depends on most and an input that would make it fail. Claude challenges and you decide.

Example: Do not tell me whether I am right. Instead, name the single assumption my reasoning depends on most, and describe an input that would make it fail.

Not to be confused with: the grade

**request versus check**  *(also: a request is a hope, and a check is a gate)*
*prompting · core · chapters 2 · kind: concept*

> The request can be ignored or misunderstood; the local check has a definite acceptance rule. This is Chapter 1's point about the system prompt, one level up: a request is a hope, and a check is a gate.
> — *the book, Ch 2 line 36*

In plain words: Asking Claude in the prompt to follow a rule is only a request and can be ignored. Checking the returned answer with code is a gate with a definite accept or reject.

Example: 'Always obey the schema' in a prompt versus checking the schema after the response arrives.

**hand Claude the contract, not your implementation**  *(also: conduct Claude Code)*
*prompting · core · chapters 3 · kind: technique*

> In Claude Code, in your learner workspace, hand it the gate you wrote, the contract and the test list, and not your implementation. Ask for an implementation that satisfies the contract and passes your tests. Then run your tests on what it returns, yourself.
> — *the book, Ch 3 line 198*

In plain words: Give Claude Code your gate, contract and tests, ask for an implementation that meets them, and run the tests yourself. A failing test often marks a gap in your gate, because Claude only sees what you wrote.

**weak bug report**
*prompting · core · chapters 6 · kind: concept*

> A bug report such as "the result is wrong" is too weak to guide a bounded change. It names no input, expected result, observed result, or scope.
> — *the book, Ch 6 line 28*

In plain words: A bug report that says only 'the result is wrong' is too weak to guide a bounded change. A usable one names an input, the expected result, the observed result and the scope.

Example: Input 2, expected 3, observed 1, allowed files app.py and its test.

**Design (first part of the gate)**  *(also: Design)*
*prompting · core · chapters 6 · kind: component*

> The rule is: return the input plus one, for the declared integer examples. The reproduction inputs are two and five, with expected results three and six. The allowed files are app.py and its learner test file.
> — *the book, Ch 6 line 66*

In plain words: The first part of the gate: the rule, the reproduction inputs with expected results, and the allowed files, all chosen by you rather than by a model.

Example: Rule: input plus one; inputs 2 and 5; allowed files app.py and its learner test file.

**specification and audit**  *(also: the specification; the audit)*
*prompting · core · chapters 7 · kind: concept*

> What stays with you is the specification (what counts as similar, what is eligible, how many results) and the audit (what the ranking left out, and whether the winning passage says what the answer claims).
> — *the book, Ch 7 line 10*

In plain words: The two jobs that stay with the human in retrieval: stating exactly what counts as similar, what is eligible and how many results to return, and then auditing what was left out and whether the winning passage supports the claim.

Example: Specification: similarity = cosine of count vectors, k = 2. Audit: list every document with its score and fate.

**conduct Claude Code with the gate**
*prompting · core · chapters 8 · kind: technique*

> Open Claude Code in your learner workspace and give it the gate, meaning the transition table, the contract, and the test list, and not your implementation. Ask for a server that satisfies the contract and passes your tests. Then run your tests on what it returns, yourself.
> — *the book, Ch 8 line 209*

In plain words: Give Claude Code your table, contract and tests, but not your implementation, ask for a server that meets them, and run your own tests on the result.

Example: A failing test is often a gap in your gate, which Claude could not see because it had only what you wrote.

**state the rule before reading the code**
*prompting · core · chapters 8 · kind: technique*

> State the rule about order first, then check that the code enforces it. The other direction, reading the code and discovering the rule inside it, is how a rule you never chose becomes the rule you have.
> — *the book, Ch 8 line 34*

In plain words: Decide and write down the rule you want first, then check the code against it, instead of letting the code teach you what the rule is.

Example: Two behaviors were never chosen: a second initialize leaves ready true, and a tools/call with no id is dropped.

**a failing test is a gap in your gate**
*prompting · core · chapters 9 · kind: failure mode*

> A failing test is often a gap in your gate that Claude could not see because it had only what you wrote. If it adds early stopping you never asked for, your stop rule had a hole.
> — *the book, Ch 9 line 244*

In plain words: When Claude's code fails one of your tests, the gap is often in what you wrote, because Claude had only what you wrote. If it adds early stopping you never asked for, your stop rule had a hole.

Example: Claude adds early stopping you never asked for.

**specification that names the refusals**
*prompting · core · chapters 11 · kind: concept*

> The refusals are decisions about what the operation means, and they are yours: a specification that never mentions True gives an implementer, human or Claude, no reason to refuse it.
> — *the book, Ch 11 line 95*

In plain words: If a specification never mentions a case such as True, whoever implements it has no reason to refuse that case. So the refusals must be written into the specification, not assumed.

Example: A spec that never mentions True gives an implementer no reason to refuse it.

**a failed test as a gap in the gate**
*prompting · core · chapters 12 · kind: technique*

> First, note which tests failed; a failure is often a gap in your gate, which Claude could not see because it had only what you wrote.
> — *the book, Ch 12 line 330*

In plain words: When Claude's output fails one of your tests, the cause is often something missing from your gate, because Claude had only what you wrote. Treat the failure as a revision to the gate.

**operational control**
*prompting · core · chapters 12 · kind: concept*

> Each row needs a trigger, an owner, evidence, a response, and a recovery condition. “Monitor for stale memory” is not operational. “On a stale-version exception for a record used by an active task, pause dependent actions, preserve both proposals, notify the decision owner, and resume only after a reviewed version is committed” can be implemented and tested.
> — *the book, Ch 12 line 348*

In plain words: A control specific enough to implement and test, with a trigger, an owner, evidence, a response and a recovery condition. A vague instruction like "monitor for stale memory" does not qualify.

Example: On a stale-version exception for a record used by an active task, pause dependent actions, preserve both proposals, notify the decision owner, resume after a reviewed version is committed.

**action (proposal field)**
*prompting · core · chapters 13 · kind: component*

> action says what operation will occur. “Update” may still be too vague; “overwrite one local Markdown file” is more reviewable.
> — *the book, Ch 13 line 48*

In plain words: The proposal field that says what operation will occur, worded specifically enough to review. 'Overwrite one local Markdown file' is more reviewable than 'update'.

Example: "overwrite one local Markdown file" instead of "Update"

**challenger prompt**
*prompting · core · chapters 14 · kind: technique*

> Do not rewrite the entry. List (1) every field whose value names a group or a role rather than a person, (2) every threshold with no observable signal, (3) every mitigation that does not address the harm I named, and (4) one decision I have not written down.
> — *the book, Ch 14 line 292*

In plain words: A prompt that forbids rewriting and asks for four specific lists: fields naming a group or role instead of a person, thresholds with no observable signal, mitigations that do not address the named harm, and one decision not yet written down.

Example: Here is my register entry and the gate I wrote before drafting it.

Not to be confused with: asking Claude to rewrite the entry

**consumer**
*prompting · core · chapters 2 · kind: concept*

> The first decision is not what to say to Claude. It is what the program receiving Claude's answer needs, because that need is the only criterion that exists before an output does.
> — *the book, Ch 2 line 28; explained across several passages, no single defining sentence*

In plain words: The program that reads Claude's answer and does something with it; what it needs is the first thing you decide, before any prompt. You also note, for each contract line, who decided it: you or a fixed requirement of the consumer.

Example: A Python function that expects an object with an answer string and a sources list.

**task packet**  *(also: bounded task packet; source-grounded task packet; bounded Cowork task packet)*
*prompting · core · chapters 7 · kind: concept*

> The task packet should name the goal, permitted sources, output format, exclusions, and acceptance checks, and state how selected passages were obtained.
> — *the book, Ch 7 line 236; explained across several passages, no single defining sentence*

In plain words: The bounded brief you hand to Claude Cowork: what the goal is, which sources it may use, what output you want, what is excluded, how you will check it, and how the passages were chosen. Without the corpus and retrieval record it is hard to audit.

Example: A packet for answering office-hours questions from three permitted documents.

**baseline prompt**  *(also: baseline request)*
*prompting · core · chapters 2 · kind: component*

> Here is a baseline request derived from the contract. It is a proposal for an experiment, not a proven improvement:
> — *the book, Ch 2 line 38; explained across several passages, no single defining sentence*

In plain words: The starting prompt, derived from the contract, against which later revisions are compared. It is a proposal for an experiment, not a proven improvement.

Example: Return a JSON object with exactly two keys: answer and sources. Do not add text outside the JSON object.

**testable condition**  *(also: stranger test)*
*prompting · core · chapters 10 · kind: technique*

> Testable means someone who did not build the pipeline can read the condition, observe the system, and decide whether it holds. "Reviewed" and "reasonable" fail that test: five reviewers will do five different things and all call it reviewing. The procedure is plain: write the condition, circle every interpretive word, replace each with a criterion, then hand it to someone who did not write it and ask them to apply it to a sample case.
> — *the book, Ch 10 line 160; explained across several passages, no single defining sentence*

In plain words: A condition is testable when someone who did not build the pipeline can read it, observe the system and decide whether it holds. To get there, circle every interpretive word, replace it with a criterion, and have a stranger apply it to a sample case.

Example: Looks good is not a handoff condition; Reviewed and reasonable fail the test.

**source boundary**
*prompting · core · chapters 2 · kind: concept*

> Write the baseline, the source boundary, and the intended output contract.
> — *the book, Ch 2 line 177; explained across several passages, no single defining sentence*

In plain words: The limit that the answer must rest on the supplied source material only, which is stated in the prompt and recorded with the experiment.

Example: Answer the question using the supplied source material.

**few-shot revision**  *(also: revision with examples)*
*prompting · core · chapters 2 · kind: technique*

> The paired lesson asks you to compare a baseline prompt and a few-shot revision on five development questions while keeping five additional questions held out.
> — *the book, Ch 2 line 175; explained across several passages, no single defining sentence*

In plain words: A revised prompt that adds examples to the baseline, compared against the baseline on the same development questions. The chapter treats 'examples will help' as a hypothesis, not an established fact.

Example: Baseline prompt versus few-shot revision on five development questions, five held out.

**write the contract first**  *(also: order matters)*
*prompting · core · chapters 2 · kind: technique*

> If you write the prompt first and tune it until the output looks right, the contract becomes whatever the output happened to look like, and every later pass rate measures agreement with your own habituation. If you write the contract first, the criterion exists before the output does.
> — *the book, Ch 2 line 32; explained across several passages, no single defining sentence*

In plain words: Write down what the consuming program needs before you try a prompt, so the criterion exists before any output does. If you tune the prompt first, the contract just becomes whatever the output looked like.

Not to be confused with: tuning the prompt until the output looks right

**"fix this report" hides four requests**  *(also: kind of result you are asking for)*
*prompting · core · chapters 3 · kind: failure mode*

> Save a new version. Alter the original. Each has a different scope and a different consequence for state, and a system will pick one if you do not.
> — *the book, Ch 3 line 32; explained across several passages, no single defining sentence*

In plain words: A vague request like fix this report could mean explain what is wrong, propose a replacement, save a new version, or alter the original. If you do not say which, the system will choose one for you.

Example: Four readings: explain, propose, save a new version, alter the original.

**the contract for the code**  *(also: second half of the gate; contract and test list)*
*prompting · core · chapters 3 · kind: technique*

> Next, write the second half of the gate: the contract for the code, before anyone implements it. Mine has five claims.
> — *the book, Ch 3 line 192; explained across several passages, no single defining sentence*

In plain words: The contract is a short list of exact behaviors the code must have, written before anyone implements it. It also names the wrong versions the tests must catch.

Example: An unknown surface is refused; a write anywhere yields agent.

**connection gate**  *(also: the gate)*
*prompting · core · chapters 8 · kind: technique*

> This is the gate you first wrote in Chapter 1, now guarding a connection and not an experiment. It has two halves: the lifecycle as a state machine you predicted, and the four ledgers for the connection decision. Write both in your learner workspace before you read the reference and before you ask Claude for anything.
> — *the book, Ch 8 line 181; explained across several passages, no single defining sentence*

In plain words: A written plan you make before connecting a server: your predicted lifecycle table plus the four ledgers, with who decided each item. You hand it to Claude Code and run your own tests against what comes back.

Example: A transition table with your predictions entered before you looked at the answers, plus four ledgers for the read-only server and a hypothetical save_report server.

**write the gate before Claude implements it**  *(also: write the approval predicate before anything is approved)*
*prompting · core · chapters 13 · kind: technique*

> Write it in your learner workspace, in plain sentences and test names, before you ask Claude for any code. Name who decided each item. Where Claude proposed and you accepted, say so.
> — *the book, Ch 13 line 205; explained across several passages, no single defining sentence*

In plain words: Before asking Claude for any code, write the gate yourself in plain sentences and test names, saying who decided each item and where Claude proposed and you accepted. The owner, budget and identities that force a new decision are your judgments.

Example: The approval predicate for one consequential action, such as the report.md write.

**success as an observable state**  *(also: observable state that means done)*
*prompting · core · chapters 15 · kind: technique*

> Then define success as an observable state. “The agent completed the task” is narration. “The generated report contains the three required sections, every consequential claim maps to an approved source passage, the target file matches the reviewed diff, and publication remains pending” is inspectable.
> — *the book, Ch 15 line 53; explained across several passages, no single defining sentence*

In plain words: Define success as something you can look at and check in the resulting state, not as a statement that the agent finished. Also write the conditions that make the result unacceptable.

Example: The generated report contains the three required sections, every consequential claim maps to an approved source passage, the target file matches the reviewed diff, and publication remains pending.

Not to be confused with: “The agent completed the task” (narration)

**prompt revision as a hypothesis**  *(also: prompt revision)*
*prompting · core · chapters 2 · kind: technique*

> Then predict a specific failure the revision might address. Perhaps the baseline does not produce the required object shape, and you hypothesize that examples will help. That is a testable proposal, not a result because adding examples sounds like established practice.
> — *the book, Ch 2 line 177; explained across several passages, no single defining sentence*

In plain words: Treat a changed prompt as a testable guess: name the specific failure you expect the change to fix, then test it on a fixed evaluation set. It is not a result just because the change sounds like good practice.

Example: Hypothesis: the baseline does not produce the required object shape, and adding examples will help.

**the requirement comes first, from you**
*prompting · core · chapters 6 · kind: concept*

> The requirement was supposed to come first, and it was supposed to come from you.
> — *the book, Ch 6 line 8; explained across several passages, no single defining sentence*

In plain words: The rule the code must satisfy has to be written down first, by you, so a proposed implementation cannot redefine the problem you meant to solve. Claude can implement a wrong rule perfectly.

Example: State the rule as: return the input plus one.

**retriever contract**  *(also: contract)*
*prompting · core · chapters 7 · kind: concept*

> Cosine of count vectors is never negative; identical direction scores one whatever the lengths; an empty side scores 0.0, a convention and not a finding about the query. retrieve returns only positive scores, best first, equal scores in key order, at most k rows.
> — *the book, Ch 7 line 192; explained across several passages, no single defining sentence*

In plain words: The exact behaviors the retriever must have, written before it is built: score ranges, ordering, tie rules, the k limit, rejection of bad k, and an audit view. It is what you give Claude Code instead of your own implementation.

Example: retrieve returns only positive scores, best first, ties in key order, at most k rows.

**ask for discrepancies, not a verdict**  *(also: ask for leads and withhold the verdict)*
*prompting · core · chapters 8 · kind: technique*

> The second use is reading. Claude can take a whole transcript, the server source, and the advertised description, and compare them side by side without skipping the tedious message. Ask for leads and withhold the verdict:
> — *the book, Ch 8 line 215; explained across several passages, no single defining sentence*

In plain words: Prompt Claude to list every place where the transcript, source and description disagree, quoting the line it used, and tell it not to say whether to connect or call anything safe.

Example: Prompt: list every place where they disagree, quote the line you relied on, do not tell me whether to connect this server, and do not call any behavior safe.

**conduct Claude Code against your gate (Use It)**  *(also: Use It)*
*prompting · core · chapters 9 · kind: technique*

> Now hand Claude the work it is good at. Open Claude Code in your learner workspace and give it the gate you wrote, with the change, the objective, the held-out list, the stop rule, and your test list, but not your implementation.
> — *the book, Ch 9 line 242; explained across several passages, no single defining sentence*

In plain words: Give Claude Code your gate (the change, objective, held-out list, stop rule, and test list) but not your implementation, then run your own tests on what it returns.

Example: Ask for a train function and a held-out evaluation that satisfy the gate and pass your tests.

**three conditions (baseline, few-shot, retrieved context)**  *(also: baseline prompt; few-shot prompt; retrieved-context condition)*
*prompting · core · chapters 9 · kind: technique*

> Prepare a baseline prompt, a few-shot prompt, and a retrieved-context condition on the same bounded task, and change only one object between conditions. Write your prediction for each first. If you run them, record the actual responses, interface, date, and displayed model label; if you do not, label the design proposed.
> — *the book, Ch 9 line 246; explained across several passages, no single defining sentence*

In plain words: Compare a baseline prompt, a few-shot prompt, and a retrieved-context condition on the same bounded task, changing only one object between conditions, with a prediction written first. These conditions change inputs, not Claude's weights.

**plan-only request**
*prompting · core · chapters 10 · kind: technique*

> Then give Claude Code the bounded objective and the exclusions, and ask for a plan in the eight fields, saying explicitly that it should change no file yet. What returns is a proposal.
> — *the book, Ch 10 line 271; explained across several passages, no single defining sentence*

In plain words: To get a plan from Claude Code, give it the bounded objective and the exclusions, ask for the eight fields, and tell it explicitly to change no file yet. Treat what comes back as a proposal to review.

**resolved identity**  *(also: resolved target)*
*prompting · core · chapters 13 · kind: concept*

> Content binding is only as semantic as the proposal representation, and a high-stakes gate may bind resolved identifiers, immutable versions, or object hashes rather than friendly text alone.
> — *the book, Ch 13 line 175; explained across several passages, no single defining sentence*

In plain words: A concrete name for what an action touches (a resolved path, account, immutable version or object hash) instead of a friendly display name. A high-stakes gate may bind these rather than friendly text alone.

Example: Replacing a friendly target with a resolved identity in the six fields.

**Claude as challenger, not author**  *(also: use Claude as a challenger instead of an author)*
*prompting · core · chapters 14 · kind: technique*

> Withholding the rewrite is deliberate: you want the weak lines found, not smoothed. Verify each finding yourself against the entry; a finding you cannot locate in the text is a fluent guess.
> — *the book, Ch 14 line 298; explained across several passages, no single defining sentence*

In plain words: Instead of letting Claude rewrite your entry, ask it only to find the weak lines, and verify each finding yourself against the text. A finding you cannot locate in the text is a fluent guess.

# agents and the agent loop (142)

**drive**  *(also: driving)*
*agents and the agent loop · core · chapters 1, 3, 4, 5, 6, 8, 9, 10, 11, 14 · kind: concept*

> Drive. Who authorized the action, and what keeps that decision with a person? The split of labor is the driver's seat.
> — *the book, Ch 3 line 14*

In plain words: Keep the decision about who authorized an action with a person, and split the work between you and Claude on purpose.

**conduct**  *(also: conducting)*
*agents and the agent loop · core · chapters 1, 3, 5, 6, 8, 10, 11, 14 · kind: concept*

> Conduct. How much autonomy does this task need, and did I decide that before I granted anything? Writing that decision down is the gate.
> — *the book, Ch 3 line 12*

In plain words: Decide how much freedom the task needs before you give the system any ability, and write that decision down as the gate.

Example: Deciding that a folder summary needs read but not write.

**controller**  *(also: the loop; the next operation needs a controller)*
*agents and the agent loop · core · chapters 3, 4, 5, 11 · kind: concept*

> A set of tools is not a loop. Something must take the current state, select an action, execute it, observe the result, and decide whether to continue.
> — *the book, Ch 3 line 298*

In plain words: A controller takes the current state, picks an action, runs it, looks at the result and decides whether to keep going. Having tools is not the same as having a loop.

Example: Chapter 4 builds it in Python with a finite action budget.

Not to be confused with: a set of tools

**the driver's seat**  *(also: drive)*
*agents and the agent loop · core · chapters 2, 7, 8, 12, 15 · kind: framework*

> You drove: you gave Claude the coordination and the parallel work, and kept the initial judgment and the decision, because a stale-write error is a signal to reopen a human decision, not a prompt to retry.
> — *the book, Ch 12 line 428; explained across several passages, no single defining sentence*

In plain words: The division of work between you and Claude: Claude does the coordination, fast implementation and parallel work, while you keep the initial judgment and the decision. The chapter's table gives, for each task, what Claude should do, what you should do, and why it stays with you.

Example: Resolving a conflict between proposals: Claude lays out both and their evidence; you commit, reject with a reason, or leave it unresolved.

**trace**  *(also: agent trace)*
*agents and the agent loop · core · chapters 3, 4, 15 · kind: component*

> The state the controller builds is the trace: a list of records, each holding a turn number, an action name, and an observation.
> — *the book, Ch 4 line 32*

In plain words: The list the controller builds as it runs, with one record for each completed non-finish turn holding its turn number, action name and observation. It records events, not knowledge, and it leaves out the finish action and the lookup key.

Example: The lookup of color that returned blue is stored as one trace entry beside its turn number.

Not to be confused with: knowledge or evidence that the answer is right

**stop condition**  *(also: the stop condition)*
*agents and the agent loop · core · chapters 4, 6, 10, 15 · kind: component*

> The patch does not move downstream until the test was saved before the plan (a file timestamp or a commit will show it), the plan names only allowed files, and the test and existing suite have been run against the current diff, with commands and exit status recorded.
> — *the book, Ch 6 line 70*

In plain words: The condition the patch must meet before it moves downstream: the test saved before the plan, the plan naming only allowed files, and the test and existing suite run on the current diff with commands and exit status recorded.

Example: A file timestamp or a commit shows the test was saved before the plan.

**capability versus authority**  *(also: capability declaration)*
*agents and the agent loop · core · chapters 4, 8, 11, 15 · kind: concept*

> Chapter 3 drew the line between capability and authority, and Chapter 5 made the permission policy a design constraint you author. This chapter puts that line on a wire: the protocol carries the capability declaration, and the authority is written somewhere else, by someone, before the call.
> — *the book, Ch 8 line 30*

In plain words: What a server says it can do (capability) is separate from whether a task is allowed to use it (authority); the protocol carries the first and a person writes the second before the call.

Example: The listing declares a lookup capability; whether it may run is settled in your permission ledger.

**authorization**
*agents and the agent loop · core · chapters 3, 8, 13 · kind: concept*

> Authorization answers whether a particular capability should run in this task. A clean handshake settles the first question and is silent on the second.
> — *the book, Ch 8 line 4*

In plain words: The decision about whether a particular capability should be allowed to run for this task; the protocol syntax cannot make it for you.

Example: A read-only lookup and a file-writing lookup look the same on the wire, but they deserve different permissions.

Not to be confused with: interoperability

**action**  *(also: an action leaves a mark)*
*agents and the agent loop · core · chapters 3, 4 · kind: concept*

> Chapter 2 applied those jobs to an answer, with a contract written before the prompt and a pass that names what it passed. This chapter applies them to an action, which raises the stakes, because an action leaves a mark after the conversation ends.
> — *the book, Ch 3 line 10*

In plain words: An action is something the system does that outlasts the chat, such as changing a file. An answer is only a response you read, so actions raise the stakes.

Example: Saving an edited report to disk.

Not to be confused with: answer

**finished**
*agents and the agent loop · core · chapters 4, 11 · kind: concept*

> The word finished is also a choice. It names a controller state. Had the same state been called verified, downstream code would read the name and not the mechanism.
> — *the book, Ch 11 line 160*

In plain words: finished is the controller's exit status when the model's reply ends with end_turn before the request budget runs out. It says the loop saw a stop signal, not that the answer is right.

Example: A trace with status finished whose final sentence (99) disagrees with the tool result (42).

Not to be confused with: verified

**scope**
*agents and the agent loop · core · chapters 6, 10 · kind: component*

> What may change, and what must stay untouched?
> — *the book, Ch 10 line 84*

In plain words: The boundary of the work: what is allowed to change and what must be left alone.

Example: File paths, permitted operations, excluded systems, output destinations (not: Be careful).

**plan**  *(also: plan.md)*
*agents and the agent loop · core · chapters 10, 15 · kind: component*

> The `plan` lays out evidence-producing steps with dependencies, stop conditions, budgets, and replanning triggers.
> — *the book, Ch 15 line 122*

In plain words: The artifact that lays out the steps that produce evidence, with their dependencies, when to stop, spending limits, and what would force the plan to change.

Example: The plan invokes the gates.

**handoff condition**  *(also: pass condition)*
*agents and the agent loop · core · chapters 5, 8, 10 · kind: concept*

> The companion book on delegation makes one demand of any handoff condition: a person who did not build the pipeline can read it, observe the system, and tell whether it is met. "Looks good" is not a handoff condition.
> — *the book, Ch 8 line 193*

In plain words: A condition clear enough that a stranger can read it, observe the system and tell whether it is met.

Example: A stranger can mark every ledger line with an evidence type, finds no empty cell, and finds a re-review trigger beside the decision.

**agent**  *(also: agent surface)*
*agents and the agent loop · core · chapters 3, 4 · kind: concept*

> Then `write` takes precedence: if a write appears anywhere in the list, the result is `agent`.
> — *the book, Ch 3 line 133; explained across several passages, no single defining sentence*

In plain words: In this chapter, agent is the label for the surface that can reason, read and write, so it can change state. A trace gets the label as soon as a write appears anywhere in it; the label does not say who chooses the next step.

Example: ['reason', 'read', 'write'] is labeled agent.

Not to be confused with: a predefined workflow that writes; a model-directed process

**permission policy**  *(also: policy; the policy; design constraint)*
*agents and the agent loop · core · chapters 4, 5, 8 · kind: concept*

> The first decision is not a line of Python. It is what this tool may touch and what it may do, and you answer it by asking what the task requires, not what the tool is able to do.
> — *the book, Ch 5 line 28; explained across several passages, no single defining sentence*

In plain words: The written rules for what a tool may touch (the root) and what it may do (the allowed operations), decided from what the task needs before any code or grant exists. One root and two operations is small enough for a stranger to audit in minutes.

Example: Root: one disposable directory. Operations: read and write, no other operation, ever.

**capability**
*agents and the agent loop · core · chapters 3 · kind: concept*

> Capability is what the system may do, which is this chapter's sets.
> — *the book, Ch 3 line 113*

In plain words: Capability is what the system is able to do, as written in its capability set. It is separate from who chooses the next step and from how hard the output must be checked.

Not to be confused with: control; scrutiny; authorization

**observation**
*agents and the agent loop · core · chapters 4 · kind: component*

> If the records hold {"color": "blue"}, the observation is the string blue, and the trace stores it beside the turn number and action name. That is evidence of the local operation's result.
> — *the book, Ch 4 line 87*

In plain words: What the controller gets back from carrying out an action, such as the value a lookup found; it is stored in the trace. It is evidence of that one operation's result, not of anything outside the exercise or of private reasoning.

Example: A lookup of the key color against the records {"color": "blue"} gives the observation blue.

Not to be confused with: new evidence

**allowlist**
*agents and the agent loop · core · chapters 5, 11 · kind: component*

> An allowlist gives the application a closed set of operations. Exact argument rules narrow each operation further. Permissions can then be checked around the actual effect.
> — *the book, Ch 11 line 105*

In plain words: An allowlist is the fixed list of operations the application is willing to run. Anything the model proposes outside the list, or with arguments outside the rules, is refused.

Example: A one-tool allowlist containing only add.

**tool call**  *(also: proposal; tool request; proposed call)*
*agents and the agent loop · core · chapters 8, 11 · kind: concept*

> Claude produces a structured block that can be read as a proposal: call the tool named add with these arguments. The application decides what that name means, checks the arguments, executes its own implementation, and constructs the result message. The model does not reach through the message and touch a function.
> — *the book, Ch 11 line 76*

In plain words: A tool call is a structured block of data in which Claude names a tool and gives arguments; it is only a proposal. The application decides what the name means, checks it, and runs its own code.

Example: Call the tool named add with a = 17 and b = 25.

**AI should / Human should**  *(also: the driver's seat)*
*agents and the agent loop · core · chapters 9, 13, 14 · kind: framework*

> AI should prepare the six-field proposal, expose changed fields, assemble scoped evaluation evidence, identify missing information, and keep the action queued during review. For each pending proposal it can also state what a reviewer would need to know to notice a wrong evidence claim. It should stop at the authorization boundary: silence, timeout, model confidence, and a favorable automated score are not consent.
> — *the book, Ch 13 line 416; explained across several passages, no single defining sentence*

In plain words: A split of each task between Claude and a person (the chapter's driver's seat table): AI should prepare the proposal, expose changed fields, assemble evidence and stop at the authorization boundary. Human should inspect the exact proposal and evidence, decide within their authority (approve, refuse, defer or escalate), and keep a workload that permits judgment.

Example: Claude keeps the action queued during review; a person approves, refuses, defers or escalates.

**turn budget**  *(also: max_turns; request budget; budget-exhausted)*
*agents and the agent loop · core · chapters 4, 11 · kind: component*

> A turn budget prevents unbounded continuation. It does not guarantee progress, since four repeated calls can consume it without moving the task forward, and it does not certify safety, since an unauthorized operation could be damaging on the first turn.
> — *the book, Ch 11 line 158*

In plain words: A turn budget is a cap on how many times the loop may call the model (one through four here), so it cannot continue forever. It does not show that the task is progressing or that nothing unsafe happened.

Example: Four repeated calls can use up the budget without moving the task forward.

**autonomy**  *(also: capability, control, scrutiny)*
*agents and the agent loop · core · chapters 2, 3 · kind: framework*

> Three things hide inside the word autonomy, and the classifier measures only one.
> — *the book, Ch 3 line 113*

In plain words: Autonomy is not one thing; it hides capability, control and scrutiny. The classifier measures only capability, so a recommendation should keep a sentence for each.

**control**  *(also: the controller)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Control is who or what chooses the next operation.
> — *the book, Ch 3 line 113*

In plain words: Control is who or what picks the next step: a fixed program or the model itself. It is separate from capability, and Chapter 4 makes the controller explicit.

Example: A predefined program can write a file; a model-directed process can decide a lot without writing.

Not to be confused with: capability

**tool error**  *(also: is_error; represented tool error; returned tool error)*
*agents and the agent loop · core · chapters 8, 11 · kind: pattern*

> A rejected proposal is useful evidence for the next turn: the model can see that a particular request failed and why. The application does not pretend the tool ran, and it does not crash the whole conversation. Error becomes part of the protocol trace.
> — *the book, Ch 11 line 128*

In plain words: When a proposed call is invalid, the application returns a tool_result flagged is_error with the reason instead of crashing. The model can see what failed and why, and may try again.

Example: A Boolean argument for sum-1 comes back as a tool_result with is_error True.

**human in the loop**  *(also: human approval; supervisor)*
*agents and the agent loop · core · chapters 5, 14 · kind: concept*

> A human in the loop is also not automatically a control. The same companion chapter says that when checking is expensive, the cost structure pushes a supervisor toward accepting, and it calls that economics acting on attention, not a character flaw. I extend that to grants, as my reading and not the book's claim: if approval is requested for every small step, the answer can drift toward yes.
> — *the book, Ch 5 line 145*

In plain words: Having a person approve steps is not automatically a safeguard, because when checking is costly the supervisor drifts toward saying yes. The chapter's fix is to make approvals rare, specific, and tied to the actual change.

Example: If approval is requested for every small step, the answer can drift toward yes.

**terminal state is not correctness**  *(also: finish action; finished status; finite action budget)*
*agents and the agent loop · core · chapters 3, 4 · kind: failure mode*

> We give it a finite action budget and inspect a trace in which a finish action produces a finished status even when the final answer is wrong. The pattern should feel familiar by now: just as a capability label does not confer permission, a terminal state does not establish the correctness of the result that comes with it.
> — *the book, Ch 3 line 300*

In plain words: A loop can end with a finished status while the final answer is still wrong. Stopping tells you the controller stopped, not that the result is right.

Example: A finish action produces finished status even when the final answer is wrong.

Not to be confused with: capability label vs permission

**three jobs: conduct, check, drive**  *(also: conduct; check; drive)*
*agents and the agent loop · core · chapters 6, 15 · kind: framework*

> This chapter is where the book's three jobs arrive together: conduct (decide before Claude implements), check (find out what is wrong, and sign only what the record supports), and drive (keep the choices that are yours). Earlier chapters practiced them one artifact at a time.
> — *the book, Ch 15 line 11*

In plain words: Three things a person does when working with Claude: conduct (decide before Claude builds), check (find what is wrong and sign only what the record supports), and drive (keep the decisions that are yours). The capstone needs all three at once.

Example: Conduct lives in the six pre-build artifacts, check in evidence and audit-note, drive in the artifact's use and transfer-reflection.

**tool use**
*agents and the agent loop · core · chapters 11 · kind: concept*

> Tool use brings them together: a planned step becomes a model-proposed request, validation decides whether the application may dispatch it, execution produces an observation, and verification compares consequential claims with evidence outside the model's narration.
> — *the book, Ch 11 line 367*

In plain words: Tool use means the model proposes a request, your program checks it and runs it, and the result comes back as evidence. Claude then reports on that evidence, and a separate check tests the report.

Example: Claude proposes add(17, 25), the application runs the addition and returns 42.

**lookup**
*agents and the agent loop · core · chapters 4 · kind: component*

> lookup produces an observation from the records, or the string not found.
> — *the book, Ch 4 line 74; explained across several passages, no single defining sentence*

In plain words: One of the two permitted action names: it reads the value for a key from the records and returns it as the observation, or the string not found. It is the only operation the dispatcher actually runs.

Example: The action {"name": "lookup", "key": "color"}.

**policy**  *(also: scripted policy; action sequence)*
*agents and the agent loop · core · chapters 4 · kind: component*

> In this reference the first job is a policy: an iterable of action dictionaries. The controller creates an iterator and asks it for the next item on each turn, so a prepared list is enough. That is a deliberately limited use of the word.
> — *the book, Ch 4 line 30; explained across several passages, no single defining sentence*

In plain words: The part of the loop that proposes the next action; here it is just a prepared list of action dictionaries that the controller reads one at a time. It is not a learned model and does not change its next action based on what was observed.

Example: A policy of two actions: a lookup of color, then a finish with answer red.

Not to be confused with: a learned model

**turn**  *(also: iteration)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> Here we add sequence and termination. The questions are which action arrives next, what observation follows, what gets recorded, and which condition ends the run.
> — *the book, Ch 4 line 16; explained across several passages, no single defining sentence*

In plain words: One pass of the loop: the controller takes the next action from the policy, dispatches it, records the observation, and checks whether a condition ends the run. Each turn consumes exactly one action, and a finish counts as one.

Example: On turn one the lookup is dispatched, the observation is blue, and the trace gains an entry.

**state**  *(also: state update)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> The controller's state update is only the append. It does not alter the records or send observations back to the policy, so repeating a lookup against an unchanged mapping adds another observation of the same operation, not new evidence.
> — *the book, Ch 4 line 91; explained across several passages, no single defining sentence*

In plain words: What the loop carries from turn to turn; here it is just the trace, and each turn updates it only by appending a record. The records themselves are never changed.

**version**  *(also: version counter; local revision counter)*
*agents and the agent loop · core · chapters 12 · kind: component*

> version is a local revision counter;
> — *the book, Ch 12 line 54; explained across several passages, no single defining sentence*

In plain words: A number on each record that goes up by one each time a write is accepted, so it shows the order of commits for that key. It does not say when anything was observed.

Example: The first write to a new key returns version 1.

Not to be confused with: observation time

**stop reason**
*agents and the agent loop · core · chapters 4, 11 · kind: concept*

> Notice also that the trace is the same in both runs, one lookup entry. Trace length alone cannot reconstruct the stop reason, so the configured budget and the returned status are part of the evidence, not decoration.
> — *the book, Ch 4 line 119; explained across several passages, no single defining sentence*

In plain words: Why the run ended, which the returned status and the configured budget record and the trace length alone cannot show. They are part of the evidence.

Example: One lookup gives one trace entry under a budget of one (budget-exhausted) and a budget of four (incomplete).

**grant**  *(also: granting a capability)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Granting a capability is a decision, and writing the grant as a set makes it a decision you can inspect.
> — *the book, Ch 3 line 46*

In plain words: Giving the system an ability is a decision you make, and writing the grant down as a set lets you inspect it.

Example: Granted: reason, read (nothing wider).

**assistant**  *(also: assistant surface)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> A read-only source inspection requires `read`, not `write`. In this nested model, `assistant` covers that requirement without the extra write capability of `agent`.
> — *the book, Ch 3 line 89; explained across several passages, no single defining sentence*

In plain words: In the teaching model, assistant is the surface that can reason and read but cannot write. A trace with a read and no write is labeled assistant.

Example: ['reason', 'read', 'reason'] is labeled assistant.

Not to be confused with: chat; agent

**stale write**  *(also: Stale memory version; stale-version exception)*
*agents and the agent loop · core · chapters 12 · kind: failure mode*

> At commit time the current version is one. The comparison fails and Python raises ValueError("Stale memory version"). Worker B cannot silently overwrite A using an obsolete premise.
> — *the book, Ch 12 line 122*

In plain words: A write whose expected version no longer matches the record's current version is refused with an error and changes nothing, because the worker's premise is out of date. The refusal says nothing about which value is right.

Example: Write claim=blue, source s1, expected 1 when the record is already at version 2: rejected with Stale memory version.

**agent loop**  *(also: loop)*
*agents and the agent loop · core · chapters 4 · kind: pattern*

> Any agent loop contains three jobs that products blur into one experience. Something proposes the next action. Something dispatches it, records the result, and decides whether the run continues.
> — *the book, Ch 4 line 28*

In plain words: The cycle that drives an agent: something proposes the next action, something carries it out, records the result and decides whether to continue, and something decides whether the final result is any good. The chapter says chat windows blur these three jobs into one voice saying done, and that pulling them apart gives each one an owner.

Example: In the offline research run, an iterator supplies action dictionaries, a dispatcher handles a lookup, and a trace accumulates observations.

**reversibility**  *(also: state-changing edges; the trail)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> Here reversibility and the trail do most of the work. If the learner workspace is under version control, a new test can be reverted from the diff, so its edge needs evidence but not a human gate. A command that writes outside the fixture, or deletes, cannot be reverted from a diff, so it gets a hard human approval or it falls outside the scope.
> — *the book, Ch 10 line 166*

In plain words: Whether an action can be undone decides how much human approval it needs: an undoable change needs evidence only, while a write outside the fixture or a delete needs a hard human approval or is out of scope. Attach evidence to state-changing edges first.

Example: A new test in a version-controlled workspace can be reverted from the diff; a delete cannot.

**planning before acting**  *(also: design first; design first, then let Claude implement)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> Design first, then let Claude implement: that sentence is the discipline this chapter teaches. Planning exists to make proposed work inspectable before action. That means exposing the destination, allowed inputs and scope, intended steps, tools, risks, evidence, and stopping rule while change is still cheap.
> — *the book, Ch 10 line 34*

In plain words: Write down where the work is going, what it may use and touch, the steps, tools, risks, evidence and stopping rule before Claude acts, so others can inspect and challenge it while changes are cheap.

Example: A revision costs a paragraph before the run and a rollback after it.

**revision boundary**
*agents and the agent loop · core · chapters 12 · kind: concept*

> The revision boundary, the thing one version covers, is a choice you make before any worker runs, and it decides which conflicts the store can see.
> — *the book, Ch 12 line 92*

In plain words: The decision about what one version number covers, made before any worker runs. A version guards one key, so a decision that depends on several keys can be stale even when each key's version is current.

Example: If one decision reads three keys, three version numbers can each be current while the decision is stale.

**repetition detector**
*agents and the agent loop · core · chapters 4 · kind: technique*

> The turn budget limits completed iterations. It does not notice that two actions are the same or that two observations add nothing. The reference contains no repetition detector, which makes one a good learner extension: propose a rule that notices an unproductive cycle, then find a case where it would stop useful work.
> — *the book, Ch 4 line 137*

In plain words: A stop rule that notices an unproductive cycle of repeated actions or repeated observations. It needs a stated target failure and a test where it would wrongly stop useful work, and the budget stays a separate backstop.

Not to be confused with: turn budget

**action boundary**
*agents and the agent loop · core · chapters 2 · kind: concept*

> Suppose a later system can read files, write changes, or request a tool call. A correctly shaped answer now sits near an action boundary, and the distinction we practiced becomes more consequential: passing an output contract does not establish permission to perform the requested action.
> — *the book, Ch 2 line 316*

In plain words: The point where a correctly shaped answer could lead a system to read files, write changes or request a tool call. Passing an output contract does not give permission to act.

Not to be confused with: permission to perform the requested action

**incomplete**  *(also: policy exhaustion; policy silence)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> next(iterator) raises StopIteration when the policy has no next action. The controller returns incomplete with the trace so far. It does not read silence as completion: an exhausted supply of scripted actions is a different condition from an explicit finish.
> — *the book, Ch 4 line 72; explained across several passages, no single defining sentence*

In plain words: The status returned when the policy had no next action before the budget was spent. It does not mean the task is done or that it is impossible.

Example: A one-lookup policy with a budget of four: the second turn finds no action and returns incomplete.

Not to be confused with: budget-exhausted

**preflight**  *(also: preflight check; preflight function; preflight pathname check; displayed preflight)*
*agents and the agent loop · core · chapters 5 · kind: concept*

> The function checks a proposed operation under a supplied root and approval value. It does not perform the operation, and it does not authenticate where those inputs came from.
> — *the book, Ch 5 line 105; explained across several passages, no single defining sentence*

In plain words: A preflight is a check run before an action that decides whether a proposed action is allowed. It returns a decision (a path or an error) but does not carry out the read or write.

Example: authorize returns the resolved path for a contained read; no open, read_text or write_text appears in its lines.

Not to be confused with: a completed file operation; an operating-system sandbox

**bounded edit**
*agents and the agent loop · core · chapters 6 · kind: technique*

> Permit a bounded edit. Then, before running anything, read the diff and write the audit record. Only then run the targeted regression and existing tests on the current diff, preserving commands, outputs, and exit status.
> — *the book, Ch 6 line 227*

In plain words: Permit Claude a limited edit, then read the diff and write the audit record before running anything, then run the targeted regression and existing tests on the current diff, preserving commands, outputs and exit status.

**refusal path**  *(also: refusal paths)*
*agents and the agent loop · core · chapters 10 · kind: pattern*

> A plan written only for success pressures every observation into forward motion, so add refusal paths for missing authority, unavailable evidence, out-of-scope changes, and failed checks. Refusal here means the workflow preserves its state and reports what blocks the next transition.
> — *the book, Ch 10 line 178*

In plain words: A route written into the plan for when authority, evidence or checks are missing: the workflow keeps its state and reports what blocks the next step instead of pushing on.

Example: A resolved target outside the disposable parent is a hard stop; a failed existing test routes back to diagnosis.

**chain of custody**
*agents and the agent loop · core · chapters 11 · kind: concept*

> It is the chain of custody: a proposed request crosses a validation boundary, an application dispatches a named operation, execution produces evidence, a result is paired with a request, and a later claim is checked against something other than itself.
> — *the book, Ch 11 line 13*

In plain words: The chain of custody is the sequence a tool request goes through: validated, dispatched, executed, paired with its result, and finally checked as a claim. If any link is removed, a fluent summary can hide the gap.

**Claude coordinates**  *(also: coordinator)*
*agents and the agent loop · core · chapters 12 · kind: pattern*

> Claude coordinates: it routes tasks, compares artifacts, flags conflicts, keeps the original outputs, and summarizes disagreement without flattening it.
> — *the book, Ch 12 line 217*

In plain words: In the chapter's split of work, Claude's part is to route tasks, compare artifacts, flag conflicts, keep each worker's original output, and summarize disagreement without smoothing it away. Keeping the originals stops a synthesis from erasing disagreement.

Example: A coordinator compares artifacts and detects version conflicts between researcher and reviewer.

Not to be confused with: humans deliberate

**humans deliberate**
*agents and the agent loop · core · chapters 12 · kind: pattern*

> Humans deliberate: they hold the initial interpretation formed before the synthesis, bring local knowledge the shared notes never contained, weigh what a conflict means for the stakes, hear dissent, and decide.
> — *the book, Ch 12 line 217*

In plain words: In the chapter's split of work, the human's part is to hold an initial interpretation formed before the synthesis, add local knowledge the notes lack, weigh what a conflict means for the stakes, hear dissent, and decide. The decision has an owner whose name goes on it.

Example: A reviewer knows which section a date applies to, which the shared notes never recorded.

Not to be confused with: claude coordinates

**Claude proposes, Python constrains**
*agents and the agent loop · core · chapters 15 · kind: pattern*

> “Claude proposes, Python constrains” is a division of labor with a reason behind it. Claude does the language work: drafting, summarizing, proposing a tool call. Python holds whatever must be the same every time: which tools exist, whether an argument is valid, whether a path stays inside the approved root, whether a proposal matches the content a person approved, and what gets recorded.
> — *the book, Ch 15 line 150*

In plain words: Claude does the language work, such as drafting, summarizing and proposing a tool call. Python decides what must be the same every time: which tools exist, whether arguments and paths are valid, whether a proposal matches what a person approved, and what is recorded.

Example: Python checks whether a path stays inside the approved root before any action.

**chat**  *(also: chat surface)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Otherwise it is `chat`, which includes a list containing only `reason` and, by inspection, an empty list.
> — *the book, Ch 3 line 133; explained across several passages, no single defining sentence*

In plain words: In the teaching model, chat is the surface that can only reason, meaning produce a response, with no reading or writing. A trace with only reason events, or no events, is labeled chat.

Example: ['reason'] is labeled chat.

Not to be confused with: assistant

**sufficient autonomy**  *(also: smaller is not automatically better)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> If you widen the scope after seeing the work, rewrite the gate, date the new version, keep the old one, and authorize again. Design first does not mean freeze the design. Sufficient autonomy means matching the outcome, not minimizing the tool set whatever the work.
> — *the book, Ch 3 line 111*

In plain words: Choose the amount of autonomy that fits the outcome the task needs; a response-only interface cannot produce a saved file. If the scope grows, rewrite and date the gate, keep the old one, and authorize again.

Not to be confused with: minimizing the tool set whatever the work

**the model proposes; you authorize**  *(also: fluent permission request is not consent)*
*agents and the agent loop · core · chapters 3 · kind: pattern*

> A model can ask for permission fluently, and a fixture can supply an approval instantly. Neither is a person deciding. The model proposes; you authorize.
> — *the book, Ch 3 line 246*

In plain words: The model may propose an action and ask for permission, but only a person can authorize it. A fluent request or a fixture's instant approval is not a person deciding.

Not to be confused with: a simulated approval

**before the output moves on**
*agents and the agent loop · core · chapters 4 · kind: component*

> The answer leaves the controller only if the status is finished and that check passes. Any other status sends the status and the trace to a person, and nothing else. For a real task, a person also reads the trace before the answer is used.
> — *the book, Ch 4 line 171*

In plain words: The rule for when an answer may be passed on: only if the status is finished and the outcome check passes. Any other status sends the status and trace to a person, and for a real task a person also reads the trace.

**authorize**  *(also: authorize(root, target, operation, approved=False); reference implementation)*
*agents and the agent loop · core · chapters 5 · kind: component*

> The function is called authorize. What it does is resolve a name, compare two paths, and hand one back. The distance between those two descriptions is the subject here.
> — *the book, Ch 5 line 8; explained across several passages, no single defining sentence*

In plain words: The chapter's eleven-line Python function that decides whether a proposed read or write is allowed. Despite its name, it only resolves the path, runs three checks, and returns the path or raises PermissionError.

Example: Given the root /tmp/course and the target notes.txt it returns /private/tmp/course/notes.txt on macOS.

Not to be confused with: a complete approval system

**plan before any edit**
*agents and the agent loop · core · chapters 6 · kind: technique*

> Ask for a plan before any edit, and check it against the allowed list. A plan that names a file outside the list is a decision for you, not an assumption for Claude.
> — *the book, Ch 6 line 225*

In plain words: Ask Claude for a plan first and check it against the allowed list. A plan that names a file outside the list is a decision for you, not an assumption for Claude.

**discovery is not consent to call**  *(also: discovery)*
*agents and the agent loop · core · chapters 8 · kind: concept*

> Discovery is not consent to call. A host can learn which tools exist and still deny them under its permission policy. A read-only tool may suit public course fixtures and not restricted material.
> — *the book, Ch 8 line 103*

In plain words: Seeing a tool in the listing does not mean it is allowed to run; the host's permission policy decides.

**capability does not create authority**
*agents and the agent loop · core · chapters 10 · kind: concept*

> Every step needs information it is authorized to use. If no step writes, a write-capable tool is unnecessary; if a step needs a capability the tools field lacks, the plan is infeasible. An available tool can still be forbidden for this task: capability does not create authority.
> — *the book, Ch 10 line 191*

In plain words: Having a tool that can do something does not mean this task may use it. Each step must be checked against the information and tools it is authorized to use.

**one step at a time**  *(also: hold it to the plan)*
*agents and the agent loop · core · chapters 10 · kind: technique*

> Third, only after the gate passes, let Claude Code act on the approved version one step at a time, and hold it to the plan. The stop conditions are now what you check its diff and commands against; if a halt condition fires, the plan stops there and the record says so.
> — *the book, Ch 10 line 275*

In plain words: Only after the gate passes, let Claude Code act on the approved plan one step at a time, checking its diff and commands against the stop conditions. If a halt condition fires, work stops there and the record says so.

**optimistic concurrency control**  *(also: optimistic concurrency; expected-version check)*
*agents and the agent loop · core · chapters 12 · kind: technique*

> This is optimistic concurrency control in miniature. A worker reads a version and does its work on the optimistic assumption that the record will not change. At commit time, it supplies the version it read.
> — *the book, Ch 12 line 88*

In plain words: Workers read a record and its version, do their work without locking the record, and at write time must hand back the version they read; if the record has changed, the write is refused.

Example: Worker B writes with expected=0 after Worker A has moved the key to version 1, and the store raises Stale memory version.

**cascade**
*agents and the agent loop · core · chapters 12 · kind: failure mode*

> The first is a cascade. One worker's output is wrong with some small probability, a second conditions on it, a third on the second, and by the end the system's error is governed by how errors compound across the chain. Checking each worker in isolation tells you little about that.
> — *the book, Ch 12 line 187*

In plain words: A multi-worker failure pattern in which each worker builds on the previous worker's output, so small error chances compound across the chain. Checking each worker alone does not reveal it.

Example: One worker's output is wrong, a second conditions on it, a third on the second.

Not to be confused with: authority laundering

**authority laundering**
*agents and the agent loop · core · chapters 12 · kind: failure mode*

> The second is authority laundering. A worker passes data to another as a legitimate output; the receiver cannot verify where it came from, so the data takes on the standing of the channel it arrived through. Limiting what a single worker may access does not prevent this.
> — *the book, Ch 12 line 187*

In plain words: A failure pattern in which data passed from one worker to another is treated as legitimate just because of the channel it arrived through, since the receiver cannot verify its origin. Tracking provenance across workers addresses it; limiting one worker's access does not.

Example: One worker writes a claim, another summarizes it, a third cites the summary.

Not to be confused with: cascade

**incident state machine**  *(also: active, challenged, paused, reviewed, superseded, resumed)*
*agents and the agent loop · core · chapters 12 · kind: pattern*

> The coordinator needs states richer than “success” and “failure.” A useful incident machine might include active, challenged, paused, reviewed, superseded, and resumed. The researcher's evidence moves the assumption to challenged.
> — *the book, Ch 12 line 247*

In plain words: A set of states the coordinator tracks for an incident, richer than success and failure: active, challenged, paused, reviewed, superseded, and resumed. New evidence moves an assumption to challenged, dependent tasks pause, a named human reviews, the old record is superseded, and work resumes only after regeneration.

Example: Evidence of a Monday date challenges version 3; tasks depending on the closing date pause; after review the record is superseded and work resumes.

**pause-and-resume harness**
*agents and the agent loop · core · chapters 12 · kind: component*

> Ask for a Memory that satisfies the contract and passes your tests, and for a small pause-and-resume harness: when a stale exception hits a key an active task depends on, the task pauses, both proposals are preserved, and nothing resumes until a reviewed version is committed and the task rereads it.
> — *the book, Ch 12 line 328*

In plain words: A small piece of code that, on a stale exception for a key an active task depends on, pauses the task and keeps both proposals. Nothing resumes until a reviewed version is committed and the task rereads it.

Example: A stale exception hits a key an active task depends on, so the task pauses.

**control plane**
*agents and the agent loop · core · chapters 14 · kind: concept*

> The register is also a control plane. It draws on every previous layer: tool permissions define action authority, memory records data lineage and lifetime, evaluations describe observed behavior and exclusions, and approval gates bind decisions to exact proposals. A register that can pause execution, revoke approval, shorten retention, change evaluation, assign repair, or end the project is governance.
> — *the book, Ch 14 line 308*

In plain words: The register is a control plane when it can actually pause execution, revoke approval, shorten retention, change evaluation, assign repair or end the project. It draws on tool permissions, memory, evaluations and approval gates; if updating it changes nothing the system does, it is only documentation.

**inspect resulting state, not only trajectory**  *(also: outcome state)*
*agents and the agent loop · core · chapters 15 · kind: concept*

> Inspect resulting state, not only trajectory. An agent can execute the planned calls while the destination remains wrong. A file write can succeed locally without being committed or published.
> — *the book, Ch 15 line 215*

In plain words: Check what actually ended up true in the world, not just the sequence of steps taken. An agent can run every planned call and still leave the destination wrong.

Example: A file write can succeed locally without being committed or published.

Not to be confused with: trajectory

**authority drift**
*agents and the agent loop · core · chapters 15 · kind: failure mode*

> Authority drift (conduct). A local-write approval is described as permission to publish.
> — *the book, Ch 15 line 342*

In plain words: A failure of the conduct job: approval for a small, local action is later described as permission for a bigger one, such as publishing.

Example: A local-write approval described as permission to publish.

Not to be confused with: capability versus authority

**good result vs authorized action**
*agents and the agent loop · core · chapters 3 · kind: failure mode*

> The ability arrived with the interface. A good result and an authorized action are different judgments, and in this story only the first was ever made.
> — *the book, Ch 3 line 6*

In plain words: Even when an action turns out well, someone still has to decide that the system was allowed to do it. In the folder story, nobody decided the system could write.

Example: A summary task where the system also saves a cleaned-up version over the original.

Not to be confused with: a good result

**what could, what allowed, what did (the chapter's three questions)**  *(also: the question this chapter makes inspectable)*
*agents and the agent loop · core · chapters 3 · kind: framework*

> I use them because they expose the question this chapter makes inspectable. What could the system do, what did you let it do, and what evidence says what it did? A product name answers none of those.
> — *the book, Ch 3 line 8*

In plain words: Ask three things of any AI system: what it was able to do, what you actually let it do, and what the record shows it did. A product name or a final message that says done answers none of them.

Not to be confused with: the product name or label

**missing set (R minus C)**  *(also: M; required capabilities; declared capabilities)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Let R be the set of capabilities a task requires, and let C be the set declared for a surface. The missing set is R minus C, the requirements that do not appear in the surface
> — *the book, Ch 3 line 58*

In plain words: The missing set is what a task requires that a surface does not declare. Subtract the surface's capabilities from the task's required capabilities.

Example: A task needing read and write: chat is missing read, write; assistant is missing write; agent is missing none.

**proposed, attempted, completed, observed**  *(also: four verbs)*
*agents and the agent loop · core · chapters 3 · kind: framework*

> Inside a trace, keep four verbs apart. A write can be proposed, when a response offers it; attempted, when the operation was requested of the runtime; completed, when the runtime reported success; and observed, when you saw the changed state. A report should say which verb its evidence supports.
> — *the book, Ch 3 line 148*

In plain words: Four stages for a write: offered by the response, requested of the runtime, reported successful by the runtime, and seen by you in the changed state. A report should say which stage its evidence supports.

**control-flow layer versus evidence layer**  *(also: controller status versus outcome evaluation; two-part report)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> The repair is not to rename every termination status failure, which would throw away distinctions the controller reports correctly. Separate controller status from outcome evaluation. A result can be finished at the control-flow layer and contradicted at the evidence layer, and that two-part report says more than an unqualified success or an undifferentiated failure.
> — *the book, Ch 4 line 103*

In plain words: A run can be finished at the control-flow layer, meaning the controller returned, and still be contradicted at the evidence layer, meaning the answer disagrees with the records. Report both parts instead of one success or failure label.

Example: finish(red) after a lookup that observed blue: finished at the control-flow layer, contradicted at the evidence layer.

Not to be confused with: renaming the status failure

**budget chosen before the run**
*agents and the agent loop · core · chapters 4 · kind: pattern*

> A limit chosen before the run is a property of the controller. A limit discovered afterward is an incident report.
> — *the book, Ch 4 line 115*

In plain words: A limit decided and written down before the loop starts is built into the controller, while a limit found only after something went wrong is just an incident. The stop was designed, not discovered.

Example: Someone chose the number two before the loop ran.

**feedback from observation to policy**  *(also: adaptive system)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> The list is not a learned model, and it does not change its next action based on what the controller observed, because nothing feeds the observation back. A more adaptive system would need a defined route from observations to its next decision. Do not describe that route as implemented merely because the code uses the name policy.
> — *the book, Ch 4 line 30*

In plain words: In this reference the policy never sees what the controller observed, so its next action cannot depend on it. A more adaptive system would need a defined route sending observations back to the next decision.

**policy in the request versus policy in a function**  *(also: two places to put a policy)*
*agents and the agent loop · core · chapters 5 · kind: pattern*

> There are two places to put such a policy. One is a sentence in the request: stay inside the course folder, do not overwrite anything. The other is a function between the request and the filesystem that raises when the request is out of bounds.
> — *the book, Ch 5 line 32*

In plain words: A rule can be stated as a sentence in the prompt, or enforced as code that sits between the request and the filesystem and refuses out-of-bounds requests. Only the code version does not depend on how persuasive the request is.

Example: Request sentence: stay inside the course folder. Code: a function that raises PermissionError.

Not to be confused with: system prompt

**the scope decision stays with the task owner**
*agents and the agent loop · core · chapters 6 · kind: concept*

> Claude can tell you which files it believes it must touch and why, and the reason may be good. What it has no access to is the rest of your situation: who else depends on that configuration file, what is in flight on another branch, whose name is on the release. Whether the task should grow to include a new file is a decision about what the change is for, and it stays with the person who owns the task.
> — *the book, Ch 6 line 138*

In plain words: Claude can say which files it thinks it must touch and why, but whether the task should grow to include a new file depends on context only the owner has, such as who else depends on the file and what is in flight on another branch.

Example: A configuration file others depend on.

**stop rule for a fluent guess**  *(also: missing record continuation)*
*agents and the agent loop · core · chapters 8 · kind: technique*

> In Chapter 1's terms, nothing in the loop that produces Claude's next token stops a fluent guess at an office number. The stop has to be a rule you wrote into the host or the instruction, and a check you run on the answer afterward.
> — *the book, Ch 8 line 177*

In plain words: Nothing in how Claude produces its next word stops it from guessing when a record is missing, so you must write a stop rule into the host or the instruction and check the answer afterward. The right continuation is to report the absence and decide whether to ask another authorized source.

Example: When lookup returns Record not found, the answer should say the record is missing, not invent an office number.

**exit owner**
*agents and the agent loop · core · chapters 10 · kind: concept*

> Each exit needs an owner. An automated test can halt on a failing assertion. A person must decide whether a newly discovered risk changes scope.
> — *the book, Ch 10 line 176*

In plain words: Every exit from the work needs someone responsible for it: a test can halt on a failing assertion, but a person must decide whether a new risk changes scope. Claude's good summary of the evidence is not a decision with a name on it.

**no identical retry**  *(also: activity versus progress)*
*agents and the agent loop · core · chapters 10 · kind: pattern*

> If the same check fails with no new evidence, the next step is not an identical retry: route to diagnosis, revise the plan, or defer. Activity becomes progress only when it changes the evidence or the decision state.
> — *the book, Ch 10 line 180*

In plain words: If a check fails again and nothing new has been learned, do not just run it again: diagnose, revise the plan, or defer. Work counts as progress only when it changes the evidence or the decision state.

**Claude proposes, your Python executes**  *(also: division of labor)*
*agents and the agent loop · core · chapters 11 · kind: pattern*

> So the division here is deliberate: Claude proposes the call and interprets the trace, and your Python owns exact argument validation and arithmetic.
> — *the book, Ch 11 line 52*

In plain words: Claude suggests the call and explains the trace, while your own code does the exact checking and the arithmetic. The number then comes from an operation you can read, re-run and test.

Example: Claude proposes add(17, 25); the dispatcher returns 42.

**tool_use exit**  *(also: extending the outgoing history)*
*agents and the agent loop · core · chapters 11 · kind: pattern*

> If it is tool_use, build results, append assistant content followed by a user message containing those results, then continue, unless the turn budget is exhausted.
> — *the book, Ch 11 line 154*

In plain words: When the reply asks for a tool, the loop builds the results, adds the assistant's content and then a user-role message holding the results to the history, and calls the model again. The next call sees both its own requests and the application's responses.

Example: Assistant content with the add request, then a user message with the tool_result for sum-1.

**inherited mistakes in shared memory**
*agents and the agent loop · core · chapters 12 · kind: concept*

> Once an observation becomes memory, later work inherits it, mistakes included, and this is where Claude's strength turns into the hazard. Claude sessions work in parallel and at a volume no team of people matches, so one unchecked note can be read, summarized, cited, and acted on by several workers before anyone looks at it.
> — *the book, Ch 12 line 11*

In plain words: When an observation is stored as memory, every later piece of work that reads it inherits it along with any error. Because Claude sessions run in parallel and at volume, one unchecked note can spread through several workers quickly.

Example: One unchecked note read, summarized, cited, and acted on by several workers before anyone looks at it.

**memory (stored state, not recollection)**  *(also: record store; shared memory; memory record)*
*agents and the agent loop · core · chapters 12 · kind: concept*

> There is no semantic recall, embedding search, or learned representation here. A key indexes a Python dictionary. Claude remembers nothing through this class; a model that uses it receives whatever text your application puts into its context.
> — *the book, Ch 12 line 42*

In plain words: In this chapter, memory is a store of records kept in a Python dictionary under keys, outside the model. Claude remembers nothing through it; the model only sees what your application chooses to put in its context.

Example: class Memory with self.records = {} and self.lock = Lock().

Not to be confused with: model recollection

**multiple Claude sessions as parallel workers**  *(also: multiple workers; bounded workload)*
*agents and the agent loop · core · chapters 12 · kind: pattern*

> Multiple Claude sessions can split a bounded workload: one extracts source passages while another tries boundary cases, and a coordinator compares artifacts and detects version conflicts. That is real work, done in more parallel threads than you can match.
> — *the book, Ch 12 line 211*

In plain words: Several Claude sessions each take a bounded part of a job, for example one extracting source passages and another trying boundary cases, while a coordinator compares their artifacts and detects version conflicts. This gives parallel work but not independent judgment.

Example: A researcher session and a reviewer session on sanitized fixtures, with a coordinator.

Not to be confused with: independent judgment

**responsibility must remain with a person or organization**  *(also: an automated system can stop work safely)*
*agents and the agent loop · core · chapters 14 · kind: concept*

> An automated system can stop work safely, but responsibility must remain with an authorized person or organization.
> — *the book, Ch 14 line 262*

In plain words: An automated system can stop work safely, but responsibility for the outcome must stay with an authorized person or organization. An agent cannot take that responsibility by naming itself.

**teaching surface**  *(also: surface; capability handles)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> The labels `chat`, `assistant`, and `agent` belong to this exercise. They are not a verified map of current product features, and they do not claim that every system bearing one of those names has the same permissions or architecture.
> — *the book, Ch 3 line 16; explained across several passages, no single defining sentence*

In plain words: A teaching surface is one of three imaginary interface types (chat, assistant, agent), each defined by an explicit set of capabilities. They are handles for inspecting an operation, not claims about real products.

Example: chat = reason; assistant = reason, read; agent = reason, read, write.

Not to be confused with: a real product's feature list

**reason, read, write**  *(also: the three capabilities; source access (read); mutation (write))*
*agents and the agent loop · core · chapters 3 · kind: concept*

> The strings are categories within the teaching model. `reason` stands for response-level processing, `read` for access to information through the modeled reading capability, and `write` for a modeled ability to change state. Inserting a string into a set creates no access; the program stores a declared description that later functions compare.
> — *the book, Ch 3 line 56; explained across several passages, no single defining sentence*

In plain words: The three modeled capabilities: reason is producing a response, read is accessing information, and write is changing state. Putting a string in a set grants nothing real; it only records a description.

Example: A write changes a stored artifact, which is a mutation.

**error observation**  *(also: error: tool not allowed; unknown action name)*
*agents and the agent loop · core · chapters 4 · kind: component*

> Any other name becomes the observation error: tool not allowed, appended to the trace, and the loop continues if a turn remains. A name like shell is never dispatched, and a lesson test checks for the not-allowed message.
> — *the book, Ch 4 line 74; explained across several passages, no single defining sentence*

In plain words: What the controller records when an action's name is neither lookup nor finish: nothing is run, the error is appended to the trace, the turn is consumed, and the run continues if a turn remains. It does not establish permissions for any larger runtime.

Example: An action named shell.

Not to be confused with: stopping, retrying, or escalating

**reviewed recovery**
*agents and the agent loop · core · chapters 15 · kind: technique*

> Recovery is not “ask Claude again until it passes.” A human or declared policy reviews why the case failed. The plan may narrow the claim, select a different approved source, add an abstention rule, or defer.
> — *the book, Ch 15 line 172; explained across several passages, no single defining sentence*

In plain words: After a failure, a person or a declared policy reviews why it failed and changes the plan, for example by narrowing the claim, choosing another source, adding an abstention rule or deferring. The changed proposal goes back through its gate and is compared with the original failure.

Example: Narrow the claim or select a different approved source.

Not to be confused with: recovery by repetition

**capability set**  *(also: declared capabilities; SURFACES)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Capability sets describe what a surface is declared able to do. Event traces describe what is recorded as having happened.
> — *the book, Ch 3 line 121; explained across several passages, no single defining sentence*

In plain words: A capability set lists what a surface is declared able to do. It describes what is available, not what happened in any particular run.

Example: agent: {reason, read, write}.

Not to be confused with: event trace

**allowed-file list**  *(also: allowed files; allowed list)*
*agents and the agent loop · core · chapters 6 · kind: component*

> Do not respond to this limitation by making the allowed list the whole repository; that erases the boundary the check was meant to enforce. If the patch reveals a legitimate dependency outside the initial scope, pause and revise the scope explicitly.
> — *the book, Ch 6 line 134; explained across several passages, no single defining sentence*

In plain words: The list of files the patch may change. Do not make it the whole repository, because that erases the boundary; if a real dependency appears outside it, pause and revise the scope explicitly.

Example: app.py and its learner test file.

**unit of the budget**
*agents and the agent loop · core · chapters 4 · kind: concept*

> This is a decision about the unit. The name turn budget counts action-consumption turns, and the terminal action costs one. If you meant tool calls, you need a different implementation and different tests.
> — *the book, Ch 4 line 121; explained across several passages, no single defining sentence*

In plain words: What one count of the budget stands for, which a person writes down before the run. Here it is a turn that consumes one action from the policy, so the finish also costs one.

Example: A lookup followed by a finish cannot finish through that finish if the budget allows only the first turn.

Not to be confused with: tool calls

**dependency graph**  *(also: directed dependency graph; directed obligations; after)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> Steps are not a list. They are a graph, and each arrow is an obligation. If step verify has after: [build], then build must appear before verify: verify may not be called ready until build has produced what verify needs.
> — *the book, Ch 10 line 118; explained across several passages, no single defining sentence*

In plain words: Treat a plan's steps as a graph in which an arrow from one step to another means the second may not be called ready until the first has produced what it needs. You decide which arrows exist; the function can only order the ones you declared.

Example: verify has after: [build], so build must come before verify.

Not to be confused with: a list of steps

**action-surface-map**  *(also: action map)*
*agents and the agent loop · core · chapters 15 · kind: component*

> The `action-surface-map` shows what the workflow can read, propose, write, send, or publish, separating capability from authority and flagging external or irreversible effects.
> — *the book, Ch 15 line 122; explained across several passages, no single defining sentence*

In plain words: The artifact that lists what the workflow is able to read, propose, write, send or publish, and keeps what it can do separate from what it is allowed to do. It flags effects that reach outside or cannot be undone.

Example: The data boundary constrains the action map.

**the condition that sends control back to you**  *(also: Back to me if)*
*agents and the agent loop · core · chapters 3 · kind: technique*

> You should be able to write the gate before any grant is made: the smallest capability set that finishes the task, the operation and target that are authorized, and the condition that sends control back to you.
> — *the book, Ch 3 line 22; explained across several passages, no single defining sentence*

In plain words: A line in the gate that names when the system must stop and hand the decision back to you. It is how a person stays in charge of what the system does next.

Example: Back to me if the system proposes saving anything, touching a second file, or changing the request.

**the stop that ends the run**
*agents and the agent loop · core · chapters 4 · kind: concept*

> Two different stops hide under the word done. One ends the run: the controller returns.
> — *the book, Ch 4 line 38; explained across several passages, no single defining sentence*

In plain words: The controller returning from the loop, whether because a finish arrived, the policy ran out, or the budget was spent. Claude may request this stop and the controller can take it.

Example: Claude reports that it is done.

Not to be confused with: the stop that closes the task

**the stop that closes the task**
*agents and the agent loop · core · chapters 4 · kind: concept*

> The other closes the task: a person, or a check a person designed, accepts the result as meeting the need that started the run. The controller can take the first stop. Nothing in this function can take the second, and the rest of the chapter is about keeping the two from being confused.
> — *the book, Ch 4 line 38; explained across several passages, no single defining sentence*

In plain words: A person, or a check a person designed, accepting the result as meeting the need that started the run. Only the human takes this stop, by accepting, narrowing or withholding and signing.

Example: Accept, narrow, or withhold, and sign.

Not to be confused with: the stop that ends the run

**model-backed policy**  *(also: model-backed decision source; live model call)*
*agents and the agent loop · core · chapters 4 · kind: component*

> A model-backed policy would be a new source of action requests, and it should not inherit the power to redefine the runtime's limits just because it supplies the next action.
> — *the book, Ch 4 line 34; explained across several passages, no single defining sentence*

In plain words: A policy whose next actions come from a model instead of a prepared list. It only supplies action requests, while the controller limits and evidence checks stay explicit outside it.

Not to be confused with: scripted policy

**bounded loop**
*agents and the agent loop · core · chapters 4 · kind: concept*

> Here the configured limit bounds ordinary completed turns in the demonstrated loop; it is not a general timeout, a memory cap, a credential policy, or a correctness check.
> — *the book, Ch 4 line 251; explained across several passages, no single defining sentence*

In plain words: Any claim that a loop is bounded must name its unit and assumptions. Here the budget bounds ordinary completed turns and nothing else.

Not to be confused with: timeout

**topological ordering**  *(also: order function; ordering of named dependencies)*
*agents and the agent loop · core · chapters 10 · kind: technique*

> The ordering loop finds all entries whose prerequisite sets are empty. These are the ready steps. It sorts their ids for deterministic output, appends them to the result, removes them from the graph, and deletes their ids from the remaining prerequisite sets.
> — *the book, Ch 10 line 144; explained across several passages, no single defining sentence*

In plain words: Repeatedly take every step with no unfinished prerequisites, add those to the order sorted by id, and remove them, until the graph is empty. The result is an order in which every declared prerequisite comes first.

Example: inspect has no prerequisites, build comes after inspect, verify after build, so the order is inspect, build, verify.

Not to be confused with: an executable plan (the order only uses the arrows you declared)

**persistent change**  *(also: persistent file change; state change; persistent state)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> A persistent change creates a before and an after that you can check separately from the final explanation, so a proposed revision and a saved revision are different deliverables.
> — *the book, Ch 3 line 34; explained across several passages, no single defining sentence*

In plain words: A persistent change is an edit that is still there after the chat is over, such as a saved file. Because there is a before and an after, you can check it separately from what the system said.

Example: Saving an edited report changes a file; telling you which paragraphs to change does not.

Not to be confused with: a response (advice or a proposed revision)

**capability is not authorization**  *(also: capability does not confer authority; capability is not authority)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> It does not say you own the target, that affected people consented, that the source may be uploaded, or that a write is appropriate. None of those facts is an input to the subtraction, and reading the empty result more enthusiastically will not recover them. This is the center of the chapter, and the figure compresses it: one task, three surfaces, and a permission check standing between capability and outcome.
> — *the book, Ch 3 line 178; explained across several passages, no single defining sentence*

In plain words: Being able to do something, because it is in the capability set, is not the same as having permission to do it. Ownership, consent and whether a write is appropriate are not part of the capability calculation.

Example: A write-capable surface covers a write requirement, but that does not say the write was approved.

Not to be confused with: authority

**a write is not necessarily dynamic agency**  *(also: write vs dynamic agency)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Here the pattern reaches actions: capability is not authorization, an event label is not independent proof, and a write is not necessarily dynamic agency. We keep those three apart while we choose an interface sufficient for a bounded task.
> — *the book, Ch 3 line 18; explained across several passages, no single defining sentence*

In plain words: Saving a file does not by itself mean the system is directing its own process. A fixed program can write a file, and a model-directed process can make several decisions without writing one.

Example: A predefined program that writes a file.

Not to be confused with: agent label

**stopping is a control-flow event**
*agents and the agent loop · core · chapters 4 · kind: concept*

> Stopping is a control-flow event. Success needs evidence.
> — *the book, Ch 4 line 2; explained across several passages, no single defining sentence*

In plain words: When a loop ends, all that has happened is that the program returned by one of its exit paths, which says nothing about whether the answer is correct. Whether the result is right needs separate evidence.

Example: A lookup that sees blue followed by a finish with answer red still returns the status finished.

Not to be confused with: task success

**lookup environment**  *(also: records; fixture; mapping)*
*agents and the agent loop · core · chapters 4 · kind: component*

> The mapping of records is the lookup environment, and the controller never alters it.
> — *the book, Ch 4 line 32; explained across several passages, no single defining sentence*

In plain words: The dictionary of records that lookups read from; the controller reads it but never changes it. It is a made-up fixture, so an answer agreeing with it is not thereby true outside the exercise.

Example: The records {"color": "blue"}.

**select the lowest layer that does the job**  *(also: route deterministic work out of the model)*
*agents and the agent loop · core · chapters 4 · kind: pattern*

> Its working rule is to select the lowest layer that does the job and to route deterministic work out of the model entirely. The stack and its reliability labels are the book's own teaching device, not an industry standard, and the rule is a design preference, not a measurement showing that loops perform worse.
> — *the book, Ch 4 line 147; explained across several passages, no single defining sentence*

In plain words: Use the simplest layer that gets the job done, and keep deterministic work out of the model entirely. The chapter calls this a design preference, not a measurement.

Example: The question "what is the color record" is just records["color"], with no loop.

**visible trace**
*agents and the agent loop · core · chapters 4 · kind: concept*

> A visible trace shows requested tool actions, returned output, and a final message. That is enough to ask questions about sequence and evidence. It is not a window into private reasoning, so do not narrate an internal deliberation, and do not claim the production system uses this Python loop.
> — *the book, Ch 4 line 199; explained across several passages, no single defining sentence*

In plain words: What you can see of a real Claude task: requested tool actions, returned output and a final message, which you can map onto actions and observations. It does not show private reasoning, and you may not claim the real system uses this Python loop.

Example: A Claude Code bug fix in a disposable repository, or a document task.

**iteration count and permission are separate controls**  *(also: a bounded loop can still cross a boundary once)*
*agents and the agent loop · core · chapters 4 · kind: concept*

> A budget of one can still allow one wrong target or one unauthorized mutation in a system that exposes such tools. Iteration count and permission are separate controls.
> — *the book, Ch 4 line 301; explained across several passages, no single defining sentence*

In plain words: Limiting how many turns the loop runs does not limit what a single turn may touch. A budget of one can still allow one wrong target or one unauthorized change.

Example: A budget of one allowing one unauthorized mutation.

**least privilege**  *(also: lowest capability that does the step)*
*agents and the agent loop · core · chapters 5 · kind: concept*

> The book does not state it for permissions; this lesson calls the permissions version least privilege. A tool that summarizes course notes needs to read them. Every operation you add to the vocabulary is a capability you must later verify, so a write has to earn its place.
> — *the book, Ch 5 line 30; explained across several passages, no single defining sentence*

In plain words: Give a tool only the access its task needs and nothing more, because every extra operation is something you must later verify. Decide the smallest root and vocabulary that suffices.

Example: A tool that summarizes course notes needs to read them, so it gets read and not write.

**read and write are different authority questions**  *(also: read versus write; a contained read needs no approval)*
*agents and the agent loop · core · chapters 5 · kind: concept*

> Which operations need a human, and which do not? This policy answers: a contained read does not, and a contained write does. That is a judgment about consequences, and it is yours to make for each task.
> — *the book, Ch 5 line 133; explained across several passages, no single defining sentence*

In plain words: Whether an operation needs a human approval is a judgment about its consequences. In this policy a contained read passes without approval and a contained write needs it.

Example: The same target can be accepted for reading and rejected for writing without inconsistency.

**finishing is not succeeding**
*agents and the agent loop · core · chapters 6 · kind: concept*

> The same holds for what Claude Code tells you at the end of a session. A final message that says the tests pass is a claim about a run, standing exactly where checks_passed=True stands: it carries no command, output, or link to the diff you are about to merge unless you go and get them. Chapter 4 made this point about loops: finishing is not succeeding.
> — *the book, Ch 6 line 144; explained across several passages, no single defining sentence*

In plain words: A closing message from Claude Code saying the tests pass is a claim about a run, like checks_passed=True, with no command, output or link to the diff unless you get them. A tidy summary is the finish, not the evidence.

Example: A final message that says the tests pass.

**not-waterfall rule**  *(also: design first is not design frozen; reopening the plan; controlled state with versions)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> A plan is a controlled state with versions. When a result contradicts an assumption the plan rested on, you revise the plan, with the reason recorded, instead of pushing forward on a stale one.
> — *the book, Ch 10 line 42; explained across several passages, no single defining sentence*

In plain words: A plan is not frozen: when a result contradicts an assumption, you revise the plan and record why, rather than pushing on. The first reviewed version still must exist before Claude changes anything, so you can see which decision evidence reopened.

Example: Auditing the diff of the discount-rule example shows rounding was never specified, which reopens the requirement.

**loop exit**  *(also: exit status; controller status)*
*agents and the agent loop · core · chapters 11 · kind: concept*

> Each exit is a decision about what the loop may claim. There are three main exits:
> — *the book, Ch 11 line 150; explained across several passages, no single defining sentence*

In plain words: A loop exit is a way the controller can end or continue, and each is a decision about what the loop may claim. end_turn returns finished, any other non-tool stop returns stopped with the reason, and tool_use runs the tools and continues unless the budget is exhausted.

Example: end_turn gives finished; max_tokens gives stopped; a tool_use stop with no calls raises an error.

**lowest sufficient capability**  *(also: smaller surface; smallest capability set that finishes the task; select the lowest capability the step requires; verifiability first)*
*agents and the agent loop · core · chapters 3 · kind: technique*

> That is a reason to choose the smaller surface, and the reason is not that the larger one is untrustworthy. The task does not need its extra operation, and every operation you grant is one more thing you must be able to check afterward.
> — *the book, Ch 3 line 89; explained across several passages, no single defining sentence*

In plain words: Grant only the abilities the task needs, so that if reading is enough you do not grant writing. Each extra ability is one more thing you must be able to check afterward.

Example: A read-only folder summary needs read, not write, so assistant is enough.

Not to be confused with: minimizing the tool set whatever the work

**predefined workflow vs model-directed process**  *(also: workflow-versus-agent distinction)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> distinguishes predefined workflows from systems in which the model directs its own process. A predefined program can write a file, and a model-directed process can make several decisions without writing one.
> — *the book, Ch 3 line 113; explained across several passages, no single defining sentence*

In plain words: A predefined workflow follows steps written in advance, while a model-directed process lets the model decide its own steps. Which one it is concerns control, not whether the system can write.

Example: One hypothetical predefined workflow that writes and one model-directed process that does not need to write.

Not to be confused with: agent surface (write capability)

**proposed vs executed**  *(also: proposed apart from the executed)*
*agents and the agent loop · core · chapters 3 · kind: concept*

> Record files before and after. Keep the proposed apart from the executed: a response may offer to save a file, ask permission, or explain a command without running it, and none of those is the completed write a trace stipulates.
> — *the book, Ch 3 line 204; explained across several passages, no single defining sentence*

In plain words: Offering to save a file, asking permission, or explaining a command is not the same as doing it. Only a completed write counts as a write event.

Example: The system says it will save the file but never runs the operation.

**activity versus progress**
*agents and the agent loop · core · chapters 4 · kind: concept*

> A longer trace is more recorded activity. Success at the tool boundary does not imply progress at the task boundary, and the controller computes no progress measure.
> — *the book, Ch 4 line 91; explained across several passages, no single defining sentence*

In plain words: A longer trace only shows that more actions were recorded; it does not show the task is closer to a supported answer. The controller keeps no measure of progress.

Example: Repeating a lookup against an unchanged mapping adds another observation of the same operation, not new evidence.

Not to be confused with: new evidence

**policy exhaustion versus budget exhaustion**
*agents and the agent loop · core · chapters 4 · kind: concept*

> These results do not contradict each other. The statuses report different boundaries the controller actually reached. With a larger budget it can discover the iterator has ended; with a budget of one it reaches its own limit first.
> — *the book, Ch 4 line 119; explained across several passages, no single defining sentence*

In plain words: Policy exhaustion means the actions ran out first, giving incomplete; budget exhaustion means the turns ran out first, giving budget-exhausted. Which one you see depends on the path the controller actually took, not on what was waiting beyond it.

Example: The same one-lookup policy returns incomplete under a budget of four and budget-exhausted under a budget of one.

**separating the three jobs**
*agents and the agent loop · core · chapters 4 · kind: technique*

> Something decides whether the final result is any good. In a chat window they arrive as one voice saying done. Pulling them apart is how you give each one an owner.
> — *the book, Ch 4 line 28; explained across several passages, no single defining sentence*

In plain words: Keeping the proposer, the controller and the judge as separate parts so each can be debugged and owned on its own. A poor action sequence dispatched as specified is a fault in the sequence, and the right sequence with the wrong status is a fault in the controller.

**when a loop earns its place**  *(also: does this task need a loop)*
*agents and the agent loop · core · chapters 4 · kind: pattern*

> I build the loop here because the exits are the subject, not because the task needs one. A loop earns its place when the next action depends on what the previous one found, and this controller's scripted policy does not yet. It is a skeleton for the exits.
> — *the book, Ch 4 line 149; explained across several passages, no single defining sentence*

In plain words: Ask first whether the task needs a loop at all. A loop is worth it when the next action depends on what the previous one found, and every loop you add is an exit you must design and a finish you must check.

Example: A one-line dictionary lookup, records["color"], needs no loop, no exits and no finish.

**who took each stop**  *(also: stop log)*
*agents and the agent loop · core · chapters 4 · kind: technique*

> Add one column to your notes for each run: every point where it stopped, and who took that stop. Claude ended its turn and reported done; you interrupted; you approved or declined a request; you accepted the result.
> — *the book, Ch 4 line 201; explained across several passages, no single defining sentence*

In plain words: For each run, note every point where it stopped and who took that stop: Claude ended its turn, you interrupted, you approved or declined a request, or you accepted the result.

Example: Claude ended its turn and reported done.

**three layers of the conclusion**  *(also: policy, controller, check)*
*agents and the agent loop · core · chapters 4 · kind: pattern*

> Your conclusion should name three layers: the policy supplied an action, the controller processed it and stopped under a named rule, and a separate check assessed the answer against the task evidence. Where a layer is absent, say so. The wrong finish shows that the first two can occur without the third succeeding.
> — *the book, Ch 4 line 207; explained across several passages, no single defining sentence*

In plain words: Your report should name three layers: the policy supplied an action, the controller stopped under a named rule, and a separate check assessed the answer. If a layer is absent, say so.

Example: In the wrong finish the first two layers occur without the third succeeding.

**a returned path is not a completed operation**  *(also: authorization result versus execution; preflight versus performed operation)*
*agents and the agent loop · core · chapters 5 · kind: concept*

> A returned Path is therefore not evidence that anything was opened. Existence, object type, access at the moment of use, and success are separate questions. This matters most for writes: a file you are about to create does not exist yet, so the preflight can accept a location it cannot inspect, and acceptance neither creates the file nor shows that its contents are valid.
> — *the book, Ch 5 line 46; explained across several passages, no single defining sentence*

In plain words: When authorize hands back a path, that only means the proposal passed the check; nothing was opened, read, written or created. Whether the file exists, can be accessed at the time of use, and the operation succeeded are separate questions.

Example: A report that says the test wrote x because the returned path ends in x confuses an authorization result with execution.

Not to be confused with: a completed file operation

**proposal versus grant**  *(also: proposal; accepted proposal; Claude proposes actions)*
*agents and the agent loop · core · chapters 5 · kind: pattern*

> Claude keeps a role: it proposes actions, and a proposal is useful input to review. What it cannot do is grant itself the permission. That separation is the design.
> — *the book, Ch 5 line 36; explained across several passages, no single defining sentence*

In plain words: The model's job is to propose an action; a person or the surrounding process decides whether it is allowed. The model cannot approve its own request, even by writing the word approved.

Example: A model can propose an action and explain why, but it does not get to produce its own independent human approval.

Not to be confused with: a Boolean approval value (not a human act)

**enforcement in the runtime**  *(also: runtime enforcement; executable rules mediate actions)*
*agents and the agent loop · core · chapters 5 · kind: pattern*

> A request for caution is a hope. A function that raises PermissionError does not care how persuasive the request was. Enforcement lives in the runtime, where text cannot reach it.
> — *the book, Ch 5 line 32; explained across several passages, no single defining sentence*

In plain words: Rules that must hold are put in code that runs between the request and the action and refuses with an error, so no wording in the request can change the outcome.

Example: authorize raises PermissionError("Path escapes the data boundary") however persuasive the request is.

Not to be confused with: a request for caution written in prose

**three decisions in authorize**  *(also: three checks; operation, location, write approval)*
*agents and the agent loop · core · chapters 5 · kind: framework*

> Read it as three decisions, in the order the function makes them. The first is the operation vocabulary. Only read and write are allowed, and execute is refused even with approval true, before the path is resolved at all.
> — *the book, Ch 5 line 103; explained across several passages, no single defining sentence*

In plain words: authorize makes three separate decisions in order: is the operation allowed, is the resolved target inside the root, and for a write is approval exactly True. Each is independent, so passing one never substitutes for another.

Example: An unapproved contained write passes the first two checks and fails the third.

**the driver's seat (what Claude does, what you keep)**  *(also: task split between Claude and you)*
*agents and the agent loop · core · chapters 5 · kind: framework*

> Record, in the artifact, one task you delegated and one judgment you retained, each pointing to a transcript line, a diff, or an edit you made. If you cannot point to them, the split happened in your head and not in the record.
> — *the book, Ch 5 line 256; explained across several passages, no single defining sentence*

In plain words: A task-by-task split: Claude lists candidates, drafts approval records, proposes edge cases and writes the function fast, while you choose the smallest root and vocabulary, name the approver, write the first edge-case list, run the tests, and choose the verb you sign. The split must be traceable in your record.

Example: Claude proposes edge cases such as links, absolute targets, siblings, unknown operations and non-Boolean approval; you write the first list and choose which become tests.

**conduct, check, drive (the three jobs)**  *(also: three jobs; Conduct; Check; Drive)*
*agents and the agent loop · core · chapters 9 · kind: framework*

> Those are Chapter 1's three jobs applied to a change request. Conduct: state what should change, and how you will tell, before you change it. That is the gate.
> — *the book, Ch 9 line 8; explained across several passages, no single defining sentence*

In plain words: The three jobs a human does when working with Claude: conduct (state what should change, and how you will tell, before you change it), check (claim only what the record supports, and sign or withhold), and drive (decide what kind of question you are answering).

Example: You wrote the objective, held-out list, and stop rule before the loop ran (conduct), wrote "training loss decreased" and nothing more (check), and kept the prediction-or-intervention question (drive).

**gate items are human decisions**  *(also: none of it can be delegated)*
*agents and the agent loop · core · chapters 9 · kind: pattern*

> Every line above is a human decision, and none can be derived from the data, because the data have no opinion about what "better" should mean. For the toy they are my choices; no model produced them. For a real change request they are yours, and that is why none of it can be delegated.
> — *the book, Ch 9 line 116; explained across several passages, no single defining sentence*

In plain words: The objective, held-out set, and stop rule cannot be derived from the data, because the data have no opinion about what "better" should mean. Claude can sharpen the gate but cannot choose the objective for you.

Example: Claude can propose the wrong version and the test that catches it.

**eight plan fields**  *(also: FIELDS; required plan fields)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> Each field is a place where a decision was made or was not. The reference declares them in one tuple:
> — *the book, Ch 10 line 69; explained across several passages, no single defining sentence*

In plain words: A plan is checked for eight named parts: objective, inputs, scope, steps, tools, risks, verification, and stop. Each name stands for a question a reviewer asks, while code can only see whether the name has a value.

Example: FIELDS = (objective, inputs, scope, steps, tools, risks, verification, stop)

**plan predicts, result records**  *(also: prediction versus record)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> A plan is a set of predictions. The steps predict what will be done, the verification field predicts what you will observe if it worked, and the stop field predicts which events end the work. A result is a record of what happened.
> — *the book, Ch 10 line 186; explained across several passages, no single defining sentence*

In plain words: A plan states predictions and a result records what actually happened; they are different documents and should stay apart. If the plan is edited after the run to match the run, it has become a description of the result.

Example: The symlink plan's predicts line: the new test passes, the existing tests still pass, and the diff lists only allowed files.

**plan is a proposal**  *(also: returned plan remains a proposal)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> Claude Code can propose or critique a plan through the assumed course account, but the returned plan remains a proposal.
> — *the book, Ch 10 line 20; explained across several passages, no single defining sentence*

In plain words: A plan that Claude drafts is only a suggestion until a person has reviewed and approved it.

Example: Asking Claude Code for a plan in the eight fields: what returns is a proposal.

**problem formulation**  *(also: formulate before you plan; framing)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> The first decision in a plan is not in any of the eight fields. It is which problem the plan is for. A perfectly ordered plan can optimize the wrong objective, and the cost is highest when Claude executes it fluently, because a polished, internally checked answer to the wrong question carries authority the question never earned.
> — *the book, Ch 10 line 46; explained across several passages, no single defining sentence*

In plain words: Before ordering any steps, decide which problem the plan is for: write candidate formulations that differ in what counts as success, then choose one. A flawless plan for the wrong problem is still wrong.

Example: Three candidates for the plus-one bug: A, the single failing test goes green; B, the declared behavior is restored within scope; C, the learner can explain the bug.

**division of drafting and deciding**  *(also: driver's seat)*
*agents and the agent loop · core · chapters 10 · kind: concept*

> You can hand some of these questions to Claude to draft: the steps, the tools list. Others you answer, because they depend on things no file contains. What the work is for, what you are willing to have touched, which risks you accept, and who decides when to stop are yours.
> — *the book, Ch 10 line 93; explained across several passages, no single defining sentence*

In plain words: Claude may draft the steps and the tools list, but you answer the questions that depend on things no file contains: what the work is for, what may be touched, which risks you accept, and who decides when to stop.

Example: In the symlink plan, the steps are marked Claude drafted, I revised; the objective, scope and stop are marked me.

**initial judgments before synthesis**  *(also: sequencing practice; independent initial judgment; preserve dissent)*
*agents and the agent loop · core · chapters 12 · kind: technique*

> I use only its sequencing practice, which stands on its own as a design rule: collect initial judgments before showing a synthesis, then deliberate with the sources visible, and preserve dissent rather than averaging it into smooth prose.
> — *the book, Ch 12 line 215; explained across several passages, no single defining sentence*

In plain words: Collect each person's own judgment before anyone sees a synthesis, then discuss with the sources visible and keep the disagreements instead of averaging them away. The chapter's reason is that showing the synthesis first collapses the variety before it can do any work.

Example: A solo learner writes a dated initial interpretation before reading any Claude synthesis.

**independence of judgments**  *(also: copies are not independence; failure correlation)*
*agents and the agent loop · core · chapters 12 · kind: concept*

> It does not produce independent judgment, because copies are not independence. Two sessions may share a model, training influences, tool configuration, source corpus, and prompt author, and role labels such as “researcher” and “reviewer” do not manufacture independence. Independence is a design question about failure correlation: would the two routes fail for the same reason?
> — *the book, Ch 12 line 213; explained across several passages, no single defining sentence*

In plain words: Two workers are independent only if they would not fail for the same reason. Sessions sharing a model, sources, tools or a prompt author are copies, so their agreement is not independent confirmation.

Example: Two agents retrieving from one incomplete corpus can agree for the same cause.

Not to be confused with: two sessions agreeing

**no automatic retry after a stale write**  *(also: version conflict is not a merge algorithm)*
*agents and the agent loop · core · chapters 12 · kind: pattern*

> Retrying automatically at version four would be unsafe, because the human-approved value may carry a qualification the worker's proposal lacks. The stale worker must reread, compare the semantic changes, and either withdraw or create a new reviewable proposal. Version conflict is not a merge algorithm.
> — *the book, Ch 12 line 261; explained across several passages, no single defining sentence*

In plain words: When a write is rejected as stale, the worker must not simply reread and retry. It has to reread, compare what changed in meaning, and either withdraw or submit a new proposal for a reviewer, because the conflict is a signal to go back to a decision.

Example: A worker's expected=3 Monday update fails after the reviewer commits version four; retrying at version four could drop a qualification the approved value carries.

Not to be confused with: merge

**AI should, Python should, Human should**  *(also: Human should)*
*agents and the agent loop · core · chapters 12 · kind: framework*

> AI should execute bounded research and review tasks, retain source identifiers, compare revisions, surface conflicts, and summarize disagreements without flattening them. Python should enforce the expected-version rule and preserve reproducible state transitions. AI should not label model agreement as human consensus or treat a fresh revision as verified truth.
> — *the book, Ch 12 line 452; explained across several passages, no single defining sentence*

In plain words: The chapter's split of responsibilities by task: AI does bounded research and review and surfaces conflicts, Python enforces the expected-version rule, and the human forms an initial interpretation, supplies missing context, judges the stakes, hears dissent and decides.

Example: AI should not label model agreement as human consensus.

**gate sequence (proposal to observed outcome)**
*agents and the agent loop · core · chapters 13 · kind: framework*

> Steps 3 and 4 are where your gate does its work; steps 5 and 6 are where it stops being yours to automate. Changing the proposal returns the workflow to step three or earlier, because a valid old approval is evidence about history, not authority for the new object. Approval permits a bounded attempt and does not guarantee the intended result, so keep the proposal fingerprint, the effect evidence, and the post-action check as separate linked records.
> — *the book, Ch 13 line 291; explained across several passages, no single defining sentence*

In plain words: Eight steps: build a proposal from the plan and state, validate it, run scoped evaluations and record exclusions, freeze and fingerprint it, present it to an authorized reviewer, record approve, refuse or defer, recheck fingerprint, expiry, revocation and use at execution, then observe the actual outcome separately. Changing the proposal sends the workflow back to step three or earlier.

**finished wrong answer**  *(also: finish(red); blue-record red-answer counterexample)*
*agents and the agent loop · core · chapters 4 · kind: named result or case*

> Now compare answer and observation. Red does not agree with blue. The controller does not perform that comparison, and its status is an accurate description of its own event: it received a finish.
> — *the book, Ch 4 line 101*

In plain words: A constructed run where the records say color is blue, the policy looks it up and sees blue, then finishes with red, and the controller still returns finished. It shows a finished status can sit beside an answer the evidence contradicts.

Example: Records {"color": "blue"}, policy: lookup color then finish with answer red.

Not to be confused with: verified task success

**repeated-lookup run**  *(also: repeated-action run; repeated lookup)*
*agents and the agent loop · core · chapters 4 · kind: named result or case*

> Consider a policy that repeatedly supplies a lookup action and a budget of two. Each turn consumes one action and records one observation. After the second append the loop has no turn left and returns budget-exhausted.
> — *the book, Ch 4 line 113*

In plain words: A scripted policy that keeps asking for the same lookup is stopped by a turn budget of two after two recorded observations, with status budget-exhausted. The policy does not need to be finite for the limit to hold, but the limit bounds turns, not time.

Example: Budget of two: two trace entries, then budget-exhausted.

# how models generate (29)

**objective**
*how models generate · core · chapters 9, 10 · kind: concept*

> The average binary logistic loss on the four training pairs listed below, and nothing else. "Better" means "lower on this objective on these pairs." That is the only thing the training run may be called.
> — *the book, Ch 9 line 102; explained across several passages, no single defining sentence*

In plain words: The one quantity the optimizer is told to lower, chosen by a human before training. "Better" only means lower on this objective, on these pairs.

Example: The average binary logistic loss on the four training pairs.

Not to be confused with: better (a claim about the task, which the loss does not hold)

**temperature**  *(also: concentration control; positive temperature)*
*how models generate · core · chapters 1, 9 · kind: concept*

> A smaller positive T makes the exponent larger and increases the probability ratio; a larger T brings the ratio closer to one. The transformation is changing relative concentration, which explains the temperature effect without a slogan about creativity.
> — *the book, Ch 1 line 311; explained across several passages, no single defining sentence*

In plain words: Temperature T divides the scores before they become probabilities: a smaller T concentrates probability on the largest score and a larger T spreads it out. It changes how concentrated the distribution is, not which score is largest and not whether any answer is true.

Example: Scores [1, 2, 3]: the largest score gets about 87 percent at T = 0.5 and about 51 percent at T = 2.

Not to be confused with: creativity

**score**  *(also: logit; logits)*
*how models generate · core · chapters 1 · kind: concept*

> The list [1, 2, 3] expresses an ordering: the third entry is largest. It does not yet express chances. Call its entries scores, or logits when referring to the function's parameter name; the word gives them no extra authority.
> — *the book, Ch 1 line 249*

In plain words: A score is a raw number given to each outcome; it gives an ordering but is not yet a chance. It must be turned into a probability before anything is drawn.

Example: Scores [1, 2, 3]: outcome two has score three; keep the index separate from the score.

Not to be confused with: probability

**token**
*how models generate · core · chapters 1 · kind: concept*

> The machine does not predict words. It predicts tokens: fragments drawn from a fixed vocabulary, where a common word may be one token, a rare word several, and a space is usually part of the token that follows it. unbelievable might arrive in three pieces.
> — *the book, Ch 1 line 67*

In plain words: The unit the model predicts at each step is a token, a fragment drawn from a fixed vocabulary, not a word and not a fact. A word that spans three tokens takes three steps to finish.

Example: A prompt that asks for an exact character count asks the machine to reason about a unit it does not natively see.

Not to be confused with: word

**transcript**  *(also: a chat as a single string with role markers)*
*how models generate · core · chapters 1 · kind: concept*

> If the model only continues text, how does it hold a conversation? By being handed text that looks like a conversation. Under the interface, a chat is a single string with role markers, something with the shape of:
> — *the book, Ch 1 line 93*

In plain words: Under the interface, a chat is one string of text with role markers that the model continues. That is how a text-continuing machine holds a conversation.

Example: System: You are a careful assistant. / User: What does the attached policy say about late submissions? / Assistant:

**training**  *(also: parameter learning)*
*how models generate · core · chapters 9 · kind: concept*

> Training changes parameters through an objective and an update rule. Prompting and retrieval change the information supplied to an already configured model for inference.
> — *the book, Ch 9 line 4*

In plain words: Training changes the model's stored numbers (its parameters) by using an objective and an update rule. Changing the input to a model that already exists is a different thing.

Example: In the toy, train returns w and b after using labels and a loss-derived gradient.

Not to be confused with: prompting and retrieval

**weight**  *(also: w)*
*how models generate · core · chapters 9 · kind: concept*

> A positive learned weight makes positive x values produce positive scores and probabilities above one-half; negative x values produce negative scores and probabilities below one-half when the bias stays near zero. That geometry matches our constructed labels. The parameter does not learn a word meaning or a causal relationship.
> — *the book, Ch 9 line 90*

In plain words: One of the toy's two learned numbers. A positive weight pushes positive inputs toward label one, and it fits the relationship in the supplied pairs, not a meaning or a cause.

Example: After 200 steps the learned weight is about 3.1669517461.

**step count (budget)**  *(also: budget; steps)*
*how models generate · core · chapters 9, 10 · kind: concept*

> The step count is a budget in the same way. Two hundred is the demo setting, not a discovered natural stopping point. The function runs exactly that many updates and has no convergence test, validation-based early stopping, or best-checkpoint selection.
> — *the book, Ch 9 line 182*

In plain words: The number of updates the loop is allowed to run. Two hundred is the demo setting, not a natural stopping point, and the toy has no convergence test or early stopping.

Example: Exactly 200 updates.

**sampling**  *(also: draw; weighted selection; sample one)*
*how models generate · core · chapters 1 · kind: technique*

> The probability function returns a recipe for selection, not a thousand outcomes. The next function makes that transition. It creates a local pseudorandom generator, asks for weighted selections, counts which indices appeared, and returns a dictionary of counts.
> — *the book, Ch 1 line 335*

In plain words: Sampling turns a distribution, which is only a recipe for selection, into actual outcomes by drawing at random in proportion to the probabilities. What you get back is counts of what was drawn in this one run.

Example: 1,000 draws from scores [1, 2, 3] at temperature 1 with seed 7 gave counts of 102, 268 and 630.

Not to be confused with: the distribution that generated it

**observed frequency**  *(also: observed share; observed count; expected count)*
*how models generate · core · chapters 1 · kind: concept*

> At temperature one, outcome two's observed share is 630 / 1000, or 0.63, against an assigned probability of about 0.66524. Keep both numbers in the report. They answer different questions: what chance was assigned, and what fraction appeared in this sample?
> — *the book, Ch 1 line 362*

In plain words: The fraction of draws that actually came out a given way in one sample, which differs from the probability the distribution assigned. Counts are evidence of the recorded run, not exact expressions of the theoretical probabilities.

Example: Temperature 1: outcome two assigned about 0.66524, observed 630 of 1,000 (0.63).

Not to be confused with: assigned probability

**next-token prediction**  *(also: next-token predictor; one prediction, run in a loop; continuation engine)*
*how models generate · core · chapters 1 · kind: concept*

> When you send a message to Claude, no component in the system is answering your question. One component is repeatedly answering a different question, what plausibly comes next in this text, and a loop around it turns those answers into something that reads like a reply.
> — *the book, Ch 1 line 57*

In plain words: A language model does not answer your question; it repeatedly answers what plausibly comes next in the text so far, and a loop around it makes that read like a reply. A chatbot is one prediction run in a loop.

Example: A page of dialogue with the assistant's half torn away: the machine returns a ranked field of plausible continuations, you append one and feed the longer text back in.

**prediction loop**  *(also: sample one, append and repeat)*
*how models generate · core · chapters 1 · kind: pattern*

> The transcript goes into the model, the model returns a probability for every possible next token, one token is sampled and appended, and the same question is asked again.
> — *the book, Ch 1 line 60*

In plain words: The cycle that produces a reply: feed in the transcript, get a probability for every possible next token, sample one, append it, and ask again until the machine proposes an ending.

Example: Figure 1.1: transcript so far, model, probability for every token, sample one, append and repeat.

**what the loop does not contain**  *(also: the machine's boundary)*
*how models generate · core · chapters 1 · kind: concept*

> Nothing in the loop reads a document, checks an answer key, or knows whether the growing text is true. Retrieval, tools, permissions, and approval gates arrive in later chapters as attempts to supply something the loop does not contain, and every one of those attempts is something you design and then check.
> — *the book, Ch 1 line 63*

In plain words: The prediction loop never consults a source or an answer key, so nothing in it knows whether the text is true. Retrieval, tools, permissions and approval gates are later attempts to add what the loop lacks.

Example: Retrieval, tools, permissions, and approval gates arrive in later chapters.

**no memory between conversations**  *(also: the entire transcript is resupplied every turn; what feels like memory is a growing string)*
*how models generate · core · chapters 1 · kind: concept*

> Second, the model does not remember your last conversation: the entire transcript is resupplied every turn. What feels like memory is a growing string, which is why long conversations behave differently from short ones and why Chapter 7 treats context as something you engineer rather than something you have.
> — *the book, Ch 1 line 103*

In plain words: The model keeps nothing between turns; the whole transcript is sent again every turn, so what feels like memory is a growing string of text.

Example: Long conversations behave differently from short ones.

**fluent answer from incomplete evidence**  *(also: Claude downstream of a dropped source)*
*how models generate · core · chapters 7 · kind: failure mode*

> Put Claude downstream of either one. It will write a fluent answer from whatever reached it, and nothing it received says what was left out. The sentence reads the same whether the evidence was complete or not.
> — *the book, Ch 7 line 8*

In plain words: Claude writes a smooth answer from whatever it is given, and nothing in the text tells you whether the only relevant source was left out earlier. So completeness has to be checked upstream of the answer.

Example: The tuition-refund retriever silently dropped the only relevant document, and the answer reads just as well.

**mutable object (the five objects)**  *(also: five things a system can change; weights, prompt, context, tools, or settings)*
*how models generate · core · chapters 9 · kind: framework*

> Before you pick a technique you face a decision the sentence hides: which object are you allowed to change? The choices differ in cost, in how they persist, in who can reverse them, and in how you will tell whether they worked. There are five.
> — *the book, Ch 9 line 28*

In plain words: The five things you can change in an AI system are its weights, prompt, context, tools, and settings. Before choosing a technique you decide which one you are allowed to change, because they differ in cost, persistence, reversibility, and evidence.

Example: "Make it stop inventing dates" could be attempted by changing any of the five, and each leaves different evidence.

Not to be confused with: calling every change 'training'

**settings**  *(also: run-time configuration)*
*how models generate · core · chapters 9 · kind: concept*

> A setting changes how an output is drawn from scores. It does not fit anything.
> — *the book, Ch 9 line 40; explained across several passages, no single defining sentence*

In plain words: A run-time choice about how an output is drawn from the model's scores, such as temperature. It does not fit or change the model.

Example: A lowered temperature.

Not to be confused with: weights (training)

**pretraining**
*how models generate · core · chapters 1 · kind: concept*

> This stage is called pretraining, and it produces something that completes internet text rather than something that behaves like an assistant.
> — *the book, Ch 1 line 124; explained across several passages, no single defining sentence*

In plain words: The first training stage: take a passage, hide the next token, compare the model's distribution with the token that actually followed, and nudge the parameters toward it, over an enormous corpus. Nothing in it is told what is true.

Example: Hide the next token of a passage and reward the model for putting more probability on the token that actually followed.

**preference tuning**  *(also: second stage)*
*how models generate · core · chapters 1 · kind: concept*

> A second stage adjusts for that. People are shown candidate replies and asked which they prefer; those judgments shift the parameters toward what raters approved of.
> — *the book, Ch 1 line 124; explained across several passages, no single defining sentence*

In plain words: A second training stage in which people choose which candidate replies they prefer and the parameters are shifted toward what raters approved of. Its target is approval, which is not the same as correctness.

Example: Figure 1.3: in preference tuning the target is the reply human raters preferred.

Not to be confused with: correctness

**softmax**  *(also: normalization; exponentiate then divide by the total weight)*
*how models generate · core · chapters 1 · kind: technique*

> The mechanism exponentiates score differences, then divides by the total weight. An exponential converts any finite real input into a positive weight.
> — *the book, Ch 1 line 253; explained across several passages, no single defining sentence*

In plain words: The transformation that turns scores into probabilities: exponentiate each score (divided by the temperature) to get a positive weight, then divide each weight by the total so they sum to one. It is the final step you build by hand in Part 2.

Example: Scores [1, 2, 3] at temperature 1 give probabilities about 0.090, 0.245 and 0.665.

**a score is not a probability**  *(also: the chapter's one distinction)*
*how models generate · core · chapters 1 · kind: concept*

> Both parts serve one distinction: a score is not a probability, a probability is not an observed frequency, and an observed frequency is not a correctness judgment. We can make one outcome increasingly likely without adding any evidence that it is correct, and make a run repeatable without making its answer true.
> — *the book, Ch 1 line 13; explained across several passages, no single defining sentence*

In plain words: The chapter keeps four things apart: a score, a probability, an observed frequency, and a correctness judgment. Making an outcome more likely or a run repeatable adds no evidence that the answer is true.

Example: Scores [1, 2, 3]; probabilities from the transformation; counts from 1,000 draws; and none of them says an outcome is correct.

**changing what the model sees is not changing what the model is**  *(also: Training changes parameters; prompting changes inputs; these conditions change inputs, not Claude's weights)*
*how models generate · core · chapters 9 · kind: concept*

> Changing what the model sees is not changing what the model is.
> — *the book, Ch 9 line 2; explained across several passages, no single defining sentence*

In plain words: Giving a model different input (a prompt, examples, documents) does not change the model itself; only training changes its stored parameters. A better answer after you change the input is not evidence that the model was retrained.

Example: You upload documents and revise a system prompt and get a better answer, but nothing in Claude was trained.

Not to be confused with: training

**persistence is not proof of training**  *(also: it stuck)*
*how models generate · core · chapters 9 · kind: concept*

> Training is identified by its mechanism, not by later influence. In the toy, train returns w and b after using labels and a loss-derived gradient, and that is direct implementation evidence. A saved prompt influences later requests by being included again as input.
> — *the book, Ch 9 line 48; explained across several passages, no single defining sentence*

In plain words: A change that sticks (a saved prompt, a retrieved document, a permission rule, a memory record) is not evidence of training. Training is identified by its mechanism: labels and a loss-derived gradient updating parameters.

Example: A saved prompt influences later requests by being included again as input.

Not to be confused with: training

**variation between runs**  *(also: same input, different output)*
*how models generate · core · chapters 1 · kind: concept*

> You cannot yet say what this implies about the variation you observe: ask the same question twice and the answers differ, but the parameters and architecture did not change between runs. Something else moved. Part 2 shrinks the system until that moving part is the only thing left in the room.
> — *the book, Ch 1 line 227; explained across several passages, no single defining sentence*

In plain words: Asking the same question twice can give different answers even though the model itself did not change. The chapter traces the difference to the random selection step that Part 2 shrinks down and inspects.

Example: Two answers to the same question: the second has a different example, a different qualification, perhaps a different conclusion.

**probability distribution over tokens**  *(also: distribution; ranking over strings; a ranked field of candidates)*
*how models generate · core · chapters 1 · kind: concept*

> The output for one step is not a token. It is a number for every token in the vocabulary, tens of thousands of them, arranged so the numbers are nonnegative and sum to one. Every candidate continuation gets a share, including absurd ones.
> — *the book, Ch 1 line 83; explained across several passages, no single defining sentence*

In plain words: At each step the model outputs a nonnegative number for every token in the vocabulary, and the numbers sum to one. Every candidate gets a share, so nothing is excluded and the absurd ones just get small shares.

Example: After The capital of France is, Paris receives a high probability.

Not to be confused with: a single predicted token

**ranking is not truth**  *(also: the load-bearing distinction; the mechanism ranks continuations)*
*how models generate · core · chapters 1 · kind: concept*

> The mechanism ranks continuations, and ranking a continuation highly is not evidence that it is true. You do not need a position on machine understanding to accept that.
> — *the book, Ch 1 line 223; explained across several passages, no single defining sentence*

In plain words: The model's numbers rank possible continuations of a string, based on how phrases continue in the training text, and an answer key is not among the inputs. A high ranking is therefore not evidence that something is true.

Example: Paris gets a high probability after The capital of France is because of how that phrase continues in the corpus, and the agreement with the facts is not guaranteed in the next case.

Not to be confused with: a lookup against an atlas

**misnaming a change (the verb carries a claim)**  *(also: mechanism label; branding)*
*how models generate · core · chapters 9 · kind: failure mode*

> But the verb carries a claim about what changed, and that claim decides what happens next.
> — *the book, Ch 9 line 4; explained across several passages, no single defining sentence*

In plain words: Calling a change 'training' when you only changed a prompt, retrieved text, a tool, or a setting names the wrong thing. The wrong name sends you to maintain, audit, and pay for the wrong thing.

Example: A teammate writes up a better answer as "we trained Claude on our policies."

Not to be confused with: training versus prompt versus retrieval

**classify a change by the object it modifies**
*how models generate · core · chapters 9 · kind: technique*

> Then take four proposed changes, say a rewritten system prompt, a new document in a workspace, a newly enabled tool, and a lowered temperature, and classify each by the object it modifies. For each, say how you would observe the change. If the only evidence is a different output, do not jump to a claim about changed weights.
> — *the book, Ch 9 line 289; explained across several passages, no single defining sentence*

In plain words: Sort each proposed change (a rewritten system prompt, a new workspace document, a newly enabled tool, a lowered temperature) by the object it changes, and say how you would observe it. A different output alone does not justify a claim about changed weights.

Example: A rewritten system prompt is a prompt change; a lowered temperature is a settings change.

Not to be confused with: claiming changed weights from a different output

**lowering temperature is not a truth guarantee**  *(also: temperature is not a fact checker; concentration is not correctness)*
*how models generate · core · chapters 1 · kind: named result or case*

> Lowering temperature concentrates selection on label two, which is wrong under the stipulated answer key. The transformation works as designed; the failure is in treating its preference as a truth guarantee. Do not report this as an observed Claude error.
> — *the book, Ch 1 line 325; explained across several passages, no single defining sentence*

In plain words: If the checked answer is a different label from the top-scored one, lowering temperature concentrates selection on the wrong label. The transformation works as designed; the mistake is treating its preference as a guarantee of truth.

Example: Constructed hypothetical: the independently checked answer is label zero, but lower temperature concentrates on label two.

Not to be confused with: fact checker

# tools and integration (46)

**Use It**  *(also: conduct Claude Code against your gate)*
*tools and integration · core · chapters 1, 2, 4, 13, 14, 15 · kind: pattern*

> Give it the gate you wrote, the contract and the test list and the fixtures, and not your validator. Ask for an implementation that satisfies the contract and passes your tests. Then run your tests on what it returns, yourself.
> — *the book, Ch 2 line 209*

In plain words: Step two of the spine: give Claude Code your gate (contract, tests, fixtures) but not your validator, ask for an implementation, and run your own tests on what it returns. A failing test often reveals a gap in your gate.

Example: Ask Claude for three plausible-but-wrong validators and run your tests against each.

**Claude Code**
*tools and integration · core · chapters 2, 3, 4, 6 · kind: protocol or tool*

> Claude Code can read a repository, propose a plan, edit files, and run commands faster than you can read the result; do not compete with that.
> — *the book, Ch 6 line 10*

In plain words: A coding assistant that can read a repository, propose a plan, edit files and run commands, often faster than a person can read the result. The chapter treats its output as something you conduct, check and decide on, not something you race.

Example: In a disposable repository it proposes a patch, and you keep its actual plan, diff, commands and outputs.

**server**  *(also: MCP server)*
*tools and integration · core · chapters 8, 9 · kind: component*

> The server implements capabilities and describes them.
> — *the book, Ch 8 line 28*

In plain words: The program that offers capabilities such as the lookup tool and describes them. It cannot say whether it should be used for a task.

Example: The teaching server named info7375-readonly.

Not to be confused with: host

**tools**  *(also: actions and information sources the host exposes)*
*tools and integration · core · chapters 9, 10 · kind: component*

> Which actions and information sources the host exposes, and which are permitted
> — *the book, Ch 9 line 35*

In plain words: The actions and information sources the host makes available to the model, and which of them are allowed. Changing them changes what the system can do, not the model.

Example: A newly enabled tool.

Not to be confused with: weights (training)

**conduct Claude Code against your gate**  *(also: Use It)*
*tools and integration · core · chapters 5, 11, 12 · kind: technique*

> Give it the gate you wrote, the contract, the tests, and the matrix, and not your implementation. Ask for an implementation that satisfies the contract and passes your tests, then run your tests on what it returns, yourself.
> — *the book, Ch 11 line 319; explained across several passages, no single defining sentence*

In plain words: Hand Claude Code a complete specification (the gate, contract, tests and matrix) and ask for an implementation, then run your own tests on what it returns. A failing test is often a gap in your gate, which Claude cannot see because it only has what you wrote.

Example: Compare its implementation with your baseline and name one difference in behavior.

**retrieval**  *(also: retriever)*
*tools and integration · core · chapters 7, 9 · kind: concept*

> Retrieval asks which documents are similar enough under a rule to inspect first. Evidence review asks whether a selected passage supports a specific claim.
> — *the book, Ch 7 line 170; explained across several passages, no single defining sentence*

In plain words: Retrieval picks out the documents that look most similar to the query under a stated scoring rule, so a person can inspect them first. It does not decide whether any passage actually supports a claim.

Example: Query “office hours” ranks a document saying “Office hours by appointment.” highly.

Not to be confused with: evidence review

**tool schema**  *(also: tool description; input_schema)*
*tools and integration · core · chapters 8, 11 · kind: component*

> This schema tells Claude which request shape the application is prepared to consider. It does not import an add function into the model. It does not prove that the application enforces the schema.
> — *the book, Ch 11 line 74*

In plain words: A tool schema is the description (name, purpose, and allowed input shape) that you advertise to Claude. It only tells Claude what kind of request the application will consider; it does not run anything and does not enforce itself.

Example: The add tool: inputs a and b, both numbers, both required, no extra keys.

Not to be confused with: execution engine

**MCP**
*tools and integration · core · chapters 7, 8 · kind: protocol or tool*

> MCP itself supplies a communication structure. It did not choose the tool, and it does not vouch for what comes back.
> — *the book, Ch 8 line 28; explained across several passages, no single defining sentence*

In plain words: A protocol that gives a host and a server a shared structure for exchanging messages about tools. It does not decide which tool to use or vouch for the content returned.

**diff**  *(also: behavioral proposal)*
*tools and integration · core · chapters 6 · kind: concept*

> When Claude Code edits your files, the diff is the thing you review. Its narration of the change is a second-hand account; the diff is the change.
> — *the book, Ch 6 line 82; explained across several passages, no single defining sentence*

In plain words: The record of exactly which text changed between the before and after versions of a file. When an agent edits your files, the diff is what you review, not its narration of what it did.

Example: -return x - 1 / +return x + 1

Not to be confused with: Claude's narration of the change (a second-hand account)

**dispatcher**  *(also: dispatch)*
*tools and integration · core · chapters 4, 11 · kind: component*

> A file tool's dispatcher would also resolve paths, compare the destination with an approved root, and distinguish reads from writes; a database tool's would restrict the statement type, credentials, and row count. Tool schemas help the model form usable proposals. They are not a substitute for these enforcement checks.
> — *the book, Ch 11 line 107; explained across several passages, no single defining sentence*

In plain words: The dispatcher is the application code that takes a proposed call, checks its name and arguments, and runs the real operation. It is where enforcement happens; the schema only helps Claude form proposals.

Example: The dispatch function for add refuses unknown names, extra keys, Booleans and non-finite numbers.

Not to be confused with: tool schema

**Claude Code permissions**  *(also: runtime permission rules; permission rules)*
*tools and integration · core · chapters 5, 9 · kind: protocol or tool*

> The relevant connection is runtime enforcement: requesting caution in prose is not the same as constraining tool actions through permission rules. Our teaching function is only a preflight illustration, not a reproduction of the product's safeguards.
> — *the book, Ch 5 line 325; explained across several passages, no single defining sentence*

In plain words: Claude Code's real permission rules are executable rules that mediate what actions a tool may take, unlike a request for caution written in prompt text. The chapter's Python function is only a small illustration of that idea.

Example: Read-only inspection of the permission configuration in your Claude Code environment, without changing institutional settings.

**containment**  *(also: contained; in-root; is_relative_to)*
*tools and integration · core · chapters 5 · kind: concept*

> First, containment is a statement about the destination, not about which characters look suspicious. A request can step into a subdirectory and back to its parent and still land inside the root. A request with no visible parent component can lead out through a link.
> — *the book, Ch 5 line 44; explained across several passages, no single defining sentence*

In plain words: A target is contained when the place it resolves to lies under the approved root. The test is about where the request ends up, not about suspicious-looking characters such as '..'.

Example: A request that steps into a subfolder and back to its parent still lands inside the root.

Not to be confused with: string-prefix similarity

**host**
*tools and integration · core · chapters 8 · kind: component*

> The host constructs requests, interprets responses, exposes selected tools to Claude, and decides what content enters context.
> — *the book, Ch 8 line 28; explained across several passages, no single defining sentence*

In plain words: The software around Claude that builds the requests, reads the replies, chooses which tools Claude sees, and controls what enters Claude's context.

Example: A host can learn which tools exist and still deny them under its permission policy.

Not to be confused with: server

**interoperability**
*tools and integration · core · chapters 8 · kind: concept*

> Interoperability answers whether components can exchange messages they understand. Authorization answers whether a particular capability should run in this task. A clean handshake settles the first question and is silent on the second.
> — *the book, Ch 8 line 4*

In plain words: Whether two pieces of software can send each other messages that both sides understand. A clean, valid exchange shows this and nothing more.

Example: Two servers both advertise a tool called lookup and both return valid JSON-RPC messages, yet one only reads a fixture and the other writes files.

Not to be confused with: authorization

**four parties**  *(also: the four parties)*
*tools and integration · core · chapters 8 · kind: framework*

> A connection has four parties, and most confusion about MCP is confusion about which party did what. The server implements capabilities and describes them. The host constructs requests, interprets responses, exposes selected tools to Claude, and decides what content enters context.
> — *the book, Ch 8 line 28*

In plain words: The four roles in a connection: the server, the host, Claude or a workflow around it that proposes using a tool, and the people and policies that define authority. Each does a different job and only the people can answer whether this server belongs in this task.

**accountable context**  *(also: not maximal context)*
*tools and integration · core · chapters 7 · kind: concept*

> The result is not maximal context. It is accountable context: enough authorized material to support the bounded answer, an explicit record of what was left out, and a route for saying the evidence is insufficient.
> — *the book, Ch 7 line 282*

In plain words: The chapter's goal: enough authorized material to support a bounded answer, a record of what was left out and a way to say the evidence is insufficient. It is deliberately not the largest possible context.

Not to be confused with: maximal context

**history is part of the protocol**
*tools and integration · core · chapters 8 · kind: concept*

> What should the server do with a message that is legal in one state and illegal in another? You decide per state, in writing, before you read the branch that decides it.
> — *the book, Ch 8 line 119*

In plain words: The same message can be accepted or rejected depending on what came before it, so you decide the response for each state in advance.

Example: tools/list fails in row 2 and succeeds in row 7, and the only difference is history.

**connecting a tool is not training a model**
*tools and integration · core · chapters 8 · kind: concept*

> An MCP server can add information and actions to a host without changing model parameters. That distinction is the bridge to Chapter 9.
> — *the book, Ch 8 line 333*

In plain words: Adding an MCP server gives the host new information and actions, but it does not change the model's parameters.

Not to be confused with: training a model

**verifiability-first engineering**  *(also: lowest-capability rule)*
*tools and integration · core · chapters 11 · kind: framework*

> Conducting AI turns this into a selection rule it calls verifiability-first engineering: choose the lowest capability that does the step, because the most constrained tool is the one you can check.
> — *the book, Ch 11 line 50*

In plain words: When choosing how to do a step, pick the least powerful tool that can do it, since the most constrained tool is the easiest to check. Arithmetic, exact lookups, deterministic transforms and schema validation belong outside the model.

Example: Totaling every line item over $10,000 across 200 invoices: extract fields per invoice, then filter and sum in deterministic code.

**lifecycle**  *(also: handshake; initialization sequence; lifecycle table)*
*tools and integration · core · chapters 8 · kind: concept*

> You can follow a minimal MCP exchange as a state machine: initialize changes one state, the initialized notification changes another, and tool operations become available only afterward.
> — *the book, Ch 8 line 323; explained across several passages, no single defining sentence*

In plain words: The ordered sequence of an MCP connection: an initialize request and reply, then an initialized notification, and only after that tool operations. You read it as behavior, asking which message may come next and what state changes.

Example: Listing tools before initialization returns an error; after initialize plus the notification it returns the one tool.

**misleading tool description**  *(also: tool description steering)*
*tools and integration · core · chapters 8 · kind: failure mode*

> If a host places a tool description in Claude's context, it is more text competing for influence there, and a misleading description can steer which tool gets chosen before any runtime check runs.
> — *the book, Ch 8 line 99*

In plain words: A tool description placed in Claude's context is just more text, so a misleading one can push Claude toward the wrong tool before any runtime check happens.

Example: A defective or malicious server could advertise a harmless purpose and do something else.

**returned content is untrusted data**  *(also: untrusted data)*
*tools and integration · core · chapters 8 · kind: concept*

> And the content stays untrusted data. A successful response containing text does not make the text correct.
> — *the book, Ch 8 line 115*

In plain words: Text a tool returns is just data; a successful reply does not make it true, and it should not be treated as an instruction.

Example: Host to Claude's context: the text is data to cite with its role, not an instruction and not a current fact.

**tools/list**  *(also: tool listing; discovery)*
*tools and integration · core · chapters 8 · kind: protocol or tool*

> After readiness, a tools/list request returns one tool description. Its name is lookup. Its description says it reads a public course fixture.
> — *the book, Ch 8 line 82; explained across several passages, no single defining sentence*

In plain words: The request a client sends once the server is ready to ask which tools exist and what they accept; before that, it is rejected as too early.

Example: Before initialization it returns an error; after readiness it returns one tool, lookup.

**readiness**  *(also: ready)*
*tools and integration · core · chapters 8 · kind: concept*

> The design choice is to make readiness a statement by the client and a precondition for the server, instead of inferring it from the fact that a process exists or that a tool list could be built.
> — *the book, Ch 8 line 47; explained across several passages, no single defining sentence*

In plain words: The state where the server will do tool work. It is set only when the client says so with the initialized notification, not guessed from the server simply running.

Example: Initialization and readiness are distinct protocol states: tools/list fails after initialize and before the notification.

Not to be confused with: initialization

**state machine**
*tools and integration · core · chapters 8 · kind: concept*

> Before any code, decide when the server is allowed to do anything. The protocol's answer is a sequence, and a sequence is a state machine.
> — *the book, Ch 8 line 34; explained across several passages, no single defining sentence*

In plain words: A system that is always in one state and moves to another only when a particular message arrives, so what it accepts depends on its history.

Example: Initialize moves the server from (false, false) to (true, false); the notification moves it to (true, true).

**audit view**  *(also: fate of a document; selected, below the cutoff, or zero overlap)*
*tools and integration · core · chapters 7 · kind: technique*

> Notice what the function does not return: the documents it dropped, and why. A list of winners gives you the same view the final prose does, one stage earlier. To see an omission you have to compute it, which is why the gate below asks for an audit view listing every document with its score and its fate: selected, below the cutoff, or zero overlap.
> — *the book, Ch 7 line 154; explained across several passages, no single defining sentence*

In plain words: A listing of every document with its score and one of three fates: selected, below the cutoff, or zero overlap. It lets you see what the ranking left out instead of only the winners.

Example: A top-k omission recorded as an audit row with its score and fate.

Not to be confused with: the list of winners

**expected-source list**  *(also: the expected sources; list of sources you expect the task to need; dated list)*
*tools and integration · core · chapters 7 · kind: technique*

> Before you ingest anything, write the list of sources you expect the task to need: title or identifier, owner, version or date, why each is authorized, and the number of items you expect the corpus to hold. Date it.
> — *the book, Ch 7 line 202; explained across several passages, no single defining sentence*

In plain words: A dated list you write yourself, before ingesting and before asking Claude, of the sources the task should need, with owners, versions, authorization and expected item count. You compare it with what was found, and the gap is the learning.

Example: A source you expected and did not find, or one you found and had not expected.

**tool_use block**  *(also: tool-use block; tool request)*
*tools and integration · core · chapters 11 · kind: component*

> A response may contain multiple content blocks. The results function walks the blocks and acts only on those whose type is tool_use. For each tool request it requires a nonempty string identifier that has not already appeared in that content batch.
> — *the book, Ch 11 line 134; explained across several passages, no single defining sentence*

In plain words: A tool_use block is the part of the model's response that asks for a tool; it carries a type, an id, a name and an input. The application acts only on blocks of this type.

Example: {type: tool_use, id: sum-1, name: add, input: {a: 17, b: 25}}

**cosine similarity**  *(also: cosine; normalized dot product)*
*tools and integration · core · chapters 7 · kind: metric*

> Cosine similarity divides the dot product by both lengths:
> — *the book, Ch 7 line 88; explained across several passages, no single defining sentence*

In plain words: A score for how much two count vectors overlap: the dot product divided by the two vector lengths. It is never negative, is one for the same direction whatever the lengths, and is zero when there is no shared token.

Example: “office hours” against “office hours appointment” scores 2 / sqrt(6), about 0.8165.

Not to be confused with: relevance or support (a high cosine does not show a passage supports a claim)

**tool description**  *(also: tool listing entry)*
*tools and integration · core · chapters 8 · kind: component*

> A host uses this to build a request, and in some integration designs a model or a user uses it to decide whether the tool is worth calling. It is server-supplied text about the server.
> — *the book, Ch 8 line 97; explained across several passages, no single defining sentence*

In plain words: The name, description and input schema a server lists for a tool. A host uses it to build requests and a model may use it to decide whether to call the tool, but it is only the server's own text.

Example: name lookup, description Read a public course fixture.

**initialized notification**  *(also: notifications/initialized)*
*tools and integration · core · chapters 8 · kind: protocol or tool*

> Why two steps? The request and response let client and server exchange protocol information, and the notification lets the client say it has finished that phase.
> — *the book, Ch 8 line 47; explained across several passages, no single defining sentence*

In plain words: A follow-up message from the client, with no id and no reply, saying it has finished the initialize phase; it is what makes the server ready for tool operations.

Example: A valid initialized notification returns no response but changes ready to true.

Not to be confused with: initialize request

**initialize request**  *(also: initialize exchange; initialization)*
*tools and integration · core · chapters 8 · kind: protocol or tool*

> A valid initialize request sets initialized to true and returns server information and capabilities.
> — *the book, Ch 8 line 45; explained across several passages, no single defining sentence*

In plain words: The first message in the lifecycle: the client introduces itself, and the server answers with its protocol version, capabilities and name and marks itself initialized.

Example: The recorded initialize request returns protocol version 2025-11-25.

Not to be confused with: initialized notification

**synonym miss**  *(also: paraphrase miss; tuition refund versus fee reimbursement)*
*tools and integration · core · chapters 7 · kind: failure mode*

> Now change the query to “tuition refund” and put the phrase “fee reimbursement” in the only relevant document. A human reader can see the relationship. The retriever returns nothing because its representation sees no shared token.
> — *the book, Ch 7 line 4; explained across several passages, no single defining sentence*

In plain words: The retriever fails to return a document that means the same thing as the query because the two use different words, so the count vectors share no token. A person sees the link; the scorer does not.

Example: Query “tuition refund” and a document about “fee reimbursement” score zero.

Not to be confused with: zero overlap meaning absent from the corpus

**top-k**  *(also: k; cutoff; top-k selection)*
*tools and integration · core · chapters 7 · kind: technique*

> Top-k introduces an exclusion even among positive matches. With k one, only the first ranked candidate remains, and a second relevant document can be omitted because another score is larger or because the tie-break key comes later. The returned list is selected candidates under a particular scoring and cutoff rule, not all available evidence.
> — *the book, Ch 7 line 150; explained across several passages, no single defining sentence*

In plain words: Keeping only the k highest-ranked documents drops some positive matches. The returned list is a selection under one rule, not all the evidence.

Example: With k = 1, a second relevant document is omitted.

Not to be confused with: zero overlap (a different reason for omission)

**tool_result block**  *(also: tool result; results function)*
*tools and integration · core · chapters 11 · kind: component*

> Then it returns a block whose tool_use_id repeats the request identifier.
> — *the book, Ch 11 line 134; explained across several passages, no single defining sentence*

In plain words: A tool_result block is what the application sends back for each request: it repeats the request's identifier and carries the content, or an error flag. It is appended in the next user-role message.

Example: {type: tool_result, tool_use_id: sum-1, content: "42"}

**ranking turns scores into omissions**  *(also: retrieve function; ranking as a policy about what to leave out)*
*tools and integration · core · chapters 7 · kind: concept*

> Claude receives what `retrieve` returns and nothing else, so read the function as a policy about what to leave out. It scores every declared document, removes nonpositive scores, sorts the remainder, and takes at most k rows:
> — *the book, Ch 7 line 131; explained across several passages, no single defining sentence*

In plain words: The retriever scores every document, drops the nonpositive ones, sorts, and keeps at most k, and Claude sees only what survives. So the function is really a rule for which documents get left out.

Example: retrieve(query, documents, k=2)

**context selection**  *(also: selection into context; selection into context (stage); context engineering decision)*
*tools and integration · core · chapters 7 · kind: concept*

> More text can include the missing evidence, but it can also contain contradictions, irrelevant material, and more content than a bounded task should expose. Context selection is an engineering and data-governance decision. The goal is sufficient, authorized evidence with an inspectable selection path.
> — *the book, Ch 7 line 180; explained across several passages, no single defining sentence*

In plain words: Choosing which passages Claude is actually shown, rather than handing over the whole corpus. The aim is enough authorized evidence with a path you can inspect, not the largest possible context.

Example: The corpus holds twenty items, the retriever returns two, and the interface receives one after another filter.

Not to be confused with: supplying the entire corpus

**a name is a request for a destination**  *(also: judge the place, not the string; spelling versus destination)*
*tools and integration · core · chapters 5 · kind: concept*

> Before you can write the policy, decide what it judges: the string someone typed, or the place that string leads. This policy judges the place.
> — *the book, Ch 5 line 40; explained across several passages, no single defining sentence*

In plain words: A permission check should look at where a requested name actually ends up in the filesystem, not at how the name is spelled. Two names that look different can lead to the same place, and a local-looking name can lead outside.

Example: notes.txt, ../notes.txt, and a link inside the folder are all just strings; only the resolved destination says whether each is inside the root.

Not to be confused with: the name being inside the folder (versus the resolved target being inside it)

**containment by string prefix**  *(also: string-prefix similarity; sibling-prefix; shared prefix)*
*tools and integration · core · chapters 5 · kind: failure mode*

> Imagine two sibling directories under a disposable parent: course and course-other. A target inside course-other must not be accepted under a policy allowing only course. A string test that asks whether the target starts with the text naming course confuses the two.
> — *the book, Ch 5 line 113; explained across several passages, no single defining sentence*

In plain words: A wrong containment test that checks whether the target's text starts with the root's text, so it wrongly accepts a sibling folder like course-other for the root course. The right test compares resolved paths.

Example: course versus course-other.

Not to be confused with: containment (a relation between resolved paths)

**seven narrowing stages**  *(also: chain of omissions; what reaches Claude)*
*tools and integration · core · chapters 7 · kind: framework*

> When Claude answers from your sources, the answer was shaped by seven narrowing stages. You made, delegated, or never noticed each one.
> — *the book, Ch 7 line 28; explained across several passages, no single defining sentence*

In plain words: The path from documents to a sentence in a report passes through seven stages: eligibility, ingestion, representation, scoring and cutoff, selection into context, use, and claim. Each narrows what can reach the answer, and most leave nothing visible in the prose.

Example: Eligibility, ingestion, representation, scoring and cutoff, selection into context, use, claim.

**validate tool names and arguments in Python**  *(also: resolve paths before action)*
*tools and integration · core · chapters 15 · kind: technique*

> Validate tool names and arguments in Python, and resolve paths before action.
> — *the book, Ch 15 line 152; explained across several passages, no single defining sentence*

In plain words: Python, not Claude, checks that a requested tool exists, that its arguments are valid, and that a file path stays inside the approved folder before anything runs.

Example: Whether a path stays inside the approved root.

**conducting Claude Code against the gate**  *(also: conduct Claude Code; Claude Code)*
*tools and integration · core · chapters 7 · kind: technique*

> Open Claude Code in your learner workspace. Give it the contract, the test list, and the audit-view specification from your gate, and not your implementation. Ask for an implementation that satisfies the contract and passes your tests, plus the audit view, then run your tests on what it returns, yourself.
> — *the book, Ch 7 line 230; explained across several passages, no single defining sentence*

In plain words: You give Claude Code your written contract, tests and audit-view spec, not your own code, and it implements the retriever. Then you run your own tests on what it returns, compare it with your baseline and note where it differs.

Example: Run your tests yourself on Claude's implementation and note which of them failed.

**zero score versus absence from the corpus**  *(also: zero overlap; no overlap versus absence)*
*tools and integration · core · chapters 7 · kind: failure mode*

> Do not report zero score as proof of irrelevance. It means no counted token overlap under this representation. The relevant source might be absent from the corpus, present but phrased differently, or present with text the tokenizer represents poorly.
> — *the book, Ch 7 line 152; explained across several passages, no single defining sentence*

In plain words: A score of zero only says no counted word is shared under this representation. The source could be missing, worded differently, or poorly tokenized, and each calls for a different repair.

Example: “tuition refund” versus “fee reimbursement” scores zero though they are related.

Not to be confused with: irrelevance

**representation (stage)**  *(also: vectorizer; what counts as the same)*
*tools and integration · core · chapters 7 · kind: concept*

> The first decision is what counts as the same. Before any ranking, someone chooses which features of a text survive into the thing being compared, and everything the representation drops is invisible to every later stage.
> — *the book, Ch 7 line 50; explained across several passages, no single defining sentence*

In plain words: The choice of which features of a text are kept for comparison, which sets what can match at all. Whatever it drops, such as word order or synonyms, no later stage can recover.

Example: Count vectors keep frequency but drop order, so “hours office” and “office hours” match exactly.

**server self-description**  *(also: a description is a sentence the server wrote about itself; testimony)*
*tools and integration · core · chapters 8 · kind: concept*

> Claude, handed only the listing, has two descriptions to compare, and a description is a sentence the server wrote about itself.
> — *the book, Ch 8 line 6; explained across several passages, no single defining sentence*

In plain words: What a server says about itself in its listing is only its own claim, so it cannot show how the server really behaves or whether it belongs in the task.

Example: The listing says lookup reads a public course fixture, but that sentence was written by the server.

**protocol-level error**  *(also: JSON-RPC error; error with a code; request-validation failure)*
*tools and integration · core · chapters 8 · kind: concept*

> A tool-level negative is a result with isError. A protocol-level problem is an error with a code.
> — *the book, Ch 8 line 185; explained across several passages, no single defining sentence*

In plain words: A reply carrying an error code because the message itself was wrong or came at the wrong time, so the tool never produced a content result.

Example: An unknown tool name or a missing, extra or non-string key argument gives code -32602.

Not to be confused with: tool-level error (isError)

# evaluation and validation (27)

**check**
*evaluation and validation · core · chapters 1, 3, 5, 6, 8, 10, 11, 14 · kind: concept*

> A fluent sentence establishes nothing. Only a check that fails differently from the thing it checks can say no to it.
> — *the book, Ch 11 line 40*

In plain words: Check is the second human job: testing what comes back with something that can disagree with it. A matching identifier or a finished status does not do this.

Example: A matching identifier establishes who asked; a finished status establishes that the controller saw a stop signal.

**target**
*evaluation and validation · core · chapters 3, 6 · kind: component*

> A target: what should the verification hunt for ("check the whole thing" is not a target)?
> — *the book, Ch 6 line 154*

In plain words: What the verification should hunt for; 'check the whole thing' is not a target.

Example: Behavior at an input other than two.

**approval**  *(also: human approval; pending status)*
*evaluation and validation · core · chapters 5, 10 · kind: concept*

> Item six is not Claude's to fill. Approval is a person's act, and a sentence from Claude saying "approved" records nothing.
> — *the book, Ch 10 line 254; explained across several passages, no single defining sentence*

In plain words: Approving a plan is something only a named person can do, with a date; Claude writing approved records nothing. With no approval the status is pending and nothing consequential runs.

**re-engagement trigger**
*evaluation and validation · core · chapters 12, 13 · kind: concept*

> An unexpected outcome, harmless or not, should change the next evaluation set before another approval is requested. That is the re-engagement trigger from Chapter 12 applied to the gate itself: the design is not frozen at approval time.
> — *the book, Ch 13 line 264*

In plain words: An unexpected outcome should change the next evaluation set before another approval is requested, so the gate's design is not frozen at approval time. The chapter takes the idea from Chapter 12.

**the sign-off**  *(also: sign-off; check device)*
*evaluation and validation · core · chapters 15 · kind: concept*

> The graph's residual-gap column, the Gap Account, and the handoff exclusions all feed one short statement, the last thing the audit-note says. Claude can write the words of a sign-off fluently, and they will be empty: the part that matters, what was not tested, is the part a model has no record of. Write it from your record.
> — *the book, Ch 15 line 256; explained across several passages, no single defining sentence*

In plain words: A short closing statement that says what was checked, how, what was not checked, what is not claimed and who cleared it. Write it from your own record, because the untested part is what Claude has no record of.

Example: Template fields: Checked, How, Not checked, Not claiming, Cleared by, Verbs, Signed or withheld.

**outcome check**  *(also: outcome evaluation; outcome checker; judging the result)*
*evaluation and validation · core · chapters 4, 13 · kind: component*

> For the question the task asks, the finished answer must equal the value in the records for the key the task names. This check reads the records, not the trace, and it never changes the controller's status.
> — *the book, Ch 4 line 169; explained across several passages, no single defining sentence*

In plain words: A separate check, outside the controller, that decides whether a finished answer is actually right; here it compares the answer with the record for the key the task names. This is the third job of the loop, which the reference implementation does not contain.

Example: Comparing the finished answer red with the record value blue and reporting a mismatch.

Not to be confused with: the controller's status

**accept, revise, or reject**  *(also: review outcomes)*
*evaluation and validation · core · chapters 6 · kind: concept*

> These labels are human review outcomes, not values the AI should invent on behalf of a person. Claude can summarize evidence, challenge a rationale, and propose a recommendation. The responsible reviewer owns the decision where the workflow assigns that responsibility.
> — *the book, Ch 6 line 187*

In plain words: The three possible outcomes of a review, chosen by the responsible person from the evidence on a specific proposal. Claude may summarize the evidence and recommend, but does not decide.

**one-object-at-a-time test**  *(also: one-object test; intervention on your own system)*
*evaluation and validation · core · chapters 9 · kind: technique*

> The test that separates the cases is an intervention on your own system: change one object and hold the rest fixed. In the toy, set w and b back to zero and the learned boundary is gone, whatever else you did. For a Claude interaction, remove the saved text and run the same input again; if the behavior goes with it, the text was holding it.
> — *the book, Ch 9 line 50*

In plain words: Change one object, hold the rest fixed, and watch what follows. If the behavior goes away when you remove the saved text, the text was holding it.

Example: Prepare a baseline prompt, a few-shot prompt, and a retrieved-context condition on the same bounded task, changing only one object.

Not to be confused with: asking what correlates with the improvement

**what did the green test actually test, who decided that, and when?**  *(also: the chapter's question)*
*evaluation and validation · core · chapters 6 · kind: concept*

> So the question for this chapter is not "what are the steps of a code review?" It is: what did the green test actually test, who decided that, and when?
> — *the book, Ch 6 line 8*

In plain words: The chapter's central review question: not the steps of a code review but what the passing test really tested, who chose that, and when. A recipe can be followed in full and the claim can still fail.

Example: The defect was reproduced, a test passed and the diff was small, yet the patch returns the constant three.

**approval drift**  *(also: content drift; authorization drift)*
*evaluation and validation · core · chapters 13 · kind: failure mode*

> If the system retained only a generic yes, the old decision can now be presented as permission for an action she never saw. Every step of the recipe was followed: there was a button, a name, a timestamp. The authorization had still drifted away from its object.
> — *the book, Ch 13 line 5*

In plain words: An approval can stay on file after the thing it approved has changed, so the old yes gets shown as permission for an action the reviewer never saw. Every step (a button, a name, a timestamp) can be followed and the authorization has still drifted from its object.

Example: A reviewer approves writing report.md; later the target becomes elsewhere and the old decision is still presented as permission.

**machine gate**
*evaluation and validation · core · chapters 14 · kind: concept*

> There are two gates in this chapter, and they fail differently. The validator is a machine gate: its pass condition is a list of tests you can run.
> — *the book, Ch 14 line 37*

In plain words: A gate whose pass condition is a list of tests you can run; here, the validator. It is evidence only for the structural checks.

Not to be confused with: human gate

**a prediction has to forbid something**  *(also: specific prediction)*
*evaluation and validation · core · chapters 15 · kind: concept*

> A prediction has to forbid something. “The review will find weak integration” can be matched by anything, so it teaches nothing.
> — *the book, Ch 15 line 197*

In plain words: A useful prediction names something specific that could turn out wrong. A vague prediction that any outcome can satisfy teaches nothing.

Example: The gate's rollback claim ignores an external message (specific) versus 'the review will find weak integration' (vague).

Not to be confused with: vague prediction

**structure versus substance**
*evaluation and validation · core · chapters 15 · kind: concept*

> It is the validator revealing its honest job. Structure can be checked mechanically. Substance must be established through connected evidence and accountable judgment.
> — *the book, Ch 15 line 7*

In plain words: A machine can check that the right files exist and are long enough (structure). Whether the work is true, relevant and trustworthy (substance) needs connected evidence and a person who is accountable.

Example: An empty folder reports ten missing artifacts, and ten meaningless long-enough files pass.

**obligation**  *(also: what a pass covers)*
*evaluation and validation · core · chapters 2 · kind: concept*

> You can look at the validator and name the job of every condition. Parsing, object shape, exact keys, answer type, nonblank content, source-list type, nonempty membership, and allowed identifiers are separate obligations, and you can say which of them the lesson's tests defend and which they leave open.
> — *the book, Ch 2 line 308; explained across several passages, no single defining sentence*

In plain words: A separate thing a response must satisfy, such as parsing, shape, exact keys, answer type, nonblank content or known identifiers. When the validator says passed, you should be able to list exactly which obligations that pass covers and which it never faced.

Example: The red answer passes every implemented obligation but was never checked against the source sentence.

**source identifier**  *(also: address; allowed identifier set)*
*evaluation and validation · core · chapters 2 · kind: concept*

> It does not receive the source sentence. That design lets it reject an invented address such as missing, but it cannot decide whether the words attached to s1 support the answer. Membership in a registry and support for a proposition are different relations.
> — *the book, Ch 2 line 110; explained across several passages, no single defining sentence*

In plain words: A label such as s1 that points to a supplied source. The validator can tell whether the label belongs to the supplied set, but not whether the text behind it backs up the answer.

Example: source_text = {"s1": "The color is blue."}; the validator receives only {"s1"}.

Not to be confused with: source support (membership is not support)

**source support**
*evaluation and validation · core · chapters 2 · kind: concept*

> Does the referenced source exist in the supplied collection? Does that source support this particular claim? Passing the first makes the second possible; it does not answer it.
> — *the book, Ch 2 line 122; explained across several passages, no single defining sentence*

In plain words: Whether the words in the cited source actually back the claim made. It is a separate question from whether the cited source exists in the supplied collection.

Example: An address can point to a real document while the accompanying summary misstates it.

Not to be confused with: source membership (the identifier is in the supplied set)

**content binding**
*evaluation and validation · core · chapters 13 · kind: concept*

> The decision matches the original proposal. Change the target and the same decision no longer matches. This demonstrates content binding.
> — *the book, Ch 13 line 7; explained across several passages, no single defining sentence*

In plain words: Tying a recorded decision to the exact content of one proposal, so that if the content changes the old decision no longer matches. It does not show who approved, their authority, or that the proposal is safe.

Example: Changing the target from report.md to elsewhere makes the original decision fail to match.

Not to be confused with: a real person's consent, the approver's identity or authority

**six-field proposal**  *(also: approval request; reference proposal)*
*evaluation and validation · core · chapters 13 · kind: framework*

> The fields are a minimum teaching contract, not a universal governance schema. Each exists because a reviewer cannot decide without it.
> — *the book, Ch 13 line 48; explained across several passages, no single defining sentence*

In plain words: An approval request that must name six things: the action, the target, the reason, the effects, the evidence and the rollback. Each is there because a reviewer cannot decide without it.

Example: {action: write, target: report.md, reason: deliver draft, effects: one local file, evidence: source checks passed, rollback: restore previous file}

Not to be confused with: a generic 'Allow?' prompt

**test before the patch**  *(also: provenance)*
*evaluation and validation · core · chapters 6 · kind: technique*

> Write the regression test before the proposed fix. The reason is provenance. A test written after you have seen the patch is shaped by it: you check the cases the patch handles and take the expected values from what it returns.
> — *the book, Ch 6 line 32; explained across several passages, no single defining sentence*

In plain words: Write the regression test yourself, from the rule, before any patch exists, so the patch is what is on trial. The chapter's reason is provenance: where the test's expected values came from.

Example: A file timestamp or commit showing the test was saved before the plan.

Not to be confused with: retrospective blessing

**plausibility audit**
*evaluation and validation · core · chapters 6 · kind: technique*

> The audit consults none. It runs on your own model of how the thing should behave, and it decides two things: whether a source needs consulting at all, and what the verification should look for.
> — *the book, Ch 6 line 152; explained across several passages, no single defining sentence*

In plain words: A step between reading the diff and running the check that uses only your own model of how the thing should behave, without consulting a source. It decides whether a source needs consulting and what verification should look for.

Example: A function specified as input plus one whose body is return 3 looks suspect.

Not to be confused with: verification

**format validity versus source support**  *(also: known citation does not entail support)*
*evaluation and validation · core · chapters 2 · kind: concept*

> The validator is not broken. It succeeds at enforcing its stated structural and identifier contract. It fails only if someone misrepresents that contract as a complete evidence check.
> — *the book, Ch 2 line 120; explained across several passages, no single defining sentence*

In plain words: An answer can be correctly formatted and cite a real source while still contradicting it, because format and support are independent. The validator is fine as long as nobody reports its pass as an evidence check.

Example: The red answer citing s1 passes every format rule but is contradicted by the sentence.

**relevance versus entailment**  *(also: relevance is not entailment; relevance and support are separate checks; relevant versus supported)*
*evaluation and validation · core · chapters 7 · kind: concept*

> Relevant should refer to a scoring or human topical judgment you can describe. Supported should refer to a claim-evidence relationship you actually inspected. Do not swap them because both sound favorable.
> — *the book, Ch 7 line 335; explained across several passages, no single defining sentence*

In plain words: A passage is relevant when it scores well or is on topic; it is supported only when you have compared it with the specific claim and it backs that claim. A precise score does not turn relevance into support.

Example: A passage says office hours are by appointment, but the answer claims Tuesday at two; the passage is relevant but does not support the time.

Not to be confused with: supported

**review gate**  *(also: the review is the gate; reviewed plan gate)*
*evaluation and validation · core · chapters 10 · kind: concept*

> Two things follow. The plan is worth the most before anything has run: a revision costs a paragraph there and a rollback later. And the review is the gate, because a plan nobody reviewed is a draft however complete its form.
> — *the book, Ch 10 line 40; explained across several passages, no single defining sentence*

In plain words: Nothing changes until a person has reviewed the plan and a stated condition holds. A plan nobody reviewed is only a draft, however complete it looks.

Not to be confused with: a complete form (completeness is not review)

**gate clearance conditions**  *(also: the gate)*
*evaluation and validation · core · chapters 10 · kind: framework*

> This is the chapter's gate, the large version of the one you wrote in Chapter 1. There it was an experiment contract. Here it is the plan for a piece of work, plus the condition that must hold before the plan goes downstream into implementation.
> — *the book, Ch 10 line 204; explained across several passages, no single defining sentence*

In plain words: A plan goes downstream to implementation only when six things hold: an objective chosen from three distinct candidates, empty missing_fields plus cross-field review, an order with evidence and failure routes on state-changing edges, a stop field with owned exits, a counterexample the plan rejects, and a named, dated approval.

**approval contract**  *(also: bounded attempt)*
*evaluation and validation · core · chapters 13 · kind: framework*

> A decision authorizes one bounded attempt if, and only if, all of this holds. The decision is a record whose approved is exactly True. Its approver is a nonblank string (in production, an authenticated identity, which your fixture will not have).
> — *the book, Ch 13 line 209; explained across several passages, no single defining sentence*

In plain words: A decision authorizes one bounded attempt only if approved is exactly True, the approver is a nonblank string, the recorded fingerprint equals a fresh fingerprint of the proposal about to execute, and the deadline has not passed, it has not been revoked and it has not been used. Approval permits a bounded attempt; it does not guarantee the intended result.

Example: One second after the deadline, the decision no longer authorizes the attempt.

**silence, timeout, model confidence and automated score authorize nothing**
*evaluation and validation · core · chapters 13 · kind: concept*

> Absence, silence, a timeout, a model's confidence, and a favorable automated score authorize nothing.
> — *the book, Ch 13 line 209; explained across several passages, no single defining sentence*

In plain words: A missing answer, silence, a timeout, a model's confidence, or a favorable automated score never counts as approval. Only a recorded decision by a person with authority does.

**color fixture**  *(also: the research fixture; the response that is well formed and wrong)*
*evaluation and validation · core · chapters 2 · kind: named result or case*

> Its identifier is s1. A response arrives saying that the fixture says red, and it cites s1. The response passes our validator.
> — *the book, Ch 2 line 4; explained across several passages, no single defining sentence*

In plain words: A source says only 'The color is blue.', yet a response claiming the fixture says red and citing that source still passes the validator. It shows a well-shaped answer with a known citation can contradict its source.

Example: {"answer":"The fixture says red","sources":["s1"]} is accepted although s1 says "The color is blue."

Not to be confused with: a real Claude mistake (the chapter says it is constructed, not a transcript of Claude)

# governance, ethics and risk (13)

**sign-off**  *(also: Signed or withheld)*
*governance, ethics and risk · core · chapters 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 · kind: technique*

> End the register with a statement you could put your name to. Claude can draft its words in seconds, and the draft will be fluent. Write yours from your record.
> — *the book, Ch 14 line 310*

In plain words: A closing statement for the register with Checked, How, Not checked, Not claiming and Signed or withheld lines, written from your own record. It claims no more than your evidence supports.

Example: Not claiming: that the workflow is ethical, consented to, or compliant.

**register**  *(also: governance record; AI-use register; team AI-use register)*
*governance, ethics and risk · core · chapters 14 · kind: concept*

> So the question for this chapter is not whether the register is complete. It is what "complete" is standing in for. When the status turns green, what has been decided, who decided it, and who will answer for it when the system causes harm?
> — *the book, Ch 14 line 7; explained across several passages, no single defining sentence*

In plain words: A record listing the owner, purpose, data, retention, approver, evaluation and incident contact for an AI workflow. It can be complete on paper while nobody has accepted responsibility for the workflow.

Example: owner: "project team"

**governance**
*governance, ethics and risk · core · chapters 14 · kind: concept*

> Governance is not prose wrapped around a technical system. It is the assignment of decisions, evidence, authority, relationships, monitoring, recourse, and response.
> — *the book, Ch 14 line 13*

In plain words: Governance is assigning decisions, evidence, authority, relationships, monitoring, recourse and response to specific people. It is not paragraphs of prose wrapped around a technical system.

**deferral**  *(also: defer; ship, narrow, defer, or stop)*
*governance, ethics and risk · core · chapters 14, 15 · kind: concept*

> Automation is not the default destination of every workflow. Defer when the purpose is contested, affected people have not been consulted, the data boundary is unknown, evaluation cannot observe the consequential outcome, the team lacks incident capacity, or no authorized owner will accept the decision.
> — *the book, Ch 14 line 266; explained across several passages, no single defining sentence*

In plain words: Automation is not the default outcome of every workflow. Defer when the purpose is contested, people were not consulted, the data boundary is unknown, evaluation cannot see the consequential outcome, there is no incident capacity, or no owner will accept the decision.

**human gate**
*governance, ethics and risk · core · chapters 14 · kind: concept*

> The register's content is a human gate: its pass condition is that a named person accepted each role and that the routes work when someone uses them. The validator is evidence for the first gate only.
> — *the book, Ch 14 line 37*

In plain words: A gate whose pass condition is that a named person accepted each role and that the routes work when someone uses them. The validator cannot give evidence for it, and treating it as such is the failure the opening sentence describes.

Not to be confused with: machine gate

**generic risk language**
*governance, ethics and risk · core · chapters 14 · kind: failure mode*

> Generic risk language protects the record from falsification. "There may be bias or privacy concerns" can be pasted into almost any register and tells no one what to do.
> — *the book, Ch 14 line 180*

In plain words: Vague worries such as there may be bias or privacy concerns fit almost any register and tell nobody what to do. Name who can be affected, how, and what happens to them instead.

Example: "There may be bias or privacy concerns"

Not to be confused with: concrete harm

**ready-for-human-review**
*governance, ethics and risk · core · chapters 14 · kind: concept*

> "Ready" means the teaching record cleared these structural checks and contains no flagged class or external-write condition. It does not mean "approved."
> — *the book, Ch 14 line 122; explained across several passages, no single defining sentence*

In plain words: The status returned when the record passes the validator's structural checks and nothing is flagged, so it can go to people for review. It does not mean anyone has reviewed, approved, or consented to it, or that it is compliant.

Example: assess on the demo record returns {"status": "ready-for-human-review", "issues": []}.

Not to be confused with: approval, consent, compliance, ethical acceptability

**five decisions**  *(also: five choices)*
*governance, ethics and risk · core · chapters 14 · kind: framework*

> Five decisions sit under every register, and none of them is a drafting problem.
> — *the book, Ch 14 line 31; explained across several passages, no single defining sentence*

In plain words: Owner, threshold, retention, consultation and recourse are the five decisions under every register. People make them first and the form records them.

Example: A team that fills the form first has produced the shape of a decision, not a decision.

**concrete harm**  *(also: harm mechanism)*
*governance, ethics and risk · core · chapters 14 · kind: concept*

> Concrete harms might include misrepresenting a deadline, exposing a student's attributed work, omitting a required accommodation route, or publishing an unsupported instruction. Each has a person who pays for it and, usually, a different person who could have prevented it.
> — *the book, Ch 14 line 182; explained across several passages, no single defining sentence*

In plain words: A concrete harm names who is affected, how it happens and what the consequence is, such as students planning around a wrong deadline. Each harm has a person who pays for it and usually a different person who could have prevented it.

Example: misrepresenting a deadline

Not to be confused with: generic risk language

**seven required fields**  *(also: FIELDS; owner, purpose, data_classes, retention_days, approver, evaluation, incident_contact)*
*governance, ethics and risk · core · chapters 14 · kind: component*

> The fields are necessary prompts, not sufficient answers.
> — *the book, Ch 14 line 75; explained across several passages, no single defining sentence*

In plain words: The seven fields are owner, purpose, data classes, retention days, approver, evaluation and incident contact. Each opens a governance question, but a filled field is a prompt, not an answer.

Example: purpose: "use AI" does not bound use.

**operational record**  *(also: bounded response; stranger test)*
*governance, ethics and risk · core · chapters 14 · kind: technique*

> This statement names a signal, threshold, owner, response, scope, and recovery condition. It can still be improved (what counts as approved, how quickly review occurs, who handles disagreement), but another person can now test whether the process ran. That is the standard for a threshold: a stranger can tell, from the record, whether it fired.
> — *the book, Ch 14 line 202; explained across several passages, no single defining sentence*

In plain words: A statement specific enough to be tested: it names a signal, threshold, owner, response, scope and recovery condition. The standard is that a stranger can tell from the record whether the threshold fired.

Example: Rewrite "monitor quality and intervene if needed" so the content owner reviews every unsupported-source flag and publication pauses if a deadline claim lacks an approved source identifier.

**structurally complete, operationally hollow**
*governance, ethics and risk · core · chapters 14 · kind: failure mode*

> That sentence is possible because a governance record can be structurally complete and operationally hollow.
> — *the book, Ch 14 line 5; explained across several passages, no single defining sentence*

In plain words: A register can have every field filled while no named person has accepted responsibility, no affected person was consulted, and no threshold triggers a response. The boxes are ticked but nobody is answerable.

Example: The field named owner can contain "project team".

Not to be confused with: a complete register (complete is not the same as responsible)

**output is cheap, verification is not**
*governance, ethics and risk · core · chapters 15 · kind: concept*

> Claude produces such a graph in a minute; checking one edge means opening its target. Output is cheap and verification is not, and a project that does not budget for verification will not get it.
> — *the book, Ch 15 line 236; explained across several passages, no single defining sentence*

In plain words: Claude can draft a whole packet or graph in minutes, but confirming each claim in it still takes human time. So the real cost of a capstone is checking, and it has to be planned for.

Example: Claude produces a claim-to-evidence graph in a minute; checking one edge means opening its target.

# other (6)

**conduct, check, drive**  *(also: three jobs that stay yours)*
*other · core · chapters 1, 2, 4, 7, 12, 13 · kind: framework*

> So three jobs stay with you: decide where it goes before it runs, check what comes back, and sign your name to what you keep. I call them conduct, check, and drive.
> — *the book, Ch 1 line 9*

In plain words: Three jobs stay with the human when Claude does the producing: decide before it runs what the work must do, check what comes back, and sign only what you keep. The book calls them conduct, check, and drive.

Example: Each job has a question and a device: conduct, the gate; check, the sign-off; drive, the driver's seat.

**handoff**  *(also: handoff that survives the author)*
*other · core · chapters 8, 12, 15 · kind: concept*

> A handoff is a seam, and seams are where risk lives. A packet that only its author can run has a gate with one person behind it. A new authorized person should be able to understand the purpose, run the offline path, inspect evidence, identify decision owners, and know what not to do, using only the prerequisites, commands, expected outputs, failure behavior, recovery steps, and open issues you wrote down.
> — *the book, Ch 15 line 244*

In plain words: The point where the packet passes to someone else, which is risky because a packet only its author can run has just one person behind it. A new authorized person should be able to run the offline path and understand the purpose, evidence, owners and limits using only what you wrote.

**the three jobs: conduct, check, drive**  *(also: three jobs that stay with you)*
*other · core · chapters 3, 8 · kind: framework*

> Claude is far better than you at fluent, fast, parallel production, so you do not compete with it there, and three jobs stay with you: you conduct it, you check what comes back, and you drive, because your name goes on the result.
> — *the book, Ch 3 line 10*

In plain words: The book's split of labor: Claude produces, and you keep three jobs: conducting the work, checking what comes back, and driving, because your name goes on the result. In this chapter each job asks one question about an action.

**capstone packet**  *(also: ten artifacts; the packet)*
*other · core · chapters 15 · kind: concept*

> The capstone is one bounded workflow, not ten unrelated documents. Its packet should let another person trace a line from a real need and consenting owner, through data and action boundaries, into a plan, approval gates, implementation, failures, recovery, evidence, and transfer.
> — *the book, Ch 15 line 13; explained across several passages, no single defining sentence*

In plain words: The ten documents a student submits, which must form one traceable argument rather than ten separate files. A person who was not in the room should be able to follow it from the real need to the final decision.

Example: brief, data-boundary, action-surface-map, plan, gates, pre-mortem, evidence, artifact, audit-note, transfer-reflection.

**build, gate, conduct, check, sign**  *(also: the same sequence)*
*other · core · chapters 1 · kind: framework*

> Build the small mechanism. Write the gate. Conduct Claude against it.
> — *the book, Ch 1 line 45; explained across several passages, no single defining sentence*

In plain words: Every chapter runs the same sequence: build the small mechanism, write the gate, conduct Claude against it, check what comes back, and sign only what the record supports.

Example: This chapter: build the sampler by hand, write the gate, give Claude Code the gate, run your tests on what it returns, sign or withhold the sampling report.

**cross-references between artifacts**  *(also: ten islands; the lines between them)*
*other · core · chapters 15 · kind: technique*

> Without those links, ten documents remain ten islands. Claude can add such cross-references in minutes, and a validator cannot check them, so treat each reference as a claim: open the target and confirm it says what the pointer says.
> — *the book, Ch 15 line 128; explained across several passages, no single defining sentence*

In plain words: Each artifact should point to the others it depends on. A pointer is itself a claim, so you open the target and confirm it says what the pointer says.

Example: The brief's success criterion maps to evidence; the data boundary constrains the action map; the plan invokes the gates.

