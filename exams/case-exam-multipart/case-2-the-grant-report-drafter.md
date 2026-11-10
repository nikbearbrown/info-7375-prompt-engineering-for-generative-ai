# Case 2: The grant-report drafter

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario

Tomás is the program manager at a literacy nonprofit. He uses an assistant to draft a paragraph for a funder report. A fixed pipeline written by his team runs three steps in this order: (1) search last year's reports and take the top 5 passages; (2) ask the model to write a paragraph using only those passages; (3) format the result as JSON. The code, not the model, decides the order of the steps.

### Setup and run record

```text
SETTINGS     temperature 0.2, top-p 1.0
PROMPT       <sources> ...5 retrieved passages, each with an id... </sources>
             "Write one paragraph about enrollment using only the sources between the tags.
              Output JSON with the fields paragraph and citations (a list of source ids)."
             (two example paragraphs come before the sources)
RETRIEVAL    the pipeline calls the document store's search tool, served by an MCP server and described as
             "Searches approved final reports only." It returns the top 5 passages by vector similarity
             from 300-word chunks of 50 reports. Two of the five:
SOURCE R12-c3 (2023 final report):            "...412 students enrolled in the spring program..."
SOURCE R7-c1  (2022 DRAFT, never submitted):  "...about 500 students..."

RUN 1   {"paragraph": "In spring 2023, 512 students enrolled in the program.", "citations": ["R12-c3", "R7-c1"]}
RUN 2   (same input, nothing changed)
        {"paragraph": "In spring 2023, 412 students enrolled in the program.", "citations": ["R12-c3"]}
CLOSING NOTE from the assistant after run 1: "All numbers verified against sources."

TEAM'S CHECKS  The JSON is valid and every cited id exists in the store. Both runs pass.
               A judge model from the same family as the drafting model scored 30 drafts: average 4.6 out of 5.
PLAN           To match the funder's tone, the team will fine-tune the drafting model on the 30 best
               past paragraphs and then test it on those same 30 paragraphs.
```

### Statements

Check each statement that is true. Each statement is worth 1 point (10 points total).

- [ ] A. Run 1 and run 2 differ because the model draws each token at random from a probability distribution; a temperature of 0 would make the two runs more likely to agree, but the answer they agree on could still be wrong.
- [ ] B. Writing "Output JSON with the fields paragraph and citations" in the prompt guarantees that the reply is valid JSON.
- [ ] C. A judge model from the same family as the drafting model gives independent evidence that the drafts are accurate.
- [ ] D. Because a model writes the paragraph, this assistant is an agent.
- [ ] E. The closing note "All numbers verified against sources" is a claim, not evidence, and run 1 contradicts it.
- [ ] F. Because the cited id R12-c3 exists in the store, run 1's claim of 512 students is supported by it.
- [ ] G. The search tool's description ("approved final reports only") is the server's own claim, and the draft R7 appearing in the results shows it should not be taken as proof.
- [ ] H. Testing the fine-tuned model on the same 30 paragraphs it was trained on is a fair test of how well it will do on new paragraphs.
- [ ] I. Fine-tuning changes the weights, so it suits matching a tone or style, but it is a poor way to teach the model this year's enrollment figures, which belong in the context.
- [ ] J. The paragraph's support includes R7, a draft that was never submitted; a record of where each number came from and who checked it would have exposed that.

---

## TA KEY PAGE (do not hand to students)

**Key:** A=T B=F C=F D=F E=T F=F G=T H=F I=T J=T

**Why:**

- A: Sampling draws tokens by probability, so identical input can give different output. Lower temperature raises repeatability, not correctness.
- B: A prompt instruction is a request. Valid output has to be checked by code (or forced by schema-constrained decoding), not assumed.
- C: A same-family judge can share the drafter's blind spots and favor its own style. It also was not asked whether claims match sources. It is weak evidence.
- D: A fixed pipeline where the code chooses the steps is a workflow. In an agent, the model directs the next step.
- E: Run 1 says 512; the cited passage says 412. The assistant's own claim of verification is not evidence you can check independently.
- F: A citation can point to a real source and still not support the claim. Valid citation is not support.
- G: A tool description is text the server wrote about itself. What comes back must be checked.
- H: Test data must be held out and untouched by training. Testing on the training set overstates performance.
- I: Behavior goes in the weights, changing knowledge goes in the context. Fine-tuned knowledge is hard to trace and update.
- J: Provenance is where something came from and who checked it. Without it, errors hide.

**Parts and concepts** (the six parts are the cheat sheet's Parts A to F)

| Statement | Part | Concept tested | Answer |
|---|---|---|---|
| A | A. How a language model works | sampling; temperature; repeatability vs correctness | True |
| B | B. The gate and checking | output contract; validator; request vs gate | False |
| C | B. The gate and checking | LLM-as-judge; self-preference; independence | False |
| D | C. Agents and verification | workflow vs agent | False |
| E | C. Agents and verification | claim vs evidence; self-report | True |
| F | D. Retrieval, tools and MCP | citation vs support | False |
| G | D. Retrieval, tools and MCP | tool description is a claim; MCP is not trust | True |
| H | E. Training and fine-tuning | held-out data; leakage | False |
| I | E. Training and fine-tuning | fine-tuning vs retrieval | True |
| J | F. Seeing, stopping and owning an agent's work | provenance | True |
