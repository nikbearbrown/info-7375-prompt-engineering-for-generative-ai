# Jargon test: false friends


## MA-k03.1

A Python script sorts employee records by salary and then sorts the result by department. The team wants records grouped by department, with salary order kept inside each department. Which statements about "stable" in this sort are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Sorting by salary first and then by department gives the wanted grouping because the second sort is stable.
- [ ] B. If the second sort were unstable, the two-pass approach would still keep salary order inside each department.
- [ ] C. "Stable" here means the sort returns the same output when run on different inputs.
- [ ] D. "Stable" here means the sort does not crash on large lists.
- [ ] E. Python's sorted keeps the original relative order of items whose keys are equal.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Ties in department keep the salary order.
- B: An unstable sort may reorder equal departments, so a single combined key would be needed.
- C: Stability is about ties within one input.
- D: It describes tie order, not robustness.
- E: Equal keys keep their earlier order.

**Source:** stable (sort)

## MA-k03.2

A vendor release note says an endpoint of the Claude API is "stable", and a developer wants to build a client on it. Which statements about this sense of "stable" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. "Stable" in an API and "stable" in a sort name the same property.
- [ ] B. A stable API returns the same response time on each call.
- [ ] C. Pinning a dated model snapshot is a way to keep model behaviour steady between releases.
- [ ] D. A stable API keeps its documented fields and behaviour compatible across versions so existing clients keep working.
- [ ] E. A stable endpoint means the model returns identical text for repeated calls.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: Tie order versus compatibility.
- B: Latency is a different property.
- C: A pinned snapshot does not change under the client.
- D: Stable means compatibility.
- E: Output variation comes from sampling, not API stability.

**Source:** stable (API)

## MA-k03.3

A Python function updates a config file by writing to a temporary file in the same folder and then calling os.replace to put it over the real file. A reader may open the config at any moment. Which statements about "atomic" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Opening the config in "w" mode and writing it directly is atomic because Python does it in one call.
- [ ] B. An atomic update either completes in full or leaves no visible change to other readers.
- [ ] C. An atomic write is seen by readers as either the old file or the new file, never a mixture.
- [ ] D. In planning, an "atomic task" means a small step that can be checked alone, which is a different sense from an atomic write.
- [ ] E. Writing a temp file and then os.replace onto the target is a common way to get an atomic file update on one filesystem.

**Key:** A=F B=T C=T D=T E=T

**Why:**

- A: A reader can see a truncated or half-written file.
- B: No partial state is visible.
- C: Readers never see a partial file.
- D: Two senses of the same word.
- E: The replace step is a single rename.

**Source:** atomic (file write)

## MA-k03.4

A user tells Claude Code: "Make each commit atomic." The branch currently has one commit that fixes a bug and renames three modules. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The mixed bug-fix and rename commit already satisfies the request.
- [ ] B. An atomic commit is applied by git as a database transaction that rolls back on failure.
- [ ] C. Atomic commits make review and revert easier because each can be undone on its own.
- [ ] D. In git, an atomic commit holds one logical change.
- [ ] E. An atomic commit has the fewest lines possible.

**Key:** A=F B=F C=T D=T E=F

**Why:**

- A: It should be split into a fix commit and a rename commit.
- B: That is the database sense, not the git sense.
- C: Separate changes revert separately.
- D: One change per commit.
- E: Size is not the test; one logical change is.

**Source:** atomic (commit)

## MA-k03.5

A Python tool returns a dictionary that includes a datetime value, and the result must be sent back to Claude as a tool_result. Which statements about "serializable" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A tool_result accepts a Python dict object directly without conversion.
- [ ] B. Serializable here means convertible to a text or byte format such as JSON and back.
- [ ] C. json.dumps converts a datetime object without any extra handling.
- [ ] D. Passing a default= function to json.dumps is one way to convert types it cannot handle.
- [ ] E. Serializable isolation in a database is the same property as an object being JSON-serializable.

**Key:** A=F B=T C=F D=T E=F

**Why:**

- A: Content is text or blocks, so convert first.
- B: This is the data sense.
- C: It raises TypeError.
- D: The function is called for unknown types.
- E: Different meaning.

**Source:** serializable (data)

## MA-k03.6

Two database transactions each read an account balance of 100, check that a withdrawal of 80 is allowed, and then subtract 80. The team wants only one to succeed. Which statements about "serializable" isolation are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Serializable isolation means each transaction's rows can be written to JSON.
- [ ] B. Serializable isolation works because Python's GIL runs the transactions on one thread.
- [ ] C. A weaker isolation level can let both transactions read 100 and both subtract, which is a lost update.
- [ ] D. Serializable isolation makes the outcome match some order of running the transactions one after another.
- [ ] E. Under serializable isolation the two withdrawals cannot both commit from the same starting balance of 100.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Wrong sense.
- B: The database enforces it, not the interpreter.
- C: This is the check-then-act race.
- D: That is the definition.
- E: One would abort or see the updated balance.

**Source:** serializable (isolation)

## MA-k03.7

A developer calls the Claude API with the same long system prompt and tool definitions on each request and wants lower cost and latency. Which statements about prompt caching are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Prompt caching reuses processing of an unchanged prompt prefix.
- [ ] B. Prompt caching stores Claude's earlier answers and returns them when the same question repeats.
- [ ] C. Changing a sentence near the start of the prefix breaks reuse for the text after it.
- [ ] D. Prompt caching teaches the model the cached text, as fine-tuning does.
- [ ] E. Putting the changing user text before the system prompt helps produce cache hits.

**Key:** A=T B=F C=T D=F E=F

**Why:**

- A: The prefix is the cached part.
- B: It caches input processing, not answers.
- C: The cache matches from the beginning.
- D: Weights are not changed.
- E: Stable content goes first.

**Source:** cache (prompt caching)

## MA-k03.8

A Python function ask(question) calls Claude and is decorated with functools.lru_cache. The same question is asked twice with temperature 1. Which statements about this "cache" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Arguments to an lru_cache function need to be hashable, so passing a list raises TypeError.
- [ ] B. A cached function that depends on the current time or on external data can return stale values.
- [ ] C. lru_cache returns the stored result for the same arguments without running the function body again.
- [ ] D. Because temperature is 1, the second call returns a fresh, different answer.
- [ ] E. lru_cache and API prompt caching are the same mechanism.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Hashing is how entries are keyed.
- B: The cache does not know the world changed.
- C: Second call skips the model.
- D: The cached answer is returned.
- E: One is in your process, one is on the provider side.

**Source:** cache (lru_cache vs prompt)

## MA-k03.9

A user told Claude Code a rule an hour ago and Claude now ignores it. The session is very long. Which statements about "context" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Context is the tokens the model reads for a request, including earlier turns kept in the conversation.
- [ ] B. A fact stated once in the conversation is visible to the model only while it is still inside the window.
- [ ] C. A larger context window makes the model learn the rule permanently.
- [ ] D. When a conversation exceeds the context window, older content can be dropped or summarised, so the rule may no longer be seen.
- [ ] E. Moving the rule into CLAUDE.md puts it in context at the start of each session.

**Key:** A=T B=T C=F D=T E=T

**Why:**

- A: Context is the input.
- B: Once outside the window it is not seen.
- C: The window is not learning.
- D: Hence the lapse.
- E: Memory files are loaded at session start.

**Source:** context (window)

## MA-k03.10

A user asks Claude to "give the model more context" so a Python bug is diagnosed correctly. Which statements correctly unpack this request? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Adding context to a prompt changes the model's weights.
- [ ] B. Saying "you remember our earlier chats" supplies context from them even when they are not included.
- [ ] C. Pasting a whole log is as exact as naming the failing section, since the model reads all of it.
- [ ] D. Adding the failing file contents, the error text and the goal to the prompt adds context.
- [ ] E. In "context window", context is a limit measured in tokens.

**Key:** A=F B=F C=F D=T E=T

**Why:**

- A: It changes the input only.
- B: Absent text is not visible.
- C: Irrelevant text can crowd out the relevant lines.
- D: Context is what is in the prompt.
- E: Window size is counted in tokens.

**Source:** context (more context)

## MA-k03.11

A user says to Claude Code: "Remember that we use pytest, so you know it next week." Nothing else is configured. Which statements about "memory" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A CLAUDE.md file is discarded when the session that read it ends.
- [ ] B. A Python list of messages in RAM survives a restart of the script.
- [ ] C. Model weights update after each chat so the model remembers the user.
- [ ] D. Saying "remember this" to Claude Code writes it to durable storage on its own.
- [ ] E. Conversation history inside one session is context, not durable memory across sessions.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: The file stays on disk and is read again next session.
- B: Process memory is lost on exit.
- C: Weights are fixed at inference.
- D: Nothing is saved unless a file or store is written.
- E: It disappears when the session ends.

**Source:** memory (persistent vs context)

## MA-k03.12

A developer builds a Python agent for a support desk and wants it to recall customer preferences from last month. Which statements about "memory" in this design are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Appending notes to a JSON file that the agent reads at start is a memory store.
- [ ] B. Fine-tuning after each chat is the usual way to give an agent memory of one user.
- [ ] C. The API server stores your message list between calls, so the code need not resend it.
- [ ] D. Retrieving past notes into the prompt changes the model's weights so it remembers the customer.
- [ ] E. The message list sent in each API call is short-term conversation state that the code resends.

**Key:** A=T B=F C=F D=F E=T

**Why:**

- A: Notes persist outside the model.
- B: It is slow, costly and not per-user.
- C: The Messages API is stateless.
- D: Retrieval changes the input, not the weights.
- E: The code carries the state.

**Source:** memory (agent)

## MA-k03.13

A Python script calls Claude to classify a ticket, calls Claude again to draft a reply, and then sends the email, in that fixed order every run. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A fixed-path workflow is easier to test because the sequence of steps is predictable.
- [ ] B. Wrapping the three calls in a function named agent makes it an agent.
- [ ] C. A step in a workflow can call Claude with a prompt, and the program is still a workflow.
- [ ] D. This is a workflow because code fixes the steps.
- [ ] E. A system where Claude picks among tools and loops until it judges the task done is an agent.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Fewer paths to cover.
- B: A name does not give it a decision loop.
- C: Model calls inside fixed steps are allowed.
- D: Path set in advance.
- E: The model chooses the path.

**Source:** agent vs workflow (fixed)

## MA-k03.14

A team must handle support requests where the number and kind of steps differ per request, and one proposal uses an agent loop while another uses a fixed pipeline. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Work whose steps cannot be listed in advance fits an agent loop.
- [ ] B. Using an agent for a fixed three-step pipeline adds cost and variability for no gain.
- [ ] C. An agent loop needs no stop condition because the model decides when to end.
- [ ] D. Work with the same steps in the same order each run needs an agent loop, since a loop adapts.
- [ ] E. Switching from a workflow to an agent makes the outputs deterministic.

**Key:** A=T B=T C=F D=F E=F

**Why:**

- A: The model decides the next step.
- B: Over-engineering.
- C: A step or time limit is still set.
- D: A fixed path fits a workflow.
- E: It adds run-time variability.

**Source:** agent vs workflow (choice)

## MA-k03.15

A team uses Claude Code and wants to add capabilities. They are comparing a tool with a skill. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A skill is an API function that returns data from an external service.
- [ ] B. A tool_use block is how Claude requests a call to a tool.
- [ ] C. A skill is a packaged set of instructions, with optional scripts, that Claude loads when relevant.
- [ ] D. A tool is a callable function with a schema that Claude can invoke to take an action.
- [ ] E. Installing a skill gives Claude a permission it did not have.

**Key:** A=F B=T C=T D=T E=F

**Why:**

- A: That describes a tool.
- B: Request side of the exchange.
- C: Skills guide.
- D: Tools act.
- E: Permissions are set separately.

**Source:** tool vs skill

## MA-k03.16

A team wants Claude to follow its code-review checklist and also to look up ticket status in an internal ticket database. Which statements about choosing a skill or a tool are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A skill that is only text can read the ticket database without any tool.
- [ ] B. A skill can tell Claude how and when to use a tool.
- [ ] C. Looking up ticket status needs a tool, for example one exposed by an MCP server.
- [ ] D. Writing the checklist as a tool with a schema is the right form for text guidance.
- [ ] E. The checklist is instructions, so it fits a skill or CLAUDE.md.

**Key:** A=F B=T C=T D=F E=T

**Why:**

- A: Reading data takes a callable action.
- B: Instructions can reference tools.
- C: It requires an action.
- D: A tool is for action, not guidance.
- E: Text guidance.

**Source:** tool vs skill (choice)

## MA-k03.17

A Python program calls the Anthropic Messages API with a system parameter and a messages list. Which statements about "prompt" and "system prompt" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Prompt means only the text of the latest user message.
- [ ] B. The system parameter holds standing instructions such as role and rules for the conversation.
- [ ] C. A rule placed in the system prompt is enforced by the API, so the model obeys it.
- [ ] D. A user message in messages is treated as part of the system prompt.
- [ ] E. The system prompt is stored by the model and reused in other conversations.

**Key:** A=F B=T C=F D=F E=F

**Why:**

- A: Prompt can mean the whole input.
- B: System prompt is standing text.
- C: It guides, it does not guarantee.
- D: The system prompt is the separate system parameter.
- E: It is sent with each request.

**Source:** prompt vs system prompt

## MA-k03.18

A developer builds a Python app that pastes retrieved web pages into Claude's input, and one page contains the text "ignore your rules". Which statements about where to place text are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A system-prompt rule reduces the chance that pasted instructions change behaviour, so checks outside the prompt are still needed.
- [ ] B. Untrusted text belongs in the user turn, clearly delimited and labelled as data.
- [ ] C. Putting retrieved text in the system parameter would give any instructions in it standing authority.
- [ ] D. Putting retrieved text in the system parameter is a safe way to make Claude treat it as data.
- [ ] E. The system prompt is hidden from the model's view of the conversation.

**Key:** A=T B=T C=T D=F E=F

**Why:**

- A: Prompts are not enforcement.
- B: Delimiting reduces confusion.
- C: Placement affects weight.
- D: It does the opposite.
- E: The model reads it.

**Source:** system prompt vs untrusted text

## MA-k03.19

Claude's summary of a codebase cites a function parse_header that does not exist in the repository. Which statements about "hallucination" and "error" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A hallucination is fluent output that states something not supported by the source or the facts.
- [ ] B. An exception such as a 404 returned in a tool_result is an error, not a hallucination.
- [ ] C. A hallucinated claim can be checked by searching the repository for the named function.
- [ ] D. A syntax error in generated Python is a hallucination.
- [ ] E. Asking Claude "are you sure?" does not by itself verify a claim; a check against the repository does.

**Key:** A=T B=T C=T D=F E=T

**Why:**

- A: The cited function is unsupported.
- B: The tool reports it.
- C: Check against the source.
- D: It is an error caught by the interpreter.
- E: Self-confirmation is not independent evidence.

**Source:** hallucination vs error

## MA-k03.20

An agent reports "I updated config.yaml" but the file is unchanged, and another run of the agent hit a PermissionError from a write tool. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A PermissionError is fixed by telling the agent in the prompt to be more careful, with no change to permissions.
- [ ] B. Both problems are fixed by raising the temperature.
- [ ] C. A claimed update with no change on disk is a claim/code mismatch, a fabricated report.
- [ ] D. A PermissionError counts as a hallucination because the model did not predict it.
- [ ] E. Running git diff or listing the file is a check that settles the first claim.

**Key:** A=F B=F C=T D=F E=T

**Why:**

- A: A permission fault is fixed by scope or path.
- B: Sampling does not cause either.
- C: The claim lacks evidence.
- D: A tool reported a real error.
- E: Evidence beats assertion.

**Source:** hallucination vs error (agent)

## MA-k03.21

A team has a pytest suite for a function that parses model output into a dict and also has 200 graded questions for judging answer quality. Which statements about "test" and "evaluation" are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. An eval compares the output with one fixed expected string exactly.
- [ ] B. A passing pytest suite shows the answer quality is good.
- [ ] C. Running the evals removes the need for tests on the parsing code.
- [ ] D. An eval produces a single pass or fail for the whole run, as a test does.
- [ ] E. A test checks a fixed expectation with a pass or fail result, such as the parser returning the expected dict.

**Key:** A=F B=F C=F D=F E=T

**Why:**

- A: That is a test; evals score varying output.
- B: It only checks the code's fixed expectations.
- C: They check different things.
- D: Evals usually give scores or rates.
- E: Test = fixed pass/fail.

**Source:** evaluation vs test

## MA-k03.22

A user asks Claude Code: "Evaluate my prompt change." Which statements about writing an exact instruction and judging the result are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A held-out set not used while editing the prompt gives a fairer estimate of performance on new inputs.
- [ ] B. "Run pytest" evaluates the quality of the prompt.
- [ ] C. Using the same cases and the same scoring for both prompts makes the comparison fair.
- [ ] D. Tuning the prompt on the eval cases and then reporting those scores shows how it will do on new inputs.
- [ ] E. "Run the 200-case eval on the old and new prompt and report both scores" is an exact instruction.

**Key:** A=T B=F C=T D=F E=T

**Why:**

- A: Avoids tuning to the cases.
- B: Pytest checks fixed expectations of code.
- C: Only the prompt differs.
- D: That is overfitting to the cases.
- E: Names cases, versions and output.

**Source:** evaluation vs test (instruction)

## MA-k03.23

A developer writes a Python MCP server with FastMCP that exposes a search function, and Claude Desktop connects to it. Which statements about "server" and "client" in MCP are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. The client is the host application, such as Claude Desktop or Claude Code, that connects to servers and relays tool calls.
- [ ] B. The model's weights run inside the MCP server.
- [ ] C. One server can be connected to by more than one client application, such as Claude Desktop and Claude Code.
- [ ] D. The server exposes capabilities such as tools, resources and prompts.
- [ ] E. An MCP server can run locally on the user's machine and talk over stdio.

**Key:** A=T B=F C=T D=T E=T

**Why:**

- A: Client consumes.
- B: The model is separate.
- C: The server is a separate process that clients connect to.
- D: Server offers.
- E: Local servers are common.

**Source:** MCP server vs client

## MA-k03.24

A Python MCP server exposes a delete_file tool, and the team asks where to put controls. Which statements about MCP roles are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. A local stdio script is not an MCP server, since "server" means a remote machine.
- [ ] B. The server chooses which of the client's tools to run.
- [ ] C. A path allowlist inside the server adds a second control on what the tool can touch.
- [ ] D. An approval gate is usually placed in the client or host, before the tool call is sent.
- [ ] E. The client sends a tools/call request and the server returns the result.

**Key:** A=F B=F C=T D=T E=T

**Why:**

- A: Server is a role, not a location.
- B: The client side, with the model, chooses.
- C: Defence in two places.
- D: The host asks the user.
- E: Request and response.

**Source:** MCP approval and roles

## MA-k03.25

A bug report says "Claude deleted the file". The team wants to separate model from agent. Which statements are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Switching to a larger model changes a chat system into an agent.
- [ ] B. The word "Claude" names only the model, so a report need not say which layer acted.
- [ ] C. Fine-tuning a model produces an agent.
- [ ] D. An agent is a model combined with tools, instructions and a loop.
- [ ] E. A model has tool access built in, so it can run commands by itself.

**Key:** A=F B=F C=F D=T E=F

**Why:**

- A: Tools and a loop make an agent.
- B: It can name the model or a product that wraps it.
- C: Fine-tuning changes weights, not tools.
- D: Agent adds action.
- E: A model only produces tokens; tools come from the harness.

**Source:** model vs agent

## MA-k03.26

A Claude Code run deleted a file the user wanted to keep, and the team is deciding what to change. Which statements about model and agent are true? Check each statement that is true. Each statement is worth 1 point (5 points total).

- [ ] A. Changing the model version alone fixes the issue regardless of permission settings.
- [ ] B. The model proposed the tool call and the harness executed it.
- [ ] C. The deletion was carried out by the model's weights.
- [ ] D. If the permission scope allowed delete, the agent's configuration, not the model alone, decided what could run.
- [ ] E. A good report names the model version and the tool and permission configuration.

**Key:** A=F B=T C=F D=T E=T

**Why:**

- A: The permission still allows delete.
- B: Proposal versus execution.
- C: Weights only produce tokens.
- D: Scope sets what can happen.
- E: Both layers matter.

**Source:** model vs agent (attribution)
