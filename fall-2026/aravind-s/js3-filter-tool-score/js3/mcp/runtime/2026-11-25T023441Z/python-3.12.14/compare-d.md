# Comparison `d`: our server at a54c424 (the evaluated commit) against the current server, and against our client's run of a54c424 recorded on 2026-11-21

Each answer is compared line by line, session by session (times left out); where two lines differ, every JSON field that differs is listed, and a tool result's text is compared as the JSON it holds.

## `own-d` against `own-a`

- Answers: **different** (SHA-256 of all answers without times: `02fff3bfdbfd6f0d...` and `81e722ad72d6fb0b...`)
- Event summaries: **different** (leaving out the run's name, command and sandbox setting)

| Session | Step | id | Field | own-d | own-a |
|---|---:|---:|---|---|---|
| main | 4 | 3 | `$.result.content[0].text (its JSON).filter.sha256` | `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1` | `4d79d279f5b5157e8905cb0e2109e4c50b1b983d410d8bff2a0614077e32a572` |
| main | 5 | 4 | `$.result.content[0].text (its JSON).filter.sha256` | `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1` | `4d79d279f5b5157e8905cb0e2109e4c50b1b983d410d8bff2a0614077e32a572` |

Event summary differences:

| Field | own-d | own-a |
|---|---|---|
| `$.filter_md_sha256` | `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1` | `4d79d279f5b5157e8905cb0e2109e4c50b1b983d410d8bff2a0614077e32a572` |
| `$.server_sha256` | `e39a82fe67a097d206ee49e1758bf68a4242107c265b4350bbca5e8d84e5325c` | `db44168911705a2ee853b999ac1ebac7ddbc10914c293ce418f7478799c5a347` |

## `own-d` against `js3/mcp/transcripts/2026-11-21T084407Z-own-client.jsonl`

- Answers: **the same** (SHA-256 of all answers without times: `02fff3bfdbfd6f0d...` and `02fff3bfdbfd6f0d...`)
