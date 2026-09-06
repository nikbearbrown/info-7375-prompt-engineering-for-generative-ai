# Planning before acting

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Training mechanics and Claude configuration](../../09-training-and-configuration/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 10
**Reading alignment:** Module 5 video; Claude Agentic AI Ch. 7

## Learning Objectives

- Explain the mechanism behind planning before acting.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable reviewed plan.

## The Problem

A plausible plan omits how success will be tested. Running it faster cannot repair an undefined destination.

## The Concept

A plan externalizes intended work so someone can inspect it before execution. Use eight fields: objective, inputs, scope, steps, tools, risks, verification, and stop conditions. Presence checks catch omissions; a reviewer must judge feasibility and evidence.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Validate the eight fields, then order named steps by dependency. Reject duplicate names, missing prerequisites, and cycles. This explicit graph is a small foundation for planning; it does not invent a plan or estimate whether the work is worthwhile.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/10-planning-before-acting/code/main.py
python3 -m unittest discover -s lessons/10-planning-before-acting/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Ask Claude for a plan for a bounded Python change, using the eight fields. Review the graph before allowing action. Relate the visible plan and tool feedback to ReAct and reflection in theory; assess the plan from evidence rather than requesting hidden reasoning.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Add mutually dependent review and implementation steps. Resolve the cycle by identifying what each step actually needs as input.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship the proposed plan, validation failures, human revisions, stop conditions, and the final approved scope.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-10/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — compare prompt chaining and orchestrator-worker patterns with your dependency graph.
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — examine the exploration and planning guidance before implementation.

Explain whether your task needs a fixed workflow or dynamic decisions. The eight-field checklist is this course's review tool, not a checklist attributed to Anthropic.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Delegation, Trust, and the Supervisory Role — the handoff condition](../../../docs/computational-skepticism.md#delegation-and-handoffs). The chapter treats delegation as a testable contract, not merely a division of tasks.

Take one edge in your dependency graph and write what evidence permits work to cross it, who checks that evidence, and what happens if the check fails. Ask another student to apply the condition to a fixture. If “reviewed” or “reasonable” leaves them guessing, make the condition more precise. An acyclic graph orders work; it does not establish a trustworthy handoff.

## Conducting AI

Read [Problem Formulation — the distinctness test](../../../docs/conducting-ai.md#distinct-reframings). A valid dependency graph can execute the wrong objective perfectly; reframing changes what counts as success, not just the wording of the prompt.

Before asking Claude Code to plan, write three candidate formulations of your bounded change. For each pair, describe a concrete proposed solution that would satisfy one formulation but fail the other. If you cannot, revise the formulations. Select one using feasibility, importance, and whose interests it serves; record one interest it leaves out. Put the selection in the existing plan's objective and scope, then let Claude critique it. You retain the decision; no additional API call is required.
