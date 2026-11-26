# SOURCES — Job-Search Agent 3

**Who did what, at a glance:**
- **Claude Code** (the agent in the Claude desktop app, Code tab; session of 2026-11-25) drafted
  almost all the code, tests, tools, and documents.
- **Aravind** made every decision marked [DECIDED], gave every hand verdict and hand label, named
  every false friend, confirmed every claim label, and ran the claude.ai and Claude Desktop sessions.
- Commit hashes point to the evidence. I remain responsible for all of it.

## Inherited (copied, not written for JS3)

| File | From | Changed? |
|---|---|---|
| `data/raw/…` | my JS2 run `20261110T225032086Z-post-patch-2` (`data/MANIFEST.json`) | no (SHA-256 checked by a test) |
| `persona/maya-sehgal.resume.json` | The Reallocation Engine example persona, via JS2 | no (SHA-256 in `persona/SOURCE.md`) |
| `persona/persona-prefs.json` | JS2 (my 2026-10-31 preferences) | **yes:** experience policy corrected 2026-11-25, after the audit (`f3cefa22`) |
| `src/text.mjs` | JS2 `src/text.mjs` | no, apart from a header comment |
| Filter rules inherited from JS1 | title list, junior terms, experience regex, veto phrases | revised in v1.1.0-a…e (FILTER.md §9) |

## Claude Code, file by file (drafted by Claude Code; decisions by Aravind)

| File(s) | Claude Code wrote | Aravind decided or changed |
|---|---|---|
| `FILTER.md` | the draft of every section, the [SUGGESTED] rules, the wrong versions W1–W12, and all CHANGELOG rows and measurements | accepted or edited each part at Checkpoint 1 (threshold 0.70 → 0.80, W13); every [DECIDED] amendment (shortlist definition, v1.1 evidence rules, TPM rule, persona correction, location field); every v1.1 change and its cited rows |
| `src/spec.mjs`, `normalize.mjs`, `filter.mjs`, `evidence.mjs`, `corpus.mjs`, `boilerplate.mjs` | all | the rules they implement |
| `src/stats.mjs`, `rng.mjs`, `csv.mjs`, `sheet.mjs` | all | — |
| `src/justify.mjs`, `src/judge.mjs` | all (validator, quote-source rule, filing guard, tool-less call) | the location-field rule; the filing guard (after Aravind's misfiling) |
| `test/*.test.mjs`, `testlib/helpers.mjs` | all tests. Fixtures are synthetic unless marked SNAPSHOT. | which wrong versions to catch (W13's exact cases are Aravind's) |
| `tools/run-filter.mjs`, `make-samples.mjs`, `judging-plan.mjs`, `audit-results.mjs`, `false-friends.mjs`, `known-limits.mjs`, `grep-sponsor.mjs` | all | sample sizes, strata, seeds, the judging plan, the recheck lists |
| `tools/judge-audit.mjs` | all (blind judging, recheck, label modes) | asked for it and specified it |
| `tools/justify-shortlist.mjs`, `import-manual.mjs`, `confirm-claims.mjs` | all | the manual-route fallback; `my-labels.json` content |
| `tools/eval-labels.mjs`, `tools/make-diffset.mjs`, `experiments/FILTER.exp1-threshold-0.70.md` | all; the threshold change was chosen and justified by Claude Code (`phase5/PLAN.md`) | approved Phase 5 scope |
| `prompts/justify.v1.md` | the prompt text | approved before any call |
| `mcp/server.mjs` | all (no MCP SDK) | read-only scope; the description fix |
| `audit/RESULTS.md`, `shortlist/SHORTLIST.md`, `evaluations/*.md`, `phase5/*.md`, `transcripts/README.md`, `README.md`, `SIGNOFF.md` (template) | drafts and generated text | the trust decisions, the false-friend naming, the relevance-vs-entailment cases, and the sign-off are Aravind's to confirm and sign |

## Aravind's own work (not drafted by Claude)

- **Audit:** 45 hand verdicts (`1c9ce17b`) and 14 rechecks with reasons (`c711833a`), using
  `tools/judge-audit.mjs`.
- **Labels:** 40 hand labels, dev and held-out (`6fc19f50`).
- **Claims:** confirmed labels for all 54 claims; 8 differ from Claude's (`shortlist/my-labels.json`).
- **Names and decisions:** the false friends, the location-field decision, and the persona
  correction.
- **Claude sessions:** the 7 claude.ai sessions (raw replies in
  `runs/claude/justify.v1-v1.1.0-e/manual/responses/`) and the Claude Desktop session (3 calls,
  screenshots `transcripts/screenshots/`).
- `FRICTIONAL.md` and the Not checked / Not claiming / signature parts of `SIGNOFF.md`: Aravind's. As both files state, **chat-Claude (claude.ai, Claude Opus 5.5) helped draft them** from Aravind's answers, and Aravind reviewed and edited the text.
- Diff-set labels: 12 blind labels (`5540e14b`).

## Claude responses used as data

| What | How obtained | Where |
|---|---|---|
| 7 shortlist justifications | **claude.ai web, incognito chat, Claude Opus 5.5 (self-reported), 2026-11-25**, pasted by Aravind. The intended `claude -p` path failed on the spend limit (`3caf2978`). | `runs/claude/justify.v1-v1.1.0-e/A*.json` (SHA-256 of prompt and reply, `manual_paste: true`) |
| Desktop answers to the 3 tool calls | Claude Desktop, 2026-11-25. **The prose is not used as evidence**; the server transcript is. | `transcripts/screenshots/` |

## External sources

- The reference Filesystem MCP server: `modelcontextprotocol/servers`, `src/filesystem`, v2.4.0, commit
  `c799c855` (2026-11-18). Read from source, not run (`evaluations/filesystem-server.md`).
- The MCP message shapes (JSON-RPC 2.0; `initialize` / `tools/list` / `tools/call`; protocol versions
  2024-11-05 to 2025-06-18) were written from Claude Code's knowledge of the published
  specification. The server was then checked against two real clients (`transcripts/`).
- Course text, Chapters 7–9; the assignment brief.
