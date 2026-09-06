# Context retrieval and Claude Cowork

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Claude Code and evidence-based diff review](../../06-claude-code-and-diff-review/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 7
**Reading alignment:** Claude Agentic AI Ch. 5; Module 3 video

## Learning Objectives

- Explain the mechanism behind context retrieval and claude cowork.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable source grounded task packet.

## The Problem

A document assembly task cites a plausible passage that does not answer the question. Debug retrieval separately from generation and check every resulting claim against its source.

## The Concept

Retrieval selects evidence before generation. Build word vectors with counts and cosine similarity to expose representation, scoring, and ranking. These are lexical vectors, not neural embeddings. Claude receives the selected passages as context; no external embedding provider is required.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Tokenize with a regular expression, count terms, compute a sparse dot product and vector norms, then rank documents. Exclude zero-overlap documents and break ties deterministically. Measure how synonym queries fail before proposing a better representation.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/07-context-retrieval-and-cowork/code/main.py
python3 -m unittest discover -s lessons/07-context-retrieval-and-cowork/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Build a Claude Cowork task packet containing goal, permitted sources, output format, exclusions, and acceptance checks. Use the retriever's source IDs to inspect coverage. Assemble a Markdown report in a controlled folder and verify quoted facts against the originals.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Query 'tuition refund' against a document that only says 'fee reimbursement.' Explain the zero score. Add a small, explicit synonym map and measure both useful matches and false positives.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship corpus with provenance, retrieval results, task packet, report, and a claim-to-source evidence table.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-07/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

## Verify It

Run the demo and six tests, then your two additional tests. Preserve commands, observed outputs, and your interpretation. Compare observed behavior with the claim you intend to make. A passing test suite establishes only the tested behavior, not universal reliability or permission to act.

## Assessments

1. Reimplement the core function without looking at the reference, then compare behavior.
2. Complete the boundary experiment in Practice Lab with your own fixture.
3. Integrate the artifact into your capstone and document a case where it should refuse or escalate.

## Capstone Connection

Add this week's artifact to the evidence trail for the Week 15 project. Explicitly name which capstone claim it supports and what additional review that claim still needs.

## Knowledge Check

Answer [quiz.json](../quiz.json): one pre-question, three comprehension checks, and two transfer questions. Explanations are included for self-review after answering.

## Anthropics

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic discusses selecting useful context, tool design, and managing information over a task.

Compare your selected passages with supplying the whole corpus in Claude Code. Record relevance and missing evidence. The article guides context design; it does not turn this lesson's lexical count vectors into neural embeddings.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Data Validation — reconstructing the epistemic frame](../../../docs/computational-skepticism.md#data-and-retrieval). The chapter asks what a dataset excludes before interpreting what its contents appear to establish.

Apply that question to your retrieval corpus: which sources should be present, which were ingested, and what did filtering or chunk selection leave out? Trace one answer passage to its original source. Distinguish “not retrieved” from “not in the corpus” and from “not true.” A high cosine score cannot resolve those differences. Add the missing-source finding to your task packet rather than filling it with a plausible answer.
