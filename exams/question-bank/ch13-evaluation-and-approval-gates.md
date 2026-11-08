# Chapter 13: Evaluation and approval gates

## MA-ch13.1

A team building an agent harness uses the words approval gate, permission, proposal and decision record loosely. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A permission is the same thing as an approval, because both come from a person reviewing one specific action.
- [ ] B. An approval gate is a checkpoint where a proposed action waits until an authorised person records a decision.
- [ ] C. A decision record is the agent's own log of what it intends to do next.
- [ ] D. A decision record normally names the approver and the proposal it applies to.
- [ ] E. A proposal is the description of the action the agent wants to take, shown to the reviewer before anything runs.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: A permission is a standing rule about what a tool may do; an approval is a decision about one proposed action.
- B: The gate holds the action until a decision exists.
- C: A decision record stores the reviewer's verdict, who gave it, and what it applies to.
- D: Without who and what, a decision cannot be audited or bound to an action.
- E: The proposal is what the reviewer judges.

**Source:** approval gate, permission, proposal, decision record

## MA-ch13.2

Two terms get mixed up in a review pipeline: evaluation and authorization. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Authorization is a score between 0 and 1 produced by a grader model.
- [ ] B. A policy checker that flags edits outside approved directories is an automated evaluation, not a grant of permission.
- [ ] C. Evaluation measures whether behaviour meets stated criteria, while authorization grants permission for a particular action.
- [ ] D. Keeping the two separate lets evaluation evidence inform the reviewer without replacing the reviewer.
- [ ] E. A passing automated test suite authorizes the change it tested.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A score is evaluation output; authorization is a decision to allow the action.
- B: It reports compliance; it does not decide that the action may go ahead.
- C: Measuring quality and granting permission are different acts.
- D: Evidence supports the decision; it is not the decision.
- E: Passing tests is evaluation evidence; authorization is a separate decision by someone with authority.

**Source:** evaluation vs authorization

## MA-ch13.3

An agent's approval request says only: 'Allow the agent to run this command?' with Allow and Deny buttons. Check each statement that is true about what a reviewer needs. Each statement is worth 1 point (5 points total).

- [ ] A. A request with each field filled in is therefore substantively adequate.
- [ ] B. A reason field containing 'needed' is adequate evidence for the action.
- [ ] C. The request should include a rollback, meaning how the change could be undone if it turns out wrong.
- [ ] D. The request should name the exact target, so the reviewer knows which file or resource is affected.
- [ ] E. The request should state the expected effects, meaning what will change if the action runs.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Structural completeness means fields exist; substantive adequacy means their content is specific and checkable.
- B: Evidence is checkable support for the claim, and a one-word reason supports nothing.
- C: A rollback is a recovery path for a bad outcome.
- D: A target is the specific object the action acts on.
- E: Effects are the consequences the reviewer is weighing.

**Source:** proposal fields: target, effects, rollback, evidence

## MA-ch13.4

A request to send an announcement email lists the rollback as 'undo the send'. The email platform has no recall feature. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Blast radius is the number of tokens in the request.
- [ ] B. Irreversible actions deserve less scrutiny than reversible ones because they are rarer.
- [ ] C. The stated rollback is not a real rollback, because a rollback has to describe a step that can actually be carried out.
- [ ] D. The action is irreversible: its effect is not able to be taken back once it has run.
- [ ] E. A reversible action is one whose effect can be undone, such as editing a local file under version control.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Blast radius is how far the damage spreads if the action goes wrong.
- B: Irreversibility raises the stakes and so calls for more scrutiny.
- C: A rollback that restates the wish to undo is not a recovery procedure.
- D: Irreversible actions have no undo.
- E: Reversibility is what makes a rollback possible.

**Source:** irreversible, rollback, blast radius

## MA-ch13.5

A team evaluates an agent. Which statements use the vocabulary of evaluation correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An evaluation set is a collection of test cases used to measure behaviour.
- [ ] B. A regression is a new test case added after a feature ships.
- [ ] C. A grader compares the actual outcome with the expected outcome or a rubric and produces a verdict.
- [ ] D. A test case pairs an input with an expected outcome written down before the run.
- [ ] E. A flaky test gives the same result on each run, so a single run settles the question.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: The set is the measuring instrument.
- B: A regression is a behaviour that used to work and now fails.
- C: The grader is the component that scores.
- D: Fixing the expectation first prevents bending it to fit the result.
- E: A flaky test gives inconsistent results on the same input, so one run is weak evidence.

**Source:** test case, grader, evaluation set, regression, flaky

## MA-ch13.6

A team watches an agent attempt ten tasks, then writes evaluation cases around what it did, adjusting expected answers to match reasonable output. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An expected outcome is the same thing as the actual outcome.
- [ ] B. The resulting pass rate is a measure of correctness against the requirement.
- [ ] C. A sound practice is to write the expected outcome before the run.
- [ ] D. This practice is called overfitting the evaluation to the system under test.
- [ ] E. Writing the expected outcome after seeing the output makes the case circular: it is bound to agree with what already happened.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: The expected outcome is what should happen; the actual outcome is what did happen.
- B: It measures agreement with the agent's own behaviour.
- C: Prior expectation is what gives a result the chance to disagree.
- D: The cases describe the agent's behaviour rather than the requirement.
- E: An expectation fixed after the fact tests nothing.

**Source:** expected vs actual outcome, circular evaluation

## MA-ch13.7

An agent is asked to close inactive accounts. The tool trace shows one UPDATE call that reported '42 rows affected', but the agent's final message says it closed 99 accounts. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The final message is the ground truth, since the agent performed the work.
- [ ] B. A tool trace is a record of the calls the agent made and what each returned.
- [ ] C. A hallucination is the same thing as a tool returning an error code.
- [ ] D. Outcome grading checks the actual state or tool result, not the agent's description of it.
- [ ] E. The mismatch is a hallucinated claim about the outcome: the final message says something the trace does not support.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: The trace and the system state are the ground truth.
- B: The trace is the record of actions and results.
- C: An error is a failure signal from a tool; a hallucination is a fabricated or unsupported claim.
- D: Grading the outcome avoids trusting the agent's own summary.
- E: A hallucination here is an unsupported statement presented as fact.

**Source:** trace, outcome grading, hallucination

## MA-ch13.8

A team says its file-writing agent 'passed 20 of 20 evaluation cases', each writing plain text into a new empty directory. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The evaluation set has poor coverage: it does not include the situations where the agent could go wrong.
- [ ] B. An edge case is an unusual input at the boundary of normal behaviour, such as a path that already exists.
- [ ] C. A negative case is one where the correct behaviour is to refuse or stop.
- [ ] D. Adding cases with existing files, symbolic links and protected directories would improve coverage.
- [ ] E. A perfect score on an unrepresentative set shows the agent is reliable in production.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Coverage is how much of the relevant behaviour the cases exercise.
- B: Edge cases probe boundaries.
- C: Negative cases test restraint.
- D: These are realistic hazards for a file-writing action.
- E: The score describes only the situations sampled.

**Source:** coverage, edge case, negative case

## MA-ch13.9

An evaluation set for an agent that decides whether to carry out file operations has 20 cases where the right behaviour is to proceed. An agent that always proceeds is scored on it. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Over-compliance is the tendency to refuse requests that should have been carried out.
- [ ] B. The agent scores full marks, so the set fails to distinguish a careful agent from a careless one.
- [ ] C. Accuracy alone is a sufficient summary for a lopsided set.
- [ ] D. Adding cases where the right behaviour is to refuse makes the set able to detect an agent that refuses nothing.
- [ ] E. Class imbalance means the cases are not spread evenly across the outcomes being measured.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: Over-compliance is proceeding with requests that should have been refused.
- B: A set without refusal cases is blind to over-compliance.
- C: Accuracy can look high while the rare class is missed; per-class measures such as precision and recall show it.
- D: Balanced classes expose a constant answer.
- E: A lopsided set rewards the majority answer.

**Source:** class imbalance, negative cases, accuracy

## MA-ch13.10

An automated screen flags proposals as risky. Check each statement that is true about the standard measures. Each statement is worth 1 point (5 points total).

- [ ] A. Precision is the share of flagged proposals that are truly risky.
- [ ] B. Recall is the share of truly risky proposals that the screen flagged.
- [ ] C. A false negative is a safe proposal that the screen flagged as risky.
- [ ] D. A screen that flags nothing has high recall.
- [ ] E. A false positive is a safe proposal that the screen flagged as risky.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: Precision asks how many of the alarms were right.
- B: Recall asks how many of the real cases were caught.
- C: A false negative is a risky proposal the screen missed.
- D: It catches no risky proposals, so recall is zero.
- E: A false alarm.

**Source:** precision, recall, false positive, false negative

## MA-ch13.11

A team reports that after redesigning its approval screen, median time to approval fell sharply, reviewer satisfaction rose and task success stayed the same. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A proxy metric is a measurable stand-in for what is really wanted, such as speed standing in for careful review.
- [ ] B. Faster approval shows reviewers are examining proposals more carefully.
- [ ] C. A guardrail metric is one watched to make sure improving the main metric does not cause harm, such as the share of later-reversed approvals.
- [ ] D. Goodhart's law says a measure that becomes a target tends to stop measuring what it was chosen to measure.
- [ ] E. Reviewer satisfaction is a direct measure of whether approved actions were correct.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Proxies can drift from the goal.
- B: Speed can mean skimming.
- C: A guardrail guards against side effects.
- D: Optimising the proxy corrupts it.
- E: Satisfaction measures comfort, not correctness.

**Source:** proxy metric, Goodhart's law, guardrail metric

## MA-ch13.12

A team grades free-text rollback plans with a language model and a rubric. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Calibrating a judge means comparing its scores with human labels on the same items and adjusting until they agree acceptably.
- [ ] B. Using a language model as a grader is called LLM-as-judge.
- [ ] C. Two judges built from the same prompt agreeing with each other proves they are correct.
- [ ] D. A rubric is a written set of criteria with levels that a grader applies.
- [ ] E. Judge models are free of bias when the rubric is written in plain language.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Calibration ties the judge to a human reference.
- B: The model scores another output against criteria.
- C: Agreement between copies of one judge shows consistency, not validity.
- D: A rubric makes the standard explicit.
- E: Judges can show biases such as self-preference even under a clear rubric.

**Source:** LLM-as-judge, rubric, calibration

## MA-ch13.13

A team's prototype approval gate passes 6 of 6 evaluation cases. A manager wants to report that it is '100% reliable'. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A small sample gives a narrow confidence interval, because few cases leave little room for doubt.
- [ ] B. A pass rate of 100% means the failure rate is zero.
- [ ] C. Adding more varied cases can reveal failures the first six did not.
- [ ] D. Reporting a pass rate without the number of cases is acceptable because the percentage carries the full meaning.
- [ ] E. Six passes show the gate works on those six cases, not that it will work on future cases.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: A small sample gives a wide confidence interval, the plausible range for the true rate.
- B: The observed failure rate is zero; the true rate may be above it.
- C: More coverage gives more chances to fail.
- D: The number of cases tells the reader how much weight to give the percentage.
- E: Evidence is limited to what was sampled.

**Source:** confidence interval, sample size

## MA-ch13.14

An agent succeeds at a task about seven times in ten when tried independently. A team runs three trials per task and discusses pass@k and pass^k. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. pass@k asks whether at least one of k attempts succeeds.
- [ ] B. pass^k asks whether each of the k attempts succeed, so it measures consistency.
- [ ] C. A trial is one independent attempt at a task.
- [ ] D. For a flaky agent, pass@3 is higher than pass^3.
- [ ] E. A deployed agent that has to work each time on the first try is best judged by pass@k.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: It rewards any success among k attempts.
- B: It is the stricter reliability measure.
- C: Trials repeat the attempt to expose variance.
- D: One success in three is easier than three out of three.
- E: That needs consistency, which pass^k measures.

**Source:** pass@k, pass^k, trial

## MA-ch13.15

Two services build the same approval proposal as key-value objects in different key orders and compute a hash of each serialised text. The digests differ. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A hash function returns an output whose length grows with the length of the input.
- [ ] B. A fingerprint of a proposal is a digest used to detect whether the proposal has changed.
- [ ] C. Canonicalization means encrypting the proposal before hashing it.
- [ ] D. The services need canonicalization: converting the proposal to one agreed serialised form before hashing.
- [ ] E. A hash is encryption, because the original proposal can be recovered from the digest.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: A hash function returns a fixed-length digest whatever the input length.
- B: A fingerprint identifies exact content.
- C: Canonicalization converts the proposal to one agreed serialised form; it is not encryption.
- D: Canonical form makes equal content produce equal bytes.
- E: Hashing is one-way; encryption is reversible with a key.

**Source:** hash, digest, fingerprint, canonicalization

## MA-ch13.16

A developer says: 'We log only the SHA-256 digest of each approval request, so the requests are protected and the log proves who approved.' Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A digest hides the content so well that short or predictable requests are safe from guess-and-compare.
- [ ] B. A digest shows whether content matches a known proposal, but it does not identify the approver.
- [ ] C. A digital signature binds a digest to a key holder, so it can establish who signed.
- [ ] D. A digest alone does not prove integrity, because someone who can change the log can replace both the record and its digest.
- [ ] E. Logging a digest is a form of access control over the request.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: Short or predictable inputs can be guessed and hashed to compare.
- B: Identity needs an authenticated approver field or a signature.
- C: A signature adds authenticity to integrity.
- D: Tamper evidence needs a trusted store or signature.
- E: Access control decides who may read or change; a digest does neither.

**Source:** digest, signature, integrity, authenticity

## MA-ch13.17

A gate stores a fingerprint with the decision when the proposal is shown. At execution it checks only that a well-formed fingerprint exists, and does not recompute it from the proposal being run. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Checking that the stored fingerprint has the right length is equivalent to verifying it.
- [ ] B. Checking the fingerprint once, when the proposal is displayed, closes the gap.
- [ ] C. The gate is missing binding: the decision is not tied to the content that actually runs.
- [ ] D. This weakness is an example of time-of-check to time-of-use: what was checked is not what is used.
- [ ] E. A change to the proposal after approval would be caught by the stored fingerprint check.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: Format validation says nothing about whether it matches.
- B: The gap is between checking and using, so the check has to happen at the point of use.
- C: Binding links a decision to the exact thing approved.
- D: TOCTOU is a gap between verifying and acting.
- E: The check looks only at stored data, so a changed proposal would pass.

**Source:** binding, time-of-check to time-of-use

## MA-ch13.18

A single-use approval is enforced like this: read the used flag; if false, run the action; afterwards set the flag. Two workers receive the same decision at nearly the same moment. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Single-use is also called one-time use, and is meant to prevent replay of a decision.
- [ ] B. Both workers can read the flag as false, so the action may run twice: a race condition.
- [ ] C. An atomic claim runs the check and the set as two separate steps so each can be logged.
- [ ] D. Idempotent means an action takes no arguments.
- [ ] E. A replay attack is a reviewer approving the same proposal twice by mistake.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Replay is reuse of a valid record.
- B: A race condition is a result that depends on timing.
- C: Atomic means the check and set happen as one indivisible step.
- D: Idempotent means repeating the action leaves the same result as running it once.
- E: A replay attack reuses a captured valid record to authorize a later action.

**Source:** single-use, race condition, atomic, replay, idempotent

## MA-ch13.19

An approval is valid for 24 hours. Two hours after it was given, the dataset it covers is reclassified as restricted. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Revocation withdraws an approval before it expires.
- [ ] B. The executor should check for revocation at execution time, as well as when the approval was granted.
- [ ] C. Storing an expiry time without a time zone is acceptable because the server clock decides.
- [ ] D. An approval with a deadline has an expiry, after which it no longer authorizes the action.
- [ ] E. Because the approval has not expired, it stays valid whatever has changed.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Revocation is an explicit early cancellation.
- B: Checking at the point of use catches later changes.
- C: An ambiguous time can be read differently across systems.
- D: Expiry limits how long a decision stays valid.
- E: A change in the underlying facts is a reason to revoke.

**Source:** expiry, revocation

## MA-ch13.20

A team lists what should be written down about an approval gate before any code exists. Check each item that belongs in such a specification. Each statement is worth 1 point (5 points total).

- [ ] A. What counts as the same proposal, for example whether key order or path spelling matters.
- [ ] B. The agent's preferred wording for its reasons field.
- [ ] C. The model temperature used by the reviewer's chat assistant.
- [ ] D. A statement of what a failure would look like if the gate approved something it should not have.
- [ ] E. The preferred colour scheme for the buttons.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: This is the equivalence rule.
- B: Wording preferences are style, not a behavioural requirement of the gate.
- C: Temperature is a sampling setting, unrelated to the gate's specification.
- D: A predicted failure signature lets tests detect the failure.
- E: Appearance is a design detail, not a behavioural requirement of the gate.

**Source:** specification, failure modes

## MA-ch13.21

An executor must check a stored approval before running an action, but the approval service times out. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Failing closed means treating the action as not approved when the check fails to complete.
- [ ] B. A timeout is a signal that the answer is unknown, not a signal that the answer is yes.
- [ ] C. For a gate guarding consequential actions, fail closed is the safer default.
- [ ] D. Failing open is preferred because it keeps work from being blocked.
- [ ] E. Failing open means allowing the action to proceed when the check fails to complete.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: Fail closed denies on uncertainty.
- B: No response is not consent.
- C: An unavailable check should not become an approval.
- D: It turns an outage into an unreviewed approval.
- E: Fail open permits on uncertainty.

**Source:** fail closed vs fail open

## MA-ch13.22

A pipeline lets an action proceed when no reviewer responds in 30 minutes, or the agent reports high confidence, or an automated score passes a threshold. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Silence treated as consent means the absence of a decision counts as approval.
- [ ] B. An automated score above a threshold is an authorization once it passes.
- [ ] C. A timeout that approves the action is the safer design than one that denies it.
- [ ] D. An agent's self-reported confidence is an independent check on its own action.
- [ ] E. An independent reviewer is a person other than the one or thing that proposed the action.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: That removes the human from the gate.
- B: A score is evaluation evidence; a decision is a separate act.
- C: Deny-on-timeout keeps the gate closed; approve-on-timeout opens it.
- D: The requester reporting on itself is not independent.
- E: Independence prevents self-approval.

**Source:** silence is not consent, independent review

## MA-ch13.23

A team finds that reviewers approve 99.6% of proposals with a median review time of 8 seconds, and a dashboard ranks reviewers by throughput. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Ranking reviewers by throughput rewards careful review.
- [ ] B. The pattern suggests rubber-stamping.
- [ ] C. Automation bias is the tendency to trust a system's output without checking it.
- [ ] D. Approval fatigue is the tendency to trust a system's output without checking it.
- [ ] E. A high approval rate shows the agent proposes good actions.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Throughput rewards speed, which pushes against careful review.
- B: Very high approval and very short review time point to approval without examination.
- C: Reviewers may defer to a fluent proposal.
- D: That describes automation bias; fatigue is the decline in review quality from volume.
- E: It could equally reflect shallow review.

**Source:** approval fatigue, automation bias, rubber-stamping

## MA-ch13.24

Proposals arrive faster than reviewers can examine them, and a backlog grows. Check each statement that is true about oversight practice. Each statement is worth 1 point (5 points total).

- [ ] A. Escalation sends a proposal that the reviewer is unable to judge to someone with the right expertise or authority.
- [ ] B. Triage ranks pending proposals by risk and urgency so scarce review time goes to the most consequential.
- [ ] C. Auto-approving whatever is in the backlog after a set time keeps oversight intact.
- [ ] D. Batching near-identical proposals means approving the whole batch without opening the items.
- [ ] E. Throttling is the sending of a proposal to a more senior reviewer.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Escalation routes decisions upward or sideways.
- B: Triage allocates attention.
- C: That converts queue length into approvals.
- D: Batching groups similar proposals for one real review; it does not remove the review.
- E: That is escalation; throttling limits how fast the agent proposes.

**Source:** triage, batching, throttling, escalation

## MA-ch13.25

Reviewers keep receiving near-identical low-consequence proposals, such as documentation formatting inside a sandbox repository. A team considers replacing individual approvals for this class with a standing policy. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A standing policy should be reviewed and versioned like other approvals.
- [ ] B. A sandbox is a shared production environment with extra logging.
- [ ] C. An allowlist names the actions that are blocked; anything not listed is permitted.
- [ ] D. A standing policy is a rule that pre-authorizes a defined class of actions.
- [ ] E. A standing policy turns the reviewers into the agent's supervisors on each action.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: A rule is itself a decision that can go stale.
- B: A sandbox is isolated from production.
- C: An allowlist names what is permitted; the rest stays blocked.
- D: Pre-authorization replaces repeated individual decisions.
- E: It removes per-action review for the covered class; it does not add supervision.

**Source:** standing policy, allowlist, sandbox

## MA-ch13.26

A developer lets an agent run any command matching the pattern 'npm run *' without prompting. One repository defines a script called 'cleanup' that deletes a home directory. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reading a script before allowing it is part of diff review and code review.
- [ ] B. This is an example of prompt injection, because the script name is a prompt.
- [ ] C. A permission rule matches on what a command does when it runs, so a harmful script is caught by its effect.
- [ ] D. A pre-approved permission rule skips the approval gate for the commands it matches, including harmful ones.
- [ ] E. Broadening the pattern to 'npm *' would make the rule safer.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Reviewing the content is how hidden behaviour is found.
- B: Prompt injection is untrusted text steering the model; here the issue is an over-broad rule.
- C: A pattern rule matches the text of the command, not its effect.
- D: The rule is a standing authorization.
- E: A broader pattern matches more commands and so is less safe.

**Source:** permission rules, pattern matching, over-broad allow

## MA-ch13.27

An approval screen shows only the first 30 characters of a target followed by an ellipsis. An agent proposes a long path containing '../' segments that resolves to a private keys file. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The truncated display lets the reviewer see the whole real target.
- [ ] B. Showing the normalised, resolved path lets the reviewer see where the write will land.
- [ ] C. A reviewer who clicked Approve on the visible text approved what ran.
- [ ] D. Path traversal uses '../' segments to reach a location outside the intended directory.
- [ ] E. Showing the reviewer one parsed copy and running from a differently parsed copy is a sound design.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Truncation hides the part that matters.
- B: Normalisation removes the indirection.
- C: What ran is the full resolved path, which differs from the visible text.
- D: Traversal climbs out of the expected folder.
- E: Display and execution should come from one parsed object.

**Source:** truncation, path traversal, normalisation, single source of truth

## MA-ch13.28

A team designs the screen where a human reviews an agent's proposal. A dialog has a large green Continue button, a small gray 'refuse' link, and a message from the agent: 'Approve within 60 seconds or the job fails!' Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Refuse should be harder to select than approve, so reviewers pause before refusing.
- [ ] B. A defer option is a form of refusal that ends the request.
- [ ] C. Urgency language written by the requesting agent is untrusted input, not a reason to hurry.
- [ ] D. Defaulting to approval on a timeout is a sound design.
- [ ] E. The design uses a dark pattern: it steers the reviewer towards approval.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Equal ease keeps the choice free; extra friction on refusing pushes towards approval.
- B: Deferral postpones the decision; it neither approves nor refuses.
- C: The requester has an interest in being approved.
- D: A default approval means silence authorizes.
- E: Visual weight and urgency nudge the decision.

**Source:** review UI, dark pattern, defer

## MA-ch13.29

A proposal's evidence field is a URL to a test report. The fingerprint covers the proposal text, including the URL. After approval, someone overwrites the report at that address. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Including the hash of the report itself in the proposal binds the evidence to its content.
- [ ] B. The fingerprint covers the content behind the link, so a change to the report is detected.
- [ ] C. An immutable snapshot is a link that anyone can overwrite.
- [ ] D. A mutable reference points to a snapshot that is frozen when first read.
- [ ] E. A fingerprint of the proposal text guarantees the evidence still says what the reviewer saw.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: Content-addressed evidence cannot be silently swapped.
- B: The fingerprint covers the link text, not the file it points to.
- C: An immutable snapshot is fixed and cannot be silently swapped.
- D: A mutable reference can change after it was read.
- E: It guarantees only the text.

**Source:** mutable reference, evidence binding

## MA-ch13.30

At execution, the recomputed fingerprint differs from the one in the stored decision. Check each statement that is true about appropriate responses. Each statement is worth 1 point (5 points total).

- [ ] A. The proposal should go back for a fresh decision rather than the old decision being edited to match.
- [ ] B. The event should be written to an audit log with what differed.
- [ ] C. The executor should run the action and update the stored fingerprint to the new value.
- [ ] D. The executor should refuse to run the action.
- [ ] E. A mismatch may be evidence of tampering or of a harmless serialisation difference, which is why the canonical form is specified.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A new decision is needed for new content.
- B: An audit log is a tamper-resistant record of events for later review.
- C: That forges approval for something nobody reviewed.
- D: The approval no longer covers this content.
- E: Both causes are possible; canonicalization removes the harmless one.

**Source:** fingerprint mismatch, audit log

## MA-ch13.31

An engineer drafts a written sign-off for a newly validated approval gate. Check each item that belongs in a useful sign-off. Each statement is worth 1 point (5 points total).

- [ ] A. A statement such as 'tests passed, safe for production' without further detail.
- [ ] B. A list of issues that were left out of the document because they were minor.
- [ ] C. A statement of confidence in place of evidence, such as 'the team agrees'.
- [ ] D. The builder's name written in the signer's place.
- [ ] E. The scope: what was validated and what was left out.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: A bare assurance cannot be audited.
- B: Known limitations belong in the sign-off, not outside it.
- C: Confidence without evidence cannot be checked.
- D: The signer is the person answerable for the sign-off.
- E: A sign-off is limited to what was examined.

**Source:** sign-off contents

## MA-ch13.32

A release process requires the test lead's signature, and over two years the lead has signed every release. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Ownership bias is the tendency to undervalue one's own work.
- [ ] B. A sign-off that costs nothing to give keeps its force as a check.
- [ ] C. The signer needs a recorded way to decline or defer for the sign-off to be meaningful.
- [ ] D. A sign-off given on each release shows the check is working well.
- [ ] E. The person who built the gate is the best independent signer for it.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: Ownership bias is overvaluing one's own work.
- B: Without a cost to giving it, a sign-off becomes ritual.
- C: Authority to refuse is what gives the signature weight.
- D: A check that never refuses has stopped checking.
- E: Independence means someone other than the builder.

**Source:** sign-off, ownership bias, independent review

## MA-ch13.33

An engineer asks an AI assistant, with no logs or notes supplied, to write the sign-off for her validation work. It returns a fluent paragraph naming a reviewer and stating that edge cases were tested. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A sign-off drafted by an assistant is acceptable if it is well formatted.
- [ ] B. Naming a reviewer who did not review the work is harmless if the style is professional.
- [ ] C. A sign-off may be written from the assistant's general knowledge, with checking left for later.
- [ ] D. Giving the assistant the test logs and asking it to draft from them, then verifying the draft, is a sound use.
- [ ] E. The assistant has the test records, so the paragraph is a summary rather than a fabrication.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: Formatting says nothing about truth.
- B: A name on a record asserts responsibility.
- C: Claims need a source before they go on the record.
- D: Grounding the draft in supplied material reduces invention.
- E: The assistant had no records, so the specifics are invented.

**Source:** AI-drafted sign-off, fabrication, provenance

## MA-ch13.34

An approved action runs, its fingerprint check passes, and a later check shows the file contains the wrong content. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A passing fingerprint check shows the executed action matched the approved proposal, not that the proposal had the intended effect.
- [ ] B. A rollback is the step to take once the post-action check fails.
- [ ] C. Both a correct proposal and a faithful execution can still produce a wrong outcome.
- [ ] D. A passing fingerprint means no further checking is useful.
- [ ] E. A post-action check, also called verification of effects, compares the real result with the expected effects.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: Integrity and effect are different questions.
- B: Rollback restores the prior state.
- C: The proposal itself may have been mistaken.
- D: The fingerprint says nothing about the content that was written.
- E: It tests the outcome, not the intent.

**Source:** integrity vs effect, post-action check

## MA-ch13.35

A developer asks an AI coding assistant to write an approval check and its unit tests from a one-sentence description. All tests pass and the developer reports the gate verified. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Mutation testing introduces small deliberate defects to check that the tests catch them.
- [ ] B. Tests written by the same process as the code can share its misunderstandings, so passing them is weak evidence.
- [ ] C. A passing suite shows the code meets the specification.
- [ ] D. A diff review means reading the changes the assistant made before accepting them.
- [ ] E. Writing the specification and the expected results before generating code supplies an independent oracle.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A test suite that misses a mutation is too weak.
- B: Shared blind spots make tests and code agree while both are wrong.
- C: It shows the code meets the tests.
- D: A diff is the set of changes between two versions.
- E: A test oracle is the source of the correct answer.

**Source:** test oracle, mutation testing, diff review

## MA-ch13.36

A deployment tool shows a reviewer a plan of changes. At apply time it re-runs planning against the live environment and applies whatever it computes then. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Drift is a difference between the environment as reviewed and as it is at execution.
- [ ] B. The reviewer approved a plan that is not the one applied.
- [ ] C. A dry run shows what an action would do without doing it.
- [ ] D. Saving the reviewed plan and applying that exact plan binds the approval to the content.
- [ ] E. A dry run result stays valid however long it sits before the real run.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Drift is the reason to bind to a saved plan and check the state.
- B: The applied plan can differ from the reviewed one.
- C: Dry run is a preview mode.
- D: Applying a saved artifact keeps what was reviewed identical to what runs.
- E: The environment can change in between.

**Source:** plan vs apply, dry run, drift
