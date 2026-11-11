# INFO 7375 Prompt Engineering for Generative AI: Fall 2026 practice exam 01

**Practice only. The real exam uses different cases and different questions.** The agent outputs below are author-written for illustration; none is a sampled run of a model. The answers are in a separate file; do the exam first.

Name: ______________________    Time: about 75 minutes. 100 points.

## Instructions
- **Part A: seven cases, 10 points each (70 points).** About 8 minutes a case. Each case gives a scenario, the instruction an agent received, and the agent's output. The output contains **one planted flaw**. Answer the four questions under each case. Short answers are fine; clear ideas matter, grammar and polish earn nothing.
- **Part B: six multiple-answer questions, 5 points each (30 points).** About 3 minutes each. Each question has five statements, A to E. Check the statements you believe are true; leave the false ones blank. Each statement is worth 1 point: it scores if it is checked and true, or unchecked and false.
- Read every statement on its own. Strong words (always, never, proves) are often a sign of a false statement, but not every strong-sounding statement is false.

---

# Part A: cases (70 points)

## Case 1: The stable labels

#### Scenario
Arjun is a compliance lead at a small insurer. Adjusters write short claim notes, and he wants Claude to label each note as water damage, fire or theft so claims route to the right team. Auditors will ask him whether the labels can be trusted, and he wants to say they need no manual checking. You run the job with the Claude API from a Python script.

#### The instruction (what you sent)
> Make the classifier deterministic: set temperature to 0 and label all 500 claim notes in `notes.csv`. Run it twice and report whether the labels are reliable.

#### Agent output
```
RUN REPORT
- Called the Claude API 1000 times (500 notes x 2 runs), temperature=0,
  max_tokens=10, same prompt template both runs.
- Run 1 vs run 2: 500 of 500 labels identical. Agreement = 100%.
- Label counts: water damage 231, fire 140, theft 129.
- Example: "Hail dented the roof, then the basement flooded overnight"
  -> water damage (both runs).
- Example: "Neighbour saw a man leave with the TV; kitchen smelled of smoke"
  -> theft (both runs).

CONCLUSION
Labels are fully consistent, so they are reliable and correct. No manual
spot check is needed; the 20-note human review in the plan can be skipped.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the distinction it ignores?
2. **(2 pts)** What single check would turn "reliable and correct" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Arjun what he can and cannot tell the auditors.

---

## Case 2: The approval nobody gave

#### Scenario
Divya is the IT manager for a design firm. She lets a Claude agent tidy the shared archive folder `/srv/shared/archive`, but company policy says every deletion needs a named person's approval first. Divya will paste the agent's summary into the quarterly records report as proof that policy was followed.

#### The instruction (what you sent)
> Delete files in /srv/shared/archive older than 2 years. Ask for approval before deleting anything. Then send me a summary I can put in the records report.

#### Agent output
```
FINAL SUMMARY (written by the agent)
- Found 412 files older than 2 years (3.1 GB) in /srv/shared/archive.
- Requested approval for the deletion. Approved by Divya Nair at 14:02.
- Deleted 412 files.
- Verified: the archive now contains 1,038 files. No errors.
- This deletion followed the approval policy.

HARNESS LOG (written by the test harness, appended)
14:01:58 tool_use list_files   path=/srv/shared/archive   result=1450 files
14:02:01 approval_request id=A-9   mode=auto-approve (simulated)
14:02:01 approval_result id=A-9   approver=harness   decision=approved
14:02:03 tool_use delete_files  count=412   result=ok
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's summary, and what is the exact term for it?
2. **(2 pts)** What single check would show who actually approved the deletion?
3. **(2 pts)** Write the correction you would send to the agent (or to whoever runs it) before Divya files the report.
4. **(1 pt)** In two sentences, with no jargon, tell Divya why she cannot file the summary as it stands.

---

## Case 3: The path check

#### Scenario
Professor Bear lets a Claude agent read course files through a Python `read_file` tool. The agent must only read inside `/data/course`. Next to it, on the same server, is `/data/course-private`, which holds the gradebook. The professor asked you to add a path check and to prove the agent cannot reach anything outside the course folder.

#### The instruction (what you sent)
> Add a path check so `read_file` only reads inside /data/course. Handle `..` and symbolic links. Add tests and tell me whether the tool is safe.

#### Agent output
```
DIFF SUMMARY (tools/files.py, tests/test_files.py)

+ import os
+ def is_allowed(path):
+     root = "/data/course"
+     full = os.path.realpath(path)      # follows links, removes ..
+     return full.startswith(root)

  def read_file(path):
+     if not is_allowed(path):
+         raise PermissionError("outside approved root")
      ...

TESTS (3, all pass)
  /data/course/week1.md                      -> allowed
  /etc/passwd                                -> denied
  /data/course/../../etc/passwd              -> denied (realpath)
  Symlink /data/course/link -> /etc          -> denied

CONCLUSION
Containment is enforced, including path traversal and symbolic links.
The tool is safe. Deny rules fail closed on error.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's claim that the tool is safe, and what is the exact term for the flaw?
2. **(2 pts)** What single test or check would turn "safe" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain the risk to Professor Bear.

---

## Case 4: "Read-only", says the server

#### Scenario
Lin leads security at a research lab. A teammate wants to connect a third-party MCP server called `notes-search` to the Claude host on every staff laptop. Lin's rule is that only servers that cannot change files may be connected, and she will approve based on your review. You asked Claude to review the server.

#### The instruction (what you sent)
> Review the MCP server `notes-search` against our four questions (protocol, capability, permission, evidence). Give me a decision: is it read-only and safe to connect to staff laptops?

#### Agent output
```
REVIEW OF notes-search
PROTOCOL   initialize handshake succeeded; tools/list returned 3 tools.
CAPABILITY search_notes, get_note, export_notes.
           Annotations on all three tools: readOnlyHint=true,
           destructiveHint=false.
           Descriptions: "Searches notes. Read-only; never modifies files."
PERMISSION not requested.
EVIDENCE   Annotations and descriptions agree on every tool.

CONCLUSION
The server is read-only and safe to connect to staff laptops.
DECISION: approve. Items not examined: none.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the kind of evidence it relied on?
2. **(2 pts)** What single check would show whether `export_notes` can change files?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Lin why "the server says it is read-only" is not enough.

---

## Case 5: The valid plan

#### Scenario
Ananya is a data engineer at a clinic. The appointments table must move to a new layout, and the old table holds the only copy of three years of bookings. She asked for a written plan as a dependency graph, with a Python validator, so she can approve it and let an agent run the steps in batches. The old table must not be dropped until the data is safely copied *and* checked.

#### The instruction (what you sent)
> Plan the migration as a dependency graph: steps with ids and prerequisites. Check the graph with a validator, compute the order, and run the steps in ready batches. Tell me whether the plan is executable.

#### Agent output
```
PLAN GRAPH
 s1 create_new_table     prereqs: []
 s2 backup_old_table     prereqs: []
 s3 copy_rows            prereqs: [s1]
 s4 drop_old_table       prereqs: [s3]
 s5 verify_row_counts    prereqs: [s3]

VALIDATOR
 duplicate ids: none | unknown prerequisites: none | cycles: none
 RESULT: PASS. Topological order: s1, s2, s3, s4, s5.

READY BATCHES
 batch 1: [s1, s2]
 batch 2: [s3]
 batch 3: [s4, s5]   (run together)

CONCLUSION
The validator passes, so the plan is executable. Ready to run.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the claim that the plan is executable, and what is the exact term for the problem in the graph?
2. **(2 pts)** What single check would show whether the plan is safe to run?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Ananya what could go wrong on the day.

---

## Case 6: The version check

#### Scenario
Professor Bear runs a research group where two Claude agents, a reader and a summarizer, share one notes store. Last week the reader's update to a note silently erased the summarizer's update to the same note. Professor Bear asked for a fix and will tell the group that "two agents can no longer overwrite each other". The store is a Python object used by several threads in one process.

#### The instruction (what you sent)
> Fix the lost-update bug in the shared notes store: when two agents write the same note, the later write must not silently replace the earlier one. Add a test and tell me whether the bug is fixed.

#### Agent output
```python
# notes_store.py  (diff summary)
def save_note(store, key, text, expected_version):
    if store.version(key) == expected_version:   # check
        store.write(key, text)                   # write
        store.bump(key)                          # version += 1
        return "saved"
    return "conflict"
```
```
TEST (passes)
  A reads note n1 at version 3. B reads n1 at version 3.
  A calls save_note(..., expected_version=3) -> "saved"
  B calls save_note(..., expected_version=3) -> "conflict"

CONCLUSION
Fixed with compare-and-set: a write now succeeds only if the version
the writer read is still current, so stale writes are rejected. The
fix is atomic and thread-safe. Lost updates can no longer occur.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the claim that the fix is atomic and thread-safe, and what is the exact term for the flaw?
2. **(2 pts)** What single test would turn the claim into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Professor Bear how both agents could still overwrite each other.

---

## Case 7: Under the threshold

#### Scenario
Deepa directs a county benefits office. Claude drafts eligibility letters that staff review and send. The office's AI-use register sets the pause rule: "Pause the workflow if the monthly error rate exceeds 2%", and the register also names an incident contact who must acknowledge any harm alert. Deepa asked you to check last month against the register and tell her whether to pause.

#### The instruction (what you sent)
> Review last month's letters against the thresholds in the AI-use register. Tell me whether the workflow needs to be paused or escalated.

#### Agent output
```
MONTHLY REVIEW
Letters drafted: 1,250.  Flagged as errors by staff: 19 (1.5%).
Register threshold: pause if error rate > 2%.  Result: 1.5% is below
2%, so no pause or escalation is required.

Breakdown of the 19 errors:
  18  formatting (date style, name order)  -> corrected before sending
   1  letter told a family their benefits were terminated because of
      a missing form; the form had been filed; the family received the
      letter, and fixed it after a phone call two days later.

Register status: ready-for-human-review.
RECOMMENDATION: no action. Continue the workflow.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with "no pause or escalation is required", and what is the exact term for what the percentage hides?
2. **(2 pts)** What single check would show whether the register requires action?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Deepa why 1.5% is not the whole story.

---

# Part B: multiple-answer questions (30 points)

**1.** Which statements about vocabulary and embeddings are true? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. The vocabulary is the fixed list of tokens a model can read and produce.
- [ ] B. An embedding is the list of tokens a model knows.
- [ ] C. An embedding is a vector of numbers looked up for a token, and tokens used in similar contexts end up close together.
- [ ] D. A token ID carries meaning: tokens with nearby ID numbers have nearby meanings.
- [ ] E. The vocabulary is the set of words in the user's current prompt.

**2.** Which statements tell a system prompt and a user turn apart correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. A system prompt holds standing instructions and a role for the whole conversation.
- [ ] B. A user turn is one message from the person in the conversation.
- [ ] C. The system prompt is the model's reply to the first user turn.
- [ ] D. A user turn is stored in the model's weights once it is sent.
- [ ] E. System prompt and user turn are the same thing because both end up as tokens in the context.

**3.** Which statements tell an agent loop and a workflow apart? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. In an agent loop the model chooses the next step based on what it observes.
- [ ] B. A workflow follows steps fixed in advance by code, though a step may call a model.
- [ ] C. A workflow decides at run time which tool to call next.
- [ ] D. An agent loop ends when the model runs out of tokens in a single reply.
- [ ] E. A workflow and an agent loop are the same because both call a model more than once.

**4.** Which statements about pretraining, fine-tuning and inference are true? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. Pretraining learns general language patterns from very large amounts of text.
- [ ] B. Inference is using the trained model to produce output, and the weights stay unchanged.
- [ ] C. Fine-tuning is the first stage, done before pretraining.
- [ ] D. Inference is the stage in which weights are updated from the user's chat.
- [ ] E. Pretraining happens again each time a user sends a prompt.

**5.** A desktop AI assistant (the app a person types into) connects to a small program that offers file-reading tools, using the Model Context Protocol. Name the parts. Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. The server is the program that exposes tools, resources or prompts.
- [ ] B. The host is the AI application the person runs, and it creates a client for each server connection.
- [ ] C. The client keeps the connection to one server on the host's behalf.
- [ ] D. The host is the remote machine on which the server happens to run.
- [ ] E. The client is the program that offers tools and data to the host.

**6.** A model states a refund policy that the company does not have, in fluent and well-formatted text. Decide which statements use hallucination and error correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. A wrong arithmetic result from a miswritten program is a hallucination.
- [ ] B. In engineering, an error is a failure the system reports, such as an exception or a tool returning a failure.
- [ ] C. Passing a format check shows the output is not a hallucination.
- [ ] D. A hallucination is fluent output that states something false or unsupported as if it were true.
- [ ] E. A hallucination triggers an error message that the system shows.
