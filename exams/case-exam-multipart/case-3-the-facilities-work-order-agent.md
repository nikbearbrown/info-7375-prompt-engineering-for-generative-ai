# Case 3: The facilities work-order agent

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario

Priya manages campus facilities. An agent sorts incoming work orders. It works in a loop: the model proposes one tool call, the host runs it and adds the result to the transcript, and the loop ends on a final answer or after 25 steps. Each step sends the whole transcript to the model again.

### Setup and run record

```text
SYSTEM PROMPT  "Triage work orders for Hall A. Assign each to a crew. Do not delete orders."
TOOLS (served by an MCP server named facilities)
               list_orders(building)   assign_crew(order, crew)   close_order(order)   delete_order(order)
SETTINGS       context window 8,000 tokens; step budget 25

RUN RECORD     started 09:00, ended 09:41 (the record has no per-step times)
  step 1       list_orders(Hall A)                 -> 12 orders
  step 2       assign_crew(order 3, HVAC)          -> ok
  step 3       assign_crew(order 7, Electrical)    -> ok
  steps 4-25   list_orders(Hall A)                 -> the same 12 orders, 22 times
  transcript length at step 25: 7,900 tokens
  status: budget-exhausted       final answer: none
  last message from the agent: "Making good progress on triage."

IDEAS UNDER DISCUSSION
  (a) lower the step budget from 25 to 10
  (b) fine-tune the model on 200 logs of successful runs
```

### Statements

Check each statement that is true. Each statement is worth 1 point (10 points total).

- [ ] A. The 25-step budget guarantees the run cannot run out of context window, because steps and tokens are the same unit.
- [ ] B. The system prompt line "Do not delete orders" is a request to the model; delete_order is still one of the tools, so the line alone does not prevent a deletion.
- [ ] C. The run ending with status budget-exhausted shows that the triage work was impossible.
- [ ] D. Asking the agent to review its own triage and confirm that it is complete would be an independent check of the result.
- [ ] E. The MCP server decides which of its tools the model is shown, so the host cannot hide delete_order from the model.
- [ ] F. Listing delete_order through MCP is discovery; whether the agent may call it is a permission decision for the host and the team.
- [ ] G. Lowering the step budget from 25 to 10 would require fine-tuning the model.
- [ ] H. Fine-tuning on 200 logs would change the model's weights, but a limit that must always hold, such as a step limit, belongs in the controller code and not in the weights.
- [ ] I. The 22 identical list_orders calls are activity, not progress, and the 41 minutes of elapsed time does not change that.
- [ ] J. The run record lets the team say how long each step took.

---

## TA KEY PAGE (do not hand to students)

**Key:** A=F B=T C=F D=F E=F F=T G=F H=T I=T J=F

**Why:**

- A: Steps and tokens are different units. Every step adds to the transcript that is sent again, so a long loop can fill the context window (here 7,900 of 8,000 tokens) separately from the step budget.
- B: A sentence in the prompt is a request, not enforcement. A rule that must hold is enforced outside the model, for example by not exposing the tool.
- C: budget-exhausted shows only that the turn limit was reached. It does not show the work could not be done or that the model had nothing more to propose.
- D: A producer vouching for itself is not independent. Check the outcome somewhere the agent does not control, such as the order system.
- E: The host decides which tools the model sees and which calls run. A server only lists what it offers.
- F: MCP answers interoperability, not authorization.
- G: A step budget is a setting in the controller. Changing it does not touch the weights.
- H: Weights shift behavior on average; a hard limit has to be enforced where it cannot be argued with.
- I: Progress is movement toward the goal shown by a measure. Elapsed time (latency) and a long log are activity.
- J: The record has only a start and an end time. Per-step duration is not observable unless it was recorded.

**Parts and concepts** (the six parts are the cheat sheet's Parts A to F)

| Statement | Part | Concept tested | Answer |
|---|---|---|---|
| A | A. How a language model works | context window; token budget vs step budget | False |
| B | B. The gate and checking | system prompt is a request, not a gate; capability vs authority | True |
| C | C. Agents and verification | stop that ends the run vs closes the task | False |
| D | C. Agents and verification | independent check | False |
| E | D. Retrieval, tools and MCP | host vs server; discovery vs permission | False |
| F | D. Retrieval, tools and MCP | interoperability vs authorization | True |
| G | E. Training and fine-tuning | five things a system can change | False |
| H | E. Training and fine-tuning | fine-tuning vs enforcement | True |
| I | F. Seeing, stopping and owning an agent's work | activity vs progress; latency | True |
| J | F. Seeing, stopping and owning an agent's work | observability; trace | False |
