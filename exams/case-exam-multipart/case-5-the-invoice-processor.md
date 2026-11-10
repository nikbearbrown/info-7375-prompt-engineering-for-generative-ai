# Case 5: The invoice processor

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario

Kofi, a developer at a distributor, built an agent that reads 200 invoice PDFs, extracts the line items, and reports the total of all line items over $10,000. It can read PDFs, write files and send email through tools served by an MCP server named office.

### Setup and run record

```text
SYSTEM PROMPT  "Use exact arithmetic. Report the total of all line items over $10,000."
SETTINGS       temperature 0
RUN
  read_pdf x 200   -> line items extracted; all of them are now in the model's context
  final message    "Total of line items over $10,000: $1,284,500. All 200 invoices processed.
                    I emailed the spreadsheet to finance."
  send_email(to=finance, attachment=totals.xlsx) -> sent
                   (the run record contains no approval step)

LATER CHECK    a 12-line script filters and sums the extracted line items: $1,248,500
               (the model's total is $36,000 higher)
OPTION         the vendor offers to fine-tune the model on 50 correct totals
KOFI'S MESSAGE TO CLAUDE CODE
               "Write the totaling function and its tests first. Show me a failing test, then implement it."
```

### Statements

Check each statement that is true. Each statement is worth 1 point (10 points total).

- [ ] A. The model writes the total one token at a time as likely text; even at temperature 0, a fluent number is not a computed number.
- [ ] B. Having every line item in the model's context guarantees that the model sums them correctly.
- [ ] C. Telling the model "Use exact arithmetic" in the system prompt guarantees that its sum is exact.
- [ ] D. A fluent, confident final message is not evidence that the total is right; fluency says nothing about correctness.
- [ ] E. Filtering and summing line items belongs in ordinary code that the agent calls as a tool, where the result can be checked, and not in the model's reply.
- [ ] F. An email to finance cannot be unsent, so the host should require a person's approval before send_email runs; the MCP server listing the tool does not grant that permission.
- [ ] G. Fine-tuning the model on 50 correct totals would guarantee exact sums on new invoices.
- [ ] H. Fine-tuning changes the weights and suits style or format; for exact arithmetic, ordinary code is the better tool.
- [ ] I. The 12-line script's total is a stronger check on the sum than asking the model to recompute it, because the script does not share the model's way of failing.
- [ ] J. Because Kofi's request to Claude Code asks for tests first, the totals the agent produced no longer need to be checked.

---

## TA KEY PAGE (do not hand to students)

**Key:** A=T B=F C=F D=T E=T F=T G=F H=T I=T J=F

**Why:**

- A: A language model predicts the next token. It does not run a calculation unless a tool does it.
- B: Context changes what the model sees. It does not turn prediction into arithmetic.
- C: The instruction is a request. Exact work must be done by code you can check.
- D: The more fluently an output reads, the more confident you become in it and in your own evaluation. Form and content are independent.
- E: Choose the lowest capability that does the step: exact work goes to deterministic code.
- F: Irreversible, external actions get a human approval. Listing a tool is discovery, not authority.
- G: Fine-tuning shifts behavior on average; it does not guarantee exact arithmetic.
- H: Use the least powerful tool that does the step, because the most constrained tool is the easiest to check.
- I: A trustworthy check fails differently from the thing it checks.
- J: Tests of the function do not check the extracted line items or the totals the agent actually produced; those still need verification.

**Parts and concepts** (the six parts are the cheat sheet's Parts A to F)

| Statement | Part | Concept tested | Answer |
|---|---|---|---|
| A | A. How a language model works | next-token prediction; temperature | True |
| B | A. How a language model works | context vs computation | False |
| C | B. The gate and checking | system prompt is a request, not a gate | False |
| D | B. The gate and checking | fluency trap | True |
| E | C. Agents and verification | deterministic tools; verifiability first | True |
| F | D. Retrieval, tools and MCP | cost versus risk; capability is not authority | True |
| G | E. Training and fine-tuning | fine-tuning limits | False |
| H | E. Training and fine-tuning | fine-tuning vs deterministic code | True |
| I | F. Seeing, stopping and owning an agent's work | independence; verification | True |
| J | F. Seeing, stopping and owning an agent's work | verification vs request | False |
