# Chapter 14: Governance and ethics

## MA-ch14.1

A team's AI-use register for an LLM workflow names three roles: an owner, an approver and an incident contact. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Writing a group label such as "the team" in the owner field satisfies the definition of an owner.
- [ ] B. The incident contact is the person, or a documented backup, who receives and acknowledges an alert about harm.
- [ ] C. The approver gives the authorized yes to a specific proposal before launch or change.
- [ ] D. The approver is the person who first receives and acknowledges an alert during an incident.
- [ ] E. The owner is the person who answers for the workflow as it runs and has authority to pause or change it.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: A group label names no individual who has accepted responsibility.
- B: The incident contact is the entry point of the response route.
- C: Approval is an act by an authorized person on a particular proposal.
- D: That describes the incident contact; the approver gives the authorized yes to a proposal.
- E: An owner is the accountable person with real control over the running system.

**Source:** Register roles: owner, approver, incident contact

## MA-ch14.2

A governance validator returns one of three statuses for a record: "incomplete", "review-required" or "ready-for-human-review". Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "ready-for-human-review" means the record passed the validator's structural checks.
- [ ] B. "ready-for-human-review" means a person has already approved the workflow.
- [ ] C. "ready-for-human-review" certifies that the workflow complies with regulation.
- [ ] D. "incomplete" means the validator found a concern about the wording of a line and asked a person to judge it.
- [ ] E. "review-required" routes a flagged issue to a person instead of resolving it automatically.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: The status reports presence and shape checks and nothing beyond them.
- B: The status says the record is ready for a person to review, not that review or approval happened.
- C: Compliance is a legal and institutional determination that a script cannot make.
- D: "incomplete" means required fields are missing; a flagged concern is "review-required".
- E: When the machine cannot decide, the conservative design hands the question to a human.

**Source:** Validator statuses and what they claim

## MA-ch14.3

A team announces "We are compliant" after finishing an internal AI-use register. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Completeness describes whether fields are filled in, while compliance is a legal and institutional determination.
- [ ] B. A structural check, a legal review and an ethical judgment answer different questions.
- [ ] C. "The record is complete and structurally valid" is a claim no stronger than the evidence supports.
- [ ] D. Ethical judgment belongs to people with context, and a script that checks field presence does not supply it.
- [ ] E. A complete register is evidence that the workflow complies with applicable law.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: The two words answer different questions and are not interchangeable.
- B: Each kind of review has its own evidence and its own competent reviewer.
- C: The claim names what the check actually established.
- D: A presence check has no access to values, harms or affected people.
- E: A filled-in form shows the form is filled in, not that the law is met.

**Source:** Completeness vs compliance

## MA-ch14.4

A manager asks an LLM assistant to draft an AI-use register, and it returns a fluent, plausible document in seconds. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Writing a person's name in the owner field creates accountability although the person has not accepted the role.
- [ ] B. A fluent draft is a first draft for people to decide on, not a decision.
- [ ] C. Accountability exists when a named person accepts the role and has authority to act.
- [ ] D. The assistant that drafted the register holds ongoing accountability for the workflow.
- [ ] E. The fact that an AI system is not a party that can be sued removes the need to name an accountable person.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Being named in a cell is not acceptance.
- B: Language models draft structured text well, but the decisions belong to people.
- C: Acceptance plus authority is what makes accountability usable.
- D: A model has no continuing duty or channel; accountability stays with the deploying people.
- E: Responsibility for outputs stays with the people and organization that deploy the system.

**Source:** Accountability vs a drafted register

## MA-ch14.5

A team rewrites vague monitoring promises into thresholds. A threshold is usable when a stranger reading the record could tell whether it fired. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Quality will be monitored regularly" is a usable threshold.
- [ ] B. "The team will respond promptly to serious incidents" is a usable threshold.
- [ ] C. "If a weekly random sample of 100 outputs has more than 2 unsupported claims, publication pauses and the content owner investigates" is a usable threshold.
- [ ] D. "The team will remain responsive to user concerns" is a usable threshold.
- [ ] E. "We will intervene when risk becomes unacceptable" is a usable threshold.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: It names no signal, measurement or trigger.
- B: It states an intention without an observable condition.
- C: It gives a signal, a sampling method, a trigger, a response and a responsible role.
- D: It states an attitude, not a condition and a response.
- E: "Unacceptable" is undefined, so nothing observable can be checked.

**Source:** Threshold: signal, trigger, response

## MA-ch14.6

A team monitors an LLM drafting tool. A dashboard shows a high aggregate pass rate on an automated quality check, but review of the failing outputs shows that a few exposed customers' personal data. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Improving the aggregate pass rate guarantees fewer personal-data disclosures.
- [ ] B. A severe harm class is best watched by trend alone, because one event is statistical noise.
- [ ] C. An aggregate pass rate weights each failure equally and does not reflect severity.
- [ ] D. A stop rule for a severe harm class can fire on a single confirmed event.
- [ ] E. The aggregate pass rate already accounts for severity, so the disclosures need no separate handling.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: The aggregate can improve while the rare severe category stays the same.
- B: Severe harm is handled by event-based triggers, not only by trends.
- C: Rare severe events disappear into a large denominator.
- D: One severe event can be unacceptable by itself.
- E: A pass rate counts failures; it does not weight them by harm.

**Source:** Aggregate rate vs severity; stop rule

## MA-ch14.7

An incident owner is named for an LLM publishing pipeline, but staff are rewarded for shipping on time and penalized for delay. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Staff evaluation criteria affect whether a control gets used, so a governance record addresses them.
- [ ] B. How staff are evaluated is an HR matter that a governance record need not address.
- [ ] C. The cost of a pause should be absorbed by the organization rather than by the person who triggers it.
- [ ] D. An owner without authority to pause the pipeline holds a title rather than control.
- [ ] E. A written pause right is unlikely to be used when performance reviews punish delay.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Incentives shape behavior more than policy text does.
- B: Evaluation criteria decide whether controls get used, so they are part of governance.
- C: Making the individual pay discourages use of the control.
- D: Accountability needs the power to act when harm appears.
- E: People respond to what is rewarded, so the control stays on paper.

**Source:** Pause authority and incentives

## MA-ch14.8

The incident contact for an LLM service is on leave, and an alert about a possible data exposure has gone unacknowledged beyond the declared acknowledgment window. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The AI agent running the service can close the gap by naming itself the responsible party.
- [ ] B. A missing escalation path is a defect to fix, not a gap to tolerate until the contact returns.
- [ ] C. The acknowledgment window is the declared time within which an alert should be acknowledged.
- [ ] D. Halting the service's work while the alert is open is a reasonable fail-safe default if a person remains responsible.
- [ ] E. A documented backup with delegated pause authority is part of a sound escalation path.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: An agent is not an accountable person or organization.
- B: Harm can accrue while the response waits for one person.
- C: It turns "respond quickly" into a checkable commitment.
- D: Stopping is low-risk and reversible, but responsibility still sits with an authorized human.
- E: A backup means response does not depend on one person's availability.

**Source:** Escalation path, backup, acknowledgment window

## MA-ch14.9

A team compares two designs for checking data labels. Design 1 keeps a denylist of known sensitive labels and raises a flag on a match. Design 2 keeps an allowlist of approved labels and sends any other label to human review. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A denylist flags the labels it enumerates, so an unlisted sensitive category passes unnoticed.
- [ ] B. A case-sensitive allowlist silently accepts "Public" as if it were "public".
- [ ] C. A label being on the allowlist shows that the proposed use of that data is appropriate.
- [ ] D. An allowlist that routes unrecognized labels to a person fails closed, which is the more conservative default.
- [ ] E. A flag from the allowlist design proves the data is sensitive.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: A denylist only catches what someone thought to list.
- B: An exact comparison fails for "Public", so the value goes to review.
- C: A label says nothing about whether this specific use is appropriate.
- D: When the machine cannot classify, the safe fallback is to ask a human.
- E: It shows only that the label was not recognized.

**Source:** Allowlist vs denylist; fail closed

## MA-ch14.10

A designer wants an automated check on governance records, such as a list of banned phrases for the owner and evaluation lines. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Whether an evaluation line describes an adequate test is a judgment for a person.
- [ ] B. A numeric limit such as a maximum retention period belongs in code, because a validator can enforce it exactly.
- [ ] C. A banned-phrase list reliably detects weak owner lines.
- [ ] D. An LLM judge scoring an owner line as adequate replaces the named person's acceptance of the role.
- [ ] E. A validator that states narrowly what it checks is more honest than one implying it assesses quality.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: Adequacy depends on the system and the harm, which strings cannot encode.
- B: A range is something a validator can check exactly.
- C: Minor rewording passes while saying the same thing.
- D: A score cannot stand in for the person accepting responsibility.
- E: Overstated validators invite trust beyond what was tested.

**Source:** What a validator refuses vs what a person judges

## MA-ch14.11

A validator marks this record "ready-for-human-review": owner "everyone", purpose "help", approver "manager", evaluation "looks fine", incident contact "team", retention 99999 days. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "everyone" in the owner field is a group label, not an accountable person.
- [ ] B. The vague lines are tested against the real world by a person, not by the validator.
- [ ] C. A retention of 99999 days works as a meaningful stated retention period.
- [ ] D. A purpose of "help" bounds the use of the system clearly.
- [ ] E. The record shows that a presence-and-shape check is not evidence of adequate governance.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: No individual has accepted responsibility.
- B: Meaning and sufficiency need human judgment.
- C: It is effectively unlimited retention, which defeats the purpose of stating a period.
- D: It excludes nothing, so no later use can be called out of scope.
- E: The record is complete yet weak, so the status cannot certify quality.

**Source:** Complete but weak record

## MA-ch14.12

A validator decides a field is missing with the test `not record.get(field)`. One record sets retention_days to 0 as a deliberate design choice, and a second record leaves out a key entirely. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. 0 is falsy in Python, so this test reports retention_days as missing.
- [ ] B. A string made of spaces is falsy and is reported as missing.
- [ ] C. A key that is absent is skipped, because the lookup returns a default that is ignored.
- [ ] D. Testing explicitly for a missing value, rather than for falsiness, separates an absent value from a legitimate zero.
- [ ] E. A falsiness test distinguishes a deliberate zero from an absent value.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: A falsy value is treated the same as an absent one.
- B: A non-empty string is truthy even when it holds only whitespace.
- C: The default is falsy, so the absent key is reported as missing.
- D: An explicit missing-value test does not treat 0 as absent.
- E: It treats both the same.

**Source:** Truthy and falsy in a presence check

## MA-ch14.13

A function validates a retention-day count with `isinstance(d, int) and d >= 0`. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In Python, bool is a subclass of int.
- [ ] B. An exact type test such as `type(d) is int` rejects True.
- [ ] C. isinstance(30.0, int) evaluates to True.
- [ ] D. isinstance(True, int) evaluates to True.
- [ ] E. The function rejects 0 because zero is falsy.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: That is why True behaves as 1 in arithmetic.
- B: type(True) is bool, which is not int.
- C: 30.0 is a float, not an int.
- D: A subclass instance passes an isinstance test for its parent class.
- E: The function tests a type and a sign, not truthiness, so 0 passes.

**Source:** isinstance vs exact type; bool is a subclass of int

## MA-ch14.14

A developer writes tests for a retention validator before asking an assistant to implement it. Two deliberately wrong versions exist: one accepts any value for which isinstance(d, int) is true, and one treats a falsy value as missing. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A test expecting True to be rejected tells the correct version from the isinstance version.
- [ ] B. Running the suite against deliberately wrong versions shows whether the suite can tell right from wrong.
- [ ] C. A suite of a normal case plus an empty-record case, and nothing else, catches both wrong versions.
- [ ] D. A passing suite shows the implementation is correct for inputs the suite did not exercise.
- [ ] E. Tests written by a person from a specification before seeing the code capture that person's intent independently.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: The isinstance version accepts True because bool is a subclass of int.
- B: A suite that passes wrong versions is too weak.
- C: Both wrong versions still pass those two cases.
- D: Tests demonstrate only the behavior they exercise.
- E: They are not shaped by what the implementation happens to do.

**Source:** Test-first; checking a suite with wrong versions

## MA-ch14.15

A reviewer words claims in a validation write-up so that each claim is no stronger than its evidence. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Inspecting the stores the team controls supports claims about those stores.
- [ ] B. Test coverage bounds a claim, because untested cases stay unknown.
- [ ] C. A labeled test report sent to the incident contact and acknowledged within the stated time is evidence the route works.
- [ ] D. Reading a provider's documentation that says logs are deleted supports "we verified deletion at the provider".
- [ ] E. "The validator confirmed the workflow is safe" is worded no stronger than a script run supports.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Evidence covers the stores that were actually examined.
- B: A passing suite speaks only for the cases it ran.
- C: The route was exercised, not just listed.
- D: Documentation is the provider's claim; verification needs inspection.
- E: The script checked presence and shape; it did not establish safety.

**Source:** Wording claims to match evidence

## MA-ch14.16

An assistant approved to summarize public course notes is later pointed at student-submitted essays. Its register purpose field reads "use AI". Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The purpose field is decoration because a validator is unable to judge it.
- [ ] B. Using the assistant on a different kind of data is a change of scope that triggers re-review.
- [ ] C. An unchanged model and prompt mean an unchanged risk profile.
- [ ] D. A broad purpose is preferable because it avoids re-review when uses change.
- [ ] E. A purpose statement gives a boundary that people can later check uses against.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: The field forces the team to state a boundary a person can test.
- B: New data and new affected people need a fresh decision.
- C: Risk depends on the data, the people affected and the consequences.
- D: A broad purpose excludes nothing, so scope creep goes unnoticed.
- E: The value of the field is in stating a limit.

**Source:** Purpose statement and scope change

## MA-ch14.17

A register states "retention: 30 days" for user prompts. Prompts also appear in a nightly backup kept 90 days, an e-mailed weekly report and a model provider's service logs. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A stated retention number shows that deletion happened at that time.
- [ ] B. Deleting a prompt from the application log removes summaries derived from it.
- [ ] C. A prompt copied into a nightly backup follows the backup's own retention period.
- [ ] D. A deletion test inserts a labeled test record, runs the lifecycle and inspects the stores the team controls.
- [ ] E. Retention covers the whole lifecycle of the data, including backups, exports and provider copies.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: A number states policy for a store; it is not evidence of deletion.
- B: Derived artifacts live in other stores and may still reveal the source.
- C: The backup's lifetime is set by its own schedule.
- D: Inspecting copies is how deletion is verified.
- E: A policy about one store does not govern the others.

**Source:** Retention lifecycle and copies

## MA-ch14.18

A design document sets retention_days to 0 for a workflow that handles customer messages that go to an external model provider. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Zero can mean delete right after the task, do not persist application data, or keep a de-identified record as evidence.
- [ ] B. Zero retention in the company's own systems makes the provider's terms irrelevant.
- [ ] C. The register should record the provider's retention separately from the company's own.
- [ ] D. A presence check based on falsiness wrongly reports a zero as missing.
- [ ] E. A stated zero is evidence that no copies exist.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: The number does not say which is intended, so the document needs to.
- B: The provider still processes the data under its own terms.
- C: Different parties hold different copies under different rules.
- D: 0 is falsy, so a presence test needs to check for absence instead.
- E: A stated value is a design intent; copies can exist regardless.

**Source:** Zero retention and provider copies

## MA-ch14.19

A team deletes a customer's row from its application database after a deletion request. The customer's data also fed a vector index of embeddings, a weekly summary, a log of hashed e-mail addresses and a backup. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An embedding in a vector index holds no information from its source once it is embedded.
- [ ] B. Stores the team is unable to verify, such as provider systems and backups, are listed as open rather than assumed clean.
- [ ] C. "Removed from this table" supports the claim "erased everywhere".
- [ ] D. A hashed identifier counts as a derived copy of a record that can be matched back to a person.
- [ ] E. Removing a withdrawn participant's quotation from the published summary completes the withdrawal.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: Embeddings are derived data that can still carry information about the source.
- B: Unexamined copies stay unknown.
- C: The claim needs every copy and derivative to be accounted for.
- D: A hash used for matching is still linked to a person; treat it as a copy needing a decision.
- E: The words may remain in an index, an evaluation set and a backup.

**Source:** Deletion across derived copies

## MA-ch14.20

A team compares three ways to log an AI agent's actions: keep full prompts and outputs indefinitely, keep nothing, or keep a minimal audit record. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Keeping nothing is the privacy-safest option and needs no further justification.
- [ ] B. Keeping no trace leaves no way to reconstruct what the agent did after an incident.
- [ ] C. Keeping full prompts and outputs indefinitely creates its own exposure.
- [ ] D. A minimal audit record should hold the full prompt and output text so reviewers see everything.
- [ ] E. A minimal record can hold an operation ID, the policy decision taken, references to evidence stored elsewhere and an error category.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: It trades privacy for the loss of accountability and needs justification.
- B: Without a record, review and recourse are not possible.
- C: Retained content is a target for leaks and misuse.
- D: A minimal record holds identifiers and references, not the content.
- E: References support review without duplicating sensitive data.

**Source:** Minimal audit record

## MA-ch14.21

Two LLM agents score the same on the same evaluation set. Agent A reads public notes and writes a local draft that a person publishes. Agent B reads internal HR records, publishes straight to an external site and keeps its inputs for a long time. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An evaluation score measures performance on a test set, not exposure or consequence.
- [ ] B. Reversibility describes how often an action is repeated.
- [ ] C. Saving a draft in a private workspace is easier to undo than publishing to an indexed public website.
- [ ] D. Action surface is the set of systems and audiences an agent's actions can reach.
- [ ] E. Identical scores mean the two agents need identical governance.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Risk also depends on data, audience and what the agent can do.
- B: Reversibility describes how hard an action is to undo.
- C: A public, indexed copy is hard to recall.
- D: Agent B has a larger action surface than Agent A.
- E: Different data and different consequences call for different controls.

**Source:** Action surface and reversibility

## MA-ch14.22

Two summarizers make the same number of deadline errors. Summarizer X states a deadline its sources do not support. Summarizer Y leaves the deadline out when its sources conflict. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reporting error types separately shows who bears each kind of error.
- [ ] B. Equal accuracy means the two kinds of error cost the same to the people affected.
- [ ] C. A false positive and a false negative can fall on different people.
- [ ] D. Leaving out a deadline when sources conflict is an abstention that moves the checking work to the reader.
- [ ] E. Stating a deadline the sources do not support is a fabrication, often called a hallucination.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Splitting by direction and consequence exposes who is affected.
- B: A false statement and an omission harm different people differently.
- C: Who bears an error depends on the direction of the error.
- D: The error exists but is visible to the reader.
- E: The output asserts something unsupported by the evidence.

**Source:** Error types and who bears them

## MA-ch14.23

A classifier is applied to two groups with different base rates of true positives. Its true positive rate and false positive rate are the same for both groups. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Equal true and false positive rates guarantee equal positive predictive value across the groups.
- [ ] B. Positive predictive value depends on the base rate as well as on the error rates.
- [ ] C. True positive rate is the share of positive predictions that are correct.
- [ ] D. Fairness criteria can conflict, so choosing one is a value decision.
- [ ] E. The data alone will identify the correct fairness definition.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Differing base rates change positive predictive value.
- B: With a lower base rate, a larger share of positive predictions are false.
- C: That is positive predictive value; true positive rate is the share of actual positives found.
- D: Numbers cannot say which definition of fair a society should adopt.
- E: The choice reflects values and context.

**Source:** Base rate, PPV and fairness criteria

## MA-ch14.24

A company reports that its resume-ranking LLM agrees with past hiring decisions on an evaluation set built from people who were hired. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Historical labels can carry the bias of earlier decisions into the model.
- [ ] B. A false negative here is a qualified applicant who is ranked low.
- [ ] C. A set built from hired people contains no rejected candidates, so false negatives are invisible.
- [ ] D. Agreement with past decisions measures consistency with history, not whether those decisions were good.
- [ ] E. Overall agreement shows who bears the false positives.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: A model trained or checked against past outcomes reproduces their pattern.
- B: A false negative is a real positive that the tool misses.
- C: Qualified people who were passed over never appear.
- D: The labels are only as sound as the process that produced them.
- E: A single aggregate hides who is affected.

**Source:** Evaluation population and bias

## MA-ch14.25

A risk register for an LLM tool contains the entry "There may be bias or privacy concerns." Another entry says a student relies on a summary with the wrong deadline and misses the real one. A third lists, for retained health-question logs, the mitigation "weekly test of answer accuracy". Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A weekly accuracy test mitigates the harm of retained logs being exposed.
- [ ] B. A concrete harm lets a team choose a signal, a threshold and an owner.
- [ ] C. "There may be bias or privacy concerns" is a generic risk statement.
- [ ] D. A concrete harm description names the model's architecture rather than the affected person.
- [ ] E. A mitigation is matched to a harm when it reduces that harm's likelihood or severity.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: Accuracy testing addresses a different harm from exposure of stored data.
- B: Specific harm points to what to measure and who should respond.
- C: It names no affected person, event or path.
- D: A concrete harm names who is harmed, what happens and how.
- E: Matching is judged against the named harm.

**Source:** Generic risk vs concrete harm; matched mitigation

## MA-ch14.26

A team plans to consult people affected by a new AI workflow and tries an LLM that role-plays an affected student. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Replies from an LLM role-playing a student are simulated responses, not evidence of what real people think.
- [ ] B. Simulated responses can be recorded in the register as stakeholder input.
- [ ] C. A friendly colleague speaking for the stakeholders counts as consultation.
- [ ] D. Consultation is real when affected people can change the plan as a result.
- [ ] E. Open questions such as "what worries you about this?" invite honest disagreement.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: The model produces plausible text, often agreeable, with no stake in the outcome.
- B: They need to be labeled as simulated and kept apart from real statements.
- C: Consultation involves the people actually affected.
- D: Without a chance to change the plan, it is only announcement.
- E: They do not steer the answer toward acceptance.

**Source:** Consultation vs simulated stakeholders

## MA-ch14.27

An LLM-assisted benefits tool denies a claim, and the claimant has only a general support e-mail address to contact. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The remedy for a displayed error is the same as the remedy for a denied opportunity.
- [ ] B. A reviewer who built the system being contested needs no further safeguard.
- [ ] C. A general support address satisfies recourse for an automated decision.
- [ ] D. Recourse is a path by which an affected person reaches a human, contests a decision and obtains a remedy.
- [ ] E. A contest route preserves the inputs, the output and the record of the decision for the reviewer.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: Different harms need different remedies.
- B: Such a reviewer has a conflict of interest.
- C: It names no reviewer, deadline or remedy.
- D: It has a route, a reviewer and an outcome.
- E: A reviewer cannot judge what was not kept.

**Source:** Recourse, contest and remedy

## MA-ch14.28

A published AI-written summary turns out to be wrong. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Copies outside the team's control are recorded as open rather than assumed fixed.
- [ ] B. An incident record states what happened, what was fixed and what remains open.
- [ ] C. Correction is complete once the primary page is fixed.
- [ ] D. Copies in systems the team controls are located and corrected.
- [ ] E. Pausing publication of affected summaries is an early step, because it stops further spread.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Unreached copies remain unknown.
- B: The record keeps open items visible after the correction.
- C: Copies and derivatives may still carry the error.
- D: A correction applies to every copy the team can reach.
- E: Containment comes before cleanup.

**Source:** Correction sequence

## MA-ch14.29

A vendor says "a human is in the loop" for a system producing hundreds of decisions an hour. One reviewer clicks Approve on each item, with no time budget per item, no authority to reject beyond choosing another button, and no record of the decision. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reviewer count smaller than the volume still satisfies a policy that each item be reviewed.
- [ ] B. A person clicking Approve on each item is meaningful oversight.
- [ ] C. The statement "a human is in the loop" says by itself how well the loop works.
- [ ] D. Meaningful review specifies time per item, authority to change or reject, and a record of the decision.
- [ ] E. A reviewer who can approve but has no real authority to reject gives oversight in name rather than in fact.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: Review capacity below volume means the policy is not being met.
- B: Volume and lack of authority turn the click into a formality.
- C: It names a role without describing time, authority or evidence.
- D: These details make the human step real and checkable.
- E: Oversight needs power to change the outcome.

**Source:** Meaningful human review vs rubber stamp

## MA-ch14.30

A coding agent can read files, run shell commands and call external services in developers' environments. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Text in a file or web page the agent reads is untrusted input and can carry instructions aimed at the agent, known as prompt injection.
- [ ] B. Giving the agent write access to a customer system reduces the chance of e-mailing errors.
- [ ] C. A permission rule and an approval gate are the same mechanism.
- [ ] D. Least privilege means giving the agent broad permissions so tasks do not stall.
- [ ] E. An approval gate that pauses for a person before an external write narrows the action surface.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Content read by the agent is data, not an instruction from its principal.
- B: More write access widens the action surface.
- C: A permission decides what is allowed; an approval gate asks a person at the moment of action.
- D: Least privilege grants the narrowest permissions the task requires.
- E: A human yes sits between the agent and the consequence.

**Source:** Least privilege, approval gate, prompt injection

## MA-ch14.31

A team lead signs off on a governance record. One draft sign-off says "Reviewed and found safe, ethical and compliant." Another lists what was checked and how, what was not checked, and what is not claimed. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Withholding a signature can be the right result when an accepted owner or needed evidence is missing.
- [ ] B. A script's output counts as a signature on the record.
- [ ] C. A sign-off is an act by a named person who accepts responsibility.
- [ ] D. A sign-off stating "safe, ethical and compliant" is stronger than one that lists its limits.
- [ ] E. An honest sign-off names what was not checked.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: A signature is a claim, so it is withheld when the claim is unsupported.
- B: Sign-off belongs to a person who can be held to it.
- C: It is not an output a script produces.
- D: It overstates what a review can establish.
- E: The unchecked part tells the reader what remains open.

**Source:** Honest sign-off

## MA-ch14.32

A governance register can be a document or wired into the system, so that updating a record can pause execution, revoke an approval or shorten retention. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A document register enforces its entries on the running system.
- [ ] B. A document register stays in step with the system without anyone updating it.
- [ ] C. A register wired as a control plane changes system behavior when a record changes.
- [ ] D. Editing a retention field in a document register shortens retention in the running system.
- [ ] E. A control-plane register removes the need for a named owner.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: A document describes the system and changes nothing by itself.
- B: It drifts out of date unless people maintain it.
- C: Entries act as controls rather than descriptions.
- D: The system changes only if it reads the record.
- E: Someone still has to be accountable for the entries.

**Source:** Control plane vs documentation

## MA-ch14.33

An AI-assisted workflow publishes a wrong figure. The reporting user, the content owner, the drafting-tool vendor, the model provider and the institution that supplied the data each made choices that mattered. The team records a decision note. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A decision note records the evidence behind a recommendation and whose interests the change serves or disadvantages.
- [ ] B. Blaming the model provider moves accountability away from the deploying team.
- [ ] C. The deploying organization keeps a named accountable person even when vendors and providers shared in the choices.
- [ ] D. A decision note separates what the model proposed from what a person added or corrected.
- [ ] E. A decision note written by a model shows that a person reviewed it.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Evidence and affected interests let a reader judge the decision.
- B: Shared choices do not remove the deploying organization's accountability.
- C: Distributed causes do not mean distributed answerability.
- D: Separating them shows where human judgment entered.
- E: Review is shown by a named person and what they changed.

**Source:** Decision note and shared responsibility

## MA-ch14.34

A policy says customer records are deleted "30 days after the case is created", and a separate policy forbids pasting customer data into public chatbots. Staff are rewarded for speed and those who raise concerns are called obstructive. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A policy that staff ignore because they are rewarded for speed shows a gap between policy and practice.
- [ ] B. The chatbot rule is enforced by the policy text without changes to incentives.
- [ ] C. "Retention: 30 days" is ambiguous without a stated start event.
- [ ] D. Counting from creation and counting from last use give the same deletion date for a record used after it was created.
- [ ] E. The event that starts the retention clock, such as creation or last use, needs to be stated for the number to mean anything.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Incentives decide whether policy is followed.
- B: Rewards and penalties push behavior against the rule.
- C: Two reasonable readings give different deadlines.
- D: The later start event gives a later date.
- E: Without a start event, "30 days" is ambiguous.

**Source:** Retention clock; policy-practice gap

## MA-ch14.35

A developer asks an assistant to critique a register entry without rewriting it. Several candidate prompts are proposed. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Check whether our register is compliant" is a question a read of the text can settle.
- [ ] B. "List each field that names a group instead of a person" is a precise instruction.
- [ ] C. "Tell me if the governance looks fine" is vague because it names no criteria.
- [ ] D. "List each threshold that has no observable signal" is a precise instruction.
- [ ] E. Telling the assistant to "make it better" keeps it in a critique role.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: Compliance is a legal and institutional determination.
- B: It names the exact defect to find.
- C: The assistant has no test to apply.
- D: It names a checkable defect.
- E: That asks it to author a rewrite.

**Source:** Precise critique prompts

## MA-ch14.36

A team builds a summarizer that reads notes written by instructors and students, shows summaries on a portal, and routes corrections through a volunteer maintainer. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A stakeholder concern is handled by recording it and then either changing the plan or stating why it did not change.
- [ ] B. A stakeholder is a person or group affected by the workflow or able to influence it.
- [ ] C. The volunteer maintainer is affected by a correction route that adds work.
- [ ] D. Authors whose notes are summarized are affected even if they do not use the portal.
- [ ] E. The affected group is the same as the set of direct users.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: This keeps consultation traceable.
- B: The term covers more than direct users.
- C: Recourse design creates burdens that fall on people.
- D: Their words are processed and shown.
- E: Indirect parties are also affected.

**Source:** Stakeholders and affected parties
