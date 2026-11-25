"""Runtime evidence for JS3's two MCP servers: what each one opens, writes, connects to and starts, at run time.

The two evaluations (js3/mcp/EVALUATION-OWN.md and EVALUATION-OTHER.md) read every call that opens, writes, runs or
connects in the source, but left run-time file and network behavior uninspected. This tool runs each server, with
its code unchanged, under a Python audit hook (PEP 578: tools/mcp_trace_boot.py installs the hook, then runs the
server with runpy), drives it through the same scripted sessions as our client (tools/mcp_client.py: early, main,
lifecycle, bytes, deep; each on a fresh process) and keeps what the hook saw:

  own-a        our server (python3 -B -m job_agent.mcp_server), traced
  own-b        the same, started with --transcript: the one write the server is allowed
  own-c        own-a with the network denied by the operating system (sandbox-exec, macOS)
  own-d        our server at a54c424, the commit EVALUATION-OWN.md evaluated (git archive into a temporary folder)
  own-plain    our server, not traced: the control that shows the hook changes no answer
  other-a, other-c, other-plain    the same three for the lesson 8 reference server (js3/mcp/other-server/main.py)

and compares the answers: c against a (the network denied against allowed), d against a and against the run recorded
on 2026-11-21 (js3/mcp/transcripts/), a against plain. What the record shows is what happened in these runs on these
inputs, not proof for every input.

Privacy: the hook keeps arguments only for an allowlist of events (tools/mcp_trace_boot.py lists them), never an
environment variable's value; every path is written with <repo> for the server's folder, <boot> for the folder of
the boot script, <python> for Python's standard library and ~ for the home folder; every saved file is checked for
the home folder, the account name, the temporary folder and secret-looking environment values before the run ends.

Usage (from the repo root):
  python3 tools/mcp_runtime_trace.py record          every run, saved in js3/mcp/runtime/<UTC time>/
  python3 tools/mcp_runtime_trace.py check FOLDER    every run again in a temporary folder, compared with FOLDER: the
                                                     same event summaries and the same answers, or each difference
Exit code: 0 when every run ran (record) or everything is as saved (check), 1 when not, 2 when nothing could run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
BOOT = TOOLS / "mcp_trace_boot.py"
RUNTIME = REPO / "js3" / "mcp" / "runtime"
OWN_SERVER = "job_agent/mcp_server.py"
OTHER_SERVER = "js3/mcp/other-server/main.py"
EVALUATED = "a54c424"  # the commit EVALUATION-OWN.md evaluated
RECORDED = "js3/mcp/transcripts/2026-11-21T084407Z-own-client.jsonl"  # our client's run of that commit, 2026-11-21
TRANSCRIPT = "js3/mcp/transcripts/runtime-trace-own-b.jsonl"  # run own-b's --transcript; moved into the evidence
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
NO_NETWORK = "(version 1)(allow default)(deny network*)"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = _load("mcp_client", TOOLS / "mcp_client.py")
boot = _load("mcp_trace_boot", BOOT)  # the same event lists the hook uses

RUNS = (
    {"label": "own-a", "server": "own", "tree": "current", "traced": True, "transcript": False, "sandbox": False,
     "about": "our server, traced, without --transcript"},
    {"label": "own-b", "server": "own", "tree": "current", "traced": True, "transcript": True, "sandbox": False,
     "about": "our server, traced, with --transcript"},
    {"label": "own-c", "server": "own", "tree": "current", "traced": True, "transcript": False, "sandbox": True,
     "about": "our server, traced, the network denied by sandbox-exec"},
    {"label": "own-d", "server": "own", "tree": EVALUATED, "traced": True, "transcript": False, "sandbox": False,
     "about": "our server at a54c424 (the evaluated commit), traced"},
    {"label": "own-plain", "server": "own", "tree": "current", "traced": False, "transcript": False, "sandbox": False,
     "about": "our server, not traced (the control)"},
    {"label": "other-a", "server": "other", "tree": "current", "traced": True, "transcript": False, "sandbox": False,
     "about": "the lesson 8 reference server, traced"},
    {"label": "other-c", "server": "other", "tree": "current", "traced": True, "transcript": False, "sandbox": True,
     "about": "the lesson 8 reference server, traced, the network denied by sandbox-exec"},
    {"label": "other-plain", "server": "other", "tree": "current", "traced": False, "transcript": False,
     "sandbox": False, "about": "the lesson 8 reference server, not traced (the control)"},
)
COMPARISONS = (
    {"name": "c", "about": "the network denied by sandbox-exec, against the same traced run with the network allowed",
     "pairs": (("own-c", "own-a"), ("other-c", "other-a")), "summaries": True},
    {"name": "d", "about": "our server at a54c424 (the evaluated commit) against the current server, and against our "
                           "client's run of a54c424 recorded on 2026-11-21",
     "pairs": (("own-d", "own-a"), ("own-d", RECORDED)), "summaries": True},
    {"name": "plain", "about": "each traced run against the same server not traced",
     "pairs": (("own-a", "own-plain"), ("other-a", "other-plain")), "summaries": False},
)

# Modules that can reach a network or start a process: tests/test_network_door.py's list, the C modules under them,
# and the process modules. Each name also covers its submodules ("http" covers http.client).
NETWORK_OR_PROCESS = ("socket", "_socket", "ssl", "_ssl", "select", "selectors", "http", "urllib.request",
                      "urllib.error", "ftplib", "imaplib", "nntplib", "poplib", "smtplib", "telnetlib", "xmlrpc",
                      "socketserver", "asyncio", "webbrowser", "subprocess", "_posixsubprocess", "multiprocessing",
                      "_multiprocessing", "concurrent.futures.process", "pty", "ctypes", "_ctypes", "requests",
                      "httpx", "urllib3", "aiohttp")
NETWORK_SENDS = {"http.client.send", "ftplib.sendcmd", "imaplib.send", "nntplib.putline", "poplib.putline",
                 "smtplib.send", "telnetlib.Telnet.write"}
# Python loads a module's code either by compiling its source or by unmarshalling its cached bytecode; which one
# depends on whether a cache exists, so the two counts are kept as one.
CODE_LOADING = {"compile", "marshal.loads"}
CATEGORIES = (
    ("python", "Python's own files (standard library and its bytecode caches)"),
    ("code", "the server's code"),
    ("filter", "FILTER.md"),
    ("persona", "persona/ (the fictional persona)"),
    ("runs", "runs/ (the saved board answers)"),
    ("repo", "anything else in the repo"),
    ("launcher", "the boot script"),
    ("descriptor", "an open file descriptor whose path was not found"),
    ("outside", "anything else"),
)
REPO_PARTS = (("FILTER.md", "filter"), ("job_agent", "code"), ("js3/mcp/other-server", "code"),
              ("runs", "runs"), ("persona", "persona"))
PYC = re.compile(r"^(?P<dir>.*)/__pycache__/(?P<name>[^/]+?)\.[^/.]+(?:\.opt-[12])?\.pyc$")
WRITE_FLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")
FLAG_NAMES = ("O_APPEND", "O_CREAT", "O_TRUNC", "O_EXCL", "O_NOFOLLOW", "O_CLOEXEC", "O_NONBLOCK", "O_SYNC",
              "O_DSYNC", "O_DIRECTORY", "O_NOCTTY", "O_SHLOCK", "O_EXLOCK", "O_SYMLINK", "O_EVTONLY")
SECRET_NAME = re.compile(r"(?i)(key|token|secret|pass|auth|cookie|session|credential)")


# Reading the record.

def is_write(mode, flags) -> bool:
    """An open is a write when its mode has w, a, x or +, or its flags ask to write, create, truncate or append."""
    if isinstance(mode, str) and any(ch in mode for ch in "wax+"):
        return True
    if isinstance(flags, int):
        bits = 0
        for name in WRITE_FLAGS:
            bits |= getattr(os, name, 0)
        return bool(flags & bits)
    return False


def flag_names(flags) -> list:
    if not isinstance(flags, int):
        return []
    names = [{0: "O_RDONLY", 1: "O_WRONLY", 2: "O_RDWR"}.get(flags & 3, "O_ACCMODE")]
    known = 3
    for name in FLAG_NAMES:
        bit = getattr(os, name, 0)
        if bit and flags & bit == bit and not known & bit == bit:
            names.append(name)
            known |= bit
    if flags & ~known:
        names.append(hex(flags & ~known))
    return names


def kind(event: str) -> str:
    if event in ("open", "import"):
        return event
    if event in boot.FILE_CHANGES or event.startswith(("shutil.", "syslog.")):
        return "change"
    if event in boot.LISTINGS:
        return "listing"
    if event.startswith("socket."):
        return "socket"
    if event in boot.CONNECTS or event in NETWORK_SENDS or event == "urllib.Request":
        return "network"
    if event in boot.PROCESSES:
        return "process"
    if event.startswith("ctypes."):
        return "ctypes"
    return "other"


def watched(module: str) -> bool:
    return any(module == name or module.startswith(name + ".") for name in NETWORK_OR_PROCESS)


def _forms(path) -> list:
    """A folder as given and as resolved, the longer first."""
    if not path:
        return []
    return sorted({str(path), os.path.realpath(str(path))}, key=len, reverse=True)


def _under(path: str, prefixes) -> str:
    """The part of path below one of prefixes ("" for the prefix itself), or None."""
    for prefix in prefixes:
        if path == prefix:
            return ""
        if path.startswith(prefix.rstrip("/") + "/"):
            return path[len(prefix.rstrip("/")) + 1:]
    return None


class Where:
    """Where a recorded path lies (its category) and how it is shown (with placeholders, never the home folder)."""

    def __init__(self, start: dict, tree: Path):
        self.cwd = start.get("cwd") or str(tree)
        self.tree = _forms(tree)
        self.boot = _forms(BOOT.parent)  # shown as <boot>: the folder itself, and the boot file
        self.boot_file = _forms(BOOT)
        self.stdlib = _forms(start.get("stdlib"))
        self.python = sorted({form for d in (start.get("python_dirs") or []) for form in _forms(d)},
                             key=len, reverse=True)
        self.pycache_prefix = start.get("pycache_prefix")
        self.home = _forms(Path.home())

    def absolute(self, path):
        if not isinstance(path, str):
            return path
        if path == "<fd>":
            return path
        return os.path.normpath(path if os.path.isabs(path) else os.path.join(self.cwd, path))

    def source(self, path):
        """(the module source for a bytecode cache file, True), or (path, False)."""
        if not isinstance(path, str) or not path.endswith(".pyc"):
            return path, False
        prefix = (self.pycache_prefix or "").rstrip("/")
        if prefix and path.startswith(prefix + "/"):
            folder, name = os.path.split(path[len(prefix):])
            return os.path.join(folder, name.split(".")[0] + ".py"), True
        match = PYC.match(path)
        if match:
            return match.group("dir") + "/" + match.group("name") + ".py", True
        return path, False

    def category(self, path) -> str:
        if path == "<fd>" or not isinstance(path, str):
            return "descriptor"
        if path in self.boot_file:
            return "launcher"
        rel = _under(path, self.tree)
        if rel is not None:
            for part, name in REPO_PARTS:
                if rel == part or rel.startswith(part + "/"):
                    return name
            return "repo"
        if _under(path, self.stdlib) is not None or _under(path, self.python) is not None:
            return "python"
        return "outside"

    def shown(self, path):
        if not isinstance(path, str):
            return path
        if path in self.boot or path in self.boot_file:
            return "<boot>" + ("/" + BOOT.name if path in self.boot_file else "")
        for prefixes, label in ((self.tree, "<repo>"), (self.stdlib, "<python>"), (self.home, "~")):
            rest = _under(path, prefixes)
            if rest is not None:
                return label + ("/" + rest if rest else "")
        return scrub(path)


def scrub(text: str) -> str:
    """The home folder written as ~ anywhere in a text."""
    for home in _forms(Path.home()):
        if len(home) > 1:
            text = text.replace(home, "~")
    return text


def read_events(path: Path) -> list:
    events = []
    for line in Path(path).read_text(encoding="ascii", errors="replace").splitlines():
        if line.strip():
            try:
                events.append(json.loads(line))
            except ValueError:
                events.append({"n": "_unreadable", "p": "?"})
    return events


def summarize(raw: dict, tree: Path, extra: dict = None) -> dict:
    """The event summary of one run: raw maps each session's name to its event log, in session order."""
    phases = ("server", "exit")
    reads = {p: {name: Counter() for name, _ in CATEGORIES} for p in phases}
    code_files = {p: {"python": set(), "code": set(), "launcher": set()} for p in phases}
    listings = {p: Counter() for p in phases}
    writes, changes, sockets, network, processes, ctypes = Counter(), Counter(), Counter(), Counter(), Counter(), \
        Counter()
    other = {p: Counter() for p in ("launcher",) + phases}
    launcher = {"modules": [], "python_files": set(), "listings": Counter(), "other_reads": Counter()}
    startup, loaded, not_loaded, at_exit, seen_modules = None, [], [], [], set()
    per_session, hook_errors, unreadable, python, missing = {}, 0, 0, None, []
    for session, path in raw.items():
        if not Path(path).exists():
            missing.append(session)  # nothing was recorded, so nothing may be claimed for this session
            continue
        events = read_events(path)
        start = next((e for e in events if e.get("n") == "_start"), {})
        python = python or start.get("python")
        where = Where(start, tree)
        counts = Counter()
        imports = {"launcher": [], "server": [], "exit": []}
        end, previous_open = None, None
        for e in events:
            name, phase = e.get("n"), e.get("p")
            if name == "open":
                same = (e.get("path"), e.get("flags"))
                if e.get("mode") is None and previous_open == same:
                    previous_open = None  # Python 3.9's pathlib: io.open's event, then its opener's os.open, one open
                    continue
                previous_open = same if isinstance(e.get("mode"), str) else None
            if name == "_modules":
                if phase == "startup":
                    startup = startup if startup is not None else list(e["m"])
                    seen_modules.update(e["m"])
                else:
                    end = set(e["m"])
                    seen_modules.update(e["m"])
                continue
            if name in ("_start", "_phase"):
                continue
            if name == "_unreadable":
                unreadable += 1
                continue
            hook_errors += 1 if e.get("hook_error") else 0
            k = kind(name)
            if k == "import":
                imports.setdefault(phase, []).append(e.get("m"))
                seen_modules.add(e.get("m"))
                continue
            if phase == "launcher":
                if k == "open" and not is_write(e.get("mode"), e.get("flags")):
                    source, _ = where.source(where.absolute(e.get("path")))
                    if where.category(source) == "python":
                        launcher["python_files"].add(where.shown(source))
                    else:
                        launcher["other_reads"][where.shown(source)] += 1
                    continue
                if k == "listing":
                    for p in e.get("paths") or []:
                        if p is not None:
                            launcher["listings"][where.shown(where.absolute(p))] += 1
                    continue
                if k == "other":
                    other["launcher"][_event_key(name)] += 1
                    continue
                # anything else in the launcher's own phase is counted with the server's, so it can never hide
            bucket = phase if phase in phases else "server"  # a launcher-phase write is listed, never dropped
            if k == "open":
                path_ = where.absolute(e.get("path"))
                if is_write(e.get("mode"), e.get("flags")):
                    writes[(where.shown(path_), e.get("mode"), tuple(flag_names(e.get("flags"))),
                            bool(e.get("fd")), phase)] += 1
                    counts["writes"] += 1
                    continue
                source, _ = where.source(path_)
                category = where.category(source)
                if category in code_files[bucket]:  # module code: which files, not how many opens (see README)
                    code_files[bucket][category].add(where.shown(source))
                else:
                    reads[bucket][category][where.shown(source)] += 1
                    counts["data_reads"] += 1
            elif k == "listing":
                for p in e.get("paths") or [None]:
                    target = where.absolute(p if p is not None else where.cwd)
                    if isinstance(target, str) and "*" in os.path.basename(target):
                        continue  # a glob's pattern; its folder is the listing
                    listings[bucket][(where.category(target), where.shown(target), name)] += 1
                counts["listings"] += 1
            elif k == "change":
                shown = tuple(where.shown(where.absolute(p)) for p in (e.get("paths") or []))
                changes[(name, shown, phase)] += 1
                counts["writes"] += 1
            elif k == "socket":
                sockets[(name, json.dumps({x: e[x] for x in ("family", "type", "proto", "address") if x in e}))] += 1
                counts["sockets"] += 1
            elif k == "network":
                network[(name, json.dumps({x: e[x] for x in ("address", "scheme", "host") if x in e}))] += 1
                counts["network"] += 1
            elif k == "process":
                processes[(name, e.get("program"))] += 1
                counts["processes"] += 1
            elif k == "ctypes":
                ctypes[name] += 1
                counts["ctypes"] += 1
            else:
                other[bucket][_event_key(name)] += 1
        end = end or set()
        for module in _unique(imports.get("launcher", [])):
            if module in end and module not in launcher["modules"]:
                launcher["modules"].append(module)
        for module in _unique(imports.get("server", [])):
            if module in end and module not in (startup or []):
                counts["modules_loaded"] += 1
                if module not in loaded:
                    loaded.append(module)
        for module in _unique(imports.get("launcher", []) + imports.get("server", [])):
            if module not in end and module not in not_loaded:
                not_loaded.append(module)
        for module in _unique(imports.get("exit", [])):
            if module not in at_exit:
                at_exit.append(module)
        per_session[session] = {key: counts.get(key, 0) for key in (
            "data_reads", "listings", "writes", "sockets", "network", "processes", "ctypes", "modules_loaded")}
    summary = {
        "python": python,
        "sessions": list(raw),
        "writes": [{"path": p, "mode": m, "flags": list(f), "through_descriptor": d, "phase": ph, "count": c}
                   for (p, m, f, d, ph), c in sorted(writes.items(), key=lambda i: (i[0][0], i[0][3], str(i[0])))],
        "file_changes": [{"event": n, "paths": list(p), "phase": ph, "count": c}
                         for (n, p, ph), c in sorted(changes.items(), key=str)],
        "sockets": [dict(event=n, count=c, **json.loads(a)) for (n, a), c in sorted(sockets.items())],
        "network": [dict(event=n, count=c, **json.loads(a)) for (n, a), c in sorted(network.items())],
        "processes": [{"event": n, "program": p, "count": c} for (n, p), c in sorted(processes.items(), key=str)],
        "ctypes": dict(sorted(ctypes.items())),
        "reads": {phase: _reads(reads[phase], code_files[phase], listings[phase]) for phase in phases},
        "modules": {
            "before_the_hook": startup or [],
            "launcher": launcher["modules"],
            "server": loaded,
            "at_exit": at_exit,
            "not_loaded": not_loaded,
            "network_or_process": sorted(m for m in seen_modules if isinstance(m, str) and watched(m)),
        },
        "launcher": {"python_files": len(launcher["python_files"]),
                     "listings": dict(sorted(launcher["listings"].items())),
                     "other_reads": dict(sorted(launcher["other_reads"].items()))},
        "per_session": per_session,
        "other_events": {phase: dict(sorted(c.items())) for phase, c in other.items()},
        "hook_errors": hook_errors,
        "unreadable_lines": unreadable,
        "sessions_without_a_record": missing,
    }
    if extra:
        summary = dict(extra, **summary)
    return summary


def _event_key(name: str) -> str:
    return "compile or marshal.loads" if name in CODE_LOADING else name


def _unique(items) -> list:
    out = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _reads(counters: dict, code: dict, listings: Counter) -> dict:
    out = {}
    for name, _ in CATEGORIES:
        entry = {}
        if name in code and code[name]:
            entry["files"] = sorted(code[name])
        if counters[name]:
            entry["opens"] = dict(sorted(counters[name].items()))
        shown = {f"{path} ({event})": c for (category, path, event), c in sorted(listings.items())
                 if category == name}
        if shown:
            entry["listings"] = shown
        if entry:
            out[name] = entry
    return out


# One run.

def answers(log: list) -> dict:
    """Each session's lines from the server (step, text) and its exit code, from a client record; times left out."""
    out = {}
    for e in log:
        if e.get("type") == "session":
            out[e["session"]] = {"lines": [], "exit_code": None}
        elif e.get("type") == "line" and e.get("dir") == "server->client" and e.get("session") in out:
            out[e["session"]]["lines"].append([e["step"], e["text"]])
        elif e.get("type") == "session_end" and e.get("session") in out:
            out[e["session"]]["exit_code"] = e.get("exit_code")
    return out


def digest(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def commands(spec: dict, tree: Path, python: str, log_path: Path = None) -> list:
    """The command one session runs: the server's own command, or the boot in front of it."""
    if spec["server"] == "own":
        extra = ["--transcript", TRANSCRIPT] if spec["transcript"] else []
        command = ([python, "-B", str(BOOT), str(log_path), "-m", "job_agent.mcp_server"] if spec["traced"] else
                   [python, "-B", "-m", "job_agent.mcp_server"]) + extra
    else:
        command = ([python, "-B", "-I", str(BOOT), str(log_path), OTHER_SERVER, "--stdio"] if spec["traced"] else
                   [python, "-B", "-I", OTHER_SERVER, "--stdio"])
    return [SANDBOX_EXEC, "-p", NO_NETWORK] + command if spec["sandbox"] else command


def shown_command(command: list, python: str) -> list:
    out = []
    for part in command:
        if part == python:
            out.append("python3")
        elif part == str(BOOT):
            out.append("tools/mcp_trace_boot.py")
        elif part.endswith(".events.jsonl"):
            out.append("<event log>")
        else:
            out.append(part)
    return out


def execute(spec: dict, tree: Path, work: Path, out: Path, python: str) -> dict:
    """Run every session of one run; write <label>.client.jsonl (and the summary files for a traced run) into out."""
    label = spec["label"]
    plan = client.own_plan() if spec["server"] == "own" else client.other_plan()
    transcript = tree / TRANSCRIPT if spec["transcript"] else None
    if transcript is not None and transcript.exists():
        raise FileExistsError(f"{TRANSCRIPT} already exists; this run never appends to or removes a file it did "
                              "not make (if an interrupted run left it, look at it and remove it by hand)")
    version = python_version(python)
    log = [{"type": "run", "label": label, "about": spec["about"], "server": spec["server"],
            "tree": "the repo at " + EVALUATED + " (git archive)" if spec["tree"] == EVALUATED else "the repo",
            "traced": spec["traced"], "sandbox": NO_NETWORK if spec["sandbox"] else None,
            "command": shown_command(commands(spec, tree, python, work / "x.events.jsonl"), python),
            "python": version, "cwd": "the repo root", "env": client.SERVER_ENV, "started_at": client.now(),
            "client": "tools/mcp_client.py (own_plan or other_plan, run_session)",
            "recorded_by": "tools/mcp_runtime_trace.py"}]
    raw, outcomes = {}, []
    for session_plan in plan:
        log_path = work / f"{label}-{session_plan['name']}.events.jsonl"
        command = commands(spec, tree, python, log_path)
        outcomes += client.run_session(session_plan, command, tree, dict(client.SERVER_ENV), log)
        if spec["traced"]:
            raw[session_plan["name"]] = log_path
    matched = sum(1 for o in outcomes if o["match"])
    log.append({"type": "summary", "steps": len(outcomes), "matched": matched, "finished_at": client.now()})
    for entry in log:
        if entry.get("type") == "session_end":  # the client wrote the server's folder as <repo>; the boot's too
            for form in _forms(BOOT.parent):
                entry["stderr"] = entry["stderr"].replace(form, "<boot>")
            entry["stderr"] = scrub(entry["stderr"])
    _write_jsonl(out / f"{label}.client.jsonl", log)
    got = answers(log)
    result = {"spec": spec, "log": log, "answers": got, "steps": len(outcomes), "matched": matched,
              "python": version, "files": [f"{label}.client.jsonl"]}
    extra = {"run": label, "about": spec["about"], "tree": log[0]["tree"],
             "server_file": OWN_SERVER if spec["server"] == "own" else OTHER_SERVER,
             "server_sha256": sha256_file(tree / (OWN_SERVER if spec["server"] == "own" else OTHER_SERVER)),
             "sandbox": NO_NETWORK if spec["sandbox"] else None, "command": log[0]["command"],
             "client": {"steps": len(outcomes), "as_the_plan_expects": matched},
             "answers": {"lines_from_the_server": sum(len(s["lines"]) for s in got.values()),
                         "exit_codes": {name: s["exit_code"] for name, s in got.items()}, "sha256": digest(got)}}
    if spec["server"] == "own":
        extra["filter_md_sha256"] = sha256_file(tree / "FILTER.md")
    if transcript is not None:
        extra["server_transcript"] = _take_transcript(transcript, log, out / f"{label}.server.jsonl")
        result["files"].append(f"{label}.server.jsonl")
    if spec["traced"]:
        summary = summarize(raw, tree, extra)
        _write_json(out / f"{label}.summary.json", summary)
        (out / f"{label}.summary.md").write_text(render_summary(summary), encoding="utf-8")
        result["summary"] = summary
        result["files"] += [f"{label}.summary.json", f"{label}.summary.md"]
    else:
        result["summary"] = extra
    return result


def _take_transcript(path: Path, log: list, keep: Path) -> dict:
    """The server's own record of run own-b: checked against the client's, then moved into the evidence folder."""
    comparison = client.compare_with_server_log(log, path)
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    keep.write_bytes(path.read_bytes())
    path.unlink()
    timeless = [{k: v for k, v in e.items() if k != "at"} for e in entries]
    return {"written_as": TRANSCRIPT, "kept_as": keep.name, "entries": len(entries),
            "sessions": comparison.get("sessions"), "lines": comparison.get("lines"),
            "ends": [e.get("reason") for e in entries if e.get("event") == "end"],
            "matches_the_client_record": comparison["match"], "details": comparison["details"],
            "sha256_without_times": digest(timeless)}


def export(commit: str, dest: Path, repo: Path = REPO) -> str:
    """git archive COMMIT | tar -x -C DEST; returns the full commit hash."""
    full = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", commit + "^{commit}"],
                          capture_output=True, text=True, check=True).stdout.strip()
    dest.mkdir(parents=True)
    archive = subprocess.Popen(["git", "-C", str(repo), "archive", full], stdout=subprocess.PIPE)
    untar = subprocess.run(["tar", "-x", "-C", str(dest)], stdin=archive.stdout, capture_output=True)
    archive.stdout.close()
    if archive.wait() != 0 or untar.returncode != 0:
        raise RuntimeError(f"git archive {commit} | tar -x failed: {untar.stderr.decode('utf-8', 'replace')}")
    return full


def sandbox_check(python: str) -> dict:
    """Whether sandbox-exec runs here, and whether its profile refuses a connection (a planted one, to 127.0.0.1)."""
    if not Path(SANDBOX_EXEC).exists():
        return {"available": False, "error": f"{SANDBOX_EXEC} does not exist"}
    plain = subprocess.run([SANDBOX_EXEC, "-p", NO_NETWORK, "/usr/bin/true"], capture_output=True, text=True)
    if plain.returncode != 0:
        return {"available": False, "error": f"exit {plain.returncode}: {plain.stderr.strip()}"}
    planted = ("import socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\ntry:\n"
               "    s.connect(('127.0.0.1', 9))\n    print('connected')\nexcept OSError as exc:\n"
               "    print(type(exc).__name__, exc.errno)\nfinally:\n    s.close()\n")
    done = subprocess.run([SANDBOX_EXEC, "-p", NO_NETWORK, python, "-B", "-I", "-c", planted], capture_output=True,
                          text=True, env=dict(client.SERVER_ENV))
    return {"available": True, "profile": NO_NETWORK,
            "planted_connect_to_127.0.0.1_port_9": (done.stdout.strip() or done.stderr.strip()[-200:])}


# Comparing runs.

MISSING = "(absent)"


def field_diff(a, b, path: str = "$") -> list:
    """Every JSON path where a and b differ, with both values; a string holding JSON is compared as JSON."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b), key=str):
            if key not in a or key not in b:
                out.append((f"{path}.{key}", a.get(key, MISSING), b.get(key, MISSING)))
            else:
                out += field_diff(a[key], b[key], f"{path}.{key}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(f"{path} (length)", len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += field_diff(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, str) and isinstance(b, str) and a != b:
        x, y = _json(a), _json(b)
        if isinstance(x, (dict, list)) and isinstance(y, (dict, list)):
            return field_diff(x, y, path + " (its JSON)")
    return [] if a == b else [(path, a, b)]


def _json(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError, RecursionError):
        return None


def _short(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 160 else text[:160] + f"... ({len(text):,} characters)"


def answer_differences(left: dict, right: dict) -> list:
    out = []
    for session in _unique(list(left) + list(right)):
        a, b = left.get(session), right.get(session)
        if a is None or b is None:
            out.append({"session": session, "step": None, "path": "the session", "left": "present" if a else MISSING,
                        "right": "present" if b else MISSING})
            continue
        if a["exit_code"] != b["exit_code"]:
            out.append({"session": session, "step": None, "path": "exit code", "left": a["exit_code"],
                        "right": b["exit_code"]})
        for i in range(max(len(a["lines"]), len(b["lines"]))):
            x = a["lines"][i] if i < len(a["lines"]) else None
            y = b["lines"][i] if i < len(b["lines"]) else None
            if x == y:
                continue
            if x is None or y is None or x[0] != y[0]:
                out.append({"session": session, "step": (x or y)[0], "path": f"line {i + 1}",
                            "left": _short(x[1]) if x else MISSING, "right": _short(y[1]) if y else MISSING})
                continue
            left_message, right_message = _json(x[1]), _json(y[1])
            rid = left_message.get("id") if isinstance(left_message, dict) else None
            for where, p, q in field_diff(x[1] if left_message is None else left_message,
                                          y[1] if right_message is None else right_message):
                out.append({"session": session, "step": x[0], "id": rid, "path": where, "left": _short(p),
                            "right": _short(q)})
    return out


IDENTITY = ("run", "about", "sandbox", "command", "tree", "answers", "client", "server_transcript")


def summary_differences(left: dict, right: dict) -> list:
    def strip(summary):
        return {k: v for k, v in summary.items() if k not in IDENTITY}
    return [{"path": p, "left": _short(x), "right": _short(y)} for p, x, y in field_diff(strip(left), strip(right))]


def compare(results: dict, repo: Path = REPO) -> list:
    out = []
    for comparison in COMPARISONS:
        pairs = []
        for left, right in comparison["pairs"]:
            a = results.get(left)
            if right in results:
                b, b_name = results[right], right
                b_answers, b_summary = b["answers"], b.get("summary")
            elif right == RECORDED and (repo / RECORDED).exists():
                recorded = [json.loads(line) for line in (repo / RECORDED).read_text(encoding="utf-8").splitlines()
                            if line]
                b_name, b_answers, b_summary = RECORDED, answers(recorded), None
            else:
                pairs.append({"left": left, "right": right, "skipped": "not run"})
                continue
            if a is None:
                pairs.append({"left": left, "right": b_name, "skipped": "not run"})
                continue
            differences = answer_differences(a["answers"], b_answers)
            pair = {"left": left, "right": b_name, "answers_equal": not differences,
                    "left_sha256": digest(a["answers"]), "right_sha256": digest(b_answers),
                    "answer_differences": differences}
            if comparison["summaries"] and b_summary is not None and a["spec"]["traced"]:
                summary_diff = summary_differences(a["summary"], b_summary)
                pair["summaries_equal"] = not summary_diff
                pair["summary_differences"] = summary_diff
            if comparison["name"] == "plain":
                pair["stderr_last_lines"] = _stderr_tails(a["log"], b["log"])
            pairs.append(pair)
        out.append({"name": comparison["name"], "about": comparison["about"], "pairs": pairs})
    return out


def _stderr_tails(left: list, right: list) -> dict:
    """The last stderr line of each session (the exception, if one ended it), and whether the two runs agree."""
    def tails(log):
        return {e["session"]: (e["stderr"].strip().splitlines() or [""])[-1] for e in log
                if e.get("type") == "session_end"}
    a, b = tails(left), tails(right)
    return {"equal": a == b, "left": a, "right": b}


# The files.

def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, entries: list) -> None:
    with open(path, "x", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def render_summary(s: dict) -> str:
    title = {OWN_SERVER: "our server", OTHER_SERVER: "the lesson 8 reference server"}.get(s["server_file"],
                                                                                         "the traced program")
    reads = s["reads"]["server"]
    modules = s["modules"]
    lines = [f"# Runtime trace `{s['run']}`: {s['about']}", "",
             f"{title.capitalize()}: `{s['server_file']}` in {s['tree']} (SHA-256 `{s['server_sha256']}`), Python "
             f"{s['python']}, the sessions of `tools/mcp_client.py` ({', '.join(s['sessions'])}), each on a fresh "
             f"process. Command: `{' '.join(s['command'])}`." +
             (f" FILTER.md SHA-256 `{s['filter_md_sha256']}`." if s.get("filter_md_sha256") else ""),
             "", "What the audit hook saw while the server ran and as its process ended (after the boot had "
                 "installed the hook and imported runpy). Evidence type: executed on a fixture. It shows what "
                 "happened in these sessions on these inputs, not every possible input.", "",
             "| What | Seen |", "|---|---|",
             f"| Event logs | {len(s['sessions']) - len(s['sessions_without_a_record'])} of {len(s['sessions'])} "
             f"sessions recorded; {s['hook_errors']} hook errors; {s['unreadable_lines']} unreadable lines |",
             f"| Answers | {s['client']['as_the_plan_expects']} of {s['client']['steps']} as the client's plan "
             f"expects; {s['answers']['lines_from_the_server']} lines from the server; exit codes "
             f"{', '.join(f'{k} {v}' for k, v in s['answers']['exit_codes'].items())} |",
             f"| Files opened to write, or changed | {_writes_text(s) or 'none'} |",
             f"| Sockets and network calls | {_events_text(s['sockets'] + s['network']) or 'none'} |",
             f"| Processes started or signalled | {_events_text(s['processes']) or 'none'} |",
             f"| ctypes | {', '.join(f'{k} ({v})' for k, v in s['ctypes'].items()) or 'none'} |",
             f"| Network or process modules loaded at any point ({', '.join(NETWORK_OR_PROCESS[:4])}, "
             f"http, subprocess, ...) | {', '.join(modules['network_or_process']) or 'none'} |"]
    for name, label in CATEGORIES:
        entry = reads.get(name)
        if not entry:
            if name in ("python", "code", "filter", "persona", "runs"):
                lines.append(f"| Read: {label} | none |")
            continue
        lines.append(f"| Read: {label} | {_read_text(name, entry)} |")
    lines += [f"| Modules the server's run loaded | {len(modules['server'])}: {', '.join(modules['server'])} |",
              f"| Import attempts that loaded nothing | {', '.join(modules['not_loaded']) or 'none'} |",
              f"| Modules already loaded before the hook | {len(modules['before_the_hook'])} (by Python's own "
              "startup; the boot imports nothing more) |",
              f"| The launcher (boot and runpy) | {len(modules['launcher'])} modules "
              f"({', '.join(modules['launcher'])}), {s['launcher']['python_files']} files of Python's own read, "
              f"listings {', '.join(s['launcher']['listings']) or 'none'} |"]
    exit_reads = s["reads"]["exit"]
    if exit_reads:
        lines.append("| As the process ended | " + "; ".join(f"{dict(CATEGORIES)[n]}: {_read_text(n, e)}"
                                                         for n, e in exit_reads.items()) + " |")
    if s.get("server_transcript"):
        t = s["server_transcript"]
        lines.append(f"| The server's own transcript | {t['entries']} entries, {t['sessions']} sessions, ends "
                     f"{', '.join(sorted(set(t['ends'])))}; matches the client's record line for line: "
                     f"{'yes' if t['matches_the_client_record'] else 'NO'}; written as `{t['written_as']}`, kept "
                     f"here as `{t['kept_as']}` |")
    lines += ["", "## Per session", "",
              "| Session | data reads | listings | writes | sockets | network | processes | ctypes | modules loaded |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, c in s["per_session"].items():
        lines.append(f"| {name} | {c['data_reads']} | {c['listings']} | {c['writes']} | {c['sockets']} | "
                     f"{c['network']} | {c['processes']} | {c['ctypes']} | {c['modules_loaded']} |")
    lines += ["", "## Every other event Python reported, with its count", ""]
    for phase, counts in s["other_events"].items():
        if counts:
            lines.append(f"- {phase}: " + ", ".join(f"`{k}` {v}" for k, v in counts.items()))
    lines += ["", f"Hook errors: {s['hook_errors']}. Unreadable lines in the event logs: {s['unreadable_lines']}. "
                  f"Sessions with no event log: {', '.join(s['sessions_without_a_record']) or 'none'}. Opens are "
                  "open calls: Python 3.9's pathlib raises two events for one open (io.open's, then os.open's), "
                  "counted once here. The full lists (every file, listing and module) are in "
                  f"`{s['run']}.summary.json`; every line of the sessions is in `{s['run']}.client.jsonl`."]
    return "\n".join(lines) + "\n"


def _writes_text(s: dict) -> str:
    parts = [f"`{w['path']}`: {w['count']} open(s), mode {w['mode']!r}, {'+'.join(w['flags'])}"
             + (" (through the descriptor just opened)" if w["through_descriptor"] else "") for w in s["writes"]]
    parts += [f"{c['event']} {', '.join(c['paths'])} ({c['count']})" for c in s["file_changes"]]
    return "; ".join(parts)


def _cell(value) -> str:
    """A value inside a Markdown table cell: a | would end the cell."""
    return str(value).replace("|", "\\|")


def _events_text(items: list) -> str:
    return "; ".join(", ".join(f"{k} {v}" for k, v in item.items()) for item in items)


def _read_text(name: str, entry: dict) -> str:
    parts = []
    if "files" in entry:
        files = entry["files"]
        parts.append(f"{len(files)} files" + ("" if name == "python" else ": " + ", ".join(f"`{f}`" for f in files)))
    if "opens" in entry:
        opens = entry["opens"]
        total = sum(opens.values())
        if len(opens) <= 4:
            parts.append(", ".join(f"`{p}` ({c})" for p, c in opens.items()))
        else:
            parts.append(f"{total} opens of {len(opens)} files")
    if "listings" in entry:
        parts.append(f"{sum(entry['listings'].values())} directory listings")
    return "; ".join(parts)


def render_comparisons(comparisons: list) -> dict:
    """One Markdown page per comparison."""
    pages = {}
    for comparison in comparisons:
        lines = [f"# Comparison `{comparison['name']}`: {comparison['about']}", "",
                 "Each answer is compared line by line, session by session (times left out); where two lines "
                 "differ, every JSON field that differs is listed, and a tool result's text is compared as the JSON "
                 "it holds.", ""]
        for pair in comparison["pairs"]:
            lines += [f"## `{pair['left']}` against `{pair['right']}`", ""]
            if pair.get("skipped"):
                lines += [f"Skipped: {pair['skipped']}.", ""]
                continue
            lines.append(f"- Answers: **{'the same' if pair['answers_equal'] else 'different'}** (SHA-256 of all "
                         f"answers without times: `{pair['left_sha256'][:16]}...` and "
                         f"`{pair['right_sha256'][:16]}...`)")
            if "summaries_equal" in pair:
                lines.append(f"- Event summaries: **{'the same' if pair['summaries_equal'] else 'different'}**"
                             " (leaving out the run's name, command and sandbox setting)")
            if "stderr_last_lines" in pair:
                tails = pair["stderr_last_lines"]
                same = "the same" if tails["equal"] else "different"
                lines.append(f"- The last line of each session's stderr: **{same}**"
                             + "".join(f"; {k}: `{v}`" for k, v in tails["left"].items() if v))
            if pair["answer_differences"]:
                lines += ["", "| Session | Step | id | Field | " + pair["left"] + " | " + pair["right"] + " |",
                          "|---|---:|---:|---|---|---|"]
                for d in pair["answer_differences"]:
                    lines.append(f"| {d['session']} | {d['step']} | {d.get('id')} | `{_cell(d['path'])}` | "
                                 f"`{_cell(d['left'])}` | `{_cell(d['right'])}` |")
            if pair.get("summary_differences"):
                lines += ["", "Event summary differences:", "", "| Field | " + pair["left"] + " | " + pair["right"]
                          + " |", "|---|---|---|"]
                for d in pair["summary_differences"]:
                    lines.append(f"| `{_cell(d['path'])}` | `{_cell(d['left'])}` | `{_cell(d['right'])}` |")
            lines.append("")
        pages[comparison["name"]] = "\n".join(lines).rstrip("\n") + "\n"
    return pages


def privacy_problems(folder: Path, extra_forbidden=()) -> list:
    """Anything private in the saved files: the home folder, the account name, the temporary folder, or the value
    of an environment variable whose name looks secret."""
    forbidden = set(_forms(Path.home())) | set(_forms(tempfile.gettempdir())) | set(extra_forbidden)
    user = os.path.basename(str(Path.home()))
    if len(user) >= 5:
        forbidden.add(user)
    for name, value in os.environ.items():
        if SECRET_NAME.search(name) and len(value) >= 8:
            forbidden.add(value)
    problems = []
    for path in sorted(Path(folder).rglob("*")):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            for item in forbidden:
                if item and len(item) > 1 and item in text:
                    problems.append(f"{path.name}: holds a private string ({len(item)} characters)")
    return problems


def render_readme(manifest: dict) -> str:
    recorded = manifest["recorded_local"]
    lines = [f"# Runtime trace of the two MCP servers, {recorded[:10]}", "",
             f"Recorded with `{manifest['command']}` on {recorded} ({manifest['recorded_at']}), at commit "
             f"`{manifest['commit'][:7]}`, once per Python: "
             + ", ".join(f"{i['version']} (`{i['python']}`, in `{i['folder']}/`)" for i in manifest["interpreters"])
             + ". Tools: " + ", ".join(f"`{name}` (SHA-256 `{sha[:12]}...`)" for name, sha in
                                         manifest["tool_sha256"].items())
             + ". Each server ran with its code unchanged, under a Python audit hook (PEP 578) installed by "
             "`tools/mcp_trace_boot.py`, and was driven through the five sessions of `tools/mcp_client.py` (early, "
             "main, lifecycle, bytes, deep), each on a fresh process. Evidence type: executed on a fixture. These "
             "files show what happened in these runs on these inputs, not proof for every input; the source reading "
             "in the evaluations covers the code paths.", "",
             "## Re-check", "", "From the repo root:", "", "```bash",
             f"python3 tools/mcp_runtime_trace.py check js3/mcp/runtime/{manifest['folder']}", "```", "",
             "It runs every run again, with each Python named above that is still on this Mac, in a temporary "
             "folder, and compares each new event summary with the saved `*.summary.json` (they must be equal) and "
             "each run's answers with the saved ones (SHA-256 of every line from the server, without times). Times "
             "in the `*.jsonl` files differ from run to run; nothing else should."]
    for interpreter in manifest["interpreters"]:
        lines += ["", f"## Python {interpreter['version']} (`{interpreter['folder']}/`)", "",
                  "| Run | What | Answers as expected | Writes | Sockets and network | Processes | Network or "
                  "process modules loaded |", "|---|---|---|---|---|---|---|"]
        for run in interpreter["runs"]:
            if "skipped" in run:
                lines.append(f"| `{run['label']}` | {run['about']} | not run: {run['skipped']} | | | | |")
                continue
            lines.append(f"| `{run['label']}` | {run['about']} | {run['as_the_plan_expects']} of {run['steps']} | "
                         + " | ".join(run.get("seen", {}).get(k, "(not traced)") for k in
                                      ("writes", "sockets", "processes", "modules")) + " |")
        lines += [""] + [f"- {line}" for line in interpreter["comparison_lines"]]
        sandbox = interpreter["sandbox"]
        if sandbox.get("available"):
            lines.append(f"- The network block: `{SANDBOX_EXEC} -p '{NO_NETWORK}'` (deprecated on macOS, still "
                         "present). Before the c runs, the same profile refused a planted connection from this Python "
                         f"to 127.0.0.1 port 9: `{sandbox['planted_connect_to_127.0.0.1_port_9']}`. The claim it "
                         "supports is only that every answer with the network denied was the same as with it allowed.")
        else:
            lines.append(f"- sandbox-exec could not run: `{sandbox.get('error')}`; the c runs were skipped.")
    if manifest.get("across"):
        lines += ["", "## Across the Pythons (`compare-python.md`)", ""] + [f"- {line}" for line in manifest["across"]]
    lines += ["", "## Reading the files", "",
              "- `<repo>` is the folder the server ran in (for `own-d`, a temporary folder holding `git archive "
              f"{EVALUATED}`), `<boot>` the folder of `tools/mcp_trace_boot.py`, `<python>` that Python's standard "
              "library, `~` the home folder. No file here names this Mac's account.",
              f"- Run `own-b`'s `--transcript` file was written as `{TRANSCRIPT}` (in the one folder the server "
              "accepts), checked against the client's record and then, after the server had ended, moved by the "
              "tool into that Python's folder as `own-b.server.jsonl`.",
              "- A bytecode cache file (`__pycache__/*.pyc`) is shown as its module's source file, and Python's "
              "`compile` and `marshal.loads` counts are added up: which of the two Python uses depends on whether a "
              "cache exists, not on the server. For the same reason module files are listed, not counted.",
              "- The hook sees a call before the system answers it: an open of a file that does not exist (Python "
              "looking for a bytecode cache) is recorded as an attempt. A write would be recorded even if it failed.",
              "- The hook keeps arguments only for an allowlist of events (the boot's docstring): file paths, modes "
              "and flags, socket families and addresses, the file name of a started program, module names. Every "
              "other event is kept as its name and a count; no environment value is ever kept.",
              "- What the hook cannot see: work done in C that raises no audit event. That covers Python's own "
              "reads before the hook was installed, the system loader opening a C extension module (such as "
              "`_json` or `zlib`: these appear in the module lists, not the file lists), and any file a C library "
              "opens by itself (for example a configuration file read by the OpenSSL library behind `_hashlib`). "
              "Neither server brings a C extension of its own."]
    return "\n".join(lines) + "\n"


def comparison_lines(comparisons: list) -> list:
    out = []
    for comparison in comparisons:
        for pair in comparison["pairs"]:
            if pair.get("skipped"):
                out.append(f"`{pair['left']}` against `{pair['right']}`: skipped ({pair['skipped']}).")
                continue
            fields = _unique(d["path"] for d in pair["answer_differences"])
            text = "the same answers" if pair["answers_equal"] else \
                f"{len(pair['answer_differences'])} differing fields ({', '.join(f'`{f}`' for f in fields)})"
            if "summaries_equal" in pair:
                text += "; event summaries " + ("the same" if pair["summaries_equal"] else "differ in " + ", ".join(
                    f"`{d['path']}`" for d in pair["summary_differences"]))
            out.append(f"`{pair['left']}` against `{pair['right']}`: {text} (`compare-{comparison['name']}.md`).")
    return out


def seen(summary: dict) -> dict:
    return {"writes": _writes_text(summary) or "none",
            "sockets": _events_text(summary["sockets"] + summary["network"]) or "none",
            "processes": _events_text(summary["processes"]) or "none",
            "modules": ", ".join(summary["modules"]["network_or_process"]) or "none"}


def compare_pythons(done: list) -> dict:
    """Each run's answers, and what its trace saw, under the first Python against each other one."""
    first, pairs = done[0], []
    for other in done[1:]:
        for label, a in first["results"].items():
            b = other["results"].get(label)
            if b is None:
                continue
            differences = answer_differences(a["answers"], b["answers"])
            pair = {"run": label, "left": first["version"], "right": other["version"], "answers_equal": not differences,
                    "answer_differences": differences}
            if a["spec"]["traced"]:
                pair["seen"] = {first["version"]: seen(a["summary"]), other["version"]: seen(b["summary"])}
            pairs.append(pair)
    return {"name": "python", "about": "each run under one Python against the same run under the other",
            "pairs": pairs}


def render_pythons(comparison: dict) -> tuple:
    lines = [f"# Comparison `python`: {comparison['about']}", "",
             "Answers compared line by line, session by session, times left out.", "",
             "| Run | Pythons | Answers | What the trace saw that differs |", "|---|---|---|---|"]
    bullets = []
    for pair in comparison["pairs"]:
        diff = ""
        if pair.get("seen"):
            a, b = pair["seen"][pair["left"]], pair["seen"][pair["right"]]
            diff = "; ".join(f"{k}: {pair['left']} {a[k]}, {pair['right']} {b[k]}" for k in a if a[k] != b[k])
        same = "the same" if pair["answers_equal"] else f"{len(pair['answer_differences'])} differing fields"
        lines.append(f"| `{pair['run']}` | {pair['left']} and {pair['right']} | {same} | {diff or 'nothing'} |")
        bullets.append(f"`{pair['run']}`: answers {same} under {pair['left']} and {pair['right']}"
                       + (f"; {diff}" if diff else "") + ".")
    return "\n".join(lines) + "\n", bullets


# The commands.

def python_version(python: str) -> str:
    return subprocess.run([python, "-B", "-c", "import sys; print(sys.version.split()[0])"], capture_output=True,
                          text=True, check=True).stdout.strip()


def run_all(out: Path, work: Path, python: str, runs=RUNS, repo: Path = REPO) -> dict:
    """Every run under one Python, its files and comparisons written into out."""
    sandbox = sandbox_check(python)
    results, skipped, trees = {}, {}, {"current": repo}
    for spec in runs:
        if spec["sandbox"] and not sandbox.get("available"):
            skipped[spec["label"]] = "sandbox-exec could not run: " + str(sandbox.get("error"))
            continue
        if spec["tree"] not in trees:
            trees[spec["tree"]] = work / spec["tree"]
            export(spec["tree"], trees[spec["tree"]], repo)
        results[spec["label"]] = execute(spec, trees[spec["tree"]], work, out, python)
    comparisons = compare(results, repo)
    for comparison in comparisons:
        _write_json(out / f"compare-{comparison['name']}.json", comparison)
    for name, page in render_comparisons(comparisons).items():
        (out / f"compare-{name}.md").write_text(page, encoding="utf-8")
    return {"python": python, "version": python_version(python), "results": results, "skipped": skipped,
            "sandbox": sandbox, "comparisons": comparisons}


def record(out_root: Path = RUNTIME, pythons=None, repo: Path = REPO) -> dict:
    pythons = list(pythons or [sys.executable])
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%M%SZ")
    out = Path(out_root) / stamp
    out.mkdir(parents=True)
    done = []
    with tempfile.TemporaryDirectory(prefix="mcp-runtime-") as work:
        for number, python in enumerate(pythons):
            sub = out / f"python-{python_version(python)}"
            sub.mkdir()
            (Path(work) / str(number)).mkdir()
            done.append(run_all(sub, Path(work) / str(number), python, repo=repo))
        work_forms = _forms(work)
    across = None
    if len(done) > 1:
        comparison = compare_pythons(done)
        _write_json(out / "compare-python.json", comparison)
        page, across = render_pythons(comparison)
        (out / "compare-python.md").write_text(page, encoding="utf-8")
    commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    manifest = {
        "folder": stamp, "recorded_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "recorded_local": now.astimezone().strftime("%Y-%m-%d %H:%M %Z"), "commit": commit,
        "command": "python3 tools/mcp_runtime_trace.py record" + "".join(f" --python {p}" for p in pythons),
        "tool": "tools/mcp_runtime_trace.py", "across": across,
        "tool_sha256": {f"tools/{path.name}": sha256_file(path) for path in (Path(__file__).resolve(), BOOT)},
        "interpreters": [{
            "python": d["python"], "version": d["version"], "folder": f"python-{d['version']}", "sandbox": d["sandbox"],
            "comparison_lines": comparison_lines(d["comparisons"]),
            "runs": [dict(spec, **({"skipped": d["skipped"][spec["label"]]} if spec["label"] in d["skipped"] else {
                "answers_sha256": digest(d["results"][spec["label"]]["answers"]),
                "steps": d["results"][spec["label"]]["steps"],
                "as_the_plan_expects": d["results"][spec["label"]]["matched"],
                "files": d["results"][spec["label"]]["files"],
                **({"seen": seen(d["results"][spec["label"]]["summary"])} if spec["traced"] else {})}))
                for spec in RUNS]} for d in done]}
    _write_json(out / "manifest.json", manifest)
    (out / "README.md").write_text(render_readme(manifest), encoding="utf-8")
    return {"folder": out, "done": done, "manifest": manifest, "privacy_problems": privacy_problems(out, work_forms)}


def check(folder: Path, repo: Path = REPO) -> dict:
    """Every saved run again, under the same Python if it is still here, compared with the saved files."""
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    report = []
    for interpreter in manifest["interpreters"]:
        python, saved_runs = interpreter["python"], interpreter["runs"]
        sub = folder / interpreter["folder"]
        version = python_version(python) if Path(python).exists() else None
        if version != interpreter["version"]:
            report.append({"python": interpreter["version"], "run": "(all)", "same": None,
                           "why": f"{python} is {'missing' if version is None else 'Python ' + version} here"})
            continue
        runs = [spec for spec in RUNS if any(r["label"] == spec["label"] and "skipped" not in r for r in saved_runs)]
        with tempfile.TemporaryDirectory(prefix="mcp-runtime-check-") as work:
            out = Path(work) / "out"
            out.mkdir()
            done = run_all(out, Path(work), python, runs=runs, repo=repo)
        for saved in saved_runs:
            label, entry = saved["label"], {"python": interpreter["version"], "run": saved["label"]}
            if "skipped" in saved:
                report.append(dict(entry, same=None, why="skipped when it was recorded"))
                continue
            if label not in done["results"]:
                report.append(dict(entry, same=False, why=done["skipped"].get(label, "not run")))
                continue
            new, problems = done["results"][label], []
            if digest(new["answers"]) != saved["answers_sha256"]:
                old_log = [json.loads(line) for line in
                           (sub / f"{label}.client.jsonl").read_text(encoding="utf-8").splitlines() if line]
                problems += [f"answer {d['session']} step {d['step']} {d['path']}"
                             for d in answer_differences(answers(old_log), new["answers"])] or ["answers"]
            if saved["traced"]:
                old = json.loads((sub / f"{label}.summary.json").read_text(encoding="utf-8"))
                problems += [f"summary {p}: {_short(x)} then {_short(y)}"
                             for p, x, y in field_diff(old, json.loads(json.dumps(new["summary"])))]
            report.append(dict(entry, same=not problems, differences=problems))
    return {"runs": report, "ok": all(r["same"] is not False for r in report)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 tools/mcp_runtime_trace.py", description=__doc__.split("\n")[0])
    commands_ = parser.add_subparsers(dest="command", required=True)
    first = commands_.add_parser("record", help="every run, saved in js3/mcp/runtime/<UTC time>/")
    first.add_argument("--out", type=Path, default=RUNTIME, help="the folder the dated folder is made in")
    first.add_argument("--python", action="append", help="a Python to run the servers with (repeat for several; "
                                                         "default: the one running this tool)")
    again = commands_.add_parser("check", help="every run again, compared with a saved folder")
    again.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        done = record(args.out, args.python) if args.command == "record" else check(args.folder)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"stopped: {exc}", file=sys.stderr)
        return 2
    if args.command == "check":
        for r in done["runs"]:
            state = {None: "skipped", True: "the same", False: "DIFFERENT"}[r["same"]]
            print(f"Python {r['python']} {r['run']}: {state}" + (f" ({r['why']})" if r.get("why") else ""))
            for line in r.get("differences") or []:
                print(f"  {line}")
        return 0 if done["ok"] else 1
    for d in done["done"]:
        for label, r in d["results"].items():
            traced = "; ".join(f"{k} {v}" for k, v in seen(r["summary"]).items()) if r["spec"]["traced"] else \
                "not traced"
            print(f"Python {d['version']} {label}: {r['matched']} of {r['steps']} as expected; {traced}")
        for label, why in d["skipped"].items():
            print(f"Python {d['version']} {label}: skipped ({why})")
        for line in comparison_lines(d["comparisons"]):
            print(f"Python {d['version']} {line}")
    for line in done["manifest"].get("across") or []:
        print(line)
    incomplete = [f"Python {d['version']} {label}" for d in done["done"] for label, r in d["results"].items()
                  if r["spec"]["traced"] and (r["summary"]["sessions_without_a_record"] or r["summary"]["hook_errors"]
                                              or r["summary"]["unreadable_lines"])]
    for item in incomplete:
        print(f"INCOMPLETE RECORD: {item}")
    for problem in done["privacy_problems"]:
        print(f"PRIVACY: {problem}")
    print(f"wrote {done['folder'].relative_to(REPO) if REPO in done['folder'].parents else done['folder']}")
    return 0 if not done["privacy_problems"] and not incomplete else 1


if __name__ == "__main__":
    sys.exit(main())
