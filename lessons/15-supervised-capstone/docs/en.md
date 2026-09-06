# Supervised agentic capstone

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Team governance and applied ethics](../../14-team-governance-and-ethics/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 15
**Reading alignment:** Claude Agentic AI Ch. 12

## Learning Objectives

- Explain the mechanism behind supervised agentic capstone.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable capstone packet.

## The Problem

A final demo looks convincing but cannot be reproduced. Require evidence of both the result and the decisions that made the work acceptable.

## The Concept

The capstone combines prompt experiments, retrieval, tool execution, memory, evaluation, and human decisions into one bounded workflow. 'In the wild' means a real context with a consenting owner and approved data, not unrestricted access.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Create a packet validator for ten named artifacts. Check file existence and substantive content, and reject symbolic links that escape the packet. This is structural validation; a human still audits factual evidence, permissions, and understanding.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/15-supervised-capstone/code/main.py
python3 -m unittest discover -s lessons/15-supervised-capstone/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Build a Python workflow using Claude as its only model provider. Demonstrate a failure, a reviewed recovery, and an independently verified result. Use the optional Messages client and tool loop where appropriate. Optionally prepare a recorded Progress Reel to explain the work.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Remove the evidence artifact and verify failure. Then supply a long but meaningless file and explain why a length check cannot grade the work. Add a rubric-based human review.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Submit brief, data boundary, action surface map, plan, gates, pre-mortem, evidence, artifact, audit note, and transfer reflection. Include reproducible commands. A final Progress Reel is optional.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-15/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Anthropic's Claude cookbooks](https://github.com/anthropics/claude-cookbooks) — select a Python example that actually matches your project's mechanism rather than adopting an entire stack.
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — compare your evaluation evidence with its distinction between a recorded trajectory and the resulting state.

In your audit note (and optional Progress Reel), identify the specific upstream example or guidance you adapted, its URL and revision/date, your changes, and the evidence that those changes work. Cite any assigned instructor film by its verified title and link. Keep API execution explicit and preserve the course's Claude/Python scope.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [The Skeptic's Toolkit — the running casebook](../../../docs/computational-skepticism.md#the-casebook) and [Accountability — attestation](../../../docs/computational-skepticism.md#attestation-and-review). The book turns skepticism into recorded predictions, observed failures, and defensible limits on a final claim.

Use one capstone failure as a miniature casebook entry: prediction made before the run, input, action, reported outcome, independently observed outcome, and the gap. Put it in your existing evidence and audit-note artifacts. Close with what you tested, what you did not test, and the actual human decisions. This strengthens the ten-artifact packet; it does not add a second capstone.

## Conducting AI

Read [The Dress Rehearsal and The Plausibility Audit](../../../docs/conducting-ai.md#critique-and-the-gap-account). The distinctive move is to evaluate the reviewer, not to treat a clean review as the finish line.

Before the Claude Code review, record three specific findings you expect, with artifact locations and reasons. Ask for read-only critique of the existing packet, then evaluate each returned finding against located evidence: revise, defend, or acknowledge an unresolved limit. Preserve the prediction, actual findings, and your reasoning in the audit note. Do not manufacture a false positive or force a defense when the reviewer is right.

Close that note with a brief Gap Account: one issue the review did not settle, what additional evidence or expertise could help, and who remains accountable for the decision. Distinguish an observed miss from the book's philosophical claim of an inherent limit; one missed issue does not prove that no future model could detect it. This stays inside the ten-artifact packet, with Claude Code access assumed and no required direct API credits.

## Irreducibly Human

Read [Tier 7 and the conclusion — useful output versus worthwhile action](../../../docs/irreducibly-human.md#purpose-and-accountability). The final division of labor is not “AI writes, human rubber-stamps.” It is assistance with the work and human responsibility for whether the work should be used.

**AI should:** Assemble the existing evidence, run the Python packet validator, identify contradictions, and compare options, including doing less or not deploying. It can challenge your rationale and draft a summary; it must not invent the decision, approval, or personal reflection.

**Human should:** Decide whether the result serves the intended people, weigh competing goods that the score does not settle, and own the ship, narrow, defer, or stop decision. Name who can revisit that decision and what would make you change it. Passing every test does not oblige you to deploy.

**Record the split:** In the transfer reflection, identify one task you will delegate more readily, one capability you must keep practicing, and one decision you will retain. Tie each to evidence from your actual project, including a reason for your final deployment choice. Treat the book's account of irreducibility as an argued position, not a requirement to prove that AI can never help with judgment.
