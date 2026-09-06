# The agent loop

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Chat, assistant, and agent](../../03-chat-assistant-agent/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 4
**Reading alignment:** Claude Agentic AI Ch. 2

## Learning Objectives

- Explain the mechanism behind the agent loop.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable agent trace.

## The Problem

An agent repeats an unhelpful action and reports completion anyway. Build the controller so exhaustion and success are different outcomes.

## The Concept

A loop needs observable state, a bounded decision step, an action dispatcher, a check, and a stop condition. A trace records transitions; it does not expose a model's private reasoning. Scripted decisions let us test control flow before paying for a model call.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Consume a finite sequence of action dictionaries. Permit only a read-only lookup and finish. Log each observation. Return budget-exhausted or incomplete when no finish occurs; never fabricate a final answer.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/04-the-agent-loop/code/main.py
python3 -m unittest discover -s lessons/04-the-agent-loop/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Trace a Claude Code bug fix and a Claude Cowork document task. Map visible observations and tool results to this controller. The two traces share a feedback structure but have different evidence and permissions.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Make the scripted policy repeat lookup forever using an iterator. Prove that the turn budget still stops execution.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship a trace with turn number, action, observation, stop reason, and the evidence that would justify completion.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-04/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — read the agent discussion for environmental feedback, stopping conditions, and the tradeoff between flexibility and complexity.

Annotate your Python trace with those elements. Identify where the scripted policy would be replaced by Claude and which runtime limits must remain.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Validating Agentic AI — from prediction to action](../../../docs/computational-skepticism.md#agent-outcomes). The chapter shifts attention from what an agent says to the state its actions actually produce.

In this Python controller, status `finished` means the policy emitted a finish action. It does not establish that the answer follows from the records. Construct a script that finishes with a wrong answer, retain the trace, and identify the independent check that would reject its completion claim. Keep control-flow completion and verified task completion separate in your shipped artifact.
