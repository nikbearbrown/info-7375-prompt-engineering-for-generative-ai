# INFO 7375 — Prompt Engineering for Generative AI

**Nik Bear Brown · Northeastern University · Claude and Python only**

**Access comes first:** INFO 7375 students have Claude Code through Northeastern, and every exercise assumes that access. Start with [Northeastern's Claude portal](https://claude.northeastern.edu/) for university sign-in and support. Public readers of this repository need their own Claude Code-enabled account.

Northeastern's portal describes enterprise Claude access for active students, faculty, and staff through university SSO, with advanced features and generous usage allowances. It provides onboarding, training, IT support, and responsible-use guidance. It says institutional inputs are not used to train Anthropic models and directs API-access questions to IT. This course's Claude Code entitlement is the instructor-provided assumption; the portal is the university's general Claude access guide. See the [short NEU access summary](docs/neu-claude-access.md).

**Claude Code account access and API credits are distinct.** Use Claude Code throughout the exercises. The Python reference programs run offline first so you can inspect the mechanics; direct Claude API calls are explicit, optional extensions that may consume separately provisioned credits. An API key is not required to start the course.

Build the mechanism before relying on the tool. This 15-week course turns prompting, retrieval, tool use, memory, evaluation, and supervision into inspectable Python programs. Each week follows **Predict → Build It → Use It → Ship It → Verify**. The reference implementations are small enough to trace by hand; students build their own versions, explain failure cases, and then apply the mechanism with Claude.

Claude chat, Claude Code, Claude Cowork, and the Claude Messages API are the course's model interfaces. All executable course reference implementations are Python. Markdown and JSON are artifact formats; YAML configures CI. No frontend build or orchestration framework is required for the book's Python lessons. NEU course prerequisites include an optional Brutalist video-production tutorial using an external media toolchain.

## Start here

Read the [adapted syllabus](SYLLABUS.md), [setup guide](docs/setup.md), and [assessment guide](ASSESSMENT.md). A strong programming background and independent research are prerequisites.

From this repository root, with Python 3.11 or newer:

```bash
python3 scripts/validate_course.py
python3 scripts/course.py list
python3 scripts/course.py run 1
python3 scripts/course.py test 1
```

Reference Python demos need no API key, no packages, and no network. The full learning exercises assume Claude Code access. The validation command runs every reference demo and the deterministic tests. Offline fixtures are labeled and do not simulate evidence of live Claude performance. Optional direct API work is documented in setup.

## NEU course prerequisites

**For students taking INFO 7375 at Northeastern only:** read the [AI policy](prerequisites/ai-policy.md) and [Relative Quartile rubric (20/100)](prerequisites/relative-quartile.md) in the [course prerequisites](prerequisites/README.md). [Brutalist video setup](prerequisites/brutalist-video.md) is optional: explainer quality matters, not the tool used. These course logistics are outside the book's numbered lessons and are not required for independent readers.

Course-related films and their source records belong in [youtube/](youtube/README.md). A film in this folder is not necessarily published.

## The 15-week build sequence

| Week | Lesson | Shipped artifact |
|---|---|---|
| 1 | [Randomness and first prompts](lessons/01-randomness-and-first-prompts/docs/en.md) | sampling report |
| 2 | [Prompt contracts and evaluation](lessons/02-prompt-contracts-and-evaluation/docs/en.md) | prompt experiment |
| 3 | [Chat, assistant, and agent](lessons/03-chat-assistant-agent/docs/en.md) | action surface comparison |
| 4 | [The agent loop](lessons/04-the-agent-loop/docs/en.md) | agent trace |
| 5 | [Tools, permissions, and boundaries](lessons/05-tools-and-permissions/docs/en.md) | permission policy |
| 6 | [Claude Code and evidence-based diff review](lessons/06-claude-code-and-diff-review/docs/en.md) | review packet |
| 7 | [Context retrieval and Claude Cowork](lessons/07-context-retrieval-and-cowork/docs/en.md) | source grounded task packet |
| 8 | [MCP from scratch](lessons/08-mcp-from-scratch/docs/en.md) | mcp evaluation and progress reel |
| 9 | [Training mechanics and Claude configuration](lessons/09-training-and-configuration/docs/en.md) | training versus context report |
| 10 | [Planning before acting](lessons/10-planning-before-acting/docs/en.md) | reviewed plan |
| 11 | [Claude tool use and verification](lessons/11-tool-use-and-verification/docs/en.md) | tool evidence matrix |
| 12 | [Memory and multiple agents](lessons/12-memory-and-multiple-agents/docs/en.md) | shared memory premortem |
| 13 | [Evaluation and human approval gates](lessons/13-evaluation-and-approval-gates/docs/en.md) | approval gate design |
| 14 | [Team governance and applied ethics](lessons/14-team-governance-and-ethics/docs/en.md) | team ai use register |
| 15 | [Supervised agentic capstone](lessons/15-supervised-capstone/docs/en.md) | capstone packet |

Theory is prepared through short instructor videos and readings; class time is for building, inspecting, breaking, and explaining. Lesson exercises and quizzes are ungraded **Assessments**. Graded **Assignments** are due every 10 days: 60 implementation + 10 Frictional + 10 GitHub version posting + 20 Relative Quartile = 100 points. Explainer videos (including Progress Reels) are optional evidence of quality within Relative Quartile. See the [submission guide](ASSESSMENT.md). The complete weekly mapping appears in the syllabus.

## What from scratch means here

Implement probability normalization, prompt checks, a bounded controller, path policy, lexical vector retrieval, a small MCP protocol subset, a gradient update, dependency ordering, Claude tool dispatch, versioned memory, and proposal-bound approvals. Derive and test these mechanisms before using their managed counterparts. This course does not recreate Claude's proprietary model or train its weights.

Weeks 3–8 use controlled repositories and files. Weeks 10–15 transfer the mechanisms to a real, approved context with named owners, shared-state failures, evidence, and human decisions. The capstone ships the ten-artifact packet in [ASSESSMENT.md](ASSESSMENT.md).

## Repository map

- lessons/: 15 weekly lessons, each with explanation, runnable reference, six tests, six-question quiz, and artifact brief.
- coursekit/: explicit opt-in Claude Messages transport written with Python's standard library.
- scripts/: course navigator and validation.
- docs/: setup, sources, original syllabus, migration record, and unresolved instructor policy decisions.
- learning-artifacts/: ignored local student work, created by students as needed.
- prerequisites/: NEU-only course preparation, separate from the book's lessons.
- youtube/: course films, beat sheets, source records, and review notes; no automatic publication.

See [ATTRIBUTION.md](ATTRIBUTION.md) for the inherited MIT provenance and [MIGRATION.md](MIGRATION.md) for the recoverable original archive. This is an independent university course adaptation, not an Anthropic certification program.
