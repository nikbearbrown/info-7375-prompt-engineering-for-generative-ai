"""Report what a process actually touches, via Python audit hooks (JS3 Step 5, declared vs actual behavior).

Imports nothing from jsagent, so it can be installed BEFORE the server's modules load: the filter reads the persona file at
import time, and a hook installed later (the first version, inside mcp_server.main) never saw that read.
"""
import sys


def _hook(event, args):
    if event == "open":
        path, mode = str(args[0]), str(args[1])
        if not path.endswith((".py", ".pyc", ".so")) and "/lib/python" not in path and "__pycache__" not in path:
            sys.stderr.write(f"AUDIT open {mode} {path}\n")
    elif event.startswith(("socket.", "subprocess.", "os.remove", "os.rename", "os.unlink", "shutil.", "urllib.")):
        sys.stderr.write(f"AUDIT {event} {args!r}\n")


def install():
    sys.addaudithook(_hook)
