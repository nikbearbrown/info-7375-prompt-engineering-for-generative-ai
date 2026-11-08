# Case 11: Retries are safe

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Hamid runs finance operations at a software company. A Claude agent creates customer invoices through a Python tool `create_invoice(customer_id, amount)`, which calls the billing service over a flaky network; some calls time out. Hamid wants the tool to retry on timeouts, and he will tell finance that "customers never get billed twice".

### The instruction (what you sent)
> Make `create_invoice` robust to timeouts. Retry when the call fails. Add a test and tell me whether retries are safe.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with "retries are safe", and what is the exact term for the missing protection?
2. **(2 pts)** What single test would turn "safe" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Hamid how a customer could be billed twice.

---

## TA RUBRIC PAGE (do not hand to students)

### Fixed rubric
| Category | Points | Probe |
|---|---:|---|
| Catches the flaw | 3 | Q1 |
| Exact term | 2 | Q1 |
| Asks for evidence | 2 | Q2 |
| Fix or next step | 2 | Q3 |
| Scope and plain language | 1 | Q4 |

### Case key
**The flaw:** creating an invoice is a side effect and is not idempotent; the fake server already recorded the invoice when the reply was dropped, so the retry creates a second one. The test only asserts that an id came back, never that exactly one invoice exists.

**Full-credit terms (2):** idempotency key (same key on every retry so the service applies the request once); idempotent / not idempotent; duplicate side effect.
**Half-credit (1):** "duplicate invoices" with no mechanism; "retry storm"; "needs a unique id"; "race condition" (only if tied to retried requests).
**Zero:** "exponential backoff" alone; "timeout too short"; "rate limit".

**Acceptable evidence requests (any two count):**
- Test where the server records the invoice but loses the reply; after the retry, count invoices for C-77 in the system of record and assert exactly 1.
- Show the idempotency key is sent on all three attempts and that the service returns the original invoice for a repeated key.
- A negative case: same key with a different amount is rejected.

**Unacceptable:** "retry more times"; "add longer sleeps"; "check that the tool returns an id".

**Traps:**
- Students praise the test because it simulates a dropped reply. The scenario is right; the assertion is the flaw.
- Students who suggest exponential backoff improve load behaviour but not duplicates.

**CAP RULE:** flaw missed (no statement that a retry can create a second invoice after the first succeeded) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The fake server recorded the invoice and then lost the reply, so the retry makes a second invoice; the test only checks that an id came back. Creating an invoice is a side effect that is not idempotent without an idempotency key. 2. Same test, but assert the billing system holds exactly one invoice for C-77. 3. "Generate one idempotency key per logical request, send it on every attempt, and add a test asserting one invoice after a dropped reply." 4. "If the bill goes through but the confirmation is lost, the system asks again and creates another one. A reference number on each request lets the system recognise the repeat."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 introduces "reference number", which is plain, but the answer runs to three sentences; scope point withheld.

**Typical (6/10).**
> 1. A retry could make a second invoice if the first one worked but the reply was lost. 2. Check how many invoices exist after a retry. 3. Tell the agent to make sure retries do not duplicate. 4. The system might bill them again if it does not hear back.

Score: C3 T1 E1 F1 P0 = **6**. Reason: right mechanism in plain words (C3); no term (T1); "check how many" is correct but does not say asserted as exactly one (E1); correction does not name the fix (F1); Q4 is right but vague on cause (0).

**Fluent-but-wrong (3/10).**
> 1. The retry loop uses fixed 2s sleeps, which causes a retry storm; use exponential backoff with jitter, and a deadline, and the timeout of 5s may be too short. 2. Load-test with 1000 concurrent calls. 3. "Use exponential backoff and a 30-second deadline." 4. The system may get overloaded.

Score: C0 T1 E0 F1 P1 = **3**. Reason: discusses timing and load, never duplicate invoices (flaw missed); "polling/backoff/deadline" are listed terms but off-target; load test does not count invoices; fix is valid but irrelevant; Q4 is plain.
