# INFO 7375 Prompt Engineering for Generative AI: practice exam 05

**PRACTICE FORM. Drawn at random from the question bank; not the real exam; not signed off by the instructor.**

20 questions, 5 points each, 100 points. Name: ______________________

**Scoring.** Five statements, each true or false, 1 point each. The student checks the statements they believe are true. A statement scores 1 point if it is checked and true, or unchecked and false; otherwise 0. Read every statement on its own and decide whether it is true by itself. Strong words (always, never, every, proves) are often what makes a statement false, but a strong-sounding statement is not false for sounding strong.

---

**1.** A developer calls the Claude API with the same long system prompt and tool definitions on each request and wants lower cost and latency. Which statements about prompt caching are true? Check each statement that is true.  *(5 points)*

- [ ] A. Prompt caching reuses processing of an unchanged prompt prefix.
- [ ] B. Prompt caching stores Claude's earlier answers and returns them when the same question repeats.
- [ ] C. Changing a sentence near the start of the prefix breaks reuse for the text after it.
- [ ] D. Prompt caching teaches the model the cached text, as fine-tuning does.
- [ ] E. Putting the changing user text before the system prompt helps produce cache hits.

**2.** Which pairings of a described behaviour and a term are correct? Check each statement that is true.  *(5 points)*

- [ ] A. The raw output scores for each possible next token: logits.
- [ ] B. The step that turns scores into probabilities that add up to one: embedding.
- [ ] C. The largest amount of text the model can consider in one request: context window.
- [ ] D. Sampling among a fixed count of the most probable tokens: top-p.
- [ ] E. A string that ends generation when it appears: max tokens.

**3.** A developer writes to Claude Code: "Refactor the payments module, but propose a plan first and let me review the diff before anything is committed." Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. Diff review means asking Claude whether the code looks right.
- [ ] B. Proposing a plan first is planning before acting: the steps are stated before files are edited.
- [ ] C. Diff review means reading the line-level changes before accepting them.
- [ ] D. Naming a plan step and a review step makes the request more precise than writing "be careful".
- [ ] E. Planning before acting means making the edits first and explaining them afterwards.

**4.** An agent reports "All tests pass" after pytest prints `2 passed`. The two tests are `assert True` and one that imports the module. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. A larger count of passing tests matters more than what each one asserts.
- [ ] B. A pass only shows that the existing checks did not fail; its weight depends on what they assert.
- [ ] C. A test with no assertion on the changed behaviour fails when the change is broken.
- [ ] D. Passing tests mean the new function is verified.
- [ ] E. A good follow-up is: "Rerun pytest and paste the line that says passed."

**5.** A user sends Claude the vague request "Make the answer good and structured, and don't let people trick it." Which rewrites use the exact terms? Check each statement that is true.  *(5 points)*

- [ ] A. "State acceptance criteria: the reply cites a source line and stays under 100 words."
- [ ] B. "Specify an output schema with named fields."
- [ ] C. "Delimit the user-supplied text with tags and tell the model to treat it as data, to lower the risk of prompt injection."
- [ ] D. "Add a jailbreak to the system prompt to stop tricks."
- [ ] E. "Replace the persona with a delimiter."

**6.** A user types: "Just start changing things in the repo and figure it out as you go." Decide which statements about planning before acting are true. Check each statement that is true.  *(5 points)*

- [ ] A. Planning before acting is the same as the model's hidden reasoning.
- [ ] B. In plan mode, Claude Code researches without editing and presents a plan for approval.
- [ ] C. Planning before acting means proposing steps and reviewing them before a change is made.
- [ ] D. A plan that a person approved needs no diff review afterward.
- [ ] E. Plan mode lets Claude edit files while it thinks.

**7.** An agent's plan says: "Step 3: update everything that needs updating." Which statements judge the plan? Check each statement that is true.  *(5 points)*

- [ ] A. It is too vague to approve, since it names no files or conditions.
- [ ] B. It is a good plan, since it leaves room for judgment.
- [ ] C. A follow-up: "List the files for step 3 and what changes in each."
- [ ] D. A good step names the file, the change and a check that it worked.
- [ ] E. Approve it and compare with the diff if something breaks.

**8.** A server offers three things: the text of a database schema, an action that runs a query, and a saved weekly-report template the user can pick from a menu. Name the primitive for each. Check each statement that is true.  *(5 points)*

- [ ] A. The weekly-report template is a tool.
- [ ] B. The action that runs a query is a resource.
- [ ] C. The query action is a prompt.
- [ ] D. The database schema text is a resource.
- [ ] E. The schema text is a prompt.

**9.** A manager tells Claude: "Fine-tune the model on our policy PDFs so it has current policy, and change the parameters like temperature to be accurate." Which statements spot the imprecise wording? Check each statement that is true.  *(5 points)*

- [ ] A. "Fine-tune ... so it has current policy" is imprecise: documents that change call for retrieval, since fine-tuned knowledge is hard to update.
- [ ] B. "Parameters like temperature" is imprecise: temperature is a generation setting, not a learned parameter.
- [ ] C. "Policy PDFs" should be "logits".
- [ ] D. "Model" should be "chunk".
- [ ] E. Fine-tuning is the right term for looking up the PDFs at question time.

**10.** Two reviewers independently label 20 answers as supported or contradicted against their sources. They agree on 17 of the 20. Check each statement that is true.  *(5 points)*

- [ ] A. Agreement between independent reviewers is called inter-rater agreement.
- [ ] B. High agreement between reviewers shows the labels are correct.
- [ ] C. A chance-corrected statistic such as kappa adjusts agreement for what chance alone would produce.
- [ ] D. Raw agreement can look high by chance when one label is much more common than the other.
- [ ] E. Cases where the reviewers disagree are best left out of the report.

**11.** Check each statement that is true about permission and approval gate when Claude Code runs tools. Check each statement that is true.  *(5 points)*

- [ ] A. An approval gate is a point where a person confirms an action before it runs.
- [ ] B. Limiting an agent to tools that read but do not write limits what its mistaken actions can change.
- [ ] C. A step limit replaces the need for permissions.
- [ ] D. Permission and approval gate are two names for the same thing.
- [ ] E. A permission is a rule about which tool actions are allowed, denied or need a prompt.

**12.** Which statements tell tool_use and tool_result apart? Check each statement that is true.  *(5 points)*

- [ ] A. tool_use is the model's request to call a named tool with arguments.
- [ ] B. tool_result is what the program sends back after running the tool.
- [ ] C. tool_result is written by the model before the tool runs.
- [ ] D. tool_use means the tool has already finished.
- [ ] E. tool_use and tool_result are two names for a single message.

**13.** A manager assigns an AI agent to draft customer refunds, and a mistake occurs. Decide which statements about accountability and responsibility are true. Check each statement that is true.  *(5 points)*

- [ ] A. Delegating a task to another agent does not delegate the answerability for it.
- [ ] B. Responsibility for doing the work and accountability for the outcome are held by the same party in a delegation.
- [ ] C. Accountability means being answerable: able to be asked to explain a result and to put it right.
- [ ] D. Accountability passes to the agent once the task is delegated.
- [ ] E. The agent can be given the work to do, while the person who deployed it stays answerable for the outcome.

**14.** Two database transactions each read an account balance of 100, check that a withdrawal of 80 is allowed, and then subtract 80. The team wants only one to succeed. Which statements about "serializable" isolation are true? Check each statement that is true.  *(5 points)*

- [ ] A. Serializable isolation means each transaction's rows can be written to JSON.
- [ ] B. Serializable isolation works because Python's GIL runs the transactions on one thread.
- [ ] C. A weaker isolation level can let both transactions read 100 and both subtract, which is a lost update.
- [ ] D. Serializable isolation makes the outcome match some order of running the transactions one after another.
- [ ] E. Under serializable isolation the two withdrawals cannot both commit from the same starting balance of 100.

**15.** A student sends Claude: "Set the temperature to zero so the model remembers my earlier chat and gives the exact same answer, and stop it at 200 words." Which statements spot the imprecise wording? Check each statement that is true.  *(5 points)*

- [ ] A. "Remembers my earlier chat" mixes up temperature with memory or context.
- [ ] B. "Stop it at 200 words" should be a max tokens limit, since the cap is counted in tokens.
- [ ] C. "Temperature" is the wrong term for this; the student should have said top-k.
- [ ] D. "Temperature" is an acceptable term for the setting that makes sampling less random.
- [ ] E. "Model" is the wrong word because the prompt is read by an embedding.

**16.** An acceptance gate is a check or human decision that an output has to pass before it is accepted or acted on. Check each statement that is true. Check each statement that is true.  *(5 points)*

- [ ] A. A rule in the system prompt enforces behaviour as reliably as a check implemented in the code around the model.
- [ ] B. A gate that has accepted each output so far can be assumed to be working.
- [ ] C. A model's own stated confidence is a sufficient gate.
- [ ] D. A gate is meaningful if it is capable of rejecting an output.
- [ ] E. A gate that compares answers with an authoritative source can stop a false answer that the model repeats consistently.

**17.** An agent says: "Safe for concurrent workers." The code is `if not os.path.exists(p): open(p, "w").write(data)`. Decide which statements are true. Check each statement that is true.  *(5 points)*

- [ ] A. Opening with mode "x" makes the check and the create one operation that fails if the file exists.
- [ ] B. Two workers can both see the file missing before either writes, which is a check-then-act race.
- [ ] C. Adding a short random sleep before the check removes the race.
- [ ] D. A follow-up that gives evidence is: "Read the code again and confirm it looks safe."
- [ ] E. The code is safe because the check runs right before the write.

**18.** Which statements about delimiters and output schemas are true? Check each statement that is true.  *(5 points)*

- [ ] A. Delimiters such as triple quotes or XML-style tags mark where one part of a prompt ends and the next begins.
- [ ] B. An output schema states the fields, names and types the answer should have.
- [ ] C. A delimiter is a rule the answer is checked against.
- [ ] D. Asking for JSON with a schema lets a validator check the shape of an answer, not whether it is true.
- [ ] E. Delimiters are a security feature that blocks prompt injection.

**19.** A user types in a chat: "Remember to use tabs in every file." In a new session, Claude Code uses spaces. The user says "it has no memory." Decide which statements name the parts correctly. Check each statement that is true.  *(5 points)*

- [ ] A. CLAUDE.md is a memory file that Claude Code reads at the start of a session.
- [ ] B. A message typed in the chat is automatically written to CLAUDE.md.
- [ ] C. A better prompt is: "Add a rule to CLAUDE.md that files use tabs."
- [ ] D. Context and a memory file are two names for the same store.
- [ ] E. Context is the text currently in the window for this session, and a new session does not carry it over.

**20.** A user tells Claude: "Make the nightly import safe to rerun." Choose the statements that compress or unpack this requirement correctly. Check each statement that is true.  *(5 points)*

- [ ] A. A one-line compression is: "Make the import idempotent: upsert on the natural key instead of inserting."
- [ ] B. The import is safe to rerun once it catches exceptions and exits with code 0.
- [ ] C. The import writes a log file with a matching name on each run.
- [ ] D. Another one-line compression is: "Make the import deterministic so it runs at the same time each night."
- [ ] E. Rerunning the import on the same file leaves the database with the same rows as one run.
