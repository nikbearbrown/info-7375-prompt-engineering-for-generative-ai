"""Report what a process actually touches, via Python audit hooks (JS3 Step 5, declared vs actual behavior).

Imports nothing from jsagent, so it can be installed BEFORE the server's modules load: the filter reads the persona file at
import time, and a hook installed later (the first version, inside mcp_server.main) never saw that read.

Reads of library code (.py/.pyc/.so, anything under /lib/python) are skipped as noise. Writes are reported WHEREVER they happen:
the first version skipped /lib/python for writes too, which would have hidden a server writing into its own installed packages
(changed 2026-11-25 before running the fetch server).
"""
import os
import sys

_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


def _is_write(mode, flags):
    if isinstance(mode, str):
        return any(c in mode for c in "wax+")
    return isinstance(flags, int) and bool(flags & _WRITE_FLAGS)


def _hook(event, args):
    if event == "open":
        path, mode, flags = str(args[0]), args[1], args[2] if len(args) > 2 else None
        if _is_write(mode, flags):
            sys.stderr.write(f"AUDIT open WRITE {mode} {path}\n")
        elif not path.endswith((".py", ".pyc", ".so")) and "/lib/python" not in path and "__pycache__" not in path:
            sys.stderr.write(f"AUDIT open {mode} {path}\n")
    elif event.startswith(("socket.", "subprocess.", "os.remove", "os.rename", "os.unlink", "os.mkdir", "shutil.", "urllib.")):
        sys.stderr.write(f"AUDIT {event} {args!r}\n")


def install():
    sys.addaudithook(_hook)
