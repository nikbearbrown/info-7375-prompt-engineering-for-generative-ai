# INFO 7375 Prompt Engineering for Generative AI: Fall 2026 exam

## Executive summary
The Fall 2026 exam is **100 points** in two parts: **5 case questions at 10 points (50)** and **10 multiple-answer questions at 5 points (50)**. It tests one skill: using this course's terms precisely to **direct and audit an AI agent**. In each case an agent hands you confident, plausible output with **one planted flaw**. You find the flaw, name it with the exact course term, say what evidence would settle it, and say what you would tell the agent to do next. Grammar and polish earn nothing; ideas do. This folder has two **practice exams** (each with a separate answer file) and a study guide. **The practice exams are practice only. The real exam uses different cases and different questions.**

## What the exam tests
Knowing a word and using it are different skills. The multiple-answer part checks that you know the terms (for example repeatability vs correctness, sentinel value, idempotency key, content binding). The case part checks that you can use them on a live problem: read an agent's output, spot the claim that outruns its evidence, and say the exact thing to say back to the agent. Agent output reads well even when it is wrong, so the exam rewards the habit of asking "what is the evidence for that?"

## Format
| Part | Questions | Points each | Total | Estimated time |
|---|---:|---:|---:|---|
| A. Cases | 5 | 10 | 50 | Half of the available answering time |
| B. Multiple-answer | 10 | 5 | 50 | Half of the available answering time |
| Reading, checking, handing in | | | | about 10 minutes |
| **Whole exam** | 15 | | **100** | Use the instructor-announced duration; no new duration is set here |

## What a case looks like
Every case has the same four pieces:
1. **Scenario.** A short story: a person with a goal.
2. **The instruction.** What was sent to the agent.
3. **The agent's output.** A plan, log, diff summary or analysis. It sounds sure of itself and contains **at least one flaw** (there may be more), each tied to a course concept. (The outputs are written by the course author for illustration; they are not sampled runs of a model.)
4. **Five case-specific questions**, 10 points total. Each question must refer to this case's claims, evidence, constraints or decision-maker, not merely ask for a general essay.

| Question role | Points | What it asks |
|---|---:|---|
| Q1 | 3 | Identify a consequential defect and justify it using the case. |
| Q2 | 2 | Name and apply the precise course concept to that defect. |
| Q3 | 2 | Propose a concrete evidence check and say what outcome would support or defeat the claim. |
| Q4 | 2 | Write a corrected instruction tailored to this case. |
| Q5 | 1 | Explain the consequence plainly to the case's decision-maker. |

Short bullets or one or two sentences per probe are enough. There is no sentence-count rule and no credit for length.

## Multiple-answer rules
Each question gives **five statements, A to E**. Each statement is either true or false and is worth **1 point** (5 points a question). Check the statements you believe are true and leave the false ones blank. A statement scores if it is checked and true, or left blank and false. Judge each statement on its own. A question can have anywhere from zero to five true statements, so do not look for a pattern.

## How cases are scored
The cases are scored against **the defect you identify**. The planted flaws are the answers the author expects, but you do not have to read the author's mind: if you find a different real problem in the agent's output and explain why it is a real problem, you earn the marks.

| Row | Points | Read from | Full credit means |
|---|---:|---|---|
| Catches a real defect | 3 | Q1 | You name a real defect in the agent's output **and** give a reason a marker can check against the case. 3 = real defect, sound reason; 1 to 2 = real defect but a thin or partly wrong reason; 0 = no real defect, or only a bare assertion with no reason ("it is unreliable") |
| Uses the exact term | 2 | Q2 | A standard course term (or an accepted standard equivalent) for **your** defect, used correctly. A loose label or a correct description with no standard name gets 1 |
| Asks for evidence | 2 | Q3 | **One** specific check that could come out against the agent's claim and addresses **your** defect. Vague = 1. A check that does not address your defect, repeats the agent's own check or asks the agent to confirm itself = 0 |
| Gives a fix or next step | 2 | Q4 | A concrete instruction that addresses **your** defect. Partial or a promise = 1; unrelated to your defect = 0 |
| Plain language | 1 | Q5 | Plain words a non-expert understands, accurate about your defect and no stronger than the evidence. Length does not matter |

If you identify no real defect with a reason, the case is capped at 5/10 (the other rows then usually score 0, because there is nothing identified to address). Grammar, length and polish earn nothing. A correct answer in plain, broken English gets full credit. Each key lists the planted flaws, the terms that earn credit, and **other defensible defects** with the reason each needs.

## Current practice generator

Use [EXAM-GENERATOR-PROMPT.md](EXAM-GENERATOR-PROMPT.md) as standalone Claude Project instructions for new-format examples. Starter knowledge is embedded; no extra upload is needed. It is a draft practice coach, not a prediction of the actual exam. The compact term list is still being narrowed by the instructor.

**Historical exercises:** The two existing practice papers and their keys below retain the old 7-case/6-multiple-answer format. Use them for topic drills, not as the current-format template. They have not been rewritten.

## How to practise
1. Open [practice-exam-01.md](practice-exam-01.md). Do it **cold**: no notes, about 75 minutes, writing real answers.
2. Only then open [practice-exam-01-KEY.md](practice-exam-01-KEY.md). For each case, read the flaw, the terms that earn credit and the near-misses, and compare with your answer. Score yourself with the table above.
3. Write down which terms you missed, study them, then repeat with [practice-exam-02.md](practice-exam-02.md) and [its answers](practice-exam-02-KEY.md).

Every exam and its answers are separate files on purpose. Do not read the answers before you answer.

The two practice exams share no cases and no multiple-answer questions. They are practice only: **the real exam uses different cases and different questions**, so do not study by memorising these.

## What to study
- [Jargon glossary](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/GLOSSARY-jargon-midterm.md): each term in plain words.
- [Question bank](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/question-bank/INDEX.md): hundreds of multiple-answer questions with explanations.
- Six more multiple-answer practice exams (20 questions each) in [practice-exams](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/): [01](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-01.md), [02](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-02.md), [03](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-03.md), [04](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-04.md), [05](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-05.md), [06](https://github.com/nikbearbrown/interview-bank/tree/main/info-7375-prompt-engineering-for-generative-ai/ma-exams/practice-exams/exam-06.md). Their answers are in the matching `-KEY` files; read them after you answer.

## Files in this folder
| File | What it is |
|---|---|
| [practice-exam-01.md](practice-exam-01.md) | Practice exam 1: 7 cases and 6 multiple-answer questions, no answers |
| [practice-exam-01-KEY.md](practice-exam-01-KEY.md) | Answers and scoring notes for practice exam 1 |
| [practice-exam-02.md](practice-exam-02.md) | Practice exam 2: different cases and questions, no answers |
| [practice-exam-02-KEY.md](practice-exam-02-KEY.md) | Answers and scoring notes for practice exam 2 |


## Updated preparation guides

Use [EXAM-PREP-GUIDE.md](EXAM-PREP-GUIDE.md), [HOW-TO-PREPARE.md](HOW-TO-PREPARE.md) and the [standalone Claude Project practice prompt](EXAM-GENERATOR-PROMPT.md) for the revised format. Historical paper timing and counts above are retained for those old-format exercises, not a new exam-duration announcement.
