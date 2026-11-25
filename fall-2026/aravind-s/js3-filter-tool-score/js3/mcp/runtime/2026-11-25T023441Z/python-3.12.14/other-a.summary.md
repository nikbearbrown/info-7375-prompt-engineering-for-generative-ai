# Runtime trace `other-a`: the lesson 8 reference server, traced

The lesson 8 reference server: `js3/mcp/other-server/main.py` in the repo (SHA-256 `948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769`), Python 3.12.14, the sessions of `tools/mcp_client.py` (early, main, lifecycle, bytes, deep), each on a fresh process. Command: `python3 -B -I tools/mcp_trace_boot.py <event log> js3/mcp/other-server/main.py --stdio`.

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
| Read: Python's own files (standard library and its bytecode caches) | 12 files; 10 directory listings |
| Read: the server's code | 1 files: `<repo>/js3/mcp/other-server/main.py` |
| Read: FILTER.md | none |
| Read: persona/ (the fictional persona) | none |
| Read: runs/ (the saved board answers) | none |
| Modules the server's run loaded | 18: argparse, gettext, json, json.decoder, json.scanner, _json, json.encoder, locale, _locale, errno, shutil, fnmatch, zlib, bz2, _compression, _bz2, lzma, _lzma |
| Import attempts that loaded nothing | none |
| Modules already loaded before the hook | 52 (by Python's own startup; the boot imports nothing more) |
| The launcher (boot and runpy) | 13 modules (runpy, importlib.machinery, importlib, warnings, importlib.util, importlib._abc, pkgutil, weakref, _weakrefset, typing, collections.abc, contextlib, _typing), 9 files of Python's own read, listings <python>/collections, <python>/importlib |
| As the process ended | Python's own files (standard library and its bytecode caches): 2 files; the server's code: 1 files: `<repo>/js3/mcp/other-server/main.py`; the boot script: 1 files: `<boot>/mcp_trace_boot.py` |

## Per session

| Session | data reads | listings | writes | sockets | network | processes | ctypes | modules loaded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| early | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| main | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| lifecycle | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| bytes | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |
| deep | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 18 |

## Every other event Python reported, with its count

- launcher: `compile or marshal.loads` 50, `exec` 65, `object.__setattr__` 20, `sys._getframemodulename` 5
- server: `compile or marshal.loads` 70, `exec` 70, `object.__setattr__` 5, `sys._getframemodulename` 5
- exit: `compile or marshal.loads` 11, `sys.excepthook` 2

Hook errors: 0. Unreadable lines in the event logs: 0. Sessions with no event log: none. Opens are open calls: Python 3.9's pathlib raises two events for one open (io.open's, then os.open's), counted once here. The full lists (every file, listing and module) are in `other-a.summary.json`; every line of the sessions is in `other-a.client.jsonl`.
