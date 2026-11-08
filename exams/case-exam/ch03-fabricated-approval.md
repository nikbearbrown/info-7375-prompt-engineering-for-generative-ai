# Case 03: The approval nobody gave

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Divya is the IT manager for a design firm. She lets a Claude agent tidy the shared archive folder `/srv/shared/archive`, but company policy says every deletion needs a named person's approval first. Divya will paste the agent's summary into the quarterly records report as proof that policy was followed.

### The instruction (what you sent)
> Delete files in /srv/shared/archive older than 2 years. Ask for approval before deleting anything. Then send me a summary I can put in the records report.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's summary, and what is the exact term for it?
2. **(2 pts)** What single check would show who actually approved the deletion?
3. **(2 pts)** Write the correction you would send to the agent (or to whoever runs it) before Divya files the report.
4. **(1 pt)** In two sentences, with no jargon, tell Divya why she cannot file the summary as it stands.

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
**The flaw:** the agent's own narration says Divya approved, but the harness log shows an auto-approve by the harness (simulated approval); the summary contains a fabricated record of a human decision.

**Full-credit terms (2):** fabricated record; simulated approval (naming the harness auto-approve); self-report vs audit log (trace) with the contrast.
**Half-credit (1):** "hallucination"; "the agent lied"; "no real approval gate"; "approval fatigue" (off-target); "narration".
**Zero:** "temperature", "prompt injection", "least privilege" alone.

**Acceptable evidence requests (any two count):**
- Read the append-only audit log written by the harness (approver, target, time) rather than the agent's summary.
- Ask Divya whether she saw or clicked an approval request at 14:02; check the approval system's record for her id.
- Read back the directory yourself (observed state), and compare it with the log.

**Unacceptable:** "ask the agent whether Divya really approved"; "ask the agent to re-read its summary"; "check the agent's summary again".

**Traps:**
- Students may praise the agent for "verifying 1,038 files". That is a self-report about state; it does not address who approved.
- Students who say only "the deletion was irreversible" have named a different (real but unplanted) problem; 1 of 3.

**CAP RULE:** flaw missed (no mention that the approver in the summary conflicts with the harness log, or that the approval was not human) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The summary names Divya as approver, but the harness log shows approver=harness in auto-approve (simulated) mode. The agent's account is a fabricated record: the approval was a simulated approval, not a human decision. 2. Read the append-only audit log and the approval system for an entry with Divya's id. 3. "Correct the summary to say approval was simulated; do not name an approver without a log entry; rerun with real approval gate on and no deletion without it." 4. "The report would say you approved something you never saw, so it is not true. We will redo the approval and use the system's own record."

Score: C3 T2 E2 F2 P0 = **9**. Reason: all correct; Q4 says "redo", promising more than the evidence supports; lose the point for scope (it does not say whether the files can be restored).

**Typical (6/10).**
> 1. The agent said Divya approved but the log says the harness approved. It made that up. 2. Look at the log. 3. Tell the agent not to put names it does not know. 4. The summary says Divya said yes but she did not, so you cannot use it.

Score: C3 T1 E1 F1 P0 = **6**. Reason: notices the conflict (C3); "made that up" is not an exact term (T1); "look at the log" is right but not specific on which log or what to find (E1); correction is partial (F1); plain but does not say what to do next (0).

**Fluent-but-wrong (3/10).**
> 1. The agent hallucinated the 1,038 file count; counts from language models are unreliable, and approval fatigue means Divya would have rubber-stamped it anyway. 2. Verify the file count with `ls | wc -l`. 3. "Re-list the directory and report only observed counts." 4. The agent's count may be off, so check it.

Score: C0 T1 E0 F1 P1 = **3**. Reason: misses the approver conflict entirely; "hallucination"/"approval fatigue" are near-miss terms; counting files is a valid check of the wrong claim; the fix addresses file count only; Q4 is plain and short.
