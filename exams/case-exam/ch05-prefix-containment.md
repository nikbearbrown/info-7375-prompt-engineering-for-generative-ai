# Case 05: The path check

> The agent output below is **author-written for illustration**. It is not a sampled run of any model.

---

## STUDENT PAGE

### Scenario
Professor Okafor lets a Claude agent read course files through a Python `read_file` tool. The agent must only read inside `/data/course`. Next to it, on the same server, is `/data/course-private`, which holds the gradebook. The professor asked you to add a path check and to prove the agent cannot reach anything outside the course folder.

### The instruction (what you sent)
> Add a path check so `read_file` only reads inside /data/course. Handle `..` and symbolic links. Add tests and tell me whether the tool is safe.

### Agent output
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

### Questions (10 points)
1. **(5 pts)** What is wrong with the agent's claim that the tool is safe, and what is the exact term for the flaw?
2. **(2 pts)** What single test or check would turn "safe" into evidence?
3. **(2 pts)** Write the correction you would send to the agent.
4. **(1 pt)** In two sentences, with no jargon, explain the risk to Professor Okafor.

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
**The flaw:** `startswith("/data/course")` compares strings, so `/data/course-private/gradebook.csv` passes; the check must compare path components against the resolved root.

**Full-credit terms (2):** sibling-directory (prefix) flaw; containment check by path components (not string prefix); resolve both paths and compare components.
**Half-credit (1):** "path traversal" (the agent handled it; the term is real but not the flaw); "the check is too loose"; "string matching"; "canonical path" with no sibling example.
**Zero:** "TOCTOU" or "symlink race" (a real issue, but not this flaw, and it earns no term credit), "prompt injection", "hallucination" alone.

**Acceptable evidence requests (any two count):**
- A test that `/data/course-private/gradebook.csv` is denied, shown failing on the current code.
- A test of the root itself, a file named `/data/coursework.txt`, and a path with the root as a prefix of another name.
- Run the check on a list of adversarial paths and read each verdict.

**Unacceptable:** "add more `..` tests"; "run the three tests again"; "ask the agent if it is sure"; "add a prompt telling the agent not to read private files" (instruction, not control).

**Traps:**
- The agent's tests cover traversal and symlinks, so students may say "tests look thorough". The missing case is the sibling directory.
- Students who suggest a denylist for `course-private` fix one name, not the check; give Fix 1 of 2.

**CAP RULE:** flaw missed (no statement that a path starting with the same characters, such as course-private, passes) => case maximum 5/10.

### Scored sample answers
**Strong (9/10).**
> 1. `full.startswith("/data/course")` is a string prefix, so `/data/course-private/gradebook.csv` is allowed. That is the sibling-directory (prefix) flaw: containment must compare path components, not characters. 2. Add the test: realpath of `/data/course-private/gradebook.csv` must be denied; run it and watch it fail on this code. 3. "Replace startswith with `Path(full).is_relative_to(Path(root).resolve())`; add tests for course-private and coursework.txt; fail closed." 4. "The guard checks that a path starts with certain letters, so a folder with a similar name sneaks through, and your gradebook sits in one."

Score: C3 T2 E2 F2 P0 = **9**. Reason: complete; Q4 is plain but runs over two sentences' worth of ideas (three clauses), so the point is withheld.

**Typical (6/10).**
> 1. The check can be fooled by a folder that starts with the same name like course-private. 2. Test course-private. 3. Tell the agent to make the check stricter. 4. A folder with a similar name might be readable, so the gradebook could leak.

Score: C3 T1 E1 F1 P0 = **6**. Reason: names the exact hole in plain words (C3); no term (T1); "test course-private" is right but names no expected outcome (E1); "stricter" is not a concrete instruction (F1); Q4 is plain but lacks consequence being clear (0).

**Fluent-but-wrong (3/10).**
> 1. The check is vulnerable to a TOCTOU race: the file could change between realpath and open, so path traversal and symlink attacks remain. 2. Add a test that swaps a symlink between check and read. 3. "Open the file by descriptor and recheck, and add tests for symlink races." 4. A person could swap a file so the check is fooled.

Score: C0 T1 E0 F1 P1 = **3**. Reason: describes a real but different concern (TOCTOU) and never notices the prefix problem (flaw missed); "path traversal" earns the near-miss point, "TOCTOU" earns nothing; the test requested does not find the actual hole; fix partly relevant; Q4 is plain and short.
