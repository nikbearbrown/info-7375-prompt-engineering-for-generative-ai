# INFO 7375 Prompt Engineering for Generative AI: Fall 2026 exam

## Executive summary
The Fall 2026 exam is **100 points** in two parts: **7 case questions at 10 points (70)** and **6 multiple-answer questions at 5 points (30)**. It tests one skill: using this course's terms precisely to **direct and audit an AI agent**. In each case an agent hands you confident, plausible output with **one planted flaw**. You find the flaw, name it with the exact course term, say what evidence would settle it, and say what you would tell the agent to do next. Grammar and polish earn nothing; ideas do. This folder has two **practice exams** (each with a separate answer file) and a study guide. **The practice exams are practice only. The real exam uses different cases and different questions.**

## What the exam tests
Knowing a word and using it are different skills. The multiple-answer part checks that you know the terms (for example repeatability vs correctness, sentinel value, idempotency key, content binding). The case part checks that you can use them on a live problem: read an agent's output, spot the claim that outruns its evidence, and say the exact thing to say back to the agent. Agent output reads well even when it is wrong, so the exam rewards the habit of asking "what is the evidence for that?"

## Format
| Part | Questions | Points each | Total | Estimated time |
|---|---:|---:|---:|---|
| A. Cases | 7 | 10 | 70 | about 8 minutes a case (about 55 minutes) |
| B. Multiple-answer | 6 | 5 | 30 | about 3 minutes each (about 20 minutes) |
| **Whole exam** | 13 | | **100** | about 75 minutes |

## What a case looks like
Every case has the same four pieces:
1. **Scenario.** A short story: a person with a goal.
2. **The instruction.** What was sent to the agent.
3. **The agent's output.** A plan, log, diff summary or analysis. It sounds sure of itself and contains **one planted flaw** tied to a course concept. (The outputs are written by the course author for illustration; they are not sampled runs of a model.)
4. **Four probes** worth 10 points:

| Probe | Points | What it asks |
|---|---:|---|
| Q1 | 5 | What is wrong with the agent's claim, and what is the exact term? |
| Q2 | 2 | What single check would turn the claim into evidence? |
| Q3 | 2 | Write the correction you would send to the agent. |
| Q4 | 1 | Explain it to the person in the scenario in two sentences, no jargon. |

## Multiple-answer rules
Each question gives **five statements, A to E**. Each statement is either true or false and is worth **1 point** (5 points a question). Check the statements you believe are true and leave the false ones blank. A statement scores if it is checked and true, or left blank and false. Judge each statement on its own. Strong words (always, never, proves) often signal a false statement, but a statement is not false just for sounding strong.

## How cases are scored
| Row | Points | Read from | Full credit means |
|---|---:|---|---|
| Catches the flaw | 3 | Q1 | You say what is wrong with the specific claim, and why it matters |
| Uses the exact term | 2 | Q1 | You use the course term correctly (a near-miss gets 1) |
| Asks for evidence | 2 | Q2 | You name a check that could come out against the agent (not "ask the agent again") |
| Gives a fix or next step | 2 | Q3 | You give the agent a concrete instruction that fixes or re-scopes the claim |
| Keeps scope and plain language | 1 | Q4 | Two sentences a non-expert understands, accurate about the planted flaw, no stronger than the evidence |

**If the planted flaw is missed, the case is capped at 5/10**, however good the rest sounds. A fluent answer about a different problem earns only the rows that happen to apply. **Grammar, length and polish earn nothing.** A correct answer in plain, broken English gets full credit.

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
