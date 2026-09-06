# Tools, permissions, and boundaries

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [The agent loop](../../04-the-agent-loop/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 5
**Reading alignment:** Claude Agentic AI Ch. 3

## Learning Objectives

- Explain the mechanism behind tools, permissions, and boundaries.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable permission policy.

## The Problem

A seemingly harmless relative path escapes the intended folder. The dangerous middle is enough access to cause harm without enough context to recognize it.

## The Concept

Least privilege is executable policy. Resolve a requested path under an allowed root, check the operation, and require independent approval for writes. A prompt asking for caution cannot replace a runtime boundary.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Normalize paths with pathlib.resolve, reject paths outside the root, and distinguish reads from writes. Test traversal and sibling-prefix attacks. Recognize that this preflight check alone is not an operating-system sandbox.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/05-tools-and-permissions/code/main.py
python3 -m unittest discover -s lessons/05-tools-and-permissions/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Inspect Claude Code's actual permission configuration on a disposable repo. Propose a narrowly scoped action surface for the same task. Run only operations authorized for that exercise and inspect the resulting diff.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Create a symlink inside a temporary root pointing outside it. Verify rejection. Explain the remaining race if another process changes the symlink after validation.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship the root, allowed operations, approval owner, denial cases, and a test proving that traversal is rejected.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-05/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Claude Code permissions](https://code.claude.com/docs/en/permissions) — compare real permission rules and modes with your Python operation allowlist.
- [Claude Code security](https://code.claude.com/docs/en/security) — read the safeguards and remaining responsibilities around commands, untrusted content, and access.

Use Claude Code to inspect the permissions in your course environment. Document one boundary enforced by the product and one that your path-checking function cannot enforce. Do not change institutional settings as part of this comparison.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).
