# Foundations (midterm-prep sections 1-12)

# 1. A brief history of AI

## MA-found.1

Two kinds of AI system are compared: a rule-based system, and a system that learns from data (machine learning). Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Overfitting means a model does well on its training examples but poorly on new inputs.
- [ ] B. In a rule-based system, a person writes the conditions that decide each output.
- [ ] C. Training data is the set of hand-written conditions that a rule-based system runs on.
- [ ] D. A learned model can give a sensible output for an input that no one wrote a rule for, which is called generalization.
- [ ] E. A rule-based system gives a sensible output for an input that its rules did not anticipate.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Overfitting is fitting the training examples too closely to carry over to new data.
- B: A rule-based system is one whose behaviour comes from hand-written conditions.
- C: Training data is the set of examples a learned model is fitted to, not a rule list.
- D: Generalization is a learned model's ability to handle inputs beyond its training examples.
- E: Rules cover only the cases someone wrote down, so unanticipated inputs fall through.

**Source:** rule-based vs learned; generalization; overfitting

## MA-found.2

Language models became far more capable over time. Check the statements that use the vocabulary correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Scaling means increasing training data, parameter count and computation together, and it has been a major source of capability gains.
- [ ] B. A model with more parameters has, for that reason alone, been shown to be more accurate on a given task.
- [ ] C. A high benchmark score establishes that a model understands text the way a person does.
- [ ] D. Fine-tuning is the first stage of training and comes before pretraining.
- [ ] E. Pretraining on raw text needs no human label for each example, because the next token in the text serves as the training target (self-supervised learning).

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Scaling is growing data, parameters and compute, which has improved model capability.
- B: Parameter count is a size, and accuracy has to be measured with an evaluation.
- C: A benchmark score measures performance on a fixed test set, not human-like understanding.
- D: Fine-tuning continues training a pretrained model on narrower data, so it follows pretraining.
- E: Self-supervised learning builds its own labels from the data, here the next token.

**Source:** self-supervised pretraining; scaling; fine-tuning

# 2. What is a model? What is a language model?

## MA-found.3

Check each statement that uses the terms model, weights, training and inference correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Tokens are the learned numbers inside the model, so token and weight are two words for the same thing.
- [ ] B. Sending a prompt to a deployed model trains it on that prompt.
- [ ] C. A model is a function from inputs to outputs whose parameters are learned from data.
- [ ] D. Inference is the stage in which the weights are adjusted from data.
- [ ] E. The weights are chosen by the person who writes each prompt.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A token is a unit of text, while a weight is a learned parameter.
- B: A prompt is input at inference time and does not change the weights.
- C: A model is a learned function; its parameters are also called weights.
- D: Training adjusts the weights; inference uses fixed weights to produce output.
- E: Weights are set during training, not by the prompt writer.

**Source:** model, weights, training vs inference

## MA-found.4

A language model turns a prompt into a reply. Check each statement that names the stages correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Softmax converts the logits into probabilities that sum to one.
- [ ] B. Sampling takes place after softmax, drawing a token according to the probabilities.
- [ ] C. The logits are one raw score for each token in the vocabulary.
- [ ] D. In autoregressive generation, each sampled token is appended to the input and the process repeats.
- [ ] E. Changing the prompt or a setting such as temperature is called fine-tuning.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Softmax is the step that turns raw scores into a probability distribution.
- B: Sampling draws from the probabilities, so it follows softmax.
- C: Logits are the unnormalized scores that come out of the final layer.
- D: Autoregressive means each output token becomes part of the next input.
- E: Fine-tuning changes the weights; a prompt or setting changes only the input or the sampling.

**Source:** logits, softmax, sampling, autoregressive

## MA-found.5

An analyst wants a language model to help with this morning's news. Check each statement that is true about the model's knowledge cutoff and the options for supplying newer information. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Pasting an article into the conversation retrains the model on that article.
- [ ] B. Placing the article in the context window lets the model use it without changing its weights.
- [ ] C. Fine-tuning changes the weights, so it changes the model's behaviour rather than handing it one day's news.
- [ ] D. Retrieval changes the model's weights so that it remembers the retrieved page.
- [ ] E. The knowledge cutoff is the point after which the training data holds no later events.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: Text in the prompt is context for that conversation, and the weights stay the same.
- B: Supplying text as context is how newer information reaches a model without retraining.
- C: Fine-tuning edits the model, whereas retrieval and prompting supply content.
- D: Retrieval changes what the model sees, not its weights.
- E: A knowledge cutoff marks the end of the model's training data.

**Source:** knowledge cutoff; retrieval vs fine-tuning; context

# 3. Feedforward networks, encoders, decoders, context and prediction

## MA-found.6

Check each statement that is true about the two main parts of a transformer language model: attention, and the step that predicts the next token. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A token has the same internal representation after attention wherever it appears.
- [ ] B. The prediction step includes a truth check on the chosen token.
- [ ] C. Self-attention checks each statement the model writes against a database of verified facts.
- [ ] D. Self-attention lets each token's representation take in information from other tokens in the context.
- [ ] E. The prediction step turns the final representation into a probability for each possible next token.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: After attention a token's representation depends on the surrounding tokens.
- B: Next-token prediction ranks likely continuations, not verified ones.
- C: Attention relates tokens in the context to each other and has no fact database.
- D: Self-attention mixes information across tokens of the context.
- E: The output step produces a distribution over the vocabulary.

**Source:** self-attention vs next-token prediction

## MA-found.7

Encoders and decoders are two kinds of transformer block stack. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An encoder suits a job such as labelling an email urgent or not urgent.
- [ ] B. A decoder can use the tokens that come after the position it is predicting.
- [ ] C. A decoder is the natural choice for writing a long reply, one token at a time.
- [ ] D. A decoder produces output one token at a time, each chosen from the tokens that came before it.
- [ ] E. An encoder reads a whole input and builds a representation of each token that takes the surrounding tokens into account.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Classification needs a representation of the whole input, which an encoder provides.
- B: Decoder attention is masked so later positions are hidden.
- C: Writing text token by token is the decoder's job.
- D: A decoder generates left to right using earlier tokens.
- E: An encoder produces context-aware representations of an input.

**Source:** encoder vs decoder

## MA-found.8

Check each statement that is true about the feedforward network (multi-layer perceptron). Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Its behaviour comes from weights learned from examples.
- [ ] B. A feedforward network that fits its training examples well is certain to predict new inputs well.
- [ ] C. It maps an input vector of numbers to an output by passing values forward through layers.
- [ ] D. Attention, not the feedforward network, is what lets tokens exchange information with each other.
- [ ] E. The nonlinear step between its layers lets it represent relationships that a single weighted sum fails to capture.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: A feedforward network is trained, and the weights store what it learned.
- B: A good fit to training examples does not ensure generalization.
- C: Feedforward means values move in one direction, layer to layer.
- D: Exchanging information across tokens is the job of attention.
- E: Nonlinearity is what gives layered networks more power than a linear rule.

**Source:** feedforward network (MLP)

## MA-found.9

Check each statement that uses the terms context window and memory correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The context window is the model's long-term memory across separate conversations.
- [ ] B. The context window is the number of tokens a model can take in at one time.
- [ ] C. A document that is neither in the training data nor in the context is available to the model.
- [ ] D. Text that is in the context can be used when the model predicts the next token.
- [ ] E. The context window carries information into a later conversation automatically.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: The context window holds one conversation's text; memory across conversations needs a separate mechanism.
- B: The context window is a limit on tokens, covering the prompt and often the reply.
- C: The model has no access to such a document unless a tool retrieves it.
- D: Context is the input the prediction is conditioned on.
- E: The context window does not persist between conversations.

**Source:** context window vs memory

# 4. Tokens and input embeddings

## MA-found.10

Check each statement that uses the terms token, word, token ID and context limit correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A token ID is an integer label for a token in the vocabulary.
- [ ] B. A token ID of 100 means the token is somewhat related to the token with ID 101.
- [ ] C. Pricing, rate limits and context limits are counted in words.
- [ ] D. A tokenizer maps each word to one token.
- [ ] E. A token can be a whole word, part of a word, a single character or punctuation.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Text is converted to token IDs before the model sees it.
- B: Token IDs are arbitrary labels, so nearby numbers say nothing about meaning.
- C: They are counted in tokens, which differ from words.
- D: Long or rare words are often split into several tokens.
- E: Tokens are the units a tokenizer cuts text into, and they vary in size.

**Source:** token vs word; token ID

## MA-found.11

Check each statement that is true about the embedding matrix, the logits and the vocabulary. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The logits vector for next-token prediction has one entry for each token in the vocabulary.
- [ ] B. The embedding dimension is the length of each embedding vector.
- [ ] C. The logits vector has a length equal to the number of tokens in the prompt.
- [ ] D. The embedding matrix has one row for each token in the vocabulary, and the token ID selects the row.
- [ ] E. The vocabulary is the tokenizer's list of tokens, including word pieces.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: The model scores every possible next token.
- B: Dimension is how many numbers describe one token.
- C: Its length is the vocabulary size, regardless of prompt length.
- D: An embedding lookup uses the token ID as an index.
- E: The vocabulary is a list of tokens, not of dictionary words.

**Source:** embedding matrix; logits; vocabulary

## MA-found.12

An input embedding is a vector of numbers selected by a token's ID. Check each statement that is true about how embeddings capture meaning. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Tokens with related meanings tend to get vectors that are close together.
- [ ] B. Two tokens with close embeddings have been verified to mean the same thing.
- [ ] C. A person labelled "Labrador" and "sheepdog" as dogs to make their embeddings close.
- [ ] D. The closeness arises because training pulls together tokens that are reasonable predictions in the same contexts.
- [ ] E. An embedding is fixed by hand before training starts and left unchanged.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Closeness in the embedding space reflects similar use.
- B: Closeness shows similar use in text, which is weaker than identical meaning.
- C: No one supplied that label; the closeness is a by-product of next-token training.
- D: Embeddings are shaped by the prediction task, not by labels from a person.
- E: The embedding vectors are parameters adjusted by training.

**Source:** input embedding; semantic closeness

## MA-found.13

A one-hot vector is as long as the vocabulary, with a 1 at the word's position and 0 elsewhere. An embedding is a shorter dense vector. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A one-hot vector for a vocabulary of tens of thousands of words has tens of thousands of entries, mostly zero.
- [ ] B. In one-hot coding each pair of different words is equally far apart, so "dog" is no nearer to "cat" than to "carburetor".
- [ ] C. What a model learns about one word through its one-hot vector carries over to similar words.
- [ ] D. An embedding of a few hundred numbers per word is longer than a one-hot vector for the same vocabulary.
- [ ] E. Words next to each other in alphabetical order, such as "cat" and "catalog", tend to be close in meaning.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: One-hot length equals vocabulary size.
- B: One-hot vectors carry no similarity information.
- C: With one-hot coding, similar words share nothing, so learning does not transfer.
- D: A dense embedding is much shorter than a one-hot vector.
- E: Alphabetical position is arbitrary with respect to meaning.

**Source:** one-hot vs embedding

# 5. Softmax and temperature

## MA-found.14

Check each statement that is true about logits and softmax. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The raw logits are already a probability distribution.
- [ ] B. A logit is a probability between 0 and 1.
- [ ] C. Softmax converts the logits into probabilities that sum to one.
- [ ] D. Softmax can give the largest probability to a token whose logit is not the highest.
- [ ] E. Softmax preserves order: the largest logit gets the largest probability.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Logits are unnormalized scores and can be negative or larger than one.
- B: A logit is a raw score; the probability appears after softmax.
- C: Softmax normalizes raw scores into a distribution.
- D: Order is preserved, so the top logit stays on top.
- E: Softmax is monotonic in the logits.

**Source:** logits vs probabilities; softmax

## MA-found.15

Check each statement that is true about temperature, top-p and sampling settings. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Lowering the temperature does not make a wrong top-ranked answer correct.
- [ ] B. A higher temperature tends to give more varied outputs across runs.
- [ ] C. Temperature and top-p are two names for the same setting.
- [ ] D. Temperature rescales the logits before softmax, so a lower value sharpens the distribution and a higher value flattens it.
- [ ] E. Top-p (nucleus) sampling draws from the smallest set of tokens whose probabilities add up to p.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Temperature changes variety, not truth.
- B: A flatter distribution gives lower-ranked tokens more chance.
- C: Temperature reshapes the distribution; top-p truncates the candidates.
- D: Temperature controls how peaked the distribution is.
- E: Top-p limits the candidate set by cumulative probability.

**Source:** temperature vs top-p

## MA-found.16

Check each statement that is true about picking the next token. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Greedy decoding picks the highest-probability token at each step.
- [ ] B. A token probability of 0.665 means the claim being generated has a 66.5% chance of being factually correct.
- [ ] C. Sampling is another name for choosing the highest-probability token.
- [ ] D. With a fixed random seed, the sampling step can be reproduced.
- [ ] E. Setting the temperature to zero makes the output factually correct.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Greedy means always taking the top token; it removes sampling randomness.
- B: It is the model's probability for that token, not a measure of factual truth.
- C: Sampling draws a token at random according to the probabilities.
- D: A seed fixes the pseudorandom draws.
- E: A low temperature makes output more repeatable, not more true.

**Source:** greedy decoding; sampling; seed

# 6. Self-attention, positional encoding and the Transformer

## MA-found.17

Check each statement that is true about self-attention. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Self-attention is the stage that turns the final representation into next-token probabilities.
- [ ] B. A token's input embedding is the same wherever the token appears, but its representation after attention depends on the surrounding words.
- [ ] C. A model built from a decoder stack attends to earlier tokens when predicting the next token, and not to later ones.
- [ ] D. Each token's new representation is a weighted mix of information from tokens in the context, with weights computed from the tokens themselves.
- [ ] E. Self-attention gives each token in the context the same weight.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: That conversion is done by the output step and softmax.
- B: Input embeddings are looked up by ID, while attended representations are contextual.
- C: Causal masking hides later positions.
- D: Attention weights depend on content, so they differ between sentences.
- E: Attention weights differ, which is how some tokens count more than others.

**Source:** self-attention; contextual representation

## MA-found.18

Check each statement that is true about positional encoding. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Positional encoding is chosen by the person writing each prompt.
- [ ] B. Without positional information, two prompts with the same tokens in different order could look alike to attention.
- [ ] C. Self-attention by itself does not tell the model which token came first.
- [ ] D. Positional encoding is needed whether or not a language has strict word order.
- [ ] E. Positional encoding adds information about each token's position, so the model can use word order.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: It is part of the model design, not a prompt choice.
- B: Attention alone is order-blind.
- C: Attention treats the context as a set unless order is added.
- D: Order information matters across languages.
- E: Position information is what makes order matter.

**Source:** positional encoding

## MA-found.19

Transformers are trained on internet-scale text and used by very many people. Check each statement that is true about parallelism. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Hardware such as GPUs, which perform many calculations at the same time, suits this workload.
- [ ] B. Generation of a reply stays sequential, since each new token depends on the ones before it.
- [ ] C. Because of this parallelism, a transformer generates the tokens of a reply simultaneously.
- [ ] D. During training, a transformer can compute predictions for the positions of a text in the same pass rather than one after another.
- [ ] E. A service can batch requests from many users to use its hardware efficiently.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Parallel hardware matches the matrix-heavy computation.
- B: Autoregressive dependence forces step-by-step generation.
- C: Generation remains autoregressive, one token at a time.
- D: Training is parallel across positions.
- E: Batching groups requests for parallel processing.

**Source:** parallelism; autoregressive generation

# 7. Programming languages vs language models

## MA-found.20

Check each statement that is true when a programming language is compared with a language model. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A programming language follows a formal grammar and is interpreted unambiguously.
- [ ] B. A language model runs outside the computer's normal instruction execution.
- [ ] C. Invalid syntax in a program produces an explicit error.
- [ ] D. A language model rejects ambiguous natural language with an error message.
- [ ] E. The same prompt can produce different outputs when sampling is on.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Code has defined syntax and semantics.
- B: A model is software run on ordinary hardware.
- C: Programs fail loudly on malformed input.
- D: A language model accepts ambiguous input and still produces output.
- E: Sampling makes a language model nondeterministic.

**Source:** formal language vs natural-language prompt

## MA-found.21

Check each statement that is true about instructions given to a program and instructions given to a language model. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A prompt is context from which a model predicts tokens, whereas code is executed as written.
- [ ] B. A sufficiently precise instruction guarantees that a model follows it the way a compiler follows code.
- [ ] C. A language model's wrong answer can read as fluently as a right one.
- [ ] D. A language model's mistakes surface as exceptions the way program errors do.
- [ ] E. A language model returns identical output on repeated runs even when sampling is on.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Models continue text; programs run instructions.
- B: Precision helps, but a model's compliance is probabilistic.
- C: Fluency does not signal correctness.
- D: Model errors usually arrive as normal-looking text.
- E: Sampling makes repeated outputs vary.

**Source:** code vs prompt; determinism

## MA-found.22

A chat API call has a system prompt and a user turn. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The system prompt and the user turn are stored in the model's weights.
- [ ] B. A rule written in the system prompt is enforced as strictly as a check in the code around the model.
- [ ] C. The user turn is the model's reply to the system prompt.
- [ ] D. A user turn and a system prompt are the same thing, written in two places.
- [ ] E. A system prompt sets standing instructions or a role for the whole conversation.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: Both are input text for the current conversation.
- B: A prompt rule is an instruction the model may not follow; code enforcement does not depend on the model.
- C: The user turn is a message from the user; the reply is the assistant turn.
- D: They are different roles with different purposes.
- E: The system prompt frames the conversation; the user turn is one message.

**Source:** system prompt vs user turn

# 8. The strength of functions

## MA-found.23

Check each statement that names a strength of a well-written pure function compared with a language model. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. It interprets vague, ambiguous instructions gracefully.
- [ ] B. Behaviour can be checked with unit tests.
- [ ] C. It can be composed with other functions and reused.
- [ ] D. It has no side effects, so it does not change anything outside itself.
- [ ] E. Same input gives the same output (deterministic).

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: Handling vague language is a language-model strength, not a function's.
- B: A unit test checks a function against an expected output.
- C: Composability lets small functions build larger ones.
- D: No side effects is part of what makes a function pure.
- E: A pure function has no hidden randomness.

**Source:** pure function; deterministic; unit test

## MA-found.24

A team adopts the principle: the model generates, and ordinary code checks. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A schema validator that rejects a response with a missing required field is a function acting as a checker.
- [ ] B. A function's failure surfaces as an explicit, inspectable error rather than as fluent wrong text.
- [ ] C. The principle says to remove the model and write the whole system by hand.
- [ ] D. A pure-function checker can return different results on repeated calls with the same input.
- [ ] E. Passing a deterministic check proves the output is correct.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: A checker is code that tests an output against an explicit rule.
- B: Explicit failure makes checks reliable.
- C: The model still generates; the code only checks.
- D: Determinism is what a pure function offers.
- E: A check proves only the property it tests.

**Source:** generate, then check with functions

# 9. Division of labor and acceptance gates

## MA-found.25

An acceptance gate is a check or human decision that an output has to pass before it is accepted or acted on. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A rule in the system prompt enforces behaviour as reliably as a check implemented in the code around the model.
- [ ] B. A gate that has accepted each output so far can be assumed to be working.
- [ ] C. A model's own stated confidence is a sufficient gate.
- [ ] D. A gate is meaningful if it is capable of rejecting an output.
- [ ] E. A gate that compares answers with an authoritative source can stop a false answer that the model repeats consistently.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: A prompt rule is an instruction; code enforcement is outside the model.
- B: A gate that never rejects may not be checking anything.
- C: Stated confidence is more model output, not an independent check.
- D: A check that cannot fail gives no assurance.
- E: An external reference is independent of the model.

**Source:** acceptance gate

## MA-found.26

A model returns the same wrong answer to a factual question on repeated runs at a low temperature. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Checking the answer against an authoritative source would expose the error.
- [ ] B. Agreement among repeated runs is strong evidence of correctness.
- [ ] C. A reference answer is a stronger basis for acceptance than agreement among runs.
- [ ] D. Repeating the answer shows the output is stable, not that it is correct.
- [ ] E. Lowering the temperature to zero would make the answer correct.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: An independent reference is a gate that can reject.
- B: A model can be consistently wrong.
- C: A reference is independent of the model, while agreement is not.
- D: Stability and correctness are separate properties.
- E: Temperature affects variety, not truth.

**Source:** stability vs correctness; reference check

## MA-found.27

A developer writes to Claude Code: "Make the login page better and tell me when it is done." Check each statement that is true about rewriting this as a prompt contract (task, constraints, output form and acceptance checks). Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Adding the phrase "be careful" gives Claude a constraint it can be checked against.
- [ ] B. Asking Claude to confirm that its own work is complete counts as independent verification.
- [ ] C. Replacing "better" with a stated, observable behaviour that a test can check makes the request testable.
- [ ] D. "Tell me when it is done" works as an acceptance gate.
- [ ] E. "Better" is precise enough, because Claude shares the developer's taste.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A vague phrase cannot be tested, so it does not act as a constraint.
- B: Verification needs a check outside the producer.
- C: A prompt contract names acceptance checks that can fail.
- D: A self-report is a claim, not an independent check.
- E: Better is a vague word with no check attached.

**Source:** prompt contract; vague word

## MA-found.28

A developer writes to Claude Code: "Refactor the payments module, but propose a plan first and let me review the diff before anything is committed." Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Diff review means asking Claude whether the code looks right.
- [ ] B. Proposing a plan first is planning before acting: the steps are stated before files are edited.
- [ ] C. Diff review means reading the line-level changes before accepting them.
- [ ] D. Naming a plan step and a review step makes the request more precise than writing "be careful".
- [ ] E. Planning before acting means making the edits first and explaining them afterwards.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: That is asking the producer, not reading the change.
- B: Planning before acting separates deciding from doing.
- C: A diff shows exactly what changed.
- D: Named steps can be checked; a general warning cannot.
- E: That reverses the order.

**Source:** planning before acting; diff review

# 10. Format validity versus factual validity

## MA-found.29

A model must answer from supplied sources and return JSON with an answer and a list of cited source identifiers. A validator checks that the output parses as JSON, has the required fields with the right types, and cites identifiers that exist in the supplied list. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Parsing as JSON is syntactic validity, and having the right fields and types is schema validity.
- [ ] B. Passing shows that the cited source supports the answer.
- [ ] C. A response with malformed JSON could still pass, because the validator examines content rather than syntax.
- [ ] D. Measuring accuracy would need a content-level check, such as comparison with reference answers or human review.
- [ ] E. Passing the validator shows the claim in the answer is true.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: These are two format checks of different strictness.
- B: It shows only that the cited identifier exists.
- C: The validator begins by parsing, so malformed JSON fails.
- D: Factual validity is checked against content.
- E: The validator checks shape, not facts.

**Source:** JSON vs schema vs factual validity

## MA-found.30

An engineer sends one factual question to a model three times and reads three answers. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Three identical answers prove the answer is correct.
- [ ] B. Sampling settings can be left unrecorded because a chat interface exposes the same ones.
- [ ] C. To make the check reproducible, the engineer records the prompt, the outputs, the model version, the date and the sampling settings.
- [ ] D. Factual correctness is judged against an independent reference.
- [ ] E. Answers that differ in wording are not automatically a failure, because phrasing and factual correctness are separate questions.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Consistency is not correctness.
- B: Settings can differ and affect output, so they belong in the record.
- C: A reproducible record names all inputs that could change the result.
- D: The reference is outside the model.
- E: Wording variation is not factual error.

**Source:** repeat runs; reproducible record

## MA-found.31

Check each statement that is true about evaluating a prompt. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A format-pass rate measures how often the answers are factually correct.
- [ ] B. Held-out cases are kept separate from the cases used to revise the prompt.
- [ ] C. Changing one feature of a prompt at a time lets a score change be attributed to that feature.
- [ ] D. An eval scores a nondeterministic system over many cases, whereas a unit test checks a deterministic expectation.
- [ ] E. Reusing the held-out cases to revise the prompt is fine, as long as the score then goes up.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: It measures how often the shape is valid.
- B: A held-out set gives an unbiased check on the revised prompt.
- C: One change at a time isolates cause.
- D: An eval and a unit test differ in what is varied and how pass is decided.
- E: Tuning on the held-out cases removes their value as a test.

**Source:** eval vs test; held-out; one change at a time

# 11. The agentic loop

## MA-found.32

An agent loop: a policy (the model) proposes the next action, a controller (the program around it) executes it, the result returns as an observation, and the state is updated. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. If the loop stops because it reached its step limit, the task has succeeded.
- [ ] B. An observation is the result of an executed action, returned to the loop.
- [ ] C. The policy is the model that proposes the next action.
- [ ] D. A step limit is better enforced by the controller than left to the policy's own judgment.
- [ ] E. The controller is the model that decides what to do next.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A stop is not success; the goal may be unmet.
- B: Observations feed the next decision.
- C: Policy is the term for the decision-maker in the loop.
- D: The controller does not depend on the model complying.
- E: The controller is the surrounding program that executes actions and enforces limits.

**Source:** policy; controller; observation; step limit

## MA-found.33

Two systems use the same model. System X takes a question and returns text. System Y can call a search tool, read files and run shell commands in a loop until a goal is met or a step budget runs out. Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Capping Y at a number of steps guarantees it is unable to take an unauthorized action.
- [ ] B. Y is an agent because its actions have results that feed back into its next decision.
- [ ] C. A chatbot becomes an agent by being described as one in marketing.
- [ ] D. In a workflow, the model decides the sequence of steps dynamically, while an agent follows a fixed path.
- [ ] E. A workflow follows a path of steps fixed in code, with the model filling in steps along it.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: A step limit bounds length, not what actions are allowed.
- B: An agent acts in a loop and observes the effects.
- C: The term depends on what the system does, not its label.
- D: This reverses the two terms.
- E: A workflow is predefined; an agent chooses its own steps.

**Source:** agent vs workflow

## MA-found.34

Check each statement that is true about permission and approval gate when Claude Code runs tools. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An approval gate is a point where a person confirms an action before it runs.
- [ ] B. Limiting an agent to tools that read but do not write limits what its mistaken actions can change.
- [ ] C. A step limit replaces the need for permissions.
- [ ] D. Permission and approval gate are two names for the same thing.
- [ ] E. A permission is a rule about which tool actions are allowed, denied or need a prompt.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: An approval gate puts a human decision in the loop.
- B: Narrower permissions reduce the cost of errors.
- C: A step limit bounds length; permissions bound capability.
- D: One is a rule, the other is a human confirmation step.
- E: Permissions define what an agent may do.

**Source:** permission vs approval gate

## MA-found.35

An assistant model calls a tool during a conversation. Check each statement that is true about tool_use and tool_result. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A tool_result block carries the tool's output back to the model.
- [ ] B. The tool_use block runs the tool inside the model.
- [ ] C. A tool_use block is the model's request to call a named tool with arguments.
- [ ] D. The program around the model, not the model, executes the requested tool.
- [ ] E. The model produces the tool_result itself, inside its own reply.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: tool_result is the response returned into the conversation.
- B: It is only a request; running it is done elsewhere.
- C: tool_use is the request the model emits.
- D: The controller or client runs the tool and returns the result.
- E: The result comes from running the tool.

**Source:** tool_use vs tool_result

## MA-found.36

Claude Code connects to a database through MCP (Model Context Protocol). Check each statement that is true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An MCP server exposes tools or resources to a client.
- [ ] B. An MCP client is the part inside the host application that connects to a server.
- [ ] C. An MCP server and an MCP client are the same program in two modes.
- [ ] D. MCP settles whether a given server should be trusted with the database.
- [ ] E. A person decides which servers are connected.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: The server is the provider side.
- B: The client is the consumer side.
- C: They are separate roles.
- D: MCP provides a shared message format, not authorization.
- E: Choosing servers is a human trust decision.

**Source:** MCP server vs client; interoperability vs authorization

# 12. Solve-verify asymmetry, fluency, and falsifiability

## MA-found.37

Check each statement that is true about solve-verify asymmetry. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Asking the same model to confirm its own answer is an independent verification.
- [ ] B. The asymmetry holds equally for each task.
- [ ] C. When verifying is as hard as solving, the advantage shrinks.
- [ ] D. Checking a completed Sudoku is easier than solving one.
- [ ] E. The asymmetry suggests generating with a model and verifying with a cheap independent check.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: A model re-reading its own answer shares its blind spots.
- B: For some tasks verifying is as hard as solving.
- C: The benefit comes from a cheaper check.
- D: Verifying a solution can be easier than finding one.
- E: Generate-then-check uses the cheaper direction.

**Source:** solve-verify asymmetry

## MA-found.38

Check each statement that is true about hallucination, error and fluency. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A program crashing with a stack trace is a hallucination.
- [ ] B. A smooth, grammatical answer is good evidence that its claim is correct.
- [ ] C. A hallucination is a fluent output that states something false or unsupported, such as a fabricated citation.
- [ ] D. A confident tone is a measure of how likely the answer is to be true.
- [ ] E. Asking a model for its confidence as a percentage gives a number that matches how often it is right.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A crash is an explicit error, which is not a hallucination.
- B: Fluency and truth are separate.
- C: Hallucination is a confident-sounding unsupported output.
- D: Tone is style, not a probability of truth.
- E: Stated confidence is not calibrated.

**Source:** hallucination vs error; fluency

## MA-found.39

Check each statement that is falsifiable as stated. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "The model is intelligent in its own way."
- [ ] B. "On the held-out cases, the revised prompt passes more checks than the old one."
- [ ] C. "This function returns a sorted list for each input in test set X."
- [ ] D. A claim is falsifiable if you can say what observation would show it wrong.
- [ ] E. "The new prompt is better."

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: No observation would count against it.
- B: A count on named cases can show the claim wrong.
- C: A test set can produce a failure.
- D: That is the definition of falsifiable.
- E: Better has no stated measure, so no result could contradict it.

**Source:** falsifiability
