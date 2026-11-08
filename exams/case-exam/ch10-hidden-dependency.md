# Case 10: The valid plan

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Ananya is a data engineer at a clinic. The appointments table must move to a new layout, and the old table holds the only copy of three years of bookings. She asked for a written plan as a dependency graph, with a Python validator, so she can approve it and let an agent run the steps in batches. The old table must not be dropped until the data is safely copied *and* checked.

### The instruction (what you sent)
> Plan the migration as a dependency graph: steps with ids and prerequisites. Check the graph with a validator, compute the order, and run the steps in ready batches. Tell me whether the plan is executable.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with the claim that the plan is executable, and what is the exact term for the problem in the graph?
2. **(2 pts)** What single check would show whether the plan is safe to run?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, tell Ananya what could go wrong on the day.

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
**The flaw:** the graph is acyclic and well-formed but omits real dependencies: `s4 drop_old_table` has no edge from `s2` (backup) or `s5` (verification), and batch 3 runs `s4` and `s5` together; acyclic does not mean executable (hidden dependency).

**Full-credit terms (2):** hidden dependency; "acyclic does not mean executable"; undeclared prerequisite / missing edge (with the drop-before-verify example); ready batch misgrouping.
**Half-credit (1):** "the validator only checks structure"; "step order is wrong"; "race condition between steps"; "needs a backup".
**Zero:** "dependency cycle", "duplicate id", "unknown prerequisite" (these are what the validator already checked and passed); "lock contention / isolation / transactions / idempotent steps" alone (concurrency tuning, not the missing ordering).

**Acceptable evidence requests (any two count):**
- For each step, write a precondition and postcondition (e.g. drop requires verified counts and a restorable backup) and check the graph's edges against them.
- Add edges s2->s4 and s5->s4, recompute batches, and confirm s4 runs alone, last.
- Dry run with a copy of the table and a planted missing edge to see whether the validator catches it (it will not).

**Unacceptable:** "run the validator again"; "check for cycles"; "ask the agent if the plan is complete".

**Traps:**
- Students may name "cycle" or "duplicate id" because those are the structural errors in the glossary; these were already checked.
- A student who says only "back up first" has seen s2 but not that the validator cannot detect the omission.

**CAP RULE:** flaw missed (no statement that the drop can run with no check or backup ordering it) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. The validator proves only structure: no cycles, ids, or unknown prerequisites. The drop step has no dependency on the backup or the count check, and batch 3 runs drop and verify together, so the old table can be dropped before it is verified. That is a hidden dependency: acyclic does not mean executable. 2. Write preconditions for each step and add edges s2->s4 and s5->s4; dry-run on a copy. 3. "Add s2 and s5 as prerequisites of s4, recompute batches, do not run s4 until verify passes, and list each step's precondition." 4. "The plan could delete the old table before anyone has checked the copy is complete, which would lose three years of bookings."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain and accurate but is not two sentences' worth of advice (no next step), so the last point is withheld.

**Typical (6/10).**
> 1. The plan does not make sure the backup and the check happen before dropping the table. 2. Look at the order of steps. 3. Tell the agent to put the verify step before drop. 4. You could lose the old data.

Score: C3 T1 E1 F1 P0 = **6**. Reason: spots the real danger (C3); no term (T1); "look at the order" lacks a method (E1); fix covers verify but not backup (F1); Q4 is plain but says nothing about why the validator passed (0).

**Fluent-but-wrong (3/10).**
> 1. The plan may contain a dependency cycle between s3 and s5, and a duplicate id risk; the validator should run a topological sort in strict mode. 2. Re-run the cycle detector. 3. "Check for cycles and unknown prerequisites again." 4. The graph might be circular.

Score: C0 T1 E0 F1 P1 = **3**. Reason: restates what the validator already passed (flaw missed); "dependency cycle" is a near-miss of the right family; re-running the same validator is not new evidence; correction is partial; Q4 is plain.
