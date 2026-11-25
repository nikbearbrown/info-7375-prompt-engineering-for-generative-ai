# Runtime trace `own-b`: our server, traced, with --transcript

Our server: `job_agent/mcp_server.py` in the repo (SHA-256 `db44168911705a2ee853b999ac1ebac7ddbc10914c293ce418f7478799c5a347`), Python 3.9.6, the sessions of `tools/mcp_client.py` (early, main, lifecycle, bytes, deep), each on a fresh process. Command: `python3 -B tools/mcp_trace_boot.py <event log> -m job_agent.mcp_server --transcript js3/mcp/transcripts/runtime-trace-own-b.jsonl`. FILTER.md SHA-256 `4d79d279f5b5157e8905cb0e2109e4c50b1b983d410d8bff2a0614077e32a572`.

What the audit hook saw while the server ran and as its process ended (after the boot had installed the hook and imported runpy). Evidence type: executed on a fixture. It shows what happened in these sessions on these inputs, not every possible input.

| What | Seen |
|---|---|
| Event logs | 5 of 5 sessions recorded; 0 hook errors; 0 unreadable lines |
| Answers | 31 of 31 as the client's plan expects; 26 lines from the server; exit codes early 0, main 0, lifecycle 0, bytes 0, deep 0 |
| Files opened to write, or changed | `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode None, O_WRONLY+O_APPEND+O_CREAT+O_NOFOLLOW+O_CLOEXEC; `<repo>/js3/mcp/transcripts/runtime-trace-own-b.jsonl`: 5 open(s), mode 'a', O_WRONLY+O_APPEND+O_CREAT+O_CLOEXEC (through the descriptor just opened) |
| Sockets and network calls | none |
| Processes started or signalled | none |
| ctypes | none |
| Network or process modules loaded at any point (socket, _socket, ssl, _ssl, http, subprocess, ...) | _posixsubprocess, select, selectors, subprocess |
| Read: Python's own files (standard library and its bytecode caches) | 33 files; 15 directory listings |
| Read: the server's code | 9 files: `<repo>/job_agent/__init__.py`, `<repo>/job_agent/errors.py`, `<repo>/job_agent/evidence.py`, `<repo>/job_agent/filter.py`, `<repo>/job_agent/filter_run.py`, `<repo>/job_agent/mcp_server.py`, `<repo>/job_agent/providers.py`, `<repo>/job_agent/resume.py`, `<repo>/job_agent/rule.py`; 5 directory listings |
| Read: FILTER.md | `<repo>/FILTER.md` (6) |
| Read: persona/ (the fictional persona) | `<repo>/persona/jane-doe.json` (3) |
| Read: runs/ (the saved board answers) | 27 opens of 16 files; 51 directory listings |
| Read: anything else in the repo | 5 directory listings |
| Modules the server's run loaded | 56: job_agent, __future__, argparse, gettext, hashlib, _hashlib, _blake2, _sha3, json, json.decoder, json.scanner, _json, json.encoder, platform, subprocess, errno, signal, threading, grp, _posixsubprocess, select, selectors, math, traceback, linecache, tokenize, token, unicodedata, datetime, _datetime, pathlib, fnmatch, ntpath, urllib.parse, urllib, job_agent.filter, job_agent.resume, copy, job_agent.errors, job_agent.providers, html, html.entities, job_agent.rule, job_agent.filter_run, gzip, struct, _struct, zlib, _compression, job_agent.evidence, locale, shutil, bz2, _bz2, lzma, _lzma |
| Import attempts that loaded nothing | msvcrt, nt, org.python.core, org.python, org |
| Modules already loaded before the hook | 37 (by Python's own startup; the boot imports nothing more) |
| The launcher (boot and runpy) | 31 modules (runpy, importlib.machinery, importlib, types, warnings, importlib.util, importlib.abc, typing, collections, heapq, _heapq, itertools, keyword, operator, _operator, reprlib, _collections, collections.abc, contextlib, functools, _functools, re, enum, sre_compile, _sre, sre_parse, sre_constants, copyreg, pkgutil, weakref, _weakrefset), 25 files of Python's own read, listings <boot>, <python>/collections, <python>/importlib |
| The server's own transcript | 67 entries, 5 sessions, ends stdin closed; matches the client's record line for line: yes; written as `js3/mcp/transcripts/runtime-trace-own-b.jsonl`, kept here as `own-b.server.jsonl` |

## Per session

| Session | data reads | listings | writes | sockets | network | processes | ctypes | modules loaded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| early | 0 | 5 | 2 | 0 | 0 | 0 | 0 | 56 |
| main | 36 | 56 | 2 | 0 | 0 | 0 | 0 | 56 |
| lifecycle | 0 | 5 | 2 | 0 | 0 | 0 | 0 | 56 |
| bytes | 0 | 5 | 2 | 0 | 0 | 0 | 0 | 56 |
| deep | 0 | 5 | 2 | 0 | 0 | 0 | 0 | 56 |

## Every other event Python reported, with its count

- launcher: `compile or marshal.loads` 135, `exec` 135, `object.__getattr__` 10, `object.__setattr__` 25, `sys._getframe` 55
- server: `builtins.id` 40, `compile or marshal.loads` 245, `exec` 245, `object.__setattr__` 55, `sys._getframe` 35

Hook errors: 0. Unreadable lines in the event logs: 0. Sessions with no event log: none. Opens are open calls: Python 3.9's pathlib raises two events for one open (io.open's, then os.open's), counted once here. The full lists (every file, listing and module) are in `own-b.summary.json`; every line of the sessions is in `own-b.client.jsonl`.
