# Prompt contracts and evaluation

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Randomness and first prompts](../../01-randomness-and-first-prompts/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 2
**Reading alignment:** Module 1; Module 2 video

## Learning Objectives

- Explain the mechanism behind prompt contracts and evaluation.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable prompt experiment.

## The Problem

A beautifully worded prompt produces an answer your Python program cannot consume. Separate JSON validity, schema validity, and factual validity so each failure has a name.

## The Concept

A prompt is an experimental intervention. State the task, audience, evidence boundary, examples, and output contract. Change one feature at a time and compare against a held-out set. A persona is a hypothesis to test, not a source of expertise.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Parse JSON with the standard library. Reject extra fields and wrong types; require a nonempty answer and source IDs from the supplied evidence. Compute a format-pass rate without calling it an accuracy score.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/02-prompt-contracts-and-evaluation/code/main.py
python3 -m unittest discover -s lessons/02-prompt-contracts-and-evaluation/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Give Claude a baseline prompt and a few-shot revision on the same five development questions. Keep five additional questions held out. Ask for a short explanation and cited evidence, not hidden chain-of-thought. Save failures as well as successes.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Create valid JSON containing a false claim with a valid source ID. Show why the validator accepts it and add a separate human evidence check.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship baseline and revised prompts, development and held-out cases, raw responses, validation results, and a change log.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-02/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Prompt engineering interactive tutorial](https://github.com/anthropics/courses/tree/master/prompt_engineering_interactive_tutorial) — Anthropic's exercises on prompt structure, examples, and separating instructions from data. Compare one technique with your baseline prompt.
- [Prompt evaluations course](https://github.com/anthropics/courses/tree/master/prompt_evaluations) — compare its evaluation approach with your format validator and held-out cases.

After your build, use Claude Code to explain which upstream idea you tested and whether the evidence supports keeping it. Read Python/notebook examples as references; older model IDs and optional tooling do not become course requirements.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Computational Skepticism

Read [Robustness — prompt sensitivity](../../../docs/computational-skepticism.md#prompt-sensitivity). The chapter asks what happens when wording changes while the intended meaning stays fixed.

Add three meaning-preserving paraphrases of one held-out prompt. Lock your prediction of which checks will pass, then compare format validity, factual content, and evidence separately. A stylistic change is not automatically a failure; an altered fact or omitted constraint may be. State the invariance your task actually requires before judging the results.
