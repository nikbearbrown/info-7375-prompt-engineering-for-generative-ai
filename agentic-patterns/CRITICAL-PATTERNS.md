# INFO 7375 Prompt Engineering: critical agentic patterns on one page

**Status: DRAFT, 2026-11-18, for TA review. The instructor has not signed it off.** Condensed by Claude from the instructor's agentic best-practices collection (48 practices, the 20 pattern decks in this folder, 85 loops). The decks are listed in the [README](README.md). The course chapters name almost none of these patterns (only ReAct, in passing); the sources are listed under each section.

**Executive summary.** Five practices hold under every pattern: write a testable handoff, decide what the agent does and what a person keeps, check the world rather than the report, prove the check can fail, and let "cannot verify" be an answer. Then come the three classes of patterns (the [three-classes deck](three-classes.html) defines them with real examples). **Workflows** fix the steps in code. **Reasoning patterns** set how a model orders its own steps. **Loop patterns** repeat a step until a real check passes. Start with the simplest design that works (one model call, then a workflow, then an agent) and add autonomy only when the task needs it.

## 1. Five practices every pattern rests on

These are the only five of the 48 practices that all five of the instructor's books state.

| Practice | In one line |
|---|---|
| **A testable handoff for every step** | Before a step runs, write a condition a stranger could check: what is passed on, and why it can be trusted. |
| **Decide the split** | Task by task, decide what the agent does, what a person supervises and what a person keeps, and where the gate sits. |
| **Check the world, not the report** | "Done" is the agent asking to stop. Confirm the result in the real file, page or system; "finished" is not "succeeded". |
| **Prove the check can fail** | Run every check on a known-bad case first. A check that can't fail proves nothing. |
| **"Cannot verify" is an answer** | Leave gaps blank. Never fill one with a plausible value; "not found" is not "not true". |

Go to: [the exam cheat sheet](https://github.com/nikbearbrown/interview-bank/blob/main/info-7375-prompt-engineering-for-generative-ai/CHEAT-SHEET.md), items 6, 10, 49 and 50; [chapter 11](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/chapters/11-tool-use-and-verification.md), [chapter 13](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/chapters/13-evaluation-and-approval-gates.md).

## 2. Workflow patterns: the code picks the steps

From Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (December 2024). In each one, code decides the order; a model does some of the steps. That's what makes them workflows: a workflow fixes who picks the next step in code, while an agent lets the model pick ([chapter 3](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/chapters/03-chat-assistant-agent.md)).

Decks: [full](full-decks/) and [worked examples](worked-examples/), Workflow family.

| Pattern | What it does | Reach for it when |
|---|---|---|
| **Prompt chaining** | Fixed steps; each step's output feeds the next, with checks between | The task splits cleanly into known steps |
| **Routing** | Sort the input, then send it down a specialized path | Different kinds of input need different handling |
| **Parallelization** | Run pieces at once (split the work, or ask several times and vote) | Pieces are independent, or one answer isn't trustworthy enough |
| **Orchestrator-workers** | One model breaks the task up and hands the pieces to workers, then combines the results | You can't know the subtasks in advance |
| **Evaluator-optimizer** | One model drafts, another judges against criteria, repeat | There's a clear standard to judge against |

## 3. Reasoning patterns: how the model orders its own steps

From *Design of Agentic Systems*, chapter 3, "Five Patterns, Five Trade-offs". Each has a typical way of failing.

Decks: [full](full-decks/) and [worked examples](worked-examples/), Reasoning family.

| Pattern | How it runs | Typical failure |
|---|---|---|
| **ReAct** | Think → act with a tool → observe → think again | The context fills up on long tasks |
| **Plan-and-Execute** | Write the whole plan, then carry it out | Keeps following a plan that has gone stale |
| **ReWOO** | Plan every tool call first, then run them all at once | Can't change course when a result surprises it |
| **Reflection** | Do the work, grade it against a rubric, revise | Grades itself too kindly, unless the rubric can be checked from outside |
| **Tree-of-Thoughts** | Try several lines of reasoning, score them, prune | Cost grows fast with every branch |

## 4. Loop patterns: repeat until a real check passes

From the instructor's grouping of the 85 loops in the [Loop Library](https://signals.forwardfuture.com/loop-library/) (Forward Future, MIT). A loop is a prompt, plus a real check, plus a stop rule.

Decks: [full](full-decks/) and [worked examples](worked-examples/), Loop checks family.

| Pattern | Shape | Fails when |
|---|---|---|
| **Measure, change one thing** | Baseline → one change → re-measure → keep only if better | The benchmark shifts between runs |
| **Burn down a worklist** | Scan → fix the top item → rerun the same scan | The agent "wins" by hiding findings or narrowing the scan |
| **Change with proof** | Reproduce the problem → smallest change → attach proof | The only proof is the agent saying so |
| **Maker is not the checker** | One builds, a different reviewer checks against fixed criteria | The reviewer is the same model in a different prompt |
| **Evidence ledger** | Every claim gets evidence for and against, then a verdict | Missing evidence is treated as disproof |
| **Replay until clean** | Rerun from a truly clean start until it passes | Leftover state makes it look fine |
| **Plan before building** | Question the plan until independent readers would build the same thing | Requirements are invented to force agreement |
| **Standing watch** | On a schedule: look, do one bounded thing or nothing, leave a record | It has more authority than intended |
| **Audit, gate and handoff** | Inspect read-only, give a verdict with evidence, hand control to a person | A "go" is read as permission to act |

(The tenth group in the collection, controlled experiments, is for studying agents, not for doing work.)

## The ten-second version

- Simplest design first: one call, then a workflow, then an agent.
- Workflow = code picks the steps. Agent = the model picks the steps.
- Every loop needs a check that can fail, run by someone other than the maker.
- "Done" is a claim. Check the real result, and let "cannot verify" stand.
- Put the person in the plan: approval before anything that can't be undone.
