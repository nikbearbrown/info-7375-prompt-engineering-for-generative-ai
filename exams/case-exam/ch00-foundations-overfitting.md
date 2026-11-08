# Case 00 (Foundations): The perfect router

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Priya runs the help desk at a university. Staff spend hours sorting incoming student emails into three queues (billing, housing, registrar), and she wants a Python classifier to do it. She has 300 emails that staff have already sorted by hand. She asked Claude Code to build the classifier and to tell her whether it is ready to go live on Monday.

### The instruction (what you sent to Claude Code)
> Build a Python classifier that routes student emails to billing, housing or registrar using the 300 labelled emails in `data/labelled.csv`. Report how accurate it is and whether it is ready to deploy.

### Agent output
```
RESULT SUMMARY
1. Loaded data/labelled.csv: 300 emails (billing 100, housing 100, registrar 100).
2. Turned each email into word counts; trained a logistic regression
   with C=1000 (almost no regularization) on all 300 rows.
3. Measured accuracy on the 300 emails: 300 of 300 correct = 100.0%.
4. Looked at the largest weights: "tuition", "refund" -> billing;
   "dorm", "roommate" -> housing; "transcript", "enrol" -> registrar.
   These are sensible.
5. Saved model.pkl and router.py (router.route(text) returns a queue).

CONCLUSION
The classifier reaches 100% accuracy and generalizes well across all
three queues. It is ready for deployment today.

NOTE
All 300 rows were used for fitting, since the dataset is small and
every email is valuable.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the problem?
2. **(2 pts)** Name one check or instruction you could give that would turn "ready to deploy" from a claim into evidence.
3. **(2 pts)** Write the correction you would send to Claude Code.
4. **(1 pt)** In two sentences, with no jargon, explain to Priya why she should not go live on Monday yet.

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
**The flaw, one sentence:** accuracy was measured on the same 300 emails the model was fitted on, so 100% shows the model fits its training examples (possible overfitting), not that it generalizes to new emails.

**Full-credit terms (2):** overfitting; generalization (named as the missing evidence); held-out / test set (or "data the model never saw").
**Half-credit near-misses (1):** "memorized the data"; "tested on the same data"; "training accuracy"; "too good to be true" without the mechanism; "data leakage" (acceptable only if they name training data in the evaluation).
**Zero:** "bias", "hallucination", "temperature", "needs more data" as the whole answer.

**Acceptable evidence requests (any two count):**
- Split off a portion (e.g. 60 emails) before fitting, never train on it, and report accuracy on it.
- Cross-validation, or running on a fresh batch of emails staff have sorted but the model never saw.
- Per-queue results on unseen emails.

**Unacceptable:** "run it again on the 300 emails"; "ask Claude if it is sure"; "add regularization" alone (this changes the model, not what is measured); "make the dataset bigger" alone.

**Traps:**
- Fluent students write about "bias and variance" or "too small a dataset" and never say the score was computed on training data. That is a miss.
- "Perfect score is suspicious" is a hunch, not the flaw; give 1 of 3 only if no mechanism is named.
- The agent's NOTE gives the mechanism away; a student who quotes it and explains why it matters catches the flaw.

**CAP RULE:** flaw missed (no mention that evaluation used the training data) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The 100% was computed on the same 300 emails the model was trained on, so it only shows the model fits those examples. That is overfitting risk (C=1000, nothing held out); it says nothing about generalization to new emails. 2. Hold out 60 emails before fitting, never train on them, report accuracy on those. 3. "Redo with a 240/60 split; fit on 240 only; report held-out accuracy per queue; do not say ready until that number is in." 4. "The test was an exam with questions it had already seen, so we don't know how it handles new emails. We will test it on fresh ones first and tell you Monday if it is good."

Score: C3 T2 E2 F2 P0 = **9**. Reason: everything correct; Q4 is plain but promises "Monday" results the student cannot guarantee (overclaims), so the last point is withheld.

**Typical (6/10).**
> 1. It tested on the same data it trained on so the accuracy is too high. 2. Test on different emails. 3. Tell Claude to get more data and retrain. 4. The model might not work as well on new emails so wait.

Score: C3 T1 E1 F1 P0 = **6**. Reason: sees the flaw in plain words (3) but no exact term (1); "different emails" is vague but right direction (1); "more data" is not the fix (1); Q4 is vague, no reason given (0).

**Fluent-but-wrong (3/10).**
> 1. A perfect score signals overfitting caused by a tiny dataset and class bias; the model's confidence is miscalibrated. 2. Request a per-queue breakdown and confusion matrix. 3. Instruct Claude to add L2 regularization and a larger vocabulary and re-run. 4. The system may be biased so deployment should be reviewed.

Score: C0 T1 E0 F1 P1 = **3**. Reason: uses the word "overfitting" but never says the score was measured on training data (flaw missed, term only half); per-queue breakdown on the same 300 is not evidence; regularization is a partial fix; Q4 is plain and short.
