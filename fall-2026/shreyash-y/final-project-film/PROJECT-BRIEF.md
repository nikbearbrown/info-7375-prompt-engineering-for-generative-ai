# Project Brief — ClaimCheck (working title)

2026-10-07, updated 2026-10-14. Nothing
for this project has been built yet, so everything about the tool below is "will."

## 1. What is it?

**A question-answering tool for insurance claim files that only answers from the
documents, quotes the exact clause it used, and says "not in the documents" when the
answer isn't there.**

When it's done, there will be a public GitHub repository containing a Python command-line
tool built on Claude, a synthetic claim file (policy, endorsement, claim form,
adjuster notes), a frozen test set of questions with correct answers and source
passages, an evaluation script, and a written analysis of where the tool fails.

## 2. Why would anyone care?

It will save a claims examiner from hunting through a long policy for the one clause that
decides a question, and from trusting a fluent answer that cites nothing. The thing it
will do that alternatives don't: **check its own citation with code.** Every answer has
to quote a passage, and a script confirms that the passage really exists in the
document and really contains the answer. If either check fails, the answer is
rejected and doesn't reach the reader.

Alternatives I tried (confirmed 2026-10-07):
- **Uploading the PDF to a general chat assistant.** It gives fluent answers but no
  test set, so there's no way to know how often it's wrong. Citations, when given,
  aren't checked.
- **A LlamaIndex / LangChain RAG template.** It retrieves chunks well but, out of the
  box, returns whatever the model says, with no evaluation set and no "not in the
  documents" rule.

## 3. Who opens it, and what do they do with it?

Target role: applied-AI / LLM engineer at an insurtech or health-tech company.
Reader: the hiring manager or engineer screening for that role. The end user in the
story is a claims examiner.

First sixty seconds: they read the README and run one command. That command prints the
evaluation table: each test question with pass or fail, the clause the tool cited,
and the questions it got wrong, which are listed first.

## 4. What does it prove about you?

- **Prompt contracts:** a written contract for the answer format (an answer, a quoted
  span, the document ID, or a refusal), enforced by a parser, not just by hoping the
  model follows it.
- **Source grounding and verification:** a deterministic citation check outside the
  model.
- **Evaluation:** a test set frozen before any prompt tuning, plus a log tying each
  prompt change to its score change.
- **Honest failure analysis:** a write-up of the failures, sorted by type.

What a reviewer could fairly conclude: I can put a checker around an LLM and measure
it honestly. What they could not conclude: that it works on real claims. It will only
ever be tested on synthetic data.

## 5. What is in, what is out, what comes first?

**In:** one synthetic claim file and roughly 30–50 questions, including trick questions
(answer not in the file, an endorsement that overrides the base policy, a number buried
in a table).
**Out, deliberately:** it will never decide whether a claim is covered, approve it, or
deny it. It only finds and quotes. It will never be shown real claims or real
customer data.
**First piece to run:** one synthetic policy, 10 questions, the citation checker, and
an `eval_report.md`. You'll know it ran because a dated report file shows pass or fail for
each question.

## 6. What could sink it?

I will write the documents, the questions, and the tool, so the test can end up
measuring my own blind spots, and the score will look better than it really is. What
I'll do about it: freeze the test set before tuning any prompts, make at least a third of the
questions adversarial, and log every prompt change with its score.

## 7. Why this project?

It's a mix. **Skill I already have, with evidence:** putting a deterministic checker around
an LLM. My evidence is Dovetail, my errand-planning agent, where a Python solver checks
the LLM's plan. All 47 of its offline tests passed when I re-ran them on 2026-10-07
(output saved in `evidence/dovetail-pytest-2026-10-07.txt`). **New to me:** the Claude API, writing prompt
contracts, and building a source-grounded test set with a failure analysis. Those are what this course
teaches. I picked insurance claims because it's the domain I want to work in.

---

## Exists today
- This brief (2026-10-07, updated 2026-10-14), the beat sheet (2026-10-07), and this
  3:33 pitch film (rendered 2026-10-14).
- No code, data, or test set for this project yet.
- Prior evidence for Q7 only (separate project): the Dovetail repository; its 47
  offline tests passed on 2026-10-07 (`evidence/dovetail-pytest-2026-10-07.txt`).

## Will exist
- The synthetic claim file and its source/licence notes.
- The frozen test set, with answers and source passages.
- The Python + Claude command-line tool with an answer-format contract and a citation checker.
- `eval_report.md`, a prompt-change log, and a failure analysis.
- A README with a one-command reproduction.
