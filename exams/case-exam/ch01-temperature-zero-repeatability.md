# Case 01: The stable labels

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Marcus is a compliance lead at a small insurer. Adjusters write short claim notes, and he wants Claude to label each note as water damage, fire or theft so claims route to the right team. Auditors will ask him whether the labels can be trusted, and he wants to say they need no manual checking. You run the job with the Claude API from a Python script.

### The instruction (what you sent)
> Make the classifier deterministic: set temperature to 0 and label all 500 claim notes in `notes.csv`. Run it twice and report whether the labels are reliable.

### Agent output
```
RUN REPORT
- Called the Claude API 1000 times (500 notes x 2 runs), temperature=0,
  max_tokens=10, same prompt template both runs.
- Run 1 vs run 2: 500 of 500 labels identical. Agreement = 100%.
- Label counts: water damage 231, fire 140, theft 129.
- Example: "Hail dented the roof, then the basement flooded overnight"
  -> water damage (both runs).
- Example: "Neighbour saw a man leave with the TV; kitchen smelled of smoke"
  -> theft (both runs).

CONCLUSION
Labels are fully consistent, so they are reliable and correct. No manual
spot check is needed; the 20-note human review in the plan can be skipped.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the distinction it ignores?
2. **(2 pts)** What single check would turn "reliable and correct" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Marcus what he can and cannot tell the auditors.

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
**The flaw:** two runs agreeing (repeatability) does not mean the labels are right (correctness); a model at temperature 0 can give the same wrong label every time.

**Full-credit terms (2):** repeatability vs correctness (either word of the pair with the contrast stated); greedy decoding as the reason runs agree *and* the contrast with correctness.
**Half-credit (1):** "consistent is not accurate"; "reliability"; "deterministic is not correct"; "needs ground truth".
**Zero:** "hallucination", "sampling noise", "top-p", "seed", "confidence interval / more runs / sample size" alone (two runs are not the issue; the issue is that agreement is not accuracy).
**Note:** "reliability vs validity" or "consistency vs accuracy" state the contrast in other words: Catch 3, Term 1 (not the course pair).

**Acceptable evidence requests (any two count):**
- Compare the labels with labels from human adjusters on a sample (e.g. 50 notes), and report the agreement rate.
- Hand-check the mixed-signal notes (hail + flood, theft + smoke) and report how many were wrong.
- Have two humans label a sample, then score Claude against them.

**Unacceptable:** "run it a third time"; "use a different seed"; "ask Claude to rate its confidence" (verbalized confidence is text, not a measurement).

**Traps:**
- Many students write "temperature 0 is not fully deterministic". That may be true but is not the planted flaw. It earns at most Catch 1 unless they also say agreement is not accuracy.
- The second example (smoke + theft) is a plausible mislabel; credit students who use it, not required.

**CAP RULE:** flaw missed (no statement that same answers each time is not the same as right answers) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. 500/500 agreement shows repeatability only. At temperature 0 the model picks the highest-probability token (greedy decoding), so it repeats itself, including its mistakes. Repeatability is not correctness; the smoke-and-theft note is probably mislabelled in both runs. 2. Have adjusters label 50 notes by hand and compute agreement with Claude's labels. 3. "Do not skip the human review. Report accuracy against 50 human labels, listing every disagreement." 4. "We can say the labels are stable, not that they are right. We will check a sample against adjusters before we tell the auditors."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 lacks a clear statement of what he *can* say (one sentence does, "stable") so the point is withheld as it is only partly answered.

**Typical (6/10).**
> 1. Both runs match but that does not mean the labels are correct. 2. Check some of the notes by hand. 3. Tell the agent to do the human review anyway. 4. The labels are the same every time but we do not know if they are right.

Score: C3 T1 E1 F1 P0 = **6**. Reason: correct contrast in plain words (C3), no exact term (T1), "some by hand" is vague about comparing to a standard (E1), "do the review" restates the plan without asking for a number (F1); Q4 correct but equals Q1 and has no auditor guidance (0).

**Fluent-but-wrong (3/10).**
> 1. Temperature 0 does not guarantee determinism because of floating-point nondeterminism in batched inference, so the 100% agreement may be an artifact; use a fixed seed and top-p of 1. 2. Run 10 more repeats and measure variance. 3. "Set seed=42, top_p=1, and rerun 5 times." 4. The model's output may vary slightly between runs.

Score: C0 T1 E0 F1 P1 = **3**. Reason: argues about determinism, never separates agreeing from being right (flaw missed); "variance"/"seed" is a near-miss term; more repeats measure repeatability again; the correction is a valid but irrelevant fix; Q4 is plain and short.
