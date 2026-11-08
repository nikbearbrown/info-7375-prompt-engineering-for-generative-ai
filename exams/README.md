# INFO 7375 Prompt Engineering for Generative AI: exams

**Status: DRAFT, built 2026-11-08. Nothing here is signed off by the instructor.** It is a snapshot of the question bank in `interview-bank/info-7375-prompt-engineering-for-generative-ai`; that copy is the source of truth, and `interview-bank/scripts/build_exam_folders.py` rebuilds this folder from it.

## Executive summary

**What is here.** 767 multiple-answer questions (a bank by chapter), 6 ready-made practice exams of 20 questions each (120 different questions, no question repeated across forms), their answer keys with a reason for every statement, and a cheat sheet.

**How to use it.** Take a practice exam cold, mark it against the matching `-KEY` file, then follow the Why lines for anything you missed. Use the cheat sheet for the terms; the glossary has every term the bank tests.

**What the questions test.** Precise use of the course's terms, so you can tell a language model or an engine exactly what to do. Format: five statements per question; check the ones that are true. Each statement is 1 point, true or false on its own.

**What is not here yet.** Chapters outside the bank's scope (see the bank README), essay questions (retired), and the predict-the-prompt exams (pilot; see below).

## Contents

| Path | What |
|---|---|
| `question-bank/` | 26 markdown files by chapter and topic; `questions.json` (keys and explanations as data); `INDEX.md` (counts) |
| `practice-exams/exam-01.md` to `exam-06.md` | student forms, no answers |
| `practice-exams/exam-01-KEY.md` to `exam-06-KEY.md` | keys with reasons |
| `GLOSSARY-jargon-midterm.md` | every tested term with a one-line meaning |
| cheat sheet | [Midterm_Fall 2026/CHEAT-SHEET.md](Midterm_Fall%202026/CHEAT-SHEET.md) (already existed; not changed) |

## Caveats

- Forms are random draws stratified across sections (seeded: same seed, same forms). They are practice, not a calibrated exam: difficulty is not balanced.
- Keys come from the bank. A statement you think is wrong is a bug in the bank, not in you: report it.
