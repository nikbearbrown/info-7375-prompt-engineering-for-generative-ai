# INFO 7375 Prompt Engineering: exam cheat sheet

**Status: DRAFT v0.1, 2026-11-04, for TA review.** Written by Claude from the instructor's notes. **The instructor has not signed it off.** Statements that rest on general knowledge, not on a source that was read, are marked *(not checked)*.

## Executive summary

**What this is.** One quick sheet of what you need to know for the midterm, in plain words. Each item says what to know, and where to go if you do not know it yet.

**How to use it.** Read the "ten-second version" first. For any line you cannot say in your own words, follow its **Go to**.

**What the exam asks.** Multiple-answer questions: each statement is true or false on its own. A statement is not false just because it sounds strong; decide whether it is true. The scoring rule is the instructor's to confirm.

**What it tests.** Concepts, not dates or names, and the things an AI cannot do for you: deciding what to do, checking the result, owning the outcome. It does not test layer widths, formulas or recurrent networks.

**Where it stops.** Items 21 to 29 (fine-tuning, training and Hugging Face) are the newest. Their sources are chapter 9, Hugging Face's documentation and two papers. Items 21 to 26 also state general practice from the instructor's discussion; no single source was read for them *(not checked)*.

## The ten-second version

- A model is a function with learned weights; a prompt never changes the weights.
- A language model predicts the next token; it can be fluent and wrong.
- Self-attention learns context; positional encoding adds order; an embedding captures meaning from use.
- Format validity is not factual validity: a green check shows the shape passed.
- An agent loop is a model proposing and a controller acting, observing and feeding back.
- Evidence is something you can confirm without asking the producer. A receipt the agent hands back is still its claim.
- MCP answers interoperability (can we exchange messages?), not authorization (should we use this?). A person decides which servers connect.
- Retrieval changes what the model sees; fine-tuning changes the model. Behavior in the weights, knowledge in the context.
- Frontier training data is a very large filtered slice of text, not "the entire internet".
- A progress bar is completion, not progress. Progress is the job working: validation loss falling and outputs improving.
- Tune on validation data, never on the test set; keep every trial.
- A token is a password: browser login, never pasted, never in a chat or a script.

## Part A: How a language model works

**1. Model and language model.** A model is a function from input to output whose parameters (weights) are learned from data. A language model gives a probability for the next token given the tokens so far. Text comes out by predicting, sampling one token, appending it and repeating (autoregressive). Sending a prompt does not change the weights; changing a prompt, context or setting is not training.
Go to: [chapter 1](../../chapters/01-next-token-prediction-and-sampling.md)

**2. Tokens and embeddings.** Text is split into tokens, which are not always words, and each token is looked up as an embedding, a vector of numbers. A token ID is only a label. An embedding captures meaning because words that are reasonable predictions in the same context end up close ("I walk my Labrador" and "I walk my sheepdog"). One-hot vectors are huge and sparse and make every word equally far from every other; alphabetical numbering is spelling, not meaning. Embeddings squeeze a vocabulary of tens of thousands into about a thousand numbers: they keep meaning efficiently, are lossy, and keep biases.
Go to: [chapter 1](../../chapters/01-next-token-prediction-and-sampling.md)

**3. The transformer, at overview depth.** Two parts: one learns the context with self-attention, the other predicts next-token probabilities. Self-attention lets each token weigh the others. Positional encoding adds word order, which attention alone lacks. An encoder reads; a decoder produces. A feedforward network (multi-layer perceptron) is the common way a network turns inputs into predictions. Transformers train in parallel, which matters at internet scale, but generate one token at a time.
Go to: [chapter 1](../../chapters/01-next-token-prediction-and-sampling.md)

**4. Softmax and temperature.** Logits are raw scores, one per vocabulary token. Softmax turns them into probabilities that sum to one. A lower temperature sharpens them (more repeatable); a higher one flattens them (more varied). Sampling means the same prompt can give different answers.
Go to: [chapter 1](../../chapters/01-next-token-prediction-and-sampling.md)

**5. Programs versus language models.** A program does exactly what its rules say; a language model predicts likely text. A well-written pure function is checkable, repeatable and testable. A sound design rule: let the model generate and let ordinary code check.
Go to: [chapter 2](../../chapters/02-prompt-contracts-and-evaluation.md)

## Part B: The gate and checking

**6. Division of labor and the gate.** AI can draft, compute, retrieve, test and challenge. Humans decide, check and own the result. A gate is a check or human decision an output must pass before it is accepted or acted on.
Go to: [chapter 2](../../chapters/02-prompt-contracts-and-evaluation.md), [chapter 13](../../chapters/13-evaluation-and-approval-gates.md)

**7. Format validity is not factual validity.** Valid JSON can hold a false answer. A validator checks the shape, not whether the claim is true. One prompt run three times gives three samples, not a measurement.
Go to: [chapter 2](../../chapters/02-prompt-contracts-and-evaluation.md)

## Part C: Agents and verification

**8. The agent loop.** A policy (the model) proposes the next action; a controller (the program around it) runs it, observes the result and feeds it back; the loop repeats until a stop. A system that can search, read files or run code is acting; one that only returns text is not, even with the same model.
Go to: [chapter 4](../../chapters/04-the-agent-loop.md)

**9. Solve-verify asymmetry, fluency, falsifiability.** Some things are easier to check than to produce, and a designer can use that to build generate-then-check systems. Fluent is not correct. A claim must be able to be shown wrong: "the prompt is better" becomes falsifiable only with a stated test.
Go to: [chapter 2](../../chapters/02-prompt-contracts-and-evaluation.md), [chapter 11](../../chapters/11-tool-use-and-verification.md)

**10. Evidence you can check independently.** An agent's claim is testimony. Evidence is something a checker can confirm without going through the producer: a reference id looked up at the system of record, a source location, a re-run test. A receipt the agent returns is an artifact it controls until someone verifies it at the payment system. Asking the same kind of model to confirm its own answer gives correlated errors. How much evidence you need scales with the consequence.
Go to: [chapter 11](../../chapters/11-tool-use-and-verification.md), [chapter 12](../../chapters/12-memory-and-multiple-agents.md)

**11. Need to know.** Give an agent only the information and the tools its task needs: less to leak, less damage when it is wrong, less clutter. It covers tool and data access, not just the prompt. A person decides what the task needs.
Go to: [chapter 5](../../chapters/05-tools-and-permissions.md), [chapter 12](../../chapters/12-memory-and-multiple-agents.md)

## Part D: Retrieval, tools and MCP

**12. Retrieval (RAG).** Look up relevant passages, put them in the prompt, then generate. It does not retrain the model and does not guarantee correct answers: retrieval ranks by similarity and can miss or mis-rank. An API call is exact; retrieval is approximate. Use retrieved or system-of-record facts for private, current or exact things; a model can propose steps and order, but facts about the real system must be observed and a plan is reviewed before acting.
Go to: [chapter 7](../../chapters/07-retrieval-and-cowork.md), [chapter 10](../../chapters/10-planning-before-acting.md)

**13. What MCP is.** The Model Context Protocol is an open standard that connects an AI application (the host, through a client) to tools and data (a server). Messages are JSON-RPC 2.0; local servers talk over standard input and output, remote ones over HTTP. A server can offer tools (model-controlled), resources (application-controlled) and prompts (user-controlled). In the course's version (protocol 2025-11-25) the order is: initialize, then the initialized notification, then ordinary requests such as tools/list and tools/call; a request made too early is rejected. **Name the version in an answer**: newer revisions change the handshake.
Go to: [chapter 8](../../chapters/08-mcp-from-scratch.md), [the MCP specification](https://modelcontextprotocol.io)

**14. MCP is not trust.** MCP answers interoperability, not authorization. A valid handshake is not a trust signal. A tool's description is the server's own claim, and it is text the model reads, so misleading text can steer the model. A JSON-RPC error means the protocol failed; a tool result with isError true means the call ran and the tool reported a failure. A person decides which servers are connected.
Go to: [chapter 8](../../chapters/08-mcp-from-scratch.md)

**15. Discover, decide, invoke.** MCP standardizes discovery (the client asks what the server offers, so a model can learn tools that appeared after its training) and invocation. Whether this server belongs in this task stays with a person. The human chooses servers, sets which tools are allowed and when to ask; the agent picks the tool, the arguments and the order; the host enforces the human's policy. Verifying a result is a further step: a signature shows who sent it, not that it is correct.
Go to: [chapter 8](../../chapters/08-mcp-from-scratch.md)

**16. MCP, APIs, REST, function calling and the command line.** An API is any agreed way for one program to use another. REST is one style of web API: resources named by URLs, HTTP verbs as actions, stateless requests, usually JSON. HTTP is the protocol it rides on. Function calling is how a model asks for a tool, and something still has to run it. MCP is a standard way to discover and run tools; servers usually wrap APIs, so it does not replace REST or function calling. Costs of MCP: tool descriptions use context, each server is more code to trust, and the standard keeps changing. For an agent with a shell, a command-line tool is often simpler.
Go to: [chapter 8](../../chapters/08-mcp-from-scratch.md), [chapter 7](../../chapters/07-retrieval-and-cowork.md)

**17. Agents talking to agents.** A2A lets one agent hand work to another; MCP connects an agent to tools and context. The design question is whether to do the task or delegate it, and what comes back. Keep three questions apart: who is this agent (identity), may it have this task and information (authorization), and did it do the work correctly (correctness, which only evidence answers). Delegating does not hand off responsibility.
Go to: [chapter 12](../../chapters/12-memory-and-multiple-agents.md)

**18. Giving a model information it does not have.** A model knows what its training data held, up to a cutoff. Frontier training data is a very large but filtered slice of text (blocked, login-gated and duplicate pages are left out; licensed and synthetic data are added), not "the entire internet" *(this description rests on secondary summaries of model documentation; not checked against the primary documents)*. New information reaches a model through its input: pasted text or a screenshot, a search, a fetched page, retrieval, or a connected tool. None of these changes the weights. A cited answer is not verified, a site can block the tool's crawler, and a person chooses the sources.
Go to: [chapter 7](../../chapters/07-retrieval-and-cowork.md), [chapter 8](../../chapters/08-mcp-from-scratch.md)

## Part E: Training and fine-tuning

**19. Five things a system can change.** Weights, prompt, context, tools and settings. Only the weights involve an optimizer. A saved prompt, a stored document, a permission rule and a memory record all persist, and none of them is training. Training is identified by its mechanism: labels and a loss-derived gradient changing parameters. The test: change one object, hold the rest fixed, and watch.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md), [lesson 9](../../lessons/09-training-and-configuration/docs/en.md)

**20. Held-out data, loss and what you may claim.** Training, development and held-out data have different roles; held-out data is touched once, after every choice is fixed. A lower training loss supports one claim: the objective fell on the examples shown. It does not show the model fits unseen data or that the objective was the right one. Prediction is not intervention: a fitted model answers "what will it say", not "what happens if we act". "Lowered the objective" and "learned" (a parameter change) are accurate verbs; "generalizes" needs a held-out result; "causes" needs assumptions the data cannot supply.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md)

**21. What fine-tuning is, and how it works.** Continue training an already-trained model on a small, targeted set so its weights shift: start from pretrained weights, collect example pairs (or better-and-worse pairs), choose an objective (a loss), run predict, measure the loss, compute the gradient, update, at a small learning rate for a few passes, then check on held-out examples and keep the result as a new artifact. It suits style, format, a narrow skill and consistency. It is a poor way to add a lot of fresh or changing facts, and it does not learn from a chat. Risks: overfitting, forgetting other abilities, flawed examples baked in.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md), [the LoRA paper](https://arxiv.org/abs/2106.09685)

**22. Fine-tuning, retrieval or a system prompt.** Fine-tuning changes the model; retrieval changes what the model sees this turn; a system prompt is standing instructions in the context. Behavior goes in the weights, knowledge in the context. Try the cheap and reversible first: prompt, then context, then tools, then fine-tuning. Retrieval can cite its sources and update instantly; fine-tuned knowledge cannot be traced or easily removed. Many small models (such as T5) have no system prompt at all: just an input and an output.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md), [chapter 7](../../chapters/07-retrieval-and-cowork.md)

**23. Why customize.** Fine-tuning can give a model your voice, your drawing hand or your writing style: things you show, not describe. Train only on your own work or with written consent, say when a voice or an image is synthetic, and guard the weights like a password. For a portfolio piece, the evidence is what counts, not the score.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md)

**24. Hyperparameters.** Settings you choose that control training; the gradient does not learn them. The main ones: learning rate (the most important, with its schedule), batch size, epochs or steps with early stopping, optimizer settings (weight decay, gradient clipping), dropout, sequence length, numeric precision and the random seed; for LoRA also the rank, a scaling factor and which layers. Tune on validation data, never the test set; change one thing at a time; random search often matches a grid with fewer runs *(not checked)*; keep every trial; a difference smaller than the gap between two seeds means nothing.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md), [the QLoRA paper](https://arxiv.org/abs/2305.14314)

**25. Progress is the job working, not the bar moving.** A progress bar (epoch 2 of 3) measures completion. Progress is evidence the task is working: validation loss falling, a task score above a baseline, outputs improving. In a long run check in the first percent or so and write an early go or no-go check into the gate, so a setup mistake costs minutes, not days. Watch two curves, training loss and validation loss. Shapes: healthy; plateau; overfitting (validation turns up while training keeps falling); never started (flat from step zero); diverged. Checks that it started: some weight changed, the loss moved, one small batch can be overfit. A flat late loss may only be the learning rate decaying. Loss shows the setup is sound; a task score shows the job works; watch both, on validation data, against a baseline.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md)

**26. Checkpoints.** A checkpoint is a saved snapshot of a run. A full one also holds the optimizer and schedule state, so a run can resume; weights alone are enough to use the model. Use them to recover from a crash or a job time limit, to keep the best (often not the last), to compare, and to branch. Evaluate more often than you save; keep the last two or three plus the best; write the interval and the keep-count in the gate. Compare checkpoints on a fixed panel: the same sample and the same few example outputs each time.
Go to: [chapter 9](../../chapters/09-training-and-configuration.md)

**27. LoRA, QLoRA and quantization.** LoRA freezes the pretrained weights and trains two small low-rank matrices per chosen layer: far fewer trainable parameters, a small adapter file, and no slowdown at inference once merged. Quantization stores numbers with fewer bits and is lossy. QLoRA is LoRA on a frozen 4-bit base (4-bit NormalFloat, double quantization, paged optimizers); its paper reports fine-tuning a 65-billion-parameter model on one 48 GB GPU while matching 16-bit fine-tuning, where regular 16-bit fine-tuning needs more than 780 GB. How few bits are enough is not settled by theory: measure it with a bit ladder on held-out data, with the tolerance set before you look.
Go to: [the LoRA paper](https://arxiv.org/abs/2106.09685), [the QLoRA paper](https://arxiv.org/abs/2305.14314)

**28. Hugging Face and its tools.** The Hub hosts models and datasets. The Python libraries do the training, on any machine, laptop or cluster (PyTorch is installed separately). The `hf` command-line tool does Hub chores such as login, download, upload and launching jobs; it does not train. Hugging Face's MCP server is an agent's interface to the Hub (search, documentation, optional repository and job tools). Spaces host apps and demos, not training; Jobs are paid compute. To read a model listing: the task tag is input to output, then size, base model, licence and the maker's own benchmark claims. Downloads show attention, not quality.
Go to: [the CLI guide](https://huggingface.co/docs/huggingface_hub/guides/cli), [the MCP server docs](https://huggingface.co/docs/hub/agents-mcp), [Jobs](https://huggingface.co/docs/huggingface_hub/guides/jobs), [Spaces GPUs](https://huggingface.co/docs/hub/spaces-gpus)

**29. Access tokens.** A token is a password. It never goes in code, a chat with an AI tool, a command line, a batch script or a screenshot. Use the browser login, make a fine-grained token if you need one, one per place you use it, log in only when you publish, and revoke a token at once if it may have leaked.
Go to: [Hugging Face on access tokens](https://huggingface.co/docs/hub/security-tokens)

## For the TAs: please review this sheet

**What we need from you.** Read it as a student would the night before the exam, and tell us:

1. **Accuracy.** Anything wrong, overstated or out of date? Name the item number.
2. **Clarity.** Anything you could not say in your own words after reading it?
3. **Coverage.** Anything the exam is likely to ask that is missing, or anything here that will not be asked?
4. **Length.** Where would you cut so it fits a quick read?
5. **Go to links.** Does each one lead to the place the idea is really taught? Any that are broken?
6. **Open questions for the instructor:** the scoring rule for the multiple-answer questions; whether items 21 to 29 are on the exam and how deep; whether the date and recurrent-network items in the older student study guide should be removed.

**How to send it.** Open an issue on this repository titled "Cheat sheet feedback" with the item number and your suggestion, or propose an edit as a pull request. One item per comment helps.

**Review log.** Each round of feedback is recorded here, with what changed.

| Date | Who | What changed |
|---|---|---|
| 2026-11-04 | Claude | First draft (v0.1) from the instructor's notes; not reviewed by anyone yet |
