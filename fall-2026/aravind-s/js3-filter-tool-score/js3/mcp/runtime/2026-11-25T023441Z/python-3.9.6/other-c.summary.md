# Runtime trace `other-c`: the lesson 8 reference server, traced, the network denied by sandbox-exec

The lesson 8 reference server: `js3/mcp/other-server/main.py` in the repo (SHA-256 `948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769`), Python 3.9.6, the sessions of `tools/mcp_client.py` (early, main, lifecycle, bytes, deep), each on a fresh process. Command: `/usr/bin/sandbox-exec -p (version 1)(allow default)(deny network*) python3 -B -I tools/mcp_trace_boot.py <event log> js3/mcp/other-server/main.py --stdio`.

What the audit hook saw while the server ran and as its process ended (after the boot had installed the hook and imported runpy). Evidence type: executed on a fixture. It shows what happened in these sessions on these inputs, not every possible input.

| What | Seen |
|---|---|
| Event logs | 5 of 5 sessions recorded; 0 hook errors; 0 unreadable lines |
| Answers | 30 of 30 as the client's plan expects; 21 lines from the server; exit codes early 0, main 0, lifecycle 0, bytes 1, deep 1 |
| Files opened to write, or changed | none |
| Sockets and network calls | none |
| Processes started or signalled | none |
| ctypes | none |
| Network or process modules loaded at any point (socket, _socket, ssl, _ssl, http, subprocess, ...) | none |
| Read: Python's own files (standard library and its bytecode caches) | 13 files; 5 directory listings |
| Read: the server's code | 1 files: `<repo>/js3/mcp/other-server/main.py` |
| Read: FILTER.md | none |
| Read: persona/ (the fictional persona) | none |
| Read: runs/ (the saved board answers) | none |
| Modules the server's run loaded | 19: argparse, gettext, json, json.decoder, json.scanner, _json, json.encoder, locale, errno, shutil, fnmatch, zlib, bz2, _compression, threading, _bz2, lzma, _lzma, grp |
| Import attempts that loaded nothing | none |
| Modules already loaded before the hook | 37 (by Python's own startup; the boot imports nothing more) |
| The launcher (boot and runpy) | 31 modules (runpy, importlib.machinery, importlib, types, warnings, importlib.util, importlib.abc, typing, collections, heapq, _heapq, itertools, keyword, operator, _operator, reprlib, _collections, collections.abc, contextlib, functools, _functools, re, enum, sre_compile, _sre, sre_parse, sre_constants, copyreg, pkgutil, weakref, _weakrefset), 25 files of Python's own read, listings <python>/collections, <python>/importlib |
| As the process ended | Python's own files (standard library and its bytecode caches): 4 files; the server's code: 1 files: `<repo>/js3/mcp/other-server/main.py`; the boot script: 1 files: `<boot>/mcp_trace_boot.py` |

## Per session

| Session | data reads | listings | writes | sockets | network | processes | ctypes | modules loaded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| early | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 |
| main | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 |
| lifecycle | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 |
| bytes | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 |
| deep | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 19 |

## Every other event Python reported, with its count

- launcher: `compile or marshal.loads` 135, `exec` 135, `object.__getattr__` 10, `object.__setattr__` 25, `sys._getframe` 55
- server: `compile or marshal.loads` 75, `exec` 75, `object.__setattr__` 5, `sys._getframe` 5
- exit: `sys.excepthook` 2

Hook errors: 0. Unreadable lines in the event logs: 0. Sessions with no event log: none. Opens are open calls: Python 3.9's pathlib raises two events for one open (io.open's, then os.open's), counted once here. The full lists (every file, listing and module) are in `other-c.summary.json`; every line of the sessions is in `other-c.client.jsonl`.
