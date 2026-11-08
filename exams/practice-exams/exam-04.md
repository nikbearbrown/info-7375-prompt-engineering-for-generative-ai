# INFO 7375 Prompt Engineering for Generative AI: practice exam 04

**PRACTICE FORM. Drawn at random from the question bank; not the real exam; not signed off by the instructor.**

20 questions, 5 points each, 100 points. Name: ______________________

**Scoring.** Five statements, each true or false, 1 point each. The student checks the statements they believe are true. A statement scores 1 point if it is checked and true, or unchecked and false; otherwise 0. Read every statement on its own and decide whether it is true by itself. Strong words (always, never, every, proves) are often what makes a statement false, but a strong-sounding statement is not false for sounding strong.

---

**1.** A user adjusts the temperature setting on a chat model. Which statements are true? Check each statement that is true.  *(5 points)*

- [ ] A. A lower temperature sharpens the distribution, so the highest-probability token is chosen more often.
- [ ] B. A higher temperature flattens the probabilities, so less likely tokens are chosen more often.
- [ ] C. Temperature changes the model's weights.
- [ ] D. Temperature rescales the logits before softmax.
- [ ] E. Temperature is a setting chosen at inference time, not something learned in training.

**2.** An agent says: "Retrieval returned the relevant document, so the answer is grounded." The answer states a figure that does not appear in that document. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. A follow-up is: "Quote the sentence in the retrieved passage that supports the figure."
- [ ] B. A citation check compares a claim against the source text.
- [ ] C. The answer is grounded because the retrieved text was in the prompt.
- [ ] D. Retrieval puts text in the context; it does not guarantee the answer uses it.
- [ ] E. A figure that is not in the sources is acceptable if it sounds plausible.

**3.** A model returns the same wrong answer to a factual question on repeated runs at a low temperature. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Checking the answer against an authoritative source would expose the error.
- [ ] B. Agreement among repeated runs is strong evidence of correctness.
- [ ] C. A reference answer is a stronger basis for acceptance than agreement among runs.
- [ ] D. Repeating the answer shows the output is stable, not that it is correct.
- [ ] E. Lowering the temperature to zero would make the answer correct.

**4.** Check each statement that is true about temperature, top-p and sampling settings. Check each statement that is true.  *(5 points)*

- [ ] A. Lowering the temperature does not make a wrong top-ranked answer correct.
- [ ] B. A higher temperature tends to give more varied outputs across runs.
- [ ] C. Temperature and top-p are two names for the same setting.
- [ ] D. Temperature rescales the logits before softmax, so a lower value sharpens the distribution and a higher value flattens it.
- [ ] E. Top-p (nucleus) sampling draws from the smallest set of tokens whose probabilities add up to p.

**5.** Which pairings of a description and a term are correct? Check each statement that is true.  *(5 points)*

- [ ] A. The maximum number of steps the loop may take: step budget.
- [ ] B. The result of an action returned to the model: observation.
- [ ] C. The program around the model that runs tools and feeds back results: controller.
- [ ] D. A fixed pipeline of steps set in code: agent loop.
- [ ] E. A restricted environment where commands run: sandbox.

**6.** A Python function updates a config file by writing to a temporary file in the same folder and then calling os.replace to put it over the real file. A reader may open the config at any moment. Which statements about "atomic" are true? Check each statement that is true.  *(5 points)*

- [ ] A. Opening the config in "w" mode and writing it directly is atomic because Python does it in one call.
- [ ] B. An atomic update either completes in full or leaves no visible change to other readers.
- [ ] C. An atomic write is seen by readers as either the old file or the new file, never a mixture.
- [ ] D. In planning, an "atomic task" means a small step that can be checked alone, which is a different sense from an atomic write.
- [ ] E. Writing a temp file and then os.replace onto the target is a common way to get an atomic file update on one filesystem.

**7.** Two systems use the same model. System X takes a question and returns text. System Y can call a search tool, read files and run shell commands in a loop until a goal is met or a step budget runs out. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Capping Y at a number of steps guarantees it is unable to take an unauthorized action.
- [ ] B. Y is an agent because its actions have results that feed back into its next decision.
- [ ] C. A chatbot becomes an agent by being described as one in marketing.
- [ ] D. In a workflow, the model decides the sequence of steps dynamically, while an agent follows a fixed path.
- [ ] E. A workflow follows a path of steps fixed in code, with the model filling in steps along it.

**8.** Check each statement that is true about the two main parts of a transformer language model: attention, and the step that predicts the next token. Check each statement that is true.  *(5 points)*

- [ ] A. A token has the same internal representation after attention wherever it appears.
- [ ] B. The prediction step includes a truth check on the chosen token.
- [ ] C. Self-attention checks each statement the model writes against a database of verified facts.
- [ ] D. Self-attention lets each token's representation take in information from other tokens in the context.
- [ ] E. The prediction step turns the final representation into a probability for each possible next token.

**9.** A team changes a prompt to fix one complaint, and later finds that answers which used to work now fail. Decide which statements about regression are true. Check each statement that is true.  *(5 points)*

- [ ] A. A regression means the score went up after the change.
- [ ] B. In this setting, a regression is the fitting of a line to a set of data points.
- [ ] C. A regression eval reruns a fixed set of earlier cases after each prompt or model change to see whether anything got worse.
- [ ] D. A regression is a change that breaks something that worked before.
- [ ] E. Deleting an old failing case after it is fixed prevents it from regressing.

**10.** A student sends Claude Code this message: "The MCP thing is broken, it gives an error when I ask for files." Decide which statements correctly name the vague parts or improve the message. Check each statement that is true.  *(5 points)*

- [ ] A. Give the transport, stdio or HTTP, because a connection problem is diagnosed differently for each.
- [ ] B. Say "MCP server" for the program that offers the file tools, instead of "the MCP".
- [ ] C. State whether the failure was a protocol error or a result with isError true, because the two have different causes.
- [ ] D. stdio is the name of the error the student is seeing.
- [ ] E. Say "host" for the program that offers the file tools.

**11.** Which statements about a prompt contract, acceptance criteria and constraints are true? Check each statement that is true.  *(5 points)*

- [ ] A. A prompt contract states the task, the inputs, the constraints, the output format and how the result will be checked.
- [ ] B. An acceptance criterion is a testable condition the output has to meet to be accepted.
- [ ] C. A constraint is a sample answer shown to the model.
- [ ] D. "Write something good" is an acceptance criterion because it states the goal.
- [ ] E. A prompt contract is a legal agreement between the user and the model vendor.

**12.** Which statements tell configuration and weights apart? Check each statement that is true.  *(5 points)*

- [ ] A. Weights are the learned numbers saved in the model file.
- [ ] B. Configuration is the settings and files that shape how the model is run, such as a system prompt, temperature, tools and permissions, without changing weights.
- [ ] C. Editing a system prompt changes the weights.
- [ ] D. Changing the weights takes training, such as fine-tuning.
- [ ] E. Configuration is stored inside the weights.

**13.** A user types to Claude Code: "Write an eval to check that my sort function returns [1, 2, 3] for [3, 1, 2]." Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. "Write a test for the sort function" is the exact request.
- [ ] B. Eval is the right word here because a language model is writing it.
- [ ] C. A test result is repeatable, while an eval over sampled output is reported as a rate or score.
- [ ] D. The request describes a test: a fixed expectation that passes or fails.
- [ ] E. An eval fits scoring Claude's summaries across many cases against a rubric.

**14.** Check each statement that is true about self-attention. Check each statement that is true.  *(5 points)*

- [ ] A. Self-attention is the stage that turns the final representation into next-token probabilities.
- [ ] B. A token's input embedding is the same wherever the token appears, but its representation after attention depends on the surrounding words.
- [ ] C. A model built from a decoder stack attends to earlier tokens when predicting the next token, and not to later ones.
- [ ] D. Each token's new representation is a weighted mix of information from tokens in the context, with weights computed from the tokens themselves.
- [ ] E. Self-attention gives each token in the context the same weight.

**15.** A one-hot vector is as long as the vocabulary, with a 1 at the word's position and 0 elsewhere. An embedding is a shorter dense vector. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. A one-hot vector for a vocabulary of tens of thousands of words has tens of thousands of entries, mostly zero.
- [ ] B. In one-hot coding each pair of different words is equally far apart, so "dog" is no nearer to "cat" than to "carburetor".
- [ ] C. What a model learns about one word through its one-hot vector carries over to similar words.
- [ ] D. An embedding of a few hundred numbers per word is longer than a one-hot vector for the same vocabulary.
- [ ] E. Words next to each other in alphabetical order, such as "cat" and "catalog", tend to be close in meaning.

**16.** Which one-line instruction best compresses: "remember this preference for future sessions"? Check each statement that is true.  *(5 points)*

- [ ] A. "Save this preference to CLAUDE.md so it loads at the start of each session."
- [ ] B. "Fine-tune the model on this preference."
- [ ] C. "Keep this in the context window."
- [ ] D. "Increase the context window to 1M tokens."
- [ ] E. "Write this to the project memory file and confirm the file contents."

**17.** A language model turns a prompt into a reply. Check each statement that names the stages correctly. Check each statement that is true.  *(5 points)*

- [ ] A. Softmax converts the logits into probabilities that sum to one.
- [ ] B. Sampling takes place after softmax, drawing a token according to the probabilities.
- [ ] C. The logits are one raw score for each token in the vocabulary.
- [ ] D. In autoregressive generation, each sampled token is appended to the input and the process repeats.
- [ ] E. Changing the prompt or a setting such as temperature is called fine-tuning.

**18.** A team trains a classifier, tries 12 combinations of learning rate and step count, picks the combination with the highest accuracy on its single evaluation set, and reports that accuracy as expected performance. Check each statement that is true.  *(5 points)*

- [ ] A. The reported accuracy is optimistically biased.
- [ ] B. This is selection on the evaluation set.
- [ ] C. Trying more combinations reduces the bias.
- [ ] D. A second look at the same evaluation set gives a fairer estimate.
- [ ] E. The reported accuracy is an unbiased estimate of performance on new data.

**19.** Which statements about tokens and words are true? Check each statement that is true.  *(5 points)*

- [ ] A. A token is a chunk of text the model reads and writes; it may be a whole word, part of a word, or a punctuation mark.
- [ ] B. Each English word corresponds to one token, so counting words gives the token count.
- [ ] C. A long or rare word is often split into several tokens.
- [ ] D. Token count, not word count, is the unit in which a context window and usage are measured.
- [ ] E. A token is a unit of meaning chosen by a linguist, such as a morpheme.

**20.** An agent ends its summary with: "I tidied some formatting in `billing.py` too." Your instruction said not to touch `billing.py`. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. The change can be accepted because a formatter is deterministic.
- [ ] B. Whitespace-only edits are not a scope violation because behaviour is unchanged.
- [ ] C. A constraint stated before the work is a preference, and the diff need not be checked against it.
- [ ] D. A correct follow-up is: "Revert `billing.py` and show `git diff --stat` so I can confirm only the allowed files changed."
- [ ] E. Editing a file outside the stated scope is a scope violation even when the change is harmless.
