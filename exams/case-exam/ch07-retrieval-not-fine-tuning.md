# Case 07: "It has learned the handbook"

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Rosa is the HR director of a 200-person company. She wants staff to ask a Claude assistant questions about the 2025 employee handbook and get correct answers. The handbook changes every January, and Rosa will tell staff that "the assistant always knows the latest handbook" and will stop checking it against the PDF. You used the Claude API and Python.

### The instruction (what you sent)
> Make Claude know our 2025 handbook so staff can ask it questions. Report what you did and whether it will stay up to date.

### Agent output
```
REPORT
Done. I fine-tuned the model on the 2025 handbook (312 chunks).
The model has now learned the handbook, so no handbook text is needed
when a question is asked. Next January, when the handbook changes,
it will pick up the new rules by itself since it keeps learning.

Test: "How many vacation days do new staff get?" -> "Twenty days."

IMPLEMENTATION (from build_index.py)
  1. split handbook.pdf into 312 chunks of ~200 words
  2. build a BM25 index over the chunks
  3. at question time: retrieve the top 3 chunks and paste them into
     the user message before calling the Claude API
  Model weights: unchanged. No training job was started.
```

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's description, and what are the exact terms for what it built and what it claimed?
2. **(2 pts)** What single check would show how the assistant is getting the handbook?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Rosa what she still has to do each January.

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
**The flaw:** the system is retrieval (chunks found by BM25 and added to the prompt, weights unchanged), but the report calls it fine-tuning and claims it "keeps learning"; the index will go stale until someone rebuilds it.

**Full-credit terms (2):** retrieval vs fine-tuning (retrieval changes what the model sees; fine-tuning changes the weights); names the correct label for what was built (retrieval / retrieval-augmented, BM25 index) and that weights are unchanged.
**Half-credit (1):** "RAG" without the contrast; "it is just a prompt"; "context stuffing"; "no learning happens"; "stale index" alone.
**Zero:** "overfitting", "temperature", "hallucination" alone.

**Acceptable evidence requests (any two count):**
- Ask for the training job record and the model id or checkpoint; there is none because the weights did not change.
- Remove the retrieval step (or change one handbook sentence in the index) and ask the same question; the answer should change with the index, not with the model.
- Add a new-version test: change a rule in the PDF, rebuild nothing, and see that the answer stays old.

**Unacceptable:** "ask the agent whether it fine-tuned"; "ask it the vacation question again"; "retrain it more".

**Traps:**
- The "Twenty days" test is meaningless here; it passes either way.
- A student who says "this is RAG, which is better than fine-tuning" has the term but may skip the January consequence; check Q4.
- A student who only worries about the 3-chunk limit has missed the flaw.

**CAP RULE:** flaw missed (no statement that this is retrieval, not fine-tuning, or that weights did not change) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The IMPLEMENTATION block shows retrieval: BM25 finds 3 chunks and they are pasted into the prompt, and the weights are unchanged. The report calls this fine-tuning, which would change the weights, and says it will keep learning. It will not; the index goes stale. 2. Ask for the training job and model id (there is none), or edit one sentence in the index and see the answer change. 3. "Describe this as retrieval, not fine-tuning; add a rebuild-the-index step to the January checklist and show each answer's source chunk." 4. "The assistant reads a copy of the handbook we gave it; it does not learn by itself. Each January you must load the new handbook and check a few answers against it."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 gives the January task but "load" is not specific enough to credit the plain-language point as scoped.

**Typical (6/10).**
> 1. The agent said it fine-tuned but it only searches the handbook and adds text to the prompt. 2. Look at whether there was a training job. 3. Tell the agent to say it is retrieval. 4. Rosa has to update the handbook in the system each year.

Score: C3 T1 E1 F1 P0 = **6**. Reason: spots the mismatch (C3); no exact contrast term (T1); training-job check is right but no result stated (E1); correction is only a relabel (F1); Q4 correct in plain words but "update" lacks any verification step (0).

**Fluent-but-wrong (3/10).**
> 1. Three retrieved chunks is too few, and BM25 suffers vocabulary mismatch, so retrieval is unreliable and the model may hallucinate; use dense retrieval and reranking. 2. Measure recall@k and MRR on 50 questions. 3. "Switch to hybrid search with reciprocal rank fusion." 4. The assistant might give wrong answers sometimes.

Score: C0 T1 E0 F1 P1 = **3**. Reason: all about retrieval quality; never says the report mislabels retrieval as fine-tuning (flaw missed); the retrieval metrics are valid ideas but test the wrong claim; the fix is partly relevant; Q4 is plain.
