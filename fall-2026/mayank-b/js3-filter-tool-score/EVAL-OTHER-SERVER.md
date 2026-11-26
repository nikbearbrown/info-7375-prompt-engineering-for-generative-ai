# Evaluation: the course's Chapter 8 teaching server (draft for Mayank's decision)

**Status: DRAFT by Claude Code. The trust decision at the end is blank and belongs to Mayank.**

| | |
|---|---|
| Server | `info7375-readonly` 1.0.0, one tool `lookup` |
| Source (named) | INFO 7375 course repository, `lessons/08-mcp-from-scratch/code/main.py`, commit `a8629ce1c437abee3a2c4f025bd8be3183b0f0af` (2026-09-06, "feat: publish INFO 7375 Claude and Python course"). The file is the same at `origin/main` |
| Local copy | `other-server/main.py`: a 6-line provenance header, then the file byte for byte. The body's SHA-256 `948337af…1769` equals `git show <commit>:<path> \| shasum -a 256` |
| Maintainer | the course (Professor Bear's INFO 7375 repo), per the file header and the repo. Not independently verified |
| Run as | `python3 -I other-server/main.py --stdio`, cwd = project root |
| Evidence | `transcripts/C-teaching-server-2026-11-26T02-23-17Z.*` (22/22 steps matched `EXPECTED-C.md`, which was written from source before the first run). The first run `…2026-11-25T20-31-04Z.*` was also 22/22. `transcripts/C2-teaching-server-replay-of-B-*` (Claude Code's real handshake lines, replayed). An `-X importtime` run (below) |
| Task evaluated for | (a) connecting it to Claude Code inside JS3; (b) the Chapter 8 classroom exercise |


> **Re-recorded on the JS3 corpus, 2026-11-25 21:26 ET** (corpus run `2026-11-26T02-20-27Z-content`): `transcripts/A-scripted-2026-11-26T02-26-36Z` (22/22 steps as predicted), `transcripts/C-teaching-server-2026-11-26T02-26-45Z` (22/22), and the real client `transcripts/B-claude-code-2026-11-26T02-26-53Z` (Claude Code 2.1.323 sent `server/discover`, then `initialize`, `notifications/initialized`, `tools/list`, `tools/call`; the tool returned `keep` for posting 5183044008, and Claude repeated the verdict and reason verbatim). The observations below were first made on the development recordings against the JS2 corpus (named where cited); the re-recordings reproduced every step.

## 1. Protocol ledger

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| P1 | `tools/*` before `initialize`, and before the initialized notification → `-32000`. Readiness is set only by the notification | executed + source-inspected | C steps 1, 3, 4, 5 | allow | a new release |
| P2 | **Ignores the requested protocol version.** It never reads `params`. `initialize` with no params at all is accepted (step 17), and a request for `2024-11-05` gets `2025-11-25` (steps 15, 18). With params present, that reply looks the same as a correct "unsupported version" answer, so only step 17 shows the difference in execution | executed + source-inspected | C steps 15, 17, 18 | pending | — |
| P3 | **A second `initialize` is accepted, and `ready` is kept.** Step 15 answered a result, and the `tools/list` right after it (step 16) still succeeded | executed | C steps 15–16 | pending (unchosen behaviour, as Chapter 8 itself notes) | — |
| P4 | **A `tools/call` with no id is dropped**: no reply and nothing on stderr. Source shows `return None` before dispatch, so it is not executed either | executed (no reply, empty stderr) + source-inspected (not executed) | C step 14 | allow (harmless here) | — |
| P5 | **`ping` is not implemented**: `-32601 Method not found` | executed | C step 12 | pending | — |
| P6 | An unknown method **before ready** gets `-32000`, not `-32601`. Claude Code's real first line, `server/discover`, got `-32000 "Initialize and notify before using tools"` in the replay. Whether Claude Code falls back to `initialize` after a `-32000` (it did after our server's `-32601`) was **not checked**, because the server was not connected to a live client | executed (replay) | `C2-…replay-of-B…md` row 1 | pending | — |
| P7 | Request vs task errors: `lookup` with a non-string key → `-32602`; an unknown key → result `isError: true`. Every `score_posting` / `apply_to_job` call → `-32602 "Unknown tool"`, even with bad arguments, because the name is checked first | executed | C steps 6–9, 13; source | allow | — |
| P8 | `-32700` id null for `{`; `-32600` id null for `{}` and `[]` | executed | C steps 11, 21, 22 | allow | — |
| P9 | Conformance beyond the subset | not claimed by its own docs ("not a production or conformance-certified MCP implementation") | lesson `docs/en.md` | — | — |

## 2. Capability ledger

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| C1 | One tool `lookup`, schema `{"key": string}` with `additionalProperties: false`, enforced as "exactly the key `key`, a string" | advertised + source-inspected + executed | C step 5; source | allow | new release |
| C2 | Data = one literal in-memory mapping `{"office": "505A Dana Hall"}`. No file is read or written: no `open(`, `write`, `os.` or `subprocess` appears in the source | source-inspected (`grep` + reading all 72 lines) | `other-server/main.py` | allow | new release |
| C3 | No network: imports only `argparse`, `json`, `sys`. An `-X importtime` run of a real session on 2026-11-26 loaded no `socket`, `ssl`, `http` or `urllib` module | source-inspected + executed | command below | allow | new release |
| C4 | OS-level file/network activity | **uninspected** | — | pending | — |
| C5 | Reply formatting: `json.dumps` default separators, one line per reply, `flush=True` | executed | C `.jsonl` | allow | — |

Imports check, as run (stderr lists every module loaded; none is a network module):

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize"}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup","arguments":{"key":"office"}}}' \
  | python3 -I -X importtime other-server/main.py --stdio
```

## 3. Permission ledger

| # | Claim | Evidence type | Status | Re-review if |
|---|---|---|---|---|
| R1 | It cannot send or change data outside the folder: nothing written, no network (C2, C3) | source-inspected + executed | allow | new release |
| R2 | "Read a **public** course fixture": the word *public* is the server's testimony. The code classifies nothing. Only the data's owner (the course) can say it is public | advertised | pending (owner: the course) | — |
| R3 | **Task need for JS3: none.** It cannot score postings, and connecting it would only add a tool to Claude's context that the job search does not use | — (a human decision) | recommend deny for JS3 | the task changes |
| R4 | Classroom task (Chapter 8 exercise): offline, read-only, fixture data | source-inspected + executed | recommend allow for that task | — |

## 4. Evidence ledger

| # | Claim | Evidence type | Status |
|---|---|---|---|
| E1 | `505A Dana Hall` (step 13) equals the declared source, the literal in `main.py` | compared with source | allow, as "the fixture says" |
| E2 | `505A Dana Hall` is a real, current office | **uninspected** (not independently sourced) | deny as a fact about the world |
| E3 | `isError: true` + "Record not found" for an unknown key means "not in the fixture", not "does not exist" | source-inspected | — |

## Declared vs actual

| Declared | Actual | Match? |
|---|---|---|
| serverInfo `info7375-readonly` | no write or network path found (C2, C3) | yes, as far as checked |
| `lookup`: "Read a public course fixture" | reads one literal mapping. "public" cannot be checked in code | partly (R2) |
| protocolVersion `2025-11-25` | always answers that, whatever was asked, with or without params (P2) | the reply is constant; there is no negotiation |
| lifecycle (lesson docs: initialize, then the notification, then tools) | holds for first use (P1). Re-initialize is accepted with `ready` kept (P3) | partly |
| (not declared) `ping` | `-32601` (P5) | — |

## What a compatible client is NOT entitled to

- That "read-only" or "public" is true just because the name and description say so. C2 and C3 are what support it, and only for commit `a8629ce1`.
- That `2025-11-25` in the reply means the server checked or negotiated anything (P2).
- That a second `initialize` started a new session (P3).
- That a `-32000` reply to an unknown method means "retry later". It may mean "this method will never exist" (P6).
- That `505A Dana Hall` is a fact about the world (E2), or that a well-formed reply has provenance beyond the source literal.
- That 22/22 matched predictions mean MCP conformance. The lesson itself disclaims that.

## Recommendation (Claude Code's, not a decision)

- **JS3 job-search task: deny.** It is not unsafe, as far as was checked. It has no capability this task needs, and it fails `ping` and the discovery probe the real client sends first (P5, P6).
- **Chapter 8 classroom task: allow, bounded** to commit `a8629ce1…`, run as `python3 -I … --stdio` on the fixture.
- Re-review if the course publishes a new commit of `main.py`, a tool is added, or the data stops being a literal fixture.

## Sign-off (template; Mayank fills it in or withholds it)

```text
Sign-off — MCP evaluation packet, other server (course Chapter 8 teaching server @ a8629ce1)
Checked:      P1–P8 executed (scripted client, 22 steps, + a replay of Claude Code's handshake); C1–C3 source-inspected
              + executed; E1 compared with source
How:          predictions written from source before running (EXPECTED-C.md); drafted with Claude Code
Not checked:  OS-level activity; live Claude Code connection (deliberately not made before a decision);
              whether the fixture value is true; other commits of the file
Not claiming: that it is secure, conformant, or endorsed beyond the named task and commit
Decision:     ____ for task ____, commit a8629ce1c437abee3a2c4f025bd8be3183b0f0af
Re-review if: new commit / new tool / non-fixture data / a different task
```

**Decision (Mayank): ____ (allow / deny / pending, date)**

Signed or withheld: ____________ (name, date)
