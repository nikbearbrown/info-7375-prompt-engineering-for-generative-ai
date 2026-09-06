# Chat, assistant, and agent

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Prompt contracts and evaluation](../../02-prompt-contracts-and-evaluation/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 3
**Reading alignment:** Claude Agentic AI Ch. 1

## Learning Objectives

- Explain the mechanism behind chat, assistant, and agent.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable action surface comparison.

## The Problem

The same request, 'fix this report,' can yield advice, a grounded revision, or an actual file change. A student needs to identify which outcome occurred and what evidence proves it.

## The Concept

See, decide, and do describe different capabilities. Reading a file expands observation; writing a file changes state. A system becomes action-capable because its runtime grants tools, not because its prose calls itself an agent.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Represent a request as required capabilities and each interface as granted capabilities. Compute the missing set. Keep capability classification separate from authorization to act.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/03-chat-assistant-agent/code/main.py
python3 -m unittest discover -s lessons/03-chat-assistant-agent/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Run the same small task through Claude chat, Claude with an uploaded source, and Claude Code in a disposable Python repo. Record files before and after. Classify each observed operation; do not infer tool access from the product name alone.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Add a read-only tool to chat. Explain whether your classification changes and why access alone still does not authorize a write.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Create a three-interface comparison with observed inputs, granted capabilities, proposed actions, actual state changes, and evidence.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-03/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic distinguishes predefined workflows from systems in which the model chooses its next actions.

Compare that architectural distinction with this lesson's see/decide/do teaching model. A write-capable system is not necessarily dynamically agent-directed: explain what the simple classifier leaves out.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Conducting AI

Read [Three Levels of AI Usage](../../../docs/conducting-ai.md#usage-and-supervision). The book classifies work by the supervision it demands, whereas this lesson classifies interfaces by capabilities. Those are different axes: Claude Code can perform a bounded rewrite or help shape an open-ended decision.

Add a supervision column to your existing comparison. For one bounded edit, one source-dependent answer, and one problem-framing request, name what you must inspect and what knowledge that inspection requires. Explain why unchanged tool permissions do not imply an unchanged review burden. Treat the book's levels as a teaching framework, not product categories.
