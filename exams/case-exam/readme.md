# INFO 7375 case exam: direct and audit an agent

Written 2026-11-08. Author-written drafts for Bear to review; nothing here is committed or pushed. Claude and Python only.

## What this is
The 30-point multiple-answer jargon section tests whether students know the terms. The case section tests whether they can **use** the terms to audit an agent. Each case gives a student:

1. a short **scenario** (a stakeholder and a goal),
2. the **instruction** that went to the agent,
3. the agent's **output** (a plan, diff summary, log or analysis), confident and plausible, with **one flaw** seeded on a concept from a chapter,
4. **four probes** worth 10 points.

The agent outputs are **written by the author for illustration; none is a sampled run of a model.** A TA grades by a fixed rubric plus a case key. The exam is short-essay in form but graded on content only.

One case per unit: `ch00` (foundations) and `ch01` to `ch15`. A live exam would use a handful of them (for example three cases = 30 points with the 30-point jargon section); the rest are a bank. Flaws are distinct across the 16 cases.

## Student page: the four probes
| Probe | Points | What it asks |
|---|---:|---|
| Q1 | 5 | What is wrong with the agent's claim, and what is the exact term? |
| Q2 | 2 | What single check or instruction turns the claim into evidence? |
| Q3 | 2 | Write the correction you would send to the agent. |
| Q4 | 1 | Explain it to the stakeholder in two sentences, no jargon. |

## Shared rubric (10 points per case)
| Category | Points | Scored from | Full credit means |
|---|---:|---|---|
| Catches the flaw | 3 | Q1 | The student says what is wrong with the specific claim, in any wording (3 = the flaw and why it matters; 1-2 = partly or without the mechanism; 0 = a different problem) |
| Exact term | 2 | Q1 | Uses a full-credit term from the case key correctly (2); a near-miss from the half-credit list (1); none or wrong (0) |
| Asks for evidence | 2 | Q2 | Names a check that could come out against the agent's claim (2 = specific and decisive; 1 = right direction but vague; 0 = repeats the agent's own check or asks the agent to confirm itself) |
| Fix or next step | 2 | Q3 | A concrete instruction to the agent that fixes or re-scopes the claim (2; 1 = partial or relies on a promise; 0 = none) |
| Scope and plain language | 1 | Q4 | Two sentences or fewer a non-expert understands, accurate **about the planted flaw**, and no stronger than the evidence (1 or 0). A clear note about a different problem scores 0 |

**CAP RULE (every case):** if the student misses the planted flaw (Catches the flaw = 0), the case maximum is **5/10**, however good the rest sounds. Fluent text about other, real, topics earns at most term, evidence, fix, and plain points that happen to apply.

## TA grading guide
1. **No credit for grammar, length or polish.** Many students write in a second language. Score the ideas. A correct answer in plain, broken English is a full-credit answer. A long, polished answer about the wrong problem is a low score.
2. **Grade one case across all students**, then the next case. This keeps your reading of the key steady.
3. **Calibrate first.** Before grading, all TAs score the three sample answers in that case's key *without looking at the listed scores*, then compare. Agreement must be **within 1 point** on each sample. If not, discuss the key and repeat before grading real answers.
4. **Double-score 10%.** A second TA independently scores about 10% of each case. Differences over 1 point go to the instructor.
5. **One-line reason for any score under 4.** Write it next to the score (for example: "fluent about TOCTOU; never mentions the prefix check"). This protects students on appeal.
6. **Time:** about 4 to 5 minutes per case. If a case takes longer, you are reading for polish.
7. **Order of reading:** find the flaw sentence in Q1 first (Catches the flaw). If absent, the cap applies; then score the rest.
8. **Use the key's lists, not your own judgement of "close"**: full-credit terms (2), near-misses (1), unacceptable evidence requests (0). A new reasonable wording is allowed; mark it for the instructor if unsure.
9. **Traps** in each key list the common wrong-but-fluent answers.

## Index
| Case | Chapter / topic | Case title | Seeded flaw (one line) | Key terms |
|---|---|---|---|---|
| [ch00](ch00-foundations-overfitting.md) | Foundations | The perfect router | 100% accuracy measured on the training emails | overfitting, generalization, held-out set |
| [ch01](ch01-temperature-zero-repeatability.md) | 1 Next-token prediction | The stable labels | Two identical runs at temperature 0 called "correct" | repeatability vs correctness, greedy decoding |
| [ch02](ch02-json-mode-grounding.md) | 2 Prompt contracts and evaluation | Every answer cites a source | Citation ids exist, so "grounded"; support never checked | structural validity vs grounding, citation vs support |
| [ch03](ch03-fabricated-approval.md) | 3 Chat, assistant, agent | The approval nobody gave | Summary names a human approver; harness log shows a simulated approval | fabricated record, simulated approval, self-report vs audit log |
| [ch04](ch04-sentinel-not-found.md) | 4 The agent loop | "Not found" means not found | Placeholder "not found" read as proof of absence; second lookup shares the bad key | sentinel value, claim vs evidence, independent check |
| [ch05](ch05-prefix-containment.md) | 5 Tools and permissions | The path check | `startswith("/data/course")` admits `/data/course-private` | sibling-directory (prefix) flaw, containment check |
| [ch06](ch06-scope-creep.md) | 6 Claude Code and diff review | Only two files | Summary says two files; diff stat shows the off-limits third | scope creep, scope check, diff review |
| [ch07](ch07-retrieval-not-fine-tuning.md) | 7 Retrieval and Cowork | "It has learned the handbook" | Retrieval into the prompt reported as fine-tuning that "keeps learning" | retrieval vs fine-tuning |
| [ch08](ch08-mcp-advertised-read-only.md) | 8 MCP from scratch | "Read-only", says the server | Advisory annotations and descriptions taken as proof | advertised evidence, annotation is advisory, enforcement outside the model |
| [ch09](ch09-tutor-confounder.md) | 9 Training and configuration | The tutor effect | Score gap between volunteers and others read as a causal effect | association vs intervention, confounder |
| [ch10](ch10-hidden-dependency.md) | 10 Planning before acting | The valid plan | Acyclic plan with no edge ordering the drop after backup and verification | hidden dependency, acyclic does not mean executable |
| [ch11](ch11-retries-idempotency.md) | 11 Tool use and verification | Retries are safe | Retrying `create_invoice` after a lost reply makes a duplicate | idempotency key, side effect |
| [ch12](ch12-check-then-act-race.md) | 12 Memory and multiple agents | The version check | Compare-and-set written as check then write; sequential test | race condition, atomic operation, lost update |
| [ch13](ch13-approval-binding.md) | 13 Evaluation and approval gates | The approved proposal | Approval stored by proposal id; action list editable afterwards | content binding, stale approval, TOCTOU |
| [ch14](ch14-rate-vs-severity.md) | 14 Governance and ethics | Under the threshold | 1.5% error rate under a 2% rule hides one severe harm | aggregate rate vs severity, stop rule |
| [ch15](ch15-trivial-tests-planted-defect.md) | 15 Supervised capstone | Tests that catch defects | Tests use ordinary inputs; boundary and cap untested; one planted defect | adversarial test case, surviving mutant, planted defect |

## File layout of each case
`## STUDENT PAGE` (scenario, instruction, agent output, questions) then `## TA RUBRIC PAGE` (fixed rubric, case key, three scored sample answers). Print the student page alone for students; give TAs the second half.

## Sample answers
Each key has three sample answers: **strong (about 9), typical (about 6) and fluent-but-wrong (about 3)**. Each shows its category scores (C = catches, T = term, E = evidence, F = fix, P = plain) and the TA's one-line reason. They are author-written, used for calibration, and should be replaced with real anonymised student answers after the first sitting.

## Status
Drafted and checked by an AI blind reader (see `blind-check.md`). Not reviewed by the instructor. The flaws, wording and terms need Bear's read; terms are taken from `GLOSSARY-jargon-midterm.md`.
