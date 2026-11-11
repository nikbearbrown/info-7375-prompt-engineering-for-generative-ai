# INFO 7375 Prompt Engineering for Generative AI terminology glossary

Every term in every deck in `decks/`, with its meaning and a tag: **in the chapter** (the chapter uses and explains it), **in the exam-term list only** (a row in `decks/exam-terms/` lists, but the chapter does not explain it), or **outside source** (named in the slide's Source line). One deck per chapter, named "NN Title.html" with NN the chapter number. Generated from the decks by `make_glossary2.js`; edit the decks, not this file.

## Decks

| Deck | Slides | Terms |
|---|---|---|
| [Next-token prediction and sampling](decks/01%20Next-token%20prediction%20and%20sampling.html) | 14 | 33 |
| [Prompt contracts and evaluation](decks/02%20Prompt%20contracts%20and%20evaluation.html) | 14 | 29 |
| [Chat, assistant, agent](decks/03%20Chat,%20assistant,%20agent.html) | 14 | 32 |
| [The agent loop](decks/04%20The%20agent%20loop.html) | 13 | 26 |
| [Tools and permissions](decks/05%20Tools%20and%20permissions.html) | 14 | 31 |
| [Claude Code and diff review](decks/06%20Claude%20Code%20and%20diff%20review.html) | 14 | 31 |
| [Retrieval and Cowork](decks/07%20Retrieval%20and%20Cowork.html) | 14 | 30 |
| [MCP from scratch](decks/08%20MCP%20from%20scratch.html) | 14 | 29 |
| [Training and configuration](decks/09%20Training%20and%20configuration.html) | 14 | 32 |
| [Planning before acting](decks/10%20Planning%20before%20acting.html) | 14 | 30 |
| [Tool use and verification](decks/11%20Tool%20use%20and%20verification.html) | 14 | 31 |
| [Memory and multiple agents](decks/12%20Memory%20and%20multiple%20agents.html) | 14 | 30 |
| [Evaluation and approval gates](decks/13%20Evaluation%20and%20approval%20gates.html) | 14 | 30 |
| [Governance and ethics](decks/14%20Governance%20and%20ethics.html) | 14 | 33 |
| [Supervised capstone](decks/15%20Supervised%20capstone.html) | 14 | 34 |

Total: 15 decks, 461 term entries.

---

## Next-token prediction and sampling

[Open the deck](decks/01%20Next-token%20prediction%20and%20sampling.html) · 14 slides · 33 terms

| Term | Meaning | Tag |
|---|---|---|
| Token | A fragment from a fixed list; the unit the model predicts, not a word. | in the chapter |
| Tokenizer | The program that cuts text into entries from the vocabulary. | in the chapter |
| Vocabulary | The fixed list of token fragments, tens of thousands long. | in the chapter |
| Embedding | The vector of learned numbers that a vocabulary entry selects. | in the chapter |
| Next-token prediction | Given the text so far, a score for every possible next token. | in the chapter |
| Prediction loop | Sample one token, append it, ask again, until an ending comes. | in the chapter |
| Transcript | One string of role-marked text that is completed, and resent whole each turn. | in the chapter |
| System prompt | A paragraph near the top of that string: a request, not a gate. | in the chapter |
| Pretraining | Fitting parameters so the token that really followed gets more probability. | in the chapter |
| Backpropagation | The method that nudges every parameter slightly toward that token. | in the chapter |
| Preference tuning | A second stage that shifts parameters toward replies raters preferred. | in the chapter |
| Hidden parameter | An assumption inside a headline number that nobody stated. | in the chapter |
| Transformer | A design that reads the whole context at once, with attention and feed-forward parts. | in the chapter |
| Self-attention | The learned part that lets each token choose which tokens to read from. | in the chapter |
| Feed-forward network | An ordinary neural network applied to each token's vector on its own. | in the chapter |
| ReLU | Sets every negative value to zero: max(0, x). | in the chapter |
| Score (logit) | A raw number per outcome: an ordering, not chances. | in the chapter |
| Softmax | Exponentiates the scores, then divides by the total so they sum to one. | in the chapter |
| Probability distribution | One nonnegative share per token, all summing to one. | in the chapter |
| Subtract the max score | Shifting every score by the maximum leaves the probabilities unchanged. | in the chapter |
| Temperature | Divides the scores first: low piles probability on the top, high flattens. | in the chapter |
| Order preserved | At any positive temperature a higher score never gets less probability. | in the chapter |
| Not a truth guarantee | Concentrating on a favorite adds no evidence that it is correct. | in the chapter |
| Sampling | Drawing outcomes at random, weighted by the distribution. | in the chapter |
| Seed | A starting value that fixes the random sequence so a run can be replayed. | in the chapter |
| Observed frequency | The share of draws that landed on an outcome in one run. | in the chapter |
| Repeatability | Same call, same result; it says nothing about being true. | in the chapter |
| Gate (conduct) | Written before the output exists: what must hold, what to refuse, which test fails a wrong version. | in the chapter |
| Sign-off (check) | Checked, how, not checked, not claiming: no more than the record supports. | in the chapter |
| Driver's seat (drive) | The task-by-task split of what Claude does and what you keep. | in the chapter |
| Variation between runs | Same question, different answers, model unchanged; the cause must be isolated. | in the chapter |
| Constrained format | A tight output format leaves fewer likely continuations, so answers converge. | in the chapter |
| Fluency without support | A confident, well-formed answer that nothing in the loop checked against a source. | in the chapter |

## Prompt contracts and evaluation

[Open the deck](decks/02%20Prompt%20contracts%20and%20evaluation.html) · 14 slides · 29 terms

| Term | Meaning | Tag |
|---|---|---|
| Consumer | The program that reads the answer, and the interface it needs. | in the chapter |
| Contract | The rules an answer must meet to be accepted, fixed before any prompt is tried. | in the chapter |
| Contract first | Write the contract and its criteria first, then derive the prompt from them. | in the chapter |
| Output contract | The shape the prompt asks for: a JSON object with exactly answer and sources. | in the chapter |
| Exact key set | The object holds these keys and no others; an extra key is a rejection. | in the chapter |
| Request versus check | A prompt asks the producer; a validator decides after the answer arrives. | in the chapter |
| Refusal state | A way to say the sources do not answer; this contract has none. | in the chapter |
| Validator | Code that checks a returned object against executable conditions. | in the chapter |
| Structural check | Tests the form of an answer, not whether its content is right. | in the chapter |
| Every-source rule | Every listed source must be known; one valid entry cannot cover a bad one. | in the chapter |
| Nonblank check | The answer must hold text once surrounding spaces are stripped. | in the chapter |
| Decision, not diagnosis | The result is True or False and does not name the rule that failed. | in the chapter |
| Test coverage gap | A contract line that no test would notice missing. | in the chapter |
| Source identifier | A label such as s1 that points to a supplied source: an address, not support. | in the chapter |
| Source support | Whether the cited passage actually backs this particular claim. | in the chapter |
| Format vs support | A well-formed answer can be unsupported, so the two are checked separately. | in the chapter |
| Pass rate | Accepted responses divided by responses supplied: here 1 of 3. | in the chapter |
| Scope of a pass rate | It describes one validator on these cases, not accuracy or real-world frequency. | in the chapter |
| Empty-experiment rule | With no responses, raise an error instead of reporting 0 or 1. | in the chapter |
| Support review | A person compares each claim with the source text, claim by claim. | in the chapter |
| Three review outcomes | Supported, contradicted, or cannot be reviewed, defined before reading outputs. | in the chapter |
| Sign-off | A statement of what was checked, how, what was not, and what is not claimed. | in the chapter |
| Evaluation set | The fixed questions used to compare prompts: five development, five held-out. | in the chapter |
| Development questions | Cases you may look at and revise against. | in the chapter |
| Held-out questions | Cases sealed until the revision is frozen; once used they become development. | in the chapter |
| Evidence criterion | What supported means for each question, written before any output. | in the chapter |
| Revision as hypothesis | A prompt change is a prediction to test, changing one identifiable feature. | in the chapter |
| Persona | A role line such as You are an expert; it adds no source and changes no check. | in the chapter |
| Provenance | The record of where a response came from: prompts, sources, model label, date. | in the chapter |

## Chat, assistant, agent

[Open the deck](decks/03%20Chat,%20assistant,%20agent.html) · 14 slides · 32 terms

| Term | Meaning | Tag |
|---|---|---|
| Teaching surface | An exercise label, not a product map. | in the chapter |
| Capability set | The operations a surface is declared able to do. | in the chapter |
| Chat | Can only reason: produce a response. | in the chapter |
| Assistant | Can reason and read, but not write. | in the chapter |
| Agent | Can reason, read and write, so it can change state. | in the chapter |
| Required set | The operations a task needs, written R. | in the chapter |
| Missing set | R minus C: what the task needs and the surface lacks. Empty means covered, and nothing more. | in the chapter |
| Gate | A decision written before any grant: required, granted, refused, target, when control returns, and what passes. | in the chapter |
| Grant | The abilities actually handed to the system. | in the chapter |
| Lowest sufficient | The smallest surface that covers the task. Smaller is not better if the task needs more. | in the chapter |
| Least privilege | Give a tool only the access its task needs. | in the exam-term list only |
| Control | Who or what chooses the next operation. | in the chapter |
| Workflow vs model-led | A program fixes the steps, or the model directs its own process. Either can write. | in the chapter |
| Scrutiny | How hard the output must be checked; set by the work, not by the permissions. | in the chapter |
| Supervision gap | Level of the work minus level of the review. The risk is the gap. | in the chapter |
| Event trace | A list of recorded operations, in order. | in the chapter |
| Classify by presence | Label a trace by which events appear: write gives agent, read gives assistant, else chat. | in the chapter |
| Lossy label | The label drops order, repeats, targets, results and authority, so keep the trace. | in the chapter |
| Persistent change | An edit still there after the chat ends, such as a saved file. | in the chapter |
| Narration | The system's own prose about what it did: shows what was said, not what happened. | in the chapter |
| State check | A before-and-after look at the folder, run against a rule you wrote. | in the chapter |
| Proposed | A response offers the action. | in the chapter |
| Attempted | The operation was requested of the runtime. | in the chapter |
| Completed | The runtime reported success. | in the chapter |
| Observed | You saw the changed state yourself. | in the chapter |
| Capability not authority | Being able to do something does not give permission to do it. | in the chapter |
| Authorization | A person's decision naming what, where and when. | in the chapter |
| Proposes, you authorize | The model may propose an action; only a person authorizes it. | in the chapter |
| Authority drift | Approval for a small action later cited for a bigger one. | in the exam-term list only |
| Acceptance statement | A completion test with a requirement and a boundary, written before the work. | in the chapter |
| Back-to-me condition | The stated case that returns control to the person, such as a proposed save. | in the chapter |
| Sign-off | A statement you can put your name to, with a Not checked line. Signed or withheld. | in the chapter |

## The agent loop

[Open the deck](decks/04%20The%20agent%20loop.html) · 13 slides · 26 terms

| Term | Meaning | Tag |
|---|---|---|
| Agent loop | Propose, carry out, record, then go on or stop. | in the chapter |
| Policy | Supplies the next action; here a prepared list. | in the chapter |
| Model-backed policy | A model picks the actions; the limits stay put. | in the chapter |
| Controller | Runs the loop, keeps the trace, owns the stops. | in the chapter |
| Dispatcher | Turns an action into an observation. | in the chapter |
| Lookup environment | The fixed records the lookups read. | in the chapter |
| Action | A request such as lookup color or finish red. | in the chapter |
| Turn | One pass of the loop; it uses one action. | in the chapter |
| Observation | What came back: a value, not found or an error. | in the chapter |
| Trace | Turn, action and observation for each turn. | in the chapter |
| State update | The only change: an append to the trace. | in the chapter |
| Stop condition | A rule that ends the run, set before it starts. | in the chapter |
| Turn budget | The most turns the loop may begin. | in the chapter |
| Unit of the budget | One count is one action taken; finish costs one. | in the chapter |
| Finished | A finish was taken, with whatever answer it held. | in the chapter |
| Incomplete | The policy ran out before any finish or limit. | in the chapter |
| Budget-exhausted | Every allowed turn was used. | in the chapter |
| Error observation | Result for a name the loop does not allow. | in the chapter |
| Stop reason | Why the run ended, read from status and budget. | in the chapter |
| Status versus evidence | Finished describes the loop, not the answer. | in the chapter |
| Outcome check | A check outside the controller against the record. | in the chapter |
| Activity versus progress | A longer trace is not more support. | in the chapter |
| Repetition detector | A rule that flags or stops on a repeat. | in the chapter |
| Gate and exit table | Exits and checks written before any code runs. | in the chapter |
| Sign-off | A closing claim from your own record. | in the chapter |
| Two stops | Ending the run versus closing the task. | in the chapter |

## Tools and permissions

[Open the deck](decks/05%20Tools%20and%20permissions.html) · 14 slides · 31 terms

| Term | Meaning | Tag |
|---|---|---|
| Permission policy | A short contract written first: root, operations, who approves a write, what must be refused. | in the chapter |
| Least privilege | Grant the smallest set of operations the task needs; each one must later be verified. | in the chapter |
| Gate | A checkpoint set before the code: work moves on only when your own tests pass. | in the chapter |
| Runtime enforcement | A rule held by code that raises an error, so the wording of a request cannot talk past it. | in the chapter |
| Operation allowlist | Only read and write may run; any other operation is refused first. | in the chapter |
| PermissionError | The error the function raises to refuse a proposal. | in the chapter |
| Path | Directions for finding a file; a relative one is read from a starting folder. | in the chapter |
| Approved root | The one folder the policy lets the tool touch. | in the chapter |
| resolve() | Follows links and removes .. parts to find the real destination, without opening it. | in the chapter |
| Parent traversal | A request using .. to climb out of the folder; where it lands decides, not the dots. | in the chapter |
| Absolute target | A target starting with / makes a join drop the root and keep the target alone. | in the chapter |
| Symbolic link | A name in a folder that redirects to another place, maybe outside it. | in the chapter |
| Containment | The resolved destination lies under the resolved root, as a path relation. | in the chapter |
| String-prefix check | Comparing characters: course-other wrongly matches course. | in the chapter |
| Preflight | A check on a proposed operation before anything is done; it returns a path and no more. | in the chapter |
| Check one, use another | Checking one path, then opening a different, unchecked one. | in the chapter |
| Time boundary | The gap between check and use; the check does not freeze what happens later. | in the chapter |
| Seam | A handoff trusted on arrival: say what passes, what it is trusted to be, how that was earned. | in the chapter |
| Write approval | An extra condition for writes; being inside the root does not waive it. | in the chapter |
| Exact identity check | approved is True accepts only the Boolean True, not 1 or any other truthy value. | in the chapter |
| Simulated approval | A True placed in a test and labeled a fixture, never credited to a person. | in the chapter |
| Handoff condition | A condition a stranger can test from the record: operation, target, approver, timing. | in the chapter |
| Proposal versus grant | A proposal suggests an action; only a person with authority grants it. | in the chapter |
| Human in the loop | A person in the approval path; asked too often, the answer drifts toward yes. | in the chapter |
| Sign-off | A closing statement of what was checked, what was not, and what is not claimed. | in the chapter |
| Boundary matrix | A table of proposals, results and the branch that decided each. | in the chapter |
| Wrong versions | Deliberately broken copies of the function that your tests must fail. | in the chapter |
| Test the permitted side | Add a success test, so a policy that refuses everything cannot pass. | in the chapter |
| Sandbox | An environment that limits what a process can do, whatever the code asks. | in the exam-term list only |
| Claude Code permissions | Runtime rules that mediate tool actions, unlike a prompt asking for caution. | in the chapter |
| Four separate events | Preflight passing, runtime permission, the operation and diff review are different events. | in the chapter |

## Claude Code and diff review

[Open the deck](decks/06%20Claude%20Code%20and%20diff%20review.html) · 14 slides · 31 terms

| Term | Meaning | Tag |
|---|---|---|
| Reproduction | The smallest legitimate case that shows intended and current behavior differ. | in the chapter |
| Second input | A test case that separates the intended rule from a convenient wrong one. | in the chapter |
| Constant patch | A fix returning one fixed value, shaped to pass the one test it saw. | in the chapter |
| Survivor | A wrong version that still passes every current test. | in the chapter |
| Regression test | A test written before the fix that fails on the defect and passes on the intended rule. | in the chapter |
| Retrospective blessing | A test written after the patch, with expected values taken from the patch. | in the chapter |
| Shared author | Test and patch from one author: one misreading sits on both sides and cancels. | in the chapter |
| Gate | Reproduction, test and scope, written before the patch, that must hold before it moves on. | in the chapter |
| Allowed-file list | The files a fix may change, chosen by the task owner before the plan. | in the chapter |
| Stop condition | What must be true, with commands and exit status recorded, before the patch moves on. | in the chapter |
| Unified diff | A listing of the lines removed (-) and added (+) between two versions. | in the chapter |
| Behavior vs inspection | Behavior: what a run returned. Inspection: what reading the source shows. | in the chapter |
| Small is not safe | One character can change every call, so review effort follows consequence. | in the chapter |
| Volume trap | Output grows with the machine, reading does not, and the gap goes unverified. | in the chapter |
| Out of scope | The reason returned when a changed file is not on the allowed list. | in the chapter |
| Filename scope | A scope check by file name only; edits inside an allowed file go uninspected. | in the chapter |
| Reasons list | Every failed obligation, collected, so more than one failure stays visible. | in the chapter |
| checks_passed | A flag that says the caller reports passing checks; no command or output comes with it. | in the chapter |
| approved | A flag that must be literal True; it does not say who approved or what they saw. | in the chapter |
| merge_ready | True only when the reasons list is empty; a summary of inputs, not proof. | in the chapter |
| Finishing vs succeeding | A tidy final message ends a run; it is not evidence that the run worked. | in the chapter |
| Stale evidence | A check run before the last edit says nothing about the current diff. | in the chapter |
| Review packet | Issue, test, plan, diff, outputs and decision, all pointing at the same version. | in the chapter |
| Negative space | The checks not run and files not inspected, listed in the packet. | in the chapter |
| Plausibility audit | Your own model of how it should behave, applied before any source is consulted. | in the chapter |
| Audit record | Verdict, target, mechanism and what would change your view, written before any run. | in the chapter |
| Cannot audit | The honest verdict when your model is silent; name what is missing. | in the chapter |
| Verification | Consulting a source, such as a test run or a recomputation. | in the chapter |
| Accept, revise, reject | A human outcome for one proposal: take it, fix the gap, or refuse the package. | in the chapter |
| Verb ladder | Eight verbs, hypothesize to prove, each needing more evidence than the last. | in the chapter |
| Sign-off | A statement with your name: what was checked, what was not, and the strongest verb. | in the chapter |

## Retrieval and Cowork

[Open the deck](decks/07%20Retrieval%20and%20Cowork.html) · 14 slides · 30 terms

| Term | Meaning | Tag |
|---|---|---|
| Tokenization | Cutting text into tokens by a fixed rule; here, lowercase runs of word characters. | in the chapter |
| Count vector | Each token and how often it occurs; word order is thrown away. | in the chapter |
| Dot product | Multiply matching token counts, then add them up. | in the chapter |
| Normalization by length | Dividing by the vector lengths so a long text does not win by size. | in the chapter |
| Cosine similarity | Dot product over both lengths: 0 with no shared token, 1 for the same direction. | in the chapter |
| Lexical similarity | Overlap in the actual words, not in meaning. | in the chapter |
| Synonym miss | A same-meaning document scores zero because no token is shared. | in the chapter |
| Synonym map | A word-to-word table applied before scoring; a person decides each pair. | in the chapter |
| Embedding | A learned list of numbers for a text; this chapter's retriever does not use one. | in the exam-term list only |
| Retrieval | Ranking documents by a stated score so a person inspects the top ones first. | in the chapter |
| Zero filter | Documents with no shared token are removed before the cutoff. | in the chapter |
| Tie-breaking | Equal scores are ordered by document key. | in the chapter |
| Top-k | Keep only the k best; other positive matches are dropped. | in the chapter |
| Corpus | The documents you assemble from authorized sources for the retriever to search. | in the chapter |
| Chunking | Splitting long sources into passages; each split is a new selection choice. | in the chapter |
| Recall and distractors | A larger k finds more useful passages and more off-topic ones. | in the chapter |
| Silent omission | Most narrowing stages leave no trace in the text of the answer. | in the chapter |
| Context selection | Deciding what Claude is actually shown, after every filter. | in the chapter |
| Selection record | A note naming each narrowing from corpus to what Claude saw. | in the chapter |
| Audit view | Every document with its score and fate, not only the winners. | in the chapter |
| Retriever contract | The behaviours the retriever must have, written before it is built. | in the chapter |
| Expected-source list | Sources the task should need, written and dated before ingesting anything. | in the chapter |
| Task packet | The bounded brief: goal, permitted sources, output format, exclusions, checks. | in the chapter |
| Relevant vs supported | Scoring well or being on topic is not the same as backing a specific claim. | in the chapter |
| Atomic claim | A claim small enough for one passage to support or not. | in the chapter |
| Insufficient | On topic, but the passage does not settle the claim. | in the chapter |
| Abstention | Saying the evidence is not enough instead of filling the gap. | in the chapter |
| Conduct, check, drive | The three jobs that stay with you: decide, verify, own the reading. | in the chapter |
| Claim-to-source table | Each claim, its exact passage, a label and a note on scope or gaps. | in the chapter |
| Sign-off | A statement of what was checked, how, what was not, and what is not claimed. | in the chapter |

## MCP from scratch

[Open the deck](decks/08%20MCP%20from%20scratch.html) · 14 slides · 29 terms

| Term | Meaning | Tag |
|---|---|---|
| MCP | A shared message structure for host and server; it chooses nothing and vouches for nothing. | in the chapter |
| Server | The program that offers tools and describes them. | in the chapter |
| Host | Software around Claude that builds requests and controls what enters context. | in the chapter |
| Four parties | Server, host, Claude, and the people and policies that set authority. | in the chapter |
| State machine | Always in one state; only certain messages move it, so history decides what is accepted. | in the chapter |
| Lifecycle | The fixed order of a connection: initialize, then the notification, then tool use. | in the chapter |
| History matters | The same message can pass or fail depending on what came before it. | in the chapter |
| Initialize request | First message; the reply gives version and capabilities, and the server is initialized. | in the chapter |
| Initialized notification | Follow-up with no id and no reply; it makes the server ready. | in the chapter |
| Readiness | The state in which the server will do tool work. | in the chapter |
| tools/list | Request, once ready, for the tools that exist and what they accept. | in the chapter |
| Tool schema | The input shape a tool accepts, advertised in its listing. | in the chapter |
| tools/call | Request naming a tool and its arguments; the reply is a result or an error. | in the chapter |
| JSON-RPC | The message format: jsonrpc 2.0, an id, a method. | in the exam-term list only |
| Request id | Pairs each reply with its request; not truth. | in the chapter |
| Protocol-level error | A reply with an error code; the tool never ran. | in the chapter |
| Tool error | A result flagged isError true; the tool ran. | in the chapter |
| Interoperability | Whether two programs can exchange messages both understand. | in the chapter |
| Authorization | The decision whether a capability may run for this task; syntax cannot make it. | in the chapter |
| Capability vs authority | What a server can do is separate from what the task is allowed to use. | in the chapter |
| Server self-description | What a server says about itself is its own claim, not evidence of behavior. | in the chapter |
| Misleading description | A description in context is more text, and can steer tool choice before any check. | in the chapter |
| Discovery is not consent | A tool seen in the listing may still be denied by the host's policy. | in the chapter |
| Untrusted content | Text a tool returns is data; a successful reply does not make it true. | in the chapter |
| Laundering | An unchecked output gains authority from the clean steps it passes through. | in the chapter |
| Stop rule | A rule written into the host so a missing record is reported, not guessed. | in the chapter |
| Connection gate | Written before connecting: the predicted lifecycle table and the four ledgers. | in the chapter |
| Four ledgers | Protocol, capability, permission, evidence: four questions kept apart. | in the chapter |
| Evidence type | How a claim is known: advertised, inspected, executed, independently sourced or uninspected. | in the chapter |

## Training and configuration

[Open the deck](decks/09%20Training%20and%20configuration.html) · 14 slides · 32 terms

| Term | Meaning | Tag |
|---|---|---|
| Mutable object | The one part of a system a change edits: weights, prompt, context, tools or settings. | in the chapter |
| Training | Changing parameters with an objective and an update rule; nothing else counts. | in the chapter |
| Weights (also parameters) | The saved numbers inside the model; only training edits them. | in the chapter |
| Prompt (includes the system prompt) | Instruction text given as input; a file you can compare and revert. | in the chapter |
| Few-shot examples | Worked examples placed in the input to show a pattern; input, not training. | in the chapter |
| Retrieval | Choosing which stored passages go into this turn's input. | in the chapter |
| Context | What actually enters the input this turn, retrieved passages included. | in the chapter |
| Tools (and permission rules) | Actions and sources the host exposes, plus the rules that allow them. | in the chapter |
| Settings (for example temperature) | Run-time choices for how output is drawn from scores; they fit nothing. | in the chapter |
| One-object test (one object at a time) | Change one object, hold the rest fixed, repeat the runs, and see what follows. | in the chapter |
| Linear score | The number a = w x + b, before any squashing; it can be any size. | in the chapter |
| Sigmoid | Squashes any score into a probability between 0 and 1; a score of zero gives one-half. | in the chapter |
| Loss (binary logistic loss) | How far a predicted probability sits from the label; confident and wrong costs most. | in the chapter |
| Objective | The average loss the update is told to lower; a choice made before training. | in the chapter |
| Gradient | How the average loss changes as each parameter changes. | in the chapter |
| Finite-difference check | Estimate a slope by nudging a value both ways; uses no derivative formula. | in the chapter |
| Gradient descent (the update rule) | Subtract rate times gradient from each parameter, again and again. | in the chapter |
| Learning rate | A setting you choose that scales each step; it is never learned. | in the chapter |
| Gate | Written before the run: the change, the objective, the held-out set and the stop rule. | in the chapter |
| Stop rule (step count (budget)) | How many updates, fixed in advance; no early stop, no extra steps after peeking. | in the chapter |
| Sign-off | A closing statement: what was checked, how, what was not, and what is not claimed. | in the chapter |
| Held-out set | Points fixed beforehand and never passed to training; separate, not automatically typical. | in the chapter |
| Development data | Held-out points that guided a choice; their next use is no longer independent. | in the chapter |
| Contamination (also leakage) | Evaluation points the optimizer already used, so the result stops meaning anything. | in the chapter |
| Generalization | Doing well on cases beyond those used to fit; it needs its own evidence. | in the chapter |
| Calibration | Whether stated probabilities match how often the outcome happens; needs many labeled cases. | in the chapter |
| Threshold | The cutoff that turns a probability into a decision; you choose it, training never sees it. | in the chapter |
| Decision boundary | The input where w x + b = 0, so the probability is one-half. | in the chapter |
| Prediction (association: what goes with what) | What the fitted function outputs for an input; a statement about the model. | in the chapter |
| Intervention | What happens if we do something; observational data alone cannot settle it. | in the chapter |
| Counterfactual | What would have happened to this case had it gone differently. | in the chapter |
| Confounder | A third factor that drives both input and outcome and creates an association. | in the chapter |

## Planning before acting

[Open the deck](decks/10%20Planning%20before%20acting.html) · 14 slides · 30 terms

| Term | Meaning | Tag |
|---|---|---|
| Problem formulation | Choosing which problem the plan is for, before any step is ordered. | in the chapter |
| Distinctness test | Two formulations differ only if some result passes one and fails the other. | in the chapter |
| Error of the third kind | A right answer to the wrong problem. | in the chapter |
| Primary generator | The first, often unspoken idea of what the task is about; it decides which solutions you can see. | in the chapter |
| Constraint set | Criteria written before any scoring: feasibility, plus salience and whose interests are centered. | in the chapter |
| Values decision | Choosing whose interests the framing centers, and saying who it leaves out. | in the chapter |
| Plan | The decisions on problem, boundary, order, evidence and stopping, written down where another person can challenge them. | in the chapter |
| Eight plan fields | Objective, inputs, scope, steps, tools, risks, verification and stop: eight questions a reviewer asks. | in the chapter |
| A field that has a job | An entry concrete enough that a person can disagree with it. | in the chapter |
| missing_fields | Lists the fields whose value is absent or false-valued, in the order of FIELDS. | in the chapter |
| Structural check | A check on form only: it rejects absence, not poor content. | in the chapter |
| All-x plan | Every field holds the string x: nothing is missing, nothing is meant. | in the chapter |
| Semantic review | A person asks if each entry is meaningful, authorised and tests the claim. | in the chapter |
| Dependency graph | Steps as nodes; an arrow means the second waits for the first. | in the chapter |
| Topological ordering | Take every step with no waiting prerequisite, sorted by id, remove it, and repeat. | in the chapter |
| Duplicate step | Two steps share one id; one key cannot hold both. | in the chapter |
| Unknown prerequisite | A step waits on an id that is not in the plan. | in the chapter |
| Dependency cycle | Steps wait on each other, so none can become ready. | in the chapter |
| Acyclic, not executable | An order exists, but the declared arrows may omit real dependencies or allow an unsafe action. | in the chapter |
| Handoff condition | What one step must hand the next, stated so a stranger can check it. | in the chapter |
| Reversibility | Whether a change can be undone decides how much human approval it needs. | in the chapter |
| Stop condition | Three exits, complete, halt or defer, each with an observable trigger. | in the chapter |
| Refusal path | A route for missing authority, evidence or checks: keep state and report what blocks the next step. | in the chapter |
| Exit owner | Whoever answers for an exit: a test can halt, but a person decides what a new risk changes. | in the chapter |
| Predict versus record | The plan states predictions; the result records what happened; keep the two apart. | in the chapter |
| Not-waterfall rule | A plan is revised, with the reason recorded, when a result contradicts it. | in the chapter |
| Counterexample review | Imagine a plan that meets a field's wording but fails its purpose, and check that the plan rejects it. | in the chapter |
| Review gate | Nothing changes until a person has reviewed the plan and a stated condition holds. | in the chapter |
| Approval | A named person's dated act; a sentence from Claude records nothing. | in the chapter |
| Sign-off | A statement of what was checked, how, what was not, and what is not claimed. | in the chapter |

## Tool use and verification

[Open the deck](decks/11%20Tool%20use%20and%20verification.html) · 14 slides · 31 terms

| Term | Meaning | Tag |
|---|---|---|
| Proposes vs executes | Claude emits a request as data; your own program does the exact work and reports the returned value. | in the chapter |
| Verifiability first | Pick the most constrained tool that does the step, because that is the one you can check. | in the chapter |
| Capability vs authority | Each operation you let the dispatcher run is power you hand over; the allowlist records that policy. | in the chapter |
| Tool schema | The description of a tool and its arguments shown to Claude. It shapes requests but enforces nothing. | in the chapter |
| Tool call | A request from Claude naming a tool, its arguments and an id. It is a proposal, not an execution. | in the chapter |
| Dispatcher | The application code that checks a proposal and runs the real operation, or refuses it. | in the chapter |
| Allowlist | The closed set of operations the application will run. Any other name is refused. | in the chapter |
| Argument validation | Checking a call's name, keys and values against the contract before anything runs. | in the chapter |
| Exact-type check | Tests the exact Python type, because True counts as an int and would slip past a loose test. | in the chapter |
| Finite-number check | Refuses infinity and not-a-number inputs, and checks that the sum is finite too. | in the chapter |
| Identifier | A label on each request that its result repeats, so each result is paired with its request. | in the chapter |
| tool_result block | The message block that carries the tool's output back, tagged with the request's identifier. | in the chapter |
| Tool error | A refused call returned as a result marked is_error, so the model can see what failed and why. | in the chapter |
| Duplicate-ID guard | Stops a batch in which two requests share an id, since results could no longer be paired. | in the chapter |
| Bounded controller | The loop that asks for a response, runs requested tools and repeats, within a fixed turn limit. | in the chapter |
| Stop reason | The field saying why the model stopped: end_turn, tool_use or max_tokens. The loop branches on it. | in the chapter |
| Finished | The controller's status when a reply ends with end_turn. It says a stop signal was seen, nothing more. | in the chapter |
| Turn budget | The cap on turns. It ends endless looping but does not show progress or safety. | in the chapter |
| Protocol vs verification | A loop can end cleanly with a false final sentence. Finishing describes machinery; verifying describes the claim. | in the chapter |
| Final claim is new | The last sentence is a new claim. Nothing carries evidence into it until it is compared. | in the chapter |
| Verified | A word reserved for a claim whose check came from outside the route that produced it. | in the chapter |
| Evidence matrix | A table pairing each claim with its evidence, what that shows, and a check from a different route. | in the chapter |
| Independent check | A check that fails differently from the thing it checks, so it can say no. | in the chapter |
| Repetition ≠ evidence | Running the same helper twice repeats its answer, bug included. Agreement is not corroboration. | in the chapter |
| Shared assumption | An input or source both routes rely on; a flaw there fools both checks together. | in the chapter |
| Gate | The contract, tests and evidence matrix written before the run, with who decided each item named. | in the chapter |
| Sign-off | A closing statement of what was checked, how, what was not checked and what is not claimed. | in the chapter |
| Not checked line | The sign-off line listing what the record does not show; a drafted sign-off tends to leave it out. | in the chapter |
| Operation vs outcome | A tool result reports an operation; a reader's word like saved or sent claims an outcome. | in the chapter |
| Verification surface | Evidence a tool leaves for checking: resolved path, read-back, diff, tests, remote state. | in the chapter |
| Deterministic, fallible | Code repeats its logic every time, so a wrong formula or stale input gives the same wrong answer. | in the chapter |

## Memory and multiple agents

[Open the deck](decks/12%20Memory%20and%20multiple%20agents.html) · 14 slides · 30 terms

| Term | Meaning | Tag |
|---|---|---|
| Memory (stored state) | A dictionary of records under keys, kept outside the model. | in the chapter |
| Absent fields | What a record lacks: expiry, author, signature, verification, truth. | in the chapter |
| Version zero | What a missing key returns: no write yet, not a stored null fact. | in the chapter |
| Version | A revision counter for one key; it orders commits, not truth. | in the chapter |
| Source label | Caller-written text saying where a value came from. | in the chapter |
| Optimistic concurrency | Work proceeds unlocked; at commit the writer hands back the version it read. | in the chapter |
| Stale write | A write whose expected version is out of date: refused, nothing changes. | in the chapter |
| Last-writer-wins | The later write replaces the earlier one with no check. | in the exam-term list only |
| No automatic retry | After a stale rejection, reread and compare; never just retry. | in the chapter |
| Lock (process-local) | One thread at a time may check and write, within this one object. | in the chapter |
| Deep copy on read | A read returns a copy, so editing it cannot change the store. | in the chapter |
| Revision boundary | What one version number covers, decided before any worker runs. | in the chapter |
| Freshness is not truth | Newer or unexpired does not mean correct; fresh depends on the use. | in the chapter |
| Provenance | Where a value came from; a label alone does not prove it. | in the chapter |
| Authentication | Shows who produced the bytes, not that the claim is true. | in the chapter |
| Cascade | Each worker builds on the last, so small error chances compound. | in the chapter |
| Authority laundering | Unverified data gains standing from the channel it arrived through. | in the chapter |
| Lineage | The chain a claim was derived from; copies of one root are one source. | in the chapter |
| Facts, not instructions | Stored facts enter the prompt as quoted claims with their source. | in the chapter |
| Quarantine state | A suspect record kept out of prompts but kept for incident review. | in the chapter |
| Independence | Two routes are independent only if they would not fail for one reason. | in the chapter |
| Role contract | A worker's inputs, task, tools, output, budget and escalation, written down. | in the chapter |
| Initial judgments first | Collect each person's judgment before anyone sees a synthesis. | in the chapter |
| Re-engagement trigger | An event, not an attitude, that sends work back to reopen a decision. | in the chapter |
| Dependency conflict | Running work rests on a value new evidence challenges; versions cannot see it. | in the chapter |
| Incident state machine | States richer than pass or fail: active, challenged, paused, reviewed. | in the chapter |
| Dependency map | Which tasks depend on which keys, so the right work pauses. | in the chapter |
| Idempotency key | A token that makes repeating an action have one effect. | in the exam-term list only |
| Premortem | List how it could fail; give each failure a control and a residual risk. | in the chapter |
| Sign-off | A statement of what was checked, how, what was not, and what is not claimed. | in the chapter |

## Evaluation and approval gates

[Open the deck](decks/13%20Evaluation%20and%20approval%20gates.html) · 14 slides · 30 terms

| Term | Meaning | Tag |
|---|---|---|
| Approval gate | Where evidence is gathered and a decision about that exact proposal is recorded. | in the chapter |
| Evaluation | Finding out how well a proposal meets a stated criterion; it produces evidence. | in the chapter |
| Authorization | A responsible person or policy permitting the action; it spends the evidence. | in the chapter |
| Approval drift | An approval stays on file after the thing it approved has changed. | in the chapter |
| Six-field proposal | A request naming action, target, reason, effects, evidence and rollback. | in the chapter |
| Generic approval prompt | An “Allow?” question that hides what the yes covers. | in the chapter |
| Structural validity | Every required field is filled; says nothing about whether the content is adequate. | in the chapter |
| Plausibility auditing | Judging whether a claim is credible, however confidently it is stated. | in the chapter |
| Canonical serialization | Writing equal content as equal bytes, such as sorting keys, before hashing. | in the chapter |
| Fingerprint | A SHA-256 digest, 64 hex characters, that changes when the serialized content changes. | in the chapter |
| Content binding | Tying a decision to the exact content of one proposal, so changed content cannot reuse it. | in the chapter |
| Approval predicate | A test of whether a decision record has the required shape and matches the content. | in the chapter |
| Simulated decision | A made-up decision record from test code, labelled as such; not a person's sign-off. | in the chapter |
| Target aliasing | Different strings naming one file, or one string naming different files. | in the chapter |
| Approval scope | What one approval covers: one run, one environment, one time window, one maximum effect. | in the chapter |
| Expiry | A deadline, with a stated time basis, after which a decision no longer counts. | in the chapter |
| Revocation | Withdrawing a decision that has not yet expired. | in the chapter |
| Replay | Presenting the same valid decision again to get the effect again. | in the chapter |
| Single-use consumption | Checking and marking a decision used in one step, so a second use fails. | in the chapter |
| Evaluation set | Cases chosen before the result is seen, built so that they can fail the proposal. | in the chapter |
| Refusal case | A case whose correct outcome is to stop. | in the chapter |
| Recorded exclusions | A written list of what the set does not cover. | in the chapter |
| Outcome check | Reading the real state after the action instead of trusting the agent's sentence. | in the chapter |
| Review budget | How many proposals a reviewer can read carefully in a period; an assumption unless measured. | in the chapter |
| Volume trap | Output grows tenfold but verification does not, so more goes unreviewed. | in the chapter |
| Habituation | Reflexive clicking that sets in when prompts outnumber the attention available. | in the exam-term list only |
| Decision record | What a reviewer produces: approve, refuse or defer, with scope, gaps and authority. | in the chapter |
| Sign-off | The statement a builder signs about the gate built, with a line for what was not checked. | in the chapter |
| Attestation | A four-part statement: what was tested, what was not, who cleared which gate, calibrated verbs. | in the chapter |
| Right to withhold | The signer's option to decline when the record does not support signing. | in the chapter |

## Governance and ethics

[Open the deck](decks/14%20Governance%20and%20ethics.html) · 14 slides · 33 terms

| Term | Meaning | Tag |
|---|---|---|
| Register | A record of the owner, purpose, data, retention, approver, evaluation and incident contact for one AI workflow. | in the chapter |
| Seven required fields | Owner, purpose, data classes, retention days, approver, evaluation, incident contact; each opens a question. | in the chapter |
| Missing-field check | A field is missing when its key is absent or its value is None, empty text or an empty list. | in the chapter |
| Classroom allowlist | The three data classes accepted without review: public, synthetic, internal; case-sensitive. | in the chapter |
| External write | A flag for acting outside the system; the validator adds an approval issue and checks nothing more. | in the chapter |
| Review-required | The status when a check found an issue, such as an unknown class or an external write. | in the chapter |
| Ready-for-human-review | The status when every structural check passed; it is not approval, consent or compliance. | in the chapter |
| Complete but hollow (structurally complete, operationally hollow) | Every field is filled while nobody has accepted a role and no threshold fires. | in the chapter |
| Machine gate | A gate that passes when a list of tests you can run passes; here, the validator. | in the chapter |
| Human gate | A gate that passes when a named person accepted each role and the routes work when used. | in the chapter |
| Verb ladder | Listed, confirmed, exercised, verified: use the weakest verb the evidence supports. | in the chapter |
| Five decisions | Owner, threshold, retention, consultation and recourse, made by people before the form is filled. | in the chapter |
| Owner | The person who accepts the workflow as a continuing system and may stop it. | in the chapter |
| Threshold | The observable signal that triggers a response, and what the response is. | in the chapter |
| Operational record | A statement a stranger can test: signal, threshold, owner, response, scope, recovery. | in the chapter |
| Retention lifecycle | Every copy of the data, how long it lives and how deletion is checked; retention_days is one input. | in the chapter |
| Deletion test | Insert a labelled fixture, run the lifecycle, inspect the stores you control, state what is unverified. | in the chapter |
| Concrete harm | Names who is affected, how it happens and the consequence, such as a wrong deadline. | in the chapter |
| Generic risk language | Worries like “bias or privacy concerns” that fit any register and tell nobody what to do. | in the chapter |
| Same score, other error | Equal accuracy can hide different errors that cost different people. | in the chapter |
| Values claim | Choosing which error or equality matters is a decision with an owner, not an optimization. | in the chapter |
| Consultation | Asking real people, where the answer could change the purpose, limits, retention or the decision to automate. | in the chapter |
| Consent by simulation | Presenting model-written stakeholder reactions as if people had given feedback. | in the chapter |
| Recourse path | The whole route from report to correction, not just an email address. | in the chapter |
| Contestability | A person can trigger real reconsideration; it does not mean every challenge wins. | in the chapter |
| Deferral | Deciding not to automate yet, and recording what evidence or capacity would justify revisiting. | in the chapter |
| Narrowing scope | Keeping the work but cutting data, authority or retention until the risk can be handled. | in the chapter |
| Human in the loop | Counts only when the human task, evidence, authority, time budget and stop rule are named. | in the chapter |
| Pause authority | The owner's explicit power to halt the workflow, with a backup when the owner is unavailable. | in the chapter |
| Sign-off | A closing statement of what was checked, how, what was not, and what is not claimed. | in the chapter |
| Not checked line | The sign-off line naming what the author did not verify; an AI-written sign-off leaves it out. | in the chapter |
| Withholding | Declining to sign when the evidence does not support it, then narrowing or deferring. | in the chapter |
| Control plane | A register that can pause, revoke approval, shorten retention, change evaluation, assign repair or end the project. | in the chapter |

## Supervised capstone

[Open the deck](decks/15%20Supervised%20capstone.html) · 14 slides · 34 terms

| Term | Meaning | Tag |
|---|---|---|
| validate_packet | A function that checks ten named files: inside the folder, present, at least 40 characters. | in the chapter |
| structurally_complete | The flag that reads True when no file is missing, escaping or too short. | in the chapter |
| Meaningless packet | Ten long files of repeated x that pass, showing length is not substance. | in the chapter |
| Structure vs substance | A machine checks files and sizes; truth and trust need evidence and a person. | in the chapter |
| Capstone packet | Ten documents that let a stranger trace the work from a real need to a decision. | in the chapter |
| Three jobs | Conduct decides before building, check finds faults and signs, drive keeps the choices. | in the chapter |
| Cross-references | Each artifact points to those it depends on; every pointer is a claim to open and test. | in the chapter |
| Brief | The first artifact: need, owner, who is affected, success, non-purpose, decision scope. | in the chapter |
| Non-purpose | A written line on what the workflow will not do, giving reviewers a scope-drift test. | in the chapter |
| Data boundary | The inventory of sources: label, origin, access, retention, deletion, exclusions. | in the chapter |
| Action surface map | What the workflow can read, propose, write, send or publish, outside effects flagged. | in the chapter |
| Plan | Evidence-producing steps with dependencies, stop conditions, budgets and replanning triggers. | in the chapter |
| Pre-mortem | Failures predicted before the run, each with a detector, owner, response and leftover risk. | in the chapter |
| Gates | Each consequential proposal tied to the exact content a named person approved, with an expiry. | in the chapter |
| Authority drift | A local-write approval later described as permission to publish. | in the chapter |
| Python constrains | Claude drafts and proposes; code fixes what must be identical every time. | in the chapter |
| Prompt is a request | A prompt is a request, not a boundary: only a missing capability stops an action. | in the chapter |
| Validate in Python | Code checks the tool exists, the arguments are valid and the path stays inside the root. | in the chapter |
| Capability vs authority | What the system is able to do versus what it is approved to do. | in the chapter |
| Controlled failure | One safe, reproducible failure staged on purpose, predicted first and traced end to end. | in the chapter |
| Reviewed recovery | A person or stated policy finds why it failed, changes the plan, rechecks independently. | in the chapter |
| Recovery by repetition | Rerunning the same prompt until a wanted answer appears, with no reviewed change. | in the chapter |
| Forbidding prediction | A prediction that rules outcomes out, so some result could prove it wrong. | in the chapter |
| Audit the reviewer | Predict the review's findings first, judge each as genuine or false, score the match. | in the chapter |
| Gap Account | The audit-note's record of what the review could not reach, and who is accountable. | in the chapter |
| Contingent miss | A gap that a better prompt, a second run or more evidence would close. | in the chapter |
| Structural gap | A gap owing to the reviewer's kind and access, so rerunning it will not close it. | in the chapter |
| Claim-to-evidence graph | Claims broken into parts, each linked to evidence that could disagree with it. | in the chapter |
| Inspect state | Check what ended up true, not only that the planned calls ran. | in the chapter |
| Verification costs | A graph takes a minute to draft; opening each edge takes real time, so budget for it. | in the chapter |
| Sign-off | A closing statement of what was checked, how, what was not, and who cleared it. | in the chapter |
| Handoff | The seam where the packet passes to someone else, who must be able to run it unaided. | in the chapter |
| Ship/narrow/defer/stop | The four final choices; evidence informs the choice and a named person owns it. | in the chapter |
| Driver's seat | The split of work: Claude assembles and drafts; you choose, judge and sign. | in the chapter |

---

## Alphabetical index

| Term | Deck | Meaning |
|---|---|---|
| A field that has a job | Planning before acting | An entry concrete enough that a person can disagree with it. |
| Absent fields | Memory and multiple agents | What a record lacks: expiry, author, signature, verification, truth. |
| Absolute target | Tools and permissions | A target starting with / makes a join drop the root and keep the target alone. |
| Abstention | Retrieval and Cowork | Saying the evidence is not enough instead of filling the gap. |
| Accept, revise, reject | Claude Code and diff review | A human outcome for one proposal: take it, fix the gap, or refuse the package. |
| Acceptance statement | Chat, assistant, agent | A completion test with a requirement and a boundary, written before the work. |
| Action | The agent loop | A request such as lookup color or finish red. |
| Action surface map | Supervised capstone | What the workflow can read, propose, write, send or publish, outside effects flagged. |
| Activity versus progress | The agent loop | A longer trace is not more support. |
| Acyclic, not executable | Planning before acting | An order exists, but the declared arrows may omit real dependencies or allow an unsafe action. |
| Agent | Chat, assistant, agent | Can reason, read and write, so it can change state. |
| Agent loop | The agent loop | Propose, carry out, record, then go on or stop. |
| All-x plan | Planning before acting | Every field holds the string x: nothing is missing, nothing is meant. |
| Allowed-file list | Claude Code and diff review | The files a fix may change, chosen by the task owner before the plan. |
| Allowlist | Tool use and verification | The closed set of operations the application will run. Any other name is refused. |
| Approval | Planning before acting | A named person's dated act; a sentence from Claude records nothing. |
| Approval drift | Evaluation and approval gates | An approval stays on file after the thing it approved has changed. |
| Approval gate | Evaluation and approval gates | Where evidence is gathered and a decision about that exact proposal is recorded. |
| Approval predicate | Evaluation and approval gates | A test of whether a decision record has the required shape and matches the content. |
| Approval scope | Evaluation and approval gates | What one approval covers: one run, one environment, one time window, one maximum effect. |
| approved | Claude Code and diff review | A flag that must be literal True; it does not say who approved or what they saw. |
| Approved root | Tools and permissions | The one folder the policy lets the tool touch. |
| Argument validation | Tool use and verification | Checking a call's name, keys and values against the contract before anything runs. |
| Assistant | Chat, assistant, agent | Can reason and read, but not write. |
| Atomic claim | Retrieval and Cowork | A claim small enough for one passage to support or not. |
| Attempted | Chat, assistant, agent | The operation was requested of the runtime. |
| Attestation | Evaluation and approval gates | A four-part statement: what was tested, what was not, who cleared which gate, calibrated verbs. |
| Audit record | Claude Code and diff review | Verdict, target, mechanism and what would change your view, written before any run. |
| Audit the reviewer | Supervised capstone | Predict the review's findings first, judge each as genuine or false, score the match. |
| Audit view | Retrieval and Cowork | Every document with its score and fate, not only the winners. |
| Authentication | Memory and multiple agents | Shows who produced the bytes, not that the claim is true. |
| Authority drift | Chat, assistant, agent | Approval for a small action later cited for a bigger one. |
| Authority drift | Supervised capstone | A local-write approval later described as permission to publish. |
| Authority laundering | Memory and multiple agents | Unverified data gains standing from the channel it arrived through. |
| Authorization | Chat, assistant, agent | A person's decision naming what, where and when. |
| Authorization | MCP from scratch | The decision whether a capability may run for this task; syntax cannot make it. |
| Authorization | Evaluation and approval gates | A responsible person or policy permitting the action; it spends the evidence. |
| Back-to-me condition | Chat, assistant, agent | The stated case that returns control to the person, such as a proposed save. |
| Backpropagation | Next-token prediction and sampling | The method that nudges every parameter slightly toward that token. |
| Behavior vs inspection | Claude Code and diff review | Behavior: what a run returned. Inspection: what reading the source shows. |
| Boundary matrix | Tools and permissions | A table of proposals, results and the branch that decided each. |
| Bounded controller | Tool use and verification | The loop that asks for a response, runs requested tools and repeats, within a fixed turn limit. |
| Brief | Supervised capstone | The first artifact: need, owner, who is affected, success, non-purpose, decision scope. |
| Budget-exhausted | The agent loop | Every allowed turn was used. |
| Calibration | Training and configuration | Whether stated probabilities match how often the outcome happens; needs many labeled cases. |
| Cannot audit | Claude Code and diff review | The honest verdict when your model is silent; name what is missing. |
| Canonical serialization | Evaluation and approval gates | Writing equal content as equal bytes, such as sorting keys, before hashing. |
| Capability not authority | Chat, assistant, agent | Being able to do something does not give permission to do it. |
| Capability set | Chat, assistant, agent | The operations a surface is declared able to do. |
| Capability vs authority | MCP from scratch | What a server can do is separate from what the task is allowed to use. |
| Capability vs authority | Tool use and verification | Each operation you let the dispatcher run is power you hand over; the allowlist records that policy. |
| Capability vs authority | Supervised capstone | What the system is able to do versus what it is approved to do. |
| Capstone packet | Supervised capstone | Ten documents that let a stranger trace the work from a real need to a decision. |
| Cascade | Memory and multiple agents | Each worker builds on the last, so small error chances compound. |
| Chat | Chat, assistant, agent | Can only reason: produce a response. |
| Check one, use another | Tools and permissions | Checking one path, then opening a different, unchecked one. |
| checks_passed | Claude Code and diff review | A flag that says the caller reports passing checks; no command or output comes with it. |
| Chunking | Retrieval and Cowork | Splitting long sources into passages; each split is a new selection choice. |
| Claim-to-evidence graph | Supervised capstone | Claims broken into parts, each linked to evidence that could disagree with it. |
| Claim-to-source table | Retrieval and Cowork | Each claim, its exact passage, a label and a note on scope or gaps. |
| Classify by presence | Chat, assistant, agent | Label a trace by which events appear: write gives agent, read gives assistant, else chat. |
| Classroom allowlist | Governance and ethics | The three data classes accepted without review: public, synthetic, internal; case-sensitive. |
| Claude Code permissions | Tools and permissions | Runtime rules that mediate tool actions, unlike a prompt asking for caution. |
| Complete but hollow | Governance and ethics | Every field is filled while nobody has accepted a role and no threshold fires. |
| Completed | Chat, assistant, agent | The runtime reported success. |
| Concrete harm | Governance and ethics | Names who is affected, how it happens and the consequence, such as a wrong deadline. |
| Conduct, check, drive | Retrieval and Cowork | The three jobs that stay with you: decide, verify, own the reading. |
| Confounder | Training and configuration | A third factor that drives both input and outcome and creates an association. |
| Connection gate | MCP from scratch | Written before connecting: the predicted lifecycle table and the four ledgers. |
| Consent by simulation | Governance and ethics | Presenting model-written stakeholder reactions as if people had given feedback. |
| Constant patch | Claude Code and diff review | A fix returning one fixed value, shaped to pass the one test it saw. |
| Constrained format | Next-token prediction and sampling | A tight output format leaves fewer likely continuations, so answers converge. |
| Constraint set | Planning before acting | Criteria written before any scoring: feasibility, plus salience and whose interests are centered. |
| Consultation | Governance and ethics | Asking real people, where the answer could change the purpose, limits, retention or the decision to automate. |
| Consumer | Prompt contracts and evaluation | The program that reads the answer, and the interface it needs. |
| Containment | Tools and permissions | The resolved destination lies under the resolved root, as a path relation. |
| Contamination | Training and configuration | Evaluation points the optimizer already used, so the result stops meaning anything. |
| Content binding | Evaluation and approval gates | Tying a decision to the exact content of one proposal, so changed content cannot reuse it. |
| Contestability | Governance and ethics | A person can trigger real reconsideration; it does not mean every challenge wins. |
| Context | Training and configuration | What actually enters the input this turn, retrieved passages included. |
| Context selection | Retrieval and Cowork | Deciding what Claude is actually shown, after every filter. |
| Contingent miss | Supervised capstone | A gap that a better prompt, a second run or more evidence would close. |
| Contract | Prompt contracts and evaluation | The rules an answer must meet to be accepted, fixed before any prompt is tried. |
| Contract first | Prompt contracts and evaluation | Write the contract and its criteria first, then derive the prompt from them. |
| Control | Chat, assistant, agent | Who or what chooses the next operation. |
| Control plane | Governance and ethics | A register that can pause, revoke approval, shorten retention, change evaluation, assign repair or end the project. |
| Controlled failure | Supervised capstone | One safe, reproducible failure staged on purpose, predicted first and traced end to end. |
| Controller | The agent loop | Runs the loop, keeps the trace, owns the stops. |
| Corpus | Retrieval and Cowork | The documents you assemble from authorized sources for the retriever to search. |
| Cosine similarity | Retrieval and Cowork | Dot product over both lengths: 0 with no shared token, 1 for the same direction. |
| Count vector | Retrieval and Cowork | Each token and how often it occurs; word order is thrown away. |
| Counterexample review | Planning before acting | Imagine a plan that meets a field's wording but fails its purpose, and check that the plan rejects it. |
| Counterfactual | Training and configuration | What would have happened to this case had it gone differently. |
| Cross-references | Supervised capstone | Each artifact points to those it depends on; every pointer is a claim to open and test. |
| Data boundary | Supervised capstone | The inventory of sources: label, origin, access, retention, deletion, exclusions. |
| Decision boundary | Training and configuration | The input where w x + b = 0, so the probability is one-half. |
| Decision record | Evaluation and approval gates | What a reviewer produces: approve, refuse or defer, with scope, gaps and authority. |
| Decision, not diagnosis | Prompt contracts and evaluation | The result is True or False and does not name the rule that failed. |
| Deep copy on read | Memory and multiple agents | A read returns a copy, so editing it cannot change the store. |
| Deferral | Governance and ethics | Deciding not to automate yet, and recording what evidence or capacity would justify revisiting. |
| Deletion test | Governance and ethics | Insert a labelled fixture, run the lifecycle, inspect the stores you control, state what is unverified. |
| Dependency conflict | Memory and multiple agents | Running work rests on a value new evidence challenges; versions cannot see it. |
| Dependency cycle | Planning before acting | Steps wait on each other, so none can become ready. |
| Dependency graph | Planning before acting | Steps as nodes; an arrow means the second waits for the first. |
| Dependency map | Memory and multiple agents | Which tasks depend on which keys, so the right work pauses. |
| Deterministic, fallible | Tool use and verification | Code repeats its logic every time, so a wrong formula or stale input gives the same wrong answer. |
| Development data | Training and configuration | Held-out points that guided a choice; their next use is no longer independent. |
| Development questions | Prompt contracts and evaluation | Cases you may look at and revise against. |
| Discovery is not consent | MCP from scratch | A tool seen in the listing may still be denied by the host's policy. |
| Dispatcher | The agent loop | Turns an action into an observation. |
| Dispatcher | Tool use and verification | The application code that checks a proposal and runs the real operation, or refuses it. |
| Distinctness test | Planning before acting | Two formulations differ only if some result passes one and fails the other. |
| Dot product | Retrieval and Cowork | Multiply matching token counts, then add them up. |
| Driver's seat | Supervised capstone | The split of work: Claude assembles and drafts; you choose, judge and sign. |
| Driver's seat (drive) | Next-token prediction and sampling | The task-by-task split of what Claude does and what you keep. |
| Duplicate step | Planning before acting | Two steps share one id; one key cannot hold both. |
| Duplicate-ID guard | Tool use and verification | Stops a batch in which two requests share an id, since results could no longer be paired. |
| Eight plan fields | Planning before acting | Objective, inputs, scope, steps, tools, risks, verification and stop: eight questions a reviewer asks. |
| Embedding | Next-token prediction and sampling | The vector of learned numbers that a vocabulary entry selects. |
| Embedding | Retrieval and Cowork | A learned list of numbers for a text; this chapter's retriever does not use one. |
| Empty-experiment rule | Prompt contracts and evaluation | With no responses, raise an error instead of reporting 0 or 1. |
| Error observation | The agent loop | Result for a name the loop does not allow. |
| Error of the third kind | Planning before acting | A right answer to the wrong problem. |
| Evaluation | Evaluation and approval gates | Finding out how well a proposal meets a stated criterion; it produces evidence. |
| Evaluation set | Prompt contracts and evaluation | The fixed questions used to compare prompts: five development, five held-out. |
| Evaluation set | Evaluation and approval gates | Cases chosen before the result is seen, built so that they can fail the proposal. |
| Event trace | Chat, assistant, agent | A list of recorded operations, in order. |
| Every-source rule | Prompt contracts and evaluation | Every listed source must be known; one valid entry cannot cover a bad one. |
| Evidence criterion | Prompt contracts and evaluation | What supported means for each question, written before any output. |
| Evidence matrix | Tool use and verification | A table pairing each claim with its evidence, what that shows, and a check from a different route. |
| Evidence type | MCP from scratch | How a claim is known: advertised, inspected, executed, independently sourced or uninspected. |
| Exact identity check | Tools and permissions | approved is True accepts only the Boolean True, not 1 or any other truthy value. |
| Exact key set | Prompt contracts and evaluation | The object holds these keys and no others; an extra key is a rejection. |
| Exact-type check | Tool use and verification | Tests the exact Python type, because True counts as an int and would slip past a loose test. |
| Exit owner | Planning before acting | Whoever answers for an exit: a test can halt, but a person decides what a new risk changes. |
| Expected-source list | Retrieval and Cowork | Sources the task should need, written and dated before ingesting anything. |
| Expiry | Evaluation and approval gates | A deadline, with a stated time basis, after which a decision no longer counts. |
| External write | Governance and ethics | A flag for acting outside the system; the validator adds an approval issue and checks nothing more. |
| Facts, not instructions | Memory and multiple agents | Stored facts enter the prompt as quoted claims with their source. |
| Feed-forward network | Next-token prediction and sampling | An ordinary neural network applied to each token's vector on its own. |
| Few-shot examples | Training and configuration | Worked examples placed in the input to show a pattern; input, not training. |
| Filename scope | Claude Code and diff review | A scope check by file name only; edits inside an allowed file go uninspected. |
| Final claim is new | Tool use and verification | The last sentence is a new claim. Nothing carries evidence into it until it is compared. |
| Fingerprint | Evaluation and approval gates | A SHA-256 digest, 64 hex characters, that changes when the serialized content changes. |
| Finished | The agent loop | A finish was taken, with whatever answer it held. |
| Finished | Tool use and verification | The controller's status when a reply ends with end_turn. It says a stop signal was seen, nothing more. |
| Finishing vs succeeding | Claude Code and diff review | A tidy final message ends a run; it is not evidence that the run worked. |
| Finite-difference check | Training and configuration | Estimate a slope by nudging a value both ways; uses no derivative formula. |
| Finite-number check | Tool use and verification | Refuses infinity and not-a-number inputs, and checks that the sum is finite too. |
| Five decisions | Governance and ethics | Owner, threshold, retention, consultation and recourse, made by people before the form is filled. |
| Fluency without support | Next-token prediction and sampling | A confident, well-formed answer that nothing in the loop checked against a source. |
| Forbidding prediction | Supervised capstone | A prediction that rules outcomes out, so some result could prove it wrong. |
| Format vs support | Prompt contracts and evaluation | A well-formed answer can be unsupported, so the two are checked separately. |
| Four ledgers | MCP from scratch | Protocol, capability, permission, evidence: four questions kept apart. |
| Four parties | MCP from scratch | Server, host, Claude, and the people and policies that set authority. |
| Four separate events | Tools and permissions | Preflight passing, runtime permission, the operation and diff review are different events. |
| Freshness is not truth | Memory and multiple agents | Newer or unexpired does not mean correct; fresh depends on the use. |
| Gap Account | Supervised capstone | The audit-note's record of what the review could not reach, and who is accountable. |
| Gate | Chat, assistant, agent | A decision written before any grant: required, granted, refused, target, when control returns, and what passes. |
| Gate | Tools and permissions | A checkpoint set before the code: work moves on only when your own tests pass. |
| Gate | Claude Code and diff review | Reproduction, test and scope, written before the patch, that must hold before it moves on. |
| Gate | Training and configuration | Written before the run: the change, the objective, the held-out set and the stop rule. |
| Gate | Tool use and verification | The contract, tests and evidence matrix written before the run, with who decided each item named. |
| Gate (conduct) | Next-token prediction and sampling | Written before the output exists: what must hold, what to refuse, which test fails a wrong version. |
| Gate and exit table | The agent loop | Exits and checks written before any code runs. |
| Gates | Supervised capstone | Each consequential proposal tied to the exact content a named person approved, with an expiry. |
| Generalization | Training and configuration | Doing well on cases beyond those used to fit; it needs its own evidence. |
| Generic approval prompt | Evaluation and approval gates | An “Allow?” question that hides what the yes covers. |
| Generic risk language | Governance and ethics | Worries like “bias or privacy concerns” that fit any register and tell nobody what to do. |
| Gradient | Training and configuration | How the average loss changes as each parameter changes. |
| Gradient descent | Training and configuration | Subtract rate times gradient from each parameter, again and again. |
| Grant | Chat, assistant, agent | The abilities actually handed to the system. |
| Habituation | Evaluation and approval gates | Reflexive clicking that sets in when prompts outnumber the attention available. |
| Handoff | Supervised capstone | The seam where the packet passes to someone else, who must be able to run it unaided. |
| Handoff condition | Tools and permissions | A condition a stranger can test from the record: operation, target, approver, timing. |
| Handoff condition | Planning before acting | What one step must hand the next, stated so a stranger can check it. |
| Held-out questions | Prompt contracts and evaluation | Cases sealed until the revision is frozen; once used they become development. |
| Held-out set | Training and configuration | Points fixed beforehand and never passed to training; separate, not automatically typical. |
| Hidden parameter | Next-token prediction and sampling | An assumption inside a headline number that nobody stated. |
| History matters | MCP from scratch | The same message can pass or fail depending on what came before it. |
| Host | MCP from scratch | Software around Claude that builds requests and controls what enters context. |
| Human gate | Governance and ethics | A gate that passes when a named person accepted each role and the routes work when used. |
| Human in the loop | Tools and permissions | A person in the approval path; asked too often, the answer drifts toward yes. |
| Human in the loop | Governance and ethics | Counts only when the human task, evidence, authority, time budget and stop rule are named. |
| Idempotency key | Memory and multiple agents | A token that makes repeating an action have one effect. |
| Identifier | Tool use and verification | A label on each request that its result repeats, so each result is paired with its request. |
| Incident state machine | Memory and multiple agents | States richer than pass or fail: active, challenged, paused, reviewed. |
| Incomplete | The agent loop | The policy ran out before any finish or limit. |
| Independence | Memory and multiple agents | Two routes are independent only if they would not fail for one reason. |
| Independent check | Tool use and verification | A check that fails differently from the thing it checks, so it can say no. |
| Initial judgments first | Memory and multiple agents | Collect each person's judgment before anyone sees a synthesis. |
| Initialize request | MCP from scratch | First message; the reply gives version and capabilities, and the server is initialized. |
| Initialized notification | MCP from scratch | Follow-up with no id and no reply; it makes the server ready. |
| Inspect state | Supervised capstone | Check what ended up true, not only that the planned calls ran. |
| Insufficient | Retrieval and Cowork | On topic, but the passage does not settle the claim. |
| Interoperability | MCP from scratch | Whether two programs can exchange messages both understand. |
| Intervention | Training and configuration | What happens if we do something; observational data alone cannot settle it. |
| JSON-RPC | MCP from scratch | The message format: jsonrpc 2.0, an id, a method. |
| Last-writer-wins | Memory and multiple agents | The later write replaces the earlier one with no check. |
| Laundering | MCP from scratch | An unchecked output gains authority from the clean steps it passes through. |
| Learning rate | Training and configuration | A setting you choose that scales each step; it is never learned. |
| Least privilege | Chat, assistant, agent | Give a tool only the access its task needs. |
| Least privilege | Tools and permissions | Grant the smallest set of operations the task needs; each one must later be verified. |
| Lexical similarity | Retrieval and Cowork | Overlap in the actual words, not in meaning. |
| Lifecycle | MCP from scratch | The fixed order of a connection: initialize, then the notification, then tool use. |
| Lineage | Memory and multiple agents | The chain a claim was derived from; copies of one root are one source. |
| Linear score | Training and configuration | The number a = w x + b, before any squashing; it can be any size. |
| Lock (process-local) | Memory and multiple agents | One thread at a time may check and write, within this one object. |
| Lookup environment | The agent loop | The fixed records the lookups read. |
| Loss | Training and configuration | How far a predicted probability sits from the label; confident and wrong costs most. |
| Lossy label | Chat, assistant, agent | The label drops order, repeats, targets, results and authority, so keep the trace. |
| Lowest sufficient | Chat, assistant, agent | The smallest surface that covers the task. Smaller is not better if the task needs more. |
| Machine gate | Governance and ethics | A gate that passes when a list of tests you can run passes; here, the validator. |
| MCP | MCP from scratch | A shared message structure for host and server; it chooses nothing and vouches for nothing. |
| Meaningless packet | Supervised capstone | Ten long files of repeated x that pass, showing length is not substance. |
| Memory (stored state) | Memory and multiple agents | A dictionary of records under keys, kept outside the model. |
| merge_ready | Claude Code and diff review | True only when the reasons list is empty; a summary of inputs, not proof. |
| Misleading description | MCP from scratch | A description in context is more text, and can steer tool choice before any check. |
| Missing set | Chat, assistant, agent | R minus C: what the task needs and the surface lacks. Empty means covered, and nothing more. |
| missing_fields | Planning before acting | Lists the fields whose value is absent or false-valued, in the order of FIELDS. |
| Missing-field check | Governance and ethics | A field is missing when its key is absent or its value is None, empty text or an empty list. |
| Model-backed policy | The agent loop | A model picks the actions; the limits stay put. |
| Mutable object | Training and configuration | The one part of a system a change edits: weights, prompt, context, tools or settings. |
| Narration | Chat, assistant, agent | The system's own prose about what it did: shows what was said, not what happened. |
| Narrowing scope | Governance and ethics | Keeping the work but cutting data, authority or retention until the risk can be handled. |
| Negative space | Claude Code and diff review | The checks not run and files not inspected, listed in the packet. |
| Next-token prediction | Next-token prediction and sampling | Given the text so far, a score for every possible next token. |
| No automatic retry | Memory and multiple agents | After a stale rejection, reread and compare; never just retry. |
| Non-purpose | Supervised capstone | A written line on what the workflow will not do, giving reviewers a scope-drift test. |
| Nonblank check | Prompt contracts and evaluation | The answer must hold text once surrounding spaces are stripped. |
| Normalization by length | Retrieval and Cowork | Dividing by the vector lengths so a long text does not win by size. |
| Not a truth guarantee | Next-token prediction and sampling | Concentrating on a favorite adds no evidence that it is correct. |
| Not checked line | Tool use and verification | The sign-off line listing what the record does not show; a drafted sign-off tends to leave it out. |
| Not checked line | Governance and ethics | The sign-off line naming what the author did not verify; an AI-written sign-off leaves it out. |
| Not-waterfall rule | Planning before acting | A plan is revised, with the reason recorded, when a result contradicts it. |
| Objective | Training and configuration | The average loss the update is told to lower; a choice made before training. |
| Observation | The agent loop | What came back: a value, not found or an error. |
| Observed | Chat, assistant, agent | You saw the changed state yourself. |
| Observed frequency | Next-token prediction and sampling | The share of draws that landed on an outcome in one run. |
| One-object test | Training and configuration | Change one object, hold the rest fixed, repeat the runs, and see what follows. |
| Operation allowlist | Tools and permissions | Only read and write may run; any other operation is refused first. |
| Operation vs outcome | Tool use and verification | A tool result reports an operation; a reader's word like saved or sent claims an outcome. |
| Operational record | Governance and ethics | A statement a stranger can test: signal, threshold, owner, response, scope, recovery. |
| Optimistic concurrency | Memory and multiple agents | Work proceeds unlocked; at commit the writer hands back the version it read. |
| Order preserved | Next-token prediction and sampling | At any positive temperature a higher score never gets less probability. |
| Out of scope | Claude Code and diff review | The reason returned when a changed file is not on the allowed list. |
| Outcome check | The agent loop | A check outside the controller against the record. |
| Outcome check | Evaluation and approval gates | Reading the real state after the action instead of trusting the agent's sentence. |
| Output contract | Prompt contracts and evaluation | The shape the prompt asks for: a JSON object with exactly answer and sources. |
| Owner | Governance and ethics | The person who accepts the workflow as a continuing system and may stop it. |
| Parent traversal | Tools and permissions | A request using .. to climb out of the folder; where it lands decides, not the dots. |
| Pass rate | Prompt contracts and evaluation | Accepted responses divided by responses supplied: here 1 of 3. |
| Path | Tools and permissions | Directions for finding a file; a relative one is read from a starting folder. |
| Pause authority | Governance and ethics | The owner's explicit power to halt the workflow, with a backup when the owner is unavailable. |
| Permission policy | Tools and permissions | A short contract written first: root, operations, who approves a write, what must be refused. |
| PermissionError | Tools and permissions | The error the function raises to refuse a proposal. |
| Persistent change | Chat, assistant, agent | An edit still there after the chat ends, such as a saved file. |
| Persona | Prompt contracts and evaluation | A role line such as You are an expert; it adds no source and changes no check. |
| Plan | Planning before acting | The decisions on problem, boundary, order, evidence and stopping, written down where another person can challenge them. |
| Plan | Supervised capstone | Evidence-producing steps with dependencies, stop conditions, budgets and replanning triggers. |
| Plausibility audit | Claude Code and diff review | Your own model of how it should behave, applied before any source is consulted. |
| Plausibility auditing | Evaluation and approval gates | Judging whether a claim is credible, however confidently it is stated. |
| Policy | The agent loop | Supplies the next action; here a prepared list. |
| Pre-mortem | Supervised capstone | Failures predicted before the run, each with a detector, owner, response and leftover risk. |
| Predict versus record | Planning before acting | The plan states predictions; the result records what happened; keep the two apart. |
| Prediction | Training and configuration | What the fitted function outputs for an input; a statement about the model. |
| Prediction loop | Next-token prediction and sampling | Sample one token, append it, ask again, until an ending comes. |
| Preference tuning | Next-token prediction and sampling | A second stage that shifts parameters toward replies raters preferred. |
| Preflight | Tools and permissions | A check on a proposed operation before anything is done; it returns a path and no more. |
| Premortem | Memory and multiple agents | List how it could fail; give each failure a control and a residual risk. |
| Pretraining | Next-token prediction and sampling | Fitting parameters so the token that really followed gets more probability. |
| Primary generator | Planning before acting | The first, often unspoken idea of what the task is about; it decides which solutions you can see. |
| Probability distribution | Next-token prediction and sampling | One nonnegative share per token, all summing to one. |
| Problem formulation | Planning before acting | Choosing which problem the plan is for, before any step is ordered. |
| Prompt | Training and configuration | Instruction text given as input; a file you can compare and revert. |
| Prompt is a request | Supervised capstone | A prompt is a request, not a boundary: only a missing capability stops an action. |
| Proposal versus grant | Tools and permissions | A proposal suggests an action; only a person with authority grants it. |
| Proposed | Chat, assistant, agent | A response offers the action. |
| Proposes vs executes | Tool use and verification | Claude emits a request as data; your own program does the exact work and reports the returned value. |
| Proposes, you authorize | Chat, assistant, agent | The model may propose an action; only a person authorizes it. |
| Protocol vs verification | Tool use and verification | A loop can end cleanly with a false final sentence. Finishing describes machinery; verifying describes the claim. |
| Protocol-level error | MCP from scratch | A reply with an error code; the tool never ran. |
| Provenance | Prompt contracts and evaluation | The record of where a response came from: prompts, sources, model label, date. |
| Provenance | Memory and multiple agents | Where a value came from; a label alone does not prove it. |
| Python constrains | Supervised capstone | Claude drafts and proposes; code fixes what must be identical every time. |
| Quarantine state | Memory and multiple agents | A suspect record kept out of prompts but kept for incident review. |
| Re-engagement trigger | Memory and multiple agents | An event, not an attitude, that sends work back to reopen a decision. |
| Readiness | MCP from scratch | The state in which the server will do tool work. |
| Ready-for-human-review | Governance and ethics | The status when every structural check passed; it is not approval, consent or compliance. |
| Reasons list | Claude Code and diff review | Every failed obligation, collected, so more than one failure stays visible. |
| Recall and distractors | Retrieval and Cowork | A larger k finds more useful passages and more off-topic ones. |
| Recorded exclusions | Evaluation and approval gates | A written list of what the set does not cover. |
| Recourse path | Governance and ethics | The whole route from report to correction, not just an email address. |
| Recovery by repetition | Supervised capstone | Rerunning the same prompt until a wanted answer appears, with no reviewed change. |
| Refusal case | Evaluation and approval gates | A case whose correct outcome is to stop. |
| Refusal path | Planning before acting | A route for missing authority, evidence or checks: keep state and report what blocks the next step. |
| Refusal state | Prompt contracts and evaluation | A way to say the sources do not answer; this contract has none. |
| Register | Governance and ethics | A record of the owner, purpose, data, retention, approver, evaluation and incident contact for one AI workflow. |
| Regression test | Claude Code and diff review | A test written before the fix that fails on the defect and passes on the intended rule. |
| Relevant vs supported | Retrieval and Cowork | Scoring well or being on topic is not the same as backing a specific claim. |
| ReLU | Next-token prediction and sampling | Sets every negative value to zero: max(0, x). |
| Repeatability | Next-token prediction and sampling | Same call, same result; it says nothing about being true. |
| Repetition ≠ evidence | Tool use and verification | Running the same helper twice repeats its answer, bug included. Agreement is not corroboration. |
| Repetition detector | The agent loop | A rule that flags or stops on a repeat. |
| Replay | Evaluation and approval gates | Presenting the same valid decision again to get the effect again. |
| Reproduction | Claude Code and diff review | The smallest legitimate case that shows intended and current behavior differ. |
| Request id | MCP from scratch | Pairs each reply with its request; not truth. |
| Request versus check | Prompt contracts and evaluation | A prompt asks the producer; a validator decides after the answer arrives. |
| Required set | Chat, assistant, agent | The operations a task needs, written R. |
| resolve() | Tools and permissions | Follows links and removes .. parts to find the real destination, without opening it. |
| Retention lifecycle | Governance and ethics | Every copy of the data, how long it lives and how deletion is checked; retention_days is one input. |
| Retrieval | Retrieval and Cowork | Ranking documents by a stated score so a person inspects the top ones first. |
| Retrieval | Training and configuration | Choosing which stored passages go into this turn's input. |
| Retriever contract | Retrieval and Cowork | The behaviours the retriever must have, written before it is built. |
| Retrospective blessing | Claude Code and diff review | A test written after the patch, with expected values taken from the patch. |
| Reversibility | Planning before acting | Whether a change can be undone decides how much human approval it needs. |
| Review budget | Evaluation and approval gates | How many proposals a reviewer can read carefully in a period; an assumption unless measured. |
| Review gate | Planning before acting | Nothing changes until a person has reviewed the plan and a stated condition holds. |
| Review packet | Claude Code and diff review | Issue, test, plan, diff, outputs and decision, all pointing at the same version. |
| Review-required | Governance and ethics | The status when a check found an issue, such as an unknown class or an external write. |
| Reviewed recovery | Supervised capstone | A person or stated policy finds why it failed, changes the plan, rechecks independently. |
| Revision as hypothesis | Prompt contracts and evaluation | A prompt change is a prediction to test, changing one identifiable feature. |
| Revision boundary | Memory and multiple agents | What one version number covers, decided before any worker runs. |
| Revocation | Evaluation and approval gates | Withdrawing a decision that has not yet expired. |
| Right to withhold | Evaluation and approval gates | The signer's option to decline when the record does not support signing. |
| Role contract | Memory and multiple agents | A worker's inputs, task, tools, output, budget and escalation, written down. |
| Runtime enforcement | Tools and permissions | A rule held by code that raises an error, so the wording of a request cannot talk past it. |
| Same score, other error | Governance and ethics | Equal accuracy can hide different errors that cost different people. |
| Sampling | Next-token prediction and sampling | Drawing outcomes at random, weighted by the distribution. |
| Sandbox | Tools and permissions | An environment that limits what a process can do, whatever the code asks. |
| Scope of a pass rate | Prompt contracts and evaluation | It describes one validator on these cases, not accuracy or real-world frequency. |
| Score (logit) | Next-token prediction and sampling | A raw number per outcome: an ordering, not chances. |
| Scrutiny | Chat, assistant, agent | How hard the output must be checked; set by the work, not by the permissions. |
| Seam | Tools and permissions | A handoff trusted on arrival: say what passes, what it is trusted to be, how that was earned. |
| Second input | Claude Code and diff review | A test case that separates the intended rule from a convenient wrong one. |
| Seed | Next-token prediction and sampling | A starting value that fixes the random sequence so a run can be replayed. |
| Selection record | Retrieval and Cowork | A note naming each narrowing from corpus to what Claude saw. |
| Self-attention | Next-token prediction and sampling | The learned part that lets each token choose which tokens to read from. |
| Semantic review | Planning before acting | A person asks if each entry is meaningful, authorised and tests the claim. |
| Server | MCP from scratch | The program that offers tools and describes them. |
| Server self-description | MCP from scratch | What a server says about itself is its own claim, not evidence of behavior. |
| Settings | Training and configuration | Run-time choices for how output is drawn from scores; they fit nothing. |
| Seven required fields | Governance and ethics | Owner, purpose, data classes, retention days, approver, evaluation, incident contact; each opens a question. |
| Shared assumption | Tool use and verification | An input or source both routes rely on; a flaw there fools both checks together. |
| Shared author | Claude Code and diff review | Test and patch from one author: one misreading sits on both sides and cancels. |
| Ship/narrow/defer/stop | Supervised capstone | The four final choices; evidence informs the choice and a named person owns it. |
| Sigmoid | Training and configuration | Squashes any score into a probability between 0 and 1; a score of zero gives one-half. |
| Sign-off | Prompt contracts and evaluation | A statement of what was checked, how, what was not, and what is not claimed. |
| Sign-off | Chat, assistant, agent | A statement you can put your name to, with a Not checked line. Signed or withheld. |
| Sign-off | The agent loop | A closing claim from your own record. |
| Sign-off | Tools and permissions | A closing statement of what was checked, what was not, and what is not claimed. |
| Sign-off | Claude Code and diff review | A statement with your name: what was checked, what was not, and the strongest verb. |
| Sign-off | Retrieval and Cowork | A statement of what was checked, how, what was not, and what is not claimed. |
| Sign-off | Training and configuration | A closing statement: what was checked, how, what was not, and what is not claimed. |
| Sign-off | Planning before acting | A statement of what was checked, how, what was not, and what is not claimed. |
| Sign-off | Tool use and verification | A closing statement of what was checked, how, what was not checked and what is not claimed. |
| Sign-off | Memory and multiple agents | A statement of what was checked, how, what was not, and what is not claimed. |
| Sign-off | Evaluation and approval gates | The statement a builder signs about the gate built, with a line for what was not checked. |
| Sign-off | Governance and ethics | A closing statement of what was checked, how, what was not, and what is not claimed. |
| Sign-off | Supervised capstone | A closing statement of what was checked, how, what was not, and who cleared it. |
| Sign-off (check) | Next-token prediction and sampling | Checked, how, not checked, not claiming: no more than the record supports. |
| Silent omission | Retrieval and Cowork | Most narrowing stages leave no trace in the text of the answer. |
| Simulated approval | Tools and permissions | A True placed in a test and labeled a fixture, never credited to a person. |
| Simulated decision | Evaluation and approval gates | A made-up decision record from test code, labelled as such; not a person's sign-off. |
| Single-use consumption | Evaluation and approval gates | Checking and marking a decision used in one step, so a second use fails. |
| Six-field proposal | Evaluation and approval gates | A request naming action, target, reason, effects, evidence and rollback. |
| Small is not safe | Claude Code and diff review | One character can change every call, so review effort follows consequence. |
| Softmax | Next-token prediction and sampling | Exponentiates the scores, then divides by the total so they sum to one. |
| Source identifier | Prompt contracts and evaluation | A label such as s1 that points to a supplied source: an address, not support. |
| Source label | Memory and multiple agents | Caller-written text saying where a value came from. |
| Source support | Prompt contracts and evaluation | Whether the cited passage actually backs this particular claim. |
| Stale evidence | Claude Code and diff review | A check run before the last edit says nothing about the current diff. |
| Stale write | Memory and multiple agents | A write whose expected version is out of date: refused, nothing changes. |
| State check | Chat, assistant, agent | A before-and-after look at the folder, run against a rule you wrote. |
| State machine | MCP from scratch | Always in one state; only certain messages move it, so history decides what is accepted. |
| State update | The agent loop | The only change: an append to the trace. |
| Status versus evidence | The agent loop | Finished describes the loop, not the answer. |
| Stop condition | The agent loop | A rule that ends the run, set before it starts. |
| Stop condition | Claude Code and diff review | What must be true, with commands and exit status recorded, before the patch moves on. |
| Stop condition | Planning before acting | Three exits, complete, halt or defer, each with an observable trigger. |
| Stop reason | The agent loop | Why the run ended, read from status and budget. |
| Stop reason | Tool use and verification | The field saying why the model stopped: end_turn, tool_use or max_tokens. The loop branches on it. |
| Stop rule | MCP from scratch | A rule written into the host so a missing record is reported, not guessed. |
| Stop rule | Training and configuration | How many updates, fixed in advance; no early stop, no extra steps after peeking. |
| String-prefix check | Tools and permissions | Comparing characters: course-other wrongly matches course. |
| Structural check | Prompt contracts and evaluation | Tests the form of an answer, not whether its content is right. |
| Structural check | Planning before acting | A check on form only: it rejects absence, not poor content. |
| Structural gap | Supervised capstone | A gap owing to the reviewer's kind and access, so rerunning it will not close it. |
| Structural validity | Evaluation and approval gates | Every required field is filled; says nothing about whether the content is adequate. |
| structurally_complete | Supervised capstone | The flag that reads True when no file is missing, escaping or too short. |
| Structure vs substance | Supervised capstone | A machine checks files and sizes; truth and trust need evidence and a person. |
| Subtract the max score | Next-token prediction and sampling | Shifting every score by the maximum leaves the probabilities unchanged. |
| Supervision gap | Chat, assistant, agent | Level of the work minus level of the review. The risk is the gap. |
| Support review | Prompt contracts and evaluation | A person compares each claim with the source text, claim by claim. |
| Survivor | Claude Code and diff review | A wrong version that still passes every current test. |
| Symbolic link | Tools and permissions | A name in a folder that redirects to another place, maybe outside it. |
| Synonym map | Retrieval and Cowork | A word-to-word table applied before scoring; a person decides each pair. |
| Synonym miss | Retrieval and Cowork | A same-meaning document scores zero because no token is shared. |
| System prompt | Next-token prediction and sampling | A paragraph near the top of that string: a request, not a gate. |
| Target aliasing | Evaluation and approval gates | Different strings naming one file, or one string naming different files. |
| Task packet | Retrieval and Cowork | The bounded brief: goal, permitted sources, output format, exclusions, checks. |
| Teaching surface | Chat, assistant, agent | An exercise label, not a product map. |
| Temperature | Next-token prediction and sampling | Divides the scores first: low piles probability on the top, high flattens. |
| Test coverage gap | Prompt contracts and evaluation | A contract line that no test would notice missing. |
| Test the permitted side | Tools and permissions | Add a success test, so a policy that refuses everything cannot pass. |
| Three jobs | Supervised capstone | Conduct decides before building, check finds faults and signs, drive keeps the choices. |
| Three review outcomes | Prompt contracts and evaluation | Supported, contradicted, or cannot be reviewed, defined before reading outputs. |
| Threshold | Training and configuration | The cutoff that turns a probability into a decision; you choose it, training never sees it. |
| Threshold | Governance and ethics | The observable signal that triggers a response, and what the response is. |
| Tie-breaking | Retrieval and Cowork | Equal scores are ordered by document key. |
| Time boundary | Tools and permissions | The gap between check and use; the check does not freeze what happens later. |
| Token | Next-token prediction and sampling | A fragment from a fixed list; the unit the model predicts, not a word. |
| Tokenization | Retrieval and Cowork | Cutting text into tokens by a fixed rule; here, lowercase runs of word characters. |
| Tokenizer | Next-token prediction and sampling | The program that cuts text into entries from the vocabulary. |
| Tool call | Tool use and verification | A request from Claude naming a tool, its arguments and an id. It is a proposal, not an execution. |
| Tool error | MCP from scratch | A result flagged isError true; the tool ran. |
| Tool error | Tool use and verification | A refused call returned as a result marked is_error, so the model can see what failed and why. |
| Tool schema | MCP from scratch | The input shape a tool accepts, advertised in its listing. |
| Tool schema | Tool use and verification | The description of a tool and its arguments shown to Claude. It shapes requests but enforces nothing. |
| tool_result block | Tool use and verification | The message block that carries the tool's output back, tagged with the request's identifier. |
| Tools | Training and configuration | Actions and sources the host exposes, plus the rules that allow them. |
| tools/call | MCP from scratch | Request naming a tool and its arguments; the reply is a result or an error. |
| tools/list | MCP from scratch | Request, once ready, for the tools that exist and what they accept. |
| Top-k | Retrieval and Cowork | Keep only the k best; other positive matches are dropped. |
| Topological ordering | Planning before acting | Take every step with no waiting prerequisite, sorted by id, remove it, and repeat. |
| Trace | The agent loop | Turn, action and observation for each turn. |
| Training | Training and configuration | Changing parameters with an objective and an update rule; nothing else counts. |
| Transcript | Next-token prediction and sampling | One string of role-marked text that is completed, and resent whole each turn. |
| Transformer | Next-token prediction and sampling | A design that reads the whole context at once, with attention and feed-forward parts. |
| Turn | The agent loop | One pass of the loop; it uses one action. |
| Turn budget | The agent loop | The most turns the loop may begin. |
| Turn budget | Tool use and verification | The cap on turns. It ends endless looping but does not show progress or safety. |
| Two stops | The agent loop | Ending the run versus closing the task. |
| Unified diff | Claude Code and diff review | A listing of the lines removed (-) and added (+) between two versions. |
| Unit of the budget | The agent loop | One count is one action taken; finish costs one. |
| Unknown prerequisite | Planning before acting | A step waits on an id that is not in the plan. |
| Untrusted content | MCP from scratch | Text a tool returns is data; a successful reply does not make it true. |
| Validate in Python | Supervised capstone | Code checks the tool exists, the arguments are valid and the path stays inside the root. |
| validate_packet | Supervised capstone | A function that checks ten named files: inside the folder, present, at least 40 characters. |
| Validator | Prompt contracts and evaluation | Code that checks a returned object against executable conditions. |
| Values claim | Governance and ethics | Choosing which error or equality matters is a decision with an owner, not an optimization. |
| Values decision | Planning before acting | Choosing whose interests the framing centers, and saying who it leaves out. |
| Variation between runs | Next-token prediction and sampling | Same question, different answers, model unchanged; the cause must be isolated. |
| Verb ladder | Claude Code and diff review | Eight verbs, hypothesize to prove, each needing more evidence than the last. |
| Verb ladder | Governance and ethics | Listed, confirmed, exercised, verified: use the weakest verb the evidence supports. |
| Verifiability first | Tool use and verification | Pick the most constrained tool that does the step, because that is the one you can check. |
| Verification | Claude Code and diff review | Consulting a source, such as a test run or a recomputation. |
| Verification costs | Supervised capstone | A graph takes a minute to draft; opening each edge takes real time, so budget for it. |
| Verification surface | Tool use and verification | Evidence a tool leaves for checking: resolved path, read-back, diff, tests, remote state. |
| Verified | Tool use and verification | A word reserved for a claim whose check came from outside the route that produced it. |
| Version | Memory and multiple agents | A revision counter for one key; it orders commits, not truth. |
| Version zero | Memory and multiple agents | What a missing key returns: no write yet, not a stored null fact. |
| Vocabulary | Next-token prediction and sampling | The fixed list of token fragments, tens of thousands long. |
| Volume trap | Claude Code and diff review | Output grows with the machine, reading does not, and the gap goes unverified. |
| Volume trap | Evaluation and approval gates | Output grows tenfold but verification does not, so more goes unreviewed. |
| Weights | Training and configuration | The saved numbers inside the model; only training edits them. |
| Withholding | Governance and ethics | Declining to sign when the evidence does not support it, then narrowing or deferring. |
| Workflow vs model-led | Chat, assistant, agent | A program fixes the steps, or the model directs its own process. Either can write. |
| Write approval | Tools and permissions | An extra condition for writes; being inside the root does not waive it. |
| Wrong versions | Tools and permissions | Deliberately broken copies of the function that your tests must fail. |
| Zero filter | Retrieval and Cowork | Documents with no shared token are removed before the cutoff. |
