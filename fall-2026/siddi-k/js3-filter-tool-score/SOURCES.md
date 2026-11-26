# SOURCES

## Started from

- **My JS1** (`../js1-contract-and-watch/`):
  - the Jordan Lee persona, copied unchanged;
  - the title exclusions, seniority words, years regex and skill vocab;
  - the text preparation (`js3/textprep.py` is JS1's file plus a plain-text path);
  - the judge prompts `judge_v1` and `judge_v2` (byte-identical) and their output validator;
  - the 10 held-out hand labels from 2026-10-31, with their text taken from JS1's committed board;
  - the isolated `claude` invocation.
- **My JS2** (`../js2-loop-tools-diff/`): the three boards; the allow-listed, no-redirect GET (`js3/http.py` copied); the policy pattern; the error and empty-board rules.
- **The instructor's Lectern** (`fall-2026/nik-bear-brown/lectern/keywords.json`): only the idea that a filter is a file in which every added, cut and rejected word is recorded and measured. No code or word list was taken.
- **Public APIs:** the three hosts above, probed and collected on 2026-11-25/26.
- **MCP specification:** copies saved on 2026-11-18 for Make-up 1:
  - 2025-11-25 schema: `ToolAnnotations` are hints; tool errors go in the result with `isError`;
  - 2026-07-28 stdio page: probe with `server/discover` and fall back on error;
  - 2026-07-28 discover page: `serverInfo` is self-reported.
  These are cited in TOOL-SERVER.md and not copied here.
- **The other tool server:** the course's `lessons/08-mcp-from-scratch/code/main.py` at commit `a8629ce1`, sha256 `948337af…1769`. It is run from git and checked by hash; it is not copied into this folder.
- **Python 3.13 standard library; Claude Code CLI 2.1.325**, with models `claude-sonnet-5-5` and `claude-haiku-5-5`.

## What Siddi wrote or decided

- **The choice to have Claude draft FILTER.md and edit it.** In that draft, Siddi:
  - answered its three open questions: anywhere in the USA, a years cap of 4, a budget of 30;
  - approved the rest (`4e62099c`).
- **The 62 blind hand labels** (`4d633be9`).
- **Keeping those labels as-is** after Claude reported their conflict with LABELING.md (`labels/DECISION.md`).
- **Adopting v1.1 and rejecting v1.2 for now** (FILTER.md §E).
- **Still to come, in Siddi's own words:** the two trust decisions (TOOL-SERVER.md), FRICTIONAL.md, and signing or withholding the sign-off.

## What Claude contributed

- **The FILTER.md draft**, built from Siddi's JS1 decisions, which Siddi edited and approved.
- **All code:** `js3/` (collector, filter, location rule, evidence checker, judge port, tool server) and `tools/` (sheet, held-out set, experiments, audit, probes, tap, sessions).
- **All tests and mutants.**
- **All reports:** AUDIT.md, SHORTLIST.md, TOOL-SERVER.md (facts and tables), WHAT-MOVES-THE-SCORE.md, this file, and the README with its draft sign-off.
- **The JS3 prompts** `justify_v1` and `label_claims_v1`.
- **The v1.1 place list and the v1.2 blurb cut**, both hand-set from the collection, not from labels.

## Claude's mistakes, found and fixed

- **The request count.** Claude first told Siddi that full text needed "~30" requests. It needed 31 (and 32 by the time it ran, because Canva grew to 29 postings). Siddi chose to keep 30, so 2 Canva postings have no text.
- **A missing folder.** The transcript writers in `js3/mcp_server.py` and `tools/stdio_tap.py` did not create their folder. The first course-server session failed because of it (`03-17-39Z`, kept). Fixed in `eb13b533`, before variant T ran.
- **A duplicate in H.** H holds one posting twice (Stripe 7392697), which Claude noticed only after the variants ran. It is scored once.
- **Estimated times that were wrong:**
  - the first saved labels said 23:05 ET (corrected to 22:25 before committing);
  - PLAN.md said 22:40 (it was committed at 22:15; correction note added);
  - FILTER.md, DECISION.md and the v1.1 note were corrected against commit times.
- **A loose count.** A first draft said v1 misplaced "about 100" postings. The exact count is 111.
