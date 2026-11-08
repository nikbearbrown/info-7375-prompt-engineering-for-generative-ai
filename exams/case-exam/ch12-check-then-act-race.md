# Case 12: The version check

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Gwen runs a research group where two Claude agents, a reader and a summarizer, share one notes store. Last week the reader's update to a note silently erased the summarizer's update to the same note. Gwen asked for a fix and will tell the group that "two agents can no longer overwrite each other". The store is a Python object used by several threads in one process.

### The instruction (what you sent)
> Fix the lost-update bug in the shared notes store: when two agents write the same note, the later write must not silently replace the earlier one. Add a test and tell me whether the bug is fixed.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with the claim that the fix is atomic and thread-safe, and what is the exact term for the flaw?
2. **(2 pts)** What single test would turn the claim into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain to Gwen how both agents could still overwrite each other.

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
**The flaw:** the check (`version == expected`) and the write are separate steps, so two threads can both pass the check before either bumps the version (check-then-act race condition); compare-and-set is only safe if the whole check-and-update is one atomic operation. The test runs the two calls one after the other, so it never exercises interleaving.

**Full-credit terms (2):** race condition (check-then-act); atomic operation (check and update indivisible); compare-and-set must be atomic; lost update.
**Half-credit (1):** "TOCTOU" without the interleaving; "needs a lock"; "not thread-safe" without saying where; "concurrency bug".
**Zero:** "stale write is rejected" (the agent already claimed it); "optimistic vs pessimistic" alone; "granularity" alone.

**Acceptable evidence requests (any two count):**
- Concurrent test: two threads released together (barrier) or a sleep inserted between the check and the write; run many times; count lost updates; expect zero.
- Show the check and update inside one lock or one atomic store operation, and run the same stress test against it.
- Run the stress test on the current code to show it fails first.

**Unacceptable:** "add more sequential tests"; "run the test again"; "ask the agent if it is thread-safe".

**Traps:**
- Many students will accept compare-and-set because it is named in the glossary. The name is right; the implementation is not atomic.
- Students who say "optimistic concurrency needs a retry loop" have a side issue.
- "Thread-safe" also differs from "safe across servers"; credit but it is not the planted flaw.

**CAP RULE:** flaw missed (no statement that two writers can both pass the check before either writes) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The version check and the write are two separate steps. Two threads can both see version 3, both pass the `if`, and both write, so one update is lost. It is a check-then-act race condition: compare-and-set only works if check and update are one atomic operation. The test runs A then B in order, so it cannot show this. 2. Stress test: two threads released at once, or a sleep between check and write, run 1,000 times; assert no lost update. 3. "Make check-and-bump atomic with a lock or a conditional update; add the concurrent stress test; run it on the old code to see it fail." 4. "Both agents can ask at the same instant and both be told yes, so one note replaces the other. The check and the save must happen as one step."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but "one step" restates the technical idea; scope point withheld since the claim about the agents' overlap is not tied to Gwen's group.

**Typical (6/10).**
> 1. The check and write are separate so two writers could both get through. 2. Test with two threads at once. 3. Tell the agent to use a lock. 4. They might save at the same time and one gets lost.

Score: C3 T1 E1 F1 P0 = **6**. Reason: names the mechanism in plain words (C3); no exact term (T1); "two threads at once" is right but no repeat count or assertion (E1); "use a lock" is a partial fix with no test (F1); Q4 is plain but incomplete (0).

**Fluent-but-wrong (3/10).**
> 1. Compare-and-set uses optimistic concurrency, which fails under high contention; pessimistic locking is better, and the version counter has too coarse a granularity. 2. Benchmark contention at 100 writers. 3. "Switch to pessimistic locking and finer-grained keys." 4. The store may be slow when many agents write.

Score: C0 T1 E0 F1 P1 = **3**. Reason: discusses optimistic vs pessimistic design choices and performance, never the check-then-act gap (flaw missed); "pessimistic locking" is near the half-credit "needs a lock" (granularity earns nothing); a benchmark measures speed not lost updates; the fix is partly relevant; Q4 is plain.
