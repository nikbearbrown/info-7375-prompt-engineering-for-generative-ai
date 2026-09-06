# Team governance and applied ethics

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Evaluation and human approval gates](../../13-evaluation-and-approval-gates/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 14
**Reading alignment:** Module 5 video; Claude Agentic AI Ch. 11

## Learning Objectives

- Explain the mechanism behind team governance and applied ethics.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable team ai use register.

## The Problem

A team ships an agent with no owner for memory deletion or incident response. Technical success leaves operational responsibility unresolved.

## The Concept

Governance assigns responsibility for data, actions, evaluation, and incidents. A register makes decisions inspectable, but a completed form does not establish ethical acceptability. Examine who benefits, who can be harmed, and who can challenge a result.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Validate an AI-use record for owner, purpose, data classes, retention days, approver, evaluation, and incident contact. Route sensitive data and external writes to explicit review. These are classroom categories, not a legal compliance determination.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/14-team-governance-and-ethics/code/main.py
python3 -m unittest discover -s lessons/14-team-governance-and-ethics/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Draft a register entry for the capstone's actual Claude workflow. Map access, affected people, failure recovery, and appeal routes. Use the Week 11 evidence matrix and Week 13 gate as supporting artifacts rather than relying on a model-generated ethics paragraph.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Compare two equally accurate agents with different retention periods and write authority. Explain why identical accuracy does not imply identical risk.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship a team register entry, harm scenario, mitigation owner, monitoring threshold, retention plan, and incident escalation path.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-14/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Claude Code security](https://code.claude.com/docs/en/security) — use Anthropic's security guidance to examine access boundaries and handling of untrusted inputs in your team's workflow.

Connect one recommendation to a named owner and incident response in your register. Product guidance supplements the course's governance analysis; Northeastern's policies still determine permitted institutional use.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Fairness Metrics — the defended choice](../../../docs/computational-skepticism.md#values-and-accountability) alongside the accountability chapter's discussion of recourse. The book asks who bears an error's cost, who chooses the criterion, and who can challenge the result.

If your workflow ranks or evaluates people, defend a relevant fairness criterion and its tradeoffs. Otherwise, identify a concrete harm and the stakeholder who bears it; do not manufacture demographic metrics for an unrelated task. Add the decision owner, a usable route for contesting an output, and the evidence that would change the team's choice to your register.

## Conducting AI

Read [Interpretive Judgment — Memo B](../../../docs/conducting-ai.md#interpretation-and-accountability). The book separates Claude's contribution from the human interpretation of what a recommendation means in its actual setting.

Add a short decision note to your existing team register: what Claude proposed; what context you added or corrected; what evidence supports the decision; whose interests it serves or disadvantages; and the named human recommendation. Use the retention or write-authority comparison from Practice Lab. Highlight a sentence that merely restates Claude, then distinguish it from a sentence that supplies a concrete contextual reason. A name on unchanged model prose is not evidence of review; do not invent approval.

## Irreducibly Human

Read [Tier 3 — supervise the assistance, protect the relationship](../../../docs/irreducibly-human.md#relationships-and-consent). A polished communication is not evidence that an affected person was heard.

**AI should:** Draft a plain-language explanation of the proposed workflow, suggest questions for a stakeholder conversation, and organize approved, sanitized feedback. It should flag uncertainty and preserve objections rather than invent consent or speak as though it represents the stakeholder.

**Human should:** Hold the conversation, listen to concerns that do not fit the draft, negotiate expectations, and remain reachable for correction or repair. Obtain actual permission where needed and decide how the feedback changes retention, access, or deployment.

**Record the split:** Add to the register one question Claude helped prepare and one change or unresolved concern from a real, consented discussion. If using classroom role-play, label it as simulation and state which real consultation remains pending. Fluent reassurance is not a substitute for consent or a functioning human appeal route.
