# Randomness and first prompts

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** Python programming
**Time:** ~150 minutes, plus independent project work
**Week:** 1
**Reading alignment:** Module 1

## Learning Objectives

- Explain the mechanism behind randomness and first prompts.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable sampling report.

## The Problem

Two runs of the same prompt disagree. Before editing the prompt, distinguish a distribution from a deterministic function. A more confident distribution can still concentrate on a wrong answer.

## The Concept

A language model assigns scores to possible continuations. Softmax converts scores into probabilities; sampling chooses a continuation. Temperature changes the distribution, not the truth of the answer. Our three-token model makes the computation visible without pretending to reproduce Claude's tokenizer or internals.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Subtract the maximum logit for numerical stability. Divide by a positive temperature, exponentiate, and normalize. Sample with a local seeded random generator. Compare empirical counts with probabilities at temperatures 0.5 and 2.0.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/01-randomness-and-first-prompts/code/main.py
python3 -m unittest discover -s lessons/01-randomness-and-first-prompts/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Use Claude chat to repeat one evidence-based prompt three times. Save the exact prompt, outputs, model label, date, and interface. Compare factual correctness separately from surface variation. API settings differ by model: this lab does not assume temperature is universally configurable.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Replace the largest logit with a confidently wrong label. Explain why lower temperature does not repair the answer.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Record logits, temperatures, probabilities, counts, predictions, and the difference between repeatability and correctness.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-01/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

## Computational Skepticism

Read [Probability, Uncertainty, and the Confidence Illusion — calibration](../../../docs/computational-skepticism.md#probability-and-confidence). The chapter separates a model's stated confidence from observed correctness. Your softmax probabilities describe which toy token will be sampled; they are not calibrated probabilities that a generated claim is true.

Before running the experiment, record what you expect changing temperature to do. Then compare the observed counts with that prediction. Explain why choosing a sampling temperature is different from fitting a calibration parameter on labeled held-out data. Neither operation alone establishes factual truth.

## Irreducibly Human

Read [Tier 1 — beneficial offloading and baseline knowledge](../../../docs/irreducibly-human.md#foundations-before-offloading). “AI does AI stuff; humans do human stuff” does not mean skipping the learning that makes supervision possible.

**AI should:** After your first attempt, help diagnose Python errors, propose boundary cases, run authorized checks, and organize the observed sampling results. It can offer explanations for you to test; it should not manufacture your prediction or present its explanation as proof that you understand.

**Human should:** Predict the temperature effect, build the first version, and explain one sample path and one failure without Claude supplying the answer. Decide what the result supports and what it does not. These are protected learning steps, even when Claude could produce the code faster.

**Record the split:** In the sampling report, name one task you delegated and what you did with the time it saved. Include a short unaided explanation of why a repeatable sample can still be wrong. If you cannot explain it, return to the small example before delegating more.
