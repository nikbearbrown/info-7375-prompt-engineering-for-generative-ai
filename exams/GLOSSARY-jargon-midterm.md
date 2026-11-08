# INFO 7375 jargon glossary: say it exactly

This is a language test. Precise words let you tell a language model, or Claude Code, exactly what to do. "Set the temperature to zero" gets one behaviour; "make it less random" gets a guess.

Each table gives a term and one plain sentence. A term appears once, under the first set that tests it. Terms are listed as the question sets teach them; check the set's questions for the contrasts.


## Foundations

| Term | Meaning |
|---|---|
| rule-based system | a system whose output comes from conditions a person wrote by hand |
| generalization | a learned model's ability to give sensible output on inputs beyond its training examples |
| overfitting | fitting training examples so closely that performance on new inputs is poor |
| self-supervised pretraining | training on raw text where the next token is the label, with no human labelling |
| scaling | increasing data, parameters and computation together |
| fine-tuning | further training of a pretrained model on narrower data, which changes the weights |
| model / weights | a learned function; its learned parameters |
| training vs inference | weights are adjusted in training; they are fixed while producing output |
| knowledge cutoff | the point after which the training data holds no events |
| context / context window | the tokens the model can take in at one time; not memory across conversations |
| retrieval | adding source text to the context; it changes what the model sees, not the weights |
| logits | raw unnormalized score for each token in the vocabulary |
| softmax | step converting logits to probabilities that sum to one |
| temperature | scaling of logits before softmax: low sharpens, high flattens |
| top-p (nucleus) sampling | sampling from the smallest set of tokens whose probabilities reach p |
| greedy decoding | choosing the highest-probability token at each step |
| sampling / seed | drawing the next token at random by probability; a seed makes the draws reproducible |
| autoregressive | each generated token is appended to the input for the next step |
| token / token ID | unit of text from the tokenizer; integer label for it |
| vocabulary | the tokenizer's list of tokens |
| embedding / embedding dimension | dense vector for a token, learned in training; the length of that vector |
| one-hot vector | vector as long as the vocabulary with a single 1 |
| self-attention | weighted mixing of information from tokens in the context |
| encoder vs decoder | encoder builds representations of a whole input; decoder generates left to right from earlier tokens |
| feedforward network (MLP) | layered nonlinear map applied to each token's vector |
| positional encoding | position information added so order matters |
| system prompt vs user turn | standing instructions for a conversation vs one message from the user |
| pure function / unit test | deterministic function without side effects; check of a function against an expected output |
| acceptance gate | a check or human decision an output has to pass before it is accepted |
| prompt contract | a statement of task, constraints, output form and acceptance checks |
| planning before acting / diff review | stating steps before editing; reading line-level changes before accepting |
| JSON / schema / factual validity | parses; has the right fields and types; true |
| held-out cases | cases kept apart from those used to revise a prompt |
| eval vs test | scored over many cases for a nondeterministic system vs deterministic expectation |
| policy / controller / observation | model that proposes; program that executes and enforces limits; result returned |
| agent vs workflow | model chooses its steps in a loop vs a path fixed in code |
| permission vs approval gate | rule on allowed actions vs human confirmation before an action |
| tool_use / tool_result | model's request to call a tool; the output returned to the model |
| MCP server / client | provider of tools or resources; the part of the host that connects to it |
| solve-verify asymmetry | checking a solution is often easier than finding it |
| hallucination | fluent output that states something false or unsupported |
| falsifiable | a claim for which an observation that would show it wrong can be named |

## Chapter 1: Next-token prediction and sampling

| Term | Meaning |
|---|---|
| token | a unit of text the tokenizer produces (a word, a fragment of a word, or punctuation) |
| tokenizer | the component that converts text to token IDs from a fixed vocabulary and back |
| context window | the maximum number of tokens a model can take in on one call, shared by prompt and reply |
| parameters (weights) | the learned numbers in the model, fixed during inference |
| stateless API | a service that keeps no conversation between calls, so the caller resends the history |
| max_tokens | a setting that caps the number of output tokens, counted in tokens not words |
| embedding | a learned vector of numbers representing a token |
| attention | the mechanism that mixes information across token positions |
| feed-forward step | the per-token transformation inside a layer using learned parameters |
| positional information | information added so the model can tell word order |
| interpretability | the study of what a model's internal parts compute |
| attention weight | how much one token draws on another in a layer, not a causal explanation |
| top-k | truncation to the k highest-probability tokens |
| top-p (nucleus) | truncation to the smallest set of top tokens whose cumulative probability reaches p |
| sampling | drawing the next token at random in proportion to its probability |
| beam search | keeping several candidate sequences and favouring high overall sequence probability |
| seed | a value fixing the random-number stream used in sampling |
| time to first token | the delay before the first generated token appears |
| streaming | showing tokens as they are generated |
| overflow | a number too large to represent, which becomes infinity |
| pretraining | training a base model on next-token prediction over a large corpus |
| base model | a pretrained model that continues text and does not yet follow instructions |
| instruction tuning | further training on instruction and response examples |
| preference tuning | further training on human comparisons of replies |
| sycophancy | tendency to agree with the user over the facts |
| loss | the negative log of the probability assigned to the true next token |
| perplexity | a summary of average per-token uncertainty; lower fits the text better |
| causal masking | hiding later tokens during training so the model cannot copy the target |
| training cutoff | the point after which the training data holds no text |
| prompt injection | untrusted input text that tries to override the developer's instructions |
| calibration | stated confidence matching how often answers are right |
| verbalized confidence | a confidence number the model writes as generated text |
| token probability | the probability assigned to a generated token |
| repeatability vs correctness | the same output each time is not the same as a correct output |

## Chapter 2: Prompt contracts and evaluation

| Term | Meaning |
|---|---|
| output contract | a written statement, made before the prompt, of the output a consuming program accepts |
| validator | code that checks one response against fixed rules and accepts or rejects it |
| prompt template | reusable text sent to the model (not the checking code) |
| JSON mode | provider setting that guarantees syntactically valid JSON, not particular keys |
| schema-constrained decoding | generation restricted to tokens that keep the output conforming to a supplied schema |
| strict vs lenient validator | strict rejects unexpected keys; lenient ignores them |
| parse error / wrong shape / key mismatch / wrong type / bad value | ordered categories of validator failure |
| structural validity vs grounding | well-formed output vs content supported by the supplied sources |
| citation vs support | an identifier that exists vs a source whose text backs the claim |
| partial support | some claims in an answer supported and others not |
| abstention | declining to answer when evidence is insufficient |
| ungrounded | not traceable to supplied evidence |
| eval | a measurement of a prompt over a set of cases |
| test case / test set / pass rate / metric | one input with its criterion / the list of cases / fraction accepted / summary number |
| code-graded, model-graded, human-graded | scored by a program, by a model, by a person |
| LLM-as-judge; position bias, verbosity bias, self-preference | model scoring; favouring first-shown, longer, or own-family text |
| judge calibration | measuring a grader's agreement with a standard such as human labels |
| development set vs held-out set | data used to revise a prompt vs data kept unseen until the revision is frozen |
| leakage / contamination | evaluation items reaching the prompt or tuning |
| few-shot prompting | including worked input-output examples in the prompt |
| overfitting; Goodhart's law | fitting tuning cases at the cost of new inputs; a measure that becomes the target stops measuring the goal |
| controlled comparison, confound, baseline | change one thing at a time; entangled explanations; the unchanged reference run |
| temperature, sampling noise | randomness of token sampling; run-to-run variation in a score |
| role prompt (persona line) | prompt text assigning the model a role |
| provenance, raw response, audit trail | where data came from; the unedited reply; a record another person can reconstruct from |
| constructed vs observed data | hand-written test strings vs replies returned by a model |
| model alias vs pinned snapshot | a moving name vs a fixed version |
| selective reporting; change log | leaving out failures; dated entries naming what changed and why |
| first-attempt vs final pass rate; severity | pass rate before vs after retries; how harmful a failure is |
| truncation, stop reason | a reply cut off at the output limit; the API field saying why generation ended |
| tool call, allowlist, least privilege, approval gate | structured request to run a tool; permitted-action list; narrowest access needed; human confirmation before an action |
| undetermined outcome | a third verdict for answers that cannot be judged |
| inter-rater agreement; kappa | consistency between reviewers; chance-corrected agreement |
| mutation testing; edge case | deleting a rule to test whether tests notice; boundary input such as an empty list |
| diff review; planning before acting | reading the changes an assistant made; having it propose a plan before editing |
| calibration (of stated confidence) | stated confidence matching observed accuracy |

## Chapter 3: Chat, assistant, agent

| Term | Meaning |
|---|---|
| chat | text-in, text-out system with no tools for acting on the outside world |
| agent | model that uses tools, usually in a loop, to take actions toward a goal |
| workflow | predefined code paths orchestrate the model and tools; code controls the sequence |
| model-directed (agentic) control | the model chooses the next step and when to stop |
| capability | an operation the system is able to perform with its tools |
| control | which party (code or model) chooses the next step |
| scrutiny | how closely output has to be checked, set by the stakes |
| tool_use | the model's structured request to call a named tool with arguments (not execution) |
| tool_result | outcome of the tool run, sent back to the model by the application |
| agent loop | cycle of choose action, execute, observe, decide whether to continue |
| iteration budget (stop condition) | harness-enforced limit on loop cycles |
| guardrail | a check around the model that limits damage when a step goes wrong |
| permission / authorization | a decision, by someone with authority, of what may be done, where and under what conditions |
| least privilege | grant the smallest capability set that completes the task |
| scope | the named target and limits of a grant |
| allowlist / denylist | list of permitted vs forbidden items; allowlist refuses the unrecognized |
| path normalization | resolving .. and links to the real location before checking |
| fail closed / fail open | refuse vs allow by default on unrecognized input |
| approval gate | pause before a step until a person decides |
| approval fatigue | reduced attention to prompts when they are frequent |
| exfiltration | private data leaving through an outbound channel |
| side effect | change beyond the returned value |
| idempotent | repeating the operation leaves the same end state |
| dry run / plan mode | show intended changes without applying them |
| snapshot (checkpoint) | copy taken before a write to allow comparison and restore |
| self-report (narration) | the system's own account of what it did |
| proposed / attempted / completed / observed | offered in text / request issued / runtime reported success / state looked at independently |
| diff | lines added and removed between two versions |
| audit log (append-only) | harness-written record of actions with target, result and approver |
| declared capabilities vs trace | what is possible vs what a particular run did |
| automation complacency | monitoring falls as automation seems reliable |
| fabricated record | invented fact, such as naming an approver who did not approve |
| simulated approval | test-harness auto-approval, not a human decision |
| grant specification | outcome, capabilities, refused operations, target, escalation condition, evidence, pass condition |
| escalation condition | when control returns to a person |

## Chapter 4: The agent loop

| Term | Meaning |
|---|---|
| policy | the part (the model) that proposes the next action |
| controller | the program around the model that executes actions, records results and decides whether to continue |
| action | what the policy proposes to do next |
| observation | the result a tool returns after an action |
| turn | one pass of propose, execute and observe |
| turn budget | an operator-set cap on loop iterations, enforced in the harness |
| timeout | a limit on elapsed time that can interrupt a call that hangs |
| status finished / incomplete / budget-exhausted | finish received / action source ran out before budget / allowed turns all used without a finish |
| finish action | the policy's request to stop, which does not itself verify the output |
| trace | the record of actions and observations, not of reasoning |
| workflow vs agent | predefined steps in code vs the model directing its own process |
| planning before acting | stating intended steps for review before any tool runs |
| polling, backoff, deadline | repeated status calls, growing waits between them, an elapsed-time limit |
| control layer vs evidence layer | whether the run ended vs whether the output is supported by evidence |
| outcome check | a comparison of the result against a reference outside the generator |
| independent check | one that does not share the generator's failure modes |
| claim vs evidence | testimony from the producer vs something confirmable without it |
| system of record | the authoritative place where the real state lives |
| sentinel value | a placeholder value such as not found that stands for absence |
| fabricated completion | a report of finishing an action that did not happen |
| false positive / false negative (detector) | stop on fine behavior / missed loop |
| repetition detector | a heuristic that stops or flags a run on repeated actions |
| grounding | tying an answer to named evidence |
| stop_reason | tool_use (model requests a tool), end_turn (natural finish), max_tokens (cut off at the output limit) |
| parallel tool calls | several tool_use blocks in one response |
| context window / prompt caching | per-request limit on text / reuse of an unchanged prefix to cut cost |
| allowlist | the set of actions a harness will dispatch |
| idempotency key | a token letting a service apply a repeated request once |
| canonical path / symbolic link / path traversal | resolved absolute path / link pointing elsewhere / .. escaping a directory |
| mutation testing | injecting deliberate faults to see whether tests catch them |
| specification before implementation | writing intended exits and behavior before code exists |
| diff review | reading what an assistant changed before accepting it |

## Chapter 5: Tools and permissions

| Term | Meaning |
|---|---|
| path traversal | using parent components in a requested path to climb out of an approved directory |
| parent component (`..`) vs current directory (`.`) | two dots move up one level; one dot stays |
| symbolic link | a directory entry that stores a pointer to another path |
| hard link | a second name for the same underlying file contents |
| resolve | follow links and dot components to the real absolute destination |
| normalize | lexical clean-up of dot components without consulting the filesystem |
| canonical path | the single absolute form with dot components removed and links followed |
| strict vs non-strict resolve | strict raises when part of the path is missing; non-strict computes a destination anyway |
| containment check | test that a resolved target lies inside a resolved root, compared by path components |
| sibling-directory (prefix) flaw | string prefix matching accepts /data/course-private for root /data/course |
| approved root | the directory a tool is allowed to reach; chosen by a responsible person |
| fail closed | when unsure or on error, refuse |
| allowlist vs denylist | permit only what is named versus refuse only what is named |
| default deny | a request not explicitly permitted is refused |
| need to know | give the agent the information the task requires and no more |
| instruction vs control | a prompt request versus enforcement by code outside the model |
| deterministic check | gives the same verdict for the same input, so it is testable |
| permission vs approval | what the policy allows versus a person's consent to one specific action |
| scoped approval | consent bound to the exact action and target shown |
| audit log | record of operations, targets and decisions for later review (detective) |
| reversibility | how readily an action's effect can be undone |
| confused deputy | an authorised program acts on a request from a less-trusted party |
| indirect prompt injection | instructions arriving through content the model reads |
| MCP server vs client | the server exposes tools; the client in the host connects and applies policy |
| tenant isolation / identity from session | identity comes from the authenticated application, not a model argument |
| TOCTOU | time-of-check to time-of-use race between a check and a later use |
| preflight check | a function that decides whether an operation is allowed without performing it |
| allow / ask / deny rules, deny first | allow proceeds, ask prompts a person, deny refuses; deny is evaluated first |
| bypass (skip-prompts) mode and sandbox | removes the approval gate; a sandbox limits reach at the operating-system level |
| schema vs policy | schema validates argument shape; enforcement belongs in the tool code |
| call budget | a limit on how many tool calls occur, distinct from a per-call permission verdict |
| defense in depth | independent stacked layers so one failure does not expose everything |
| rubber-stamping / approval fatigue | approving without reading because prompts are too frequent |
| independence of checkers | separate checks that do not repeat the same mistake |
| seam | the handoff between pipeline stages |
| authorized vs correct | permission answers whether an action is allowed, not whether the change is right |

## Chapter 6: Claude Code and diff review

| Term | Meaning |
|---|---|
| regression test | a test that checks behaviour that was fixed or established has not broken again; it fails on the unfixed code and passes after the fix |
| reproduction | the input, observed output and expected output that trigger a reported failure |
| diagnosis | the explanation of the cause of a failure |
| oracle | the trusted source of the expected value, such as the written requirement |
| mutant | a deliberately altered, wrong variant of code used to test a test suite |
| killed mutant / surviving mutant | a mutant the suite detects (fails on) / one the suite passes, pointing to behaviour not checked |
| equivalent mutant | a mutant that behaves the same as the original, so no test can kill it |
| known wrong implementation | a version the checks must reject, used to test the tests |
| hard-coding | returning the expected answer for the tested input without implementing the rule |
| weakening a test | editing an assertion to match the output instead of fixing the code |
| harness error vs test failure | an error stops the run before assertions about the patch; a failure is a false assertion |
| unified diff, hunk, context lines | textual change format; a hunk is a block of changes with surrounding unchanged lines |
| git diff vs git diff --staged vs git status | working tree vs index; index vs last commit; status lists untracked files |
| scope / allowed-file list / scope creep | the files the agent may change / the list itself / changes beyond it |
| scope check (set difference) | changed files minus allowed files; sees file names, not content |
| planning before acting (plan mode) | the agent proposes a plan and makes no edits until it is approved |
| permission rule (allow, ask, deny) | tool-level control of what Claude Code may do |
| hook | a user-defined command that runs at a point in the agent lifecycle and can block an action |
| CLAUDE.md (instruction file) | guidance the model reads; it is not enforcement |
| detective vs preventive control | finds a problem after the fact vs stops it happening |
| stale evidence | a result gathered before the code last changed |
| binding approval to a hash/digest | tying a decision to the exact version approved |
| plausibility judgment vs verification | the reviewer's own prediction before running vs a check against an external source |
| falsifiable prediction (verdict, target, mechanism) | a written prediction naming what would change the reviewer's mind |
| not-checked list | the stated limits of a sign-off |
| claim calibration | matching claim strength to evidence strength |
| verification vs validation | checking against the stated requirement vs checking that the requirement is right |
| contribution record / session transcript | what the agent drafted and the person decided, backed by the transcript |

## Chapter 7: Retrieval and Cowork

| Term | Meaning |
|---|---|
| bag of words | unordered counts of tokens; order discarded |
| case folding | lowercasing so capital and lowercase forms merge |
| term frequency | count of a term in a document |
| inverse document frequency | weight that is higher for terms found in fewer documents |
| BM25 | lexical ranking function building on tf-idf with saturation and length normalization |
| cosine similarity | dot product divided by vector lengths; angle between vectors |
| length normalization | dividing by vector length so long documents do not win on size |
| lexical retrieval | matching by shared words |
| dense retrieval | matching by meaning using embeddings |
| vocabulary mismatch | query and document use different words for the same idea |
| stemming | reducing word forms toward a common root |
| query expansion / synonym map | adding related terms to the query |
| query rewriting | model rewrites the user question into a search query |
| hybrid search | combining lexical and dense retrieval |
| reciprocal rank fusion | merging ranked lists by rank position |
| reranking | reordering candidates with a second model |
| top-k / cutoff / tie-break | count limit, score threshold, deterministic ordering rule |
| audit view | per-document score and fate listing |
| precision@k, recall@k, MRR | share of results relevant, share of relevant found, reward for early first hit |
| relevance vs entailment | topical closeness vs logical support |
| grounding / faithfulness | claims supported by sources |
| citation validity vs accuracy | marker points to a real passage vs passage supports the claim |
| claim decomposition, claim-to-source table, supported/contradicted/insufficient/not reviewed | evidence review |
| ingestion, corpus, source manifest, coverage gap | loading and completeness checks |
| chunk, chunk overlap | retrieval unit; repeated text at boundaries |
| provenance | record of source and version |
| retrieval vs fine-tuning | change the prompt vs change the weights |
| access control, indirect prompt injection, least privilege | security terms |
| spec, tests first, diff review | working with a coding assistant |

## Chapter 8: MCP from scratch

| Term | Meaning |
|---|---|
| host | the application that runs the model and mediates between it and MCP servers, deciding which tools are exposed and what enters context |
| MCP client | the component inside the host that holds the connection to one MCP server |
| MCP server | the program that implements capabilities (tools, resources, prompts) and describes them to clients |
| tool | a callable action a server offers, which the model can ask the host to run |
| resource | data a server exposes for context, identified by a URI |
| prompt (MCP) | a reusable template offered by a server, not the host's system prompt |
| transport | the channel carrying protocol messages; stdio for a local subprocess, HTTP for a remote server |
| stdio | transport in which the client launches the server as a subprocess and exchanges one JSON message per line over standard input and output |
| framing | the rule for where one message ends and the next begins (newline per message on stdio) |
| standard error | the separate stream for diagnostics, kept out of the protocol stream |
| JSON-RPC 2.0 | the message format of MCP, with requests, responses and notifications |
| request | a message with a method and an id that expects a response |
| notification | a message with a method and no id that receives no response |
| id | the identifier a response echoes so a request and its reply can be paired |
| parse error (-32700), invalid request (-32600), method not found (-32601), invalid params (-32602) | standard JSON-RPC error codes for unparseable text, a malformed request object, an unknown method and bad parameters |
| 32000 to -32099 | range reserved for implementation-defined server errors |
| initialize | the request that opens a session, carrying requested protocol version, capabilities and client information |
| notifications/initialized | the client's notification that it has finished initialization |
| protocol version negotiation | the server replies with a version it supports and the client decides whether to continue or disconnect |
| capability negotiation | each side declares optional features so both know what may be used |
| listChanged | the sub-capability announcing that a server may notify when its tool list changes |
| tools/list, tools/call | requests to discover tools and to invoke one |
| inputSchema | JSON Schema describing the argument shape of a tool |
| tool description | server-supplied free text, a claim and not verified evidence |
| annotation (readOnlyHint, destructiveHint) | advisory metadata a server publishes, not enforced by the protocol |
| isError | flag in a successful tool result reporting that the tool ran but failed at its task |
| lifecycle, request and task failure | the three layers of failure: wrong time, wrong method or arguments, and a valid call with a negative outcome |
| tool poisoning | injection carried in tool metadata that the model reads as context |
| prompt injection through tool output | instructions embedded in returned content, which is untrusted data |
| discovery versus permission | learning that a tool exists does not allow calling it; policy decides |
| authorization versus interoperability | whether a capability may run for a task versus whether parties understand each other's messages |
| allow-list | host policy naming which servers and tools may run |
| enforcement outside the model | controls in the host or process that hold even if the model is steered, unlike prompt instructions |
| conformance | behaving as the specification requires across states, not merely matching example message shapes |
| four questions | protocol, capability, permission, evidence, kept separate in a connection review |
| evidence types | advertised (the server's claim), source-inspected, executed (limited to the run, input and version), independently sourced, uninspected |
| uninspected | the honest entry for an item not examined, in place of asserting absence |
| ground truth | the declared source data a returned value is compared with, as opposed to a plausibility judgment |
| constructed versus live | hand-written test messages versus messages from a real host session, labeled apart |
| decision versus sign-off | the decision concerns the server; the signed statement concerns the evidence behind it |
| re-review trigger | a change, such as a new version, new tool or wider data scope, that reopens a decision |
| scoped claim | a statement limited to what the evidence covers, avoiding words like secure or verified without criterion |
| discrepancy request | asking an assistant to list disagreements with quoted lines and withholding a verdict |
| fine-tuning versus connecting a tool | training changes weights; a tool connection adds context and actions without changing them |

## Chapter 9: Training and configuration

| Term | Meaning |
|---|---|
| weights | learned numeric parameters of a model, changed only by training |
| prompt | instruction text sent with a request |
| system prompt | standing instruction supplied with each request |
| context | text supplied to the model in a request, including retrieved passages |
| memory | stored notes re-supplied in later prompts, not weight change |
| permission | host rule on what an agent may do |
| sampling setting | decoding control such as temperature or top-p |
| top-p | samples from the smallest token set whose probabilities add to p |
| logit | unnormalized score before softmax |
| reproducibility | others can re-run and obtain the same result |
| ablation | remove one component and measure the effect |
| few-shot example | worked input/output pair placed in the prompt |
| parameter vs hyperparameter | learned value vs chosen setting |
| learning rate | size of each gradient step |
| gradient | slope of the loss with respect to a parameter |
| epoch / batch / minibatch | full pass / data used for one update / small random subset |
| convergence / stopping rule | loss stops improving / criterion for ending training |
| loss function / cross-entropy | penalty on predictions; punishes confident wrong answers |
| sigmoid / weight / bias / threshold | score-to-probability map / feature influence / shift / decision cutoff |
| false positive / false negative | negative called positive / positive called negative |
| precision vs recall | share of predicted positives correct / share of actual positives found |
| training / validation / test data | fit / tune / final estimate |
| data leakage | evaluation data influencing training |
| multiple comparisons | best of many noisy scores is biased upward |
| numerical gradient check | finite-difference test of a derivative |
| association / intervention / counterfactual | rungs of the ladder of causation |
| confounder / Simpson's paradox | variable affecting both cause and outcome / reversal on pooling |
| distribution shift / feedback loop | changed data after deployment / predictions altering future data |
| pre-specification | plan and prediction fixed before results |
| identification | argument that a causal effect is estimable from data |

## Chapter 10: Planning before acting

| Term | Meaning |
|---|---|
| plan fields (objective, inputs, scope, steps, tools, risks, verification, stop) | the eight questions a plan answers: aim, starting material, what may change, ordered actions, permitted capabilities, ways to fail, evidence of success, exits |
| structural completeness | every plan field is present and nonempty; says nothing about meaning |
| semantic review | judging whether field contents are meaningful, consistent and adequate |
| cross-field review | comparing fields with one another to find contradictions (objective vs verification, steps vs scope, steps vs inputs) |
| truthy / falsy | whether a value counts as true in a boolean test; empty list, 0 and None are falsy |
| schema validation | checking form (parse, keys, types), not factual correctness |
| proxy | a stand-in observation that does not measure the claim |
| tools (field) | capabilities the agent may call, and which operations stay under approval |
| completion / halt / defer | the three stop exits: success condition met; stop because continuing crosses a boundary; pause and pass the decision to a named owner |
| turn limit vs finish action | effort bound vs the agent's signal of completion |
| incomplete status | honest report at a limit, partial artifacts preserved |
| refusal path | workflow preserves state and reports what blocks the next transition |
| progress | a change in the evidence or the decision state |
| prediction vs record | plan states expected observations beforehand; result records what happened |
| proposal vs approval | plan returned by a model vs an act by an accountable person |
| permission prompt | asks whether one tool action may run |
| plan mode (Claude Code) | read-only analysis that presents a plan for approval before edits |
| plan-and-execute vs adaptive loop | full plan first, then run; vs choosing each action after the previous observation |
| replanning | revising a plan with a recorded reason when evidence contradicts an assumption |
| error of the third kind | solving the wrong problem correctly (not Type I or Type II) |
| primary generator / anchor | early, often unstated idea of what a problem is about that shapes visible solutions |
| formulation / candidate formulations | the framing of the problem and the alternatives compared |
| salience criterion | asks whether solving the problem addresses what matters |
| tractable | easy to build or measure |
| precondition / postcondition / invariant | what holds before a call / after it / throughout |
| dependency / prerequisite / edge | a directed obligation between steps; the step that must come first; the arrow between them |
| topological order | ordering in which each step follows all its prerequisites |
| ready batch | steps whose declared prerequisites are done |
| hidden dependency | shared resource or real need not declared in the graph |
| duplicate id / unknown prerequisite / dependency cycle | three structural ordering errors |
| acyclic does not mean executable | a loop-free graph can still omit a real dependency |
| testable condition | one a stranger can apply by observation |
| failure route | planned next transition when an edge condition fails |
| counterexample | a plan that meets a field's wording but fails its purpose |
| sign-off | written record of what was checked, how, what was not checked, what is not claimed, and sign or withhold |

## Chapter 11: Tool use and verification

| Term | Meaning |
|---|---|
| tool definition | name, description and input schema advertised to the model; describes a tool, does not run it |
| input schema | JSON Schema description of a tool's arguments; guides generation, does not enforce |
| tool_use block | assistant-side structured request to run a named tool with arguments (a tool call) |
| tool_result block | user-side message block returning a tool's output, linked by tool_use_id |
| tool_use_id | identifier tying a result to its request; establishes correspondence, not correctness |
| stop_reason (end_turn, tool_use, max_tokens) | field saying why a response ended: natural completion, waiting on a tool, or truncation |
| dispatcher | application code mapping a requested tool name to an operation |
| strict validation vs coercion | reject mismatched input vs silently convert it |
| path traversal / canonical path | escaping an approved directory with .. or links / the resolved real location |
| error result (is_error) | tool_result flagged as a failure so the model can repair the call |
| workflow vs agent loop | fixed code-directed sequence vs model-directed repeated tool calls |
| turn limit (iteration cap) | bound on model requests; bounds cost, not progress |
| deterministic vs correct | repeatable output vs right output |
| stub (scripted response) | injected fake client; tests control logic, not model behaviour |
| repetition vs corroboration | rerunning the same path vs a check that fails differently |
| shared assumption | premise that agreeing checks both depend on |
| falsifiable claim / detection power | claim an observation could contradict / ability of a check to fail on a real fault |
| similarity vs support | embedding closeness is relevance, not entailment |
| overclaim / scope of claim | report stronger than the evidence (saved, deleted, deployed, current) |
| stale evidence / provenance | out-of-date result; dates and versions recorded with a check |
| approval gate vs permission rule | human checkpoint on one call vs standing policy on what may run |
| idempotency / idempotency key | repeat gives same effect / token marking a retry as the same request |
| indirect prompt injection / least privilege | instructions hidden in read content / narrow granted authority |
| contract and tests first | specification and tests written before the implementation is requested |
| negative case | evidence of a rejection, showing a check can say no |
| trace / redaction | record of calls for audit / masking sensitive fields |

## Chapter 12: Memory and multiple agents

| Term | Meaning |
|---|---|
| stateless | a model call keeps no information between calls beyond the text in its context window |
| semantic search | ranking stored items by closeness of meaning to a query |
| exact-key lookup | reading a record by matching its key string |
| working memory | what is in the context window during the current step |
| episodic memory | records of specific past events and interactions |
| semantic memory | general facts not tied to one event |
| procedural memory | skills and how-to instructions |
| recency / importance / relevance | scores for how recent, how generally significant, and how task-fitting a memory is |
| compaction | summarizing a conversation near the context limit and continuing from the summary |
| structured note-taking | writing notes to storage outside the context window for later retrieval |
| delegation to sub-agents | sub-agents work in their own context windows and return condensed results |
| version / expected version | a counter of committed writes, and the version a writer read |
| compare-and-set | a write applied only if the expected version equals the current version |
| stale write | a write whose expected version is older than the current version |
| optimistic concurrency control | proceed freely and check for conflict at commit |
| pessimistic locking | prevent conflict by making others wait for a lock |
| race condition | a fault whose outcome depends on how concurrent operations interleave |
| atomic operation | a check-and-update that other threads cannot interleave |
| thread-safe | correct under concurrent threads of one process, not across servers |
| lost update | a later write replacing an earlier one it never saw |
| granularity | how much state shares one key and one version counter |
| superseded / version chain | a newer reviewed version replaces an older one that stays in history |
| last-writer-wins / first-writer-wins | policies that keep the latest or earliest committed value |
| valid vs verified | valid passed the store's rules; verified was checked against evidence |
| lineage | chain of derivation from the original source |
| circular reporting | claims citing each other until they look like corroboration |
| freshness | how recent an observation is |
| event / observation / ingestion time, ingestion lag | when it happened, when it was seen, when it was stored, and the delay between the last two |
| valid-until | time by which evidence needs renewing |
| anchoring | being pulled toward the first view seen |
| input boundary | separation of untrusted data from trusted instructions |
| allowlist / least privilege | narrow, pre-set limits on what a tool or worker may do |
| quarantine | retain a record but exclude it from prompts |
| side effect / idempotency key | a change outside the agent's store, and a key that makes a repeated request apply once |
| role contract | handoff stating inputs, task, tools, output format and escalation |
| handoff | point where work and claims pass between agents |
| orchestrator vs worker | the agent that splits and combines work vs the agent that does a subtask |
| budget / escalation path | cap on resources, and a route to a named human |
| proposal queue | holding area for unreviewed candidate facts |
| premortem vs postmortem | imagine failure before launch vs review an incident after |
| sign-off statement | what was checked, how, what was not checked, what is not claimed |
| end-to-end evaluation / error propagation | measuring the chain's final output; wrong output feeding the next stage |

## Chapter 13: Evaluation and approval gates

| Term | Meaning |
|---|---|
| proposal | description of the action shown to the reviewer before it runs |
| decision record | stored verdict naming approver and what it applies to |
| evaluation vs authorization | measuring behaviour against criteria vs granting permission for an action |
| target / effects / rollback / evidence | the object acted on / what will change / how to undo / checkable support |
| irreversible, blast radius | effect cannot be undone; how far damage spreads |
| test case, grader, evaluation set, regression, flaky | input with expected outcome; scorer; collection of cases; formerly working behaviour that fails; inconsistent result on same input |
| circular evaluation | expectation written after seeing output |
| trace, outcome grading, hallucination | record of tool calls; grading the real result not the agent's summary; unsupported claim stated as fact |
| coverage, edge case, negative case, class imbalance | breadth of situations tested; boundary input; case where refusing is right; uneven outcome mix |
| precision, recall, false positive, false negative | share of flags that are right; share of real cases caught; safe case flagged; real case missed |
| proxy metric, Goodhart's law, guardrail metric | stand-in measure; target stops measuring; watched side-effect measure |
| LLM-as-judge, rubric, calibration, self-preference bias | model scoring outputs; written criteria; aligning judge with human labels; favouring own style |
| confidence interval | plausible range for the true rate |
| pass@k, pass^k, trial | at least one of k succeeds; all k succeed; one attempt |
| hash, digest, fingerprint, canonicalization | one-way fixed-length output; digest of exact content; agreed serialised form before hashing |
| digital signature | binds a digest to a key holder |
| content / scope / identity binding | tie to exact proposal / environment, deadline, uses / authenticated approver |
| time-of-check to time-of-use (TOCTOU) | gap between verifying and acting |
| single-use, race condition, atomic, replay, idempotent | one consumption; timing-dependent outcome; indivisible step; reuse of valid record; repeat gives same result |
| expiry, revocation | automatic end of validity; explicit early withdrawal |
| rubber-stamping, approval fatigue, automation bias | approval without examination; quality decline from volume; over-trusting system output |
| triage, batching, throttling, escalation | ranking by risk; grouping similar items; limiting proposal rate; routing to expertise |
| standing policy, allowlist, sandbox | pre-authorised class; permitted-only list; isolated environment |
| mutable vs immutable reference | can change after reading vs fixed |
| sign-off, ownership bias, independent review | signed accountability statement; overvaluing own work; reviewer other than builder |
| dry run, drift | preview without doing; difference between reviewed and live state |
| test oracle, mutation testing, diff review | source of correct answer; seeded defects to test the tests; reading changes |
| stub / mock | stand-in for a dependency in tests |

## Chapter 14: Governance and ethics

| Term | Meaning |
|---|---|
| owner | the person who answers for a workflow as it runs and has authority to pause or change it |
| approver | the person who gives the authorized yes to a specific proposal |
| incident contact | the person, or documented backup, who receives and acknowledges an alert about harm |
| AI-use register | the record of an AI workflow's purpose, roles, data, thresholds, retention and recourse |
| accountability | responsibility accepted by a named person who has authority to act |
| completeness vs compliance | filled-in fields versus a legal and institutional determination |
| validator status (incomplete / review-required / ready-for-human-review) | structural check results; the last means ready to be reviewed, not reviewed or approved |
| threshold / trigger / signal | an observable condition, how it is measured, and the response it sets off |
| stop rule | a trigger that can fire on a single confirmed severe event |
| aggregate rate vs severity | an average that weights each failure equally and hides rare severe harm |
| pause authority | the power to halt a workflow, only usable when incentives support it |
| escalation path / backup / acknowledgment window | who gets the alert next and the time within which it should be acknowledged |
| structural check vs adequacy judgment | what code can refuse exactly versus what people judge |
| isinstance vs exact type check; bool is a subclass of int | a subclass instance passes isinstance but not type(x) is int |
| test-first / specification | tests written from intent before the implementation exists |
| claim no stronger than the evidence | wording that matches what a check actually established |
| purpose / scope change | the stated boundary of use; a new data type or audience needs re-review |
| retention lifecycle | the life of data across logs, backups, exports, derived artifacts and provider copies |
| zero retention | a design intent that must say what it means and does not prove no copies exist |
| derived data | embeddings, summaries and hashes made from source data |
| minimal audit record / trace | identifiers and references to evidence, not full content |
| action surface | the systems and audiences an agent's actions can reach |
| fabrication (hallucination) vs abstention | a statement unsupported by sources versus leaving the answer out |
| base rate / positive predictive value | share of positives in a group; share of positive predictions that are correct |
| fairness criterion | a chosen definition of fair that numbers alone do not select |
| generic risk vs concrete harm | a vague concern versus who is harmed, what happens and how |
| matched mitigation | a control that reduces the named harm's likelihood or severity |
| consultation vs simulated stakeholder | asking affected people versus model role-play that is not evidence |
| stakeholder | a person or group affected by or able to influence the workflow |
| recourse / contest / remedy | a path to a human, a challenge to a decision and an outcome |
| meaningful human review vs rubber stamp | review with time, authority and a record versus a click |
| approval gate vs permission | a human pause at the moment of action versus a rule about what is allowed |
| prompt injection / untrusted input | instructions hidden in content the agent reads |
| control plane vs documentation | a register that changes system behavior versus one that only describes |
| decision note | a record separating model proposal from human input, with evidence and affected interests |
| retention clock start event | the event (creation, last use) from which a retention period is counted |

## Chapter 15: Supervised capstone

| Term | Meaning |
|---|---|
| structural check | a check of presence, location and length of files, not their content |
| substantive check | a judgment of what a file says and whether it does its job |
| resolved path | the real location of a path after following symbolic links |
| symbolic link (symlink) | a file that points to another path, possibly outside the folder |
| false accept / false reject | a check passing what it should reject / blocking what it should allow |
| proxy measure | a measurable stand-in correlated with the property you care about |
| Goodhart's law | a measure that becomes a target stops measuring what it stood for |
| format (schema) check | test of the shape of output, such as keys and types |
| unsupported citation | a citation present but not supported by the cited passage |
| acceptance criteria / acceptance tests | conditions fixed in advance that define done and judge the output |
| success criterion, falsifiable | a pass or fail condition that a result could contradict |
| non-goal | something the project declines to do, bounding scope |
| specification defect | an ambiguity or gap in the stated requirement |
| baseline | a hand-built reference version to compare against |
| adversarial test case | input chosen to break the function at its boundaries |
| stub | a scripted stand-in for the model call, giving repeatable tests |
| planted defect | a deliberate flaw inserted to test whether a check detects it |
| pre-registered prediction | a prediction written before the run so the result can contradict it |
| pre-mortem | imagining the project has failed to list failure modes before building |
| evaluation harness, task, trial, grader | tasks with success criteria, repeated runs, and a scorer |
| transcript vs outcome | record of the steps vs the final state of the environment |
| read-back | observing the real state after an action instead of trusting the tool's report |
| independent verification | a check using a different method or source than the producer |
| false positive / false negative (reviewer) | reported problem that is not real / real problem not reported |
| cherry-picking | selecting favourable runs or cases and hiding the rest |
| trust boundary | line between trusted instructions and untrusted input |
| capability vs permission | what the agent can do vs what it is allowed to do |
| stale approval | an approval that no longer matches the changed proposal |
| stop condition, token budget, iteration cap | rules that end an agent loop and bound cost |
| advisory output | model comments that inform but do not decide |
| claim-to-evidence graph | table linking each claim to the evidence that supports it |
| unsupported claim | a claim with no linked evidence |
| circular evidence | a document justified by what it says about itself |
| limitation statement | a sentence saying what was not tested or established |
| ship / narrow / defer / stop | deploy fully / deploy reduced scope / postpone with named evidence / end |
| handoff test | observing whether someone else can run the work from written instructions alone |
| attribution and licence | crediting and following terms for adapted code |

## Jargon sets j01 to j04: sampling, prompts, agents, retrieval

| Term | Meaning |
|---|---|
| token ID | a numeric label for a token with no meaning of its own |
| determinism | the same input and settings give the same output |
| stop sequence | a string that ends generation when it appears |
| max tokens | a cap on the number of tokens generated |
| next-token prediction | giving a probability for the next token from the tokens so far |
| autoregressive generation | sampling a token, appending it and repeating |
| user turn | one message from the person in the conversation |
| role | the label of a message's source: system, user or assistant |
| persona | a character or voice a prompt asks the model to adopt |
| zero-shot | a prompt that gives an instruction with no worked examples |
| few-shot | a prompt that includes a small number of example input-output pairs |
| instruction | text that says what to do |
| example | a sample input and output that shows what a good result looks like |
| delimiter | a marker such as quotes or tags that separates parts of a prompt |
| output format / schema | the stated fields, names and types the answer should have |
| acceptance criterion | a testable condition an output has to meet to be accepted |
| constraint | a limit placed on the output or the work |
| chain of thought | intermediate reasoning written out before the answer |
| final answer | the part of the output meant for the user or program |
| jailbreak | a user prompt that tries to get the model past its own safety rules |
| assistant | a chat model given a role and instructions to help; it may or may not use tools |
| tool schema | the shape of a tool's arguments: field names and types |
| sandbox | a restricted environment that limits what an action can reach |
| stop condition | a rule that ends the loop |
| step budget | the maximum number of loop steps allowed |
| subagent | an agent given a narrower task by another agent, often with its own context |
| orchestrator | an agent that assigns work to others and combines the results |
| RAG | retrieval-augmented generation: retrieve passages, add them to the prompt, then generate |
| chunk | a piece of a document cut to a size that can be indexed and retrieved |
| vector search | finding chunks whose vectors are nearest to the query's vector |
| citation | a pointer to the source passage behind a claim |
| inference | using a trained model to produce output with weights unchanged |
| instruction-tuned model | a base model trained further on instructions and good responses |
| hyperparameters | settings chosen by people that control a training run |
| configuration | settings and files that shape how a model is run, outside the weights |

## Jargon sets j05 to j07: MCP, evaluation and governance, saying it to Claude Code

| Term | Meaning |
|---|---|
| HTTP transport | transport for a remote server reached over a network |
| JSON-RPC request | message with an id that expects a response with the same id |
| JSON-RPC response | reply carrying the request's id and either a result or an error |
| initialized | notification from the client saying it is ready for ordinary requests |
| capabilities | what each side declares it supports during the handshake |
| JSON-RPC error | the protocol-level request failed |
| interoperability | whether host and server can exchange messages both understand |
| authorization | whether this server and tool belong in the task; decided by a person |
| discovery (tools/list) | client asks the server what it offers at run time |
| function calling | how a model asks for a tool; something else still runs it |
| test | fixed expectation that passes or fails the same way each run |
| benchmark | shared fixed task set with a scoring method for comparing systems |
| rubric | criteria with descriptions of each score level |
| LLM-as-judge | a language model scoring another output against criteria; needs checking against human labels |
| regression | a change that breaks something that worked; a regression eval reruns earlier cases |
| error (engineering) | a failure the system reports, such as an exception |
| groundedness | claims supported by supplied source material, which is not the same as true |
| human in the loop | a person able to stop or approve before the action, not only reading afterward |
| responsibility | duty to do the work; can be handed to an agent |
| bias | systematic skew in outputs favouring or disadvantaging groups |
| privacy | protecting personal information about people |
| red team | group that deliberately attacks a system to find failures before users do |
| commit | recording staged changes with a message in git history (distinct from push) |
| push | sending commits to a remote |
| file | a named unit of content |
| directory (folder) | a container holding files and other directories |
| test vs eval | fixed pass/fail expectation versus scoring of varying output |
| memory file (CLAUDE.md) | file of standing instructions read at the start of a session |
| slash command | command the user invokes by typing a name starting with a slash |
| checkpoint | in Claude Code, recorded file state before an edit so it can be rewound; in training, a snapshot of weights and optimizer state |
| verification | checking against evidence confirmable apart from the producer |
| acceptance criteria | conditions for accepting a result, stated before the work |
| plan mode / planning before acting | researching without editing and presenting a plan for approval before a change |

## Jargon sets k01 to k03: compress and decompress, reading agent output, false friends

New terms and contrasts only; terms already listed above (idempotent, deterministic, approval gate, acceptance criteria, eval vs test, diff review and others) are tested again in these sets, here as a term and its checkable conditions.

| Term | Meaning |
|---|---|
| unpacking a term | turning one word into the conditions you can check, such as idempotent = same end state after a repeat |
| compressing a requirement | writing the one-line instruction that carries all of a requirement's conditions |
| tool_use / tool_result | the model's structured request to run a tool; the matching output returned to it, linked by an id |
| permission scope | the set of actions, paths or commands a tool or agent is allowed to use |
| scope violation | a change outside the files or actions the instruction allowed, harmless or not |
| claim vs evidence | a statement of what happened vs output you can check apart from the claimant |
| claim/code mismatch | a summary that says something the diff or code does not do |
| check-then-act race | a condition checked, then acted on after another process may have changed it |
| read-modify-write race | two writers read the same value and the later write overwrites the earlier |
| partial result | a run that finished some of its work and reported as if it finished all |
| trivial test | a test that would pass whether or not the claimed behaviour exists |
| failing test first | a test shown to fail before the change, so a later pass means something |
| silent failure | an error swallowed with no signal, so the run looks successful |
| stable (sort) vs stable (API) | equal items keep their relative order; an interface that does not change between versions |
| atomic | all-or-nothing as seen by others: a file replace, a commit, or one indivisible step |
| serializable (data) vs serializable (isolation) | convertible to a stored or sent format such as JSON; transactions behave as if run one at a time |
| cache (lru_cache) vs prompt caching | stored return values for repeated calls in Python; reuse of a processed prompt prefix by the API |
| memory (agent) vs context | information kept across sessions; tokens in the current window |
| agent vs workflow | model chooses the next step at run time vs code fixes the steps in advance |
| tool vs skill | a callable function that takes an action vs packaged instructions loaded when relevant |
| prompt vs system prompt | the request in a turn vs standing instructions that frame the whole session; untrusted text does not belong in the system prompt |
| hallucination vs error | an unsupported claim stated as fact vs a failure such as an exception or wrong status code |
| evaluation vs test | scored judgment over many varying outputs vs a fixed pass/fail expectation |
| MCP server vs client | the process that exposes tools, resources and prompts vs the host side that connects to servers and calls them |
| model vs agent | the weights that produce tokens vs the system of model, tools and loop that acts |
