# Jargon test: compress and decompress

## MA-k01.1

A Python function `charge(order_id)` will be called by an agent that retries after timeouts. Which statements correctly unpack "make `charge` idempotent" into checkable conditions? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A test can call it twice and assert exactly one charge record exists for that `order_id`.
- [ ] B. Calling it twice with the same input returns the same text both times, whatever it changes.
- [ ] C. Calling it twice with the same `order_id` leaves the system in the same state as calling it once.
- [ ] D. A stored idempotency key for the `order_id` lets the second call detect the first and skip the charge.
- [ ] E. It finishes within a fixed time limit, so a retry cannot overlap the first call.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: That is a checkable form of the condition.
- B: Same return text says nothing about repeated side effects; the card could be charged twice.
- C: Idempotence is about the effect of repeated calls on state.
- D: A key lookup is a standard way to meet the condition.
- E: A time limit is a timeout, not idempotence; a slow first call can still be repeated.

**Source:** idempotent

## MA-k01.2

Claude Code proposes: "I added retry logic around `send_email(user)`; retries are safe because the function is idempotent." The function appends a row to an outbox table and calls an SMTP server on each call. Which statements judge the claim correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The claim is correct because the function returns `None` on each call.
- [ ] B. The claim holds, since the outbox row shows the email was recorded.
- [ ] C. Each call appends a row and sends a message, so a repeated call changes the outside world twice.
- [ ] D. Wrapping the call in `try/except` makes repeated calls produce one email.
- [ ] E. The claim is unsupported until a test shows two calls produce one email and one outbox row.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: The return value is not the criterion.
- B: A recorded row does not prevent a second send on retry.
- C: That is the opposite of idempotent.
- D: Exception handling does not deduplicate effects.
- E: Idempotence is demonstrated by repeated calls, not asserted.

**Source:** idempotent

## MA-k01.3

A user tells Claude: "Make the nightly import safe to rerun." Choose the statements that compress or unpack this requirement correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A one-line compression is: "Make the import idempotent: upsert on the natural key instead of inserting."
- [ ] B. The import is safe to rerun once it catches exceptions and exits with code 0.
- [ ] C. The import writes a log file with a matching name on each run.
- [ ] D. Another one-line compression is: "Make the import deterministic so it runs at the same time each night."
- [ ] E. Rerunning the import on the same file leaves the database with the same rows as one run.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Upsert on a key is a concrete way to get the effect.
- B: Exit code says nothing about duplicate rows.
- C: A matching log name is not a property of the data state.
- D: Deterministic concerns output for input, not schedule or rerun safety.
- E: This is the idempotent condition for the import.

**Source:** idempotent

## MA-k01.4

Which pairs of HTTP-style operations match the idempotent label? Judge the statements for a Python API that an agent may retry. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. `PATCH /counter` with body `{"increment": 1}`, since the request body is the same each time.
- [ ] B. `POST /orders` that creates a new order row for each request.
- [ ] C. `DELETE /sessions/42`, since the session is gone after the first call and later calls leave it gone.
- [ ] D. Any call that returns HTTP 200 counts as idempotent.
- [ ] E. `PUT /users/7` with a full replacement body, since repeating it leaves user 7 in the same state.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Same request does not mean same state; each call adds one.
- B: Each call adds a row, so repeats add more.
- C: The end state is the same after repeats.
- D: Status code does not describe repeated-call effects.
- E: Replacement converges on one state.

**Source:** idempotent

## MA-k01.5

A teammate asks Claude to "make the summarizer deterministic." Which statements unpack that into checkable conditions? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The function is idempotent, meaning repeated calls do not change stored data.
- [ ] B. The same input, with the same settings and code, yields the same output on repeated runs.
- [ ] C. A test runs the function twice and asserts the two outputs are equal.
- [ ] D. The output is correct on each input in the test set.
- [ ] E. Random seeds and sampling parameters are fixed, or sampling is removed, so no hidden randomness remains.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: Idempotence concerns state change, not output equality.
- B: This is the definition as a test.
- C: That checks the condition directly.
- D: Correctness is a separate property; a wrong output can repeat.
- E: Randomness is the usual source of variation.

**Source:** deterministic

## MA-k01.6

A Python script calls `random.choice(examples)` to pick few-shot examples for a prompt. An eval shows scores moving between runs. Which fixes address the stated requirement "same run, same prompt"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Lower the model temperature to 0.2 and leave the selection unseeded.
- [ ] B. Replace the random pick with a fixed list of example ids committed to the repo.
- [ ] C. Raise `max_tokens` so the model has room to answer the same way.
- [ ] D. Call `random.seed(1234)` once before selecting examples.
- [ ] E. Print the chosen examples to the log after each run.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: The prompt itself still varies between runs.
- B: Fixed inputs remove the randomness.
- C: Length limit does not control prompt selection.
- D: A fixed seed makes the draws reproducible.
- E: Logging records the variation without removing it.

**Source:** deterministic

## MA-k01.7

A Claude Code task says: "The report generator must be deterministic." The code includes `datetime.now()` in the header. Which statements are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Sorting the data rows makes the header stable.
- [ ] B. It is deterministic, since the body of the report is built from the same data.
- [ ] C. Passing the timestamp in as a parameter lets a test fix it and compare outputs.
- [ ] D. A snapshot test with a regex that ignores the header proves the generator is deterministic.
- [ ] E. Two runs at different times produce different header text, so the output is not identical for the same input.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Sorting does not touch the header.
- B: One varying part changes the output.
- C: Making the hidden input explicit allows equality checks.
- D: It masks the variation instead of removing it.
- E: The timestamp is a hidden input.

**Source:** deterministic

## MA-k01.8

Which statements correctly describe a `tool_use` block and a `tool_result` block in a Claude API conversation? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The application code decides whether to execute the requested call before it sends a `tool_result`.
- [ ] B. A `tool_use` block is produced by the model and names the tool and the arguments it wants run.
- [ ] C. A `tool_result` block is produced by the model after it runs the tool inside its weights.
- [ ] D. A `tool_result` block carries the `tool_use_id` of the request it answers.
- [ ] E. A `tool_use` block contains the output the tool returned.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: That is the point where checks and gates sit.
- B: The model requests; it does not execute.
- C: Your code runs the tool and sends the result.
- D: The id links result to request.
- E: Output belongs in `tool_result`.

**Source:** tool_use / tool_result

## MA-k01.9

A Python agent loop receives a response with `stop_reason == "tool_use"`. Which statements describe a correct next step? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Run the tool named in the `tool_use` block with its `input`, then send a `tool_result` with the matching id in the next user message.
- [ ] B. If the tool raised an error, return the error text in the `tool_result` so the model can adapt.
- [ ] C. Send the tool's output as an assistant message so the model sees it as its own words.
- [ ] D. Treat the response text as the final answer and stop the loop.
- [ ] E. Skip the `tool_result` and send a new prompt, since the model remembers what it asked for.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: That completes the loop turn.
- B: Errors are observations the model can use.
- C: Results go back in a user message as `tool_result`.
- D: The stop reason says the model wants a tool run.
- E: A `tool_use` without a result breaks the conversation.

**Source:** tool_use / tool_result

## MA-k01.10

Which one-line instruction to Claude Code correctly compresses: "when the model asks to read a file, run the read and return the file contents to it"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Have the model read the file inside the prompt by pasting `tool_result` first."
- [ ] B. "Add a system prompt line saying files are visible."
- [ ] C. "Return a `tool_use` block containing the file text."
- [ ] D. "Handle `tool_use` for `read_file` by running it and returning a `tool_result` with the same `tool_use_id`."
- [ ] E. "Return the file text in `tool_result` content and set `is_error` only if the read failed."

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: The result follows a request; it is not pre-pasted by the model.
- B: That does not wire up any execution.
- C: `tool_use` is the request direction.
- D: It names both blocks and the link.
- E: This keeps success and failure distinct.

**Source:** tool_use / tool_result

## MA-k01.11

A requirement says: "Add an approval gate before the agent deletes anything." Which statements unpack it into checkable conditions? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The approval request names the exact path or ids to be deleted.
- [ ] B. The delete call does not run until a person gives an explicit yes recorded for that action.
- [ ] C. The agent writes a log line saying it is about to delete, then continues.
- [ ] D. A test shows that with approval denied, the file still exists.
- [ ] E. The model is told to ask, and the code also blocks the delete call until approval is recorded.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: An approver must see what is being approved.
- B: A gate blocks until approval.
- C: A log without a pause is not a gate.
- D: Denial must leave state unchanged.
- E: Enforcement sits in code.

**Source:** approval gate

## MA-k01.12

A Claude Code session runs shell commands. Which setup is an approval gate for `git push`? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A hook that exits non-zero on `git push` until an approval flag exists.
- [ ] B. A permission rule set to ask, so each `git push` pauses for a person to confirm before it runs.
- [ ] C. A line in CLAUDE.md saying "please do not push without asking".
- [ ] D. A pre-run plan that lists a push as step 5, with no stop at that step.
- [ ] E. A system message reporting each push after it finished.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: Code enforces the pause.
- B: The tool call waits for a human.
- C: This is advice; nothing blocks the command.
- D: Listing a step does not gate it.
- E: Notification after the fact does not gate.

**Source:** approval gate

## MA-k01.13

An agent drafts customer emails and a manager must sign off. Which statements place the approval gate correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Between draft creation and the send call, with send disabled until approval is recorded.
- [ ] B. At the start of the session, once, covering the emails the agent drafts later.
- [ ] C. At the send step the approver sees the final recipient list and text, not only the template.
- [ ] D. Inside the model's reply, by asking itself whether the email is fine.
- [ ] E. After the emails are sent, the manager receives a summary to review.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: The consequential step sits behind the gate.
- B: Blanket approval cannot cover unseen content.
- C: Approval covers what will actually happen.
- D: Self-approval is not an independent gate.
- E: The gate must come before the action.

**Source:** approval gate

## MA-k01.14

Claude Code is asked to "give the agent read access to the docs folder only." Which statements are a correct unpacking of that permission scope? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A path outside `docs/` reached through `../` is treated as outside the scope.
- [ ] B. A test asks the agent to read `src/main.py` and the call is refused.
- [ ] C. The agent may read the rest of the repo once it has opened one file in `docs/`.
- [ ] D. Read tools may open files under `docs/`, and write and shell tools are not granted.
- [ ] E. The agent may edit files in `docs/` since it already reads them.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Scope checks use the resolved path.
- B: Out-of-scope reads must fail.
- C: Scope is per target, not inherited by touching a file.
- D: Scope names allowed actions on the target.
- E: Reading does not confer writing.

**Source:** permission scope

## MA-k01.15

Which one-line instruction best compresses: "the agent may run the test suite but not install packages or touch the network"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Allow `pytest` as the only shell command and deny `pip`, `curl` and network access."
- [ ] B. "Grant the Bash tool and approve each command by hand."
- [ ] C. "Run in a sandbox so mistakes are less serious."
- [ ] D. "Scope Bash to cover the shell commands the task might need, with network off."
- [ ] E. "Give the agent full shell access, and tell it not to install anything."

**Key:** A=T B=F C=F D=F E=F

**Why:**

- A: Names allowed command and denied ones.
- B: A gate on every command is not the same scope.
- C: A sandbox can still allow installs and network.
- D: The test command alone is the stated bound.
- E: The prompt asks; the scope still allows.

**Source:** permission scope

## MA-k01.16

A reviewer says the agent's permission scope is too broad. Which findings support that? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The file tool accepts any absolute path rather than a configured root.
- [ ] B. The agent logs each tool call it makes.
- [ ] C. The agent holds a database credential that can drop tables, though the task only reads rows.
- [ ] D. The agent asks for approval before each file edit.
- [ ] E. The agent has a read tool for a folder the task needs.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Scope reaches beyond the task.
- B: Logging does not widen what it can do.
- C: Write power exceeds the need.
- D: A gate narrows effective action.
- E: That matches the need.

**Source:** permission scope

## MA-k01.17

A team wants the model to answer from last week's policy PDFs, which change often. Which statements pick and unpack the approach correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A check is to edit one policy sentence and see the answer change without retraining.
- [ ] B. Retrieval fits: fetch the current passages and place them in the context at question time.
- [ ] C. Fine-tuning fits better, since updating weights after each PDF change is cheap and instant.
- [ ] D. The answer should cite the retrieved passage so a reader can verify it.
- [ ] E. Retrieval changes the model's weights so the policy stays after the session.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Retrieval changes behaviour without weight updates.
- B: Fresh content enters through the context.
- C: Fine-tuning is slow and does not track daily changes well.
- D: Citations make the grounding checkable.
- E: Retrieval leaves weights unchanged.

**Source:** retrieval vs fine-tuning

## MA-k01.18

A support bot must always reply in a fixed house format with a consistent tone, across thousands of unlike questions. Which statements are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Fine-tuning on examples of the target format can teach the style by changing weights.
- [ ] B. Fine-tuning is the way to add facts that did not exist at training time and change weekly.
- [ ] C. A system prompt with the format and a few examples is a cheaper first attempt before training.
- [ ] D. Retrieval of a style guide is required, because weights cannot hold a format.
- [ ] E. Retrieval and fine-tuning both update the weights, differing in how much data they use.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Style and format are learned behaviour.
- B: That is a retrieval need.
- C: Try the lighter option first.
- D: Weights can hold a format; retrieval is optional.
- E: Only fine-tuning updates weights.

**Source:** retrieval vs fine-tuning

## MA-k01.19

Claude Code is told: "Build the question answering over our wiki with retrieval, not fine-tuning." Which statements are checkable conditions for that? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The model is asked to recall the wiki from memory of its training data.
- [ ] B. The wiki content is stored in the model after indexing, so deleting a page needs retraining.
- [ ] C. At question time the code searches the wiki and puts the top passages into the prompt.
- [ ] D. A training job writes a new checkpoint of the model.
- [ ] E. Model weights are updated after each wiki page is added.

**Key:** A=F B=F C=T D=F E=F

**Why:**

- A: That is not retrieval.
- B: Content lives in the index, not in weights.
- C: That is retrieval.
- D: That would be fine-tuning.
- E: That is fine-tuning.

**Source:** retrieval vs fine-tuning

## MA-k01.20

A user complains: "Claude forgot what we agreed yesterday." Which statements use context window and memory correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A larger context window means the model keeps facts from yesterday's session.
- [ ] B. Memory, as in a CLAUDE.md or notes file, is saved text loaded into a new session's context.
- [ ] C. A fix is to write the agreement into a file and load it at session start.
- [ ] D. Memory is the part of the weights that stores the user's earlier chats.
- [ ] E. The context window holds the tokens the model sees in this request.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: The window does not carry over between sessions.
- B: Memory is stored outside and re-injected.
- C: That carries it across sessions.
- D: Weights are not updated by chats.
- E: That is its definition.

**Source:** context window vs memory

## MA-k01.21

Claude Code's long session starts dropping early instructions as it grows. Which statements judge the situation correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Adding more rules to the chat is the same as saving them to memory.
- [ ] B. Putting the key rules in CLAUDE.md reloads them into the context at each session start.
- [ ] C. Restarting the model process raises the window size.
- [ ] D. The memory file is full, so it should be emptied.
- [ ] E. The conversation may be exceeding what fits in the context window, so earlier content is trimmed or summarized.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: Chat text is lost when the window rolls over.
- B: Standing rules belong in memory text.
- C: Window size is set by the model.
- D: The symptom concerns the window.
- E: The window is finite.

**Source:** context window vs memory

## MA-k01.22

Which one-line instruction best compresses: "remember this preference for future sessions"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Save this preference to CLAUDE.md so it loads at the start of each session."
- [ ] B. "Fine-tune the model on this preference."
- [ ] C. "Keep this in the context window."
- [ ] D. "Increase the context window to 1M tokens."
- [ ] E. "Write this to the project memory file and confirm the file contents."

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Saved text is memory.
- B: Weights are not the route for a user note.
- C: The window clears with the session.
- D: A bigger window does not persist anything.
- E: It names the store and a check.

**Source:** context window vs memory

## MA-k01.23

A developer says: "Add a test for the prompt that classifies tickets." The model's labels vary a little between runs. Which statements place test and eval correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Running the prompt on three tickets and reading the answers once is an eval.
- [ ] B. A test is a fixed pass or fail check, such as asserting the output is one of the allowed labels.
- [ ] C. An eval runs many labelled tickets and reports a score such as accuracy.
- [ ] D. An eval is a test with a fixed expected string, where a difference fails it.
- [ ] E. Checking the output parses as JSON with the field `label` is a test.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: No scoring against criteria is defined.
- B: Tests assert exact conditions.
- C: Scoring over a set is an eval.
- D: An eval scores quality over varying output.
- E: A structural pass or fail check.

**Source:** eval vs test

## MA-k01.24

Which requirements correctly call for an eval rather than a plain test? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Compare two prompts on 200 labelled cases and pick the higher scoring one."
- [ ] B. "The function `parse_date` returns `2026-11-08` for `Nov 8, 2026`."
- [ ] C. "At least 90% of summaries must cover the three required facts, scored by a rubric."
- [ ] D. "The file exists after the build step."
- [ ] E. "The API response status is 200 for a valid request."

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: Comparison by score is eval.
- B: That is an exact unit test.
- C: Graded quality over a set.
- D: A binary check, a test.
- E: Fixed pass or fail check.

**Source:** eval vs test

## MA-k01.25

Claude says "I added an eval for the extractor" and shows one `assert extract("a") == "b"` in `test_extract.py`. Which statements judge this? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An eval would add a labelled set and a scoring rule with a threshold.
- [ ] B. A follow-up instruction: "Write the eval set of 50 labelled cases and report accuracy."
- [ ] C. It is an eval, since it checks model behaviour.
- [ ] D. It is a test: one fixed input and exact expected output.
- [ ] E. It is acceptable as evidence of quality across inputs, since it passed.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: Those are the missing parts.
- B: That turns the claim into evidence.
- C: One exact assertion is a test.
- D: Pass or fail on a fixed case.
- E: One case says little about the rest.

**Source:** eval vs test

## MA-k01.26

A user tells Claude: "Make the generations less random." Which statements unpack this into settings correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Raise top-p to 1.0, which restricts sampling to the single most likely token.
- [ ] B. Raise the temperature, since a high value makes the model more careful.
- [ ] C. Lower the temperature, which sharpens the token probabilities toward the likeliest tokens.
- [ ] D. Lower top-p, which shrinks the set of tokens that can be sampled.
- [ ] E. Set `max_tokens` low, which makes each token choice more predictable.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: Top-p 1.0 allows the full distribution.
- B: High temperature flattens probabilities.
- C: That is what temperature does.
- D: A smaller nucleus reduces variety.
- E: Length cap does not change choice.

**Source:** temperature / top-p

## MA-k01.27

Which one-line instruction best compresses: "I want the same answer on every run, as far as the API allows"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Add `be consistent` to the prompt and leave sampling alone."
- [ ] B. "Set temperature to 0 and keep the prompt text fixed."
- [ ] C. "Set temperature to 0.9 and a seed, and expect identical answers."
- [ ] D. "Use greedy decoding by setting temperature to 0."
- [ ] E. "Set top-p to 1 and temperature to 1 for balance."

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Sampling settings are not changed.
- B: Removes most sampling variation.
- C: High temperature still diverges; a seed may not exist for all APIs.
- D: Greedy picks the top token each step.
- E: That keeps the full distribution.

**Source:** temperature / top-p

## MA-k01.28

A brainstorming tool needs varied but not wild ideas. Which settings choices are correct? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Top-p limits sampling to the smallest set of tokens whose probabilities add to p.
- [ ] B. Top-p scales the logits before softmax, the same operation as temperature.
- [ ] C. Temperature 2 with top-p 1, since extremes give the best ideas.
- [ ] D. A moderate temperature with top-p below 1, which allows variety while cutting very unlikely tokens.
- [ ] E. Temperature 0, because variety needs one answer per prompt.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: That is nucleus sampling.
- B: Temperature scales logits; top-p truncates the set.
- C: Very high settings give incoherent text.
- D: Both controls play a part.
- E: That gives the least variety.

**Source:** temperature / top-p

## MA-k01.29

A ticket says "the export should be fast and correct." Which statements turn this into acceptance criteria? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "The code passes review by the lead."
- [ ] B. "The export feels responsive to users."
- [ ] C. Each criterion is written before the work starts, so it can decide acceptance.
- [ ] D. "Exports of 10,000 rows finish in under 5 seconds on the CI machine."
- [ ] E. "The CSV has a header row and the row count equals the source table's count."

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: That is a process step, not a condition on the result.
- B: Subjective; no check.
- C: Criteria precede the work.
- D: Measurable condition.
- E: A checkable correctness condition.

**Source:** acceptance criteria

## MA-k01.30

Which one-line instruction best gives Claude Code the acceptance criteria for a login fix? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Done when a wrong password returns 401, a right one returns a token, and the new tests pass."
- [ ] B. "Improve login code quality as much as possible."
- [ ] C. "Make login work properly."
- [ ] D. "Accept the change only if `pytest tests/test_login.py` passes and no other file changes."
- [ ] E. "Fix login and tell me when you feel it is solid."

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Three checkable conditions.
- B: No endpoint to judge.
- C: No check is named.
- D: A command and a scope condition.
- E: Relies on the agent's feeling.

**Source:** acceptance criteria

## MA-k01.31

The agent reports "done". Which statements show a gap in acceptance criteria rather than in the work? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The task said "make it better" and the agent chose its own bar for done.
- [ ] B. The criterion "should be robust" cannot be checked by any command.
- [ ] C. The criteria were written after the agent finished, shaped to match its output.
- [ ] D. The task listed three criteria and the output fails one of them.
- [ ] E. The task never stated what output would count as success, so "done" has no test.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: The bar was not set beforehand.
- B: Not checkable.
- C: Criteria must precede the result.
- D: That is a work failure.
- E: No criteria.

**Source:** acceptance criteria

## MA-k01.32

A user asks Claude Code: "Do a diff review of your change." Which statements unpack this correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Confirm each removed line was meant to be removed.
- [ ] B. Run the eval set and report the score.
- [ ] C. Rerun the whole task from the start and compare the new output with the old one.
- [ ] D. Flag any changed file the task did not mention.
- [ ] E. Read the lines added and removed and compare each against the requirements.

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: Deletions need intent.
- B: Evaluation measures behaviour; a diff review reads the change.
- C: That is a rerun, not a review.
- D: Scope check.
- E: That is what the review covers.

**Source:** diff review

## MA-k01.33

Claude's summary says "small refactor of `utils.py`." The diff touches `utils.py`, `config.py` and deletes a test. Which statements are the right review findings? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The diff is too long to review, so approve on the summary.
- [ ] B. The summary matches the diff, as `utils.py` was changed.
- [ ] C. A follow-up: "Explain why `config.py` changed and restore the deleted test, or justify removing it."
- [ ] D. Deleting a test is acceptable in a refactor when the remaining tests pass.
- [ ] E. The summary does not match the diff: two other files changed and a test was deleted.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: Review needs the diff.
- B: Other changes go unmentioned.
- C: Asks for evidence and scope control.
- D: A passing suite without that test hides lost coverage.
- E: Claim and code differ.

**Source:** diff review

## MA-k01.34

Which one-line instruction best compresses: "before I accept, show me exactly what changed and whether each change belongs to the task"? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Commit the work with a clear message."
- [ ] B. "Show `git diff` and map each hunk to a requirement; list anything outside the task."
- [ ] C. "Run the tests and tell me if they pass."
- [ ] D. "Summarize what you did in one paragraph."
- [ ] E. "Print the diff and mark hunks that have no requirement behind them."

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: Commit does not review.
- B: Names the artifact and the mapping.
- C: Tests do not reveal unrelated edits.
- D: A summary is the agent's own description.
- E: Same check, other wording.

**Source:** diff review

## MA-k01.35

A user tells Claude Code: "Plan before acting, then change the billing module." Which statements unpack this into checkable conditions? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. After approval, the diff is checked against the files named in the plan.
- [ ] B. The agent reads files and writes a plan listing files to change, without editing anything.
- [ ] C. The plan counts as finished once it exists, whatever it says.
- [ ] D. The agent edits the files while writing the plan, so the plan matches the edits.
- [ ] E. A person approves or amends the plan before the first edit.

**Key:** A=T B=T C=F D=F E=T

**Why:**

- A: The plan becomes a scope standard.
- B: Planning stage is read-only.
- C: An unreviewed plan is not a gate.
- D: Edits happened before approval.
- E: The plan is a checkpoint.

**Source:** planning before acting

## MA-k01.36

Which tasks justify requiring a plan before acting in Claude Code? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Printing the current directory.
- [ ] B. Renaming a function used in 40 files across several packages.
- [ ] C. Changing a database migration that has already run in production.
- [ ] D. Reformatting a single local variable name.
- [ ] E. Fixing a typo in a README sentence.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Trivial, read-only.
- B: Wide reach, so scope needs agreement first.
- C: Hard to undo; plan first.
- D: Low risk and local.
- E: A plan adds little.

**Source:** planning before acting

## MA-k01.37

An agent's plan says: "Step 3: update everything that needs updating." Which statements judge the plan? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. It is too vague to approve, since it names no files or conditions.
- [ ] B. It is a good plan, since it leaves room for judgment.
- [ ] C. A follow-up: "List the files for step 3 and what changes in each."
- [ ] D. A good step names the file, the change and a check that it worked.
- [ ] E. Approve it and compare with the diff if something breaks.

**Key:** A=T B=F C=T D=T E=F

**Why:**

- A: Cannot be reviewed against a diff.
- B: It has no checkable content.
- C: Makes the step reviewable.
- D: Plan steps need checks.
- E: Review should come before and after.

**Source:** planning before acting
