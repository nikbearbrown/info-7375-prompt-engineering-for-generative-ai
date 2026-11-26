# priya-filter: MCP tool server for the JS3 filter

Written from scratch with the Python standard library: no MCP SDK, no
network, and no process modules in the server.

## Run

Server (it waits on stdin, so it is normally started by a client):

```
python3 -m mcp.server --config config/filter-v1.1.json
```

Scripted client. It starts the server itself, runs 8 steps, prints one line
per step, and exits with 0 only if every step behaved as expected:

```
python3 -m mcp.client
python3 -m mcp.client --config config/filter-v1.1.json \
    --decisions out/filter/v1.1/decisions.jsonl
```

`--root` (the folder holding `CORPUS.sha256`) and `--transcripts` exist for
the offline tests, which point them at a constructed corpus in a temporary
folder.

## Protocol

Newline-delimited JSON-RPC 2.0 over stdio. stdout carries only JSON-RPC
messages; diagnostics go to stderr.

| Method | Behaviour |
|---|---|
| `initialize` | Echoes the client's `protocolVersion` if it is one of `2025-06-18`, `2025-03-26`, `2024-11-05`; otherwise answers `2025-06-18`. `serverInfo.name` is `priya-filter`; `capabilities` is `{"tools": {}}`. A second `initialize` is -32600. |
| `notifications/initialized` | No reply. |
| `ping` | `{}` |
| `tools/list` | Exactly one tool, `score_posting`. |
| `tools/call` | `score_posting` with `{board, id}`. |
| anything else | -32601 |

Any request other than `initialize` sent before `initialize` gets -32002
("server not initialized"); `ping` is included. Notifications never get a
reply. Unparsable JSON gets -32700; a batch array or a non-JSON-RPC object
gets -32600.

### score_posting

Input schema: `board` must be one of the boards with a frozen file in
`CORPUS.sha256` (`databricks`, `openai`, `scaleai`); `id` is a non-empty
string. Both fields are required, and `additionalProperties` is false.

The result is `content: [{type: "text", text: <JSON>}]` with `board`, `id`,
`title`, `url`, `config_version`, `decision`, `reason`, `score`,
`rules_fired` and `matched_spans` (each span gives rule, word, field, start,
end and the exact text matched).

| Input | Outcome |
|---|---|
| known posting | `isError: false`, result as above |
| unknown posting id | `isError: true`, text explains |
| extra argument (for example `"path"`) | JSON-RPC error -32602 |
| missing argument, board outside the enum, non-string id | -32602 |
| tool name other than `score_posting` | -32602 |

## Safety properties

- **Read-only.** It reads only `CORPUS.sha256`, the frozen `out/raw/` files
  (hash-checked by `js3.corpus`; a mismatch makes the call return
  `isError: true`), `config/boards.json` and the config named at startup.
- **No client-chosen paths.** The config, corpus root and transcript folder
  are fixed on the command line. `board` is checked against a fixed list and
  `id` is only a dictionary key.
- **One output file.** `transcripts/server-<UTC>.jsonl` is the only file the
  server writes. Each line is
  `{"time_utc", "direction": "in"|"out", "message"}`, or `"raw"` for input
  that was not JSON. A new file is created for each run and never reused.
- **No network or process modules.** No `socket`, `urllib`, `http`,
  `subprocess` or `os.system`. `tests/test_mcp_server.py` scans the source
  and also checks the modules actually imported at runtime.

The client also writes `transcripts/client-<UTC>.jsonl`, logging both
directions from its own side.
