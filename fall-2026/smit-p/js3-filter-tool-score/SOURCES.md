# SOURCES

## Executive summary

This file says where each part of this assignment came from: what was reused, what Smit
decided, and what Claude (Claude Code, model Opus 5.5) produced. In short: Claude wrote all
the code, the tests, the prompts and the first drafts of every document. Smit chose the
filter rules, judged 71 postings and 18 claims by hand, and chose which rule changes went
into version 1.1.

## Used (not written for this assignment)

| Source | What was used |
|---|---|
| Job-Search Agent 1 (`fall-2026/smit-p/js1-contract-and-watch`, my earlier work) | the fictional persona résumé (copied unchanged into `persona/`), the 2-skill rule, the hand-labeling rule used as the audit yardstick |
| Job-Search Agent 2 (`fall-2026/smit-p/js2-loop-tools-diff`) | the board list (Figma on Greenhouse, Spotify on Lever, Linear on Ashby). No code copied; the collector here is new and smaller |
| *The Reallocation Engine* (github.com/nikbearbrown/the-reallocation-engine) | origin of the Aarav Patel persona (via Job-Search Agent 1) |
| Instructor's Lectern (`fall-2026/nik-bear-brown/lectern`) | the idea of a filter document whose added, cut and rejected rules are recorded and measured. No code used |
| Greenhouse, Lever, Ashby public job-board APIs | the postings, collected 2026-11-14 (`runs/live-20261114/manifest.json` lists the exact URLs) |
| Microsoft Learn MCP server, `https://learn.microsoft.com/api/mcp` | the second tool server evaluated (`TOOL-SERVER.md`) |
| Model Context Protocol message shapes (initialize, tools/list, tools/call, Streamable HTTP) | from Claude's knowledge of the published specification (modelcontextprotocol.io), checked against what Claude Code 2.1.323 and Microsoft's server actually sent and accepted. The specification was not re-read for this assignment |
| Clopper–Pearson exact binomial interval | standard method; implemented from its definition and checked against known values in a test |
| Python 3.12 standard library; Claude Code CLI 2.1.323 | toolchain |

## Decided and done by me (Smit P.)

- Every filter choice in FILTER.md v1.0: boards, role words, exclusions, skill threshold,
  abstention cases, the tool to offer, the score, and both wrong versions (2026-11-14,
  picked from options Claude offered).
- 71 hand verdicts for the reject audit, from fact cards (`audit/hand-verdicts.json`).
- 18 claim labels for the shortlist (`audit/shortlist-hand-labels.json`).
- Which measured changes became FILTER v1.1 (A, B, C) and the reason for C.
- Review and signature of the sign-off in README.md. **Not done yet.**
- The trust decisions on both tool servers. **Not done yet.**
- My own entries in FRICTIONAL.md. **Not done yet.**

## Contributed by Claude (Claude Code, Opus 5.5, session of 2026-11-14)

- All code in `src/` and `experiments/`, and all tests in `tests/`, including
  `tests/test_filter.py`, which was written from FILTER.md and committed before the filter
  code (`5466e3c1`).
- The write-up of FILTER.md from Smit's choices, and every detail marked
  `[defined by Claude]` in it (US markers, how years are found, rule order).
- Both Claude judge prompts in `prompts/` and the choice of the four one-change configurations.
- The audit sampling design (strata, seed, dev/held-out split) and the fact cards Smit judged from.
- The claim checker's rules in `src/shortlist.py`.
- A read-only TA-style review by a separate Claude agent (2026-11-14), and the fixes it led to (FRICTIONAL F18).
- Running the live collection, all tool-server sessions, and all 165 Claude judge calls.
- First drafts of README.md, AUDIT.md, SHORTLIST.md, TOOL-SERVER.md,
  WHAT-MOVES-THE-SCORE.md, this file, and the FRICTIONAL.md event log.
- The model answering inside the experiments was `claude-sonnet-5-5` (and `claude-haiku-5-5`
  for the setting change). Its replies are data (`experiments/results/*.jsonl`), not authorship.
