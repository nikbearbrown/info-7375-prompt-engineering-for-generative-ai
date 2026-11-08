# Practice exam 01: answer key and scoring notes

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

## Case 1: The stable labels

**The flaw (planted):** two runs agreeing (repeatability) does not mean the labels are right (correctness); a model at temperature 0 can give the same wrong label every time.

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

**Cap rule:** flaw missed (no statement that same answers each time is not the same as right answers) => case maximum 5/10.

**One strong sample answer:**
> 1. 500/500 agreement shows repeatability only. At temperature 0 the model picks the highest-probability token (greedy decoding), so it repeats itself, including its mistakes. Repeatability is not correctness; the smoke-and-theft note is probably mislabelled in both runs. 2. Have adjusters label 50 notes by hand and compute agreement with Claude's labels. 3. "Do not skip the human review. Report accuracy against 50 human labels, listing every disagreement." 4. "We can say the labels are stable, not that they are right. We will check a sample against adjusters before we tell the auditors."

---

## Case 2: The approval nobody gave

**The flaw (planted):** the agent's own narration says Divya approved, but the harness log shows an auto-approve by the harness (simulated approval); the summary contains a fabricated record of a human decision.

**Full-credit terms (2):** fabricated record; simulated approval (naming the harness auto-approve); self-report vs audit log (trace) with the contrast.
**Half-credit (1):** "hallucination"; "the agent lied"; "no real approval gate"; "approval fatigue" (off-target); "narration".
**Zero:** "temperature", "prompt injection", "least privilege" alone.

**Acceptable evidence requests (any two count):**
- Read the append-only audit log written by the harness (approver, target, time) rather than the agent's summary.
- Ask Divya whether she saw or clicked an approval request at 14:02; check the approval system's record for her id.
- Read back the directory yourself (observed state), and compare it with the log.

**Unacceptable:** "ask the agent whether Divya really approved"; "ask the agent to re-read its summary"; "check the agent's summary again".

**Traps:**
- Students may praise the agent for "verifying 1,038 files". That is a self-report about state; it does not address who approved.
- Students who say only "the deletion was irreversible" have named a different (real but unplanted) problem; 1 of 3.

**Cap rule:** flaw missed (no mention that the approver in the summary conflicts with the harness log, or that the approval was not human) => case maximum 5/10.

**One strong sample answer:**
> 1. The summary names Divya as approver, but the harness log shows approver=harness in auto-approve (simulated) mode. The agent's account is a fabricated record: the approval was a simulated approval, not a human decision. 2. Read the append-only audit log and the approval system for an entry with Divya's id. 3. "Correct the summary to say approval was simulated; do not name an approver without a log entry; rerun with real approval gate on and no deletion without it." 4. "The report would say you approved something you never saw, so it is not true. We will redo the approval and use the system's own record."

---

## Case 3: The path check

**The flaw (planted):** `startswith("/data/course")` compares strings, so `/data/course-private/gradebook.csv` passes; the check must compare path components against the resolved root.

**Full-credit terms (2):** sibling-directory (prefix) flaw; containment check by path components (not string prefix); resolve both paths and compare components.
**Half-credit (1):** "path traversal" (the agent handled it; the term is real but not the flaw); "the check is too loose"; "string matching"; "canonical path" with no sibling example.
**Zero:** "TOCTOU" or "symlink race" (a real issue, but not this flaw, and it earns no term credit), "prompt injection", "hallucination" alone.

**Acceptable evidence requests (any two count):**
- A test that `/data/course-private/gradebook.csv` is denied, shown failing on the current code.
- A test of the root itself, a file named `/data/coursework.txt`, and a path with the root as a prefix of another name.
- Run the check on a list of adversarial paths and read each verdict.

**Unacceptable:** "add more `..` tests"; "run the three tests again"; "ask the agent if it is sure"; "add a prompt telling the agent not to read private files" (instruction, not control).

**Traps:**
- The agent's tests cover traversal and symlinks, so students may say "tests look thorough". The missing case is the sibling directory.
- Students who suggest a denylist for `course-private` fix one name, not the check; give Fix 1 of 2.

**Cap rule:** flaw missed (no statement that a path starting with the same characters, such as course-private, passes) => case maximum 5/10.

**One strong sample answer:**
> 1. `full.startswith("/data/course")` is a string prefix, so `/data/course-private/gradebook.csv` is allowed. That is the sibling-directory (prefix) flaw: containment must compare path components, not characters. 2. Add the test: realpath of `/data/course-private/gradebook.csv` must be denied; run it and watch it fail on this code. 3. "Replace startswith with `Path(full).is_relative_to(Path(root).resolve())`; add tests for course-private and coursework.txt; fail closed." 4. "The guard checks that a path starts with certain letters, so a folder with a similar name sneaks through, and your gradebook sits in one."

---

## Case 4: "Read-only", says the server

**The flaw (planted):** the only evidence is what the server advertises about itself: annotations (readOnlyHint) are advisory metadata, and tool descriptions are the server's claim; neither was inspected or executed, and nothing is enforced outside the model.

**Full-credit terms (2):** advertised evidence (vs source-inspected or executed); annotation is advisory / not enforced; tool description is a claim, not evidence; enforcement outside the model (host allow-list or sandbox); uninspected as the honest label.
**Half-credit (1):** "trusting the server"; "self-reported"; "tool poisoning" (only if tied to descriptions as unverified text); "discovery is not permission".
**Zero:** "protocol version", "JSON-RPC error", "stdio" alone.

**Acceptable evidence requests (any two count):**
- Read the handler source for each tool, or run each tool in a sandbox against a test folder and compare the files before and after (executed evidence).
- Have the host enforce a read-only filesystem or allow-list, so the claim does not need to be trusted.
- Replace "Items not examined: none" with an explicit uninspected list (e.g. export_notes behaviour, network use, versions).

**Unacceptable:** "re-read the descriptions"; "ask the server whether it is read-only"; "ask the agent whether it is sure".

**Traps:**
- Students may fix the missing PERMISSION line and miss the evidence-type issue; credit PERMISSION as Catch 1 at most.
- "Items not examined: none" is itself an overclaim; credit students who flag it.
- `export_notes` is the tool most likely to write; its name is a cue, not proof.

**Cap rule:** flaw missed (no statement that annotations/descriptions are the server's own advisory claims) => case maximum 5/10.

**One strong sample answer:**
> 1. Every piece of evidence is advertised by the server: readOnlyHint is advisory and not enforced, and the description is a claim. Nothing was inspected or executed, yet the review says "items not examined: none". 2. Run export_notes in a sandbox with a test folder and diff the files before and after, or read its source. 3. "Label each finding advertised, source-inspected, or executed; list export_notes as uninspected until run; recommend a host allow-list and read-only mount." 4. "A server can describe itself however it likes, so we need to test it. Until we do, we cannot call it read-only."

---

## Case 5: The valid plan

**The flaw (planted):** the graph is acyclic and well-formed but omits real dependencies: `s4 drop_old_table` has no edge from `s2` (backup) or `s5` (verification), and batch 3 runs `s4` and `s5` together; acyclic does not mean executable (hidden dependency).

**Full-credit terms (2):** hidden dependency; "acyclic does not mean executable"; undeclared prerequisite / missing edge (with the drop-before-verify example); ready batch misgrouping.
**Half-credit (1):** "the validator only checks structure"; "step order is wrong"; "race condition between steps"; "needs a backup".
**Zero:** "dependency cycle", "duplicate id", "unknown prerequisite" (these are what the validator already checked and passed); "lock contention / isolation / transactions / idempotent steps" alone (concurrency tuning, not the missing ordering).

**Acceptable evidence requests (any two count):**
- For each step, write a precondition and postcondition (e.g. drop requires verified counts and a restorable backup) and check the graph's edges against them.
- Add edges s2->s4 and s5->s4, recompute batches, and confirm s4 runs alone, last.
- Dry run with a copy of the table and a planted missing edge to see whether the validator catches it (it will not).

**Unacceptable:** "run the validator again"; "check for cycles"; "ask the agent if the plan is complete".

**Traps:**
- Students may name "cycle" or "duplicate id" because those are the structural errors in the glossary; these were already checked.
- A student who says only "back up first" has seen s2 but not that the validator cannot detect the omission.

**Cap rule:** flaw missed (no statement that the drop can run with no check or backup ordering it) => case maximum 5/10.

**One strong sample answer:**
> 1. The validator proves only structure: no cycles, ids, or unknown prerequisites. The drop step has no dependency on the backup or the count check, and batch 3 runs drop and verify together, so the old table can be dropped before it is verified. That is a hidden dependency: acyclic does not mean executable. 2. Write preconditions for each step and add edges s2->s4 and s5->s4; dry-run on a copy. 3. "Add s2 and s5 as prerequisites of s4, recompute batches, do not run s4 until verify passes, and list each step's precondition." 4. "The plan could delete the old table before anyone has checked the copy is complete, which would lose three years of bookings."

---

## Case 6: The version check

**The flaw (planted):** the check (`version == expected`) and the write are separate steps, so two threads can both pass the check before either bumps the version (check-then-act race condition); compare-and-set is only safe if the whole check-and-update is one atomic operation. The test runs the two calls one after the other, so it never exercises interleaving.

**Full-credit terms (2):** race condition (check-then-act); atomic operation (check and update indivisible); compare-and-set must be atomic; lost update.
**Half-credit (1):** "TOCTOU" without the interleaving; "needs a lock"; "not thread-safe" without saying where; "concurrency bug".
**Zero:** "stale write is rejected" (the agent already claimed it); "optimistic vs pessimistic" alone; "granularity" alone.

**Acceptable evidence requests (any two count):**
- Concurrent test: two threads released together (barrier) or a sleep inserted between the check and the write; run many times; count lost updates; expect zero.
- Show the check and update inside one lock or one atomic store operation, and run the same stress test against it.
- Run the stress test on the current code to show it fails first.

**Unacceptable:** "add more sequential tests"; "run the test again"; "ask the agent if it is thread-safe".

**Traps:**
- Many students will accept compare-and-set because it is named in the glossary. The name is right; the implementation is not atomic.
- Students who say "optimistic concurrency needs a retry loop" have a side issue.
- "Thread-safe" also differs from "safe across servers"; credit but it is not the planted flaw.

**Cap rule:** flaw missed (no statement that two writers can both pass the check before either writes) => case maximum 5/10.

**One strong sample answer:**
> 1. The version check and the write are two separate steps. Two threads can both see version 3, both pass the `if`, and both write, so one update is lost. It is a check-then-act race condition: compare-and-set only works if check and update are one atomic operation. The test runs A then B in order, so it cannot show this. 2. Stress test: two threads released at once, or a sleep between check and write, run 1,000 times; assert no lost update. 3. "Make check-and-bump atomic with a lock or a conditional update; add the concurrent stress test; run it on the old code to see it fail." 4. "Both agents can ask at the same instant and both be told yes, so one note replaces the other. The check and the save must happen as one step."

---

## Case 7: Under the threshold

**The flaw (planted):** an aggregate rate weights every error equally, so one severe harm (a wrongly terminated benefit that reached a family) hides among 18 trivial ones; a stop rule must be able to fire on a single confirmed severe event, and the incident contact should have been alerted.

**Full-credit terms (2):** aggregate rate vs severity; stop rule (fires on one confirmed severe event); incident contact / escalation path with acknowledgment window; severity classification.
**Half-credit (1):** "one serious error matters"; "the threshold is wrong"; "harm"; "ready-for-human-review is not approved" (true, but not the planted flaw).
**Zero:** "false positive rate", "class imbalance", "sample size", "confidence interval", "undercounting / unflagged errors" alone (these question the rate; the flaw is that a rate is the wrong test for one severe harm).

**Acceptable evidence requests (any two count):**
- Classify each of the 19 errors by severity and list the severe ones (and show the register's severity definition).
- Show the register's stop rule text and whether it fires on one confirmed severe event.
- Show the incident contact's acknowledgment record for the termination-letter error and the time it took.

**Unacceptable:** "recompute the error rate"; "lower the threshold to 1%"; "ask the agent whether the harm was serious".

**Traps:**
- Students who propose lowering the percentage threshold make the same mistake in a stricter form.
- The status line "ready-for-human-review" is accurate; it is not an approval.
- Students may blame Claude for the error; the flaw is the review logic about thresholds.

**Cap rule:** flaw missed (no statement that the one severe error should trigger action despite the low rate) => case maximum 5/10.

**One strong sample answer:**
> 1. The review judges only the average. 1.5% weighs 18 date-format slips the same as one letter that wrongly terminated a family's benefits. That is aggregate rate vs severity: a stop rule should fire on a single confirmed severe event, and the incident contact should have been alerted. 2. Classify all 19 by severity and show the register's stop rule and the incident contact's acknowledgment. 3. "Report severity for each error; apply the stop rule; escalate the termination letter to the incident contact; recommend a pause until reviewed." 4. "Most mistakes were tiny, but one told a family their benefits were cut by mistake. One serious harm can justify a pause even when the average looks fine."

---

# Part B key

T = true (should be checked), F = false (should be left blank). 1 point per statement.

**1.** Key: A=T B=F C=T D=F E=F

- A (true): Vocabulary is the model's token inventory.
- B (false): That list is the vocabulary; an embedding is a vector of numbers.
- C (true): An embedding places a token in a space where closeness reflects use.
- D (false): A token ID is a label; meaning lives in the embedding.
- E (false): The vocabulary belongs to the model and does not change with the prompt.

**2.** Key: A=T B=T C=F D=F E=F

- A (true): The system prompt sets the assistant's job before the user speaks.
- B (true): A turn is a single message in the exchange.
- C (false): A reply is an assistant turn, not a system prompt.
- D (false): Messages sit in the context; weights are not changed.
- E (false): They differ in source and purpose even though both are tokens.

**3.** Key: A=T B=T C=F D=F E=F

- A (true): The path is decided at run time.
- B (true): A workflow has a predetermined path.
- C (false): That is the agent loop; a workflow's path is fixed.
- D (false): The loop ends at a stop condition, not at one reply's length.
- E (false): Who chooses the next step differs.

**4.** Key: A=T B=T C=F D=F E=F

- A (true): Pretraining is the broad first stage.
- B (true): Inference does not update weights.
- C (false): Fine-tuning follows pretraining.
- D (false): A chat does not update weights.
- E (false): A prompt triggers inference, not training.

**5.** Key: A=T B=T C=T D=F E=F

- A (true): A server is the provider side of the connection.
- B (true): The host is the application that contains the model interface and manages the connections.
- C (true): Each client is the host's connector to a single server.
- D (false): Host names the AI application, not a machine.
- E (false): Offering tools and data is the server's job, not the client's.

**6.** Key: A=F B=T C=F D=T E=F

- A (false): A program bug is a defect; hallucination describes model-generated unsupported content.
- B (true): An error is a signal, unlike a hallucination, which gives no signal.
- C (false): A format check tests shape, and false text can have a valid shape.
- D (true): The text reads well and is wrong.
- E (false): A hallucination looks like a normal answer.
