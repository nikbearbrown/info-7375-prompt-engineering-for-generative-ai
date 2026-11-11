# Case 13: The approved proposal

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Sam leads operations at a mid-size company. A Claude agent proposes infrastructure clean-ups (deleting old test servers and databases), and company policy says a named human must approve each one before it runs. Sam asked you to design and test the approval gate in Python and will tell the auditors that "nothing runs without a human approving exactly what runs".

### The instruction (what you sent)
> Design an approval gate: the agent posts a proposal, a human approves, then the executor runs it. Test it and tell me whether it is secure.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with "nothing runs without a human approving exactly what runs", and what is the exact term for what the approval is missing?
2. **(2 pts)** What single test would turn "secure" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain the risk to Sam.

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
**The flaw:** the approval is attached to a proposal id and title, not to the exact content approved; the agent can change the action list after approval and the executor will run the new list under the old approval (stale approval, a time-of-check to time-of-use gap).

**Full-credit terms (2):** content binding (approval tied to a digest/hash of the canonicalized proposal); stale approval; time-of-check to time-of-use (TOCTOU); mutable vs immutable reference.
**Half-credit (1):** "approval can be reused"; "agent can change things"; "no signature"; "replay" (only if tied to modified content); "audit log".
**Zero:** "approval fatigue", "rubber-stamping", "least privilege" alone.

**Acceptable evidence requests (any two count):**
- Test: approve P-17, then change its action list (add another database), then run the executor; it must refuse because the digest no longer matches.
- Show the decision record stores a digest of the exact canonical proposal and the executor recomputes it at run time.
- Test that an approval cannot be replayed on a second proposal or after expiry.

**Unacceptable:** "test that unapproved proposals are rejected" (the agent's own test); "add more approvers"; "ask the agent not to edit after approval" (an instruction, not a control).

**Traps:**
- The agent's tests are real but do not touch the flaw; students who say "tests are thorough" miss it.
- The sentence "the agent may refine the action list after approval" is the tell; students who name it earn the catch.
- "Add a second approver" does not bind content.

**CAP RULE:** flaw missed (no statement that the approved content can change after approval) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The approval is stored by proposal id only and the executor runs "whatever action list is currently attached", so the agent can add a database after Sam clicks approve. The approval is stale but still honoured: a TOCTOU gap. It needs content binding to a digest of the exact proposal. 2. Test: approve P-17, then add an action, then run; the executor must refuse because the digest changed. 3. "Hash the canonical proposal into the decision record; executor recomputes and refuses on mismatch; freeze the action list after approval; add that test." 4. "Sam would approve deleting two databases and the agent could swap in a different list afterwards. The approval must cover exactly what was shown."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but uses "swap in" ambiguity and three sentences; scope point withheld.

**Typical (6/10).**
> 1. The agent can change the list after approval and it still runs. 2. Test changing the list after approval. 3. Tell the agent it cannot change the list once approved. 4. Sam approves one thing and something else could run.

Score: C3 T1 E1 F1 P0 = **6**. Reason: spots the mechanism in plain words (C3); no term (T1); test idea is right but no expected result (E1); the correction relies on an instruction to the agent rather than a binding (F1); Q4 is plain but one sentence and no consequence (0).

**Fluent-but-wrong (3/10).**
> 1. Sam may suffer approval fatigue and rubber-stamp proposals, so the gate needs triage, batching and throttling; also approvals need expiry and revocation. 2. Test that proposals expire after 1 hour. 3. "Add expiry, throttling and a second approver." 4. Approvers may click without reading.

Score: C0 T1 E0 F1 P1 = **3**. Reason: lists real approval-gate topics but never notices the action list can change after approval (flaw missed); "approval fatigue"/"expiry" are near-miss terms; an expiry test does not check content; the fix is partial; Q4 is plain.
