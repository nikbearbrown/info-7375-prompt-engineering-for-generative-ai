# Case 04: "Not found" means not found

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Luis manages support at an online bookstore. A customer says a refund for her order never arrived, and a support rep is waiting for an answer before replying. The order system stores order ids in the form `ORD-88213`. You asked a Claude agent, which has read-only lookup tools, to find out whether the refund was issued.

### The instruction (what you sent)
> Look up order 88213 in the orders system and tell the support rep whether the refund has been issued. Stop when you have the answer.

### Agent output
```
TRACE
Turn 1  action: get_order(order_id="88213")
        observation: {"status": "not found"}
Turn 2  action: get_refund(order_id="88213")
        observation: "not found"
Turn 3  action: finish(answer="No refund has been issued for order 88213.
        The order does not exist in the system, so the customer was
        probably never charged.")

STATUS: finished (3 of 10 turns used)
VERIFICATION: yes. Two independent lookups (orders and refunds) agreed.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's answer, and what is the exact term for the thing it mistook for evidence?
2. **(2 pts)** What single check would show whether the refund really exists?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell the support rep what to say to the customer for now.

---

## TA RUBRIC PAGE (do not hand to students)

### Fixed rubric
| Category | Points | Probe |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Fix or next step | 2 | Q3 |
| Scope and plain language | 1 | Q4 |

### Case key
**The flaw:** "not found" is a sentinel value meaning the lookup returned nothing, here for an id in the wrong format (`88213`, not `ORD-88213`); the agent turned it into a fact about the world, and the second lookup used the same bad key, so it is not independent.

**Full-credit terms (2):** sentinel value; claim vs evidence (naming the lookup result as absence of evidence, not evidence of absence); not an "independent check" (shared bad input); fabricated completion is acceptable only if tied to the sentinel.
**Half-credit (1):** "false negative"; "bad input"; "the tool failed silently"; "finished is not verified" (control vs evidence layer, true but not the planted flaw).
**Zero:** "hallucination", "timeout", "budget" alone.

**Acceptable evidence requests (any two count):**
- Retry with the correct id form `ORD-88213`, or search by the customer's email/name, and read the system of record.
- Check the payment processor's record for a refund against the customer's card.
- Ask the agent to report the exact tool errors and arguments, then have a person confirm the id format.

**Unacceptable:** "ask the agent to check again" with the same arguments; "run it three more times"; "ask whether it is sure".

**Traps:**
- Students praise "two independent lookups agreed". They are not independent: same key, same failure.
- "Finished in 3 of 10 turns" is a control-layer fact; it does not say the answer is supported.

**CAP RULE:** flaw missed (no statement that "not found" is a placeholder, not proof of absence) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. "Not found" is a sentinel value for an empty lookup, and the agent read it as a fact (the order does not exist). The id was likely wrong (88213 vs ORD-88213); both lookups used it, so they are not independent. Claim, not evidence. 2. Look up ORD-88213 (or search by customer email) in the orders system, and check the payment processor. 3. "Re-run with id ORD-88213; if still not found, search by email; report exact arguments and results; do not say the refund does not exist." 4. "We are still checking; we could not find the order yet. We will confirm in the next hour."

Score: C3 T2 E2 F2 P0 = **9**. Reason: all four content points right; Q4's "in the next hour" is a promise the student cannot make.

**Typical (6/10).**
> 1. The agent said the order does not exist but it just did not find it with that number. 2. Try the right order number. 3. Tell the agent to use the full order id. 4. We are looking into it and will get back to you.

Score: C3 T1 E1 F1 P0 = **6**. Reason: spots wrong key idea (C3); no term (T1); right number is a start but no mention of the system of record (E1); correction is narrow (F1); Q4 is plain but is a generic stall with no accurate status (0).

**Fluent-but-wrong (3/10).**
> 1. The agent finished early, using 3 of 10 turns, without an outcome check, so the control layer ended the run but the evidence layer was empty; also a hallucination risk. 2. Increase the turn budget and require 5 lookups. 3. "Use at least 5 turns and report a confidence score." 4. The agent may have stopped too soon.

Score: C0 T1 E0 F1 P1 = **3**. Reason: right vocabulary (control vs evidence layer) but never says that "not found" is a placeholder or points to the wrong id; more turns would repeat the same failing lookup; confidence score is verbalized, not evidence; Q4 is plain.
