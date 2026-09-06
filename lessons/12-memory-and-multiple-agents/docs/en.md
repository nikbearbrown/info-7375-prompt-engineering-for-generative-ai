# Memory and multiple agents

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Claude tool use and verification](../../11-tool-use-and-verification/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 12
**Reading alignment:** Module 5 video; Claude Agentic AI Ch. 9

## Learning Objectives

- Explain the mechanism behind memory and multiple agents.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable shared memory premortem.

## The Problem

A researcher and a reviewer edit shared notes. The last write erases a correction, and the next agent treats the stale text as truth.

## The Concept

Memory is external state with provenance, ownership, and a lifetime. Multiple workers can read the same version and overwrite one another. Optimistic concurrency checks an expected version at commit time; a stale writer must reread and reconsider.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Create an in-memory versioned record store with deep copies and an atomic lock around check-and-write. Require an expected version and source. Simulate two workers reading version one, then conflicting on their updates. This store is process-local, not a distributed database.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/12-memory-and-multiple-agents/code/main.py
python3 -m unittest discover -s lessons/12-memory-and-multiple-agents/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Use separate Claude sessions as researcher and reviewer on sanitized fixtures. Give each a bounded role and preserve source IDs. Route their proposed memory updates through a coordinator. Record conflicts rather than silently accepting last-writer-wins.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Add expiry metadata and reject expired facts. Compare a memory conflict with a factual disagreement: a newer version is not automatically more truthful.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship a pre-mortem covering stale reads, prompt injection in shared notes, duplicate actions, privacy retention, and an incident replay.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-12/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — study delegation boundaries, coordination failures, and evaluation tradeoffs from Anthropic's implementation.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — compare context-management strategies with your external memory records.

Choose one coordination failure to reproduce with your two-worker fixture. The versioned store is our teaching implementation; these articles do not establish it as Anthropic's internal storage design.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Validating Agentic AI — when agents talk to each other](../../../docs/computational-skepticism.md#shared-state-and-provenance). The chapter identifies errors that propagate through interactions and information that acquires apparent authority merely by passing through another agent.

Write an incorrect value with a fresh version and a plausible source string into your memory fixture. The concurrency check should accept the update; explain why that is correct as concurrency control and insufficient as evidence validation. Add a test scenario in which a downstream worker checks the source before relying on the value. A newer version is not a more truthful claim.

## Conducting AI

Read [Executive Integration — the re-engagement trigger](../../../docs/conducting-ai.md#re-engagement). Version checks handle stale writes; they do not decide which earlier human decision must be reconsidered when new evidence changes the situation.

In your incident replay, introduce a source update that invalidates an assumption in the approved plan. Record the triggering evidence, the earlier scope or verification decision it reopens, the person who must review it, and the downstream work paused pending that review. Do not merely retry the write with a fresh version. Keep a labeled simulation separate from a real incident: the learning target is a visible return to an earlier decision, not a claim that the coordinator automatically understands the conflict.

## Irreducibly Human

Read [Tier 6 — independence before deliberation](../../../docs/irreducibly-human.md#independence-and-deliberation). Two Claude sessions with different role prompts are useful workers, but do not by themselves establish independent judgment.

**AI should:** Carry out bounded research and review tasks, preserve source IDs, compare proposed updates, and summarize disagreements without silently flattening them into consensus. The Python coordinator should enforce version checks; neither a fresh version nor model agreement should count as a human decision.

**Human should:** Have each teammate write an initial interpretation before seeing Claude's synthesis, bring local knowledge the shared notes omit, hear dissent, and decide how to resolve a conflict. Preserve an unresolved disagreement when the evidence does not settle it.

**Record the split:** In the incident replay, compare the teammates' initial judgments with the AI summary. Identify one difference it preserved or lost and the evidence used in the final decision. Do not invent disagreement to complete the exercise. Solo learners can record their own initial judgment, but should not label two model personas as two independent human reviewers.
