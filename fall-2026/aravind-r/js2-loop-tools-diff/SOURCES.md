# Sources

All work below is dated 2026-11-10 unless stated otherwise (commit dates in `git log`). Every commit in this folder carries my git identity (`aravindravi7`). The tables say which commits Claude Code made in its session and which I made.

## Starting point: my Job-Search Agent 1 code

Copied in `ce33fd8d` from `fall-2026/aravind-r/js1-contract-and-watch/` (branch `js1-contract-and-watch-aravind-r`, last JS1 commit `fa577f9`, 2026-10-31):

- `src/claude-judge.mjs`, `src/fetch.mjs`, `src/persona.mjs`, `src/rule.mjs`, `src/state.mjs`, `src/text.mjs`, `src/watch.mjs`
- `test/contract.test.mjs`, `test/fixtures/constructed-board.json`
- `persona/` (the fictional persona), `prompts/judge.v1.md`, `prompts/judge.v2.md`
- `CONTRACT.md` (JS1's contract, read at runtime by `src/claude-judge.mjs`)

`src/state.mjs` stayed as JS1 wrote it until `c04d1ecf`.

## Written by Claude Code

Claude Code ran in the Claude desktop app (model `claude-opus-5-5`). It wrote these files, and the commits named here unless marked otherwise:

| File | Commits | What Claude Code wrote |
|---|---|---|
| `CLAUDE.md` | `ce33fd8d` (committed by me) | the file, from text I supplied; the content is mine |
| `.gitignore` | `ce33fd8d` (committed by me), `16025375` | ignore rules for `.DS_Store`, `node_modules/`, `.env`; `.mutants/` added in `16025375` |
| `GATE.md` (first committed version) | `aedc7034` (committed by me) | a draft gate with a "DRAFT proposed by Claude Code" banner, committed unedited, then replaced by my version in `359ee568` |
| `test/boundary-cases.md` (first committed version) | `aedc7034` (committed by me) | a 19-row draft; rows 1–19 of my 41-row table in `359ee568` follow it |
| `src/policy.mjs` | `49c6066e`, `7ec7cccb`, `85657387` | the permission policy: request checks, the policed network session (budgets, repeat rule, one counted retry, `min(15 s, remaining)` timeout, `redirect: 'manual'`), the file policy (reads, writes, deletes, `--approve`, `--replay` paths), CLI budget checks |
| `test/policy.test.mjs` | `49c6066e`, `7ec7cccb`, `93b5130b` | one test per boundary row (rows 1–41, then 42–43), a check that each prediction matches the table, a check that `LIMITS` match GATE.md |
| `tools/mutate-policy.mjs` | `f7a59255`, `2e8a21b1`, `85657387`, `f39a7b8e` | the mutation check: 19 broken copies of `policy.mjs`, run against the policy, loop and wrong-version tests |
| `test/no-direct-fetch.test.mjs` | `dfe31a11` | fails if a file in `src/` other than `policy.mjs` calls `fetch(` |
| `src/providers/greenhouse.mjs`, `src/providers/lever.mjs` | `56f98d82`, `85657387`, `42c9bc52` | the two providers: URL, observe through the policy session, parse; a repeated id makes the response malformed |
| `test/providers.test.mjs` | `56f98d82`, `42c9bc52` | provider URL, timeout and parse tests, including duplicate ids |
| `boards.json` | `7bd428b6` | the four boards from GATE.md |
| `src/loop.mjs` | `3057a332`, `85657387`, `e871e90d`, `377fd51c`, `1e698443` | the loop: CLI, exits and exit codes, budgets, error policy, state snapshots, `out/failures.json`, `--replay`, the append-only trace |
| `test/loop.test.mjs` | `3057a332`, `647e5633`, `677b54a8`, `85657387`, `e871e90d`, `377fd51c`, `42c9bc52`, `ea5e0198` | loop tests, including rows 38–41 as zero-network loop runs, timeout tests on an injected clock, trace order, replay and `failures.json`, the `saveState` error, duplicate raw ids, snapshot permission bits |
| `src/check.mjs` | `8f14fcd2`, `41029237`, `15ae4789` | the independent checker (rules 1–3), the no-observations result, positive Greenhouse ids |
| `test/check.test.mjs` | `8f14fcd2`, `41029237`, `15ae4789` | checker tests on hand-built `out/` trees |
| `test/wrong-versions.test.mjs` | `b9adc1db` | loop-level tests for GATE.md wrong versions 6, 7, 8, 9, 11, 12, 15, 17 and 19 |
| `configs/lv-spotify-only.json` | `c7a87cf0` | the single-board config for the finished-wrong demonstration |
| `test/state-regression.test.mjs` | `17c9225a` (committed by me) | the five-case regression test, to my specification (cases, fixture values, error code) |
| `src/state.mjs` (the patch) | `c04d1ecf` (committed by me) | the id fix and its two revisions (see `REVIEW.md`) |
| `README.md`, `REVIEW.md`, `SOURCES.md`, `TRACE.md`, and the "Actual result" column of `test/boundary-cases.md` | `88c3358e`, `634489f9` (committed by me); later `SOURCES.md` corrections by Claude Code | drafted from the commits, traces and `evidence/` files they cite |

Claude Code also made unsaved HTTP checks of the four boards with `curl` on 2026-11-10 (200 for `stripe`, `airbnb`, `spotify`; 404 for `no-such-board-js2`), which GATE.md cites in "Starting point and boards". It also ran the checker on saved traces while drafting `REVIEW.md` and `TRACE.md`, but the checker output those files quote is from my own runs, saved as `evidence/check-pre-fix.txt` and `evidence/check-post-patch.txt` (`88c3358e`).

Commits I made (not Claude Code): `ce33fd8d`, `aedc7034`, `359ee568`, `b0bc86f9`, `4c7ab6b2`, `4b1336cf`, `17c9225a`, `3aae3352`, `a0dc494a`, `c04d1ecf`, `0310af25`, `c4f9b555`, `0326b046`, `88c3358e`, `634489f9`. I also ran every live and replay run in `out/traces/`. Claude Code made no live run of the loop.

## Drafted in Claude chat

The repository holds the results, not the chat transcripts or the scripts.

| What | Where it landed |
|---|---|
| The GATE.md first draft that became my GATE.md | `359ee568` (202 lines) |
| Boundary rows 20–43 | rows 20–41 in `359ee568`; rows 42–43 in `4c7ab6b2` |
| Decision wording | the dated Decisions added in `359ee568`, `4c7ab6b2`, `17c9225a`, `3aae3352`, `a0dc494a` and `0310af25` |
| The Python insertion scripts | the scripts I used to insert that text into `GATE.md` and `test/boundary-cases.md` (not in this repository) |
