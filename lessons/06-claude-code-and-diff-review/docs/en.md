# Claude Code and evidence-based diff review

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Tools, permissions, and boundaries](../../05-tools-and-permissions/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 6
**Reading alignment:** Claude Agentic AI Ch. 4

## Learning Objectives

- Explain the mechanism behind claude code and evidence-based diff review.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable review packet.

## The Problem

An agent fixes the failing test while changing unrelated files. Separate the evidence of correctness from the decision to merge.

## The Concept

A bug-fix claim is a conjunction: the regression is demonstrated, the patch stays in scope, checks pass, and a human accepts the change. A changed-file list is a useful signal but cannot prove semantic safety.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Compute a unified diff with difflib. Build a review function that rejects empty changes, out-of-scope files, failing checks, and missing approval. Feed it results from real commands during the exercise, not invented booleans.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/06-claude-code-and-diff-review/code/main.py
python3 -m unittest discover -s lessons/06-claude-code-and-diff-review/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

In a disposable Python repository, write a failing regression test first. Ask Claude Code for a plan, review it, permit a bounded edit, run the regression and existing tests, inspect the diff, then record the merge decision. Do not merge merely because the tool reports success.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Construct a patch that passes the regression but breaks a different input. Add that input to the regression suite and explain what the first test missed.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship issue, reproduction, plan, before/after diff, exact check commands and output, review notes, and merge decision.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-06/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — focus on giving Claude executable verification and separating exploration, planning, and implementation.

Connect each practice to a concrete item in your review packet: reproduction, plan, diff, or test output. Explain why a passing command still leaves a human scope-review decision.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Communicating Uncertainty — the verb taxonomy](../../../docs/computational-skepticism.md#claims-and-evidence). The chapter treats the strength of a report's wording as something that must be justified by its evidence.

Review your patch summary sentence by sentence. Replace an unsupported claim such as “the bug is completely fixed” with the behavior and inputs actually checked, then name the untested cases. Have a peer identify one sentence whose confidence exceeds the evidence. Preserve the revision and its reason in the review packet.

## Conducting AI

Read [Plausibility Auditing — Audit First](../../../docs/conducting-ai.md#audit-before-verification). The useful distinction is between noticing a possible problem and establishing whether it is actually present.

Before running checks on the Practice Lab patch, record a provisional verdict, a specific verification target, and the constraint or expected behavior that prompted your concern. “I do not know enough to judge” is acceptable if you name the missing knowledge. Then run the targeted test and preserve both records in your review packet. Do not rewrite the initial verdict after seeing the result; an intuition is a reason to investigate, not proof of a bug or permission to skip required checks.
