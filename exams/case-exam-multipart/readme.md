# INFO 7375 case exam, multi-part version: six cases, ten statements each

**Status: DRAFT, written 2026-11-09.** Author-written for Bear to review; not yet read by the instructor or the TAs. The older one-flaw cases in `../case-exam/` are untouched.

## Executive summary

**What this is.** Six case studies. Each case gives one scenario and an agent's confident run record, then ten true-or-false statements worth 1 point each. Every case touches **all six parts** of the course (the cheat sheet's Parts A to F), some statements are true and some are false, and no statement depends on the book's wording. One case is therefore not one flaw: it asks about a few different things.

**Draft exam shape (assumed total of 100).**

| Section | Items | Points | File |
|---|---|---:|---|
| Case studies | 6 cases, 10 true/false statements each | 60 | `case-1-...md` to `case-6-...md` |
| Multiple-answer | 8 questions, 5 statements each, drawn from the question bank | 40 | [multiple-answer-section.md](multiple-answer-section.md) |
| **Total** | | **100** | |

If the total is not 100, say so and I will rescale.

**Points by part.** Each part gets 10 points from the cases. The multiple-answer questions add 5 points to parts A, B, D and E and 10 to parts C and F (the agents and the "seeing, stopping and owning" parts get two questions each). Totals: A 15, B 15, C 20, D 15, E 15, F 20.

| Multiple-answer question | Part | Topic (bank id) | True statements |
|---|---|---|---:|
| M1 | A | model, weights, training vs inference (MA-found.3) | 1 |
| M2 | B | acceptance gate (MA-found.25) | 2 |
| M3 | C | agent loop: policy, controller, observation (MA-found.32) | 3 |
| M4 | C | agent vs workflow (MA-found.33) | 2 |
| M5 | D | MCP server vs client; interoperability vs authorization (MA-found.36) | 3 |
| M6 | E | prompt vs retrieval vs fine-tuning (MA-ch09.6) | 2 |
| M7 | F | the trace (MA-ch04.5) | 3 |
| M8 | F | budget units: turns vs tool calls (MA-ch04.19) | 4 |

20 of the 40 multiple-answer statements are true.

**The six parts** (from the cheat sheet; the cases use these names only in the TA key):

| Part | Name |
|---|---|
| A | How a language model works |
| B | The gate and checking |
| C | Agents and verification |
| D | Retrieval, tools and MCP |
| E | Training and fine-tuning |
| F | Seeing, stopping and owning an agent's work |

**How to use it.** Print the STUDENT PAGE of each case and of the multiple-answer section alone. Give TAs the whole files. Score 1 point per statement, true or false on its own; there is no partial credit inside a statement.

**What changed from the older cases.** The old set has 16 cases, each with one planted flaw and four short-answer probes graded by a TA. These six are multiple-answer in form, so they grade in seconds, and each spreads its ten statements over every part.

## The six cases

| Case | Domain | Statements per part (A B C D E F) | True / false |
|---|---|---|---|
| [1 The refund assistant](case-1-the-refund-assistant.md) | customer support, refunds | 2 2 2 2 1 1 | 5 / 5 |
| [2 The grant-report drafter](case-2-the-grant-report-drafter.md) | nonprofit report drafting | 1 2 2 2 2 1 | 5 / 5 |
| [3 The facilities work-order agent](case-3-the-facilities-work-order-agent.md) | campus work orders | 1 1 2 2 2 2 | 4 / 6 |
| [4 The résumé sorter](case-4-the-resume-sorter.md) | recruiting | 2 1 1 2 2 2 | 5 / 5 |
| [5 The invoice processor](case-5-the-invoice-processor.md) | finance, invoices | 2 2 1 1 2 2 | 6 / 4 |
| [6 The course Q&A bot](case-6-the-course-qa-bot.md) | university Q&A | 2 2 2 1 1 2 | 5 / 5 |

**Balance across the 60 statements.** Ten statements per part. True per part: A 5, B 4, C 5, D 4, E 6, F 6. True per case: 5, 5, 4, 5, 6, 5 (30 of 60 true). Which parts get two statements rotates from case to case so no part is favored.

## What the cases test (from this session's class notes)

Every case mixes the ordinary concepts of the course with the ideas you asked to be on the exam:

| Idea | Where it appears |
|---|---|
| A prompt rule is a request, not a gate | cases 1, 3, 5, 6 |
| Self-report versus the trace; claim versus evidence | cases 1, 2, 3 |
| Independent check; a producer cannot vouch for itself | cases 1, 2, 3, 5, 6 |
| Validation (shape) versus verification (substance); fluency trap | cases 1, 5 |
| Cost versus risk; approval for irreversible actions | cases 1, 5 |
| Capability is not authority; need to know; host decides | cases 3, 4, 5 |
| Activity versus progress; latency; what is observable | case 3 |
| Provenance | case 2 |
| Sign-off says what was checked and what was not | cases 4, 6 |
| Held-out set; leakage; proxy metrics | cases 2, 4, 6 |
| Workflow versus agent; stop condition versus finished task | cases 2, 3, 4 |
| Retrieval versus fine-tuning; what changes weights | cases 1, 2, 3, 4, 5, 6 |
| Prompt injection; MCP is not trust | cases 6, 2 |

## Caveats

- **Author-written, not run.** The agent outputs are written for illustration. None is a sampled run of any model.
- **One-sided keys are a risk.** Statements are written to be true or false from the scenario facts plus general course concepts. A statement you think is wrong is a bug in the case: report it.
- **A blind check by an AI reader** was run on the student pages without the keys: its 60 answers matched the keys, and it flagged nine unclear spots, all fixed (see `blind-check.md`). It is the same kind of model that wrote the cases, so it shares some blind spots. It checks clarity, not truth; a TA read is still needed.
- **Scoring rule** (1 point per statement) follows the multiple-answer set. The instructor owns the rule.
- **Instruction files, sandboxes and the Claude Code workflow** are covered in the cheat sheet but not given their own statement here, because the six parts have no part for them. Say if a case should carry them.

## Open decisions for Bear

1. Is the total 100 points, with 40 from multiple-answer? (Assumed.)
2. Are the six parts the cheat sheet's A to F? (Assumed; this replaces the seven jargon sets you picked earlier.)
3. The eight multiple-answer questions are my picks from the bank (above). Swap any you do not want; the bank has 767 to choose from.
4. Retire the old 16 cases? They are left in place.
5. TA review of the keys before any use.
