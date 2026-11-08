# INFO 7375 Prompt Engineering for Generative AI: practice exam 01: KEY

Total 100 points. Statement key: T = true (check it), F = false (leave it blank).

---

**1.** A chat API call has a system prompt and a user turn. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. The system prompt and the user turn are stored in the model's weights.
- [ ] B. A rule written in the system prompt is enforced as strictly as a check in the code around the model.
- [ ] C. The user turn is the model's reply to the system prompt.
- [ ] D. A user turn and a system prompt are the same thing, written in two places.
- [ ] E. A system prompt sets standing instructions or a role for the whole conversation.

**Key:** A=F B=F C=F D=F E=T  |  `MA-found.22`  |  *7. Programming languages vs language models*  |  source: system prompt vs user turn

- A (false): Both are input text for the current conversation.
- B (false): A prompt rule is an instruction the model may not follow; code enforcement does not depend on the model.
- C (false): The user turn is a message from the user; the reply is the assistant turn.
- D (false): They are different roles with different purposes.
- E (true): The system prompt frames the conversation; the user turn is one message.

**2.** A model must answer from supplied sources and return JSON with an answer and a list of cited source identifiers. A validator checks that the output parses as JSON, has the required fields with the right types, and cites identifiers that exist in the supplied list. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Parsing as JSON is syntactic validity, and having the right fields and types is schema validity.
- [ ] B. Passing shows that the cited source supports the answer.
- [ ] C. A response with malformed JSON could still pass, because the validator examines content rather than syntax.
- [ ] D. Measuring accuracy would need a content-level check, such as comparison with reference answers or human review.
- [ ] E. Passing the validator shows the claim in the answer is true.

**Key:** A=T B=F C=F D=T E=F  |  `MA-found.29`  |  *10. Format validity versus factual validity*  |  source: JSON vs schema vs factual validity

- A (true): These are two format checks of different strictness.
- B (false): It shows only that the cited identifier exists.
- C (false): The validator begins by parsing, so malformed JSON fails.
- D (true): Factual validity is checked against content.
- E (false): The validator checks shape, not facts.

**3.** An agent runs the test suite, the output reports two failures, and the agent then edits a file. Which statements name the parts correctly? Check each statement that is true.  *(5 points)*

- [ ] A. The test output is the observation.
- [ ] B. The decision to edit the file is the model's next proposed action.
- [ ] C. The program that runs the tests and passes the output back is the controller.
- [ ] D. The edit is the observation.
- [ ] E. The test run is the stop condition.

**Key:** A=T B=T C=T D=F E=F  |  `MA-j03.8`  |  *Jargon test: agents and tools*  |  source: observation, controller

- A (true): An observation is the result fed back to the model.
- B (true): The model proposes; the controller runs.
- C (true): The controller executes actions and feeds back results.
- D (false): The edit is an action; its result would be the next observation.
- E (false): A stop condition ends the loop; a test run does not by itself.

**4.** A user types to Claude Code: "Look at what you changed and tell me if it's okay." Decide which statements correctly name the vague words or improve the prompt. Check each statement that is true.  *(5 points)*

- [ ] A. "What you changed" is called the diff: the lines added and removed compared with before.
- [ ] B. A diff is a saved snapshot of the whole project at one moment.
- [ ] C. "Review" in this prompt means running a model eval over a set of cases.
- [ ] D. Reading the diff and judging it against requirements is a diff review.
- [ ] E. A more exact prompt is: "Show me the diff and review it against the acceptance criteria below."

**Key:** A=T B=F C=F D=T E=T  |  `MA-j07.1`  |  *Jargon test: saying it exactly to Claude Code*  |  source: diff, diff review

- A (true): A diff shows the difference between two versions.
- B (false): A snapshot is a commit or checkpoint; a diff is the difference.
- C (false): A diff review is a reading of one change.
- D (true): Review means checking the change, not rerunning the whole task.
- E (true): It names the artifact and the standard.

**5.** A team uses a second model to score the first model's answers against a rubric. Decide which statements about LLM-as-judge are true. Check each statement that is true.  *(5 points)*

- [ ] A. Judge models can prefer longer or more fluent answers regardless of whether they are correct.
- [ ] B. A judge model's score is a measurement that needs no check against human labels.
- [ ] C. Using the same model to judge its own output gives errors that are independent of the original.
- [ ] D. An LLM judge is a language model that scores another output against stated criteria.
- [ ] E. Comparing a sample of the judge's scores with human labels shows how far the judge can be trusted.

**Key:** A=T B=F C=F D=T E=T  |  `MA-j06.4`  |  *Jargon test: evaluation, approval gates and governance*  |  source: LLM-as-judge

- A (true): This is a known bias of automated scoring.
- B (false): Agreement with people has to be checked.
- C (false): Errors of the same kind of model are correlated.
- D (true): It automates scoring at scale.
- E (true): That comparison is the usual calibration step.

**6.** A team uses Claude Code and wants to add capabilities. They are comparing a tool with a skill. Which statements are true? Check each statement that is true.  *(5 points)*

- [ ] A. A skill is an API function that returns data from an external service.
- [ ] B. A tool_use block is how Claude requests a call to a tool.
- [ ] C. A skill is a packaged set of instructions, with optional scripts, that Claude loads when relevant.
- [ ] D. A tool is a callable function with a schema that Claude can invoke to take an action.
- [ ] E. Installing a skill gives Claude a permission it did not have.

**Key:** A=F B=T C=T D=T E=F  |  `MA-k03.15`  |  *Jargon test: false friends*  |  source: tool vs skill

- A (false): That describes a tool.
- B (true): Request side of the exchange.
- C (true): Skills guide.
- D (true): Tools act.
- E (false): Permissions are set separately.

**7.** Which statements tell retrieval and fine-tuning apart? Check each statement that is true.  *(5 points)*

- [ ] A. Retrieval changes what the model sees in a request by adding passages to the prompt.
- [ ] B. Fine-tuning changes the model by continuing training, which updates weights.
- [ ] C. Retrieval updates the model's weights.
- [ ] D. Fine-tuning is the better way to add a large amount of changing facts.
- [ ] E. Retrieval and fine-tuning are two names for training on documents.

**Key:** A=T B=T C=F D=F E=F  |  `MA-j04.1`  |  *Jargon test: retrieval, fine-tuning and configuration*  |  source: retrieval vs fine-tuning

- A (true): Retrieval works on the context.
- B (true): Fine-tuning works on the weights.
- C (false): Retrieval leaves weights unchanged.
- D (false): Changing facts suit retrieval, which can update at once.
- E (false): Retrieval is not training.

**8.** Check each statement that is true about the embedding matrix, the logits and the vocabulary. Check each statement that is true.  *(5 points)*

- [ ] A. The logits vector for next-token prediction has one entry for each token in the vocabulary.
- [ ] B. The embedding dimension is the length of each embedding vector.
- [ ] C. The logits vector has a length equal to the number of tokens in the prompt.
- [ ] D. The embedding matrix has one row for each token in the vocabulary, and the token ID selects the row.
- [ ] E. The vocabulary is the tokenizer's list of tokens, including word pieces.

**Key:** A=T B=T C=F D=T E=T  |  `MA-found.11`  |  *4. Tokens and input embeddings*  |  source: embedding matrix; logits; vocabulary

- A (true): The model scores every possible next token.
- B (true): Dimension is how many numbers describe one token.
- C (false): Its length is the vocabulary size, regardless of prompt length.
- D (true): An embedding lookup uses the token ID as an index.
- E (true): The vocabulary is a list of tokens, not of dictionary words.

**9.** An analyst wants a language model to help with this morning's news. Check each statement that is true about the model's knowledge cutoff and the options for supplying newer information. Check each statement that is true.  *(5 points)*

- [ ] A. Pasting an article into the conversation retrains the model on that article.
- [ ] B. Placing the article in the context window lets the model use it without changing its weights.
- [ ] C. Fine-tuning changes the weights, so it changes the model's behaviour rather than handing it one day's news.
- [ ] D. Retrieval changes the model's weights so that it remembers the retrieved page.
- [ ] E. The knowledge cutoff is the point after which the training data holds no later events.

**Key:** A=F B=T C=T D=F E=T  |  `MA-found.5`  |  *2. What is a model? What is a language model?*  |  source: knowledge cutoff; retrieval vs fine-tuning; context

- A (false): Text in the prompt is context for that conversation, and the weights stay the same.
- B (true): Supplying text as context is how newer information reaches a model without retraining.
- C (true): Fine-tuning edits the model, whereas retrieval and prompting supply content.
- D (false): Retrieval changes what the model sees, not its weights.
- E (true): A knowledge cutoff marks the end of the model's training data.

**10.** A prompt reads: "Summarize the ticket in at most 80 words, in plain English, for a customer." Which single statement labels its parts correctly? Check each statement that is true.  *(5 points)*

- [ ] A. "At most 80 words" is a constraint on the output that a script could check.
- [ ] B. "For a customer" is the output schema.
- [ ] C. "Summarize the ticket" is the persona.
- [ ] D. "Plain English" is a delimiter.
- [ ] E. The whole sentence is a system prompt because it contains an instruction.

**Key:** A=T B=F C=F D=F E=F  |  `MA-j02.6`  |  *Jargon test: prompt structure and contracts*  |  source: constraint vs other parts

- A (true): A length limit is a checkable constraint.
- B (false): It names an audience, not fields and types.
- C (false): It is the task instruction.
- D (false): It is a style constraint, not a separator.
- E (false): A system prompt is defined by where it sits, not by containing an instruction.

**11.** A server offers three kinds of thing to a host. Decide which statements about tools, resources and prompts are true. Check each statement that is true.  *(5 points)*

- [ ] A. Prompts are controlled by the model, which decides when to apply them.
- [ ] B. A tool is described to the model by a name, a description and an input schema.
- [ ] C. A tool is a function the model decides to call, so tools are model-controlled.
- [ ] D. A resource is data such as a file or a schema that the application chooses to attach as context.
- [ ] E. A prompt is a reusable template that the user picks.

**Key:** A=F B=T C=T D=T E=T  |  `MA-j05.6`  |  *Jargon test: MCP*  |  source: tools vs resources vs prompts

- A (false): Prompts are user-controlled templates, such as ones chosen from a slash menu.
- B (true): Those three parts are what the model reads when choosing a tool.
- C (true): The model picks tools during its work.
- D (true): Resources are application-controlled.
- E (true): Prompts are user-controlled.

**12.** A developer tells Claude: "Retrain the model on this PDF so it knows our refund policy, and make the answers more creative by raising the learning rate." The developer actually wants the PDF used when answering, and more varied wording. Check each statement that is true.  *(5 points)*

- [ ] A. Raising the learning rate at request time changes the answer style.
- [ ] B. Learning rate controls randomness during decoding.
- [ ] C. A better rewrite is: "Use the attached PDF as context when answering, and raise the temperature slightly."
- [ ] D. "Retrain" is the wrong word for supplying a PDF at request time; "retrieve from" or "supply as context" is exact.
- [ ] E. "Learning rate" is the wrong term for output variety; the sampling setting is temperature.

**Key:** A=F B=F C=T D=T E=T  |  `MA-ch09.13`  |  *None*  |  source: imprecise prompt wording

- A (false): There is no learning step at request time.
- B (false): It sets update step size in training.
- C (true): It names context and a sampling setting.
- D (true): Retraining updates weights; supplying a document is context.
- E (true): Learning rate is a training hyperparameter.

**13.** An agent reports: "Added tests for the parser: 12 tests, all green." All 12 call the parser with the same valid string. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. Twelve tests improve branch coverage over one test.
- [ ] B. Green tests prove the parser has no bugs.
- [ ] C. A follow-up is: "Give a table of input classes (empty, malformed, unicode) with the test for each."
- [ ] D. The count of tests does not measure what they cover.
- [ ] E. Another check is to break the parser on purpose and show that a test fails.

**Key:** A=F B=F C=T D=T E=T  |  `MA-k02.20`  |  *Jargon test: reading agent output*  |  source: tests, coverage of input classes

- A (false): They repeat one path.
- B (false): They show only that these checks passed.
- C (true): It maps classes to checks.
- D (true): All twelve exercise one path.
- E (true): A test that cannot fail is not evidence.

**14.** Check each statement that is true about the feedforward network (multi-layer perceptron). Check each statement that is true.  *(5 points)*

- [ ] A. Its behaviour comes from weights learned from examples.
- [ ] B. A feedforward network that fits its training examples well is certain to predict new inputs well.
- [ ] C. It maps an input vector of numbers to an output by passing values forward through layers.
- [ ] D. Attention, not the feedforward network, is what lets tokens exchange information with each other.
- [ ] E. The nonlinear step between its layers lets it represent relationships that a single weighted sum fails to capture.

**Key:** A=T B=F C=T D=T E=T  |  `MA-found.8`  |  *3. Feedforward networks, encoders, decoders, context and prediction*  |  source: feedforward network (MLP)

- A (true): A feedforward network is trained, and the weights store what it learned.
- B (false): A good fit to training examples does not ensure generalization.
- C (true): Feedforward means values move in one direction, layer to layer.
- D (true): Exchanging information across tokens is the job of attention.
- E (true): Nonlinearity is what gives layered networks more power than a linear rule.

**15.** A team adopts the principle: the model generates, and ordinary code checks. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. A schema validator that rejects a response with a missing required field is a function acting as a checker.
- [ ] B. A function's failure surfaces as an explicit, inspectable error rather than as fluent wrong text.
- [ ] C. The principle says to remove the model and write the whole system by hand.
- [ ] D. A pure-function checker can return different results on repeated calls with the same input.
- [ ] E. Passing a deterministic check proves the output is correct.

**Key:** A=T B=T C=F D=F E=F  |  `MA-found.24`  |  *8. The strength of functions*  |  source: generate, then check with functions

- A (true): A checker is code that tests an output against an explicit rule.
- B (true): Explicit failure makes checks reliable.
- C (false): The model still generates; the code only checks.
- D (false): Determinism is what a pure function offers.
- E (false): A check proves only the property it tests.

**16.** Two kinds of AI system are compared: a rule-based system, and a system that learns from data (machine learning). Check each statement that is true.  *(5 points)*

- [ ] A. Overfitting means a model does well on its training examples but poorly on new inputs.
- [ ] B. In a rule-based system, a person writes the conditions that decide each output.
- [ ] C. Training data is the set of hand-written conditions that a rule-based system runs on.
- [ ] D. A learned model can give a sensible output for an input that no one wrote a rule for, which is called generalization.
- [ ] E. A rule-based system gives a sensible output for an input that its rules did not anticipate.

**Key:** A=T B=T C=F D=T E=F  |  `MA-found.1`  |  *1. A brief history of AI*  |  source: rule-based vs learned; generalization; overfitting

- A (true): Overfitting is fitting the training examples too closely to carry over to new data.
- B (true): A rule-based system is one whose behaviour comes from hand-written conditions.
- C (false): Training data is the set of examples a learned model is fitted to, not a rule list.
- D (true): Generalization is a learned model's ability to handle inputs beyond its training examples.
- E (false): Rules cover only the cases someone wrote down, so unanticipated inputs fall through.

**17.** Check each statement that is true about solve-verify asymmetry. Check each statement that is true.  *(5 points)*

- [ ] A. Asking the same model to confirm its own answer is an independent verification.
- [ ] B. The asymmetry holds equally for each task.
- [ ] C. When verifying is as hard as solving, the advantage shrinks.
- [ ] D. Checking a completed Sudoku is easier than solving one.
- [ ] E. The asymmetry suggests generating with a model and verifying with a cheap independent check.

**Key:** A=F B=F C=T D=T E=T  |  `MA-found.37`  |  *12. Solve-verify asymmetry, fluency, and falsifiability*  |  source: solve-verify asymmetry

- A (false): A model re-reading its own answer shares its blind spots.
- B (false): For some tasks verifying is as hard as solving.
- C (true): The benefit comes from a cheaper check.
- D (true): Verifying a solution can be easier than finding one.
- E (true): Generate-then-check uses the cheaper direction.

**18.** A Claude Code session runs shell commands. Which setup is an approval gate for `git push`? Check each statement that is true.  *(5 points)*

- [ ] A. A hook that exits non-zero on `git push` until an approval flag exists.
- [ ] B. A permission rule set to ask, so each `git push` pauses for a person to confirm before it runs.
- [ ] C. A line in CLAUDE.md saying "please do not push without asking".
- [ ] D. A pre-run plan that lists a push as step 5, with no stop at that step.
- [ ] E. A system message reporting each push after it finished.

**Key:** A=T B=T C=F D=F E=F  |  `MA-k01.12`  |  *Jargon test: compress and decompress*  |  source: approval gate

- A (true): Code enforces the pause.
- B (true): The tool call waits for a human.
- C (false): This is advice; nothing blocks the command.
- D (false): Listing a step does not gate it.
- E (false): Notification after the fact does not gate.

**19.** Which statements about greedy decoding and determinism are true? Check each statement that is true.  *(5 points)*

- [ ] A. Greedy decoding picks the highest-probability token at each step.
- [ ] B. Greedy decoding samples from the distribution, so repeated runs vary.
- [ ] C. A deterministic run gives the same output for the same input and settings.
- [ ] D. Setting the temperature very low makes sampling behave close to greedy decoding.
- [ ] E. Greedy decoding guarantees the answer is correct.

**Key:** A=T B=F C=T D=T E=F  |  `MA-j01.6`  |  *Jargon test: sampling and tokens*  |  source: greedy decoding, determinism

- A (true): Greedy decoding takes the top token without sampling.
- B (false): Sampling is what makes runs vary; greedy decoding does not sample.
- C (true): Determinism means repeatable output.
- D (true): A sharp distribution makes the top token win nearly each time.
- E (false): Picking the most probable token is not a check on truth.

**20.** An assistant model calls a tool during a conversation. Check each statement that is true about tool_use and tool_result. Check each statement that is true.  *(5 points)*

- [ ] A. A tool_result block carries the tool's output back to the model.
- [ ] B. The tool_use block runs the tool inside the model.
- [ ] C. A tool_use block is the model's request to call a named tool with arguments.
- [ ] D. The program around the model, not the model, executes the requested tool.
- [ ] E. The model produces the tool_result itself, inside its own reply.

**Key:** A=T B=F C=T D=T E=F  |  `MA-found.35`  |  *11. The agentic loop*  |  source: tool_use vs tool_result

- A (true): tool_result is the response returned into the conversation.
- B (false): It is only a request; running it is done elsewhere.
- C (true): tool_use is the request the model emits.
- D (true): The controller or client runs the tool and returns the result.
- E (false): The result comes from running the tool.
