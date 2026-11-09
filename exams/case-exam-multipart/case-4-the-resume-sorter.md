# Case 4: The résumé sorter

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario

Aisha is a recruiter at a mid-size firm. A tool ranks the 300 applications for each opening and writes a short reason for each of its top 20; recruiters read only the top 20. A script calls the model once per résumé and then sorts the results; the model chooses no steps.

### Setup and run record

```text
MODEL         a base model that the vendor fine-tuned on five years of the firm's past hiring decisions
SETTINGS      temperature 0; max_tokens 60 for each reason (a hard limit)
OUTPUT        {"rank": integer from 1 to 300, "reason": text}   (a script checks these two fields)
DATA ACCESS   the tool reads applicants through an MCP server that exposes get_applicant(id),
              which returns the résumé and also fields for age, gender and home address
SAMPLE REASON "Strong culture fit."

EVALUATION    on a held-out set of past applications: agreement with past hiring decisions 90%
              across 40 past openings, share of applicants placed in the top 20:
              group A 10%, group B 4.5%
SIGN-OFF NOTE "Tested on held-out past applications. Approved."
```

### Statements

Check each statement that is true. Each statement is worth 1 point (10 points total).

- [ ] A. At temperature 0 the reason written for a résumé is more repeatable, so it must also be accurate.
- [ ] B. If the model's reason would be longer than 60 tokens, it is cut off at the max_tokens limit, possibly in the middle of a sentence.
- [ ] C. Checking that rank is an integer from 1 to 300 and that the reason is at most 60 tokens shows that the reason is accurate.
- [ ] D. A script that calls the model once per résumé and then sorts the results is a workflow, not an agent, because the code chooses the steps.
- [ ] E. Because get_applicant returns age, gender and home address, the tool can read them; MCP only supplies the channel, so keeping those fields out of what the model sees is a decision for the host and the team.
- [ ] F. Adding the job description to the prompt by retrieval would remove any bias carried in the model's weights.
- [ ] G. Because the model was fine-tuned on past hiring decisions, patterns in those decisions, including any bias, can be carried into its weights.
- [ ] H. Because the 90% agreement figure comes from a held-out set, it shows that the ranking is fair.
- [ ] I. The gap between 10% and 4.5% in top-20 placement is a signal to investigate that an overall agreement figure can hide.
- [ ] J. The sign-off note "Tested on held-out past applications. Approved." states what was not checked and what is not claimed.

---

## TA KEY PAGE (do not hand to students)

**Key:** A=F B=T C=F D=T E=T F=F G=T H=F I=T J=F

**Why:**

- A: Repeatable is not the same as accurate. Greedy output can be consistently wrong.
- B: A token limit stops generation when it is reached, whatever the sentence is doing.
- C: That checks structure. A reason can have the right shape and be false or unfair.
- D: In an agent the model directs the next step; here the script fixes them.
- E: A protocol connects a host and a server; it does not decide what enters the model's context. Give the model only what the task needs.
- F: Retrieval changes what the model sees, not the weights. Bias learned in fine-tuning stays in the weights.
- G: Training moves the parameters toward the data it is shown. Fine-tuning on biased decisions can bake the bias in.
- H: A held-out set supports a claim about performance on unseen cases similar to training. Agreement with past decisions measures agreement with those decisions, not fairness.
- I: Aggregate performance can conceal a difference between groups, so the rates have to be examined by group.
- J: A sign-off says what was checked, how, what was not checked, what is not claimed, and whether it is signed or withheld. This note says nothing about what was not checked or what is not claimed.

**Parts and concepts** (the six parts are the cheat sheet's Parts A to F)

| Statement | Part | Concept tested | Answer |
|---|---|---|---|
| A | A. How a language model works | repeatability vs correctness | False |
| B | A. How a language model works | max tokens; truncation | True |
| C | B. The gate and checking | format validity vs factual validity | False |
| D | C. Agents and verification | workflow vs agent | True |
| E | D. Retrieval, tools and MCP | need to know; host decides context; MCP is not policy | True |
| F | D. Retrieval, tools and MCP | retrieval vs weights | False |
| G | E. Training and fine-tuning | fine-tuning; flawed examples baked in | True |
| H | E. Training and fine-tuning | held-out data; proxy metric | False |
| I | F. Seeing, stopping and owning an agent's work | aggregate rate vs per-group rates | True |
| J | F. Seeing, stopping and owning an agent's work | sign-off | False |
