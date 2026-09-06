# Training mechanics and Claude configuration

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [MCP from scratch](../../08-mcp-from-scratch/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 9
**Reading alignment:** Module 4

## Learning Objectives

- Explain the mechanism behind training mechanics and claude configuration.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable training versus context report.

## The Problem

A student says that uploading documents 'trained Claude.' Build and measure an actual parameter update, then contrast it with changing a prompt.

## The Concept

Training changes parameters; prompting and retrieval change inference inputs. A tiny logistic model exposes gradient descent: prediction is sigmoid(wx+b), cross-entropy measures error, and its gradient updates w and b. This is a binary classifier, not a language model or a Claude fine-tune.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Compute sigmoid stably, derive the binary cross-entropy gradient, and run a bounded training loop. Evaluate on a separate test set. In video theory connect this to next-token pretraining, instruction tuning, preference optimization, and RLHF without claiming this toy implements those systems.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/09-training-and-configuration/code/main.py
python3 -m unittest discover -s lessons/09-training-and-configuration/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Keep Claude as the external model. Compare a baseline prompt, a few-shot prompt, and retrieved context on the same task. Record that these experiments do not modify Claude weights. Model availability and configurable parameters must be checked against current official documentation.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Reverse the training labels and inspect how learned parameters change. Then add duplicate test examples to training and explain why the apparent improvement would be leakage.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship loss history, parameters before/after, held-out results, and a comparison table of parameter learning, prompt changes, and context changes.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-09/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

## Irreducibly Human

Read [Tier 5 — prediction versus identification](../../../docs/irreducibly-human.md#prediction-and-intervention). The classifier learns an association; deciding to change the world on that basis is a different question.

**AI should:** Help inspect the gradient calculation, run the bounded Python experiments, tabulate held-out predictions, and suggest competing explanations for a pattern. It may draft a causal diagram or experiment proposal, but must label assumptions rather than present a plausible story as established causation.

**Human should:** Decide whether the intended use asks “what will happen?” or “what happens if we intervene?” Define the outcome, justify the data and causal assumptions, and identify what evidence or domain expertise is missing before acting. A human's intuition is not sufficient causal evidence either.

**Record the split:** Add two sentences to the training-versus-context report: one predictive claim supported by your actual experiment, and one intervention claim it does not establish. Explain why changing an input to the fitted Python model measures the model's response, not necessarily the effect of changing that variable in the world. Claude can help calculate under an explicit model; you own the justification for applying that model.
