# Prompt engineering: exam terms, compact list

Built 2026-11-09 from the 15 chapters of INFO 7375, Prompt Engineering for Generative AI (1,310 inventory entries, merged to 1094 terms). Bear is cutting this down himself.

**Focus.** This course is less about validation and more about what agents are, how to prompt, how to be specific and the agentic loop. So Part A is the core terms in those areas (prompting, agents and the agent loop, how models generate, tools and integration). Validation and evaluation come after, as Part B, because some validation belongs. Governance and the rest are last. Supporting and light terms are listed by name at the end.

**Flags.** *book* = the book defines it in one sentence; *spread* = it explains it across passages. "Ch" is the chapters whose inventory names the term.

## Your headline words, and what the book calls them

The chapters mostly do not use the generic words. Exam wording should use the book's words. The table gives the book's version of each headline term and where it lives.

| Your word | What the book calls it |
|---|---|
| **agent** | agent (Ch 3, 4: used as a teaching label, never defined in one sentence); agent loop (Ch 4); controller (Ch 3, 4, 5, 11: the code that runs the loop and owns the stops) |
| **agentic loop** | agent loop (Ch 4); prediction loop (Ch 1, the next-token loop); bounded loop (Ch 4); loop exit (Ch 11); stop condition (Ch 4, 6, 10, 15) |
| **prompt** | prompt (Ch 2, 9: used, undefined); system prompt (Ch 1 defined, also Ch 5, 9); a prompt is a request, not a boundary (Ch 15); a system prompt is a request, not a gate (Ch 8); baseline prompt and prompt revision as a hypothesis (Ch 2); challenger prompt (Ch 14) |
| **a specific prompt, being specific** | complete specification (Ch 1, 2, 3, 10); contract (Ch 1, 2, 4, 11), output contract and write the contract first (Ch 2), role contract (Ch 12), design by contract (Ch 10); the chapters never say specificity |
| **context window** | context (Ch 1, 9); context selection and accountable context (Ch 7); context engineering (Ch 7); the chapters never say context window |
| **temperature** | temperature (Ch 1: defined; Ch 9: named as a setting); lowering temperature is not a truth guarantee (Ch 1); count, seed and temperature as separate controls (Ch 1) |
| **tool call** | tool call (Ch 8, 11); tool use (Ch 11); tools/call, the MCP method (Ch 8); tool-call budget (Ch 4); proposed call (Ch 11); tool error (Ch 8, 11) |
| **human in the loop** | human in the loop (Ch 5, 14); human gate (Ch 14); approval (Ch 5, 10, 13); and above all gate, the book's word in every chapter 1 to 15 |
| **guardrails** | gate (the book's pervasive term: "give Claude the gate, not your implementation"); approval contract (Ch 13); the chapters never say guardrail |
| **plan, planning** | plan, planning before acting, eight plan fields, plan is a proposal, plan-only request (Ch 10); plan before any edit (Ch 6) |
| **memory** | memory (stored state, not recollection) and memory is not permission to act (Ch 12); no memory between conversations (Ch 1) |
| **MCP** | MCP (Ch 7, 8); tools/list and tools/call (Ch 8) |

**The book's own word for all of this is gate.** It appears in every chapter from 1 to 15: you hand Claude the gate (the contract and the checks), not your implementation. That is the "not just code, but gates for the code" idea.

## Where the terms sit, by chapter

| Chapter | Terms | of which core |
|---|---|---|
| 1, Next-token prediction and sampling | 80 | 31 |
| 2, Prompt contracts and evaluation | 76 | 20 |
| 3, Chat, assistant, agent | 77 | 36 |
| 4, The agent loop | 94 | 49 |
| 5, Tools and permissions | 73 | 23 |
| 6, Claude Code and diff review | 90 | 25 |
| 7, Retrieval and Cowork | 89 | 20 |
| 8, MCP from scratch | 92 | 36 |
| 9, Training and configuration | 88 | 22 |
| 10, Planning before acting | 86 | 30 |
| 11, Tool use and verification | 81 | 17 |
| 12, Memory and multiple agents | 86 | 26 |
| 13, Evaluation and approval gates | 90 | 14 |
| 14, Governance and ethics | 96 | 24 |
| 15, Supervised capstone | 112 | 26 |

# Part A: core terms for prompting, agents, the agent loop, models and tools (282)

## prompting (65)

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **gate** | 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 | A written specification of the stop conditions made before any implementation: every exit, the unit of the budget, what must never be fabricated, and… | book |
| **contract** | 1, 2, 4, 11 | The rules fixed before the run: no exit invents an answer, a finish only means a request to stop arrived, and the budget and status are reported with… | book |
| **complete specification** | 1, 2, 3, 10 | Claude builds well from a thorough statement of the work and poorly from a thin one, and it will not warn you which you gave it. | book |
| **context** | 1, 9 | Whatever documents, passages, or records are put into the model's input for this turn. | book |
| **prompt** | 2, 9 | The instruction text and examples you give the model as input; it lives in a file or message you can compare, copy, and revert. | book |
| **system prompt** | 1, 5, 9 | A paragraph near the top of the text the model continues, which asks for behavior but competes for influence with every other paragraph. | book |
| **roles** | 1 | System, User and Assistant labels are just text inside the document the machine is completing, not modes the software switches into. | book |
| **give Claude the gate, not your implementation** | 4, 14 | Give Claude the contract and your test list, not your own code, and then run your tests on what it returns. | book |
| **brief** | 15 | The first artifact: it records the real need, the consenting owner, who is affected, what success looks like, what the workflow is not for, and when… | *spread* |
| **refusals** | 1 | Input checks that make a function reject invalid input instead of inventing a result. | book |
| **reproduction** | 6 | The smallest legitimate case that shows the gap between intended and current behavior, with a named input, expected result and observed result. | book |
| **contract (part of the gate)** | 6, 15 | The part of the gate that says what the workflow must do and what it must refuse, plus the observable state that means done and the conditions that m… | *spread* |
| **persona** | 2 | A role line such as 'You are an expert' is a part of the prompt to be tested, not a guarantee. | book |
| **non-purpose** | 15 | A written statement of what the workflow is not for. | book |
| **output contract** | 2 | What the prompt says the answer must look like (here a JSON object with answer and sources), alongside the intention that the answer rest on the sour… | book |
| **exit table** | 4 | A table written before any code listing each reason the run ends, with its status, its answer and its trace, and who decided each line. | book |
| **a system prompt is a request, not a gate** | 8 | Text in a system prompt asks Claude to behave a certain way but does not force it, and tool descriptions in context work the same way. | book |
| **role contract** | 12 | A written spec of what one worker may do, naming its inputs, task, tools, output, budget and where it escalates. | book |
| **few-shot examples** | 9 | Examples placed in the input that show the model a pattern for the current interaction. | book |
| **acceptance statement** | 3 | A statement of what counts as done that says both what the system must do and what it must not touch. | book |
| **state the rule in plain language** | 6 | Write the intended behavior in plain words and pick at least two inputs with their expected outputs before you see any patch. | book |
| **give Claude Code the gate** | 6 | Put your issue, reproduction, failing regression test and allowed-file list where Claude Code can read them, and do not hand it your implementation. | book |
| **invalid requirement** | 6 | Testing cannot repair an invalid requirement: a patch can implement the wrong rule perfectly and still be wrong. | book |
| **contract for the state machine** | 8 | A short written spec of the rules the server must obey, which you give to Claude and use as the basis for your tests. | book |
| **design by contract** | 10 | The human writes the contract, the agent writes the implementation, and assertions or tests derived from the contract check it. | book |
| **a field that has a job** | 10 | A plan field is useful only if its entry is concrete enough that a person can disagree with it, such as an exact command or named file paths. | book |
| **facts are not instructions** | 12 | Stored facts go into the model's context as quoted claims with their provenance, never into the channel that carries the system's instructions. | book |
| **a prompt is a request, not a boundary** | 15 | Telling Claude not to do something helps as context but does not stop it. | book |
| **recovery by repetition** | 15 | A failure of the check job: rerunning the same prompt until the wanted answer appears, with no reviewed change to the plan or mechanism. | book |
| **constrained output format** | 1 | Asking for a tightly constrained answer leaves fewer high-probability continuations, so repeated answers converge. | book |
| **ask for the boundary case, not the verdict** | 1 | After you have reasoned, ask Claude not whether you are right but for the one assumption your reasoning depends on most and an input that would make… | book |
| **request versus check** | 2 | Asking Claude in the prompt to follow a rule is only a request and can be ignored. | book |
| **hand Claude the contract, not your implementation** | 3 | Give Claude Code your gate, contract and tests, ask for an implementation that meets them, and run the tests yourself. | book |
| **weak bug report** | 6 | A bug report that says only 'the result is wrong' is too weak to guide a bounded change. | book |
| **Design (first part of the gate)** | 6 | The first part of the gate: the rule, the reproduction inputs with expected results, and the allowed files, all chosen by you rather than by a model. | book |
| **specification and audit** | 7 | The two jobs that stay with the human in retrieval: stating exactly what counts as similar, what is eligible and how many results to return, and then… | book |
| **conduct Claude Code with the gate** | 8 | Give Claude Code your table, contract and tests, but not your implementation, ask for a server that meets them, and run your own tests on the result. | book |
| **state the rule before reading the code** | 8 | Decide and write down the rule you want first, then check the code against it, instead of letting the code teach you what the rule is. | book |
| **a failing test is a gap in your gate** | 9 | When Claude's code fails one of your tests, the gap is often in what you wrote, because Claude had only what you wrote. | book |
| **specification that names the refusals** | 11 | If a specification never mentions a case such as True, whoever implements it has no reason to refuse that case. | book |
| **a failed test as a gap in the gate** | 12 | When Claude's output fails one of your tests, the cause is often something missing from your gate, because Claude had only what you wrote. | book |
| **operational control** | 12 | A control specific enough to implement and test, with a trigger, an owner, evidence, a response and a recovery condition. | book |
| **action (proposal field)** | 13 | The proposal field that says what operation will occur, worded specifically enough to review. | book |
| **challenger prompt** | 14 | A prompt that forbids rewriting and asks for four specific lists: fields naming a group or role instead of a person, thresholds with no observable si… | book |
| **consumer** | 2 | The program that reads Claude's answer and does something with it; what it needs is the first thing you decide, before any prompt. | *spread* |
| **task packet** | 7 | The bounded brief you hand to Claude Cowork: what the goal is, which sources it may use, what output you want, what is excluded, how you will check i… | *spread* |
| **baseline prompt** | 2 | The starting prompt, derived from the contract, against which later revisions are compared. | *spread* |
| **testable condition** | 10 | A condition is testable when someone who did not build the pipeline can read it, observe the system and decide whether it holds. | *spread* |
| **source boundary** | 2 | The limit that the answer must rest on the supplied source material only, which is stated in the prompt and recorded with the experiment. | *spread* |
| **few-shot revision** | 2 | A revised prompt that adds examples to the baseline, compared against the baseline on the same development questions. | *spread* |
| **write the contract first** | 2 | Write down what the consuming program needs before you try a prompt, so the criterion exists before any output does. | *spread* |
| **"fix this report" hides four requests** | 3 | A vague request like fix this report could mean explain what is wrong, propose a replacement, save a new version, or alter the original. | *spread* |
| **the contract for the code** | 3 | The contract is a short list of exact behaviors the code must have, written before anyone implements it. | *spread* |
| **connection gate** | 8 | A written plan you make before connecting a server: your predicted lifecycle table plus the four ledgers, with who decided each item. | *spread* |
| **write the gate before Claude implements it** | 13 | Before asking Claude for any code, write the gate yourself in plain sentences and test names, saying who decided each item and where Claude proposed… | *spread* |
| **success as an observable state** | 15 | Define success as something you can look at and check in the resulting state, not as a statement that the agent finished. | *spread* |
| **prompt revision as a hypothesis** | 2 | Treat a changed prompt as a testable guess: name the specific failure you expect the change to fix, then test it on a fixed evaluation set. | *spread* |
| **the requirement comes first, from you** | 6 | The rule the code must satisfy has to be written down first, by you, so a proposed implementation cannot redefine the problem you meant to solve. | *spread* |
| **retriever contract** | 7 | The exact behaviors the retriever must have, written before it is built: score ranges, ordering, tie rules, the k limit, rejection of bad k, and an a… | *spread* |
| **ask for discrepancies, not a verdict** | 8 | Prompt Claude to list every place where the transcript, source and description disagree, quoting the line it used, and tell it not to say whether to… | *spread* |
| **conduct Claude Code against your gate (Use It)** | 9 | Give Claude Code your gate (the change, objective, held-out list, stop rule, and test list) but not your implementation, then run your own tests on w… | *spread* |
| **three conditions (baseline, few-shot, retrieved context)** | 9 | Compare a baseline prompt, a few-shot prompt, and a retrieved-context condition on the same bounded task, changing only one object between conditions… | *spread* |
| **plan-only request** | 10 | To get a plan from Claude Code, give it the bounded objective and the exclusions, ask for the eight fields, and tell it explicitly to change no file… | *spread* |
| **resolved identity** | 13 | A concrete name for what an action touches (a resolved path, account, immutable version or object hash) instead of a friendly display name. | *spread* |
| **Claude as challenger, not author** | 14 | Instead of letting Claude rewrite your entry, ask it only to find the weak lines, and verify each finding yourself against the text. | *spread* |

## agents and the agent loop (142)

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **drive** | 1, 3, 4, 5, 6, 8, 9, 10, 11, 14 | Keep the decision about who authorized an action with a person, and split the work between you and Claude on purpose. | book |
| **conduct** | 1, 3, 5, 6, 8, 10, 11, 14 | Decide how much freedom the task needs before you give the system any ability, and write that decision down as the gate. | book |
| **controller** | 3, 4, 5, 11 | A controller takes the current state, picks an action, runs it, looks at the result and decides whether to keep going. | book |
| **the driver's seat** | 2, 7, 8, 12, 15 | The division of work between you and Claude: Claude does the coordination, fast implementation and parallel work, while you keep the initial judgment… | *spread* |
| **trace** | 3, 4, 15 | The list the controller builds as it runs, with one record for each completed non-finish turn holding its turn number, action name and observation. | book |
| **stop condition** | 4, 6, 10, 15 | The condition the patch must meet before it moves downstream: the test saved before the plan, the plan naming only allowed files, and the test and ex… | book |
| **capability versus authority** | 4, 8, 11, 15 | What a server says it can do (capability) is separate from whether a task is allowed to use it (authority); the protocol carries the first and a pers… | book |
| **authorization** | 3, 8, 13 | The decision about whether a particular capability should be allowed to run for this task; the protocol syntax cannot make it for you. | book |
| **action** | 3, 4 | An action is something the system does that outlasts the chat, such as changing a file. | book |
| **finished** | 4, 11 | finished is the controller's exit status when the model's reply ends with end_turn before the request budget runs out. | book |
| **scope** | 6, 10 | The boundary of the work: what is allowed to change and what must be left alone. | book |
| **plan** | 10, 15 | The artifact that lays out the steps that produce evidence, with their dependencies, when to stop, spending limits, and what would force the plan to… | book |
| **handoff condition** | 5, 8, 10 | A condition clear enough that a stranger can read it, observe the system and tell whether it is met. | book |
| **agent** | 3, 4 | In this chapter, agent is the label for the surface that can reason, read and write, so it can change state. | *spread* |
| **permission policy** | 4, 5, 8 | The written rules for what a tool may touch (the root) and what it may do (the allowed operations), decided from what the task needs before any code… | *spread* |
| **capability** | 3 | Capability is what the system is able to do, as written in its capability set. | book |
| **observation** | 4 | What the controller gets back from carrying out an action, such as the value a lookup found; it is stored in the trace. | book |
| **allowlist** | 5, 11 | An allowlist is the fixed list of operations the application is willing to run. | book |
| **tool call** | 8, 11 | A tool call is a structured block of data in which Claude names a tool and gives arguments; it is only a proposal. | book |
| **AI should / Human should** | 9, 13, 14 | A split of each task between Claude and a person (the chapter's driver's seat table): AI should prepare the proposal, expose changed fields, assemble… | *spread* |
| **turn budget** | 4, 11 | A turn budget is a cap on how many times the loop may call the model (one through four here), so it cannot continue forever. | book |
| **autonomy** | 2, 3 | Autonomy is not one thing; it hides capability, control and scrutiny. | book |
| **control** | 3 | Control is who or what picks the next step: a fixed program or the model itself. | book |
| **tool error** | 8, 11 | When a proposed call is invalid, the application returns a tool_result flagged is_error with the reason instead of crashing. | book |
| **human in the loop** | 5, 14 | Having a person approve steps is not automatically a safeguard, because when checking is costly the supervisor drifts toward saying yes. | book |
| **terminal state is not correctness** | 3, 4 | A loop can end with a finished status while the final answer is still wrong. | book |
| **three jobs: conduct, check, drive** | 6, 15 | Three things a person does when working with Claude: conduct (decide before Claude builds), check (find what is wrong and sign only what the record s… | book |
| **tool use** | 11 | Tool use means the model proposes a request, your program checks it and runs it, and the result comes back as evidence. | book |
| **lookup** | 4 | One of the two permitted action names: it reads the value for a key from the records and returns it as the observation, or the string not found. | *spread* |
| **policy** | 4 | The part of the loop that proposes the next action; here it is just a prepared list of action dictionaries that the controller reads one at a time. | *spread* |
| **turn** | 4 | One pass of the loop: the controller takes the next action from the policy, dispatches it, records the observation, and checks whether a condition en… | *spread* |
| **state** | 4 | What the loop carries from turn to turn; here it is just the trace, and each turn updates it only by appending a record. | *spread* |
| **version** | 12 | A number on each record that goes up by one each time a write is accepted, so it shows the order of commits for that key. | *spread* |
| **stop reason** | 4, 11 | Why the run ended, which the returned status and the configured budget record and the trace length alone cannot show. | *spread* |
| **grant** | 3 | Giving the system an ability is a decision you make, and writing the grant down as a set lets you inspect it. | book |
| **assistant** | 3 | In the teaching model, assistant is the surface that can reason and read but cannot write. | *spread* |
| **stale write** | 12 | A write whose expected version no longer matches the record's current version is refused with an error and changes nothing, because the worker's prem… | book |
| **agent loop** | 4 | The cycle that drives an agent: something proposes the next action, something carries it out, records the result and decides whether to continue, and… | book |
| **reversibility** | 10 | Whether an action can be undone decides how much human approval it needs: an undoable change needs evidence only, while a write outside the fixture o… | book |
| **planning before acting** | 10 | Write down where the work is going, what it may use and touch, the steps, tools, risks, evidence and stopping rule before Claude acts, so others can… | book |
| **revision boundary** | 12 | The decision about what one version number covers, made before any worker runs. | book |
| **repetition detector** | 4 | A stop rule that notices an unproductive cycle of repeated actions or repeated observations. | book |
| **action boundary** | 2 | The point where a correctly shaped answer could lead a system to read files, write changes or request a tool call. | book |
| **incomplete** | 4 | The status returned when the policy had no next action before the budget was spent. | *spread* |
| **preflight** | 5 | A preflight is a check run before an action that decides whether a proposed action is allowed. | *spread* |
| **bounded edit** | 6 | Permit Claude a limited edit, then read the diff and write the audit record before running anything, then run the targeted regression and existing te… | book |
| **refusal path** | 10 | A route written into the plan for when authority, evidence or checks are missing: the workflow keeps its state and reports what blocks the next step… | book |
| **chain of custody** | 11 | The chain of custody is the sequence a tool request goes through: validated, dispatched, executed, paired with its result, and finally checked as a c… | book |
| **Claude coordinates** | 12 | In the chapter's split of work, Claude's part is to route tasks, compare artifacts, flag conflicts, keep each worker's original output, and summarize… | book |
| **humans deliberate** | 12 | In the chapter's split of work, the human's part is to hold an initial interpretation formed before the synthesis, add local knowledge the notes lack… | book |
| **Claude proposes, Python constrains** | 15 | Claude does the language work, such as drafting, summarizing and proposing a tool call. | book |
| **chat** | 3 | In the teaching model, chat is the surface that can only reason, meaning produce a response, with no reading or writing. | *spread* |
| **sufficient autonomy** | 3 | Choose the amount of autonomy that fits the outcome the task needs; a response-only interface cannot produce a saved file. | book |
| **the model proposes; you authorize** | 3 | The model may propose an action and ask for permission, but only a person can authorize it. | book |
| **before the output moves on** | 4 | The rule for when an answer may be passed on: only if the status is finished and the outcome check passes. | book |
| **authorize** | 5 | The chapter's eleven-line Python function that decides whether a proposed read or write is allowed. | *spread* |
| **plan before any edit** | 6 | Ask Claude for a plan first and check it against the allowed list. | book |
| **discovery is not consent to call** | 8 | Seeing a tool in the listing does not mean it is allowed to run; the host's permission policy decides. | book |
| **capability does not create authority** | 10 | Having a tool that can do something does not mean this task may use it. | book |
| **one step at a time** | 10 | Only after the gate passes, let Claude Code act on the approved plan one step at a time, checking its diff and commands against the stop conditions. | book |
| **optimistic concurrency control** | 12 | Workers read a record and its version, do their work without locking the record, and at write time must hand back the version they read; if the recor… | book |
| **cascade** | 12 | A multi-worker failure pattern in which each worker builds on the previous worker's output, so small error chances compound across the chain. | book |
| **authority laundering** | 12 | A failure pattern in which data passed from one worker to another is treated as legitimate just because of the channel it arrived through, since the… | book |
| **incident state machine** | 12 | A set of states the coordinator tracks for an incident, richer than success and failure: active, challenged, paused, reviewed, superseded, and resume… | book |
| **pause-and-resume harness** | 12 | A small piece of code that, on a stale exception for a key an active task depends on, pauses the task and keeps both proposals. | book |
| **control plane** | 14 | The register is a control plane when it can actually pause execution, revoke approval, shorten retention, change evaluation, assign repair or end the… | book |
| **inspect resulting state, not only trajectory** | 15 | Check what actually ended up true in the world, not just the sequence of steps taken. | book |
| **authority drift** | 15 | A failure of the conduct job: approval for a small, local action is later described as permission for a bigger one, such as publishing. | book |
| **good result vs authorized action** | 3 | Even when an action turns out well, someone still has to decide that the system was allowed to do it. | book |
| **what could, what allowed, what did (the chapter's three questions)** | 3 | Ask three things of any AI system: what it was able to do, what you actually let it do, and what the record shows it did. | book |
| **missing set (R minus C)** | 3 | The missing set is what a task requires that a surface does not declare. | book |
| **proposed, attempted, completed, observed** | 3 | Four stages for a write: offered by the response, requested of the runtime, reported successful by the runtime, and seen by you in the changed state. | book |
| **control-flow layer versus evidence layer** | 4 | A run can be finished at the control-flow layer, meaning the controller returned, and still be contradicted at the evidence layer, meaning the answer… | book |
| **budget chosen before the run** | 4 | A limit decided and written down before the loop starts is built into the controller, while a limit found only after something went wrong is just an… | book |
| **feedback from observation to policy** | 4 | In this reference the policy never sees what the controller observed, so its next action cannot depend on it. | book |
| **policy in the request versus policy in a function** | 5 | A rule can be stated as a sentence in the prompt, or enforced as code that sits between the request and the filesystem and refuses out-of-bounds requ… | book |
| **the scope decision stays with the task owner** | 6 | Claude can say which files it thinks it must touch and why, but whether the task should grow to include a new file depends on context only the owner… | book |
| **stop rule for a fluent guess** | 8 | Nothing in how Claude produces its next word stops it from guessing when a record is missing, so you must write a stop rule into the host or the inst… | book |
| **exit owner** | 10 | Every exit from the work needs someone responsible for it: a test can halt on a failing assertion, but a person must decide whether a new risk change… | book |
| **no identical retry** | 10 | If a check fails again and nothing new has been learned, do not just run it again: diagnose, revise the plan, or defer. | book |
| **Claude proposes, your Python executes** | 11 | Claude suggests the call and explains the trace, while your own code does the exact checking and the arithmetic. | book |
| **tool_use exit** | 11 | When the reply asks for a tool, the loop builds the results, adds the assistant's content and then a user-role message holding the results to the his… | book |
| **inherited mistakes in shared memory** | 12 | When an observation is stored as memory, every later piece of work that reads it inherits it along with any error. | book |
| **memory (stored state, not recollection)** | 12 | In this chapter, memory is a store of records kept in a Python dictionary under keys, outside the model. | book |
| **multiple Claude sessions as parallel workers** | 12 | Several Claude sessions each take a bounded part of a job, for example one extracting source passages and another trying boundary cases, while a coor… | book |
| **responsibility must remain with a person or organization** | 14 | An automated system can stop work safely, but responsibility for the outcome must stay with an authorized person or organization. | book |
| **teaching surface** | 3 | A teaching surface is one of three imaginary interface types (chat, assistant, agent), each defined by an explicit set of capabilities. | *spread* |
| **reason, read, write** | 3 | The three modeled capabilities: reason is producing a response, read is accessing information, and write is changing state. | *spread* |
| **error observation** | 4 | What the controller records when an action's name is neither lookup nor finish: nothing is run, the error is appended to the trace, the turn is consu… | *spread* |
| **reviewed recovery** | 15 | After a failure, a person or a declared policy reviews why it failed and changes the plan, for example by narrowing the claim, choosing another sourc… | *spread* |
| **capability set** | 3 | A capability set lists what a surface is declared able to do. | *spread* |
| **allowed-file list** | 6 | The list of files the patch may change. | *spread* |
| **unit of the budget** | 4 | What one count of the budget stands for, which a person writes down before the run. | *spread* |
| **dependency graph** | 10 | Treat a plan's steps as a graph in which an arrow from one step to another means the second may not be called ready until the first has produced what… | *spread* |
| **action-surface-map** | 15 | The artifact that lists what the workflow is able to read, propose, write, send or publish, and keeps what it can do separate from what it is allowed… | *spread* |
| **the condition that sends control back to you** | 3 | A line in the gate that names when the system must stop and hand the decision back to you. | *spread* |
| **the stop that ends the run** | 4 | The controller returning from the loop, whether because a finish arrived, the policy ran out, or the budget was spent. | *spread* |
| **the stop that closes the task** | 4 | A person, or a check a person designed, accepting the result as meeting the need that started the run. | *spread* |
| **model-backed policy** | 4 | A policy whose next actions come from a model instead of a prepared list. | *spread* |
| **bounded loop** | 4 | Any claim that a loop is bounded must name its unit and assumptions. | *spread* |
| **topological ordering** | 10 | Repeatedly take every step with no unfinished prerequisites, add those to the order sorted by id, and remove them, until the graph is empty. | *spread* |
| **persistent change** | 3 | A persistent change is an edit that is still there after the chat is over, such as a saved file. | *spread* |
| **capability is not authorization** | 3 | Being able to do something, because it is in the capability set, is not the same as having permission to do it. | *spread* |
| **a write is not necessarily dynamic agency** | 3 | Saving a file does not by itself mean the system is directing its own process. | *spread* |
| **stopping is a control-flow event** | 4 | When a loop ends, all that has happened is that the program returned by one of its exit paths, which says nothing about whether the answer is correct. | *spread* |
| **lookup environment** | 4 | The dictionary of records that lookups read from; the controller reads it but never changes it. | *spread* |
| **select the lowest layer that does the job** | 4 | Use the simplest layer that gets the job done, and keep deterministic work out of the model entirely. | *spread* |
| **visible trace** | 4 | What you can see of a real Claude task: requested tool actions, returned output and a final message, which you can map onto actions and observations. | *spread* |
| **iteration count and permission are separate controls** | 4 | Limiting how many turns the loop runs does not limit what a single turn may touch. | *spread* |
| **least privilege** | 5 | Give a tool only the access its task needs and nothing more, because every extra operation is something you must later verify. | *spread* |
| **read and write are different authority questions** | 5 | Whether an operation needs a human approval is a judgment about its consequences. | *spread* |
| **finishing is not succeeding** | 6 | A closing message from Claude Code saying the tests pass is a claim about a run, like checks_passed=True, with no command, output or link to the diff… | *spread* |
| **not-waterfall rule** | 10 | A plan is not frozen: when a result contradicts an assumption, you revise the plan and record why, rather than pushing on. | *spread* |
| **loop exit** | 11 | A loop exit is a way the controller can end or continue, and each is a decision about what the loop may claim. | *spread* |
| **lowest sufficient capability** | 3 | Grant only the abilities the task needs, so that if reading is enough you do not grant writing. | *spread* |
| **predefined workflow vs model-directed process** | 3 | A predefined workflow follows steps written in advance, while a model-directed process lets the model decide its own steps. | *spread* |
| **proposed vs executed** | 3 | Offering to save a file, asking permission, or explaining a command is not the same as doing it. | *spread* |
| **activity versus progress** | 4 | A longer trace only shows that more actions were recorded; it does not show the task is closer to a supported answer. | *spread* |
| **policy exhaustion versus budget exhaustion** | 4 | Policy exhaustion means the actions ran out first, giving incomplete; budget exhaustion means the turns ran out first, giving budget-exhausted. | *spread* |
| **separating the three jobs** | 4 | Keeping the proposer, the controller and the judge as separate parts so each can be debugged and owned on its own. | *spread* |
| **when a loop earns its place** | 4 | Ask first whether the task needs a loop at all. | *spread* |
| **who took each stop** | 4 | For each run, note every point where it stopped and who took that stop: Claude ended its turn, you interrupted, you approved or declined a request, o… | *spread* |
| **three layers of the conclusion** | 4 | Your report should name three layers: the policy supplied an action, the controller stopped under a named rule, and a separate check assessed the ans… | *spread* |
| **a returned path is not a completed operation** | 5 | When authorize hands back a path, that only means the proposal passed the check; nothing was opened, read, written or created. | *spread* |
| **proposal versus grant** | 5 | The model's job is to propose an action; a person or the surrounding process decides whether it is allowed. | *spread* |
| **enforcement in the runtime** | 5 | Rules that must hold are put in code that runs between the request and the action and refuses with an error, so no wording in the request can change… | *spread* |
| **three decisions in authorize** | 5 | authorize makes three separate decisions in order: is the operation allowed, is the resolved target inside the root, and for a write is approval exac… | *spread* |
| **the driver's seat (what Claude does, what you keep)** | 5 | A task-by-task split: Claude lists candidates, drafts approval records, proposes edge cases and writes the function fast, while you choose the smalle… | *spread* |
| **conduct, check, drive (the three jobs)** | 9 | The three jobs a human does when working with Claude: conduct (state what should change, and how you will tell, before you change it), check (claim o… | *spread* |
| **gate items are human decisions** | 9 | The objective, held-out set, and stop rule cannot be derived from the data, because the data have no opinion about what "better" should mean. | *spread* |
| **eight plan fields** | 10 | A plan is checked for eight named parts: objective, inputs, scope, steps, tools, risks, verification, and stop. | *spread* |
| **plan predicts, result records** | 10 | A plan states predictions and a result records what actually happened; they are different documents and should stay apart. | *spread* |
| **plan is a proposal** | 10 | A plan that Claude drafts is only a suggestion until a person has reviewed and approved it. | *spread* |
| **problem formulation** | 10 | Before ordering any steps, decide which problem the plan is for: write candidate formulations that differ in what counts as success, then choose one. | *spread* |
| **division of drafting and deciding** | 10 | Claude may draft the steps and the tools list, but you answer the questions that depend on things no file contains: what the work is for, what may be… | *spread* |
| **initial judgments before synthesis** | 12 | Collect each person's own judgment before anyone sees a synthesis, then discuss with the sources visible and keep the disagreements instead of averag… | *spread* |
| **independence of judgments** | 12 | Two workers are independent only if they would not fail for the same reason. | *spread* |
| **no automatic retry after a stale write** | 12 | When a write is rejected as stale, the worker must not simply reread and retry. | *spread* |
| **AI should, Python should, Human should** | 12 | The chapter's split of responsibilities by task: AI does bounded research and review and surfaces conflicts, Python enforces the expected-version rul… | *spread* |
| **gate sequence (proposal to observed outcome)** | 13 | Eight steps: build a proposal from the plan and state, validate it, run scoped evaluations and record exclusions, freeze and fingerprint it, present… | *spread* |
| **finished wrong answer** | 4 | A constructed run where the records say color is blue, the policy looks it up and sees blue, then finishes with red, and the controller still returns… | book |
| **repeated-lookup run** | 4 | A scripted policy that keeps asking for the same lookup is stopped by a turn budget of two after two recorded observations, with status budget-exhaus… | book |

## how models generate (29)

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **objective** | 9, 10 | The one quantity the optimizer is told to lower, chosen by a human before training. | *spread* |
| **temperature** | 1, 9 | Temperature T divides the scores before they become probabilities: a smaller T concentrates probability on the largest score and a larger T spreads i… | *spread* |
| **score** | 1 | A score is a raw number given to each outcome; it gives an ordering but is not yet a chance. | book |
| **token** | 1 | The unit the model predicts at each step is a token, a fragment drawn from a fixed vocabulary, not a word and not a fact. | book |
| **transcript** | 1 | Under the interface, a chat is one string of text with role markers that the model continues. | book |
| **training** | 9 | Training changes the model's stored numbers (its parameters) by using an objective and an update rule. | book |
| **weight** | 9 | One of the toy's two learned numbers. | book |
| **step count (budget)** | 9, 10 | The number of updates the loop is allowed to run. | book |
| **sampling** | 1 | Sampling turns a distribution, which is only a recipe for selection, into actual outcomes by drawing at random in proportion to the probabilities. | book |
| **observed frequency** | 1 | The fraction of draws that actually came out a given way in one sample, which differs from the probability the distribution assigned. | book |
| **next-token prediction** | 1 | A language model does not answer your question; it repeatedly answers what plausibly comes next in the text so far, and a loop around it makes that r… | book |
| **prediction loop** | 1 | The cycle that produces a reply: feed in the transcript, get a probability for every possible next token, sample one, append it, and ask again until… | book |
| **what the loop does not contain** | 1 | The prediction loop never consults a source or an answer key, so nothing in it knows whether the text is true. | book |
| **no memory between conversations** | 1 | The model keeps nothing between turns; the whole transcript is sent again every turn, so what feels like memory is a growing string of text. | book |
| **fluent answer from incomplete evidence** | 7 | Claude writes a smooth answer from whatever it is given, and nothing in the text tells you whether the only relevant source was left out earlier. | book |
| **mutable object (the five objects)** | 9 | The five things you can change in an AI system are its weights, prompt, context, tools, and settings. | book |
| **settings** | 9 | A run-time choice about how an output is drawn from the model's scores, such as temperature. | *spread* |
| **pretraining** | 1 | The first training stage: take a passage, hide the next token, compare the model's distribution with the token that actually followed, and nudge the… | *spread* |
| **preference tuning** | 1 | A second training stage in which people choose which candidate replies they prefer and the parameters are shifted toward what raters approved of. | *spread* |
| **softmax** | 1 | The transformation that turns scores into probabilities: exponentiate each score (divided by the temperature) to get a positive weight, then divide e… | *spread* |
| **a score is not a probability** | 1 | The chapter keeps four things apart: a score, a probability, an observed frequency, and a correctness judgment. | *spread* |
| **changing what the model sees is not changing what the model is** | 9 | Giving a model different input (a prompt, examples, documents) does not change the model itself; only training changes its stored parameters. | *spread* |
| **persistence is not proof of training** | 9 | A change that sticks (a saved prompt, a retrieved document, a permission rule, a memory record) is not evidence of training. | *spread* |
| **variation between runs** | 1 | Asking the same question twice can give different answers even though the model itself did not change. | *spread* |
| **probability distribution over tokens** | 1 | At each step the model outputs a nonnegative number for every token in the vocabulary, and the numbers sum to one. | *spread* |
| **ranking is not truth** | 1 | The model's numbers rank possible continuations of a string, based on how phrases continue in the training text, and an answer key is not among the i… | *spread* |
| **misnaming a change (the verb carries a claim)** | 9 | Calling a change 'training' when you only changed a prompt, retrieved text, a tool, or a setting names the wrong thing. | *spread* |
| **classify a change by the object it modifies** | 9 | Sort each proposed change (a rewritten system prompt, a new workspace document, a newly enabled tool, a lowered temperature) by the object it changes… | *spread* |
| **lowering temperature is not a truth guarantee** | 1 | If the checked answer is a different label from the top-scored one, lowering temperature concentrates selection on the wrong label. | *spread* |

## tools and integration (46)

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **Use It** | 1, 2, 4, 13, 14, 15 | Step two of the spine: give Claude Code your gate (contract, tests, fixtures) but not your validator, ask for an implementation, and run your own tes… | book |
| **Claude Code** | 2, 3, 4, 6 | A coding assistant that can read a repository, propose a plan, edit files and run commands, often faster than a person can read the result. | book |
| **server** | 8, 9 | The program that offers capabilities such as the lookup tool and describes them. | book |
| **tools** | 9, 10 | The actions and information sources the host makes available to the model, and which of them are allowed. | book |
| **conduct Claude Code against your gate** | 5, 11, 12 | Hand Claude Code a complete specification (the gate, contract, tests and matrix) and ask for an implementation, then run your own tests on what it re… | *spread* |
| **retrieval** | 7, 9 | Retrieval picks out the documents that look most similar to the query under a stated scoring rule, so a person can inspect them first. | *spread* |
| **tool schema** | 8, 11 | A tool schema is the description (name, purpose, and allowed input shape) that you advertise to Claude. | book |
| **MCP** | 7, 8 | A protocol that gives a host and a server a shared structure for exchanging messages about tools. | *spread* |
| **diff** | 6 | The record of exactly which text changed between the before and after versions of a file. | *spread* |
| **dispatcher** | 4, 11 | The dispatcher is the application code that takes a proposed call, checks its name and arguments, and runs the real operation. | *spread* |
| **Claude Code permissions** | 5, 9 | Claude Code's real permission rules are executable rules that mediate what actions a tool may take, unlike a request for caution written in prompt te… | *spread* |
| **containment** | 5 | A target is contained when the place it resolves to lies under the approved root. | *spread* |
| **host** | 8 | The software around Claude that builds the requests, reads the replies, chooses which tools Claude sees, and controls what enters Claude's context. | *spread* |
| **interoperability** | 8 | Whether two pieces of software can send each other messages that both sides understand. | book |
| **four parties** | 8 | The four roles in a connection: the server, the host, Claude or a workflow around it that proposes using a tool, and the people and policies that def… | book |
| **accountable context** | 7 | The chapter's goal: enough authorized material to support a bounded answer, a record of what was left out and a way to say the evidence is insufficie… | book |
| **history is part of the protocol** | 8 | The same message can be accepted or rejected depending on what came before it, so you decide the response for each state in advance. | book |
| **connecting a tool is not training a model** | 8 | Adding an MCP server gives the host new information and actions, but it does not change the model's parameters. | book |
| **verifiability-first engineering** | 11 | When choosing how to do a step, pick the least powerful tool that can do it, since the most constrained tool is the easiest to check. | book |
| **lifecycle** | 8 | The ordered sequence of an MCP connection: an initialize request and reply, then an initialized notification, and only after that tool operations. | *spread* |
| **misleading tool description** | 8 | A tool description placed in Claude's context is just more text, so a misleading one can push Claude toward the wrong tool before any runtime check h… | book |
| **returned content is untrusted data** | 8 | Text a tool returns is just data; a successful reply does not make it true, and it should not be treated as an instruction. | book |
| **tools/list** | 8 | The request a client sends once the server is ready to ask which tools exist and what they accept; before that, it is rejected as too early. | *spread* |
| **readiness** | 8 | The state where the server will do tool work. | *spread* |
| **state machine** | 8 | A system that is always in one state and moves to another only when a particular message arrives, so what it accepts depends on its history. | *spread* |
| **audit view** | 7 | A listing of every document with its score and one of three fates: selected, below the cutoff, or zero overlap. | *spread* |
| **expected-source list** | 7 | A dated list you write yourself, before ingesting and before asking Claude, of the sources the task should need, with owners, versions, authorization… | *spread* |
| **tool_use block** | 11 | A tool_use block is the part of the model's response that asks for a tool; it carries a type, an id, a name and an input. | *spread* |
| **cosine similarity** | 7 | A score for how much two count vectors overlap: the dot product divided by the two vector lengths. | *spread* |
| **tool description** | 8 | The name, description and input schema a server lists for a tool. | *spread* |
| **initialized notification** | 8 | A follow-up message from the client, with no id and no reply, saying it has finished the initialize phase; it is what makes the server ready for tool… | *spread* |
| **initialize request** | 8 | The first message in the lifecycle: the client introduces itself, and the server answers with its protocol version, capabilities and name and marks i… | *spread* |
| **synonym miss** | 7 | The retriever fails to return a document that means the same thing as the query because the two use different words, so the count vectors share no to… | *spread* |
| **top-k** | 7 | Keeping only the k highest-ranked documents drops some positive matches. | *spread* |
| **tool_result block** | 11 | A tool_result block is what the application sends back for each request: it repeats the request's identifier and carries the content, or an error fla… | *spread* |
| **ranking turns scores into omissions** | 7 | The retriever scores every document, drops the nonpositive ones, sorts, and keeps at most k, and Claude sees only what survives. | *spread* |
| **context selection** | 7 | Choosing which passages Claude is actually shown, rather than handing over the whole corpus. | *spread* |
| **a name is a request for a destination** | 5 | A permission check should look at where a requested name actually ends up in the filesystem, not at how the name is spelled. | *spread* |
| **containment by string prefix** | 5 | A wrong containment test that checks whether the target's text starts with the root's text, so it wrongly accepts a sibling folder like course-other… | *spread* |
| **seven narrowing stages** | 7 | The path from documents to a sentence in a report passes through seven stages: eligibility, ingestion, representation, scoring and cutoff, selection… | *spread* |
| **validate tool names and arguments in Python** | 15 | Python, not Claude, checks that a requested tool exists, that its arguments are valid, and that a file path stays inside the approved folder before a… | *spread* |
| **conducting Claude Code against the gate** | 7 | You give Claude Code your written contract, tests and audit-view spec, not your own code, and it implements the retriever. | *spread* |
| **zero score versus absence from the corpus** | 7 | A score of zero only says no counted word is shared under this representation. | *spread* |
| **representation (stage)** | 7 | The choice of which features of a text are kept for comparison, which sets what can match at all. | *spread* |
| **server self-description** | 8 | What a server says about itself in its listing is only its own claim, so it cannot show how the server really behaves or whether it belongs in the ta… | *spread* |
| **protocol-level error** | 8 | A reply carrying an error code because the message itself was wrong or came at the wrong time, so the tool never produced a content result. | *spread* |

# Part B: core terms about evaluation and validation (27)

Some validation belongs; these are the core ones. The rest of the validation terms are in the list of names at the end.

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **check** | 1, 3, 5, 6, 8, 10, 11, 14 | Check is the second human job: testing what comes back with something that can disagree with it. | book |
| **target** | 3, 6 | What the verification should hunt for; 'check the whole thing' is not a target. | book |
| **approval** | 5, 10 | Approving a plan is something only a named person can do, with a date; Claude writing approved records nothing. | *spread* |
| **re-engagement trigger** | 12, 13 | An unexpected outcome should change the next evaluation set before another approval is requested, so the gate's design is not frozen at approval time. | book |
| **the sign-off** | 15 | A short closing statement that says what was checked, how, what was not checked, what is not claimed and who cleared it. | *spread* |
| **outcome check** | 4, 13 | A separate check, outside the controller, that decides whether a finished answer is actually right; here it compares the answer with the record for t… | *spread* |
| **accept, revise, or reject** | 6 | The three possible outcomes of a review, chosen by the responsible person from the evidence on a specific proposal. | book |
| **one-object-at-a-time test** | 9 | Change one object, hold the rest fixed, and watch what follows. | book |
| **what did the green test actually test, who decided that, and when?** | 6 | The chapter's central review question: not the steps of a code review but what the passing test really tested, who chose that, and when. | book |
| **approval drift** | 13 | An approval can stay on file after the thing it approved has changed, so the old yes gets shown as permission for an action the reviewer never saw. | book |
| **machine gate** | 14 | A gate whose pass condition is a list of tests you can run; here, the validator. | book |
| **a prediction has to forbid something** | 15 | A useful prediction names something specific that could turn out wrong. | book |
| **structure versus substance** | 15 | A machine can check that the right files exist and are long enough (structure). | book |
| **obligation** | 2 | A separate thing a response must satisfy, such as parsing, shape, exact keys, answer type, nonblank content or known identifiers. | *spread* |
| **source identifier** | 2 | A label such as s1 that points to a supplied source. | *spread* |
| **source support** | 2 | Whether the words in the cited source actually back the claim made. | *spread* |
| **content binding** | 13 | Tying a recorded decision to the exact content of one proposal, so that if the content changes the old decision no longer matches. | *spread* |
| **six-field proposal** | 13 | An approval request that must name six things: the action, the target, the reason, the effects, the evidence and the rollback. | *spread* |
| **test before the patch** | 6 | Write the regression test yourself, from the rule, before any patch exists, so the patch is what is on trial. | *spread* |
| **plausibility audit** | 6 | A step between reading the diff and running the check that uses only your own model of how the thing should behave, without consulting a source. | *spread* |
| **format validity versus source support** | 2 | An answer can be correctly formatted and cite a real source while still contradicting it, because format and support are independent. | *spread* |
| **relevance versus entailment** | 7 | A passage is relevant when it scores well or is on topic; it is supported only when you have compared it with the specific claim and it backs that cl… | *spread* |
| **review gate** | 10 | Nothing changes until a person has reviewed the plan and a stated condition holds. | *spread* |
| **gate clearance conditions** | 10 | A plan goes downstream to implementation only when six things hold: an objective chosen from three distinct candidates, empty missing_fields plus cro… | *spread* |
| **approval contract** | 13 | A decision authorizes one bounded attempt only if approved is exactly True, the approver is a nonblank string, the recorded fingerprint equals a fres… | *spread* |
| **silence, timeout, model confidence and automated score authorize nothing** | 13 | A missing answer, silence, a timeout, a model's confidence, or a favorable automated score never counts as approval. | *spread* |
| **color fixture** | 2 | A source says only 'The color is blue.', yet a response claiming the fixture says red and citing that source still passes the validator. | *spread* |

# Part C: core terms about governance, ethics and other (19)

| Term | Ch | In plain words | Flag |
|---|---|---|---|
| **sign-off** | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 | A closing statement for the register with Checked, How, Not checked, Not claiming and Signed or withheld lines, written from your own record. | book |
| **conduct, check, drive** | 1, 2, 4, 7, 12, 13 | Three jobs stay with the human when Claude does the producing: decide before it runs what the work must do, check what comes back, and sign only what… | book |
| **handoff** | 8, 12, 15 | The point where the packet passes to someone else, which is risky because a packet only its author can run has just one person behind it. | book |
| **the three jobs: conduct, check, drive** | 3, 8 | The book's split of labor: Claude produces, and you keep three jobs: conducting the work, checking what comes back, and driving, because your name go… | book |
| **capstone packet** | 15 | The ten documents a student submits, which must form one traceable argument rather than ten separate files. | *spread* |
| **build, gate, conduct, check, sign** | 1 | Every chapter runs the same sequence: build the small mechanism, write the gate, conduct Claude against it, check what comes back, and sign only what… | *spread* |
| **cross-references between artifacts** | 15 | Each artifact should point to the others it depends on. | *spread* |
| **register** | 14 | A record listing the owner, purpose, data, retention, approver, evaluation and incident contact for an AI workflow. | *spread* |
| **governance** | 14 | Governance is assigning decisions, evidence, authority, relationships, monitoring, recourse and response to specific people. | book |
| **deferral** | 14, 15 | Automation is not the default outcome of every workflow. | *spread* |
| **human gate** | 14 | A gate whose pass condition is that a named person accepted each role and that the routes work when someone uses them. | book |
| **generic risk language** | 14 | Vague worries such as there may be bias or privacy concerns fit almost any register and tell nobody what to do. | book |
| **ready-for-human-review** | 14 | The status returned when the record passes the validator's structural checks and nothing is flagged, so it can go to people for review. | *spread* |
| **five decisions** | 14 | Owner, threshold, retention, consultation and recourse are the five decisions under every register. | *spread* |
| **concrete harm** | 14 | A concrete harm names who is affected, how it happens and what the consequence is, such as students planning around a wrong deadline. | *spread* |
| **seven required fields** | 14 | The seven fields are owner, purpose, data classes, retention days, approver, evaluation and incident contact. | *spread* |
| **operational record** | 14 | A statement specific enough to be tested: it names a signal, threshold, owner, response, scope and recovery condition. | *spread* |
| **structurally complete, operationally hollow** | 14 | A register can have every field filled while no named person has accepted responsibility, no affected person was consulted, and no threshold triggers… | *spread* |
| **output is cheap, verification is not** | 15 | Claude can draft a whole packet or graph in minutes, but confirming each claim in it still takes human time. | *spread* |

# Supporting and light terms, by name

Not core. Listed for completeness; the definitions are in the full inventory.

**prompting (21):** controlled comparison; meaning-preserving change; exact key set; refusal state; contract for the connection; the expected response is the contract; invariance requirement; narrow task with named scope and evidence; shared notes are untrusted input; contract (memory store); abstention; hidden chain-of-thought; atomic claim; gate is not a freeze; format contract; fabricated completion; abstention rule and its counterexample; Claude as critic; one variable per experiment; having Claude attack the gate; contract version

**agents and the agent loop (87):** inputs; defer exit; delegated task and retained judgment; out of scope; version zero; failure route; duplicate action; max_tokens; last-writer-wins; enforcement belongs in the runtime; which stops belong to the controller; what this controller may claim; truthy approval; personalization; public action contract; keep the layers separate; deep copy on read; absent fields; dependency conflict; proposed is not accepted; scope narrow enough to supervise; three separate records; nested capability sets; four things kept distinguishable; budget validation; trace gaps; four separate events; revising the scope on the record; adopt or reject Claude's proposals; read-only versus write-capable tool; host defenses; Claude sharpens the gate, you write it; plan drift; scope expansion; completion exit; halt exit; refusal outputs; new authority versus obtainable information; process-local scope; comparing the version inside the lock; validate interaction patterns, not only individual agents; memory is not permission to act; limit agent throughput to review capacity; design (part of the gate); external write; Building effective agents; reviewed plan; PermissionError; re-engagement; scope change; permission check; stop, retry, or escalate; useful repetition; dependency map; empty missing set; offline research run; wall-clock guarantee; looping and resource-exhaustion failures; tool-call budget; long-horizon autonomy; readable sources and writable targets; trace discipline; parallel readiness; acyclic does not mean executable; stop policy; trigger table; fuller teaching record; identity confusion in shared channels; evidence of the split in the record; what counts as a repeat; budget as a separate backstop; report suspected repetition and continue; agent trace (artifact); permitted read does not imply permitted write; exact identity check on approval; approval bound to the operation and target; four distinctions people collapse; lock (process-local lock); source (source label); finish with no answer; symlink plan; capability classifier; real or assumed constraint; the trade-off of coded boundaries; non-dictionary action; fixed sequence or model-directed choices; missing function

**how models generate (52):** threshold; parameters; gradient; loss; vocabulary; sigmoid; bias; tokenizer; embedding; one prediction step; self-attention; backpropagation; transformer; reversibility and inspectability; approval is not correctness; order is preserved at positive temperature; count, seed and temperature as separate controls; a grounded patch; training example (feature and label); score, probability, and decision (three layers); fluency is not identification; modal framing; Claude's explanation is not a trace; continuation; seed; inference; stop rule; optimizer; feed-forward network; repeatability; binary logistic loss; linear score; learning rate; an explanation from the model is a story, not a trace; use (stage); gradient descent (update rule); binary logistic classifier (the toy); residual connection; unobserved outcome; stable loss expression; batch gradient descent; decision boundary; query, key, value; masking; attention heads; repeated runs under sampling; numerically stable sigmoid; ReLU; initial loss; attention weight; subtracting the maximum score; GPT-3 scale figures

**tools and integration (80):** identifier; path; five-layer capability stack; baseline (your own version first); preserved transcript; corpus; notification; dot product; resolve(); unified diff; Claude Code best practices; transition table; initialize result; permission controls; interface comparison; input route; textual cleanup of .. with no link resolution; joined but unresolved return value; deterministic tie-breaking; cargo cult of field names; capability negotiation; trace the object, not the filename; if the schema is correct, invalid calls cannot happen; tool proposal; absolute target (the join discards the root); initialized and ready flags; cost of state; silence is not readiness; technically accurate description; three layers of failure; stdio transport; tool boundary (action-time authorization); idempotency key; read the diff for hidden human decisions; start offline with an injected callable; opt-in live Messages path; client; count vector; symbolic link; ingestion; JSON-RPC; context engineering; scoring and cutoff; synonym map; error codes; parent traversal; tokenization; retrieval record; verification surface; read-only critique; chunking; read event; route deterministic work out of the stochastic layers; check one value, use another; Claude Cowork task; lexical similarity; selection record; silent omission; normalization by vector length; recall versus distractors; debug the pipeline in order; claim and qualification split across chunks; version negotiation fallback; teaching server; the 2 / sqrt(6) worked example; successful write; content boundary; exact-type check; catch everything; --live mode; coverage limit; implicit handshake rule; standard output is the protocol channel; finite-number check; Claude Code security guidance; zero filter; chunk identifiers; chunk overlap; client-side tool use; empty-vector convention

**evaluation and validation (347):** what a failure looks like; wrong versions your tests must catch; provenance; the "Not checked" line; a wrong version your tests must catch; verification; independent check; laundering; volume trap; validator; structural check; mechanism; reject; evaluation; accept; revise; verb ladder; fluency trap; evidence; verified; evaluation set; cannot audit; support review; fingerprint; verdict; claim-to-source table; missing_fields; narration; what the experiment may claim; prediction before running; checks_passed; premortem; evidence matrix; citation; capability ledger; capability inventory; validate_packet; protocol ledger; generalization; plan review; result review; cross-field review; event classifier; AI checking an AI; classification by presence; independence rule; evidence boundary; retrospective blessing; which different implementation could pass the current test; what this packet may claim; small is not safe; reasons list; filename scope; scope and correctness can disagree; Audit-First Protocol; downgrade the verb; deliberately wrong patch; a packet is a chain, not a folder; negative space; stale evidence; what a lower loss claims; correspondence is not correctness; independence judgment; freshness is not truth; three things an approval can be bound to; environment identity; approval interface; contract for the validator; a wrong version your checks must catch; prediction-lock; miniature casebook; bounded claim; contradiction pass; packet completeness theater; validator rules applied in order; evidence follows the object; Claude's report is not your evidence; shared author; what a diff is evidence of; fluency versus groundedness; gate versus audit; discrepancy list is leads, not proof; valid transport is not true content; repetition is not corroboration; final sentence is a new claim; operation versus outcome; deterministic is not infallible; audit with a non-generative tool; collapsed distinctions; highlight differences from the previous proposal; target (proposal field); reason (proposal field); effects (proposal field); evidence (proposal field); rollback (proposal field); evaluation components (tasks, trials, graders, transcripts, outcome checks); quiet failure; a mechanical check is reliable where it is narrow; what a failure looks like (part of the gate); revise, defend, or acknowledge; aim predictions at the seams; pass rate; Gap Account; review function; structurally_complete; audit-note; controlled failure; regression test; audit record; held-out set; lineage; review-required; four ledgers; source inspection; evidence type; incident replay; held-out questions; review packet; second input; development questions…

**governance, ethics and risk (138):** data-boundary; approved; narrow; risks; pre-mortem; owner; ship; seam; retention; decision owner; mitigation; consent; transfer-reflection; permission ledger; what was not tested; decision note; record the split; named actions; unresolved; plain-language explanation; in the wild; final recommendation; can the action be undone; evidence-based rather than AI-proof; values decision; distribution questions; ethics cannot be appended after model selection; consultation that can change the project; incident rehearsal; design before implementation is not a freeze; narrowing scope; complete form, absent responsibility; epistemic restraint; Memo A and Memo B; synthetic consent; honest deprioritizing; three questions to ask of any change; backup with delegated authority; stopping is a design result; compare the four options against the same criteria; deprioritize, supervise, protect; accountability stays with the signer; consultation; decision record; attestation; recourse; simulated approval; sandbox; allow, deny, or pending; review budget; pause authority; eligibility; prompt injection; source inventory; prompt injection in shared notes; applied ethics; values claim; classroom role-play; contestability; consent cannot be generated; five sorting questions; two model personas are not two people; production gaps; what this register may claim; defended choice; retention lifecycle; state exclusions prominently; inability is not prohibition; trust as a bounded decision; unsafe but acyclic plan; calibrated verbs; recourse path; equal accuracy, unequal risk; state of the world versus completion report (Ash case); equal accuracy, different errors; preserve the transcript; authentication limit; rubber stamp; minimum evidence; queue policy; legible answerability; gap between the level of the work and the level of the review; data policy beyond location; defended selection; quarantine state; retention competes with replay; reads follow purpose; dark patterns; narrow standing policy; right to withhold; ownership bias; minimal, separated audit record; close the loop into engineering; mitigation mismatch; unobservable threshold; consent by simulation; compliance theater; permanent pilot; governance-counterfactual question; what this build may claim; reflection without evidence; polish as quartile strategy; thin-sentence test; conceptual half and empirical half; no fabricated transcript; ceremonial review; what can be observed about Claude's weights; transcript of the session; human attention as a bound; verification depth tied to consequence; memory amplifies injection; review feedback loop; thresholds connect to harm, not only aggregate performance; questions that invite disagreement; five-question route test; withheld sign-off; cost of the sign-off; reckoning versus judgment; approver; disposable fixture…

**other (41):** Build It; Ship It; artifact; build your own baseline first; AI should and human should; integration; action-surface comparison; distinctness test; causal assumptions; constraint set; prediction versus intervention; Pearl's ladder; prediction is not identification; error of the third kind; primary generator; Claude has no stake; baseline (build your own first); handoff reproduction experiment; intervention; confounder; deciding whether the question is causal; offloading versus surrendering foundational capability; your own baseline version; first tier: pattern and association; propose versus decide; several possible sources of an association; predict first; change log; salience; invisible groupthink; Re-engagement Log; shared-information bias; hidden-profile test; delegation record; claim with provisos; three reframing moves; idle evidence; the artifact: your gate, as run; two-team scenario; Condorcet's jury theorem; Anthropic multi-agent research and context-engineering guidance

