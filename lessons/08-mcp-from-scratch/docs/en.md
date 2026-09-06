# MCP from scratch

> Predict the result, build the mechanism, verify what it can actually establish.

**Type:** Build
**Assessments:** Ungraded practice; exercises and knowledge checks provide feedback, not points.
**Languages:** Python
**Prerequisites:** [Context retrieval and Claude Cowork](../../07-context-retrieval-and-cowork/docs/en.md)
**Time:** ~150 minutes, plus independent project work
**Week:** 8
**Reading alignment:** Claude Agentic AI Ch. 6

## Learning Objectives

- Explain the mechanism behind mcp from scratch.
- Implement the reference behavior with Python's standard library.
- Diagnose a boundary case using reproducible evidence.
- Distinguish a passing automated check from human judgment.
- Ship a reusable mcp evaluation and progress reel.

## The Problem

Two servers advertise the same task but one can write files. Evaluate implementation, data flow, provenance, and permission scope before connecting either.

## The Concept

MCP gives a host a protocol for discovering and invoking capabilities. Discovery does not establish trust. Our newline-delimited JSON-RPC server implements a deliberately small stdio teaching subset: initialization, initialized notification, tool listing, and a read-only lookup.

## Predict Before Running

**Access:** This exercise assumes Claude Code through NEU. Public readers need their own Claude Code-enabled account. See [NEU access](../../../docs/neu-claude-access.md). Direct API credits are not required for this exercise.

Read the six tests in [test_main.py](../code/tests/test_main.py) before the reference implementation. Write down which input should fail and why. Implement your first attempt in your own learning-artifacts folder; consult the reference only after you can explain the expected behavior.

## Build It

Handle initialize, wait for notifications/initialized, then serve tools/list and tools/call. Distinguish protocol errors from tool errors. Run the server with --stdio only when ready to connect a client; the default demo terminates offline.

Open [main.py](../code/main.py) and trace one successful case by hand. Mark the input boundary, transformation, and returned result. Then trace one failure from the tests. Change one input at a time so an observed difference has an identifiable cause.

From the repository root:

```bash
python3 lessons/08-mcp-from-scratch/code/main.py
python3 -m unittest discover -s lessons/08-mcp-from-scratch/code/tests -v
```

The demo runs offline. Any scripted responses are fixtures, not evidence that Claude generated or verified the result. Default commands neither read credentials nor make API requests.

## Use It

Start in Claude Code with the [week-specific working prompt](../outputs/claude-code-prompt.md). Use it to review your prediction, run your Python attempt, inspect failures, and develop the shipped artifact. The Python mechanism runs offline; your Claude Code conversation uses your account allowance. Any --live API extension is separate and explicit.

Compare the protocol transcript to the versioned MCP lifecycle specification. Evaluate one read-only and one write-capable candidate server using source inspection and a disposable fixture. Connection is an explicit classroom decision. The included subset is not a production or conformance-certified MCP implementation.

Consult [setup](../../../docs/setup.md) for optional live access and [primary references](../../../docs/references.md) for dated API and protocol documentation. Record the interface and actual model used; do not substitute a fabricated live transcript when offline.

## Interactive Lab

In pairs, have one person predict and the other modify a boundary input. Compare the returned value with your prediction before reading the test assertion. Swap roles and explain the first failure without asking Claude to repair it immediately.

## Practice Lab

Send tools/list before initialization, then call an unknown tool and an unknown record. Explain why those failures have different meanings.

Add at least two tests: a meaningful success outside the demo and a failure that would matter in your capstone. State what remains untested. Use Claude to critique your explanation, then verify its criticism against the code.

## Ship It

Ship initialization transcript, capability inventory, trust decision for both candidates, and, optionally, a Week 8 Progress Reel showing the Weeks 3–8 artifacts.

Use the [artifact brief](../outputs/artifact-brief.md). Keep learner work under learning-artifacts/week-08/. Cite Claude assistance and external sources, state your code contribution estimate, and identify the license and style guide.

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

- [Anthropic's MCP builder materials](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) — inspect the Python-oriented guidance and tool-design references after building the protocol subset.
- [MCP server evaluation guide](https://github.com/anthropics/skills/blob/main/skills/mcp-builder/reference/evaluation.md) — compare its emphasis on answerable tasks and verifiable results with your server assessment.

Use these as reading, not as instructions to install or execute an external skill. Identify one useful evaluation you can reproduce with the read-only fixture. Keep the versioned MCP specification as the protocol authority.

Primary-source links checked 2026-09-06. Compare the guidance with your completed build; account access remains Claude Code through NEU (or your own account for public readers).

## Conducting AI

Read [Tool Orchestration — Every Handoff Explicit](../../../docs/conducting-ai.md#explicit-handoffs). The chapter asks what changes when an output becomes the next component's trusted input.

Annotate one actual MCP lookup transcript in your evaluation: what the server returned, what the host is entitled to infer, and which fixture or source supports that inference. Include a well-formed response with an incorrect fixture value and show the source comparison that catches it. A successful JSON-RPC exchange establishes protocol behavior, not factual provenance. Record where an unsupported value must stop before Claude uses it in an answer.
