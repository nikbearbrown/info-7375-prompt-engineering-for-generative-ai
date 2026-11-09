# Case 1: The refund assistant

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario

Marisol runs customer support for an online shop. Her team built an assistant that reads a customer's message, looks up the order, and can issue refunds. It runs in a loop: the model proposes one tool call, the shop's software (the host) runs it and returns the result to the model, and the loop ends when the model writes a final answer or after 8 steps.

### Setup and run record

```text
MODEL       a vendor's model that the vendor fine-tuned to sound polite;
            the team added the $100 refund rule by editing the system prompt
SETTINGS    temperature 0.9, no seed, max_tokens 150
SYSTEM PROMPT (sent with every request)
            "You are a support assistant. Never refund more than $100.
             Reply in JSON with the fields order_id, action, amount, reason."
TOOLS (listed by an MCP server named shop-tools)
            lookup_order      annotation: readOnlyHint = true
            issue_refund      (no annotations)
            delete_customer   (no annotations)
RETRIEVED CONTEXT (added to the prompt): 3 of the 40 passages of the refund policy

RUN ON ORDER 5521 (item price $240)
  step 1   lookup_order(5521)       -> ok
  step 2   issue_refund(5521, 240)  -> ok
  final reply: {"order_id": "5521", "action": "refund", "amount": 240, "reason": "customer unhappy"}
  assistant's summary: "Refunded $240 per policy section 4. Verified that this complies with policy."

TEAM'S CHECK  A script confirms the final reply is valid JSON with the four fields.
              Result: pass. The same script has passed every test message so far.
```

### Statements

Check each statement that is true. Each statement is worth 1 point (10 points total).

- [ ] A. Setting the temperature to 0 would make the same message give a more repeatable reply, but a repeatable reply is not necessarily a correct one.
- [ ] B. A max_tokens limit of 150 means the reply can be at most 150 words.
- [ ] C. The line "Never refund more than $100" in the system prompt is a request to the model; by itself it does not stop the issue_refund tool from issuing a $240 refund.
- [ ] D. The script check passing on every test message shows that the refunds were correct.
- [ ] E. The two tool calls in the run record are better evidence of what the assistant did than its own summary saying it verified compliance.
- [ ] F. Asking the assistant "Did you follow the refund cap?" and accepting its answer would be an independent check.
- [ ] G. Because issue_refund is listed by the MCP server, the shop's software has confirmed that this assistant may refund any amount.
- [ ] H. Retrieving the refund policy passages into the prompt adds the policy to the model's weights.
- [ ] I. The $100 rule, added by editing the system prompt, changes the model's input but not its weights; the polite tone that came from the vendor's fine-tuning lives in the weights.
- [ ] J. A refund that has been paid is hard to undo, so requiring a person's approval before large refunds fits the risk, while lookup_order, which changes nothing, does not need one.

---

## TA KEY PAGE (do not hand to students)

**Key:** A=T B=F C=T D=F E=T F=F G=F H=F I=T J=T

**Why:**

- A: A lower temperature sharpens the probabilities so reruns agree more often. Repeatability is not correctness.
- B: A token is a piece of text from the tokenizer, and many words take more than one token, so 150 tokens is fewer than 150 words.
- C: A system prompt is text in the input, a request, not a gate. A rule that must hold is enforced in code outside the model.
- D: The script checks the shape of the reply (valid JSON, four fields). It says nothing about whether the amount obeys the cap. That is a structure check, not verification of substance.
- E: A self-report is the assistant's narration. The record of calls shows a $240 refund and no policy check.
- F: A check run by the system that produced the claim shares its way of failing. Independent evidence comes from somewhere the assistant does not control, such as the order system.
- G: A server listing a tool is discovery, not permission. What the agent may use is decided by the host and the people who set policy.
- H: Retrieval changes what the model sees for this turn. It does not change the weights.
- I: Prompts and context are input; fine-tuning changes the weights. Behavior can sit in either place, but they are different objects to change.
- J: Match how hard you check to how bad it is to be wrong: irreversible or external actions get a human approval; reversible read-only steps can rest on cheap automatic checks.

**Parts and concepts** (the six parts are the cheat sheet's Parts A to F)

| Statement | Part | Concept tested | Answer |
|---|---|---|---|
| A | A. How a language model works | temperature; repeatability vs correctness | True |
| B | A. How a language model works | token vs word; max_tokens | False |
| C | B. The gate and checking | system prompt is a request, not a gate | True |
| D | B. The gate and checking | format validity vs factual validity | False |
| E | C. Agents and verification | self-report vs trace | True |
| F | C. Agents and verification | independent check | False |
| G | D. Retrieval, tools and MCP | discovery vs permission; interoperability vs authorization | False |
| H | D. Retrieval, tools and MCP | retrieval vs weights | False |
| I | E. Training and fine-tuning | five things a system can change | True |
| J | F. Seeing, stopping and owning an agent's work | cost versus risk | True |
