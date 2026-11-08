# INFO 7375 Prompt Engineering for Generative AI: practice exam 03: KEY

Total 100 points. Statement key: T = true (check it), F = false (leave it blank).

---

**1.** Which one-line instruction best compresses: "before I accept, show me exactly what changed and whether each change belongs to the task"? Check each statement that is true.  *(5 points)*

- [ ] A. "Commit the work with a clear message."
- [ ] B. "Show `git diff` and map each hunk to a requirement; list anything outside the task."
- [ ] C. "Run the tests and tell me if they pass."
- [ ] D. "Summarize what you did in one paragraph."
- [ ] E. "Print the diff and mark hunks that have no requirement behind them."

**Key:** A=F B=T C=F D=F E=T  |  `MA-k01.34`  |  *Jargon test: compress and decompress*  |  source: diff review

- A (false): Commit does not review.
- B (true): Names the artifact and the mapping.
- C (false): Tests do not reveal unrelated edits.
- D (false): A summary is the agent's own description.
- E (true): Same check, other wording.

**2.** Check each statement that is true about picking the next token. Check each statement that is true.  *(5 points)*

- [ ] A. Greedy decoding picks the highest-probability token at each step.
- [ ] B. A token probability of 0.665 means the claim being generated has a 66.5% chance of being factually correct.
- [ ] C. Sampling is another name for choosing the highest-probability token.
- [ ] D. With a fixed random seed, the sampling step can be reproduced.
- [ ] E. Setting the temperature to zero makes the output factually correct.

**Key:** A=T B=F C=F D=T E=F  |  `MA-found.16`  |  *5. Softmax and temperature*  |  source: greedy decoding; sampling; seed

- A (true): Greedy means always taking the top token; it removes sampling randomness.
- B (false): It is the model's probability for that token, not a measure of factual truth.
- C (false): Sampling draws a token at random according to the probabilities.
- D (true): A seed fixes the pseudorandom draws.
- E (false): A low temperature makes output more repeatable, not more true.

**3.** A developer writes to Claude Code: "Make the login page better and tell me when it is done." Check each statement that is true about rewriting this as a prompt contract (task, constraints, output form and acceptance checks). Check each statement that is true.  *(5 points)*

- [ ] A. Adding the phrase "be careful" gives Claude a constraint it can be checked against.
- [ ] B. Asking Claude to confirm that its own work is complete counts as independent verification.
- [ ] C. Replacing "better" with a stated, observable behaviour that a test can check makes the request testable.
- [ ] D. "Tell me when it is done" works as an acceptance gate.
- [ ] E. "Better" is precise enough, because Claude shares the developer's taste.

**Key:** A=F B=F C=T D=F E=F  |  `MA-found.27`  |  *9. Division of labor and acceptance gates*  |  source: prompt contract; vague word

- A (false): A vague phrase cannot be tested, so it does not act as a constraint.
- B (false): Verification needs a check outside the producer.
- C (true): A prompt contract names acceptance checks that can fail.
- D (false): A self-report is a claim, not an independent check.
- E (false): Better is a vague word with no check attached.

**4.** Check each statement that is true when a programming language is compared with a language model. Check each statement that is true.  *(5 points)*

- [ ] A. A programming language follows a formal grammar and is interpreted unambiguously.
- [ ] B. A language model runs outside the computer's normal instruction execution.
- [ ] C. Invalid syntax in a program produces an explicit error.
- [ ] D. A language model rejects ambiguous natural language with an error message.
- [ ] E. The same prompt can produce different outputs when sampling is on.

**Key:** A=T B=F C=T D=F E=T  |  `MA-found.20`  |  *7. Programming languages vs language models*  |  source: formal language vs natural-language prompt

- A (true): Code has defined syntax and semantics.
- B (false): A model is software run on ordinary hardware.
- C (true): Programs fail loudly on malformed input.
- D (false): A language model accepts ambiguous input and still produces output.
- E (true): Sampling makes a language model nondeterministic.

**5.** A model is given a tool named get_weather with a description and a schema asking for a city as a string. A user asks about the weather in one city. Which statements describe what happens? Check each statement that is true.  *(5 points)*

- [ ] A. The model replies with a tool_use naming get_weather and a city argument.
- [ ] B. The program runs the function and returns a tool_result.
- [ ] C. The model reads the tool_result and writes the final answer.
- [ ] D. The schema is what contains the live temperature.
- [ ] E. If the model puts a number where the schema asks for a string city, the call does not match the schema.

**Key:** A=T B=T C=T D=F E=T  |  `MA-j03.12`  |  *Jargon test: agents and tools*  |  source: tool call sequence

- A (true): The model proposes the call.
- B (true): The controller executes and reports back.
- C (true): The loop returns to the model with an observation.
- D (false): The schema describes arguments; the temperature comes in the result.
- E (true): A schema defines types that arguments are checked against.

**6.** A Python script calls Claude to classify a ticket, calls Claude again to draft a reply, and then sends the email, in that fixed order every run. Which statements are true? Check each statement that is true.  *(5 points)*

- [ ] A. A fixed-path workflow is easier to test because the sequence of steps is predictable.
- [ ] B. Wrapping the three calls in a function named agent makes it an agent.
- [ ] C. A step in a workflow can call Claude with a prompt, and the program is still a workflow.
- [ ] D. This is a workflow because code fixes the steps.
- [ ] E. A system where Claude picks among tools and loops until it judges the task done is an agent.

**Key:** A=T B=F C=T D=T E=T  |  `MA-k03.13`  |  *Jargon test: false friends*  |  source: agent vs workflow (fixed)

- A (true): Fewer paths to cover.
- B (false): A name does not give it a decision loop.
- C (true): Model calls inside fixed steps are allowed.
- D (true): Path set in advance.
- E (true): The model chooses the path.

**7.** Check each statement that uses the terms model, weights, training and inference correctly. Check each statement that is true.  *(5 points)*

- [ ] A. Tokens are the learned numbers inside the model, so token and weight are two words for the same thing.
- [ ] B. Sending a prompt to a deployed model trains it on that prompt.
- [ ] C. A model is a function from inputs to outputs whose parameters are learned from data.
- [ ] D. Inference is the stage in which the weights are adjusted from data.
- [ ] E. The weights are chosen by the person who writes each prompt.

**Key:** A=F B=F C=T D=F E=F  |  `MA-found.3`  |  *2. What is a model? What is a language model?*  |  source: model, weights, training vs inference

- A (false): A token is a unit of text, while a weight is a learned parameter.
- B (false): A prompt is input at inference time and does not change the weights.
- C (true): A model is a learned function; its parameters are also called weights.
- D (false): Training adjusts the weights; inference uses fixed weights to produce output.
- E (false): Weights are set during training, not by the prompt writer.

**8.** An agent shows this plan: "Step 3: update the database schema. Step 4: deploy." It lists no check after step 3 and no way back. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. The plan has no verification after an irreversible step and no rollback.
- [ ] B. The plan is complete because the steps are in order.
- [ ] C. A plan should say what each step changes.
- [ ] D. A step that changes a live system needs a stated check and a way back even when it looks simple.
- [ ] E. A follow-up is: "Add an approval gate before step 3 and a check of its result before step 4."

**Key:** A=T B=F C=T D=T E=T  |  `MA-k02.30`  |  *Jargon test: reading agent output*  |  source: planning before acting, approval gate

- A (true): Step 3 may fail halfway.
- B (false): Order is not checking.
- C (true): Reviewers need it to judge scope.
- D (true): Simplicity does not remove the risk.
- E (true): It stops before and verifies after.

**9.** In a long session, Claude Code ignores an instruction the user gave near the start. Decide which statements name the cause and the fix correctly. Check each statement that is true.  *(5 points)*

- [ ] A. The context window is permanent storage that carries across sessions.
- [ ] B. The context window is the limited amount of text the model considers at once.
- [ ] C. In a long session, early messages can be dropped or compressed so they carry less weight.
- [ ] D. Putting a standing rule in CLAUDE.md loads it into the context at the start of a session.
- [ ] E. Starting a subagent erases the parent's context.

**Key:** A=F B=T C=T D=T E=F  |  `MA-j07.15`  |  *Jargon test: saying it exactly to Claude Code*  |  source: context vs memory file

- A (false): Permanent storage across sessions is a file such as CLAUDE.md.
- B (true): Everything has to fit inside it.
- C (true): Long context tends to dilute early text.
- D (true): The memory file is read into context.
- E (false): A subagent has its own context and leaves the parent's alone.

**10.** Check each statement that is true about positional encoding. Check each statement that is true.  *(5 points)*

- [ ] A. Positional encoding is chosen by the person writing each prompt.
- [ ] B. Without positional information, two prompts with the same tokens in different order could look alike to attention.
- [ ] C. Self-attention by itself does not tell the model which token came first.
- [ ] D. Positional encoding is needed whether or not a language has strict word order.
- [ ] E. Positional encoding adds information about each token's position, so the model can use word order.

**Key:** A=F B=T C=T D=T E=T  |  `MA-found.18`  |  *6. Self-attention, positional encoding and the Transformer*  |  source: positional encoding

- A (false): It is part of the model design, not a prompt choice.
- B (true): Attention alone is order-blind.
- C (true): Attention treats the context as a set unless order is added.
- D (true): Order information matters across languages.
- E (true): Position information is what makes order matter.

**11.** An agent loop repeats a cycle: take the current state, choose an action, execute it, observe the result, and decide whether to continue. It stops when the model emits a finish action or after a fixed budget of actions. Check each statement that is true.  *(5 points)*

- [ ] A. The observation step puts the tool result back into the model's context for the next choice.
- [ ] B. Using a loop removes the need for permission boundaries.
- [ ] C. An iteration budget bounds the number of cycles whatever the model decides.
- [ ] D. A finish action from the model shows the final answer was verified.
- [ ] E. A stop condition can be enforced by the harness that wraps the model.

**Key:** A=T B=F C=T D=F E=T  |  `MA-ch03.8`  |  *None*  |  source: The agent loop and stopping

- A (true): Observation closes the loop: the result informs the next action.
- B (false): A loop repeats actions, which makes boundaries more important.
- C (true): A budget (maximum turns) is a stop condition enforced outside the model's choices.
- D (false): Finished means the loop ended, not that the answer was checked against sources.
- E (true): Stopping rules belong to the controller, so they hold even when the model would continue.

**12.** Encoders and decoders are two kinds of transformer block stack. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. An encoder suits a job such as labelling an email urgent or not urgent.
- [ ] B. A decoder can use the tokens that come after the position it is predicting.
- [ ] C. A decoder is the natural choice for writing a long reply, one token at a time.
- [ ] D. A decoder produces output one token at a time, each chosen from the tokens that came before it.
- [ ] E. An encoder reads a whole input and builds a representation of each token that takes the surrounding tokens into account.

**Key:** A=T B=F C=T D=T E=T  |  `MA-found.7`  |  *3. Feedforward networks, encoders, decoders, context and prediction*  |  source: encoder vs decoder

- A (true): Classification needs a representation of the whole input, which an encoder provides.
- B (false): Decoder attention is masked so later positions are hidden.
- C (true): Writing text token by token is the decoder's job.
- D (true): A decoder generates left to right using earlier tokens.
- E (true): An encoder produces context-aware representations of an input.

**13.** Which statements about RAG and chunks are true? Check each statement that is true.  *(5 points)*

- [ ] A. RAG means retrieving relevant passages, adding them to the prompt, then generating.
- [ ] B. A chunk is a piece of a document cut to a size that can be indexed and retrieved.
- [ ] C. Chunking splits the model's vocabulary into groups.
- [ ] D. Chunk size is a trade-off: large chunks dilute the match and use context, and small chunks lose surrounding meaning.
- [ ] E. RAG guarantees correct answers because the source text is supplied.

**Key:** A=T B=T C=F D=T E=F  |  `MA-j04.2`  |  *Jargon test: retrieval, fine-tuning and configuration*  |  source: RAG, chunk

- A (true): Retrieval-augmented generation retrieves before it generates.
- B (true): Documents are split into chunks for retrieval.
- C (false): Chunking splits documents, not the vocabulary.
- D (true): Chunk size affects both match quality and context use.
- E (false): Retrieval can miss or mis-rank, and the model can misread the text.

**14.** An agent sent a refund email that described a policy the company does not have. The email was well-formatted. Decide which statements correctly name and handle the situation. Check each statement that is true.  *(5 points)*

- [ ] A. Adding this case to the regression set keeps the failure from returning unnoticed.
- [ ] B. The invented policy is a hallucination.
- [ ] C. Because the email was well-formatted, the format check shows it was correct.
- [ ] D. An audit log would have stopped the email from going out.
- [ ] E. An approval gate before sending would have given a person the chance to block the email.

**Key:** A=T B=T C=F D=F E=T  |  `MA-j06.14`  |  *Jargon test: evaluation, approval gates and governance*  |  source: incident vocabulary

- A (true): Rerunning past failures catches regressions.
- B (true): Fluent and unsupported content is a hallucination.
- C (false): Format validity is not factual validity.
- D (false): A log records after the fact and does not block.
- E (true): A gate stops the action until a person decides.

**15.** Check each statement that is true about evaluating a prompt. Check each statement that is true.  *(5 points)*

- [ ] A. A format-pass rate measures how often the answers are factually correct.
- [ ] B. Held-out cases are kept separate from the cases used to revise the prompt.
- [ ] C. Changing one feature of a prompt at a time lets a score change be attributed to that feature.
- [ ] D. An eval scores a nondeterministic system over many cases, whereas a unit test checks a deterministic expectation.
- [ ] E. Reusing the held-out cases to revise the prompt is fine, as long as the score then goes up.

**Key:** A=F B=T C=T D=T E=F  |  `MA-found.31`  |  *10. Format validity versus factual validity*  |  source: eval vs test; held-out; one change at a time

- A (false): It measures how often the shape is valid.
- B (true): A held-out set gives an unbiased check on the revised prompt.
- C (true): One change at a time isolates cause.
- D (true): An eval and a unit test differ in what is varied and how pass is decided.
- E (false): Tuning on the held-out cases removes their value as a test.

**16.** Which pairings of a description and a term are correct? Check each statement that is true.  *(5 points)*

- [ ] A. The standing instructions that set the assistant's job before the conversation begins: system prompt.
- [ ] B. A requested character or voice, such as a patient tutor: persona.
- [ ] C. A character that marks where quoted material ends: acceptance criterion.
- [ ] D. Showing no worked examples: few-shot.
- [ ] E. An instruction hidden in a web page the assistant fetches: jailbreak.

**Key:** A=T B=T C=F D=F E=F  |  `MA-j02.10`  |  *Jargon test: prompt structure and contracts*  |  source: name the term

- A (true): That is the system prompt.
- B (true): That is a persona.
- C (false): That is a delimiter.
- D (false): That is zero-shot.
- E (false): That is prompt injection.

**17.** Check each statement that is true about hallucination, error and fluency. Check each statement that is true.  *(5 points)*

- [ ] A. A program crashing with a stack trace is a hallucination.
- [ ] B. A smooth, grammatical answer is good evidence that its claim is correct.
- [ ] C. A hallucination is a fluent output that states something false or unsupported, such as a fabricated citation.
- [ ] D. A confident tone is a measure of how likely the answer is to be true.
- [ ] E. Asking a model for its confidence as a percentage gives a number that matches how often it is right.

**Key:** A=F B=F C=T D=F E=F  |  `MA-found.38`  |  *12. Solve-verify asymmetry, fluency, and falsifiability*  |  source: hallucination vs error; fluency

- A (false): A crash is an explicit error, which is not a hallucination.
- B (false): Fluency and truth are separate.
- C (true): Hallucination is a confident-sounding unsupported output.
- D (false): Tone is style, not a probability of truth.
- E (false): Stated confidence is not calibrated.

**18.** An agent loop: a policy (the model) proposes the next action, a controller (the program around it) executes it, the result returns as an observation, and the state is updated. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. If the loop stops because it reached its step limit, the task has succeeded.
- [ ] B. An observation is the result of an executed action, returned to the loop.
- [ ] C. The policy is the model that proposes the next action.
- [ ] D. A step limit is better enforced by the controller than left to the policy's own judgment.
- [ ] E. The controller is the model that decides what to do next.

**Key:** A=F B=T C=T D=T E=F  |  `MA-found.32`  |  *11. The agentic loop*  |  source: policy; controller; observation; step limit

- A (false): A stop is not success; the goal may be unmet.
- B (true): Observations feed the next decision.
- C (true): Policy is the term for the decision-maker in the loop.
- D (true): The controller does not depend on the model complying.
- E (false): The controller is the surrounding program that executes actions and enforces limits.

**19.** Which statements tell top-p and top-k apart correctly? Check each statement that is true.  *(5 points)*

- [ ] A. Top-k keeps the k most probable tokens and samples among them.
- [ ] B. Top-p keeps the smallest set of most probable tokens whose probabilities add up to p.
- [ ] C. Top-p and top-k are two names for the same setting.
- [ ] D. Top-k picks a candidate set whose size shifts with how confident the model is.
- [ ] E. Top-p limits how many tokens the answer may contain.

**Key:** A=T B=T C=F D=F E=F  |  `MA-j01.5`  |  *Jargon test: sampling and tokens*  |  source: top-p vs top-k

- A (true): Top-k fixes the number of candidates.
- B (true): Top-p fixes a probability mass, so the set size varies.
- C (false): They filter candidates by different rules.
- D (false): That describes top-p; top-k has a fixed size.
- E (false): Answer length is limited by max tokens, not top-p.

**20.** An input embedding is a vector of numbers selected by a token's ID. Check each statement that is true about how embeddings capture meaning. Check each statement that is true.  *(5 points)*

- [ ] A. Tokens with related meanings tend to get vectors that are close together.
- [ ] B. Two tokens with close embeddings have been verified to mean the same thing.
- [ ] C. A person labelled "Labrador" and "sheepdog" as dogs to make their embeddings close.
- [ ] D. The closeness arises because training pulls together tokens that are reasonable predictions in the same contexts.
- [ ] E. An embedding is fixed by hand before training starts and left unchanged.

**Key:** A=T B=F C=F D=T E=F  |  `MA-found.12`  |  *4. Tokens and input embeddings*  |  source: input embedding; semantic closeness

- A (true): Closeness in the embedding space reflects similar use.
- B (false): Closeness shows similar use in text, which is weaker than identical meaning.
- C (false): No one supplied that label; the closeness is a by-product of next-token training.
- D (true): Embeddings are shaped by the prediction task, not by labels from a person.
- E (false): The embedding vectors are parameters adjusted by training.
