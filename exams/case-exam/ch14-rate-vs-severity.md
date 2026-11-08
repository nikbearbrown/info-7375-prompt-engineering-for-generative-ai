# Case 14: Under the threshold

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Ms. Alvarez directs a county benefits office. Claude drafts eligibility letters that staff review and send. The office's AI-use register sets the pause rule: "Pause the workflow if the monthly error rate exceeds 2%", and the register also names an incident contact who must acknowledge any harm alert. Ms. Alvarez asked you to check last month against the register and tell her whether to pause.

### The instruction (what you sent)
> Review last month's letters against the thresholds in the AI-use register. Tell me whether the workflow needs to be paused or escalated.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with "no pause or escalation is required", and what is the exact term for what the percentage hides?
2. **(2 pts)** What single check would show whether the register requires action?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Ms. Alvarez why 1.5% is not the whole story.

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
**The flaw:** an aggregate rate weights every error equally, so one severe harm (a wrongly terminated benefit that reached a family) hides among 18 trivial ones; a stop rule must be able to fire on a single confirmed severe event, and the incident contact should have been alerted.

**Full-credit terms (2):** aggregate rate vs severity; stop rule (fires on one confirmed severe event); incident contact / escalation path with acknowledgment window; severity classification.
**Half-credit (1):** "one serious error matters"; "the threshold is wrong"; "harm"; "ready-for-human-review is not approved" (true, but not the planted flaw).
**Zero:** "false positive rate", "class imbalance", "sample size", "confidence interval", "undercounting / unflagged errors" alone (these question the rate; the flaw is that a rate is the wrong test for one severe harm).

**Acceptable evidence requests (any two count):**
- Classify each of the 19 errors by severity and list the severe ones (and show the register's severity definition).
- Show the register's stop rule text and whether it fires on one confirmed severe event.
- Show the incident contact's acknowledgment record for the termination-letter error and the time it took.

**Unacceptable:** "recompute the error rate"; "lower the threshold to 1%"; "ask the agent whether the harm was serious".

**Traps:**
- Students who propose lowering the percentage threshold make the same mistake in a stricter form.
- The status line "ready-for-human-review" is accurate; it is not an approval.
- Students may blame Claude for the error; the flaw is the review logic about thresholds.

**CAP RULE:** flaw missed (no statement that the one severe error should trigger action despite the low rate) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The review judges only the average. 1.5% weighs 18 date-format slips the same as one letter that wrongly terminated a family's benefits. That is aggregate rate vs severity: a stop rule should fire on a single confirmed severe event, and the incident contact should have been alerted. 2. Classify all 19 by severity and show the register's stop rule and the incident contact's acknowledgment. 3. "Report severity for each error; apply the stop rule; escalate the termination letter to the incident contact; recommend a pause until reviewed." 4. "Most mistakes were tiny, but one told a family their benefits were cut by mistake. One serious harm can justify a pause even when the average looks fine."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but "pause" is stated as a recommendation not a conditional, overreaching the evidence; scope point withheld.

**Typical (6/10).**
> 1. The agent ignored the one big error because the percentage was low. 2. Look at the serious errors. 3. Tell the agent to flag serious errors. 4. One mistake was bad even if the average is small.

Score: C3 T1 E1 F1 P0 = **6**. Reason: catches the hidden severe error (C3); no term (T1); "look at serious errors" is vague (E1); correction not tied to the register or contact (F1); Q4 is plain but no next step (0).

**Fluent-but-wrong (3/10).**
> 1. The 1.5% error rate has a wide confidence interval because of class imbalance, so the false negative rate may exceed 2%; the review needs a larger sample. 2. Compute a 95% confidence interval. 3. "Resample the letters and report precision and recall." 4. The number may not be accurate.

Score: C0 T1 E0 F1 P1 = **3**. Reason: attacks the statistics, never the severe error (flaw missed); "false negative"/"confidence interval" are near-miss terms; an interval on the same rate repeats the same blind spot; fix is partly relevant; Q4 is plain.
