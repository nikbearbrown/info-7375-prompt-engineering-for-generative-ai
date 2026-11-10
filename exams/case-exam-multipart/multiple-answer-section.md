# Multiple-answer section: eight questions, 40 points

> Drawn unchanged (stems lightly cleaned of a repeated sentence) from the INFO 7375 question bank in `interview-bank/info-7375-prompt-engineering-for-generative-ai`. The bank copy is the source of truth; the bank id is in the TA key only.

---

## STUDENT PAGE

Each question has five statements. Check each statement that is true. Each statement is worth 1 point (5 points per question, 40 points in all).

### M1

Check each statement that uses the terms model, weights, training and inference correctly. Check each statement that is true.

- [ ] A. Tokens are the learned numbers inside the model, so token and weight are two words for the same thing.
- [ ] B. Sending a prompt to a deployed model trains it on that prompt.
- [ ] C. A model is a function from inputs to outputs whose parameters are learned from data.
- [ ] D. Inference is the stage in which the weights are adjusted from data.
- [ ] E. The weights are chosen by the person who writes each prompt.

### M2

An acceptance gate is a check or human decision that an output has to pass before it is accepted or acted on. Check each statement that is true.

- [ ] A. A rule in the system prompt enforces behaviour as reliably as a check implemented in the code around the model.
- [ ] B. A gate that has accepted each output so far can be assumed to be working.
- [ ] C. A model's own stated confidence is a sufficient gate.
- [ ] D. A gate is meaningful if it is capable of rejecting an output.
- [ ] E. A gate that compares answers with an authoritative source can stop a false answer that the model repeats consistently.

### M3

An agent loop: a policy (the model) proposes the next action, a controller (the program around it) executes it, the result returns as an observation, and the state is updated. Check each statement that is true.

- [ ] A. If the loop stops because it reached its step limit, the task has succeeded.
- [ ] B. An observation is the result of an executed action, returned to the loop.
- [ ] C. The policy is the model that proposes the next action.
- [ ] D. A step limit is better enforced by the controller than left to the policy's own judgment.
- [ ] E. The controller is the model that decides what to do next.

### M4

Two systems use the same model. System X takes a question and returns text. System Y can call a search tool, read files and run shell commands in a loop until a goal is met or a step budget runs out. Check each statement that is true.

- [ ] A. Capping Y at a number of steps guarantees it is unable to take an unauthorized action.
- [ ] B. Y is an agent because its actions have results that feed back into its next decision.
- [ ] C. A chatbot becomes an agent by being described as one in marketing.
- [ ] D. In a workflow, the model decides the sequence of steps dynamically, while an agent follows a fixed path.
- [ ] E. A workflow follows a path of steps fixed in code, with the model filling in steps along it.

### M5

Claude Code connects to a database through MCP (Model Context Protocol). Check each statement that is true.

- [ ] A. An MCP server exposes tools or resources to a client.
- [ ] B. An MCP client is the part inside the host application that connects to a server.
- [ ] C. An MCP server and an MCP client are the same program in two modes.
- [ ] D. MCP settles whether a given server should be trusted with the database.
- [ ] E. A person decides which servers are connected.

### M6

A team must adapt an assistant to company policies and compares three approaches: editing the prompt, adding retrieval over a policy corpus, and fine-tuning. Check each statement that is true.

- [ ] A. Editing the prompt changes behaviour without a training job.
- [ ] B. Fine-tuning changes the weights, so the change is harder to inspect and reverse than a prompt edit.
- [ ] C. Retrieval hides the supplied passage from a reader checking the answer.
- [ ] D. A policy change is easiest to roll out by retraining the model.
- [ ] E. Retrieval changes the weights so the model memorizes the corpus.

### M7

A reviewer looks at the trace of an agent run, the record of its actions and observations. Check each statement that is true.

- [ ] A. To tell which request produced which observation, the arguments need to be recorded alongside the observations.
- [ ] B. A trace records events, namely what was requested and what came back; it is not knowledge about why the model chose them.
- [ ] C. Two identical observations from two lookups can come from different keys, so the second lookup is not necessarily redundant.
- [ ] D. The trace alone is enough to reconstruct why a run stopped.
- [ ] E. A visible trace shows the model's complete private reasoning.

### M8

A harness lets the model request up to three tool calls in parallel in one response. Check each statement that is true.

- [ ] A. A budget counted in turns does not bound the number of tool calls when several can be requested per turn.
- [ ] B. A budget counted in tool calls bounds the number of side effects more directly than a turn budget.
- [ ] C. Each parallel call counts as a separate turn.
- [ ] D. A cost budget in currency bounds spend even when turns differ in price.
- [ ] E. Parallel tool calls means several tool_use blocks in one model response.

---

## TA KEY PAGE (do not hand to students)

### M1  (Part A: How a language model works; bank id MA-found.3; 1 true)

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A token is a unit of text, while a weight is a learned parameter.
- B: A prompt is input at inference time and does not change the weights.
- C: A model is a learned function; its parameters are also called weights.
- D: Training adjusts the weights; inference uses fixed weights to produce output.
- E: Weights are set during training, not by the prompt writer.

### M2  (Part B: The gate and checking; bank id MA-found.25; 2 true)

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: A prompt rule is an instruction; code enforcement is outside the model.
- B: A gate that never rejects may not be checking anything.
- C: Stated confidence is more model output, not an independent check.
- D: A check that cannot fail gives no assurance.
- E: An external reference is independent of the model.

### M3  (Part C: Agents and verification; bank id MA-found.32; 3 true)

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A stop is not success; the goal may be unmet.
- B: Observations feed the next decision.
- C: Policy is the term for the decision-maker in the loop.
- D: The controller does not depend on the model complying.
- E: The controller is the surrounding program that executes actions and enforces limits.

### M4  (Part C: Agents and verification; bank id MA-found.33; 2 true)

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: A step limit bounds length, not what actions are allowed.
- B: An agent acts in a loop and observes the effects.
- C: The term depends on what the system does, not its label.
- D: This reverses the two terms.
- E: A workflow is predefined; an agent chooses its own steps.

### M5  (Part D: Retrieval, tools and MCP; bank id MA-found.36; 3 true)

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: The server is the provider side.
- B: The client is the consumer side.
- C: They are separate roles.
- D: MCP provides a shared message format, not authorization.
- E: Choosing servers is a human trust decision.

### M6  (Part E: Training and fine-tuning; bank id MA-ch09.6; 2 true)

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Prompt edits are inputs to the model.
- B: Weights are opaque; a prompt is readable text.
- C: Retrieved passages are visible text, so they can be inspected.
- D: Updating a retrieved document or prompt is faster and reversible.
- E: Retrieval fetches passages into context at request time.

### M7  (Part F: Seeing, stopping and owning an agent's work; bank id MA-ch04.5; 3 true)

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Without the arguments, identical values are indistinguishable.
- B: A trace shows actions and results, not the model's reasoning.
- C: The same value can legitimately be stored under different keys.
- D: Identical traces can come from different stops, so the returned status and the configured budget are part of the evidence.
- E: Intentions are inferred, not observed.

### M8  (Part F: Seeing, stopping and owning an agent's work; bank id MA-ch04.19; 4 true)

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: One turn can hold several calls.
- B: It counts the units that can change the world.
- C: A turn is one pass of the loop, however many calls it holds.
- D: Money is counted directly, unlike turns.
- E: The model asks for several tools at once.

## Summary

| Question | Part | Bank id | Topic | True statements |
|---|---|---|---|---|
| M1 | A | MA-found.3 | model, weights, training vs inference | 1 |
| M2 | B | MA-found.25 | acceptance gate | 2 |
| M3 | C | MA-found.32 | policy; controller; observation; step limit | 3 |
| M4 | C | MA-found.33 | agent vs workflow | 2 |
| M5 | D | MA-found.36 | MCP server vs client; interoperability vs authorization | 3 |
| M6 | E | MA-ch09.6 | prompt vs retrieval vs fine-tuning | 2 |
| M7 | F | MA-ch04.5 | trace | 3 |
| M8 | F | MA-ch04.19 | budget units | 4 |

True statements: 20 of 40. Questions with 1 / 2 / 3 / 4 true: 1 / 3 / 3 / 1 (the bank as a whole is about 10% / 35% / 36% / 20%).
