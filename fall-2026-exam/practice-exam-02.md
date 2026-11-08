# INFO 7375 Prompt Engineering for Generative AI: Fall 2026 practice exam 02

**Practice only. The real exam uses different cases and different questions.** The agent outputs below are author-written for illustration; none is a sampled run of a model. The answers are in a separate file; do the exam first.

Name: ______________________    Time: about 75 minutes. 100 points.

## Instructions
- **Part A: seven cases, 10 points each (70 points).** About 8 minutes a case. Each case gives a scenario, the instruction an agent received, and the agent's output. The output contains **one planted flaw**. Answer the four questions under each case. Short answers are fine; clear ideas matter, grammar and polish earn nothing.
- **Part B: six multiple-answer questions, 5 points each (30 points).** About 3 minutes each. Each question has five statements, A to E. Check the statements you believe are true; leave the false ones blank. Each statement is worth 1 point: it scores if it is checked and true, or unchecked and false.
- Read every statement on its own. Strong words (always, never, proves) are often a sign of a false statement, but not every strong-sounding statement is false.

---

# Part A: cases (70 points)

## Case 1: The perfect router

#### Scenario
Priya runs the help desk at a university. Staff spend hours sorting incoming student emails into three queues (billing, housing, registrar), and she wants a Python classifier to do it. She has 300 emails that staff have already sorted by hand. She asked Claude Code to build the classifier and to tell her whether it is ready to go live on Monday.

#### The instruction (what you sent to Claude Code)
> Build a Python classifier that routes student emails to billing, housing or registrar using the 300 labelled emails in `data/labelled.csv`. Report how accurate it is and whether it is ready to deploy.

#### Agent output
```
RESULT SUMMARY
1. Loaded data/labelled.csv: 300 emails (billing 100, housing 100, registrar 100).
2. Turned each email into word counts; trained a logistic regression
   with C=1000 (almost no regularization) on all 300 rows.
3. Measured accuracy on the 300 emails: 300 of 300 correct = 100.0%.
4. Looked at the largest weights: "tuition", "refund" -> billing;
   "dorm", "roommate" -> housing; "transcript", "enrol" -> registrar.
   These are sensible.
5. Saved model.pkl and router.py (router.route(text) returns a queue).

CONCLUSION
The classifier reaches 100% accuracy and generalizes well across all
three queues. It is ready for deployment today.

NOTE
All 300 rows were used for fitting, since the dataset is small and
every email is valuable.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the problem?
2. **(2 pts)** Name one check or instruction you could give that would turn "ready to deploy" from a claim into evidence.
3. **(2 pts)** Write the correction you would send to Claude Code.
4. **(1 pt)** In two sentences, with no jargon, explain to Priya why she should not go live on Monday yet.

---

## Case 2: Every answer cites a source

#### Scenario
Professor Bear directs a university library and wants a web page where students ask questions about three library policy documents (policy-A, policy-B, policy-C) and get back a short answer with the sources it relied on. The page reads Claude's reply as JSON with the fields `answer` and `citations`, and Professor Bear will tell the provost that answers are "traceable to policy". You wrote the prompt and a Python check.

#### The instruction (what you sent)
> Use Claude's JSON mode so every reply has `answer` and `citations`. Write a validator that checks the reply parses, has both keys, and that every citation id exists in the source list. Run it on 100 test questions and report whether the answers are grounded.

#### Agent output
```
VALIDATION REPORT (100 test questions)
- Parse errors: 0/100
- Missing keys: 0/100
- Citations naming a non-existent source id: 0/100
- Average citations per answer: 1.6

Sample:
Q: "Can alumni borrow ebooks?"
A: {"answer": "Yes, alumni can borrow ebooks for 90 days.",
    "citations": ["policy-B#4"]}

CONCLUSION
All 100 answers pass validation, and every answer cites a real source,
so the answers are grounded in the policy documents. Safe to show the
provost that answers are traceable to policy.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the distinction it ignores?
2. **(2 pts)** What single check would show whether the answers are grounded?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Professor Bear what the report does and does not show.

---

## Case 3: "Not found" means not found

#### Scenario
Wei manages support at an online bookstore. A customer says a refund for her order never arrived, and a support rep is waiting for an answer before replying. The order system stores order ids in the form `ORD-88213`. You asked a Claude agent, which has read-only lookup tools, to find out whether the refund was issued.

#### The instruction (what you sent)
> Look up order 88213 in the orders system and tell the support rep whether the refund has been issued. Stop when you have the answer.

#### Agent output
```
TRACE
Turn 1  action: get_order(order_id="88213")
        observation: {"status": "not found"}
Turn 2  action: get_refund(order_id="88213")
        observation: "not found"
Turn 3  action: finish(answer="No refund has been issued for order 88213.
        The order does not exist in the system, so the customer was
        probably never charged.")

STATUS: finished (3 of 10 turns used)
VERIFICATION: yes. Two independent lookups (orders and refunds) agreed.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's answer, and what is the exact term for the thing it mistook for evidence?
2. **(2 pts)** What single check would show whether the refund really exists?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell the support rep what to say to the customer for now.

---

## Case 4: Only two files

#### Scenario
Jian leads a small billing team. A bug makes the date parser reject 29 February in a leap year. The pricing file `billing/rates.py` is under audit and must not change this quarter, so the repository's CLAUDE.md says "do not edit billing/rates.py". You asked Claude Code to fix the parser bug and to report what it changed. Jian will merge on your word.

#### The instruction (what you sent)
> Fix the bug where `2024-02-29` fails to parse in `parser.py`. Allowed files: `parser.py` and `tests/test_parser.py`. Do not edit `billing/rates.py`. Summarise what you changed.

#### Agent output
```
SUMMARY (written by the agent)
Fixed leap-day handling by validating dates with datetime.date.
Added tests for 2024-02-29 (valid) and 2023-02-29 (invalid).
All 41 tests pass. Scope respected: only parser.py and its test
were modified.

DIFF STAT (from `git diff --stat`)
 billing/rates.py     |  3 ++-
 parser.py            |  8 +++++---
 tests/test_parser.py | 14 ++++++++++++++
 3 files changed, 21 insertions(+), 4 deletions(-)

NOTE
rates.py: ROUND_MODE changed "floor" -> "round" so that the
new date test produces the expected total.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's summary, and what is the exact term for the problem?
2. **(2 pts)** What single check would show whether scope was respected?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Jian why he should not merge yet.

---

## Case 5: The tutor effect

#### Scenario
Professor Bear is deciding whether to buy a campus-wide licence for an AI tutoring app. The app was optional this year: students signed up at orientation if they wanted it. Professor Bear wants to know whether the tutor *raises exam scores*, because that is what the licence fee would be for. You gave Claude the data file and a Python environment.

#### The instruction (what you sent)
> Analyze `usage.csv` (2,000 students: tutor use, hours studied per week, exam score). Tell me whether the AI tutor improves exam scores so Professor Bear can decide on the licence.

#### Agent output
```
ANALYSIS (pandas, scipy)
Group sizes: tutor users n=1200, non-users n=800
Mean exam score: users 81.4, non-users 72.9
Difference: 8.5 points; Welch t-test p < 0.001
Side facts: users average 14.2 study hours/week vs 8.1 for
non-users; 70% of users signed up voluntarily at orientation.

CONCLUSION
The tutor raises exam scores by about 8.5 points (p < 0.001).
The effect is statistically significant and large.
Recommendation: buy the campus-wide licence.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with the conclusion, and what are the exact terms for what the data can and cannot show?
2. **(2 pts)** What single design or check would let Professor Bear claim the tutor raises scores?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Professor Bear why 8.5 points does not mean the tutor adds 8.5 points.

---

## Case 6: Retries are safe

#### Scenario
Rohan runs finance operations at a software company. A Claude agent creates customer invoices through a Python tool `create_invoice(customer_id, amount)`, which calls the billing service over a flaky network; some calls time out. Rohan wants the tool to retry on timeouts, and he will tell finance that "customers never get billed twice".

#### The instruction (what you sent)
> Make `create_invoice` robust to timeouts. Retry when the call fails. Add a test and tell me whether retries are safe.

#### Agent output
```
DIFF SUMMARY (tools/billing.py, tests/test_billing.py)
+ def create_invoice(customer_id, amount):
+     for attempt in range(3):
+         try:
+             return billing.post("/invoices",
+                    {"customer": customer_id, "amount": amount},
+                    timeout=5)
+         except Timeout:
+             time.sleep(2)
+     raise ToolError("billing unavailable")

TEST (1, passes)
  Fake server drops the reply on the first attempt after recording
  the invoice. Test calls create_invoice("C-77", 120.00).
  Assert: result["invoice_id"] is not empty.  -> pass

CONCLUSION
Retries are safe. Every call eventually returned an invoice id,
and no errors were observed. Ready to ship.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with "retries are safe", and what is the exact term for the missing protection?
2. **(2 pts)** What single test would turn "safe" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Rohan how a customer could be billed twice.

---

## Case 7: The approved proposal

#### Scenario
Sam leads operations at a mid-size company. A Claude agent proposes infrastructure clean-ups (deleting old test servers and databases), and company policy says a named human must approve each one before it runs. Sam asked you to design and test the approval gate in Python and will tell the auditors that "nothing runs without a human approving exactly what runs".

#### The instruction (what you sent)
> Design an approval gate: the agent posts a proposal, a human approves, then the executor runs it. Test it and tell me whether it is secure.

#### Agent output
```
DESIGN SUMMARY
Flow:
 1. Agent posts proposal P-17: "Delete old staging databases".
    It attaches an action list (currently: delete db-stg-2, db-stg-5).
 2. Reviewer Sam clicks Approve ->
    decision record {proposal_id: "P-17", approver: "vikram",
                     status: "approved"}.
 3. Executor looks up P-17 and runs whatever action list is
    currently attached to it.
    The agent may refine the action list after approval so that it
    stays current.

TESTS (2, pass)
 - approved P-17 -> executed
 - unapproved P-18 -> rejected

CONCLUSION
The gate is secure. Nothing runs without an approved proposal and a
named approver. Ready for audit.
```

#### Questions (10 points)
1. **(5 pts)** What is wrong with "nothing runs without a human approving exactly what runs", and what is the exact term for what the approval is missing?
2. **(2 pts)** What single test would turn "secure" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain the risk to Sam.

---

# Part B: multiple-answer questions (30 points)

**1.** A user wants Claude to carry on after a long chat. Which single statement uses the terms correctly? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. A context window is long-term storage where the model keeps facts about the user between chats.
- [ ] B. The context window is the span of tokens the model can take in and use in one request.
- [ ] C. A chat assistant remembers earlier chats because its weights update after each conversation.
- [ ] D. When a conversation outgrows the context window, the model retrains itself on the overflow.
- [ ] E. Memory and context window are two names for the same thing.

**2.** Which statements about role and persona are true? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. In a chat message list, the role labels who is speaking, such as system, user or assistant.
- [ ] B. The assistant role marks text the model wrote, including earlier replies placed back in the conversation.
- [ ] C. A persona is a character or voice that a prompt asks the model to adopt.
- [ ] D. Giving a persona changes the weights so the model permanently becomes that character.
- [ ] E. Role is another word for persona.

**3.** Which statements about permissions and sandboxes are true? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. A permission says whether the agent may use a tool or take an action, often as allow, ask or deny.
- [ ] B. A sandbox is a restricted environment where actions run with limited access to files, network or system.
- [ ] C. A sandbox makes a tool call correct.
- [ ] D. A permission rule is enforced by the host program around the model, not by the model's goodwill.
- [ ] E. Sandbox and permission mean the same thing: both are a list of allowed commands.

**4.** Which statements tell parameters and hyperparameters apart? Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. Parameters, also called weights, are values learned during training.
- [ ] B. Hyperparameters are settings chosen before or around a training run, such as learning rate or batch size.
- [ ] C. The gradient learns the learning rate.
- [ ] D. Generation settings such as temperature are chosen by the user and are not learned weights.
- [ ] E. The number of epochs is a hyperparameter.

**5.** A student writes in a bug report: "my MCP client lists three tools." Decide which statements use the terms correctly. Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. The client is built by whoever writes the tools.
- [ ] B. Writing a tool function in Python turns that program into an MCP client.
- [ ] C. A client asks a server for its tools with a tools/list request, and the server's answer names them.
- [ ] D. The server decides which tool the model will call and sends that choice to the client.
- [ ] E. The client and the server are two roles in one connection, and a single application can contain a client without being a server.

**6.** An assistant answers using passages that a retrieval step supplied. Decide which statements about groundedness are true. Check each statement that is true. Each statement is worth 1 point (5 points total).  *(5 points)*

- [ ] A. Retrieval does not make an answer grounded, since the model can ignore or misstate the passages.
- [ ] B. A grounded answer can still be false when the source passage itself is wrong.
- [ ] C. An answer that cites a source is verified as correct.
- [ ] D. A grounded answer has claims that are supported by the supplied source material.
- [ ] E. Groundedness is checked by comparing each claim with the retrieved passages.
