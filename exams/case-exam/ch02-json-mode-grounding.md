# Case 02: Every answer cites a source

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Professor Bear directs a university library and wants a web page where students ask questions about three library policy documents (policy-A, policy-B, policy-C) and get back a short answer with the sources it relied on. The page reads Claude's reply as JSON with the fields `answer` and `citations`, and Professor Bear will tell the provost that answers are "traceable to policy". You wrote the prompt and a Python check.

### The instruction (what you sent)
> Use Claude's JSON mode so every reply has `answer` and `citations`. Write a validator that checks the reply parses, has both keys, and that every citation id exists in the source list. Run it on 100 test questions and report whether the answers are grounded.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's conclusion, and what is the exact term for the distinction it ignores?
2. **(2 pts)** What single check would show whether the answers are grounded?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Professor Bear what the report does and does not show.

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
**The flaw:** the validator checks structure (valid JSON, right keys, citation ids that exist) but not whether the cited passage supports the claim, so "grounded" is unproven; a citation existing is not the same as support.

**Full-credit terms (2):** structural validity vs grounding; citation vs support (citation validity vs accuracy); "ungrounded" used for answers that cite but are unsupported.
**Half-credit (1):** "the citations might be fake / hallucinated" (they exist; this is the wrong failure); "needs fact-checking"; "faithfulness" without the contrast; "JSON mode only guarantees syntax".
**Zero:** "overfitting", "temperature", "bias".

**Acceptable evidence requests (any two count):**
- Read the cited passage for a sample of answers (e.g. 20) and mark each claim supported, partly supported or unsupported; report the rate.
- Add questions the policies do not answer and check that Claude abstains.
- Have a second pass (human, or a model checked against human labels) compare each claim with the passage text it cites.

**Unacceptable:** "run the validator again"; "check that the JSON is valid"; "ask Claude whether its answers are grounded".

**Traps:**
- Students who say JSON mode "does not guarantee the right keys" are accurate but off-target; credit only if they also separate structure from support.
- Students who worry that citations are invented miss that the validator already rules that out.

**CAP RULE:** flaw missed (no statement that the check never compares the claim with the cited text) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The validator proves the reply is well-formed and the ids exist; it never reads policy-B#4 to see if it says alumni may borrow ebooks for 90 days. That is structural validity, not grounding: a citation that exists is not a source that supports the claim. 2. Sample 20 answers and read each cited passage against the claim; report supported/unsupported counts. 3. "Add a support check: for each claim, quote the passage and say supported, partly, or not; add 10 questions the policies cannot answer and expect abstention." 4. "The report shows the answers are well-formed and point to real documents. It does not yet show the documents say what the answers claim."

Score: C3 T2 E2 F2 P0 = **9**. Reason: all four content points right; Q4 is accurate but still uses "well-formed", so the plain-language point is withheld.

**Typical (6/10).**
> 1. The validator only checks that the citations exist, not that they are correct. 2. Check a few answers against the policy. 3. Tell the agent to verify the citations are right. 4. The answers might cite documents that do not say that.

Score: C3 T1 E1 F1 P0 = **6**. Reason: right idea in plain words (C3); no exact term (T1); "a few answers" with no method (E1); "verify the citations" is the right direction but not a concrete instruction (F1); Q4 is understandable but no statement of what the report does show (0).

**Fluent-but-wrong (3/10).**
> 1. JSON mode guarantees valid JSON but not that the keys are the ones requested, so schema-constrained decoding should be used; also the citations might be hallucinated. 2. Add a stricter validator that rejects unexpected keys. 3. "Switch to schema-constrained decoding with a strict validator." 4. The output format might be wrong sometimes.

Score: C0 T1 E0 F1 P1 = **3**. Reason: all about format; the validator already passed 100% on keys, so this misses the flaw; "JSON mode vs schema" is a near-miss term; the fix is valid but irrelevant; Q4 is plain.
