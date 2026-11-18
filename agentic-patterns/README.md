# Agentic patterns

**Start with [three-classes.html](three-classes.html): what an agentic pattern is, the agentic loop, and the three classes every pattern belongs to.** Reasoning: the model decides the next step. Workflow: code decides. Loop check: a check decides whether to go round again. The three classes are what you need to know first; the twenty detailed patterns below sit inside them, each as a full deck and a shorter worked-example deck, plus a one-page condensed list.

## Where everything is

| What | Where | Length |
|---|---|---|
| **Start here:** the three classes (reasoning, workflow, loop check), defined, with real examples | [three-classes.html](three-classes.html) | 17 slides |
| **Condensed:** every pattern on one page, plus the five practices they all rest on | [CRITICAL-PATTERNS.md](CRITICAL-PATTERNS.md) | One page |
| **Simpler decks:** one worked example per pattern (a concrete task, a bounded run, a check, a stop rule) | [worked-examples/](worked-examples/) | 10 slides each |
| **Full decks:** the pattern itself, how it fails, when to use it | [full-decks/](full-decks/) | 16 slides each |
| **Index:** all 40 decks on one page, paired | [index.html](index.html) | |

**How to open a deck.** The decks are single HTML files. GitHub shows their source code, not the slides, so download the file (or clone the repository) and open it in a browser. In a deck: ← → to move, N for speaker notes, G for all slides, F for full screen. Print to save every slide.

## The patterns

### Reasoning: how a model orders its own steps

Source: *Design of Agentic Systems*, chapter 3.

| Pattern | Full deck | Worked example |
|---|---|---|
| ReAct | [full deck](full-decks/react.html) | [Recover a retired ticket-export endpoint, follow pagination, and count open tickets](worked-examples/react-examples.html) |
| Plan-and-Execute | [full deck](full-decks/plan-and-execute.html) | [Reconcile a warehouse catalog against a counted-stock file](worked-examples/plan-and-execute-examples.html) |
| ReWOO | [full deck](full-decks/rewoo.html) | [Compare five room snapshots for an 18-person accessible workshop](worked-examples/rewoo-examples.html) |
| Reflection | [full deck](full-decks/reflection.html) | [Revise a workshop description against a fixed source card](worked-examples/reflection-examples.html) |
| Tree-of-Thoughts | [full deck](full-decks/tree-of-thoughts.html) | [Make 24 from the numbers 3, 3, 8 and 8](worked-examples/tree-of-thoughts-examples.html) |

### Workflow: code fixes the steps

Source: Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).

| Pattern | Full deck | Worked example |
|---|---|---|
| Prompt chaining | [full deck](full-decks/prompt-chaining.html) | [Turn three change records into two customer release notes](worked-examples/prompt-chaining-examples.html) |
| Routing | [full deck](full-decks/routing.html) | [Route a duplicate-charge question to a billing-only draft path](worked-examples/routing-examples.html) |
| Parallelization | [full deck](full-decks/parallelization.html) | [Check a volunteer field guide against three event facts](worked-examples/parallelization-examples.html) |
| Orchestrator-workers | [full deck](full-decks/orchestrator-workers.html) | [Find which documentation needs a pagination migration](worked-examples/orchestrator-workers-examples.html) |
| Evaluator-optimizer | [full deck](full-decks/evaluator-optimizer.html) | [Revise a CSV export guide against a fixed UI contract](worked-examples/evaluator-optimizer-examples.html) |

### Loop checks: repeat until a real check passes

Source: [Loop Library](https://signals.forwardfuture.com/loop-library/) (Forward Future, MIT), grouped by the instructor.

| Pattern | Full deck | Worked example |
|---|---|---|
| Burn down a worklist | [full deck](full-decks/burn-down-a-worklist.html) | [Repair three accessibility barriers in a demo ticket form](worked-examples/burn-down-a-worklist-examples.html) |
| Measure, change one thing | [full deck](full-decks/measure-change-one-thing.html) | [Reduce cold-load JavaScript without breaking the demo editor](worked-examples/measure-change-one-thing-examples.html) |
| Replay until clean | [full deck](full-decks/replay-until-clean.html) | [Make a README work from a truly fresh clone](worked-examples/replay-until-clean-examples.html) |
| Evidence ledger | [full deck](full-decks/evidence-ledger.html) | [Verify four claims in a fictional launch draft](worked-examples/evidence-ledger-examples.html) |
| Maker is not the checker | [full deck](full-decks/maker-is-not-the-checker.html) | [Review a shipping-fee function against an owner-written contract](worked-examples/maker-is-not-the-checker-examples.html) |
| Plan before building | [full deck](full-decks/plan-before-building.html) | [Turn a vague free-shipping request into a buildable spec](worked-examples/plan-before-building-examples.html) |
| Change with proof | [full deck](full-decks/change-with-proof.html) | [Fix a false next-page indicator at a pagination boundary](worked-examples/change-with-proof-examples.html) |
| Standing watch | [full deck](full-decks/standing-watch.html) | [Draft release notes only when a nightly check finds a change](worked-examples/standing-watch-examples.html) |
| Audit, gate and handoff | [full deck](full-decks/audit-gate-and-handoff.html) | [Return a release-readiness verdict without deploying](worked-examples/audit-gate-and-handoff-examples.html) |
| Controlled experiment | [full deck](full-decks/controlled-experiment.html) | [Replay a fixed-rule cooperate-or-defect game](worked-examples/controlled-experiment-examples.html) |

## Read this before using them

- **The worked examples are teaching fixtures.** Their inputs, traces and outputs are constructed, not results from an executed agent run. Each deck says so on every slide.
- **Practice numbers in the speaker notes** (for example "#16 Check the world") refer to the instructor's list of 48 agentic best practices, which isn't published here. The five that all of the instructor's books state are in [CRITICAL-PATTERNS.md](CRITICAL-PATTERNS.md).
- **Films on each pattern are planned.** Links will be added here when they are published.
