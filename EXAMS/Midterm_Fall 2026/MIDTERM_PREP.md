# INFO 7375 - Midterm Prep: Cheatsheet and Probable Questions

> **See also:** [CHEAT-SHEET.md](CHEAT-SHEET.md), a newer cheat sheet drafted from the instructor's notes (draft for TA review).

**Prompt Engineering & Agentic AI · Prof. Nik Bear Brown · Northeastern University · Fall 2026**

> This is a living study guide. Every section has a short cheatsheet, practice questions in the exam's format, and an answer key you can expand after you try.
> Students are encouraged to contribute questions (see [Contributing](#contributing)).
> A practice chatbot built on this file is planned, so the more good questions we add here, the better it gets.

---

## Exam format: read this first

The midterm uses **multiple-answer questions** (select all that apply).

- More than one option can be correct.
- **Points are deducted for missing correct answers**, so do not stop at the first right option.
- Read every option on its own: "Is this statement true by itself?"
- Watch for absolute words (*always*, *never*, *every*, *proves*). They are usually what makes an option false.

---

## Table of contents

**Part A - Foundations**
1. [A brief history of AI](#1-a-brief-history-of-ai)
2. [What is a model? What is a language model?](#2-what-is-a-model-what-is-a-language-model)
3. [Neural network structure and RNNs](#3-neural-network-structure-and-rnns)
4. [Tokens](#4-tokens)
5. [Softmax and temperature](#5-softmax-and-temperature)
6. [Attention and the Transformer](#6-attention-and-the-transformer)
7. [Programming languages vs language models](#7-programming-languages-vs-language-models)
8. [The strength of functions](#8-the-strength-of-functions)

**Part B - Course chapters**

9. [Chapter 1: Division of Labor and The Gate](#9-chapter-1-division-of-labor-and-the-gate)
10. [Chapter 2: The three-response experiment and what the green cannot distinguish](#10-chapter-2-the-three-response-experiment-and-what-the-green-cannot-distinguish)

**Part C - Agents and verification**

11. [The agentic loop](#11-the-agentic-loop)
12. [Solve-verify asymmetry, fluency, and falsifiability](#12-solve-verify-asymmetry-fluency-and-falsifiability)

**Appendix**
- [Formula sheet](#formula-sheet)
- [Contributing](#contributing)
- [Practice chatbot](#practice-chatbot)

---

# Part A - Foundations

## 1. A brief history of AI

### Cheatsheet

| Year | Milestone |
|---|---|
| 1943 | McCulloch and Pitts publish a mathematical model of an artificial neuron |
| 1950 | Alan Turing publishes "Computing Machinery and Intelligence" (the Turing Test) |
| 1956 | Dartmouth Summer Research Project - the term "artificial intelligence" (coined by John McCarthy in the 1955 proposal) and the founding of AI as a field |
| 1958 | Rosenblatt's Perceptron |
| 1986 | Backpropagation popularized for training multi-layer networks (Rumelhart, Hinton, Williams) |
| 1997 | LSTM introduced (Hochreiter and Schmidhuber) |
| 2012 | AlexNet wins ImageNet - widely seen as the start of the modern deep learning boom |
| 2017 | "Attention Is All You Need" introduces the Transformer |
| 2018-2020 | GPT-1, BERT, GPT-2, GPT-3 - large pretrained language models |
| Nov 2022 | ChatGPT launches and brings LLMs to the general public |

**Common mix-ups**
- AI was **not** founded in 1942. The artificial neuron model is **1943**; AI as a named field is **1956**.
- "AI became famous around 2010" is loosely true: the deep learning wave started in the **early 2010s (2012, AlexNet)**. Mainstream public awareness of LLMs came with **ChatGPT in 2022**.

### Practice questions

**Q1.1** Select all statements that are historically accurate.
- A. McCulloch and Pitts published a mathematical model of an artificial neuron in 1943.
- B. The term "artificial intelligence" comes from the proposal for the 1956 Dartmouth workshop.
- C. AI was founded as a field in 1942.
- D. AlexNet's 2012 ImageNet result is widely seen as the start of the modern deep learning boom.
- E. The Transformer architecture was introduced in 2017.
- F. ChatGPT was released to the public in 2015.

**Q1.2** (Short answer) Put these in order: Transformer paper, Perceptron, Turing's "Computing Machinery and Intelligence", backpropagation popularized.

<details>
<summary>Answer key</summary>

- **Q1.1:** A, B, D, E. (C is wrong: 1943 neuron model, 1956 field. F is wrong: ChatGPT launched November 2022.)
- **Q1.2:** Turing (1950) → Perceptron (1958) → backpropagation popularized (1986) → Transformer (2017).
</details>

---

## 2. What is a model? What is a language model?

### Cheatsheet

- **Model:** a function that maps an **input** to an **output**, `output = f(input; θ)`, where the **parameters θ** (weights) are learned from data.
- **Language model (LM):** a model that assigns a probability to the **next token** given the tokens before it, `P(next token | previous tokens)`.
- **Generation is autoregressive:** predict a distribution → sample one token → append it to the input → repeat.
- **Input → output pipeline of an LLM:** text → tokens → token IDs → embeddings → Transformer layers → **logits** (one score per vocabulary token) → **softmax** → probabilities → sample a token.
- Sending a prompt does **not** change the model's weights. Changing a prompt, context, or setting is not training (Chapter 9 makes this distinction precise).

### Practice questions

**Q2.1** Select all that are true.
- A. A model is a function from inputs to outputs whose parameters are learned from data.
- B. A language model assigns probabilities to possible next tokens given the preceding tokens.
- C. A language model answers by looking up stored answers in a database of facts.
- D. Text generation is autoregressive: each chosen token is fed back as input for the next step.
- E. The model's weights are updated every time you send it a new prompt.

<details>
<summary>Answer key</summary>

- **Q2.1:** A, B, D. (C: an LM computes a distribution, it does not retrieve stored answers. E: inference does not update weights.)
</details>

---

## 3. Neural network structure and RNNs

### Cheatsheet

**Feedforward neural network**
- Layers: **input layer → one or more hidden layers → output layer**.
- Each neuron computes `activation(w · x + b)`: **weights**, **bias**, **nonlinear activation** (ReLU, sigmoid, tanh).
- Without nonlinear activations, any stack of layers collapses into a single linear transformation.
- Training: **forward pass** → **loss** (how wrong the output is) → **backpropagation** (gradients) → **gradient descent** (update weights).

**Recurrent neural network (RNN)**
- Built for sequences. Keeps a **hidden state** that is passed from one time step to the next:
  `h_t = tanh(W·x_t + U·h_(t-1) + b)`
- Processes tokens **one at a time, in order**, so training is hard to parallelize.
- Long sequences cause **vanishing or exploding gradients**, so early information fades.
- **LSTM** and **GRU** add gates that control what to keep and forget, which reduces (but does not eliminate) the problem.
- Transformers replace recurrence with **attention**, so every position can look at every other position directly and training runs in parallel.

### Practice questions

**Q3.1** Select all that are parts of a standard feedforward neural network.
- A. Weights
- B. Biases
- C. Nonlinear activation functions
- D. A compiler that translates the network into English
- E. Hidden layers

**Q3.2** Select all that are true about RNNs.
- A. An RNN carries a hidden state from one time step to the next.
- B. An RNN processes a sequence step by step, which limits parallel training.
- C. Plain RNNs struggle with long-range dependencies because of vanishing or exploding gradients.
- D. LSTMs and GRUs use gating to help preserve information over longer sequences.
- E. RNNs compute attention over all positions at once, exactly like Transformers.

<details>
<summary>Answer key</summary>

- **Q3.1:** A, B, C, E.
- **Q3.2:** A, B, C, D. (E describes Transformers, not RNNs.)
</details>

---

## 4. Tokens

### Cheatsheet

- A **token** is the unit a model's **tokenizer** splits text into. A token can be a whole word, part of a word (subword), a single character, punctuation, or a space-plus-word piece.
- **Token ≠ word.** Common words are often one token; rare or long words are split into several. "unbelievable" might become `un` + `believ` + `able`.
- Rule of thumb for English: **about 0.75 words per token** (about 4 characters per token). This is an approximation, not a constant, and it varies by language and tokenizer.
- **Where arrays come in:**
  - Tokenized text becomes an **array of integer token IDs**. Its length is the number of tokens.
  - The **context window** is the maximum length of that array the model can process at once.
  - Each ID is looked up in an **embedding matrix** of shape `vocab_size × d_model`, so a prompt of `n` tokens becomes an `n × d_model` matrix.
  - The output **logits vector** has length **`vocab_size`** - one score for every token in the vocabulary.
- Pricing, rate limits, and context limits are measured in **tokens**, not words.

### Practice questions

**Q4.1** Select all that are true.
- A. A token can be a whole word, part of a word, a character, or punctuation.
- B. One word always equals exactly one token.
- C. Before the model sees text, it is converted into an array of integer token IDs.
- D. The context window limits how many tokens the model can process at once.
- E. The output logits vector has one entry per token in the vocabulary.
- F. "0.75 words per token" holds exactly for every language and tokenizer.

**Q4.2** (Short answer) A model has a vocabulary of 50,000 tokens and an embedding size of 768. A prompt is tokenized into 12 tokens. What are the sizes of (a) the token ID array, (b) the embedded input matrix, and (c) the logits vector for the next-token prediction?

<details>
<summary>Answer key</summary>

- **Q4.1:** A, C, D, E. (B and F use absolute claims that are false.)
- **Q4.2:** (a) length 12; (b) 12 × 768; (c) length 50,000.
</details>

---

## 5. Softmax and temperature

### Cheatsheet

- A model outputs **logits** (raw scores). **Scores are not probabilities**: `[1, 2, 3]` sums to 6 and is not a distribution.
- **Softmax** turns scores into probabilities:

  `softmax(z)_i = exp(z_i / T) / Σ_j exp(z_j / T)`

- Properties:
  - Every output is between 0 and 1, and they **sum to 1**.
  - It **preserves order**: the largest logit gets the largest probability.
  - It is **shift-invariant**: adding or subtracting the same constant from every logit changes nothing. That is why implementations **subtract the maximum logit first** - it prevents overflow and does not change the result.
- **Temperature T** (must be **> 0**) divides the logits before softmax:
  - **Lower T** (e.g. 0.5) → sharper distribution, the top token dominates. As T → 0 it approaches always picking the top token (greedy).
  - **Higher T** (e.g. 2.0) → flatter distribution, more variety. As T → ∞ it approaches uniform.
  - Temperature changes **how concentrated** the distribution is. It does **not** change which answer is true, and a positive T never reorders the tokens.
- Course worked numbers, logits `[1, 2, 3]`:

  | T | p(token 1) | p(token 2) | p(token 3) |
  |---|---|---|---|
  | 0.5 | 0.016 | 0.117 | 0.867 |
  | 1.0 | 0.090 | 0.245 | 0.665 |
  | 2.0 | 0.186 | 0.307 | 0.506 |

- **Sampling:** draw one token according to those probabilities. With a **fixed seed**, the draws are reproducible. With a finite number of samples, observed counts drift from expected counts.
- Softmax probabilities say **which token will be sampled**. They are **not** calibrated probabilities that a generated claim is **true**. A confident distribution can concentrate on a wrong answer.

### Practice questions

**Q5.1** For logits `[1, 2, 3]` at T = 1, softmax gives about `[0.090, 0.245, 0.665]`. Select all that are true.
- A. The three probabilities sum to 1.
- B. Adding 100 to every logit changes the probabilities.
- C. Subtracting the maximum logit before exponentiating is for numerical stability and does not change the result.
- D. Lowering the temperature to 0.5 increases the probability of token 3.
- E. Changing the (positive) temperature can change which token has the highest probability.
- F. Token 3's probability of 0.665 means there is a 66.5% chance the answer is factually correct.

**Q5.2** Select all that are true about temperature.
- A. Temperature must be greater than zero in the softmax formula.
- B. As temperature grows very large, the distribution approaches uniform.
- C. Lowering temperature can fix an answer when the highest logit belongs to a wrong label.
- D. Higher temperature generally produces more varied outputs across runs.

<details>
<summary>Answer key</summary>

- **Q5.1:** A, C, D. (B: softmax is shift-invariant. E: positive T preserves order. F: sampling probability is not truth probability.)
- **Q5.2:** A, B, D. (C: lower T only concentrates more on the wrong label.)
</details>

---

## 6. Attention and the Transformer

### Cheatsheet

> Recommended video: **Google Cloud Tech - "Attention mechanism: Overview"** (YouTube).

- **Why attention:** in older encoder-decoder RNNs, the whole input was squeezed into one fixed vector. Attention lets the model **look back at all input positions** and weight the relevant ones for each output step.
- **Self-attention** (the Transformer version): each token builds three vectors by learned linear projections:
  - **Query (Q)** - what this token is looking for
  - **Key (K)** - what each token offers
  - **Value (V)** - the information each token passes on
- **Scaled dot-product attention:**

  `Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V`

  1. Score every query against every key (dot product).
  2. Divide by `√d_k` to keep the scores in a stable range.
  3. Softmax each row so the attention weights **sum to 1**.
  4. Output a **weighted sum of the values**.
- **Multi-head attention:** several attention operations run in parallel so different heads can capture different relationships.
- **Positional encoding:** attention by itself has no sense of word order, so position information is added to the embeddings.
- **Causal mask:** in decoder-only LLMs (like GPT and Claude), a token can only attend to earlier tokens, never future ones.
- **Context changes representation:** the vector for "bank" differs in "river bank" vs "bank account". That shows context alters the representation. It does **not** show the model "understood" either sense.

### Practice questions

**Q6.1** Select all that are true about self-attention.
- A. Queries, keys, and values are learned linear projections of token representations.
- B. Attention scores are computed as Q·Kᵀ divided by √d_k.
- C. Softmax over each query's scores produces weights that sum to 1.
- D. The output for each token is a weighted sum of value vectors.
- E. Attention on its own encodes word order, so positional information is unnecessary.
- F. Multi-head attention lets the model attend to different kinds of relationships in parallel.
- G. In a decoder-only language model, a causal mask prevents tokens from attending to future tokens.

**Q6.2** The embedding of "bank" changes when "river" appears nearby. Select all conclusions this supports.
- A. Context changes the model's internal representation of a token.
- B. The model has understood the meaning of "bank".
- C. Attention lets surrounding tokens influence a token's representation.

<details>
<summary>Answer key</summary>

- **Q6.1:** A, B, C, D, F, G. (E: attention is order-agnostic; positional encoding is needed.)
- **Q6.2:** A, C. (B overclaims: a changed vector is not evidence of understanding.)
</details>

---

## 7. Programming languages vs language models

### Cheatsheet

| | Programming language (Python, C, Java) | Language model (Claude, GPT) |
|---|---|---|
| Input | Code in a **formal grammar** | **Natural language** (ambiguous, informal) |
| How it reaches the hardware | Compiled or interpreted into **machine instructions** that execute your exact logic | Text is tokenized and run through a trained network: **matrix multiplications** producing next-token probabilities |
| Behavior | **Deterministic**: same code + same input → same output | **Probabilistic**: outputs are sampled, so they can vary at T > 0 |
| Meaning | Exactly what you wrote | A statistical prediction of a likely continuation |
| Errors | **Explicit** (syntax error, exception, failed test) | **Silent** - a wrong answer looks as fluent as a right one |
| Ambiguous input | Rejected | Always produces *something* |

**Key nuance:** an LLM is not "outside" the computer. It is itself a program doing ordinary arithmetic on CPUs/GPUs. The difference is **how your instruction is interpreted**: a program executes your instruction exactly, while the model treats your prompt as context for predicting tokens.

### Practice questions

**Q7.1** Select all that are true.
- A. Code in a programming language follows a formal grammar and is interpreted unambiguously.
- B. Invalid syntax in a program produces an explicit error.
- C. A language model accepts ambiguous natural language and still produces an output.
- D. A language model runs outside the computer's normal instruction execution.
- E. The same prompt can produce different outputs when sampling at temperature above 0.
- F. A language model's mistakes are reliably flagged as errors.

<details>
<summary>Answer key</summary>

- **Q7.1:** A, B, C, E. (D: the model is ordinary computation. F: LM errors are silent and fluent.)
</details>

---

## 8. The strength of functions

### Cheatsheet

Why the course builds mechanisms as **Python functions** and uses Claude for the fuzzy parts:

- **Deterministic** - a pure function returns the same output for the same input.
- **Testable** - you can write unit tests that pass or fail.
- **Composable and reusable** - small functions combine into larger systems.
- **Exact** - arithmetic, parsing, and comparisons are precise.
- **Explicit contracts** - inputs, outputs, and types can be checked.
- **Inspectable failures** - an exception tells you what broke and where.

**Design rule:** let the model generate, and let functions **check** (validators, schema checks, softmax, path policies). Examples from the course: `probabilities()` and `sample()` in Chapter 1, the JSON contract validator in Chapter 2.

### Practice questions

**Q8.1** Select all that are strengths of a well-written (pure) function compared with a language model.
- A. Same input gives the same output.
- B. Behavior can be checked with unit tests.
- C. Can be composed with other functions and reused.
- D. Interprets vague, ambiguous instructions gracefully.
- E. Performs exact arithmetic and comparisons.
- F. Failures surface as explicit, inspectable errors.

<details>
<summary>Answer key</summary>

- **Q8.1:** A, B, C, E, F. (D is the language model's strength, not a function's.)
</details>

---

# Part B - Course chapters

> Source: [course repository](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai) - read the chapter text in `chapters/` alongside the paired lessons in `lessons/`.

## 9. Chapter 1: Division of Labor and The Gate

<!-- TA NOTE: verify wording of "The Gate" against chapters/01-randomness-and-first-prompts.md before release -->

**Chapter 1 - Randomness and first prompts.** Core capability: calculate and inspect a sampling distribution **without mistaking it for evidence of truth.**

### Cheatsheet

**Division of Labor** - "AI does AI stuff; humans do human stuff", but this never means skipping the learning that makes supervision possible.

| AI should | Human should |
|---|---|
| Help diagnose Python errors **after your first attempt** | **Predict** the temperature effect before running |
| Propose boundary cases | **Build the first version** yourself |
| Run authorized checks | Explain one sample path and one failure **without Claude supplying the answer** |
| Organize the observed results | **Decide what the result supports** and what it does not |

- AI can offer explanations for you to test. It should not manufacture your prediction or present its explanation as proof that you understand.
- **Record the split:** name what you delegated and what you did with the time saved.

**The Gate** - the checkpoint an output must pass before it is accepted or acted on.
- A gate is only useful if it **can reject** an output. A check that passes everything is not a gate.
- The gate is a **check or a human decision**, not the model's own confidence.
- Chapter 1's version of the question: design a check that can reject a **consistently false** answer. Repeating the same wrong answer, or lowering temperature, does not get it through a real gate.

**Other Chapter 1 ideas worth knowing**
- Scores are not probabilities; softmax, stability, temperature, seeded sampling (see [Section 5](#5-softmax-and-temperature)).
- **Consistency vs correctness:** a repeatable answer can still be wrong.
- Scale slogans hide assumptions: 300B tokens × 0.75 words/token = 225B words; at 250 words per minute that is about 1,711 years of reading, and the answer moves by more than a thousand years as the assumed reading rate changes.
- Training that rewards human approval can favor confident-sounding answers over correct ones.

### Practice questions

**Q9.1** Under the course's division of labor, select all tasks that belong to the **human**.
- A. Predicting the effect of temperature before running the code
- B. Building the first version of the implementation
- C. Deciding what the experimental result does and does not support
- D. Organizing the observed sampling results into a table
- E. Explaining one failure case without Claude supplying the answer

**Q9.2** Select all that describe a working "gate".
- A. It is capable of rejecting an output.
- B. It relies on the model's stated confidence.
- C. It can stop a consistently repeated false answer.
- D. It is a check or a human decision placed before acceptance or action.

<details>
<summary>Answer key</summary>

- **Q9.1:** A, B, C, E. (D is listed as something AI can do.)
- **Q9.2:** A, C, D. (B: model confidence is not a gate.)
</details>

---

## 10. Chapter 2: The three-response experiment and what the green cannot distinguish

<!-- TA NOTE: verify section names against chapters/02-prompt-contracts-and-evaluation.md before release -->

**Chapter 2 - Prompt contracts and evaluation.** Core capability: build and evaluate a contract that **separates structural validity from supported claims.**

### Cheatsheet

**The three-response experiment**
- Send the **same** evidence-based prompt **three times**.
- Save the **exact prompt, all outputs, model label, date, and interface**.
- Compare **factual correctness separately from surface variation**:
  - Three different wordings can all be correct.
  - Three identical answers can all be wrong.
- Agreement across runs is **consistency**, not **verification**.
- Do not assume temperature is configurable everywhere - settings differ by model and interface.

**What the green cannot distinguish**
- "Green" = a passing check (validator passes, tests pass, CI shows green).
- Three different kinds of validity - name each failure separately:
  1. **JSON validity** - does it parse?
  2. **Schema validity** - right fields, right types, no extras, non-empty answer, source IDs from the supplied evidence?
  3. **Factual validity** - is the claim actually true and supported by the source?
- The validator checks 1 and 2. **It cannot tell a true claim from a false claim** written in a valid structure with a valid source ID.
- A **format-pass rate is not an accuracy score.**
- A passing test suite establishes **only the tested behavior** - not universal reliability, and not permission to act.

**Other Chapter 2 ideas**
- A prompt is an **experimental intervention**: change one feature at a time.
- Keep **development** cases separate from **held-out** cases, and do not change the test after inspecting results.
- A **persona** is a hypothesis to test, not a source of expertise.

### Practice questions

**Q10.1** A JSON validator passes (green). Select all things that the green result **cannot** distinguish.
- A. A true claim vs a false claim in a correctly structured response
- B. A source ID that supports the claim vs a valid source ID that does not
- C. Malformed JSON vs well-formed JSON
- D. A response with an extra unexpected field vs one without

**Q10.2** About the three-response experiment, select all that are true.
- A. Three identical responses prove the answer is correct.
- B. Variation in wording is not automatically a failure.
- C. You should record the model label, date, and interface.
- D. Factual correctness should be judged separately from surface variation.
- E. Temperature can be set in every Claude interface.

**Q10.3** Select all that are true.
- A. A format-pass rate measures how often the answers are factually correct.
- B. JSON validity, schema validity, and factual validity are different checks.
- C. A passing test suite establishes only the behavior it tests.
- D. Held-out cases should be kept separate from the cases used to revise the prompt.

<details>
<summary>Answer key</summary>

- **Q10.1:** A, B. (C and D are exactly what the validator does catch.)
- **Q10.2:** B, C, D. (A confuses consistency with correctness. E: settings differ by model and interface.)
- **Q10.3:** B, C, D.
</details>

---

# Part C - Agents and verification

## 11. The agentic loop

### Cheatsheet

- **Chat → assistant → agent:** the difference is the **action surface** - what the system can actually do (read files, write files, run tools). Judge by capabilities and consequences, not product labels.
- **The agentic loop:**

  ```
  state → policy chooses an action → controller executes it (tool call)
        → result becomes an observation → state is updated → repeat
        → stop when the goal is met OR the budget runs out
  ```

- **Policy vs controller:** the policy (often the model) *proposes* the next action; the controller *runs the loop* and enforces limits. They are different pieces.
- **Bound the loop:** a maximum number of turns or a budget.
- **Stopping is not always success** - the loop may have stopped because the budget ran out.
- **Repeating the same action is not progress.**
- A bounded loop can still do one **unauthorized** thing, which is why permissions come next (Chapter 5).

### Practice questions

**Q11.1** Select all that are true about an agentic loop.
- A. Each action produces an observation that updates the state for the next step.
- B. The policy and the controller are different pieces.
- C. The loop should have a turn or budget limit.
- D. When the loop stops, the task has succeeded.
- E. Repeating the same search several times counts as progress.
- F. Whether a system is an agent depends on what actions it can take, not on its product name.

<details>
<summary>Answer key</summary>

- **Q11.1:** A, B, C, F. (D: it may have exhausted its budget. E: repetition is not progress.)
</details>

---

## 12. Solve-verify asymmetry, fluency, and falsifiability

### Cheatsheet

**Solve-verify asymmetry**
- For many problems, **checking** a proposed answer is far cheaper than **producing** it.
  - Solving a Sudoku is hard; checking a filled grid is easy.
  - Factoring a large number is hard; multiplying the factors back is easy.
- **Use it:** let the model generate, then verify with a cheap, **independent** check (tests, validators, source lookup).
- **Limit:** the advantage disappears when verifying is as hard as solving (for example, judging a long, novel argument with no ground truth).
- Asking the **same model** "are you sure?" is not an independent check.

**Fluency**
- Fluent = smooth, grammatical, confident-sounding.
- **Fluency is not evidence of correctness.** A wrong answer can be just as fluent as a right one.
- Confident tone is not a calibrated probability of being right.

**Falsifiability** (Karl Popper)
- A claim is falsifiable if you can say **what observation would show it is wrong**.
- Useful claims and useful tests **can fail**. "The prompt is better" is not testable until you say better at what, measured how, on which cases.
- Course habit: **predict before running** - a prediction written down first can be proven wrong by the result.

### Practice questions

**Q12.1** Select all that are true about solve-verify asymmetry.
- A. Checking a completed Sudoku is easier than solving one.
- B. It suggests generating with a model and verifying with a cheap independent check.
- C. The asymmetry holds equally for every task.
- D. Asking the same model to confirm its own answer is an independent verification.
- E. When verifying is as hard as solving, the advantage disappears.

**Q12.2** Select all that are true about fluency.
- A. A fluent answer is not necessarily a correct one.
- B. Training that rewards human approval can favor confident-sounding answers.
- C. A confident tone is a calibrated measure of how likely the answer is to be true.

**Q12.3** Select all claims that are falsifiable as stated.
- A. "This function returns a sorted list for every input in test set X."
- B. "The model is intelligent in its own way."
- C. "For logits [1, 2, 3], lowering temperature to 0.5 raises token 3's probability above 0.8."
- D. "The new prompt is better."

<details>
<summary>Answer key</summary>

- **Q12.1:** A, B, E.
- **Q12.2:** A, B.
- **Q12.3:** A, C. (C is falsifiable and true: 0.867. B and D give no observation that could prove them wrong.)
</details>

---

# Appendix

## Formula sheet

| Concept | Formula |
|---|---|
| Softmax with temperature | `p_i = exp(z_i / T) / Σ_j exp(z_j / T)`, T > 0 |
| Stable softmax | subtract `max(z)` from every logit first (result unchanged) |
| Scaled dot-product attention | `softmax(Q·Kᵀ / √d_k) · V` |
| RNN hidden state | `h_t = tanh(W·x_t + U·h_(t-1) + b)` |
| Neuron | `activation(w · x + b)` |
| Words from tokens (English, approx.) | `words ≈ 0.75 × tokens` |

---

## Contributing

Students are encouraged to add questions. Good questions help everyone and will feed the practice chatbot.

**How to contribute**
1. Fork the repository and create a branch.
2. Add your question under the **matching section** of this file (keep the syllabus order).
3. Use the template below, including an answer key inside `<details>`.
4. Cite where the idea comes from (chapter, lesson, or a primary source).
5. Open a pull request. The TAs will review for technical accuracy before merging.

**Question template**

```markdown
**Q<section>.<next number>** <Question stem>. Select all that apply.
- A. ...
- B. ...
- C. ...
- D. ...

<details>
<summary>Answer key</summary>

- **Q<section>.<number>:** <correct letters>. <One line on why each wrong option is wrong.>
- Source: <chapter / lesson / reference>
</details>
```

**Quality checklist**
- [ ] Every option is clearly true or clearly false on its own.
- [ ] At least one option is false and at least one is true.
- [ ] No trick wording; absolute words only when they are the point.
- [ ] The answer key explains the wrong options.
- [ ] Numbers are recomputed, not copied from memory.

---

## Practice chatbot

A practice chatbot built from this guide is coming. It will quiz you section by section, check your multiple-answer selections, and explain what you missed. Watch this space for the link.

---

*Maintained by the INFO 7375 teaching team. Found an error? Open an issue or a pull request.*
