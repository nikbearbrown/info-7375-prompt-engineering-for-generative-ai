# SOURCES — Job-Search Agent 2

## Executive summary

**What this is.** Everything this submission used, what I contributed myself, and exactly what Claude Code contributed. **Why it matters.** The course rule is that I name Claude's contribution and stay responsible for the result. **In short:** I made the decisions (the gate, the predictions, the floors, the review decision, the sign-off); Claude Code wrote the code, the tests and the documents against those decisions, and ran the commands.

## What I used

| Source | Used for |
|---|---|
| My JS1, `../js1-contract-and-watch/` (commits `ea020eb`…`25e3ab4`) | starting point. Ported from JavaScript to Python: the allow-listed fetch, atomic writes, seen-ids state, raw response + SHA-256, and the whole-word title rule (`src/rule.js` → `src/jsa/rule.py`). The fictional persona `persona/priya-nair.resume.json` is copied unchanged |
| Reallocation Engine, `scripts/ats/providers/` (greenhouse.mjs, ashby.mjs, _http.mjs), github.com/nikbearbrown/the-reallocation-engine | the provider pattern (endpoint per ATS, normalized posting). Not copied: JS2 keeps each posting's id and refuses malformed bodies |
| Lectern `fall-2026/nik-bear-brown/lectern/ATS.md` (verified 2026-09-26) | board slugs (`anthropic`, `hubspotjobs`, `notion`), the `hubspot`-is-empty trap, and the posting counts my floors cite |
| Course chapters 4 (agent loop), 5 (tools and permissions), 6 (Claude Code and diff review), and Chapter 1/2 on the gate | exits and "stopping is not success"; the path wrong versions (prefix, `normpath`, truthy approval, unresolved return); the review-packet chain |
| Greenhouse Job Board API `boards-api.greenhouse.io/v1/boards/<slug>/jobs`; Ashby `api.ashbyhq.com/posting-api/job-board/<name>` | the only two hosts called (public, unauthenticated) |
| Python 3.11 standard library docs (`pathlib.Path.resolve`, `is_relative_to`, `urllib.request`) | the implementation |

## What I wrote or decided

- **Every gate decision**, answering the question sheet: language, exits, budgets, who changes them, repeat rule, error policy, escalation (4b = A + B + C, my change), independent check, permission policy, approval, wrong versions, review defect. Verbatim in `notes/gate-answers-2026-11-10.md`.
- **My failure sentence and my own wrong version W9** (a failed board's seen-ids wiped).
- Accepting the 16 boundary predictions before any test ran (CP2).
- Ran the review commands myself and **accepted** the patch (2026-11-10, `REVIEW-PACKET.md`).
- Ran `approve` on the real run myself (`runs/2026-11-11T00-24-30Z-real/approval.json`).
- Signed the sign-off (2026-11-10).
- Approved the checker floors in `config/expected-boards.json` (2026-11-10).
- Reviewed and edited `FRICTIONAL.md` myself (2026-11-10).

## What Claude Code contributed (Claude Opus 5.5, in my Claude Code session, 2026-11-05 and 2026-11-10)

- `notes/GATE-QUESTIONS.md` (2026-11-05): the question sheet with ★ recommendations, which I answered.
- `GATE.md`: written from my answers, with 6 edits listed at its end.
- `BOUNDARY-TESTS.md` predictions (accepted by me); all of `src/`, `checker/`, `tests/`, `scripts/`, `agent.py`, the configs, and the replay files.
- The floors in `config/expected-boards.json` are **proposals** from named sources, pending my approval.
- Ran every command and live run shown, and caught its own defects:
  - three test failures on the first full run, fixed before CP3;
  - the W6 `never_attempted` bug;
  - the checker's `/var` vs `/private/var` path guard;
  - a self-referential independence test.
- Found that `greenhouse/hubspot` now returns 404, probed for a live empty board, and proposed the labelled seeded replay.
- The review packet:
  - wrote the B8/B8b tests before the patch;
  - wrote the patch to `policy._resolve`;
  - collected before/after evidence;
  - wrote and ran the probe that shows the remaining escape.
- Drafted README, REVIEW-PACKET, SOURCES and FRICTIONAL from the session record.
- Not used: no Claude model is called by the agent at run time (the JS1 Claude judge is out, GATE §6).
