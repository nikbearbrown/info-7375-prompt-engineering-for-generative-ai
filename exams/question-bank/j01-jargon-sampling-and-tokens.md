# Jargon test: sampling and tokens

## MA-j01.1

Which statements about tokens and words are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A token is a chunk of text the model reads and writes; it may be a whole word, part of a word, or a punctuation mark.
- [ ] B. Each English word corresponds to one token, so counting words gives the token count.
- [ ] C. A long or rare word is often split into several tokens.
- [ ] D. Token count, not word count, is the unit in which a context window and usage are measured.
- [ ] E. A token is a unit of meaning chosen by a linguist, such as a morpheme.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: A token is the unit a model reads and writes, produced by a splitting scheme.
- B: Tokens and words differ; one word can be several tokens and a token can be less than a word.
- C: Uncommon words are broken into smaller known pieces.
- D: Limits and billing are counted in tokens.
- E: Token boundaries come from a learned splitting scheme, not linguistic analysis.

**Source:** token vs word

## MA-j01.2

Which statements about vocabulary and embeddings are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The vocabulary is the fixed list of tokens a model can read and produce.
- [ ] B. An embedding is the list of tokens a model knows.
- [ ] C. An embedding is a vector of numbers looked up for a token, and tokens used in similar contexts end up close together.
- [ ] D. A token ID carries meaning: tokens with nearby ID numbers have nearby meanings.
- [ ] E. The vocabulary is the set of words in the user's current prompt.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Vocabulary is the model's token inventory.
- B: That list is the vocabulary; an embedding is a vector of numbers.
- C: An embedding places a token in a space where closeness reflects use.
- D: A token ID is a label; meaning lives in the embedding.
- E: The vocabulary belongs to the model and does not change with the prompt.

**Source:** vocabulary vs embedding

## MA-j01.3

A model scores the next token. Which statements about logits and softmax are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Logits are raw scores, one per vocabulary token, before they become probabilities.
- [ ] B. Softmax turns logits into probabilities that add up to one.
- [ ] C. Logits are the probabilities produced after softmax.
- [ ] D. Softmax chooses the token that is written to the output.
- [ ] E. A logit can be negative or larger than one, which is not possible for a probability.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: Logits are the unnormalized outputs of the model.
- B: Softmax normalizes scores into a probability distribution.
- C: Logits come first; probabilities come after softmax.
- D: Softmax only converts scores; a decoding step then picks a token.
- E: Logits are unbounded scores.

**Source:** logits vs softmax

## MA-j01.4

A user adjusts the temperature setting on a chat model. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A lower temperature sharpens the distribution, so the highest-probability token is chosen more often.
- [ ] B. A higher temperature flattens the probabilities, so less likely tokens are chosen more often.
- [ ] C. Temperature changes the model's weights.
- [ ] D. Temperature rescales the logits before softmax.
- [ ] E. Temperature is a setting chosen at inference time, not something learned in training.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Low temperature concentrates probability on top tokens.
- B: High temperature spreads probability out.
- C: Temperature is a sampling setting; weights stay the same.
- D: Dividing logits by the temperature changes how peaked the probabilities are.
- E: It is configuration of the sampler, not a learned parameter.

**Source:** temperature

## MA-j01.5

Which statements tell top-p and top-k apart correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Top-k keeps the k most probable tokens and samples among them.
- [ ] B. Top-p keeps the smallest set of most probable tokens whose probabilities add up to p.
- [ ] C. Top-p and top-k are two names for the same setting.
- [ ] D. Top-k picks a candidate set whose size shifts with how confident the model is.
- [ ] E. Top-p limits how many tokens the answer may contain.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Top-k fixes the number of candidates.
- B: Top-p fixes a probability mass, so the set size varies.
- C: They filter candidates by different rules.
- D: That describes top-p; top-k has a fixed size.
- E: Answer length is limited by max tokens, not top-p.

**Source:** top-p vs top-k

## MA-j01.6

Which statements about greedy decoding and determinism are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Greedy decoding picks the highest-probability token at each step.
- [ ] B. Greedy decoding samples from the distribution, so repeated runs vary.
- [ ] C. A deterministic run gives the same output for the same input and settings.
- [ ] D. Setting the temperature very low makes sampling behave close to greedy decoding.
- [ ] E. Greedy decoding guarantees the answer is correct.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Greedy decoding takes the top token without sampling.
- B: Sampling is what makes runs vary; greedy decoding does not sample.
- C: Determinism means repeatable output.
- D: A sharp distribution makes the top token win nearly each time.
- E: Picking the most probable token is not a check on truth.

**Source:** greedy decoding, determinism

## MA-j01.7

A user wants Claude to carry on after a long chat. Which single statement uses the terms correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A context window is long-term storage where the model keeps facts about the user between chats.
- [ ] B. The context window is the span of tokens the model can take in and use in one request.
- [ ] C. A chat assistant remembers earlier chats because its weights update after each conversation.
- [ ] D. When a conversation outgrows the context window, the model retrains itself on the overflow.
- [ ] E. Memory and context window are two names for the same thing.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: That describes memory; the context window is the span of tokens in one request.
- B: The context window is a size limit on what the model sees at once.
- C: Prompts do not change weights; remembered notes are put back into the context.
- D: Overflow is trimmed or summarized; no training occurs.
- E: Memory is stored information; the context window is a per-request limit.

**Source:** context window vs memory

## MA-j01.8

Which statements about stop sequences and max tokens are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A stop sequence is a string that, once generated, ends the output.
- [ ] B. Max tokens is a cap on the length of the output.
- [ ] C. Max tokens tells the model to plan a shorter, more concise answer.
- [ ] D. A stop sequence is the token count at which generation ends.
- [ ] E. When output reaches the max tokens cap, the model finishes the sentence before stopping.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: A stop sequence is a marker that halts generation.
- B: Max tokens limits how many tokens can be generated.
- C: It cuts output off at the cap; it does not change how the model plans.
- D: That describes max tokens.
- E: Generation is cut off at the cap, possibly mid-sentence.

**Source:** stop sequence vs max tokens

## MA-j01.9

Which statements about next-token prediction are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A language model gives a probability for the next token given the tokens so far.
- [ ] B. Text is produced by sampling a token, appending it and repeating; this is called autoregressive generation.
- [ ] C. The model plans the whole answer first and then writes it out.
- [ ] D. Fluent output shows the predicted tokens were plausible, not that the claims are true.
- [ ] E. Changing the prompt changes the input, not the model's parameters.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: That is next-token prediction.
- B: Autoregressive means each output token feeds back as input.
- C: Generation proceeds one token at a time.
- D: Fluency and truth are different properties.
- E: A prompt does not retrain the model.

**Source:** next-token prediction

## MA-j01.10

A student sends Claude: "Set the temperature to zero so the model remembers my earlier chat and gives the exact same answer, and stop it at 200 words." Which statements spot the imprecise wording? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Remembers my earlier chat" mixes up temperature with memory or context.
- [ ] B. "Stop it at 200 words" should be a max tokens limit, since the cap is counted in tokens.
- [ ] C. "Temperature" is the wrong term for this; the student should have said top-k.
- [ ] D. "Temperature" is an acceptable term for the setting that makes sampling less random.
- [ ] E. "Model" is the wrong word because the prompt is read by an embedding.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Temperature is a sampling setting; carrying earlier chat needs context or stored memory.
- B: Length caps are set in tokens.
- C: Temperature is the right term for how random sampling is.
- D: Lower temperature reduces randomness.
- E: The model reads the prompt; an embedding is a vector for a token.

**Source:** spot the wrong word

## MA-j01.11

Which pairings of a described behaviour and a term are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The raw output scores for each possible next token: logits.
- [ ] B. The step that turns scores into probabilities that add up to one: embedding.
- [ ] C. The largest amount of text the model can consider in one request: context window.
- [ ] D. Sampling among a fixed count of the most probable tokens: top-p.
- [ ] E. A string that ends generation when it appears: max tokens.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Logits are the pre-softmax scores.
- B: That step is softmax.
- C: The context window bounds what the model sees at once.
- D: Sampling among a fixed count is top-k.
- E: That is a stop sequence; max tokens is a length cap.

**Source:** name the term

## MA-j01.12

A user tells Claude Code: "Make the model less random and cut it off before it rambles." Which rewrites use the exact terms? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Lower the temperature to reduce randomness."
- [ ] B. "Set max tokens to cap the output length."
- [ ] C. "Add a stop sequence so generation ends at a marker such as END."
- [ ] D. "Turn the vocabulary down so it picks fewer words."
- [ ] E. "Use a lower top-p to keep a narrower set of the most probable tokens at each step."

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: Temperature governs sampling randomness.
- B: Max tokens bounds output length.
- C: A stop sequence ends output at a chosen string.
- D: Vocabulary is the model's fixed token list, not a setting.
- E: A lower top-p narrows the candidate set.

**Source:** choose the rewrite
