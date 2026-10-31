# SOURCES.md: what I used, what I wrote, what Claude contributed

## Starting sources

- **Assignment:** "Job-Search Agent 1 — The Contract and the Watch",
  `assignments/assignment-js1-the-contract-and-the-watch.md` in the course
  repo.
- **Persona:** Priya Nair, from the Reallocation Engine's
  `search/examples/priya-nair/` (a fictional example persona). Rebuilt for
  this project as `resume.json`, with an `@example.com` email and a 555
  phone. RAG, PyTorch, LangChain, and vector databases were added to her
  skills so the persona includes the contract's 6 rule skills.
- **Data:** GitLab's public Greenhouse job board API
  (`boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true`), fetched
  2026-10-30. The raw responses are in `evidence/`.
- **Libraries:** Python 3.11 standard library; Anthropic Python SDK
  `anthropic==0.39.0`.

## Toolchain

Python 3.11 (tested on 3.11.15), standard library (`urllib`, `unittest`),
and `anthropic==0.39.0`, which uses `httpx` internally. There are no other
dependencies. The judgment model is pinned to `claude-opus-5-5`. This is the
same toolchain stated in README.md and CONTRACT.md.

## What I wrote and decided

- **CONTRACT.md**, before any code was written. That includes the
  relevance rule, the two wrong versions, and the dated failure case.
- **The hand labels.** All 20 Prompt Experiment labels (10 dev, 10
  held-out) are my own reading and judgment, written without AI
  assistance. The 5 Sampling Report labels and the labeling rule were
  composed in a chat conversation with Claude, which I used as a drafting
  and thinking tool. The judgment in them is mine. See FRICTIONAL.md for
  both notes.
- **Design decisions:**
  - approving the `?content=true` endpoint;
  - keeping the rule unchanged despite the "LLMs" gap;
  - pinning one model with no fallback;
  - tightening the justification grounding bar;
  - the Prompt Experiment's scope decision and its one-sentence revision;
  - choosing the action-surface posting;
  - the repo-local commit identity and real (not backdated) commit dates.
- **The runs that needed my API key or my chat account:** the compare run,
  the 20 sampling calls, the 40 experiment calls, the agent-fetch run, and
  the claude.ai paste.
- **The sign-off.** Its wording was drafted with ChatGPT's help. The checks,
  limits, and decision to sign are my own.
- **The driver's-seat table.**

## What Claude contributed

**Claude Code** (Anthropic's CLI, model `claude-opus-5-5`) acted as a coding
and drafting assistant throughout:

- **All code:** `agent/`, `scripts/`, and `tests/`, including the
  deliberately wrong stubs and the test-first wrong-version tests.
- **The runs it executed itself:** the test suites, the 2026-10-30 live
  baseline fetches, the seeded run, the dry check of the rule, and the
  action-surface file-read run. That run used a fresh Claude Code subagent;
  its tool list is self-reported.
- **Drafts I directed and edited:**
  - SAMPLING-REPORT.md, PROMPT-EXPERIMENT.md, and ACTION-SURFACE.md;
  - the FRICTIONAL.md entries, written in my voice from my instructions,
    some quoting my text directly;
  - this file and README.md, apart from the sign-off and the driver's-seat
    table;
  - the sign-off and driver's-seat skeletons.
- **Verification:** checking claims against the files on disk, which led
  to several corrections recorded in FRICTIONAL.md and the reports.
- **The git history:** commits authored as me, at my direction.

**Claude as part of the agent:** the JUDGMENT verdicts are runtime output of
`claude-opus-5-5`, called through the API. They are labeled as judgment
throughout, never presented as fact or authorship.

## What ChatGPT contributed

- The wording of the sign-off (my statement).
- **Not** the dev-set or held-out labels. An earlier note said ChatGPT
  helped with the dev labels; that was incorrect and has been corrected
  (FRICTIONAL.md, "CORRECTION").
