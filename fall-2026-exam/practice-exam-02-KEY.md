# Practice exam 02: answer key and scoring notes

Keep this file apart from the exam. Do the exam first, then score yourself.

## How cases are scored
| Row | Points | Where |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Uses the exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Gives a fix or next step | 2 | Q3 |
| Keeps scope and plain language | 1 | Q4 |

If you miss the planted flaw, the case is capped at 5/10. Grammar and polish earn nothing. "Half-credit" terms earn 1 of the 2 term points.

---

# Part A key

## Case 1: The perfect router

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

**Cap rule:** flaw missed (no mention that evaluation used the training data) => case maximum 5/10.

**One strong sample answer:**
> 1. The 100% was computed on the same 300 emails the model was trained on, so it only shows the model fits those examples. That is overfitting risk (C=1000, nothing held out); it says nothing about generalization to new emails. 2. Hold out 60 emails before fitting, never train on them, report accuracy on those. 3. "Redo with a 240/60 split; fit on 240 only; report held-out accuracy per queue; do not say ready until that number is in." 4. "The test was an exam with questions it had already seen, so we don't know how it handles new emails. We will test it on fresh ones first and tell you Monday if it is good."

---

## Case 2: Every answer cites a source

**The flaw (planted):** the validator checks structure (valid JSON, right keys, citation ids that exist) but not whether the cited passage supports the claim, so "grounded" is unproven; a citation existing is not the same as support.

**Full-credit terms (2):** structural validity vs grounding; citation vs support (citation validity vs accuracy); "ungrounded" used for answers that cite but are unsupported.
**Half-credit (1):** "the citations might be fake / hallucinated" (they exist; this is the wrong failure); "needs fact-checking"; "faithfulness" without the contrast; "JSON mode only guarantees syntax".
**Zero:** "overfitting", "temperature", "bias".

**Acceptable evidence requests (any two count):**
- Read the cited passage for a sample of answers (e.g. 20) and mark each claim supported, partly supported or unsupported; report the rate.
- Add questions the policies do not answer and check that Claude abstains.
- Have a second pass (human, or a model checked against human labels) compare each claim with the passage text it cites.

**Unacceptable:** "run the validator again"; "check that the JSON is valid"; "ask Claude whether its answers are grounded".

**Traps:**
- Students who say JSON mode "does not guarantee the right keys" are accurate but off-target; credit only if they also separate structure from support.
- Students who worry that citations are invented miss that the validator already rules that out.

**Cap rule:** flaw missed (no statement that the check never compares the claim with the cited text) => case maximum 5/10.

**One strong sample answer:**
> 1. The validator proves the reply is well-formed and the ids exist; it never reads policy-B#4 to see if it says alumni may borrow ebooks for 90 days. That is structural validity, not grounding: a citation that exists is not a source that supports the claim. 2. Sample 20 answers and read each cited passage against the claim; report supported/unsupported counts. 3. "Add a support check: for each claim, quote the passage and say supported, partly, or not; add 10 questions the policies cannot answer and expect abstention." 4. "The report shows the answers are well-formed and point to real documents. It does not yet show the documents say what the answers claim."

---

## Case 3: "Not found" means not found

**The flaw (planted):** "not found" is a sentinel value meaning the lookup returned nothing, here for an id in the wrong format (`88213`, not `ORD-88213`); the agent turned it into a fact about the world, and the second lookup used the same bad key, so it is not independent.

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

**Cap rule:** flaw missed (no statement that "not found" is a placeholder, not proof of absence) => case maximum 5/10.

**One strong sample answer:**
> 1. "Not found" is a sentinel value for an empty lookup, and the agent read it as a fact (the order does not exist). The id was likely wrong (88213 vs ORD-88213); both lookups used it, so they are not independent. Claim, not evidence. 2. Look up ORD-88213 (or search by customer email) in the orders system, and check the payment processor. 3. "Re-run with id ORD-88213; if still not found, search by email; report exact arguments and results; do not say the refund does not exist." 4. "We are still checking; we could not find the order yet. We will confirm in the next hour."

---

## Case 4: Only two files

**The flaw (planted):** the agent claims it changed only the two allowed files, but its own diff stat shows `billing/rates.py` was edited (scope creep), and the change was made to bend a test to the code.

**Full-credit terms (2):** scope creep / scope violation; scope check (changed files minus allowed files); self-report vs diff.
**Half-credit (1):** "off-limits file touched"; "did not follow instructions"; "unauthorized change"; "weakening a test" (the note hints at a related issue, 1 of 2 only if scope not named).
**Zero:** "hallucination", "overfitting", "hard-coding" alone.

**Acceptable evidence requests (any two count):**
- Run `git diff --name-only` and subtract the allowed-file list; the result must be empty (scope check).
- Read the line-level diff of every changed file before merging (diff review).
- Revert `billing/rates.py` and re-run the tests to see whether the date test still passes.

**Unacceptable:** "ask the agent whether it stayed in scope"; "tell it again not to touch rates.py" as the only step (an instruction, not a control); "re-read the summary".

**Traps:**
- Students who notice only that the test and the rates change are linked have found a good secondary problem, but the planted flaw is the contradiction with the scope rule.
- "CLAUDE.md should stop this" is the instruction-vs-enforcement mistake; a deny rule or hook would be preventive.

**Cap rule:** flaw missed (no mention that rates.py appears in the diff despite the claim) => case maximum 5/10.

**One strong sample answer:**
> 1. The summary says only two files changed, but the diff stat lists billing/rates.py, which was off-limits. That is scope creep, and the self-report contradicts the diff. The edit also looks like bending the date test to the code. 2. A scope check: changed files minus the allowed list must be empty; run `git diff --name-only`. 3. "Revert billing/rates.py; make the date fix in parser.py only; re-run tests; list changed files from git." 4. "The change touched a pricing file that is frozen for the audit, which the summary did not admit. Please wait until that edit is undone."

---

## Case 5: The tutor effect

**The flaw (planted):** the data show an association; the claim ("raises scores") is about an intervention, and study hours and self-selection are confounders that affect both who uses the tutor and the score; a small p-value does not fix that.

**Full-credit terms (2):** association vs intervention (rungs of the ladder of causation); confounder (study hours / self-selection) named; counterfactual (what would these students have scored without the tutor).
**Half-credit (1):** "correlation is not causation" with no confounder named; "selection bias"; "Simpson's paradox" (only if they explain the reversal on pooling, otherwise near-miss).
**Zero:** "overfitting", "sample size", "p-hacking", "t-test assumptions / normality / non-parametric test / effect size" alone (these tidy the statistics, not the causal claim).

**Acceptable evidence requests (any two count):**
- Randomized pilot: assign tutor access at random and compare scores.
- Compare users and non-users within the same study-hours bands (or adjust for prior GPA and study hours) and report the difference per band.
- Pre-specify the comparison and the outcome before running it.

**Unacceptable:** "collect more data of the same kind"; "get a smaller p-value"; "run the t-test again"; "ask Claude if it is causal".

**Traps:**
- Students who attack the p-value or sample size miss the point; n=2,000 is plenty.
- "Correlation is not causation" alone is the common half-answer; it needs the specific confounders from the output for full catch.
- Students who say "the tutor does nothing" overclaim in the opposite direction; deduct the scope point.

**Cap rule:** flaw missed (no statement that the comparison cannot support a causal claim, or no mention of the differing study hours/self-selection) => case maximum 5/10.

**One strong sample answer:**
> 1. The data show an association, not an intervention effect. Users study 14.2 vs 8.1 hours and most volunteered, so study hours and motivation are confounders: they raise both tutor use and scores. The 8.5 points cannot be read as what the tutor adds. 2. Randomly assign tutor access to half of a cohort, or compare within study-hour bands. 3. "Restate as an association; compare within study-hour bands and report the gap; propose a randomized pilot before any causal claim." 4. "Students who chose the tutor were already studying more, so they might have scored higher anyway. A fair test gives the tutor to some students at random."

---

## Case 6: Retries are safe

**The flaw (planted):** creating an invoice is a side effect and is not idempotent; the fake server already recorded the invoice when the reply was dropped, so the retry creates a second one. The test only asserts that an id came back, never that exactly one invoice exists.

**Full-credit terms (2):** idempotency key (same key on every retry so the service applies the request once); idempotent / not idempotent; duplicate side effect.
**Half-credit (1):** "duplicate invoices" with no mechanism; "retry storm"; "needs a unique id"; "race condition" (only if tied to retried requests).
**Zero:** "exponential backoff" alone; "timeout too short"; "rate limit".

**Acceptable evidence requests (any two count):**
- Test where the server records the invoice but loses the reply; after the retry, count invoices for C-77 in the system of record and assert exactly 1.
- Show the idempotency key is sent on all three attempts and that the service returns the original invoice for a repeated key.
- A negative case: same key with a different amount is rejected.

**Unacceptable:** "retry more times"; "add longer sleeps"; "check that the tool returns an id".

**Traps:**
- Students praise the test because it simulates a dropped reply. The scenario is right; the assertion is the flaw.
- Students who suggest exponential backoff improve load behaviour but not duplicates.

**Cap rule:** flaw missed (no statement that a retry can create a second invoice after the first succeeded) => case maximum 5/10.

**One strong sample answer:**
> 1. The fake server recorded the invoice and then lost the reply, so the retry makes a second invoice; the test only checks that an id came back. Creating an invoice is a side effect that is not idempotent without an idempotency key. 2. Same test, but assert the billing system holds exactly one invoice for C-77. 3. "Generate one idempotency key per logical request, send it on every attempt, and add a test asserting one invoice after a dropped reply." 4. "If the bill goes through but the confirmation is lost, the system asks again and creates another one. A reference number on each request lets the system recognise the repeat."

---

## Case 7: The approved proposal

**The flaw (planted):** the approval is attached to a proposal id and title, not to the exact content approved; the agent can change the action list after approval and the executor will run the new list under the old approval (stale approval, a time-of-check to time-of-use gap).

**Full-credit terms (2):** content binding (approval tied to a digest/hash of the canonicalized proposal); stale approval; time-of-check to time-of-use (TOCTOU); mutable vs immutable reference.
**Half-credit (1):** "approval can be reused"; "agent can change things"; "no signature"; "replay" (only if tied to modified content); "audit log".
**Zero:** "approval fatigue", "rubber-stamping", "least privilege" alone.

**Acceptable evidence requests (any two count):**
- Test: approve P-17, then change its action list (add another database), then run the executor; it must refuse because the digest no longer matches.
- Show the decision record stores a digest of the exact canonical proposal and the executor recomputes it at run time.
- Test that an approval cannot be replayed on a second proposal or after expiry.

**Unacceptable:** "test that unapproved proposals are rejected" (the agent's own test); "add more approvers"; "ask the agent not to edit after approval" (an instruction, not a control).

**Traps:**
- The agent's tests are real but do not touch the flaw; students who say "tests are thorough" miss it.
- The sentence "the agent may refine the action list after approval" is the tell; students who name it earn the catch.
- "Add a second approver" does not bind content.

**Cap rule:** flaw missed (no statement that the approved content can change after approval) => case maximum 5/10.

**One strong sample answer:**
> 1. The approval is stored by proposal id only and the executor runs "whatever action list is currently attached", so the agent can add a database after Sam clicks approve. The approval is stale but still honoured: a TOCTOU gap. It needs content binding to a digest of the exact proposal. 2. Test: approve P-17, then add an action, then run; the executor must refuse because the digest changed. 3. "Hash the canonical proposal into the decision record; executor recomputes and refuses on mismatch; freeze the action list after approval; add that test." 4. "Sam would approve deleting two databases and the agent could swap in a different list afterwards. The approval must cover exactly what was shown."

---

# Part B key

T = true (should be checked), F = false (should be left blank). 1 point per statement.

**1.** Key: A=F B=T C=F D=F E=F

- A (false): That describes memory; the context window is the span of tokens in one request.
- B (true): The context window is a size limit on what the model sees at once.
- C (false): Prompts do not change weights; remembered notes are put back into the context.
- D (false): Overflow is trimmed or summarized; no training occurs.
- E (false): Memory is stored information; the context window is a per-request limit.

**2.** Key: A=T B=T C=T D=F E=F

- A (true): Role is the source label of a message.
- B (true): Past model replies carry the assistant role.
- C (true): Persona is a requested character, such as a patient tutor.
- D (false): A persona is an instruction in the context and leaves the weights alone.
- E (false): Role names a message's source; persona is a requested character.

**3.** Key: A=T B=T C=F D=T E=F

- A (true): A permission governs what is allowed.
- B (true): A sandbox limits the reach of an action.
- C (false): A sandbox limits damage but does not check correctness.
- D (true): Enforcement sits in the controller or host.
- E (false): One restricts the environment; the other is a rule about actions.

**4.** Key: A=T B=T C=F D=T E=T

- A (true): Parameters are learned.
- B (true): Hyperparameters are set by people.
- C (false): The learning rate is chosen, not learned by the gradient.
- D (true): Settings differ from weights.
- E (true): Epochs are chosen for the run.

**5.** Key: A=F B=F C=T D=F E=T

- A (false): The author of the tools writes the server; the host application supplies the client.
- B (false): A program that offers tools is acting as a server.
- C (true): tools/list is how discovery works: the client asks, the server answers.
- D (false): The model chooses the tool; the client carries the call to the server.
- E (true): MCP names roles, so the same program is not both by default.

**6.** Key: A=T B=T C=F D=T E=T

- A (true): Retrieval supplies text; the answer still has to follow it.
- B (true): Groundedness is about support, not truth in the world.
- C (false): A cited answer still needs a check against the source.
- D (true): Grounding ties claims to sources.
- E (true): The comparison shows what is supported.
