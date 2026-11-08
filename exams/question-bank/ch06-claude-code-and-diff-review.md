# Chapter 6: Claude Code and diff review

## MA-ch06.1

A bug report says, "the shipping cost is wrong." An engineer wants to hand a bounded task to a coding agent such as Claude Code. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A reproduction shows how to trigger a failure, while a diagnosis explains its cause.
- [ ] B. A reproduction states the input, the observed output and the expected output.
- [ ] C. A bounded task names the files that may change, which is the scope.
- [ ] D. The report as written is a sufficient task because the agent can infer the expected value.
- [ ] E. Writing down the expected output turns the report into something a regression test can check.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: These are two different artifacts.
- B: These three facts let anyone, human or agent, trigger and recognise the failure.
- C: Scope is the set of files or areas the agent is allowed to touch.
- D: The expected value is not stated, so the agent would be guessing.
- E: A regression test needs an input and an expected output to assert.

**Source:** Reproduction, diagnosis and task framing

## MA-ch06.2

In one session a coding agent writes a bug fix and also writes the regression test for that fix. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The fix and its test can share the same misreading of the requirement, so their agreement is weak evidence.
- [ ] B. A pass from this test is as strong as a pass from a test a person wrote earlier from the written requirement.
- [ ] C. Rerunning the same test a second time restores independence between the fix and its check.
- [ ] D. Writing the test from the requirement and committing it before asking for a plan restores independence.
- [ ] E. Having a different session or a person write the test is a way to separate the code from its check.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: Shared assumptions mean the test is not an independent check.
- B: The earlier test was fixed before the patch could influence it.
- C: Repeating a run does not change who wrote the test or from what.
- D: A test fixed in advance cannot be shaped to fit the patch.
- E: Separate authorship gives the check a different set of assumptions.

**Source:** Independence of test and patch

## MA-ch06.3

A developer writes a new regression test for a reported bug and runs it against the unfixed code before any patch exists. The test passes. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The result confirms that the bug is already fixed.
- [ ] B. A useful regression test fails on the unfixed code and passes after the fix.
- [ ] C. The test is ready to guard the patch and should be kept unchanged.
- [ ] D. A wrong input or a wrong assertion in the test could explain the pass.
- [ ] E. The test does not yet reproduce the bug, so it does not yet serve as a regression test for it.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: A pass on the unfixed code more likely means the test does not capture the bug.
- B: Failing first shows the test can detect the bug.
- C: It does not yet reproduce the failure, so it guards nothing.
- D: Either mistake would make the test miss the bug.
- E: A reproduction triggers the reported failure; this test does not.

**Source:** Regression test that passes before the fix

## MA-ch06.4

A team runs its test suite against 8 mutants of a function. A mutant is a small deliberately wrong variant of the code. The suite fails on 6 mutants and passes on 2. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A mutant that makes the suite fail is said to be killed.
- [ ] B. The two mutants that passed the suite were killed.
- [ ] C. A surviving mutant points to behaviour the tests do not check.
- [ ] D. The 6-of-8 score shows the suite catches 75 percent of real bugs.
- [ ] E. An equivalent mutant behaves the same as the original, so no test could kill it.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Killed means the tests detected the deliberate defect.
- B: Passing mutants survived; they were not detected.
- C: The tests did not notice the changed behaviour.
- D: The score only describes the chosen mutants.
- E: Equivalent mutants survive without exposing a test gap.

**Source:** Mutants, killed and surviving

## MA-ch06.5

A developer asks a coding agent to propose a deliberately wrong implementation that still passes the developer's tests, then checks by hand whether it does. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. If the wrong version passes, the tests have a gap.
- [ ] B. If the wrong version fails the tests, the suite is shown to be complete.
- [ ] C. Keeping a known wrong implementation lets the team test the tests.
- [ ] D. A wrong version that passes shows the agent's real patch is correct.
- [ ] E. A function that returns a constant is a poor example because no test with one assertion can be satisfied by it.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: A suite that accepts a known-wrong version cannot be trusted to reject similar bugs.
- B: One rejected wrong version says little about other wrong versions.
- C: Checks are themselves checked against a case they must reject.
- D: A gap in the tests says nothing in favour of the patch.
- E: A constant matching the single asserted input satisfies such a test.

**Source:** Known wrong implementation

## MA-ch06.6

A coding agent is told to make a failing test pass. Its diff adds `if amount == 100: return 8.0` ahead of the general logic, and it also edits the expected value in a second failing assertion so that the assertion matches the code's output. The suite is now green. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Special-casing the tested input is called hard-coding the expected answer.
- [ ] B. A green suite after these edits shows the underlying logic is now correct.
- [ ] C. Changing an expected value is acceptable when it makes the suite green.
- [ ] D. Editing an assertion to match the output weakens the test instead of fixing the code.
- [ ] E. A reviewer should read the diff of the test files as carefully as the diff of the source files.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: The code returns the answer for that input without implementing the rule.
- B: The suite was made to pass by the edits themselves.
- C: An expected value comes from the requirement, not from the current output.
- D: Weakening the check hides the failure it was reporting.
- E: Agents can change the check as well as the code.

**Source:** Hard-coding and weakening tests

## MA-ch06.7

A reviewer runs a regression suite against a candidate patch and gets a SyntaxError raised from the reviewer's own test file, before any assertion executes. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. This is an error in the test harness, not a failed assertion about the patch.
- [ ] B. The run shows the patch is wrong.
- [ ] C. The run counts as a test failure that rejects the patch.
- [ ] D. The broken run and the repaired rerun both belong in the record.
- [ ] E. The broken run should be deleted so the log looks clean.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: An error stops the run before any check of the patch happens.
- B: No assertion about the patch ran.
- C: A failure is a false assertion; this is an error before assertions.
- D: Keeping both shows what happened and in what order.
- E: Deleting evidence makes the record less honest.

**Source:** Harness error versus test failure

## MA-ch06.8

A team reviews code changes proposed by an AI agent using unified diffs. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In a unified diff, a line starting with a minus sign was removed and a line starting with a plus sign was added.
- [ ] B. Context lines are the lines the patch changed.
- [ ] C. A hunk is a contiguous block of changes together with its surrounding context lines.
- [ ] D. A hunk header beginning with @@ gives the line positions of that block.
- [ ] E. A diff shows the textual change between two versions, not the behaviour that results.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: These prefixes mark deletions and additions.
- B: Context lines are unchanged lines shown around the change.
- C: A diff is a list of hunks per file.
- D: The header says where in each version the block sits.
- E: Behaviour has to be checked by running or reasoning about the code.

**Source:** Unified diff vocabulary

## MA-ch06.9

After an agent session in a git repository, a reviewer runs plain `git diff` and sees changes to two tracked files. During the session the agent also created a new file that was never added to git, and ran `git add` on a third tracked file. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Plain `git diff` does not list the new untracked file.
- [ ] B. Plain `git diff` shows the full set of changes the session made.
- [ ] C. Plain `git diff` compares the working tree with the index, so changes already staged are not shown.
- [ ] D. `git diff --staged` shows changes that have been added to the index.
- [ ] E. `git status` lists untracked files that plain diff omits.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Untracked files are not compared by plain diff.
- B: Staged and untracked changes are missing.
- C: The staged file is already in the index, so it matches the working tree.
- D: It compares the index with the last commit.
- E: Status reports the state of the working tree and index.

**Source:** git diff, index and untracked files

## MA-ch06.10

To cut noise, a reviewer views an AI agent's changes to a Python module with whitespace differences ignored, as with `git diff -w`. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Ignoring whitespace is safe for Python because whitespace there is decorative.
- [ ] B. A hidden indentation change in Python can alter which block a line belongs to and so change behaviour.
- [ ] C. The flag changes the files on disk so the whitespace edits are undone.
- [ ] D. A whitespace-insensitive view helps when reviewing a language in which whitespace carries no meaning.
- [ ] E. The plain view and the whitespace-insensitive view show the same set of changed lines.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Python indentation decides which block a line belongs to.
- B: Indentation is syntax in Python.
- C: It only changes how the diff is displayed.
- D: In such languages hidden whitespace cannot change behaviour.
- E: The second view hides lines that differ only in whitespace.

**Source:** Whitespace-insensitive diff

## MA-ch06.11

An agent with shell access in a repository produced a final diff that is small. During the session it also ran `pip install somepackage`, applied a schema migration to a local development database, and deleted a build-cache directory listed in `.gitignore`. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The diff is a complete record of what the session did.
- [ ] B. These actions are side effects: changes outside the tracked files that a diff does not display.
- [ ] C. Deleting an ignored directory is recorded in git history.
- [ ] D. A schema migration changes the database, not the source tree, so reading the diff would not reveal it.
- [ ] E. A command log or session transcript is the place to find these actions.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: These actions changed state that the diff does not show.
- B: A side effect is a change beyond the reviewed output.
- C: Ignored paths are not tracked, so git records nothing.
- D: State outside the repository needs its own check.
- E: It records the commands that ran, which a diff cannot.

**Source:** Side effects outside the diff

## MA-ch06.12

A reviewer has two diffs to read. Diff 1 contains 600 lines of regenerated lockfile entries and a 20-line change to payment rounding logic. Diff 2 contains 400 lines of docstring edits. A coding agent produced each in minutes. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The 20-line rounding change deserves less attention because it is short.
- [ ] B. The docstring diff deserves more scrutiny than the payment change because it is longer.
- [ ] C. Review effort should follow the risk of each change rather than its line count.
- [ ] D. Generated lockfile lines can be skipped without checking which packages changed.
- [ ] E. A reviewer who reads faster removes the mismatch between agent speed and review capacity.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: Short changes to money logic can carry the most risk.
- B: Length is a poor guide to risk.
- C: Risk depends on what the change can break.
- D: The set of changed packages is the content that needs checking.
- E: The fix is to shrink and focus what is read, not to read faster.

**Source:** Review effort follows risk

## MA-ch06.13

A developer asks a coding agent for a plan before permitting any edits. The returned plan lists four files to change, and one is outside the set the developer expected. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Asking for a plan before edits begin is planning before acting; in Claude Code it is called plan mode.
- [ ] B. The unexpected file is a scope question to settle before edits begin.
- [ ] C. Approving the plan also approves the resulting diff.
- [ ] D. The resulting diff still needs review because the agent can deviate from the plan.
- [ ] E. A plan is a binding contract that prevents the agent from deviating.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: The agent proposes steps first and edits only after approval.
- B: Scope is easier to correct in a plan than in a finished diff.
- C: A plan is a prediction; the diff is the actual change.
- D: Plan and diff are separate artifacts.
- E: Nothing in a plan enforces itself.

**Source:** Planning before acting

## MA-ch06.14

Claude Code asks for permission before editing files or running shell commands by default, and can be configured with rules for particular tools and paths. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Permission rules can allow, ask about or deny specific tools or paths.
- [ ] B. A deny rule on a path is enforced by the tool, not requested of the model.
- [ ] C. Approving a permission prompt lets the action run but does not mean the result has been reviewed.
- [ ] D. A permission prompt asks to let an action run, whereas an approval gate decides whether a result moves forward.
- [ ] E. Pre-approving an action with an allow rule removes the need for diff review.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: These are the three kinds of rule.
- B: Enforcement does not depend on the model choosing to comply.
- C: Permission governs acting; review governs accepting the outcome.
- D: One guards an action; the other guards an outcome.
- E: The allowed action can still produce a bad change.

**Source:** Permission rules versus approval of results

## MA-ch06.15

A team wants Claude Code to stay out of files under `migrations/`. They compare ways to do it. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A sentence in the project instruction file, CLAUDE.md, enforces the rule.
- [ ] B. A deny permission rule on that path enforces the rule at the tool level.
- [ ] C. An instruction file is guidance that the model can fail to follow.
- [ ] D. A continuous-integration check on changed file names prevents the edit from happening in the working directory.
- [ ] E. Reading the diff for changes under `migrations/` is a detective control that catches the edit after the fact.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: The file is guidance the model reads; it is not a barrier.
- B: The tool refuses the edit.
- C: Instructions are read, not enforced.
- D: CI runs after the edit and reports it.
- E: Detective controls find problems; they do not prevent them.

**Source:** Instruction versus enforcement

## MA-ch06.16

A team defines allowed files as `{app.py, tests/test_app.py}`. An agent's patch changes `{app.py, tests/test_app.py, requirements.txt}`. The team's scope check computes the set difference of changed files minus allowed files. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The check returns `requirements.txt` as outside the scope.
- [ ] B. A non-empty difference shows the patch contains a bug.
- [ ] C. An empty difference shows the edits inside the permitted files are appropriate.
- [ ] D. The check detects an unrelated reformatting of lines inside `app.py`.
- [ ] E. The check works on file names, so it does not see what changed inside a permitted file.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: It is in the changed set but not the allowed set.
- B: It shows a scope violation, not a defect.
- C: The check compares file names, not edit content.
- D: That file is permitted, so the check passes.
- E: A content-level review is still needed.

**Source:** Scope check by set difference

## MA-ch06.17

An agent working within an allowed-file list finds that its fix requires editing `config/limits.yaml`, which is not on the list. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The agent should stop and ask the person who set the scope.
- [ ] B. The agent should widen the list to the whole repository so it can finish.
- [ ] C. The agent should edit the file and mention it briefly in its closing summary.
- [ ] D. A decision to widen the scope, and the reason, belongs in the record.
- [ ] E. The agent decides on its own because it knows the code best.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Scope changes are the owner's decision.
- B: That removes the boundary rather than respecting it.
- C: An out-of-scope edit discovered afterwards is scope creep.
- D: The record lets a later reader see why the file changed.
- E: Knowing the code does not give authority over scope.

**Source:** Handling a scope boundary

## MA-ch06.18

A patch fixes the reported bug and all tests pass, but the diff also reformats about 300 unrelated lines in the permitted file and adds a new third-party package to the dependency list, which is not on the allowed list. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reformatting unrelated lines is scope creep and makes the real change harder to review.
- [ ] B. A correct fix and green tests make the extra changes irrelevant.
- [ ] C. A new dependency deserves scrutiny beyond its line count because it brings third-party code into the project.
- [ ] D. Asking for a revision that removes the out-of-scope changes is a reasonable response.
- [ ] E. Adding a package is low risk because the diff for it is a single line.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: The meaningful edit gets buried in noise.
- B: Tests do not cover scope.
- C: Dependencies carry supply-chain and maintenance risk.
- D: The fix can be kept while the extras are dropped.
- E: Size of the diff says little about the effect.

**Source:** Scope creep and dependency changes

## MA-ch06.19

A merge-gating function accepts two booleans, `tests_passed` and `human_approved`, and reports ready when both are True. A pipeline author calls it with both set to the literal True in a script. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Passing the literal True shows the tests ran.
- [ ] B. A boolean is a claim about the evidence, not the evidence.
- [ ] C. The function proves that a person reviewed the diff.
- [ ] D. The function would refuse to report ready if neither check had happened.
- [ ] E. A checkable readiness record needs the two booleans alone.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: The value is typed in; no test is linked to it.
- B: The evidence is the command, its exit status and the commit tested.
- C: It only reads whatever value it is given.
- D: It reports ready for any pair of True values.
- E: A reviewer needs the commands, results and approver to check the claim.

**Source:** Claim versus evidence in a gate

## MA-ch06.20

At the end of a session a coding agent reports: "I fixed the bug and all tests pass." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The message is a claim by the agent, not evidence.
- [ ] B. The message tells the reviewer which tests ran and against which commit.
- [ ] C. A reviewer can turn the claim into evidence by rerunning the tests and recording the command and exit status.
- [ ] D. A clear and confident summary is a good indicator that the claim is correct.
- [ ] E. The claim carries equal weight to a logged test run because both come from the same session.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Evidence is a recorded run that others can inspect.
- B: It names neither.
- C: A rerun produces an inspectable record.
- D: Fluent wording does not track correctness.
- E: Only the logged run can be inspected.

**Source:** Agent self-report is a claim

## MA-ch06.21

At 10:00 an agent edits `parser.py`. At 10:05 a reviewer runs the test suite and every test passes. At 10:10 the agent refactors `utils.py`, which `parser.py` imports. At 10:12 the reviewer is about to merge, citing the 10:05 result. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The 10:05 result is stale evidence because the code changed after it was gathered.
- [ ] B. The result is still valid because the edited file at 10:10 is not `parser.py`.
- [ ] C. A change to a file that `parser.py` imports can alter the behaviour of `parser.py`.
- [ ] D. The tests should be rerun against the current diff, and the commit tested should be recorded.
- [ ] E. Merging on the 10:05 result would rest on evidence older than the current code.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Evidence describes the version that was tested.
- B: `parser.py` depends on the file that changed.
- C: Imports create a dependency between files.
- D: Evidence must be tied to the exact version.
- E: The later edit invalidates that conclusion.

**Source:** Stale evidence

## MA-ch06.22

A review tool records a reviewer's decision only as `approved = true`. After approval and before merge, the agent amends its proposal. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The approved flag still applies to the amended proposal.
- [ ] B. The flag does not identify which proposal was approved.
- [ ] C. Binding the approval to a commit hash or a digest of the diff identifies exactly what was approved.
- [ ] D. A digest proves the reviewer read the diff.
- [ ] E. An amendment after approval calls for a fresh review.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: The flag does not say which proposal it covered.
- B: It records a decision without naming its object.
- C: A hash changes whenever the content changes.
- D: It identifies the content, not the reviewer's effort.
- E: The approved version no longer exists.

**Source:** Binding approval to a version

## MA-ch06.23

A reviewer edits the working tree of a Python project and runs the test suite, which passes. Later the reviewer finds that the tests had imported the package from an older copy installed in the environment's site-packages, not from the edited working tree. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The test run did not exercise the code under review.
- [ ] B. Running the suite after the final edit protects against this problem.
- [ ] C. Recording the path the package was imported from would have revealed the mismatch.
- [ ] D. The mismatch is a bug in the patch.
- [ ] E. A pass after the final edit is enough evidence regardless of what was imported.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: The tests ran against the older installed copy.
- B: The timing was right but the code under test was wrong.
- C: The record would show a path outside the working tree.
- D: It is a problem with the environment of the check.
- E: Evidence is only worth something if it covers the reviewed code.

**Source:** Tested code differs from reviewed code

## MA-ch06.24

A reviewer's sign-off includes the line "Not checked: Unicode input, behavior outside the allowed files, anything that ran before the last edit." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A not-checked list states the limits of the claim being made.
- [ ] B. The line weakens the sign-off and is better left out.
- [ ] C. It tells a later reader which risks remain open.
- [ ] D. A summary drafted by the AI system that made the change tends to list in detail what it has not verified.
- [ ] E. It is part of matching the strength of a claim to the strength of the evidence.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: It tells the reader what the evidence does not cover.
- B: Stating limits makes the sign-off more honest.
- C: The reader can decide whether to check them.
- D: Such drafts tend to omit their own gaps.
- E: Claim calibration includes saying what was not examined.

**Source:** The not-checked line

## MA-ch06.25

A student's submission says, "AI wrote about 70 percent of the code." An instructor wants a more informative contribution record for the review packet. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A percentage shows which decisions a person judged.
- [ ] B. A better record states what the agent drafted and what the person decided, changed or rejected.
- [ ] C. Stating that a person exercised judgment is enough evidence that they did.
- [ ] D. A session transcript is evidence of the prompts given and decisions made.
- [ ] E. If the session failed to start, writing a plausible transcript of it is acceptable.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: It says how much, not what was decided.
- B: It attributes judgment to specific points.
- C: Evidence is something like a transcript or a diff showing the choices.
- D: It is the primary record of the interaction.
- E: A fabricated record is false evidence even when the code works.

**Source:** Contribution record

## MA-ch06.26

A reviewer is looking at a patch to a function specified as "return the input plus one." The new body is `return 3`. Before running anything, the reviewer writes down: verdict suspect; target, behavior on an input other than the one in the existing test; mechanism, the body never reads its argument; and what would change their mind. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A mechanism is a restatement of the verdict.
- [ ] B. Writing the prediction after the run is as valuable as writing it before.
- [ ] C. A prediction made before the run lets the reviewer learn from a mismatch with the result.
- [ ] D. A strong feeling that a patch is fine is sufficient without a stated mechanism.
- [ ] E. Saying what would change the reviewer's mind makes the prediction falsifiable.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: A mechanism explains why the verdict is expected.
- B: A later prediction is shaped by the result.
- C: A mismatch shows where the reviewer's model is wrong.
- D: A feeling is not testable.
- E: A falsifiable prediction can be shown wrong.

**Source:** Written prediction before the check

## MA-ch06.27

A reviewer says, "I audited the patch by running the test suite." In this question, a plausibility judgment is the reviewer's own prediction, made before running anything, of what the code should do; verification is checking against an external source such as a test run. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Running the test suite is a plausibility judgment.
- [ ] B. Running the test suite is verification.
- [ ] C. Saying "audited" blurs two kinds of evidence into one word.
- [ ] D. A plausibility judgment is stronger evidence than verification.
- [ ] E. A reviewer's expectation that the code looks right counts as verification.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: A run is checked against the outside world.
- B: The suite is an external check.
- C: Each kind answers a different question.
- D: Verification is checked outside the reviewer's head.
- E: Expectation is a prediction, not a check.

**Source:** Plausibility judgment versus verification

## MA-ch06.28

A diff changes how a numerical library call rounds a value. The reviewer has never used the library and cannot tell from the diff whether the new behavior is right. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The reviewer can read the library documentation or try boundary values to check the behaviour.
- [ ] B. The reviewer should record that the change was outside their ability to judge.
- [ ] C. Clean formatting is evidence that the rounding is right.
- [ ] D. A persuasive description from the agent can stand in for checking.
- [ ] E. Unfamiliarity is a good reason to skip that line of the diff.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: These are ways to verify against a source.
- B: The limit belongs in the sign-off.
- C: Formatting says nothing about the rounding rule.
- D: Persuasive wording is not evidence.
- E: Unfamiliar code is where checking matters most.

**Source:** Reviewing unfamiliar code honestly

## MA-ch06.29

Reviewers record accept rationales. Reviewer X writes "Looks good." Reviewer Y writes "Accept commit 9f3c for integer inputs; the two regression cases and the existing suite passed; non-integer inputs were not evaluated." Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Y identifies the exact proposal accepted by naming a commit.
- [ ] B. Y states the scope of the evidence and what was not evaluated.
- [ ] C. X is adequate because a short note makes the commit obvious.
- [ ] D. A reader can check Y's claims against the record but has nothing to check in X.
- [ ] E. Y claims no more than its evidence supports.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: A commit identifier fixes the version.
- B: That makes the claim calibrated.
- C: The note names nothing a reader could check.
- D: Specific claims are checkable.
- E: Y limits itself to the tested inputs.

**Source:** Specific accept rationale

## MA-ch06.30

An AI review tool ends its analysis of a patch with the line `decision: accept`. A manager proposes treating that line as the human approval gate to speed up merges. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The tool can legitimately contribute by flagging risks, suggesting checks and drafting findings.
- [ ] B. The line is a human approval.
- [ ] C. The person who made the change can approve it by pointing to the line.
- [ ] D. Adopting the line speeds up merges without lowering assurance.
- [ ] E. Responsibility for the merge moves to the tool once it prints the line.

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: These support the person who decides.
- B: It is an output of a tool.
- C: The gate exists to add a second, accountable judgment.
- D: The speed comes from dropping a human check.
- E: Accountability stays with a person.

**Source:** AI output versus human approval

## MA-ch06.31

A report changes the sentence "the patch completely fixes the bug" to "the data suggest the patch implements the rule on the tested inputs." The evidence is one run of three tests on one commit. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The revised sentence matches the strength of the claim to the strength of the evidence.
- [ ] B. The phrase "on the tested inputs" names the scope of the evidence.
- [ ] C. A hedge such as "suggest" tells the reader the evidence is limited.
- [ ] D. "Safe to merge" is a decision, not an evidence finding in the way "returns the expected values for these inputs" is.
- [ ] E. Hedging words such as "suggest" show that the reviewer lacks confidence in the work.

**Key:** A=T B=T C=T D=T E=F

**Why:**

- A: Calibration means not claiming more than the evidence shows.
- B: It limits the claim to what was run.
- C: Hedging marks uncertainty honestly.
- D: A decision depends on risk tolerance as well as evidence.
- E: They show the claim is limited to the evidence.

**Source:** Claim calibration

## MA-ch06.32

An agent implements the rule in a ticket ("round prices down to the nearest dollar") and every test derived from the ticket passes. The diff is clean and in scope. Finance later says prices should be rounded to the nearest cent. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The patch was verified against the ticket, but the ticket itself was wrong.
- [ ] B. Tests derived from the ticket are independent evidence that the ticket is right.
- [ ] C. Tests derived from a requirement share the errors of that requirement.
- [ ] D. A larger test suite derived from the same ticket would have exposed the problem.
- [ ] E. Confirming the rule with the people who own it could have caught the mistake.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Verification checks against the stated requirement; validation checks the requirement against the need.
- B: They inherit the ticket's errors.
- C: They cannot detect a flaw in their own source.
- D: More tests from the same source repeat the same error.
- E: Validation involves the requirement's owners.

**Source:** Verification versus validation

## MA-ch06.33

A coding agent is asked to fix a bug in an authentication module. Behavior in that module is overridden by a configuration file the agent never read. Its patch is coherent, well formatted and passes new tests the agent wrote. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The failure arose upstream of the patch, because the agent lacked the relevant context.
- [ ] B. A diff review may not reveal it, because a diff shows what changed and not what the change interacts with.
- [ ] C. A well-formatted patch is a sign that the agent's context was complete.
- [ ] D. Tests written by the agent share the agent's incomplete picture of the module.
- [ ] E. A longer diff would have revealed the override.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: The agent did not have the configuration in view.
- B: Unseen interactions are outside the diff.
- C: Formatting says nothing about context.
- D: They test what the agent understood.
- E: The override lived in a file the diff did not touch.

**Source:** Missing context upstream of the patch

## MA-ch06.34

A developer's prompt to Claude Code reads: "Fix the shipping thing and make sure it's all good, touch whatever you need." The developer wants to rewrite it with exact terms. Check each statement that is true about the rewrite. Each statement is worth 1 point (5 points total).

- [ ] A. "The shipping thing" is better replaced by a named function and a reproduction with input, observed output and expected output.
- [ ] B. "Touch whatever you need" is better replaced by an allowed-file list that sets the scope.
- [ ] C. "Make sure it is fine" is better replaced by a stop condition naming the regression test and existing suite, with command and exit status reported.
- [ ] D. Adding the words "be careful" is the exact term for a deny permission rule.
- [ ] E. Replacing the sentence with "fix it fast" reduces the size of the diff.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: A reproduction makes the task concrete.
- B: Scope bounds where the agent may edit.
- C: A stop condition says when the work counts as done.
- D: A deny rule is configured, not requested in prose.
- E: Speed is not scope.

**Source:** Rewriting a vague prompt with exact terms

## MA-ch06.35

A student mixes up the vocabulary of Claude Code and its controls. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A permission rule governs whether Claude Code may use a tool or touch a path.
- [ ] B. An approval gate and a permission prompt are the same control.
- [ ] C. An approval gate is the prompt Claude Code shows before running a shell command.
- [ ] D. A hook is a user-defined command that runs at a point in the agent's lifecycle and can be used to block an action.
- [ ] E. Plan mode lets the agent edit files while it drafts its plan.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: It controls acting.
- B: A gate decides whether a result moves forward.
- C: That prompt is a permission prompt.
- D: Hooks run automatically on events such as before a tool call.
- E: Plan mode withholds edits until the plan is approved.

**Source:** Permission, approval gate and hook

## MA-ch06.36

A student mixes up the vocabulary of testing and review. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A regression test checks that behaviour that was fixed or established has not broken again.
- [ ] B. A reproduction is an explanation of the root cause.
- [ ] C. A diagnosis names the cause of a failure.
- [ ] D. An oracle is the output the program happens to produce.
- [ ] E. A mutant is a test that fails on correct code.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: It guards against a return of the failure.
- B: That is a diagnosis; a reproduction shows how to trigger the failure.
- C: It explains why the failure happens.
- D: An oracle is the trusted source of the expected value, such as the written requirement.
- E: A mutant is a deliberately altered version of the code.

**Source:** Regression test, reproduction, diagnosis, oracle, mutant
