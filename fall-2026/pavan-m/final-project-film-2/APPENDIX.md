# APPENDIX — Cite-the-Line: methods and evaluation in detail

The film keeps the "how" short. This appendix holds the detail. **Nothing here is built yet; everything is a plan, written in "will."**

## A. What it is
A command-line tool that reads logs from a failing backend service, proposes a root cause from a fixed list, and cites the exact log lines that support it, or declines and hands the case to a person. Target reader: a hiring manager or senior engineer for backend roles.

## B. Related work (what others did, and what they got)
| Work | What it does | What they report | Why mine differs |
|---|---|---|---|
| RCACopilot (Chen et al., Microsoft Research, arXiv:2305.15778) | Collects diagnostic data with incident "handlers", then an LLM predicts and explains a root cause category | RCA accuracy up to 0.766 on a year of real Microsoft incidents | Their data is internal; an outsider cannot re-run the score. Mine publishes incidents, answers, and errors |
| Datadog Bits AI SRE | Investigates alerts inside Datadog, forms and tests hypotheses on telemetry, can mark an investigation inconclusive | Vendor-reported results | Runs inside a paid platform on each customer's own data. Mine runs on a laptop on plain log files |
| Pasting logs into a chat assistant | Free-form answer | Not measured | No check that quoted lines exist; no score |

## C. Methods
**C1. Data (no private data).** A small FastAPI service with a Postgres database, run with Docker Compose. Faults are injected on purpose, and each injection produces real logs with a known cause:

| Cause category | How it will be injected |
|---|---|
| `db_slow` | pause Postgres or force slow queries so requests time out (first incident to build) |
| `bad_config` | wrong database host or credential in an environment variable after a "deploy" |
| `dependency_failure` | an upstream HTTP dependency returns 500s |
| `resource_exhaustion` | exhaust the connection pool or memory |
| `insufficient_evidence` | logs that do not identify a cause (no-answer cases) |

About ten incidents in total, including hard ones where the loudest error is not the real cause (for example, a slow database surfacing as upstream API errors).

**C2. The agent loop.** For each incident: observe (read its log file, numbered lines) → decide (Claude Code, headless, answers under the prompt contract) → check (the checker) → record (save the raw answer and verdict, dated) → next incident → stop.

**C3. Prompt contract.** Output must be JSON: `{"cause": <one category above>, "lines": [line numbers], "reason": "<one sentence>"}`. Anything else breaks the contract.

**C4. Tools and their limits.** Read access to the incident's log file only. No shell commands, no network, no writes outside the results folder. It never restarts, rolls back, or changes any system.

**C5. Stop conditions (rules, not the model's say-so).** Three runs per incident; at most one retry when an answer breaks the contract; the loop ends when every incident has its runs.

**C6. Human gate.** Any answer of `insufficient_evidence`, any contract failure after the retry, and any answer the checker rejects goes to a review queue for an engineer to decide. The tool never acts on its own diagnosis.

**C7. Resources.** Claude Code through a university seat (no paid API credits); a personal laptop for compute; Python and Docker, already in use. No new accounts or private data.

**C8. Build order.** (1) service + the first `db_slow` incident end to end, committed with its log, raw diagnosis and verdict; (2) the checker; (3) the loop with stop rules and the review queue; (4) the remaining incidents; (5) the keyword baseline; (6) the evaluation report.

## D. Evaluation
**D1. Checks per run.**
1. *Grounding:* every cited line number exists in the log. One invented line fails the run.
2. *Accuracy:* the cause matches the incident's known category.
3. *Abstention:* on no-answer cases, the answer is `insufficient_evidence`.

**D2. Consistency.** Each incident runs three times; the report shows how often the answer holds (3/3, 2/3, …).

**D3. Baseline.** A keyword script (for example, "timeout" → `db_slow`) scored on the same incidents with the same checks.

**D4. What result means it worked, or didn't.**
- It worked if: no run cites a line that does not exist, it beats the keyword baseline on accuracy (most of all on the hard cases), and it declines on the no-answer cases rather than guessing.
- It didn't work if: it invents citations, or does no better than the keyword script. In that case the report will say either the tool failed or the test set was too easy, and publish the numbers either way.

**D5. Limits of the evidence.** About ten incidents that I wrote, on one small service. Results would not show it works on real production logs or matches commercial tools.

## E. Risks
The main risk is a test set that is too easy because I write it. Mitigation: hard cases, no-answer cases, and the keyword baseline, which exposes an easy set.
