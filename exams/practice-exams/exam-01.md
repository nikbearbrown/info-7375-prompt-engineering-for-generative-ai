# INFO 7375 Prompt Engineering for Generative AI: practice exam 01

**PRACTICE FORM. Drawn at random from the question bank; not the real exam; not signed off by the instructor.**

20 questions, 5 points each, 100 points. Name: ______________________

**Scoring.** Five statements, each true or false, 1 point each. The student checks the statements they believe are true. A statement scores 1 point if it is checked and true, or unchecked and false; otherwise 0. Read every statement on its own and decide whether it is true by itself. Strong words (always, never, every, proves) are often what makes a statement false, but a strong-sounding statement is not false for sounding strong.

---

**1.** A chat API call has a system prompt and a user turn. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. The system prompt and the user turn are stored in the model's weights.
- [ ] B. A rule written in the system prompt is enforced as strictly as a check in the code around the model.
- [ ] C. The user turn is the model's reply to the system prompt.
- [ ] D. A user turn and a system prompt are the same thing, written in two places.
- [ ] E. A system prompt sets standing instructions or a role for the whole conversation.

**2.** A model must answer from supplied sources and return JSON with an answer and a list of cited source identifiers. A validator checks that the output parses as JSON, has the required fields with the right types, and cites identifiers that exist in the supplied list. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Parsing as JSON is syntactic validity, and having the right fields and types is schema validity.
- [ ] B. Passing shows that the cited source supports the answer.
- [ ] C. A response with malformed JSON could still pass, because the validator examines content rather than syntax.
- [ ] D. Measuring accuracy would need a content-level check, such as comparison with reference answers or human review.
- [ ] E. Passing the validator shows the claim in the answer is true.

**3.** An agent runs the test suite, the output reports two failures, and the agent then edits a file. Which statements name the parts correctly? Check each statement that is true.  *(5 points)*

- [ ] A. The test output is the observation.
- [ ] B. The decision to edit the file is the model's next proposed action.
- [ ] C. The program that runs the tests and passes the output back is the controller.
- [ ] D. The edit is the observation.
- [ ] E. The test run is the stop condition.

**4.** A user types to Claude Code: "Look at what you changed and tell me if it's okay." Decide which statements correctly name the vague words or improve the prompt. Check each statement that is true.  *(5 points)*

- [ ] A. "What you changed" is called the diff: the lines added and removed compared with before.
- [ ] B. A diff is a saved snapshot of the whole project at one moment.
- [ ] C. "Review" in this prompt means running a model eval over a set of cases.
- [ ] D. Reading the diff and judging it against requirements is a diff review.
- [ ] E. A more exact prompt is: "Show me the diff and review it against the acceptance criteria below."

**5.** A team uses a second model to score the first model's answers against a rubric. Decide which statements about LLM-as-judge are true. Check each statement that is true.  *(5 points)*

- [ ] A. Judge models can prefer longer or more fluent answers regardless of whether they are correct.
- [ ] B. A judge model's score is a measurement that needs no check against human labels.
- [ ] C. Using the same model to judge its own output gives errors that are independent of the original.
- [ ] D. An LLM judge is a language model that scores another output against stated criteria.
- [ ] E. Comparing a sample of the judge's scores with human labels shows how far the judge can be trusted.

**6.** A team uses Claude Code and wants to add capabilities. They are comparing a tool with a skill. Which statements are true? Check each statement that is true.  *(5 points)*

- [ ] A. A skill is an API function that returns data from an external service.
- [ ] B. A tool_use block is how Claude requests a call to a tool.
- [ ] C. A skill is a packaged set of instructions, with optional scripts, that Claude loads when relevant.
- [ ] D. A tool is a callable function with a schema that Claude can invoke to take an action.
- [ ] E. Installing a skill gives Claude a permission it did not have.

**7.** Which statements tell retrieval and fine-tuning apart? Check each statement that is true.  *(5 points)*

- [ ] A. Retrieval changes what the model sees in a request by adding passages to the prompt.
- [ ] B. Fine-tuning changes the model by continuing training, which updates weights.
- [ ] C. Retrieval updates the model's weights.
- [ ] D. Fine-tuning is the better way to add a large amount of changing facts.
- [ ] E. Retrieval and fine-tuning are two names for training on documents.

**8.** Check each statement that is true about the embedding matrix, the logits and the vocabulary. Check each statement that is true.  *(5 points)*

- [ ] A. The logits vector for next-token prediction has one entry for each token in the vocabulary.
- [ ] B. The embedding dimension is the length of each embedding vector.
- [ ] C. The logits vector has a length equal to the number of tokens in the prompt.
- [ ] D. The embedding matrix has one row for each token in the vocabulary, and the token ID selects the row.
- [ ] E. The vocabulary is the tokenizer's list of tokens, including word pieces.

**9.** An analyst wants a language model to help with this morning's news. Check each statement that is true about the model's knowledge cutoff and the options for supplying newer information. Check each statement that is true.  *(5 points)*

- [ ] A. Pasting an article into the conversation retrains the model on that article.
- [ ] B. Placing the article in the context window lets the model use it without changing its weights.
- [ ] C. Fine-tuning changes the weights, so it changes the model's behaviour rather than handing it one day's news.
- [ ] D. Retrieval changes the model's weights so that it remembers the retrieved page.
- [ ] E. The knowledge cutoff is the point after which the training data holds no later events.

**10.** A prompt reads: "Summarize the ticket in at most 80 words, in plain English, for a customer." Which single statement labels its parts correctly? Check each statement that is true.  *(5 points)*

- [ ] A. "At most 80 words" is a constraint on the output that a script could check.
- [ ] B. "For a customer" is the output schema.
- [ ] C. "Summarize the ticket" is the persona.
- [ ] D. "Plain English" is a delimiter.
- [ ] E. The whole sentence is a system prompt because it contains an instruction.

**11.** A server offers three kinds of thing to a host. Decide which statements about tools, resources and prompts are true. Check each statement that is true.  *(5 points)*

- [ ] A. Prompts are controlled by the model, which decides when to apply them.
- [ ] B. A tool is described to the model by a name, a description and an input schema.
- [ ] C. A tool is a function the model decides to call, so tools are model-controlled.
- [ ] D. A resource is data such as a file or a schema that the application chooses to attach as context.
- [ ] E. A prompt is a reusable template that the user picks.

**12.** A developer tells Claude: "Retrain the model on this PDF so it knows our refund policy, and make the answers more creative by raising the learning rate." The developer actually wants the PDF used when answering, and more varied wording. Check each statement that is true.  *(5 points)*

- [ ] A. Raising the learning rate at request time changes the answer style.
- [ ] B. Learning rate controls randomness during decoding.
- [ ] C. A better rewrite is: "Use the attached PDF as context when answering, and raise the temperature slightly."
- [ ] D. "Retrain" is the wrong word for supplying a PDF at request time; "retrieve from" or "supply as context" is exact.
- [ ] E. "Learning rate" is the wrong term for output variety; the sampling setting is temperature.

**13.** An agent reports: "Added tests for the parser: 12 tests, all green." All 12 call the parser with the same valid string. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. Twelve tests improve branch coverage over one test.
- [ ] B. Green tests prove the parser has no bugs.
- [ ] C. A follow-up is: "Give a table of input classes (empty, malformed, unicode) with the test for each."
- [ ] D. The count of tests does not measure what they cover.
- [ ] E. Another check is to break the parser on purpose and show that a test fails.

**14.** Check each statement that is true about the feedforward network (multi-layer perceptron). Check each statement that is true.  *(5 points)*

- [ ] A. Its behaviour comes from weights learned from examples.
- [ ] B. A feedforward network that fits its training examples well is certain to predict new inputs well.
- [ ] C. It maps an input vector of numbers to an output by passing values forward through layers.
- [ ] D. Attention, not the feedforward network, is what lets tokens exchange information with each other.
- [ ] E. The nonlinear step between its layers lets it represent relationships that a single weighted sum fails to capture.

**15.** A team adopts the principle: the model generates, and ordinary code checks. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. A schema validator that rejects a response with a missing required field is a function acting as a checker.
- [ ] B. A function's failure surfaces as an explicit, inspectable error rather than as fluent wrong text.
- [ ] C. The principle says to remove the model and write the whole system by hand.
- [ ] D. A pure-function checker can return different results on repeated calls with the same input.
- [ ] E. Passing a deterministic check proves the output is correct.

**16.** Two kinds of AI system are compared: a rule-based system, and a system that learns from data (machine learning). Check each statement that is true.  *(5 points)*

- [ ] A. Overfitting means a model does well on its training examples but poorly on new inputs.
- [ ] B. In a rule-based system, a person writes the conditions that decide each output.
- [ ] C. Training data is the set of hand-written conditions that a rule-based system runs on.
- [ ] D. A learned model can give a sensible output for an input that no one wrote a rule for, which is called generalization.
- [ ] E. A rule-based system gives a sensible output for an input that its rules did not anticipate.

**17.** Check each statement that is true about solve-verify asymmetry. Check each statement that is true.  *(5 points)*

- [ ] A. Asking the same model to confirm its own answer is an independent verification.
- [ ] B. The asymmetry holds equally for each task.
- [ ] C. When verifying is as hard as solving, the advantage shrinks.
- [ ] D. Checking a completed Sudoku is easier than solving one.
- [ ] E. The asymmetry suggests generating with a model and verifying with a cheap independent check.

**18.** A Claude Code session runs shell commands. Which setup is an approval gate for `git push`? Check each statement that is true.  *(5 points)*

- [ ] A. A hook that exits non-zero on `git push` until an approval flag exists.
- [ ] B. A permission rule set to ask, so each `git push` pauses for a person to confirm before it runs.
- [ ] C. A line in CLAUDE.md saying "please do not push without asking".
- [ ] D. A pre-run plan that lists a push as step 5, with no stop at that step.
- [ ] E. A system message reporting each push after it finished.

**19.** Which statements about greedy decoding and determinism are true? Check each statement that is true.  *(5 points)*

- [ ] A. Greedy decoding picks the highest-probability token at each step.
- [ ] B. Greedy decoding samples from the distribution, so repeated runs vary.
- [ ] C. A deterministic run gives the same output for the same input and settings.
- [ ] D. Setting the temperature very low makes sampling behave close to greedy decoding.
- [ ] E. Greedy decoding guarantees the answer is correct.

**20.** An assistant model calls a tool during a conversation. Check each statement that is true about tool_use and tool_result. Check each statement that is true.  *(5 points)*

- [ ] A. A tool_result block carries the tool's output back to the model.
- [ ] B. The tool_use block runs the tool inside the model.
- [ ] C. A tool_use block is the model's request to call a named tool with arguments.
- [ ] D. The program around the model, not the model, executes the requested tool.
- [ ] E. The model produces the tool_result itself, inside its own reply.
