# Claude tool use and verification

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Planning before acting](../../10-planning-before-acting/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 11
**Reading alignment:** Module 5 video; Claude Agentic AI Ch. 8

## Learning Objectives

- Explain the mechanism behind claude tool use and verification.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable tool evidence matrix.

## The Problem

An agent invents a tool name or requests invalid arguments. The dispatcher must reject that request before execution and preserve the error in the next model turn.

## The Concept

Claude proposes a tool call; Python validates arguments and executes the allowed function. Return a tool_result linked to the tool_use ID. A tool result is evidence about a particular operation, not blanket proof that the final answer is correct.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Create a one-tool allowlist, validate exact argument keys and numeric types, and process every tool_use block. Keep the assistant content unchanged and append user-role tool_result blocks. Bound live turns and stop explicitly on truncation or unsupported stop reasons.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/11-tool-use-and-verification/code/main.py
python3 -m unittest discover -s lessons/11-tool-use-and-verification/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

The reference demo uses scripted response blocks. The optional --live mode connects the same dispatcher to the Claude Messages transport after you configure access. Inspect the complete trace and independently recompute the result. A live run can make up to four billable requests.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Return two tool calls in one assistant response, one valid and one invalid. Verify that both receive matching result IDs and the invalid one is marked as an error.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship tool schema, validation rules, request/result trace, and a matrix pairing each final claim with evidence and an independent check.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-11/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Anthropic's tool-use course](https://github.com/anthropics/courses/tree/master/tool_use) — compare its examples with your tool schema, dispatcher, and error cases.
- [Official tool-result handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) — verify the association between tool requests and result blocks.

In Claude Code, trace one valid and one rejected call through your Python implementation. Explain which checks belong to the runtime. Running an upstream API notebook is an explicit optional credit-consuming extension, not necessary for this comparison.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Model Explainability — the gap between a local action and the user's interpretation](../../../docs/computational-skepticism.md#explanation-and-verification). The chapter examines how an explanation can describe an operation while implying a broader outcome it has not established.

In your evidence matrix, distinguish request accepted, tool executed, result returned, and final claim verified. A matching tool-use ID establishes correspondence, not truth. Recompute the arithmetic independently, then explain what additional observation a file-writing tool would need before claiming that the user's intended result exists. Asking Claude to repeat its assurance is not that observation.

## Conducting AI

Read [Tool Orchestration — verifiability-first engineering](../../../docs/conducting-ai.md#verifiability-first). The chapter's practical question is which operation should leave the probabilistic model entirely.

In your evidence matrix, mark proposal, argument validation, arithmetic execution, and final narration separately. Explain why Python owns the arithmetic and validation while Claude proposes the call and interprets its result. For the independent check, use a hand-worked fixture or separately derived Python calculation, not another invocation of the same helper. Name one shared assumption both routes could still get wrong. Deterministic code can contain silent logic errors; routing work to Python makes it inspectable, not infallible.
