# SOURCES — Job-Search Agent 3

Drafted by Claude Code from the committed records and my instructions;
reviewed and approved by Swathi, 2026-11-20.

## External sources actually used

### Job-board APIs (public GET, no login)
- **Greenhouse Job Board API**, boards `databricks` and `stripe`, with
  descriptions: `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true`
  (`job_filter.JS3_URLS`). The deliberately nonexistent board from JS2 is
  still requested and still returns 404.
- **Ashby public Job Board API**, board `plaid`:
  `https://api.ashbyhq.com/posting-api/job-board/plaid`.
- **Saved responses from my live runs:**
  - `runs/2026-11-17T21-47-06-167440-0500/` (`d4a3b94`), filtered and
    audited;
  - `runs/2026-11-19T17-31-47-142253-0500/` (`831d6af`), the held-out
    collection;
  - one Plaid response from the JS2 run `runs/2026-11-05T23-11-48-228373-0500/`,
    copied unchanged for the inherited tests (`97407ff`).

### Model Context Protocol specification (read 2026-11-20)
Cited with quotes in `tool/TOOL-SERVER.md` §2 and `tool/EVALUATION.md`.
- **Current revision 2026-07-28** (not implemented):
  - `https://modelcontextprotocol.io/specification/versioning` ("The current
    protocol version is 2026-07-28");
  - `https://modelcontextprotocol.io/specification/2026-07-28/changelog`
    (the handshake removed, `server/discover` added);
  - the 2026-07-28 stdio guidance on probing with `server/discover` and
    falling back for legacy servers, and its compatibility matrix, as
    quoted in `tool/TOOL-SERVER.md`.
- **Implemented revision 2025-11-25:**
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/transports`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/index`
  - `https://modelcontextprotocol.io/specification/2025-11-25/server/tools`
    (error handling quoted verbatim; checked before the tests and again on
    2026-11-20, `tool/EVALUATION.md` §1.1a)
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/ping`
- **JSON-RPC 2.0 error codes** (-32700, -32600 to -32603), as named in
  `tool/TOOL-SERVER.md` §2.

### The external server evaluated (`tool/EVALUATION.md` §2)
- **Package:** `@modelcontextprotocol/server-filesystem` 2.4.0, downloaded
  with `npm pack --ignore-scripts` into a throwaway directory and read, never
  installed or run. Tarball SHA-512 equal to the registry's `dist.integrity`.
  The throwaway directory was deleted afterwards.
- **npm registry metadata** (`npm view`: versions and publish times,
  `dist`, `engines`, dependencies, dist-tags; no `gitHead`), and the npm
  provenance attestation endpoint for 2.4.0.
- **Security advisory GHSA-7m4x-rv66-mxhh**, read through the repository
  advisory API and page:
  `https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-7m4x-rv66-mxhh`.
  The GitHub global advisory API and OSV returned 404; the npm bulk advisory
  endpoint returned nothing.
- **GitHub release notes** of `modelcontextprotocol/servers`, releases
  `v2.4.0` (ships filesystem 2.3.0) and `v2.5.0` (ships filesystem 2.4.0),
  through the GitHub releases API. GHSA-p9cv-8g75-4xcg and
  GHSA-rq2p-q7c4-6g27 were seen only as cited in those notes.

### Clients
- **Claude Code v2.1.308**, connected by me as an MCP client to my server on
  2026-11-20 at local scope, then unregistered. Its messages are in
  `tool/transcripts/2026-11-20T18-21-07-980276Z-9425.jsonl`.

## Persona and inherited components

- **Priya Nair is a fictional persona.** `persona/` was copied unchanged from
  JS2 (`97407ff`), which copied it from JS1. JS1's `CONTRACT.md` (copied
  here) records its origin: the Reallocation Engine's
  `search/examples/priya-nair/`. No real résumé is used anywhere.
- **From JS2, copied unchanged** from commit `91224bc` (JS3 commit
  `97407ff`): `loop.py`, `policy.py`, `parsers.py`, `rule.py`, `persona.py`,
  `GATE.md`, `CONTRACT.md`, `BOUNDARY-CASES.md`, `persona/`, and the tests
  `test_loop.py`, `test_policy.py`, `test_ashby_address.py`,
  `test_rule_cases.py` (48 of the 113 tests).
- **Changed after copying:** `parsers.py` gained an option to keep
  descriptions (`6e6b4bf`, tested by `tests/test_js3_sources.py`). `loop.py`
  and `policy.py` are unchanged.
- **From JS1:** my labeling rule, reused verbatim as `AUDIT-RULE.md`
  (`a285233`) from `js1-contract-and-watch/LABELING-RULE.md` at JS1 commit
  `ebcd515`. The JS1 title rule (`rule.py`) still runs inside the JS2 loop
  during a non-baseline collection.

## My decisions and contributions

- **The filter's rules:** I decided `FILTER.md`'s rules and every revision,
  decision and change-log entry, including the threshold decision (keep 5).
- **Approving each document.** I approved each document, with AI help
  drafting wording (see "What each AI tool contributed" below).
- **All hand judgments:** the 48 audit judgments, the Row 35 adjudication,
  the 20 held-out labels and the 21 shortlist labels, quotes and notes, with
  the AI involvement recorded below and in each file's `how_judged` or
  provenance section.
- **Approvals:** the test designs and the plans (`HELDOUT-PLAN.md`,
  `shortlist/SHORTLIST-PLAN.md`), the tool-server contract decisions and its
  amendment (rate limit, handshake cases, privacy).
- **The Claude Code session** as an MCP client, including switching to
  manual mode and approving the adversarial call (my testimony; permission
  prompts are not in the MCP transcript).
- **The version choice** for the Filesystem server (2.4.0) and the
  code-reading approach, and the decision not to upgrade Node.js or change my
  environment.
- **Both trust decisions** in `tool/EVALUATION.md` (§1.5, §2.6).
- **The sign-off and the friction log.** Claude Code drafted the factual
  lists in `SIGNOFF.md` (Checked, Not checked, Not claiming) and a list of
  FRICTIONAL candidates from the records. I wrote the driver's seat and the
  five `FRICTIONAL.md` entries, with ChatGPT reference drafts and wording
  assistance that I revised, reviewed and approved (see below), and I signed
  the sign-off.

## What each AI tool contributed

### ChatGPT
- Coordination across the assignment steps.
- **The audit draft for rows 5–48**, which I saw before reviewing those rows
  (`audit/HUMAN_AUDIT.csv` `how_judged`; `audit/AUDIT-REPORT.md` §F). Rows
  1–4 were judged before seeing it.
- **Held-out row 1:** I consulted it about the labeling format and the
  verdict before recording my verdict (`heldout/HELDOUT.csv`, row 1).
- CSV review.
- **R6 and R3 feedback** on my shortlist labels and notes
  (`shortlist/SHORTLIST.md`, "Labeling provenance").
- **Identified security advisory GHSA-7m4x-rv66-mxhh** against the
  age-based recommendation of 2.2.0.
- Prompt refinement.
- Wording assistance for my trust decisions.
- **Reference drafts and wording assistance for my driver's seat and my five
  `FRICTIONAL.md` entries**, which I revised, reviewed and approved.

### Claude Chat (claude.ai)
- An advisory role throughout, and methodological feedback.
- **Drafted most of the prompts I sent to Claude Code.** I reviewed them and
  sometimes revised them before sending.
- **Proposed methodology choices that I approved:**
  - per-group audit reporting instead of pooled rates;
  - the Row 35 adjudication approach;
  - the six adopted or rejected v1.1 proposals;
  - Option A for the "ideally" problem;
  - the fresh held-out collection with Groups A and B;
  - the shortlist claim structure and the first wording of the abstention
    rule;
  - the tool-server design: one read-only capability, the contract first,
    the 2025-11-25 choice, the rate limit and the handshake cases;
  - the code-reading approach for the Filesystem server.
- Phrasing my decisions in `FILTER.md` (its header) and discussing the
  v1.1 rule changes (`FILTER.md` change log, "Decisions discussed
  2026-11-18 (with Claude Chat and Claude Code)").
- **Rule-consistency checks:** it pointed out that my four R6 shortlist
  labels conflicted with the approved absence-of-evidence rule and the
  quote requirement; it also gave R3 and R6 note feedback
  (`shortlist/SHORTLIST.md`, "Labeling provenance").
- **The rejected age-based recommendation:** it first recommended
  Filesystem server 2.2.0 by release age, then independently checked the
  advisory and revised its recommendation (`tool/EVALUATION.md` §2.1).
- **Reviewed my driver's seat and `FRICTIONAL.md` entries** for factual
  consistency.

### Claude Code (desktop app, model `claude-opus-5-5`)
- **Implementation:** `job_filter.py`, `descriptions.py`, `collect.py`,
  `run_filter.py`, the `parsers.py` change, `make_audit_sample.py`,
  `make_heldout_sample.py`, `measure_heldout.py`, `tool/server.py`,
  `tool/client.py`, `tool/privacy_scan.py`.
- **Test development**, before the code each time: `tests/test_job_filter.py`,
  `tests/test_descriptions.py`, `tests/test_js3_sources.py` and
  `tool/tests/test_server.py`, with the predictions in `TEST-PREDICTIONS.md`
  and `tool/TEST-PREDICTIONS.md`.
- **Execution:** the live collections, the filter runs, the sample draws, the
  held-out measurement, the test runs, the scripted client run, and the
  download and SHA-512 check of the Filesystem package.
- **Documentation drafts** from my decisions: `audit/AUDIT-REPORT.md`,
  `audit/ADJUDICATION.md` (my decision, its record), `HELDOUT-PLAN.md`,
  `heldout/EXPERIMENT-REPORT.md` (except my Decision),
  `shortlist/SHORTLIST-PLAN.md`, `shortlist/SHORTLIST.md`,
  `tool/TOOL-SERVER.md`, `tool/EVALUATION.md` (except my trust decisions),
  the corpus scans in the audit report, and this file and `README.md`.
- **Validation:** checking my CSVs and labels without changing them,
  protected-file hashes, the course validator, and the recomputation check
  on 2026-11-20.
- **Transcript inspection** of the Claude Code session, and the **privacy
  checks** on every transcript and run output before it was committed.
- **The code-reading evaluation** of the Filesystem server
  (`tool/EVALUATION.md` §2), with file and line citations.
