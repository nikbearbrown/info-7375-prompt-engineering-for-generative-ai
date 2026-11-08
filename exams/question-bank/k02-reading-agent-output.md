# Jargon test: reading agent output

## MA-k02.1

An agent reports: "Retries are now safe." The diff wraps `charge_card(order)` in a retry loop that runs again on a timeout. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Wrapping any call in a retry loop makes it safe to retry.
- [ ] B. A follow-up that turns the claim into evidence is: "Write a test that calls charge_card twice with the same order and counts the charges."
- [ ] C. If the first call timed out, the caller knows it had no effect, so a retry is safe.
- [ ] D. A retry is safe only if repeating the call has the same effect as doing it once, which is what idempotent means.
- [ ] E. One passing test with a single call shows that retries are safe.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: The loop does not change what a repeated call does.
- B: The test observes the effect of a repeat.
- C: A timeout leaves the outcome unknown.
- D: Idempotent is the property retries rely on.
- E: A single call never exercises a repeat.

**Source:** idempotent, retry safety

## MA-k02.2

An agent ends its summary with: "I tidied some formatting in `billing.py` too." Your instruction said not to touch `billing.py`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The change can be accepted because a formatter is deterministic.
- [ ] B. Whitespace-only edits are not a scope violation because behaviour is unchanged.
- [ ] C. A constraint stated before the work is a preference, and the diff need not be checked against it.
- [ ] D. A correct follow-up is: "Revert `billing.py` and show `git diff --stat` so I can confirm only the allowed files changed."
- [ ] E. Editing a file outside the stated scope is a scope violation even when the change is harmless.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: Determinism says nothing about permission.
- B: The file was off limits.
- C: It belongs to the acceptance criteria.
- D: The revert is checked against evidence.
- E: Scope is set by the instruction, not by the size of the change.

**Source:** scope violation, diff review

## MA-k02.3

An agent says about a new function: "This should handle all cases." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Should" states a prediction; it is not evidence.
- [ ] B. The claim becomes evidence once the agent lists the cases it thought about in prose.
- [ ] C. Naming the input classes turns "all cases" into acceptance criteria that tests can check.
- [ ] D. "All cases" defines a checkable condition by itself.
- [ ] E. A better instruction is: "List the input classes as test cases (empty, None, duplicates, very long) and run them."

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Nothing was run or shown.
- B: A list in prose is still a claim.
- C: Enumerated classes are checkable conditions.
- D: An unbounded set must be enumerated before it can be checked.
- E: Cases become checkable when named and run.

**Source:** claim vs evidence, acceptance criteria

## MA-k02.4

An agent reports "All tests pass" after pytest prints `2 passed`. The two tests are `assert True` and one that imports the module. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A larger count of passing tests matters more than what each one asserts.
- [ ] B. A pass only shows that the existing checks did not fail; its weight depends on what they assert.
- [ ] C. A test with no assertion on the changed behaviour fails when the change is broken.
- [ ] D. Passing tests mean the new function is verified.
- [ ] E. A good follow-up is: "Rerun pytest and paste the line that says passed."

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: Assertions carry the evidence, not the count.
- B: These checks cannot fail.
- C: Without an assertion it cannot fail on the change.
- D: No test touches the new behaviour.
- E: Rerunning the same trivial checks gives the same result.

**Source:** trivial tests, verification

## MA-k02.5

An agent says: "Safe for concurrent workers." The code is `if not os.path.exists(p): open(p, "w").write(data)`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Opening with mode "x" makes the check and the create one operation that fails if the file exists.
- [ ] B. Two workers can both see the file missing before either writes, which is a check-then-act race.
- [ ] C. Adding a short random sleep before the check removes the race.
- [ ] D. A follow-up that gives evidence is: "Read the code again and confirm it looks safe."
- [ ] E. The code is safe because the check runs right before the write.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Exclusive create is atomic.
- B: The gap between check and act is the race.
- C: It makes the race less likely, not impossible.
- D: Rereading produces no observation of concurrency.
- E: Proximity does not close the gap.

**Source:** check-then-act race, atomic

## MA-k02.6

An agent summarizes: "Added input validation for empty emails." The diff changes one line: `email = email.strip()`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. When the summary and the diff disagree, the summary should win because it states intent.
- [ ] B. The diff, not the summary, is the record of what changed.
- [ ] C. The summary and the code disagree: stripping normalizes input, it does not reject it.
- [ ] D. A validation claim is checked by passing an empty string and seeing it rejected.
- [ ] E. A good follow-up is: "Show the line that rejects an empty email and a test that passes an empty string."

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: The diff is what runs.
- B: Read the diff against the claim.
- C: Nothing raises or returns an error.
- D: Rejection is observable in the result.
- E: It asks for the code and a test.

**Source:** claim vs code mismatch

## MA-k02.7

An agent reports: "Processed the batch: 480 records written." The input had 500 records and the log shows 20 lines saying `skipped`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An exit code of 0 shows that every record was handled.
- [ ] B. The next step is to rerun the whole batch without checking whether the write is idempotent.
- [ ] C. A summary of successes is complete when no exception reached the top.
- [ ] D. A follow-up is: "Reconcile the counts: input 500 = written + skipped + failed, and list the skipped IDs."
- [ ] E. The result is partial: 480 of 500 were written and the claim leaves out the 20 skipped.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: The program may exit normally after skipping.
- B: A rerun can duplicate the 480.
- C: Skips do not raise.
- D: Counts must add up.
- E: The report omits the failures.

**Source:** partial results

## MA-k02.8

An agent says: "Fixed the flaky test." The diff adds `@retry(3)` above the test and changes nothing else. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A flaky test gives the same outcome on every run of the same code and inputs.
- [ ] B. A follow-up is: "Name what varies (time, order, network) and show a test that fails reliably before the fix."
- [ ] C. Lower failure rate with retries shows the flakiness is fixed.
- [ ] D. A retry hides nondeterminism; it does not remove the cause.
- [ ] E. A test that passes after a rerun is deterministic.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Flaky means the outcomes vary.
- B: It asks for the cause and a failing test.
- C: The rate drops but the cause remains.
- D: The test can still fail for the same reason.
- E: Deterministic means the same result every run.

**Source:** flaky test, claim vs code

## MA-k02.9

An agent presents this plan before editing: "I'll refactor the module and update callers as needed." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The plan is acceptable because "as needed" lets the agent adapt.
- [ ] B. The plan is too vague to approve: it names no files, order or checks.
- [ ] C. In plan mode the agent researches without editing and presents a plan for approval.
- [ ] D. A plan is useful only after the code is written, so it can be compared with the result.
- [ ] E. A follow-up is: "List the files you will edit, the ones you will not touch, and how each step is checked, before any edit."

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: It gives the agent unbounded scope.
- B: There is nothing to compare the diff against.
- C: That is planning before acting.
- D: The plan is for approval before the change.
- E: It makes the plan checkable.

**Source:** planning before acting, plan review

## MA-k02.10

An agent writes: "I ran the tests and they pass." The transcript contains no tool call and no tool output. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The claim can be accepted because agents report what they did.
- [ ] B. The agent's own sentence counts as a tool_result.
- [ ] C. A tool_use is the output a tool returns, and a tool_result is the model's request to run it.
- [ ] D. A follow-up is: "Confirm that you ran the tests."
- [ ] E. Without a tool_use and a tool_result in the transcript, the claim is unsupported.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: Reports can be wrong; check the evidence.
- B: A tool_result is what the tool returned.
- C: The request is the tool_use; the output is the tool_result.
- D: A repeated claim is still not output.
- E: Nothing shows a run.

**Source:** tool_use, tool_result, verification

## MA-k02.11

An agent says: "I'll delete the old migration files and push to main now." It continues without pausing. Your setup lists `delete` and `git push` as ask-first. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An approval gate stops the action until a human decides.
- [ ] B. Deleting files and pushing to a remote are hard to undo and should stop at an approval gate.
- [ ] C. Listing delete and push as ask-first is a permission scope choice that makes the agent stop.
- [ ] D. Your approval of the edit plan also covers a later push to a remote.
- [ ] E. A correct instruction is: "Pause before any delete or push and show the exact paths and branch."

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A gate pauses before the action.
- B: A human decision is needed before them.
- C: The scope sets which actions need approval.
- D: Approval is per action.
- E: It names the actions and what to show.

**Source:** approval gate, permission scope

## MA-k02.12

An agent reports: "To debug, I read `~/.aws/credentials`." The permission scope was the project directory only. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A narrower scope is one that lists more directories.
- [ ] B. A follow-up is: "List every file outside the project you read and whether any content appeared in output."
- [ ] C. Being able to read the file means it was within scope.
- [ ] D. Reading is not a violation because nothing was changed.
- [ ] E. Reading a file outside the allowed directories is out of scope even if nothing was modified.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: Narrower means fewer paths and commands.
- B: It checks the extent of the exposure.
- C: Capability is not permission.
- D: The secret may now sit in the transcript.
- E: Scope covers reads.

**Source:** permission scope, least privilege

## MA-k02.13

An agent says: "Reduced latency by caching." The diff adds `@functools.lru_cache` to `load_settings()`, which reads a file that operators edit. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. lru_cache notices when the file contents change.
- [ ] B. A higher hit rate shows the change is correct.
- [ ] C. A follow-up is: "State when the cache is invalidated and test it: edit the file, call again, expect the new value."
- [ ] D. Faster output is not evidence of the same output; an equivalence check is needed.
- [ ] E. After the file changes, the cached function keeps returning the old value.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: It only compares arguments.
- B: Hits can be wrong values.
- C: The test targets staleness.
- D: Speed and correctness are separate.
- E: The cache key is the arguments, not the file.

**Source:** cache, stale data, equivalence

## MA-k02.14

An agent says: "Refactor complete, behavior unchanged." The diff changes a default argument from `timeout=10` to `timeout=20`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A refactor claim is checked against the diff for changed constants and defaults.
- [ ] B. Changing a default stays within a refactor because the signature is the same.
- [ ] C. A follow-up is: "Run the same inputs before and after and show the outputs match."
- [ ] D. The claim and the code disagree: callers that use the default now behave differently.
- [ ] E. A default argument is part of a function's behaviour for callers that omit it.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: These are common silent changes.
- B: Callers see different behaviour.
- C: A characterization check supports the claim.
- D: The default is behaviour.
- E: Omitting the argument uses the default.

**Source:** claim vs code mismatch, refactor

## MA-k02.15

An agent says a new helper is "pure". The code is `def add(item, bucket=[]): bucket.append(item); return bucket`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Python creates a fresh default list on each call.
- [ ] B. The usual fix is to copy the list on the first call and reuse the copy afterward.
- [ ] C. The function is not pure: the default list persists between calls.
- [ ] D. It is pure because it returns a value.
- [ ] E. A check is to call it twice with the same argument and see that the results differ.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: The default is made once at definition.
- B: The fix is a `None` default and a new list per call.
- C: State is shared across calls.
- D: Purity requires no hidden state.
- E: Same input, different output shows hidden state.

**Source:** pure function, mutable default

## MA-k02.16

An agent says: "Added error handling." The diff wraps the main work in `try: ... except Exception: pass`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The program is more robust because no exception reaches the user.
- [ ] B. The handler silences failures; error handling means detecting and reporting or recovering.
- [ ] C. Swallowed errors show up in the exit code as a nonzero status.
- [ ] D. A follow-up is: "Add a comment explaining why exceptions are ignored."
- [ ] E. A catch-all `pass` is acceptable if a comment explains it.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: Failures are hidden, not handled.
- B: Nothing is reported.
- C: No exception escapes, so the exit code stays zero.
- D: A comment does not make a failure observable.
- E: A comment does not report the failure.

**Source:** error handling, silent failure

## MA-k02.17

An agent builds a test around a Claude call and reports: "It is deterministic: I set temperature to 0." The test compares exact text. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Setting Python's `random.seed` fixes the model's sampling on the server.
- [ ] B. Temperature 0 reduces variation but does not guarantee identical output on every call.
- [ ] C. A sturdier test compares exact text, since text is what the user sees.
- [ ] D. A follow-up is: "Run the same prompt five times and diff the outputs."
- [ ] E. Temperature 0 guarantees byte-identical output on every call.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: The sampling does not run in your process.
- B: Other factors can change output.
- C: Exact text breaks on harmless wording changes.
- D: It measures the variation.
- E: It is not a guarantee.

**Source:** deterministic, temperature

## MA-k02.18

An agent says: "Retrieval returned the relevant document, so the answer is grounded." The answer states a figure that does not appear in that document. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A follow-up is: "Quote the sentence in the retrieved passage that supports the figure."
- [ ] B. A citation check compares a claim against the source text.
- [ ] C. The answer is grounded because the retrieved text was in the prompt.
- [ ] D. Retrieval puts text in the context; it does not guarantee the answer uses it.
- [ ] E. A figure that is not in the sources is acceptable if it sounds plausible.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: A quote can be compared with the source.
- B: That is what the check does.
- C: Grounded means supported by the text.
- D: The model may add content.
- E: Plausible is not supported.

**Source:** retrieval, grounding, citation check

## MA-k02.19

An agent reports: "I verified the fix by re-running the script; it printed `Done`." The script ends with `print("Done")` unconditionally. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A test that fails before the change shows the test can detect the bug.
- [ ] B. Printed output is a tool_result, so the verification is complete.
- [ ] C. A follow-up is: "Write a test that fails on the old code, then show it passes after the fix."
- [ ] D. The message `Done` is not evidence about the behaviour.
- [ ] E. Verification must be confirmable apart from the producer, so the script's own message cannot serve.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Otherwise its pass means little.
- B: A result is evidence only if it depends on the behaviour.
- C: A failing-first test can tell the cases apart.
- D: It prints whatever happens.
- E: The script is the producer.

**Source:** verification, failing test first

## MA-k02.20

An agent reports: "Added tests for the parser: 12 tests, all green." All 12 call the parser with the same valid string. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Twelve tests improve branch coverage over one test.
- [ ] B. Green tests prove the parser has no bugs.
- [ ] C. A follow-up is: "Give a table of input classes (empty, malformed, unicode) with the test for each."
- [ ] D. The count of tests does not measure what they cover.
- [ ] E. Another check is to break the parser on purpose and show that a test fails.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: They repeat one path.
- B: They show only that these checks passed.
- C: It maps classes to checks.
- D: All twelve exercise one path.
- E: A test that cannot fail is not evidence.

**Source:** tests, coverage of input classes

## MA-k02.21

An agent reports: "The migration succeeded." The last log lines are `table 3 of 5 done` then `Terminated`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. No error message appeared, so the migration succeeded.
- [ ] B. Rerunning from the start is safe without first checking whether the script is idempotent.
- [ ] C. A follow-up is: "Rerun the script and report whether it prints succeeded."
- [ ] D. A resumable migration restarts from the first table on each run.
- [ ] E. The result is partial: three of five tables were migrated before the process stopped.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: A killed process may print none.
- B: A rerun can duplicate rows.
- C: Rerunning may repeat the stop and duplicate earlier rows.
- D: Resumable means it skips completed tables.
- E: The log shows it stopped.

**Source:** partial results, idempotent

## MA-k02.22

An agent says: "Incremented the counter safely." The code is `n = store.get("n"); store.set("n", n + 1)` in a store shared by several workers. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Two workers can read the same value and both write n + 1, so one increment is lost.
- [ ] B. The code is safe because the two lines run one after the other.
- [ ] C. A check is to run one worker once and confirm the counter went up by one.
- [ ] D. A `threading.Lock` in each worker process protects against workers in other processes.
- [ ] E. An atomic increment, such as Redis `INCR` or SQL `SET n = n + 1`, closes the gap.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: The read and write are separate steps.
- B: Only within one worker.
- C: A single worker cannot expose the race.
- D: A lock in one process is invisible to others.
- E: The store does it in one step.

**Source:** read-modify-write race, atomic

## MA-k02.23

An agent says: "I'll remember your preferences for next week; I used the context window." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The context window holds tokens of the current conversation; it does not carry over to a new session.
- [ ] B. A follow-up is: "Write the preferences into a memory file such as CLAUDE.md and show me the file."
- [ ] C. Anything said earlier remains available in a new session.
- [ ] D. A memory file read at the start of a session is what makes standing instructions persist.
- [ ] E. A longer context window gives the agent memory across sessions.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: The next session starts empty.
- B: A file persists.
- C: Only saved content persists.
- D: It loads each time.
- E: Length is not persistence.

**Source:** context window vs memory

## MA-k02.24

An agent summarizes: "Updated 3 files: `parser.py`, `utils.py`, `README.md`." `git diff --stat` shows five files changed. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Files the agent thinks are minor can be left out of a summary.
- [ ] B. The summary is the diff, so no further check is needed.
- [ ] C. A follow-up is: "Paste `git diff --stat` and say why each file changed."
- [ ] D. The summary and the diff disagree about which files changed.
- [ ] E. An unlisted file is within scope because the summary covers the main work.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: The reader needs the full list.
- B: The diff is the record.
- C: It gets the full list.
- D: Two files are missing from the summary.
- E: Scope is set by your instruction.

**Source:** claim vs code mismatch, diff review

## MA-k02.25

An agent says: "Fixed the bug in `parse_date`; it works for the failing input." Only that one input was run. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Reading the diff for hard-coded constants checks the claim against the code.
- [ ] B. A fix that special-cases the reported input would pass the one example and leave the bug in place.
- [ ] C. Fixing the failing input implies a general fix.
- [ ] D. One example shows the fix for that input only.
- [ ] E. A follow-up is: "Write the failing test for the reported input first, then add boundary inputs."

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Special-casing shows in the diff.
- B: Special-casing passes that input only.
- C: The fix could be narrow.
- D: Other inputs were not run.
- E: It widens the evidence.

**Source:** claim vs evidence, failing test first

## MA-k02.26

An agent says: "I used an approved tool, so it's within scope." It called `run_shell` with `rm -rf build/`. Your permission allowed `run_shell` for `pytest` only. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Deleting `build/` is harmless, so it is not a scope violation.
- [ ] B. A tighter setup is an allowlist of commands, such as `pytest`.
- [ ] C. A follow-up is: "Tell me whether the commands were safe."
- [ ] D. Permission scope applies to the command given to the tool, not only to the tool name.
- [ ] E. Allowing a tool allows every command through it.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Harm is not the test; permission is.
- B: Anything else asks first.
- C: A judgment is not the record; the tool_use entries show the commands.
- D: The arguments decide what happens.
- E: Scope is narrower than the tool.

**Source:** permission scope, tool_use

## MA-k02.27

An agent says: "The eval passed: 8 of 10 graded answers were correct." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Ten cases give a precise estimate of the true accuracy.
- [ ] B. The pass threshold should have been written as acceptance criteria before the run.
- [ ] C. 8 of 10 means the system passes every case.
- [ ] D. An eval scores varying output, so its result is a rate rather than a single pass or fail.
- [ ] E. A follow-up is: "Show the two failures and the rubric used to grade."

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: A small set leaves wide uncertainty.
- B: Otherwise the threshold fits the result.
- C: Two failed.
- D: 8 of 10 is a rate.
- E: The failures show the weakness.

**Source:** eval vs test, acceptance criteria

## MA-k02.28

An agent reports: "I couldn't open `config.yaml`, but the usual structure suggests the timeout key is `timeout_s`, so I edited that." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Telling you it could not open the file was the right thing to report.
- [ ] B. The edit rests on a guess about a file the agent did not read.
- [ ] C. A follow-up is: "Do not edit until you have read `config.yaml` and quoted the relevant keys."
- [ ] D. Disclosing the guess makes acting on it safe.
- [ ] E. The edit is reasonable because the usual structure is generally right.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: The failure is stated.
- B: The key may not exist.
- C: Read first, then act.
- D: A disclosed guess is still a guess.
- E: This file may differ.

**Source:** acting on a guess, verification

## MA-k02.29

An agent says: "Done: the endpoint returns 200." It tested against a mock server that returns 200 for every request. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Acceptance criteria can leave out which dependencies are real, since a passing check is enough.
- [ ] B. The test shows how the mock behaves, not the real service.
- [ ] C. A 200 from the mock shows the real integration works.
- [ ] D. A 200 status means the body is correct.
- [ ] E. A follow-up is: "Make one request against staging and show the response body."

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: Without it an always-passing mock can satisfy the check.
- B: The mock always answers 200.
- C: The mock never ran the real code.
- D: Status and body are different.
- E: It uses the real dependency.

**Source:** mock, verification, acceptance criteria

## MA-k02.30

An agent shows this plan: "Step 3: update the database schema. Step 4: deploy." It lists no check after step 3 and no way back. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The plan has no verification after an irreversible step and no rollback.
- [ ] B. The plan is complete because the steps are in order.
- [ ] C. A plan should say what each step changes.
- [ ] D. A step that changes a live system needs a stated check and a way back even when it looks simple.
- [ ] E. A follow-up is: "Add an approval gate before step 3 and a check of its result before step 4."

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Step 3 may fail halfway.
- B: Order is not checking.
- C: Reviewers need it to judge scope.
- D: Simplicity does not remove the risk.
- E: It stops before and verifies after.

**Source:** planning before acting, approval gate

## MA-k02.31

An agent reports: "Batch finished in 2 seconds for 10,000 files." Earlier runs on 100 files took 40 seconds. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Run time is outside what needs checking.
- [ ] B. A follow-up is: "Report how many files you opened and show one output file."
- [ ] C. The speed is a reason to check that the files were read at all.
- [ ] D. A glob that matched nothing or a swallowed exception could explain the time.
- [ ] E. A fast run proves the code is efficient.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: A surprising number is a signal.
- B: A count and a sample are evidence.
- C: It is far out of line with earlier runs.
- D: Both give quick, empty runs.
- E: It may have done less work.

**Source:** claim vs evidence, partial results

## MA-k02.32

An agent says: "Made `get_or_create` thread-safe by using a dict instead of a list." The function does `if k not in d: d[k] = make()`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Changing the container does not remove the check-then-act sequence.
- [ ] B. A follow-up is: "Run it from 20 threads with the same key and count how many times `make` ran."
- [ ] C. A lock around the check and the create closes the gap.
- [ ] D. Every dict operation is atomic, so any code using a dict is thread-safe.
- [ ] E. The GIL makes any sequence of Python operations atomic.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Two threads can both pass the check.
- B: The count shows the race.
- C: They run as one unit.
- D: Single operations are; sequences are not.
- E: Threads can switch between lines.

**Source:** check-then-act race, atomic

## MA-k02.33

An agent says: "No changes outside the `parser` module." The diff also adds a line to `requirements.txt`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A follow-up is: "Keep the dependency in the same commit and move on."
- [ ] B. A new dependency is invisible at runtime.
- [ ] C. A new dependency is a change outside the module and should be asked about.
- [ ] D. A diff review covers source files only, since config files do not run.
- [ ] E. It is not behaviour, so it is outside what needs review.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: That accepts the change without testing the need.
- B: It is imported and run.
- C: It changes what installs.
- D: Config and requirements change what runs.
- E: A dependency changes the runtime.

**Source:** scope violation, diff review

## MA-k02.34

An agent says: "I verified the answer: I asked Claude again and it agreed." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Two runs agreeing is verification.
- [ ] B. Agreement across repeated runs proves the answer is true.
- [ ] C. Verification means checking against evidence you can confirm apart from the producer.
- [ ] D. Agreement from the same producer is not an independent check.
- [ ] E. A follow-up is: "Check it against the source document, or run the code and show the output."

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: They share the same blind spots.
- B: Consistent is not correct.
- C: That is the definition.
- D: It can repeat the same mistake.
- E: Evidence apart from the producer.

**Source:** verification, independence

## MA-k02.35

An agent summarizes: "Implemented caching; tests pass." The diff adds the cache and also deletes `tests/test_cache.py`. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A diff review looks for removed assertions as well as added code.
- [ ] B. Reading the pass count alone is enough.
- [ ] C. Deleting the test explains why the suite passes.
- [ ] D. Removing an outdated test is a normal part of adding a feature.
- [ ] E. A follow-up is: "Restore the test, run it, and show the result."

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Deleted checks hide failures.
- B: The count fell with the tests.
- C: The check that could fail is gone.
- D: Nothing says this test was outdated.
- E: The result can be read.

**Source:** claim vs code mismatch, diff review
