# Evaluation and human approval gates

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Memory and multiple agents](../../12-memory-and-multiple-agents/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 13
**Reading alignment:** Module 5 video; Claude Agentic AI Ch. 10

## Learning Objectives

- Explain the mechanism behind evaluation and human approval gates.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable approval gate design.

## The Problem

An 'Allow?' button conceals a changed destination. A generic yes must not authorize a different action later.

## The Concept

A useful gate names the action, target, reason, effects, evidence, and rollback. Bind approval to the exact proposal so a changed target requires a new decision. A hash detects changes; it does not authenticate a human or establish authority by itself.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Canonicalize a six-field proposal and compute its SHA-256 fingerprint. Compare a recorded approval to the current proposal. Reject changed content and absent approvers. Keep identity verification and expiry as explicit production requirements.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/13-evaluation-and-approval-gates/code/main.py
python3 -m unittest discover -s lessons/13-evaluation-and-approval-gates/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Take a real Claude tool proposal and rewrite its approval request using six fields. Evaluate task success, invalid action rate, and reviewer burden separately. Explain what evidence the reviewer needs before approving the proposed action.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Approve a proposal, change its target, and demonstrate rejection. Add a deadline and single-use decision ID, then test expiry and replay.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship before/after gate wording, an evaluated proposal, rejection tests, and the human decision record without fabricated approvals.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-13/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — distinguish tasks, trials, graders, transcripts, and actual outcomes.
- [Claude Code permissions](https://code.claude.com/docs/en/permissions) — compare the product's approval behavior with your proposal-bound gate.

Write one outcome check that could contradict an agent's success claim. The six-field gate and fingerprint are course mechanisms, not claims about Anthropic's authentication implementation.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Accountability — the attestation you sign](../../../docs/computational-skepticism.md#attestation-and-review). The chapter requires a sign-off to declare what was checked, what remains unchecked, who made the decision, and what the evidence warrants. It also insists that a reviewer must be able to withhold approval.

Attach that account to one proposal in your gate design. Record one unresolved gap that would make the reviewer decline or defer. The fingerprint binds a decision to content; it does not establish that the reviewer performed the checks, understood the consequences, or had authority to approve.

## Irreducibly Human

Read [Tier 4 — the volume trap](../../../docs/irreducibly-human.md#review-capacity). A gate needs a reviewer with time and evidence, not just a place to store an approval.

**AI should:** Prepare the six-field proposal, surface changed fields and missing evidence, run the specified checks, and queue work when review is pending. It should stop at the authorization boundary rather than treating silence, a timeout, or its own favorable assessment as consent.

**Human should:** Set a review workload they can actually handle, inspect the exact action and supporting evidence, and approve, refuse, or defer within their authority. Decide what requires another specialist; do not accept a faster stream of proposals by merely clicking faster.

**Record the split:** Extend the gate evaluation with a small, labeled backlog simulation: submit several proposals while one is awaiting review. Show which actions remain blocked and name the pause or escalation rule. Measure actual review time if reporting it; otherwise label the budget as a design assumption. The fingerprint checks unchanged content, not available human attention.
