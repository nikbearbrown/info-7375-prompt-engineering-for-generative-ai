# PROJECT-BRIEF.md — agent-reliability-audit

## 1. What is it?

A command-line tool that measures whether an AI agent is *reliably* right,
not just right once — and whether it fails safely when one of its tools
returns bad data.

When done, it will exist as a Python CLI and library, `agent-reliability-audit`,
installable and runnable against any agent that exposes a simple
`run(task) -> output, tool_trace` interface. Its output is a Markdown report
showing two numbers most agent demos never show side by side: **pass@k**
(did the agent succeed at least once across k attempts) and **pass^k** (did
it succeed *every* time) — plus a safe-degradation rate measured under
deliberately corrupted tool responses.

## 2. Why would anyone care?

Real alternatives I looked at: the public quickstart and evaluation
documentation for both LangChain's agent-eval tooling and OpenAI's Evals
repository report pass@1 or pass@k as their headline success metric. I did
not find either reporting pass^k by default, even though a recent (2026)
agent-evaluation methodology piece makes the gap between the two numbers
concrete: it reports a real example where pass@3 looks like 97% success
for an agent whose pass^3 (succeeding all three times) is only ~34% — a
63-point gap, and the honest consistency number is far less flattering
than the headline one. These two figures are quoted directly from the
source (see `SOURCES.md` for the exact citation and quoted figures); this
framing is not my own discovery, I found it while researching this idea.

This tool reports the less-flattering, more honest number, and pairs it
with a fault-injection test most public agent demos skip entirely: what
happens when a tool call returns malformed JSON, a stale cached value, or
times out? Does the agent notice and flag it, or does it silently pass bad
data downstream? It saves an engineer evaluating a candidate agent — their
own, or a third-party one — from being misled by a flattering pass@k number
into shipping something that only works most of the time.

## 3. Who opens it, and what do they do with it?

**Target role:** ML/AI engineer, specifically agent-evaluation or
ML-platform reliability work.
**Reader:** a hiring manager or engineer scanning my GitHub.

**First sixty seconds:** they land on the README and see a pre-run example
report — a real pass@k vs. pass^k gap, and a real example of the agent
correctly refusing to answer when its one tool returned truncated content —
already committed in the repo, with no setup required to see real output.
If they're interested, they clone it and point it at the included demo
agent to reproduce the same numbers themselves.

## 4. What does it prove about you?

- **Evaluation design** (course topic): choosing pass^k over pass@k as the
  honest reliability metric, and being able to justify why, with a cited
  source for the framing rather than an invented one.
- **Verification** (course topic): the fault-injection tests are themselves
  a verification harness — proving a specific claim (safe degradation under
  a corrupted tool response) rather than asserting it.
- **Agent loops / tool use** (course topic): building a genuinely pluggable
  interface requires understanding what a generic agent tool-call trace
  looks like, independent of any one framework's conventions.
- **Source grounding** (course topic): the demo agent's one tool fetches a
  real, public documentation page over HTTP and must cite the exact page it
  used — "safe degradation" has a checkable definition (refuse or flag,
  never fabricate an answer from a bad fetch).

**What a reviewer could fairly conclude, with evidence:** that I can design
and run a real evaluation harness against a real (not toy) tool-using
agent, and that I understand the difference between a flattering metric and
an honest one. The evidence is the committed example report itself, plus
the fault-injection test log.

## 5. What is in, what is out, what comes first?

**In:** one real tool — fetching documentation pages from
`docs.python.org` (standard library pages only: `functools`, `itertools`,
`pathlib`) over a real HTTP request — against a fixed set of 5–10 test
questions; the pass@k/pass^k audit; the fault-injection harness
(malformed JSON, stale cached value, timeout) wrapping that one real tool.

**Deliberately out:** multi-agent systems or agent-to-agent delegation
(scope is a single agent with tools); a polished web UI (CLI and Markdown
report only); broad documentation coverage or a general-purpose
doc-search product — the demo agent stays intentionally small, because the
audit harness is the point, not the assistant.

**First thing that will run:** the demo agent answering one fixed question
against one real `docs.python.org` page, run k=5 times with no fault
injection yet, producing a real pass@k/pass^k table. Someone will know it
ran because the report is committed in `reports/` with a timestamp and the
exact command used to produce it.

## 6. What could sink it?

The hardest part is making the agent interface genuinely pluggable rather
than secretly hardcoded to my one demo agent — that's real interface-design
work, not just scripting. If I run out of time, the honest fallback is to
ship it working against the demo agent only, and explicitly label the
"works against any agent" claim as **will** (a named next step in the
exists-today/will-exist split below), not **does**.

A second, smaller risk: `docs.python.org`'s page structure could change
between when I write the fetch logic and when I run the final demo,
breaking the "real tool" fetch. Mitigation: pin the fetch to a small, fixed
set of stable standard-library pages rather than anything likely to change.

## 7. Why this project?

Mostly new learning, with one piece I already have real evidence for.

**New to me:** designing a fault-injection harness, and formalizing pass@k
vs. pass^k as a metric pair — I have not built either of these before.

**Something I already have evidence for:** tool-contract thinking and
source-grounded system design. In my Reallocation Engine recipe (a real,
open pull request against `nikbearbrown/the-reallocation-engine`), I ran a
deliberate adversarial break-attempt against a scoring function, found a
real flaw it had (a company with zero approved visa petitions scoring
above a company with over 12,000), and documented three attempted fixes —
two that failed and one that worked, each backed by real measured numbers.
This project applies that same "try to break it, measure what actually
happens" instinct to a different kind of system: a tool-using agent instead
of a scoring function.

---

## Exists today
- This brief.
- The real-world precedent for the core metric (pass@k vs. pass^k),
  sourced and cited in `SOURCES.md`.
- The decision to use `docs.python.org` as the real, public tool-fetch
  target, scoped to three standard-library pages.

## Will exist
- `auditor/runner.py` — runs a task k times against a pluggable agent
  interface.
- `auditor/metrics.py` — pass@k / pass^k computation.
- `auditor/fault_injection.py` — malformed JSON / stale value / timeout
  injection, wrapping the real `docs.python.org` fetch tool.
- `auditor/report.py` — Markdown report generator.
- `examples/demo_agent.py` — a small reference agent with one real,
  source-grounded tool (fetches and cites `docs.python.org` pages).
- `reports/example-run.md` — a real, committed report from an actual run.
- `tests/` — tests for the metrics logic itself, run against synthetic
  pass/fail sequences (not against the live agent, so they stay fast and
  deterministic).
