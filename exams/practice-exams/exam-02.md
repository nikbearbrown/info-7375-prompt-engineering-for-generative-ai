# INFO 7375 Prompt Engineering for Generative AI: practice exam 02

**PRACTICE FORM. Drawn at random from the question bank; not the real exam; not signed off by the instructor.**

20 questions, 5 points each, 100 points. Name: ______________________

**Scoring.** Five statements, each true or false, 1 point each. The student checks the statements they believe are true. A statement scores 1 point if it is checked and true, or unchecked and false; otherwise 0. Read every statement on its own and decide whether it is true by itself. Strong words (always, never, every, proves) are often what makes a statement false, but a strong-sounding statement is not false for sounding strong.

---

**1.** Which statements about grounding and citation are true? Check each statement that is true.  *(5 points)*

- [ ] A. Grounding is tying an answer to supplied source material.
- [ ] B. A citation points to the source passage behind a claim so a reader can check it.
- [ ] C. A citation proves the claim is true.
- [ ] D. A grounded answer can still misquote or misread its source, so the cited passage is worth checking.
- [ ] E. Grounding means fine-tuning the model on the sources.

**2.** Check each statement that is true about instructions given to a program and instructions given to a language model. Check each statement that is true.  *(5 points)*

- [ ] A. A prompt is context from which a model predicts tokens, whereas code is executed as written.
- [ ] B. A sufficiently precise instruction guarantees that a model follows it the way a compiler follows code.
- [ ] C. A language model's wrong answer can read as fluently as a right one.
- [ ] D. A language model's mistakes surface as exceptions the way program errors do.
- [ ] E. A language model returns identical output on repeated runs even when sampling is on.

**3.** Check each statement that is true about logits and softmax. Check each statement that is true.  *(5 points)*

- [ ] A. The raw logits are already a probability distribution.
- [ ] B. A logit is a probability between 0 and 1.
- [ ] C. Softmax converts the logits into probabilities that sum to one.
- [ ] D. Softmax can give the largest probability to a token whose logit is not the highest.
- [ ] E. Softmax preserves order: the largest logit gets the largest probability.

**4.** Check each statement that names a strength of a well-written pure function compared with a language model. Check each statement that is true.  *(5 points)*

- [ ] A. It interprets vague, ambiguous instructions gracefully.
- [ ] B. Behaviour can be checked with unit tests.
- [ ] C. It can be composed with other functions and reused.
- [ ] D. It has no side effects, so it does not change anything outside itself.
- [ ] E. Same input gives the same output (deterministic).

**5.** Which statements about a tool definition and a tool schema are true? Check each statement that is true.  *(5 points)*

- [ ] A. A tool definition gives the model a tool's name, a description and the parameters it takes.
- [ ] B. A tool schema describes the shape of the arguments, such as field names and types.
- [ ] C. The model runs the tool itself inside its weights.
- [ ] D. The description is text the model reads when deciding whether to call the tool.
- [ ] E. A clear tool description helps the model pick the right tool and fill in arguments.

**6.** Transformers are trained on internet-scale text and used by very many people. Check each statement that is true about parallelism. Check each statement that is true.  *(5 points)*

- [ ] A. Hardware such as GPUs, which perform many calculations at the same time, suits this workload.
- [ ] B. Generation of a reply stays sequential, since each new token depends on the ones before it.
- [ ] C. Because of this parallelism, a transformer generates the tokens of a reply simultaneously.
- [ ] D. During training, a transformer can compute predictions for the positions of a text in the same pass rather than one after another.
- [ ] E. A service can batch requests from many users to use its hardware efficiently.

**7.** Check each statement that uses the terms token, word, token ID and context limit correctly. Check each statement that is true.  *(5 points)*

- [ ] A. A token ID is an integer label for a token in the vocabulary.
- [ ] B. A token ID of 100 means the token is somewhat related to the token with ID 101.
- [ ] C. Pricing, rate limits and context limits are counted in words.
- [ ] D. A tokenizer maps each word to one token.
- [ ] E. A token can be a whole word, part of a word, a single character or punctuation.

**8.** A user tells an AI system, "fix the report". One run lists the paragraphs that should change. A second run returns a rewritten version in the chat window. A third run overwrites the report file on disk. Check each statement that is true.  *(5 points)*

- [ ] A. The wording of the final message reveals which of the three operations took place.
- [ ] B. Saving a new version beside the original carries the same risk as overwriting the original.
- [ ] C. Overwriting the file on disk is a state change that outlasts the conversation.
- [ ] D. Returning a list of suggested changes counts as a write operation.
- [ ] E. A rewrite shown in the chat window has not changed a stored file.

**9.** A team says: "The handshake succeeded, so the server is safe to use on customer data." Decide which statements use interoperability and authorization correctly. Check each statement that is true.  *(5 points)*

- [ ] A. Authorization means two programs can parse each other's messages.
- [ ] B. A successful handshake shows that the server is trustworthy.
- [ ] C. Authorization, meaning whether this server and its tools are allowed in this task, is decided by a person.
- [ ] D. Interoperability is whether a host and a server can exchange messages that both understand.
- [ ] E. MCP's standard message format decides which tools the model may call.

**10.** An engineer sends one factual question to a model three times and reads three answers. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Three identical answers prove the answer is correct.
- [ ] B. Sampling settings can be left unrecorded because a chat interface exposes the same ones.
- [ ] C. To make the check reproducible, the engineer records the prompt, the outputs, the model version, the date and the sampling settings.
- [ ] D. Factual correctness is judged against an independent reference.
- [ ] E. Answers that differ in wording are not automatically a failure, because phrasing and factual correctness are separate questions.

**11.** A user tells Claude Code: "Make the model less random and cut it off before it rambles." Which rewrites use the exact terms? Check each statement that is true.  *(5 points)*

- [ ] A. "Lower the temperature to reduce randomness."
- [ ] B. "Set max tokens to cap the output length."
- [ ] C. "Add a stop sequence so generation ends at a marker such as END."
- [ ] D. "Turn the vocabulary down so it picks fewer words."
- [ ] E. "Use a lower top-p to keep a narrower set of the most probable tokens at each step."

**12.** A user writes to Claude: "In my system prompt, add two examples of the task and call them instructions, and make the answer valid by checking that the schema is true." Which statements spot the imprecise wording? Check each statement that is true.  *(5 points)*

- [ ] A. "Call them instructions" is imprecise: input-output pairs are examples, not instructions.
- [ ] B. "The schema is true" is imprecise: an output is valid against a schema, and truth is a different property.
- [ ] C. "System prompt" is the wrong place because examples do not belong in a system prompt.
- [ ] D. "Two examples" should be "two roles".
- [ ] E. Adding examples makes the prompt zero-shot.

**13.** Check each statement that is falsifiable as stated. Check each statement that is true.  *(5 points)*

- [ ] A. "The model is intelligent in its own way."
- [ ] B. "On the held-out cases, the revised prompt passes more checks than the old one."
- [ ] C. "This function returns a sorted list for each input in test set X."
- [ ] D. A claim is falsifiable if you can say what observation would show it wrong.
- [ ] E. "The new prompt is better."

**14.** Claude Code connects to a database through MCP (Model Context Protocol). Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. An MCP server exposes tools or resources to a client.
- [ ] B. An MCP client is the part inside the host application that connects to a server.
- [ ] C. An MCP server and an MCP client are the same program in two modes.
- [ ] D. MCP settles whether a given server should be trusted with the database.
- [ ] E. A person decides which servers are connected.

**15.** Check each statement that uses the terms context window and memory correctly. Check each statement that is true.  *(5 points)*

- [ ] A. The context window is the model's long-term memory across separate conversations.
- [ ] B. The context window is the number of tokens a model can take in at one time.
- [ ] C. A document that is neither in the training data nor in the context is available to the model.
- [ ] D. Text that is in the context can be used when the model predicts the next token.
- [ ] E. The context window carries information into a later conversation automatically.

**16.** Which one-line instruction to Claude Code correctly compresses: "when the model asks to read a file, run the read and return the file contents to it"? Check each statement that is true.  *(5 points)*

- [ ] A. "Have the model read the file inside the prompt by pasting `tool_result` first."
- [ ] B. "Add a system prompt line saying files are visible."
- [ ] C. "Return a `tool_use` block containing the file text."
- [ ] D. "Handle `tool_use` for `read_file` by running it and returning a `tool_result` with the same `tool_use_id`."
- [ ] E. "Return the file text in `tool_result` content and set `is_error` only if the read failed."

**17.** An agent presents this plan before editing: "I'll refactor the module and update callers as needed." Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. The plan is acceptable because "as needed" lets the agent adapt.
- [ ] B. The plan is too vague to approve: it names no files, order or checks.
- [ ] C. In plan mode the agent researches without editing and presents a plan for approval.
- [ ] D. A plan is useful only after the code is written, so it can be compared with the result.
- [ ] E. A follow-up is: "List the files you will edit, the ones you will not touch, and how each step is checked, before any edit."

**18.** A user types: "Save my work." after Claude Code has edited several files, and wants the changes recorded in the project's history. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. Committing and pushing are two names for the same step.
- [ ] B. "Commit these changes with a message that says why" names the wanted action exactly.
- [ ] C. "Save my work" is exact, since saving and committing mean the same thing.
- [ ] D. Saving a file in an editor creates a commit.
- [ ] E. In git, recording staged changes with a message in the project history is a commit.

**19.** A team has a function that adds tax to a price and a prompt that summarizes support tickets. Decide which statements about a test and an eval are true. Check each statement that is true.  *(5 points)*

- [ ] A. An eval gives the same pass or fail result on each run, as a sampled model is repeatable.
- [ ] B. Test and eval are two names for the same thing.
- [ ] C. An eval scores the quality of model outputs over a set of cases, often reported as a rate, because the outputs vary.
- [ ] D. A test checks a fixed expectation, such as the function returning 10.50 for a given input, and passes or fails the same way each run.
- [ ] E. Running a prompt once and judging the answer by eye gives a sample, not an eval.

**20.** Language models became far more capable over time. Check the statements that use the vocabulary correctly. Check each statement that is true.  *(5 points)*

- [ ] A. Scaling means increasing training data, parameter count and computation together, and it has been a major source of capability gains.
- [ ] B. A model with more parameters has, for that reason alone, been shown to be more accurate on a given task.
- [ ] C. A high benchmark score establishes that a model understands text the way a person does.
- [ ] D. Fine-tuning is the first stage of training and comes before pretraining.
- [ ] E. Pretraining on raw text needs no human label for each example, because the next token in the text serves as the training target (self-supervised learning).
