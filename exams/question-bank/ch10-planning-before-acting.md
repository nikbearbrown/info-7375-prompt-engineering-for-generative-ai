# Chapter 10: Planning before acting

## MA-ch10.1

A planning template for an AI agent has eight named fields: objective, inputs, scope, steps, tools, risks, verification and stop. Each field answers one question. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The verification field names the observation that would show the objective was met.
- [ ] B. The scope field states what may change and what stays untouched.
- [ ] C. The inputs field says what the work is trying to achieve.
- [ ] D. The risks field says how the plan could fail and ties each failure to a response.
- [ ] E. The stop field lists the capabilities the agent may call.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Verification is the evidence plan for the objective.
- B: Scope is the boundary of permitted change.
- C: The objective field states the aim; inputs name the material the work starts from.
- D: Risks name failure modes together with mitigation, owner or trigger.
- E: Capabilities are listed in the tools field; stop defines the exits.

**Source:** The eight plan fields

## MA-ch10.2

A team checks a proposed agent plan with a function that reports a field as missing when `plan.get(field)` is falsy. They run it on a plan in which all eight fields are present and each value is the string "x". Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The check is a semantic review of the plan.
- [ ] B. A pass rate of this check over many plans measures plan quality.
- [ ] C. The empty result shows the plan is ready for approval.
- [ ] D. A reviewer could still judge each field meaningless, because presence differs from meaning.
- [ ] E. The function returns an empty list, which is correct for the rule it implements.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: A truthiness check looks at presence, not meaning.
- B: It measures structural completeness, not quality.
- C: The function checks that values are truthy, which says nothing about readiness.
- D: Structural completeness is a different property from semantic adequacy.
- E: A nonempty string is truthy, so no field is reported missing.

**Source:** Structural completeness versus semantic review

## MA-ch10.3

In Python, a plan-checker reports a field as missing when `not plan.get(field)` is true. It is run on `{"inputs": [], "scope": 0, "steps": ["inspect"], "tools": None, "risks": " "}`. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "steps" is reported missing, because the list has a single entry.
- [ ] B. "scope" is reported missing, because the integer zero is falsy.
- [ ] C. "tools" is reported missing even though the key is present.
- [ ] D. "inputs" is reported missing, because an empty list is falsy.
- [ ] E. "risks" is reported missing, because it holds a single space.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A nonempty list is truthy regardless of its length.
- B: Zero evaluates as false, showing that truthiness can misjudge a legitimate value.
- C: None is falsy, so a present key with value None counts as missing under this rule.
- D: An empty list evaluates as false in a boolean test.
- E: A string containing a space is nonempty and so truthy.

**Source:** Truthy versus falsy values

## MA-ch10.4

A support assistant must reply in JSON of the form {"answer": string, "confidence": number between 0 and 1}. A schema validator checks that the reply parses and has both keys with the right types. The refund window in the company policy is 30 days. The assistant replies {"answer": "Our refund window is 90 days.", "confidence": 0.97}. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Schema validation and a comparison against the policy text test the same property.
- [ ] B. The reply passes schema validation.
- [ ] C. The confidence of 0.97 is evidence that the answer is grounded in the policy.
- [ ] D. The pass rate of the validator over many replies measures factual accuracy.
- [ ] E. Adding a range rule for confidence would catch the wrong refund window.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: Validation tests form; comparison with a source tests grounding.
- B: It parses, has both keys and has the right types.
- C: A self-reported confidence number is not a grounding check.
- D: A schema validator measures structure; a well-formed reply can state a false fact.
- E: A range rule constrains a number and says nothing about the answer text.

**Source:** Schema validation versus grounding

## MA-ch10.5

A plan for an agent that fixes a bug lists these steps: read source files, run the test suite, write a report. Its tools field lists a shell with write access and network access. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Because the steps read files and run tests, the extra capability in tools is harmless.
- [ ] B. Narrowing tools to file reading and test execution would match capability to the steps.
- [ ] C. The scope field and the tools field are two names for the same thing.
- [ ] D. The tools entry grants more capability than the steps use, which a reviewer can challenge.
- [ ] E. A presence check on the fields would flag the mismatch.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: A granted capability exists whether or not the steps use it.
- B: Least capability keeps the tools field consistent with the steps.
- C: Scope bounds what may change; tools names what the agent may call.
- D: Tools should name the capability needed, and write plus network access go beyond reading and testing.
- E: A presence check does not compare fields with each other; a cross-field review does.

**Source:** Tools field versus scope field

## MA-ch10.6

A plan states the objective "restore correct rounding in the invoice-total function". Its verification entry is the shell command `ls tests/`. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A sound verification entry names an observation that would differ if the objective failed.
- [ ] B. A rule requiring verification to be a shell command settles whether it tests the right claim.
- [ ] C. A successful directory listing shows that the rounding is correct.
- [ ] D. The entry tests a proxy at best, because it observes nothing about rounding.
- [ ] E. The entry passes review because a command is present.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Verification should be able to show failure of the stated objective.
- B: Whether a command tests the claim is a semantic judgment, not a format rule.
- C: Listing a directory runs no test and observes no rounding behavior.
- D: A proxy is a stand-in observation that does not measure the claim.
- E: A command in the field satisfies structure but not purpose.

**Source:** Verification versus proxy

## MA-ch10.7

A plan's stop field is supposed to define three exits: completion, halt and defer. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "The scoped tests pass and the named reviewer accepts the diff" is a completion condition.
- [ ] B. "The turn budget is exhausted with two scoped tests still failing" is a completion condition.
- [ ] C. A defer exit pauses the work and passes the decision to a named owner.
- [ ] D. "Stop when it looks good" is an observable completion condition.
- [ ] E. "The next command would write outside the permitted directory" is a halt condition.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: It names observations and an accountable person.
- B: Exhausting a budget with failures is an incomplete exit, not completion.
- C: Deferring leaves the decision with someone accountable instead of continuing or fabricating a finish.
- D: It names no observation that a second person could apply.
- E: A halt stops the run because continuing would cross a boundary.

**Source:** Completion, halt and defer

## MA-ch10.8

An agent run has a maximum of 30 turns and a separate finish action that the agent can call. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reaching the turn limit means the task is done.
- [ ] B. Finishing before the turn limit shows the work is correct.
- [ ] C. Reaching the limit should produce an incomplete status with partial artifacts preserved.
- [ ] D. At the limit the agent should write a final result so the record looks complete.
- [ ] E. A turn limit bounds how much effort is allowed, while a finish action signals that the agent considers the task complete.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: A limit bounds effort; it does not signal completion.
- B: Calling finish records the agent's judgment, which still needs evidence.
- C: An honest stop reports the state of the work instead of a made-up result.
- D: Fabricating a final result misreports the run.
- E: They answer different questions.

**Source:** Turn limit versus finish action

## MA-ch10.9

A team adds refusal paths to an agent's plan. A refusal here means that the workflow preserves its state and reports what blocks the next transition. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A good refusal report says why the step stopped, what evidence was available and what decision would allow safe resumption.
- [ ] B. When a source does not support a claim, filling the field with plausible wording counts as a valid refusal.
- [ ] C. Shrinking a claim or marking it unresolved is an acceptable alternative to inventing support.
- [ ] D. Refusal paths cover missing authority, unavailable evidence, out-of-scope changes and failed checks.
- [ ] E. An unexplained halt is hard to tell apart from a crashed workflow.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: The report lets a person decide the next move.
- B: Plausible filler is the opposite of a refusal; it hides the gap.
- C: Reporting what the evidence supports keeps the record honest.
- D: Each is a condition under which a transition should not proceed.
- E: A refusal must carry its reason to be distinguishable from a failure.

**Source:** Refusal path

## MA-ch10.10

An agent runs the same failing test command three times, with no change to the code, the inputs or its hypothesis, and gets the same failure each time. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The reruns added no new evidence.
- [ ] B. The number of reruns is a measure of progress.
- [ ] C. A cap on retries is evidence that the task succeeded.
- [ ] D. A better next move is to diagnose the cause, revise the plan or defer.
- [ ] E. A deterministic failure is expected to pass on a further rerun.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Progress means a change in the evidence or in the decision state.
- B: Activity is not progress when nothing changes.
- C: A retry cap is a resource bound, not a success signal.
- D: Each changes the evidence or the decision state.
- E: The same inputs produce the same failure.

**Source:** Progress and retry bounds

## MA-ch10.11

A team treats a plan as a set of predictions and the executed result as a record of what happened. Before running anything, they write down the expected observations. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A plan is a description of what has already happened.
- [ ] B. Writing down what a wrong outcome would look like lets the result refute the plan.
- [ ] C. A prediction written after seeing the result is as informative as one written before.
- [ ] D. The executed result is the record of what happened.
- [ ] E. Comparing prediction with record is how a surprise is noticed.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: A plan is written before action and predicts.
- B: A prediction that names its own failure can be tested.
- C: A prediction made afterward can be fitted to the outcome.
- D: Prediction and record are separate artifacts.
- E: A surprise is a gap between what was expected and what was observed.

**Source:** Plan as prediction, result as record

## MA-ch10.12

A developer asks a coding agent to propose a plan for a refactor and states that no file may be changed yet. The agent returns a plan whose last line reads "Approved by reviewer." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A fluent justification in the plan is evidence that the plan is sound.
- [ ] B. The returned plan is a proposal.
- [ ] C. Approval is an act by an accountable person, not a property of text the model returns.
- [ ] D. The line "Approved by reviewer" records an approval.
- [ ] E. Asking for a plan with no edits authorizes the plan for execution.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Fluency says little about whether the commitments are correct or safe.
- B: A proposal awaits a decision by a person.
- C: Approval attaches to a person and a decision.
- D: Text written by the model cannot record that a person approved anything.
- E: Requesting a proposal and authorizing it are separate acts.

**Source:** Proposal versus approval

## MA-ch10.13

An LLM application team compares two designs. In a plan-and-execute design, a planner writes a full list of steps first and an executor then runs them. In an adaptive design, the model chooses each next action after seeing the previous observation. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In a workflow the model decides dynamically which tools to call, while in an agent the code paths are predefined.
- [ ] B. In an adaptive loop each observation can change the next action.
- [ ] C. A fixed, predictable sequence of steps favors a predefined workflow over open-ended model-directed choice.
- [ ] D. Plan-and-execute removes the need to check results between steps.
- [ ] E. A plan written up front can be inspected by a person before action is taken.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: The definitions are reversed: a workflow follows predefined code paths and an agent directs its own process.
- B: The model reacts to the observation instead of following a fixed list.
- C: When the path is known, a fixed sequence is simpler and more predictable.
- D: An early failure can invalidate later steps, so results still need checking.
- E: Inspectability before action is the main benefit of an explicit plan.

**Source:** Workflow, agent and plan-and-execute

## MA-ch10.14

A reviewer auditing a diff from a coding agent sees that the code rounds prices using one particular rounding mode. The requirements never said how to round. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The gap should be logged, the requirement reopened and the plan updated with the reason.
- [ ] B. The code should be left as it is because the choice is already implemented.
- [ ] C. A decision the agent made implicitly is hard to challenge because it was not written down.
- [ ] D. The revised plan is a new version and needs its own review.
- [ ] E. The episode shows that planning before acting is pointless because requirements change.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: A missing requirement is a decision that was never made, and recording it keeps the design history honest.
- B: An unrecorded implicit decision stays hidden and may be wrong.
- C: Unwritten decisions are not available for review.
- D: A change to the plan is a new commitment.
- E: A reviewed first plan is what makes visible which decision the new evidence reopens.

**Source:** Replanning on new evidence

## MA-ch10.15

Midway through a task, an agent reports that fixing the bug properly requires editing a file outside the plan's declared scope. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The plan should be revised and the expansion approved before the edit.
- [ ] B. Describing the edit as an implementation detail of an in-scope step is an appropriate way to proceed.
- [ ] C. Logging a warning while the edit proceeds is a sound design.
- [ ] D. The scope field is advisory, so the agent may override it when it judges the change helpful.
- [ ] E. A request to leave the declared scope is a reason to halt or defer for a decision.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Scope is a boundary; widening it is a change of commitment that needs approval.
- B: Relabeling an out-of-scope change hides it from review.
- C: A warning after the fact does not prevent the out-of-scope change.
- D: A scope field that the agent can override does not bound anything.
- E: It is a boundary crossing, which belongs among the halt or defer conditions.

**Source:** Scope as a boundary

## MA-ch10.16

A data team spends a quarter building a very accurate model that predicts which customers will open a marketing email. The business actually needed to know which customers are about to cancel their subscriptions. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Raising the model's accuracy further would remove the problem.
- [ ] B. This is an error of the third kind: a right answer to the wrong problem.
- [ ] C. Checking the finished result against the framing it already assumes is a weak test of whether the framing was right.
- [ ] D. This is a Type II error, a false negative.
- [ ] E. This is a Type I error, rejecting a true null hypothesis.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Accuracy on the wrong target is irrelevant to the need.
- B: The error lies in the formulation of the problem, not in the solution.
- C: An audit sharing the framing's assumptions cannot reveal that the framing is off.
- D: A Type II error is failing to reject a false null hypothesis within a given problem.
- E: A Type I error is a false positive inside a given test, not a wrong choice of problem.

**Source:** Formulation and the error of the third kind

## MA-ch10.17

A developer asks an LLM to frame a problem before writing down any framing of their own. Design researchers call an early, often unstated idea of what a problem is really about a primary generator. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Writing candidate framings first keeps a basis for judging the model's framing independently.
- [ ] B. Naming a framing explicitly makes it available for challenge.
- [ ] C. A primary generator shapes which solutions look natural to the designer.
- [ ] D. The model's framing can become the developer's anchor by default.
- [ ] E. A developer can avoid having a primary generator by staying neutral.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Having one's own candidates gives something to compare against.
- B: An unstated framing cannot be questioned.
- C: Whatever the first framing is, it narrows the solutions that are visible.
- D: The first framing named tends to set the reference point.
- E: Some first idea of the problem forms regardless; the choice is whether to name it.

**Source:** Primary generator and anchoring

## MA-ch10.18

A team has written several candidate formulations of a problem and is writing the criteria for choosing among them. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. If the criteria concern cost, time and feasibility alone, the process tends to pick the most tractable formulation.
- [ ] B. The criteria are set before a candidate is scored.
- [ ] C. A salience criterion asks whether solving the problem addresses what matters in this context.
- [ ] D. A model can propose candidate criteria while the team owns the final ones.
- [ ] E. Criteria written after the scores are known are better because they reflect what was learned.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Feasibility-only scoring rewards what is easy to build or measure.
- B: Criteria chosen after the scores can be bent toward a preferred option.
- C: Salience brings importance into the comparison.
- D: Drafting can be delegated; the criteria encode what the team values.
- E: Criteria written afterward let the outcome shape the standard meant to judge it.

**Source:** Formulation criteria and salience

## MA-ch10.19

An engineer writes preconditions, postconditions and invariants for a function and then asks a coding agent to write the implementation. Tests are derived from the written contract, not from the agent's code. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Tests derived from the contract stay independent of the agent's assumptions.
- [ ] B. The agent's statement that the contract holds is evidence that it holds.
- [ ] C. Writing the contract first fixes boundary decisions while they are cheap to change.
- [ ] D. A precondition is what is required to hold before the function runs, and a postcondition is what holds afterward.
- [ ] E. Tests derived from the agent's own implementation are as independent as tests derived from the contract.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: The contract is an external reference.
- B: A claim of compliance is not evidence; the tests are.
- C: The decisions precede the code.
- D: Pre- and postconditions bracket the call.
- E: Tests built from the implementation encode its mistakes.

**Source:** Contract: preconditions, postconditions, invariants

## MA-ch10.20

In a plan, the step "verify" declares that it comes after the step "build". The steps are drawn as a directed graph. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. build is a prerequisite of verify.
- [ ] B. The edge in the graph runs from build to verify.
- [ ] C. verify may start before build finishes if that is faster.
- [ ] D. The edge from build to verify is the place to attach an evidence condition for the handoff.
- [ ] E. A dependency is a directed obligation: verify requiring build does not mean build requires verify.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A prerequisite is a step that must be done first.
- B: Edges point from a prerequisite to the step that depends on it.
- C: The declared dependency forbids starting verify first.
- D: Evidence belongs on the edges where work passes between steps.
- E: The relation has a direction.

**Source:** Dependency, prerequisite and edge

## MA-ch10.21

A build plan has four steps. Lint and test have no prerequisites. Build requires both lint and test. Deploy requires build. Check each statement that is a valid topological order of the steps. Each statement is worth 1 point (5 points total).

- [ ] A. build, lint, test, deploy
- [ ] B. deploy, build, lint, test
- [ ] C. lint, build, test, deploy
- [ ] D. test, lint, deploy, build
- [ ] E. lint, test, build, deploy

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: Build would run before the lint and test steps it requires.
- B: The order is reversed, so every step precedes its prerequisites.
- C: Build would run before test, one of its prerequisites.
- D: Deploy would run before build, its prerequisite.
- E: Each step appears after all of its prerequisites.

**Source:** Topological order

## MA-ch10.22

In a plan graph, the steps migrate_schema and seed_test_data declare no dependency on each other, so they become ready in the same batch. Both write to the same database. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Being ready in the same batch means no declared dependency links the two steps.
- [ ] B. Adding an edge between the two steps would put them in sequence.
- [ ] C. The ordering function detects shared writes by examining the steps.
- [ ] D. The absence of a declared dependency proves that the two steps can run at the same time safely.
- [ ] E. A shared database is a hidden dependency that the graph does not represent.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: A batch collects steps whose declared prerequisites are done.
- B: A declared dependency orders the steps.
- C: Ordering uses declared prerequisites only.
- D: A shared resource can make them conflict.
- E: The graph encodes only what was declared.

**Source:** Ready batch and hidden dependency

## MA-ch10.23

A function orders plan steps by their declared prerequisites and raises ValueError in three situations. Input 1 has two steps that both have the id "test". Input 2 is the single step {"id": "verify", "after": ["test"]} and no step named "test". Input 3 is {"id": "a", "after": ["b"]} and {"id": "b", "after": ["a"]}. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Input 2 is a dependency cycle.
- [ ] B. Input 1 is a duplicate-id error.
- [ ] C. Input 3 is a dependency cycle, so no step can become ready first.
- [ ] D. Input 2 is an unknown-prerequisite error.
- [ ] E. Sorting the ids alphabetically would resolve Input 3.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A cycle needs steps that depend on each other, directly or through a chain.
- B: Two steps share one identifier, so a prerequisite reference is ambiguous.
- C: Each step waits for the other.
- D: The reference points to a step that does not exist.
- E: A cycle is a property of the dependencies, not of the id order.

**Source:** Duplicate id, unknown prerequisite and cycle

## MA-ch10.24

A plan declares three steps with no prerequisites: analyze, load and archive. In the real world, analyze needs the file that load produces. A function orders the steps by sorted id within each batch of ready steps and returns analyze, archive, load without error. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reviewer comparing each step's description with the declared prerequisites can find the omission.
- [ ] B. The ordering succeeds because the graph has no cycle.
- [ ] C. The plan omits a real dependency of analyze on load, and the graph encodes the declared prerequisites alone.
- [ ] D. The successful ordering shows the plan is correct.
- [ ] E. A cycle check would detect the omitted dependency.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Finding a missing dependency needs a semantic comparison.
- B: An acyclic graph can always be ordered.
- C: A missing edge is a defect the ordering cannot see.
- D: Acyclic does not mean executable; the order may violate a real dependency.
- E: A cycle check finds loops, not absent edges.

**Source:** Acyclic does not mean executable

## MA-ch10.25

A team writes handoff conditions for a pipeline. A condition is testable when someone who did not build the pipeline can read it, observe the system and decide whether it holds. Check each condition that is testable in that sense. Each statement is worth 1 point (5 points total).

- [ ] A. Each claim in the draft is paired with the name of the source document it came from.
- [ ] B. Each figure in the draft appears in the supplied source table with the same value.
- [ ] C. The draft looks reasonable.
- [ ] D. The exit status of the test command is 0.
- [ ] E. The diff touches no file outside the scoped directory.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A stranger can open the source and check the pairing.
- B: It names an observable comparison with a defined outcome.
- C: Different reviewers would apply this differently.
- D: A stranger can run the command and read the status.
- E: A stranger can list the changed files and compare them with the directory.

**Source:** Testable handoff conditions

## MA-ch10.26

A coding agent finishes a task and writes, "I ran the tests and they pass." A team is deciding what counts as evidence for moving the work to review. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A description of the tests as passing is as strong as a recorded exit status.
- [ ] B. A test failure can be waved through if the agent explains why it does not matter.
- [ ] C. The sentence is evidence because the agent states it confidently.
- [ ] D. The agent's summary of the output replaces the command output.
- [ ] E. The sentence is a claim, not evidence.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: A recorded exit status is an observation; a description is a report of one.
- B: An explanation does not satisfy the handoff condition.
- C: Confident wording is not an observation.
- D: A summary is the agent's description and can differ from what was produced.
- E: A claim reports what the agent says happened; evidence is something a reviewer can inspect.

**Source:** Claim versus evidence

## MA-ch10.27

A plan defines a handoff from a test-run step to a review step. The condition is that the targeted test passes, and the recorded test run shows a failure. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The work proceeds to review and the failure is noted there.
- [ ] B. A failure route is the planned next transition when an edge condition fails.
- [ ] C. The agent's assertion that the test passes can satisfy the condition in place of the record.
- [ ] D. The handoff condition is not met.
- [ ] E. The failing test shows that the plan graph contains a cycle.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: A failed condition blocks the transition.
- B: Examples are repair, halt or defer.
- C: The condition refers to the recorded run, not to an assertion.
- D: The evidence condition for the edge is unsatisfied.
- E: A test failure concerns the work, not the dependency structure.

**Source:** Evidence condition and failure route

## MA-ch10.28

Handoff conditions differ in who can apply them. Condition 1 is "the exit status of the test command is 0". Condition 2 is "the cited regulatory clause actually governs the proposed change". Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Condition 2 needs a qualified person to judge it.
- [ ] B. Naming who applies each condition is part of making the handoff testable.
- [ ] C. Condition 2 should be dropped from the plan because it needs human judgment.
- [ ] D. Condition 2 is as mechanical as Condition 1 once the clause is cited.
- [ ] E. Condition 1 can be applied by a machine.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: Whether a clause governs a change is an interpretation.
- B: A condition with no applicant is not applied.
- C: Human judgment is a legitimate evidence condition when an accountable owner is named.
- D: Citing a clause does not decide whether it governs.
- E: It is a mechanical check of a value.

**Source:** Machine-applied versus judgment-applied conditions

## MA-ch10.29

A reviewer ends a plan review with a written sign-off whose lines state what was checked, how it was checked, what was not checked, what is not claimed, and whether the reviewer signs or withholds. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A fluent sign-off drafted by a model is as good as one written from the reviewer's own record.
- [ ] B. The line on what was not checked shows the limits of the sign-off.
- [ ] C. A sign-off on a plan claims less than a sign-off on a result: the plan survived the described review, not that the work succeeded.
- [ ] D. Withholding a signature is an honest outcome when the evidence does not support signing.
- [ ] E. A sign-off states what is not claimed, which keeps it within the review that was done.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: A sign-off is only worth what the reviewer's record supports.
- B: Stating the gaps keeps the sign-off from overclaiming.
- C: A plan review concerns the proposal, not the outcome.
- D: A sign-off that cannot be given should not be given.
- E: Stated non-claims prevent the signature from being read as a broader assurance.

**Source:** Sign-off

## MA-ch10.30

A reviewer, before approving a plan, imagines for each important field a plan that satisfies the field's wording but fails its purpose, and also asks an AI assistant for counterexamples to the plan. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A counterexample that slips through shows the field's entry needs tightening.
- [ ] B. An assistant can generate candidate counterexamples, but the reviewer judges whether each one is real.
- [ ] C. If the assistant finds no counterexample, the plan is shown to be sound.
- [ ] D. A plan that meets the wording but fails the purpose is a counterexample to that wording.
- [ ] E. Counterexample review replaces the structural presence check.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: The entry should be reworded so that the counterexample fails.
- B: Generating and judging are separate steps.
- C: Finding none shows only that none was found.
- D: A counterexample shows the field is too loosely worded.
- E: They test different things and both have a place.

**Source:** Counterexample review

## MA-ch10.31

A developer tells Claude Code: "Quickly fix the login bug, touch whatever you need, and tell me when it is done." Check each statement that correctly identifies a problem with the wording. Each statement is worth 1 point (5 points total).

- [ ] A. The prompt asks for a plan to be reviewed before editing.
- [ ] B. "tell me when it is done" gives no observable stop condition.
- [ ] C. "fix the login bug" supplies a verification command.
- [ ] D. "Quickly" specifies a turn budget.
- [ ] E. "touch whatever you need" leaves the scope undefined.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: The prompt asks for the fix directly.
- B: Done is defined by the agent's judgment rather than by an observation.
- C: It names a goal and no observation that would confirm it.
- D: A budget is a stated limit, not a vague adverb.
- E: A scope names what may change and what stays untouched.

**Source:** Spotting imprecise wording in a prompt

## MA-ch10.32

A developer wants Claude Code to plan before acting on a refactor. Check each prompt that uses exact terms for that purpose. Each statement is worth 1 point (5 points total).

- [ ] A. "Write a plan that sounds confident and mark it approved so we can save time."
- [ ] B. "Plan carefully in your head and show me the finished work."
- [ ] C. "Propose a plan with objective, scope, steps, tools, risks, verification and stop. Do not modify files until I approve."
- [ ] D. "Think hard about it, make a good plan and then go ahead and do it."
- [ ] E. "Make a plan with as many steps as possible so it is thorough."

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: Approval is an act by a person, not text.
- B: A private plan cannot be reviewed before action.
- C: It names the fields and the approval gate.
- D: This lets the agent proceed without review.
- E: Step count is not a field of the plan and does not make it reviewable.

**Source:** Best prompt to plan before acting

## MA-ch10.33

In Claude Code, plan mode has the model read and analyze the project and present a plan for the user to approve before it edits files. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The plan presented is a proposal until the user approves it.
- [ ] B. Permission to run a tool is the same thing as approval of the plan.
- [ ] C. A tool permission prompt asks whether one action may run, while an approval gate asks whether a reviewed plan or result may advance.
- [ ] D. Plan mode is the same as a mode that accepts edits automatically.
- [ ] E. The user's approval of the plan is an approval gate.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Approval is a separate act.
- B: Permitting a tool call does not approve the plan.
- C: They check different things at different levels.
- D: Plan mode withholds edits until approval.
- E: A gate is a point where work waits for a person's decision.

**Source:** Plan mode, permission and approval gate

## MA-ch10.34

A plan's risks field reads "data loss; wrong output; cost overrun", with no mitigation, owner or trigger given for any item. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A risk is stronger when it is tied to a mitigation, an owner or a stop trigger.
- [ ] B. The risks field is adequate when it is short.
- [ ] C. A risk with a trigger can be turned into a halt condition in the stop field.
- [ ] D. A risks entry names how the plan could fail, while the verification entry names how success is observed.
- [ ] E. A bare list of risk names fills the field without being concretely challengeable.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: The tie makes the entry something a reviewer can challenge.
- B: Length says nothing about whether the entries can be challenged.
- C: The trigger links risks to the exits.
- D: The two fields answer different questions.
- E: A reviewer cannot dispute "data loss" without a stated cause or response.

**Source:** Risks field

## MA-ch10.35

A developer decides which parts of a plan to hand to an AI assistant for a first draft that the developer then reviews, and which parts to answer personally. Check each statement that describes a part reasonable to hand over for a first draft. Each statement is worth 1 point (5 points total).

- [ ] A. Making the final selection among the formulations.
- [ ] B. Writing several candidate formulations of the problem.
- [ ] C. Signing off on the plan.
- [ ] D. Deciding whether the plan is approved for execution.
- [ ] E. Proposing candidate criteria for choosing among the formulations.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: The selection encodes what the team values and the team answers for it.
- B: Generating candidates is drafting work that a person then compares.
- C: A sign-off is an act of an accountable person.
- D: Approval is a decision by a person, not a draft.
- E: Criteria can be drafted by a model and owned by the team.

**Source:** What to delegate and what to own

## MA-ch10.36

A plan's steps include "read the customer table and compute churn rates". The customer table contains personal data. The inputs field lists only the source files of the analysis code, and the scope field excludes personal data. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reordering the steps resolves the contradiction.
- [ ] B. The data that the steps read is missing from the inputs field.
- [ ] C. The steps contradict the scope, because reading the table touches excluded data.
- [ ] D. A presence check on the eight fields would flag the problem.
- [ ] E. An inputs field that lists filenames is adequate without provenance or version.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: The contradiction is between the fields, not in the order.
- B: The inputs field should name what the work starts from.
- C: A cross-field review compares fields with one another.
- D: Each field is present and nonempty.
- E: Provenance and version tell a reviewer what exactly the work depends on.

**Source:** Cross-field review
