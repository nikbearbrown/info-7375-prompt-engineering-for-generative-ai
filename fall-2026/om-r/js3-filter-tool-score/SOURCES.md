# SOURCES.md: what I used, what I wrote, what Claude contributed

## Starting sources

- **Assignment:** "Job-Search Agent 3" (INFO 7375, Chapters 7–9). It covers
  a filter with stated rules and a reject audit, a tool exposed in MCP
  shape, and an experiment on what moves the score.
- **Job-Search Agent 1** (`fall-2026/om-r/js1-contract-and-watch/`). JS3
  reuses:
  - **the persona:** Priya Nair, `resume.json`, a fictional persona. The
    shortlist and the MCP server read it from JS1 (`$JS1_ROOT`); it is not
    copied.
  - **the rule-1 pattern this filter extends:** the 6 skill words, the
    "≥2 of 6" threshold, whole-word and case-insensitive matching, and
    quote windowing. It is ported from JS1's `agent/rule.py` into
    `js3/filter.py` rather than imported, because JS1 and JS2 both name
    their package `agent`. `tools/rule1_vs_js1.py` checks the port
    against JS1's own rule on all 1,332 postings: 22 vs 22, zero
    disagreements.
  - **the judgment conventions:** a pinned model, a strict validator that
    never repairs output, and no fallback model. JS3's `shortlist-v1`
    follows JS1's `judge-v1` here.
- **Job-Search Agent 2** (`fall-2026/om-r/js2-loop-tools-diff/`).
  `agent.loop` is imported **unchanged** for collection (`js3/collect.py`,
  `$JS2_ROOT`). JS3 sets only `root=` to this project, so JS2's WritePolicy
  confines the run's writes to this project's `evidence/`, `state/` and
  `logs/`. JS3 also follows JS2's conventions: the wrong-version tests,
  numbered `logs/`, FRICTIONAL.md, and the board-drift finding behind the
  evidence-commit exception.
- **Data:** the three public job-board APIs, reused from JS2 through its
  loop. They were fetched on 2026-11-21 (run `20261121T132140Z`, 1,332
  postings), and again on 2026-11-23 in the README's fresh-clone check
  (not used for any result).
  - Greenhouse, `gitlab`:
    `boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true`
  - Greenhouse, `stripe`:
    `boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
  - Lever, `palantir`: `api.lever.co/v0/postings/palantir?mode=json`
    (paginated)

  The raw responses for run `20261121T132140Z` are committed in
  `evidence/`, a deliberate exception (README.md).
- **The MCP specification, version 2025-06-18**, read directly from the
  published spec at modelcontextprotocol.io on 2026-11-22. It covers the
  stdio transport, the lifecycle, tools, and the error split. The newest
  version (2026-07-28) was read too, to establish why this server targets
  2025-06-18 (TOOL-SERVER.md section 1).
- **The reference filesystem MCP server**
  (`@modelcontextprotocol/server-filesystem`, version 2.4.0). For
  Evaluation 2, its real published source was read on `main` of
  `github.com/modelcontextprotocol/servers`, `src/filesystem`, together
  with the repo's security advisories page. It was read, not run. The
  files read and not read are listed in TOOL-SERVER.md section 6.
- **Libraries:** the Python 3.11 standard library, plus the Anthropic
  Python SDK `anthropic==0.39.0`. The SDK is used only by the shortlist and
  the MCP server's judgment call.

## Toolchain

Python 3.11 (tested on 3.11.15), standard library, and
`anthropic==0.39.0`. There is no `requirements.txt`. I checked this by
parsing every import in `js3/`, `tests/` and `tools/`.

The SDK is imported lazily inside `js3/shortlist.py:get_client()`, so every
offline step runs without it. The judgment model is pinned to
`claude-opus-5-5` at effort `medium`. This is the same toolchain stated in
README.md.

## What I wrote and decided

- **FILTER.md, in full, before any code existed:**
  - v1.0.0's three rules and the reasoning for each;
  - the two wrong versions the tests had to catch;
  - the evidence rules (supported / contradicted / insufficient);
  - the abstention rule.
- **The v1.1.0 amendment's scope and promotion criteria.** Claude drafted
  the amendment text from them.
- **All 90 reject-audit hand labels and reasons** (88 distinct postings),
  every one my own writing, with no AI drafting. A claude.ai chat helped
  only with the wording of the labeling rule itself (see "AI use
  disclosure" below).
- **The Group B sampling reduction:** 2 forced rule-2 rejects plus 38
  sampled from the 154 exactly-1-word postings, instead of all 156
  (FRICTIONAL.md, entry 4).
- **The Chapter 9 discipline:**
  - write the split rule first, with a new seed (7375), before rule 4
    existed;
  - design rule 4 on dev only;
  - lock it, then do a single guarded held-out read
    (`JS3_FINAL_HELDOUT=1`, logged in `heldout_access.log`).
- **The promotion decision and its framing.** Rule 4 was promoted on the
  false-positive-removal rate (dev 10/11, held-out 5/8), **not** on bucket
  precision. Held-out precision went from 0/8 to 0/3, which is structural:
  held-out had no true positives in the bucket to begin with.
- **The evidence-commit exception:** committing run `20261121T132140Z`'s
  raw evidence (`a1988cb`), so the audit, the experiment and the grounding
  checks rest on checkable text rather than a drifting live fetch.
- **The key-incident response:**
  - delete the leaked log rather than redact it;
  - rotate the key;
  - catch the stray bracket in the replacement key myself, by checking
    its prefix before retrying (TOOL-SERVER.md sections 4.3–4.4).
- **The runs that needed my API key:** logs 21 and 22 (shortlist) and logs
  29 and 30 (audited MCP sessions), run in my own terminal.
- **The sign-off** (`SIGNOFF.md`) **and the driver's-seat table.**

## What Claude contributed

**Claude Code** (Anthropic's CLI, model `claude-opus-5-5`) acted as a coding
and drafting assistant throughout. It did this in Claude Code sessions
separate from the claude.ai chat described below.

- **All code:**
  - `js3/`: filter, grounding, rule 4, filter v1.1.0, postings, collect,
    run_filter, reject_audit, experiment, shortlist, mcp_server,
    minischema;
  - `tests/`: all 91 tests and their constructed fixtures;
  - `tools/`: `rule1_vs_js1.py`, `dev_evidence.py`, `mcp_client.py`,
    `mcp_audit.py`.
- **The deliberately wrong code:** `js3/wrong_stub_filter.py`,
  `js3/wrong_stub_grounding.py` and `js3/wrong_stub_rule4.py`.
- **The MCP server, its test client and the audit wrapper**, including the
  wire-log cross-check.
- **Two find-and-fixes:**
  - **the `oneOf` schema gap.** Claude found it in self-evaluation and
    fixed it test-first (logs 27 and 28).
  - **the environment leak.** Claude's own audit hook logged the child
    process's environment, including my API key, into a local log.
    Claude spotted it before anything was staged, fixed the hook so it
    never records environments, and verified the fix with a fake secret
    (TOOL-SERVER.md section 4.3).
- **Drafts I directed and corrected:**
  - REJECT-AUDIT.md (structure, plus parsing my worksheets and checking
    every quote attributed to me against the committed text);
  - EXPERIMENT.md;
  - SHORTLIST.md;
  - TOOL-SERVER.md;
  - FRICTIONAL.md;
  - README.md and this file, apart from the sign-off and driver's-seat
    content;
  - the SIGNOFF-DRAFT.md skeleton.
- **Corrections Claude flagged against the record, which I accepted:**
  - my planned Case 2 framing in SHORTLIST.md: posting 8738179002's
    contradiction flag came from the "varying levels of experience"
    boilerplate, not the location sentence;
  - the "corrupted key copy" claim for log 21 in my sign-off: that was
    log 29;
  - its own errors, among them a claim total (37 → 38) and a test-count
    wording.
- **The runs it executed itself:**
  - every test run in `logs/`;
  - the live collection (2026-11-21);
  - the filter run and the rule-1 cross-check;
  - the reject-audit draws;
  - the split, the dev measurements, and the single held-out read;
  - the no-key MCP sessions (logs 25, 26, 26a);
  - the fresh-clone reproduction of every [offline] and [live] README
    command (2026-11-23).
- **Source reading:** the MCP spec pages and, through a fetch subagent,
  the filesystem server's source.
- **The git history and `js3-history.bundle`:** commits authored as me, at
  my direction.

**Claude as part of the agent:** the shortlist verdicts and claims, and
the MCP judge transcripts, are runtime output of `claude-opus-5-5`, called
through the API. They are labeled as judgment throughout, and every quote
is checked against the posting. They are never presented as fact or as my
authorship.

## AI use disclosure

Two different AI surfaces were used in this build, both Anthropic's Claude:

1. **Claude Code:** all code, tests and tools, plus document drafting and
   verification, as listed above.
2. **A claude.ai chat conversation.** I used it to plan and draft this
   submission's work throughout, separately from the Claude Code sessions
   that did the implementation. In the submitted text it contributed:
   - **the reject-audit labeling rule's wording.** It helped only with the
     labeling rule itself, not with any individual label or reason
     sentence. All 90 labels and reasons are my own writing, with no AI
     drafting. That help came from the claude.ai chat (as best I recall),
     not from the Claude Code session. That session never saw the
     worksheets until they arrived already judged; it then parsed them,
     checked my quotes, and drafted REJECT-AUDIT.md's structure.
   - **the sign-off's wording**, drafted from Claude Code's scaffold
     (SIGNOFF-DRAFT.md). The checks, limits and decision to sign are my
     own.

No AI tool beyond these two was used anywhere in this build. That includes
ChatGPT, which helped with JS1's sign-off but was not used here.
