# Jargon test: saying it exactly to Claude Code

## MA-j07.1

A user types to Claude Code: "Look at what you changed and tell me if it's okay." Decide which statements correctly name the vague words or improve the prompt. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "What you changed" is called the diff: the lines added and removed compared with before.
- [ ] B. A diff is a saved snapshot of the whole project at one moment.
- [ ] C. "Review" in this prompt means running a model eval over a set of cases.
- [ ] D. Reading the diff and judging it against requirements is a diff review.
- [ ] E. A more exact prompt is: "Show me the diff and review it against the acceptance criteria below."

**Key:** A=T B=F C=F D=T E=T

**Why:**

- A: A diff shows the difference between two versions.
- B: A snapshot is a commit or checkpoint; a diff is the difference.
- C: A diff review is a reading of one change.
- D: Review means checking the change, not rerunning the whole task.
- E: It names the artifact and the standard.

**Source:** diff, diff review

## MA-j07.2

A user types: "Save my work." after Claude Code has edited several files, and wants the changes recorded in the project's history. Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Committing and pushing are two names for the same step.
- [ ] B. "Commit these changes with a message that says why" names the wanted action exactly.
- [ ] C. "Save my work" is exact, since saving and committing mean the same thing.
- [ ] D. Saving a file in an editor creates a commit.
- [ ] E. In git, recording staged changes with a message in the project history is a commit.

**Key:** A=F B=T C=F D=F E=T

**Why:**

- A: Commit records locally; push sends commits to a remote.
- B: It uses the exact term and asks for a message.
- C: They are different actions.
- D: Saving writes the file; a commit is a separate step.
- E: A commit is a named entry in history.

**Source:** commit

## MA-j07.3

A user types: "Fix the whole project's login problem." Decide which statements about scope are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Scope means the number of tokens that Claude is allowed to use.
- [ ] B. Naming the scope up front makes the diff easier to review.
- [ ] C. "Fix the token check in auth/login.py and leave the other files unchanged" gives a tighter scope.
- [ ] D. "The whole project" is a precise scope because it covers the most ground.
- [ ] E. Scope is the boundary of what a task covers, such as which files and behaviours it touches.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: That would be a limit on length, not scope.
- B: A small, bounded change is easier to check.
- C: It names a place and a boundary.
- D: Breadth makes a scope loose, not precise.
- E: Scope tells the agent where to work.

**Source:** scope

## MA-j07.4

A user types: "Open the folder utils.py and change the directory called parse.py." Decide which statements name the terms correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A directory holds files and other directories.
- [ ] B. A file holds content, and utils.py is a file.
- [ ] C. In everyday use, folder is another name for directory.
- [ ] D. A name ending in .py names a directory.
- [ ] E. An exact rewrite is: "Open the file utils.py in the src directory and change the file parse.py."

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: A directory is a container.
- B: A file is a single named unit of content.
- C: The two words refer to the same thing.
- D: The .py ending marks a Python file.
- E: It uses file for content and directory for containers.

**Source:** file vs directory

## MA-j07.5

A user types to Claude Code: "Write an eval to check that my sort function returns [1, 2, 3] for [3, 1, 2]." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Write a test for the sort function" is the exact request.
- [ ] B. Eval is the right word here because a language model is writing it.
- [ ] C. A test result is repeatable, while an eval over sampled output is reported as a rate or score.
- [ ] D. The request describes a test: a fixed expectation that passes or fails.
- [ ] E. An eval fits scoring Claude's summaries across many cases against a rubric.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: It names a deterministic check.
- B: The word depends on what is checked, not on who writes it.
- C: One is a pass or fail; the other a measurement.
- D: A known input with a known output is a test.
- E: Outputs that vary need scoring over a set.

**Source:** test vs eval

## MA-j07.6

A user types: "Let Claude use the Bash tool without asking me." Decide which statements use tool and permission correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Granting a permission installs the tool.
- [ ] B. An exact rewrite is: "Add an allow permission rule for running the test command with the Bash tool."
- [ ] C. A permission is the capability itself, meaning what Claude can do.
- [ ] D. Bash is a tool: a capability Claude can call.
- [ ] E. Allowing it without asking is a permission rule, set to allow, about that tool.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: A permission controls use; it does not add a tool.
- B: It names the tool, the rule and the scope of the rule.
- C: That describes the tool.
- D: A tool is something the model can invoke.
- E: A permission governs whether a tool may be used.

**Source:** tool vs permission

## MA-j07.7

A user types in a chat: "Remember to use tabs in every file." In a new session, Claude Code uses spaces. The user says "it has no memory." Decide which statements name the parts correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. CLAUDE.md is a memory file that Claude Code reads at the start of a session.
- [ ] B. A message typed in the chat is automatically written to CLAUDE.md.
- [ ] C. A better prompt is: "Add a rule to CLAUDE.md that files use tabs."
- [ ] D. Context and a memory file are two names for the same store.
- [ ] E. Context is the text currently in the window for this session, and a new session does not carry it over.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: It carries standing instructions between sessions.
- B: The user has to ask for the rule to be added to the file.
- C: It puts the rule in the memory file.
- D: One is the current window and the other is a file read into it.
- E: Context is per session.

**Source:** memory file (CLAUDE.md) vs context

## MA-j07.8

A user types: "Have another Claude dig through the logs so this chat doesn't fill up." Decide which statements about a subagent are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A subagent shares the parent's context window, so it sees the whole chat.
- [ ] B. A subagent is a separate Claude instance with its own context window that takes a task and returns a result.
- [ ] C. A subagent is another name for a slash command.
- [ ] D. Sending a long search to a subagent keeps the main context smaller.
- [ ] E. Delegating to a subagent hands accountability for the result to the subagent.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Its separate context is the point.
- B: A subagent works apart and reports back.
- C: A slash command is typed by the user; a subagent is a delegated worker.
- D: Only the summary returns to the parent.
- E: The person stays accountable.

**Source:** subagent

## MA-j07.9

A user types: "Every time you edit a Python file, run the formatter." Claude sometimes forgets. Decide which statements about a hook are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A hook is a command that Claude Code runs automatically at a defined event, such as after a tool is used.
- [ ] B. A hook runs when the model decides to call it.
- [ ] C. A hook is a prompt that the model chooses whether to follow.
- [ ] D. The exact request is: "Configure a hook on file edits that runs the formatter."
- [ ] E. A hook is a command that the user types starting with a slash.

**Key:** A=T B=F C=F D=T E=F

**Why:**

- A: Hooks are tied to events.
- B: A hook fires on the event, whether or not the model remembers.
- C: A hook is a command run by the harness, not advice.
- D: It names the mechanism and the event.
- E: That is a slash command.

**Source:** hook

## MA-j07.10

A user wants to type /review and send the same instructions each time. Decide which statements about slash commands are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A slash command is the same as a subagent.
- [ ] B. A slash command fires automatically when an event happens, as a hook does.
- [ ] C. A slash command changes the model's weights.
- [ ] D. A slash command starts a separate Claude with its own context window.
- [ ] E. A slash command is invoked by the user typing a name that starts with a slash.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: A subagent is a separate worker with its own context.
- B: A user invokes a slash command; a hook is event-triggered.
- C: It sends a prompt; it does not train.
- D: It runs in the current session.
- E: The user decides when it runs.

**Source:** slash command

## MA-j07.11

A user types: "Go back to how things were before that last change." Decide which statements about checkpoints and commits are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. In Claude Code, a checkpoint records the state of files before Claude's edits so the user can rewind.
- [ ] B. A commit is a deliberate entry in git history, which is different from a checkpoint taken before an edit.
- [ ] C. A checkpoint is another word for a commit message.
- [ ] D. In model training, a checkpoint is a snapshot of weights and optimizer state, which is the same word with a different meaning.
- [ ] E. In Claude Code, a checkpoint also saves the model's weights.

**Key:** A=T B=T C=F D=T E=F

**Why:**

- A: It is an undo point.
- B: A checkpoint is a safety net; a commit is a record.
- C: A commit message is text that describes a commit.
- D: The word is reused in training.
- E: Weights are not part of a project state.

**Source:** checkpoint vs commit

## MA-j07.12

A user types: "Make sure it works." Decide which statements about verification and acceptance criteria are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Acceptance criteria are stated before the work, so they can be checked afterward.
- [ ] B. Verification is checking a result against evidence that can be confirmed apart from the producer, such as a test run.
- [ ] C. Claude replying "done, it works" is verification.
- [ ] D. A more exact prompt is: "Make the failing test pass, run the suite, and show me the output."
- [ ] E. Acceptance criteria are stated conditions for accepting the result, such as: the existing tests pass and the page loads without console errors.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Setting them afterward makes them fit the result.
- B: Evidence beats a claim.
- C: That is a claim by the producer.
- D: It names a check and the evidence to show.
- E: They define done.

**Source:** verification, acceptance criteria

## MA-j07.13

A user types: "Just start changing things in the repo and figure it out as you go." Decide which statements about planning before acting are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Planning before acting is the same as the model's hidden reasoning.
- [ ] B. In plan mode, Claude Code researches without editing and presents a plan for approval.
- [ ] C. Planning before acting means proposing steps and reviewing them before a change is made.
- [ ] D. A plan that a person approved needs no diff review afterward.
- [ ] E. Plan mode lets Claude edit files while it thinks.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: A plan is a visible proposal that a person can review.
- B: Plan mode is read-only until approved.
- C: The plan is reviewed first.
- D: A diff review checks that the change matches the plan.
- E: Editing waits for approval.

**Source:** plan mode, planning before acting

## MA-j07.14

A user's request is: "Make the app better and save it." Decide which rewrites use the terms exactly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Add a hook so you remember that rounding should be fixed."
- [ ] B. "In the file src/cart.py, fix the rounding in total(); show me the diff, and I will commit after review."
- [ ] C. "Write an eval that checks total() returns 10.50 for items of 5.25 and 5.25."
- [ ] D. "Enter plan mode and edit the cart file to fix rounding, then show me the plan."
- [ ] E. "In the directory src/cart.py, fix the rounding; show me the commit before you edit."

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: A hook runs a command on an event; a memory file holds a rule.
- B: File, diff and commit are each used for the right thing.
- C: A fixed expected output is a test, not an eval.
- D: Plan mode comes before editing, and the plan comes before the change.
- E: cart.py is a file, and a commit cannot be shown before an edit.

**Source:** exact rewrite

## MA-j07.15

In a long session, Claude Code ignores an instruction the user gave near the start. Decide which statements name the cause and the fix correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The context window is permanent storage that carries across sessions.
- [ ] B. The context window is the limited amount of text the model considers at once.
- [ ] C. In a long session, early messages can be dropped or compressed so they carry less weight.
- [ ] D. Putting a standing rule in CLAUDE.md loads it into the context at the start of a session.
- [ ] E. Starting a subagent erases the parent's context.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: Permanent storage across sessions is a file such as CLAUDE.md.
- B: Everything has to fit inside it.
- C: Long context tends to dilute early text.
- D: The memory file is read into context.
- E: A subagent has its own context and leaves the parent's alone.

**Source:** context vs memory file

## MA-j07.16

A user types: "Clean up the repo and push it." Decide which statements are true. Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Pushing is the step that creates a commit.
- [ ] B. A commit records changes locally, and a push sends commits to a remote.
- [ ] C. "Clean up" lacks a scope, so the prompt should name the files and the kind of change.
- [ ] D. Pushing to a shared remote needs no approval gate.
- [ ] E. "Clean up" is an acceptance criterion.

**Key:** A=F B=T C=T D=F E=F

**Why:**

- A: Committing creates the commit.
- B: These are two steps.
- C: A bounded request is easier to carry out and check.
- D: Pushing affects shared state, so a person's approval before it is reasonable.
- E: It is a vague instruction; a criterion is a checkable condition.

**Source:** scope, commit vs push
