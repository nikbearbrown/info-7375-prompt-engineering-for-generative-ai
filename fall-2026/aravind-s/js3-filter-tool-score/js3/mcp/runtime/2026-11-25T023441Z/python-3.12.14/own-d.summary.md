# Runtime trace `own-d`: our server at a54c424 (the evaluated commit), traced

Our server: `job_agent/mcp_server.py` in the repo at a54c424 (git archive) (SHA-256 `e39a82fe67a097d206ee49e1758bf68a4242107c265b4350bbca5e8d84e5325c`), Python 3.12.14, the sessions of `tools/mcp_client.py` (early, main, lifecycle, bytes, deep), each on a fresh process. Command: `python3 -B tools/mcp_trace_boot.py <event log> -m job_agent.mcp_server`. FILTER.md SHA-256 `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1`.

What the audit hook saw while the server ran and as its process ended (after the boot had installed the hook and imported runpy). Evidence type: executed on a fixture. It shows what happened in these sessions on these inputs, not every possible input.

| What | Seen |
|---|---|
| Event logs | 5 of 5 sessions recorded; 0 hook errors; 0 unreadable lines |
| Answers | 31 of 31 as the client's plan expects; 26 lines from the server; exit codes early 0, main 0, lifecycle 0, bytes 0, deep 0 |
| Files opened to write, or changed | none |
| Sockets and network calls | none |
| Processes started or signalled | none |
| ctypes | none |
| Network or process modules loaded at any point (socket, _socket, ssl, _ssl, http, subprocess, ...) | none |
| Read: Python's own files (standard library and its bytecode caches) | 35 files; 20 directory listings |
| Read: the server's code | 9 files: `<repo>/job_agent/__init__.py`, `<repo>/job_agent/errors.py`, `<repo>/job_agent/evidence.py`, `<repo>/job_agent/filter.py`, `<repo>/job_agent/filter_run.py`, `<repo>/job_agent/mcp_server.py`, `<repo>/job_agent/providers.py`, `<repo>/job_agent/resume.py`, `<repo>/job_agent/rule.py`; 5 directory listings |
| Read: FILTER.md | `<repo>/FILTER.md` (6) |
| Read: persona/ (the fictional persona) | `<repo>/persona/jane-doe.json` (3) |
| Read: runs/ (the saved board answers) | 27 opens of 16 files; 51 directory listings |
| Read: anything else in the repo | 5 directory listings |
| Modules the server's run loaded | 57: job_agent, __future__, argparse, gettext, hashlib, _hashlib, _blake2, json, json.decoder, json.scanner, _json, json.encoder, platform, signal, traceback, collections.abc, linecache, tokenize, token, _tokenize, textwrap, contextlib, unicodedata, datetime, _datetime, pathlib, fnmatch, ntpath, errno, urllib.parse, urllib, math, ipaddress, job_agent.filter, job_agent.resume, copy, weakref, _weakrefset, job_agent.errors, job_agent.providers, html, html.entities, job_agent.rule, job_agent.filter_run, gzip, _compression, struct, _struct, zlib, job_agent.evidence, locale, _locale, shutil, bz2, _bz2, lzma, _lzma |
| Import attempts that loaded nothing | _wmi, _winapi, nt |
| Modules already loaded before the hook | 52 (by Python's own startup; the boot imports nothing more) |
| The launcher (boot and runpy) | 6 modules (runpy, importlib.machinery, importlib, warnings, importlib.util, importlib._abc), 3 files of Python's own read, listings <boot>, <python>/importlib |

## Per session

| Session | data reads | listings | writes | sockets | network | processes | ctypes | modules loaded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| early | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 57 |
| main | 36 | 57 | 0 | 0 | 0 | 0 | 0 | 57 |
| lifecycle | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 57 |
| bytes | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 57 |
| deep | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 57 |

## Every other event Python reported, with its count

- launcher: `compile or marshal.loads` 15, `exec` 30
- server: `builtins.id` 40, `compile or marshal.loads` 255, `exec` 260, `object.__setattr__` 55, `sys._getframemodulename` 35

Hook errors: 0. Unreadable lines in the event logs: 0. Sessions with no event log: none. Opens are open calls: Python 3.9's pathlib raises two events for one open (io.open's, then os.open's), counted once here. The full lists (every file, listing and module) are in `own-d.summary.json`; every line of the sessions is in `own-d.client.jsonl`.
