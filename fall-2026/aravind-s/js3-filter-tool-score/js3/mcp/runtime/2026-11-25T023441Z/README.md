# Runtime trace of the two MCP servers, 2026-11-24

Recorded with `python3 tools/mcp_runtime_trace.py record --python /opt/homebrew/bin/python3.12 --python /usr/bin/python3` on 2026-11-24 21:34 EST (2026-11-25T02:34:41Z), at commit `03ff5d8`, once per Python: 3.12.14 (`/opt/homebrew/bin/python3.12`, in `python-3.12.14/`), 3.9.6 (`/usr/bin/python3`, in `python-3.9.6/`). Tools: `tools/mcp_runtime_trace.py` (SHA-256 `4b376d78ab48...`), `tools/mcp_trace_boot.py` (SHA-256 `fa4c869d2db3...`). Each server ran with its code unchanged, under a Python audit hook (PEP 578) installed by `tools/mcp_trace_boot.py`, and was driven through the five sessions of `tools/mcp_client.py` (early, main, lifecycle, bytes, deep), each on a fresh process. Evidence type: executed on a fixture. These files show what happened in these runs on these inputs, not proof for every input; the source reading in the evaluations covers the code paths.

Claude Code ran this at Aravind's request on 2026-11-24 (Boston time; the folder's name is the UTC time), for `js3/mcp/EVALUATION-OWN.md` and `js3/mcp/EVALUATION-OTHER.md`. The sections below this one are written by the tool from the saved files; this section is not.

## What these runs show

In these sessions, on these inputs (the saved board answers of run `2026-11-20T114036Z`, FILTER.md, the fictional persona), on both Pythons:

- **Our server** (`job_agent/mcp_server.py`, SHA-256 `db441689...a347`) opened no file to write and changed no file, except in run `own-b`, where the only write was the transcript it was started with: `js3/mcp/transcripts/runtime-trace-own-b.jsonl`, one `os.open` with `O_WRONLY+O_APPEND+O_CREAT+O_NOFOLLOW` and one open of that descriptor in mode `a` per session. It created no socket, made no network call and started or signalled no process. It read its own code (9 files in `job_agent/`), `FILTER.md` (6 opens: 2 for each of the 3 calls that reached its sources), `persona/jane-doe.json` (3), 16 files under `runs/` (27 opens), and Python's own files; Python's import system listed the repo's top folder once per session. Nothing outside the repo and the Python install was opened.
- **The lesson 8 reference server** (`js3/mcp/other-server/main.py`, SHA-256 `948337af...8b1769`, the bytes the evaluation names) read its own file and Python's own files and nothing else; it wrote nothing, created no socket and started no process. When it ended on the bytes and deep inputs, Python's traceback printer read the source files named in the traceback.
- **Modules.** On Python 3.12.14 neither server loaded `socket`, `ssl`, `http`, `subprocess` or any other module that can reach a network or start a process (the list is `NETWORK_OR_PROCESS` in `tools/mcp_runtime_trace.py`). On Python 3.9.6 our server loaded `subprocess`, `_posixsubprocess`, `select` and `selectors`: `job_agent/mcp_server.py` imports `platform` (line 48), and Python 3.9's `platform.py` imports `subprocess` when it loads (its line 119; Python 3.12's waits until a function needs it). No process was started on either Python. The reference server loaded none of them on either.
- **The network block.** With the network denied by `sandbox-exec`, every answer of both servers was the same as with it allowed (`compare-c.md` in each Python's folder).
- **The hook changed no answer.** Each traced run's answers are the same as the untraced run's (`compare-plain.md`).
- **The evaluated commit.** Our server at `a54c424` gave the same answers as today's server, except one field: `filter.sha256` in the two `score_posting` results of the main session (step 4, id 3, the kept posting; step 5, id 4, the rejected posting), which is FILTER.md's SHA-256: `f1edbf0b...ba6f1` at `a54c424`, `4d79d279...a572` today, after FILTER.md v1.1 was added below v1.0 in `5dff01f`. Its answers are also the same as the ones our client recorded from it on 2026-11-21 (`compare-d.md`).

None of this makes either server conformant or shows it to be secure.

## Re-check

From the repo root:

```bash
python3 tools/mcp_runtime_trace.py check js3/mcp/runtime/2026-11-25T023441Z
```

It runs every run again, with each Python named above that is still on this Mac, in a temporary folder, and compares each new event summary with the saved `*.summary.json` (they must be equal) and each run's answers with the saved ones (SHA-256 of every line from the server, without times). Times in the `*.jsonl` files differ from run to run; nothing else should.

## Python 3.12.14 (`python-3.12.14/`)

| Run | What | Answers as expected | Writes | Sockets and network | Processes | Network or process modules loaded |
|---|---|---|---|---|---|---|
| `own-a` | our server, traced, without --transcript | 31 of 31 | none | none | none | none |
| `own-b` | our server, traced, with --transcript | 31 of 31 | `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode None, O_WRONLY+O_APPEND+O_CREAT+O_NOFOLLOW+O_CLOEXEC; `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode 'a', O_WRONLY+O_APPEND+O_CREAT+O_CLOEXEC (through the descriptor just opened) | none | none | none |
| `own-c` | our server, traced, the network denied by sandbox-exec | 31 of 31 | none | none | none | none |
| `own-d` | our server at a54c424 (the evaluated commit), traced | 31 of 31 | none | none | none | none |
| `own-plain` | our server, not traced (the control) | 31 of 31 | (not traced) | (not traced) | (not traced) | (not traced) |
| `other-a` | the lesson 8 reference server, traced | 30 of 30 | none | none | none | none |
| `other-c` | the lesson 8 reference server, traced, the network denied by sandbox-exec | 30 of 30 | none | none | none | none |
| `other-plain` | the lesson 8 reference server, not traced (the control) | 30 of 30 | (not traced) | (not traced) | (not traced) | (not traced) |

- `own-c` against `own-a`: the same answers; event summaries the same (`compare-c.md`).
- `other-c` against `other-a`: the same answers; event summaries the same (`compare-c.md`).
- `own-d` against `own-a`: 2 differing fields (`$.result.content[0].text (its JSON).filter.sha256`); event summaries differ in `$.filter_md_sha256`, `$.server_sha256` (`compare-d.md`).
- `own-d` against `js3/mcp/transcripts/2026-11-21T084407Z-own-client.jsonl`: the same answers (`compare-d.md`).
- `own-a` against `own-plain`: the same answers (`compare-plain.md`).
- `other-a` against `other-plain`: the same answers (`compare-plain.md`).
- The network block: `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'` (deprecated on macOS, still present). Before the c runs, the same profile refused a planted connection from this Python to 127.0.0.1 port 9: `PermissionError 1`. The claim it supports is only that every answer with the network denied was the same as with it allowed.

## Python 3.9.6 (`python-3.9.6/`)

| Run | What | Answers as expected | Writes | Sockets and network | Processes | Network or process modules loaded |
|---|---|---|---|---|---|---|
| `own-a` | our server, traced, without --transcript | 31 of 31 | none | none | none | _posixsubprocess, select, selectors, subprocess |
| `own-b` | our server, traced, with --transcript | 31 of 31 | `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode None, O_WRONLY+O_APPEND+O_CREAT+O_NOFOLLOW+O_CLOEXEC; `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode 'a', O_WRONLY+O_APPEND+O_CREAT+O_CLOEXEC (through the descriptor just opened) | none | none | _posixsubprocess, select, selectors, subprocess |
| `own-c` | our server, traced, the network denied by sandbox-exec | 31 of 31 | none | none | none | _posixsubprocess, select, selectors, subprocess |
| `own-d` | our server at a54c424 (the evaluated commit), traced | 31 of 31 | none | none | none | _posixsubprocess, select, selectors, subprocess |
| `own-plain` | our server, not traced (the control) | 31 of 31 | (not traced) | (not traced) | (not traced) | (not traced) |
| `other-a` | the lesson 8 reference server, traced | 30 of 30 | none | none | none | none |
| `other-c` | the lesson 8 reference server, traced, the network denied by sandbox-exec | 30 of 30 | none | none | none | none |
| `other-plain` | the lesson 8 reference server, not traced (the control) | 30 of 30 | (not traced) | (not traced) | (not traced) | (not traced) |

- `own-c` against `own-a`: the same answers; event summaries the same (`compare-c.md`).
- `other-c` against `other-a`: the same answers; event summaries the same (`compare-c.md`).
- `own-d` against `own-a`: 2 differing fields (`$.result.content[0].text (its JSON).filter.sha256`); event summaries differ in `$.filter_md_sha256`, `$.server_sha256` (`compare-d.md`).
- `own-d` against `js3/mcp/transcripts/2026-11-21T084407Z-own-client.jsonl`: the same answers (`compare-d.md`).
- `own-a` against `own-plain`: the same answers (`compare-plain.md`).
- `other-a` against `other-plain`: the same answers (`compare-plain.md`).
- The network block: `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)'` (deprecated on macOS, still present). Before the c runs, the same profile refused a planted connection from this Python to 127.0.0.1 port 9: `PermissionError 1`. The claim it supports is only that every answer with the network denied was the same as with it allowed.

## Across the Pythons (`compare-python.md`)

- `own-a`: answers the same under 3.12.14 and 3.9.6; modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess.
- `own-b`: answers the same under 3.12.14 and 3.9.6; modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess.
- `own-c`: answers the same under 3.12.14 and 3.9.6; modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess.
- `own-d`: answers the same under 3.12.14 and 3.9.6; modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess.
- `own-plain`: answers the same under 3.12.14 and 3.9.6.
- `other-a`: answers the same under 3.12.14 and 3.9.6.
- `other-c`: answers the same under 3.12.14 and 3.9.6.
- `other-plain`: answers the same under 3.12.14 and 3.9.6.

## Reading the files

- `<repo>` is the folder the server ran in (for `own-d`, a temporary folder holding `git archive a54c424`), `<boot>` the folder of `tools/mcp_trace_boot.py`, `<python>` that Python's standard library, `~` the home folder. No file here names this Mac's account.
- Run `own-b`'s `--transcript` file was written as `js3/mcp/transcripts/runtime-trace-own-b.jsonl` (in the one folder the server accepts), checked against the client's record and then, after the server had ended, moved by the tool into that Python's folder as `own-b.server.jsonl`.
- A bytecode cache file (`__pycache__/*.pyc`) is shown as its module's source file, and Python's `compile` and `marshal.loads` counts are added up: which of the two Python uses depends on whether a cache exists, not on the server. For the same reason module files are listed, not counted.
- The hook sees a call before the system answers it: an open of a file that does not exist (Python looking for a bytecode cache) is recorded as an attempt. A write would be recorded even if it failed.
- The hook keeps arguments only for an allowlist of events (the boot's docstring): file paths, modes and flags, socket families and addresses, the file name of a started program, module names. Every other event is kept as its name and a count; no environment value is ever kept.
- What the hook cannot see: work done in C that raises no audit event. That covers Python's own reads before the hook was installed, the system loader opening a C extension module (such as `_json` or `zlib`: these appear in the module lists, not the file lists), and any file a C library opens by itself (for example a configuration file read by the OpenSSL library behind `_hashlib`). Neither server brings a C extension of its own.
