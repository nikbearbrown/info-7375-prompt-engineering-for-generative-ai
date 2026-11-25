"""Run the real MCP server under a Python audit hook (PEP 578) that reports,
to stderr, every file opened for WRITING, every directory/file mutation,
every DNS lookup / socket connect, and every subprocess or exec. Used by
tools/mcp_client.py --audit to check what the server ACTUALLY does against
what it declares. stdout is untouched (it stays the MCP channel).

Limits: an audit hook sees what CPython raises events for. C extensions
that bypass the Python runtime (none are imported by this server) would not
show up. It observes; it does not block.
"""
import json
import os
import runpy
import sys

_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
_err = sys.stderr


def _emit(kind, **kw):
    _err.write("AUDIT " + json.dumps({"kind": kind, **kw}, default=str) + "\n")
    _err.flush()


def hook(event, args):
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or \
                  (isinstance(flags, int) and flags & _WRITE_FLAGS)
        if writing and not isinstance(path, int):
            _emit("write_open", path=os.path.abspath(path) if isinstance(path, (str, bytes)) else path)
    elif event in ("os.mkdir", "os.rename", "os.replace", "os.remove", "os.rmdir", "os.truncate",
                   "os.chmod", "os.symlink", "os.link", "shutil.rmtree", "shutil.copyfile", "shutil.move"):
        _emit("fs_mutation", event=event, args=[str(a) for a in args])
    elif event in ("socket.getaddrinfo", "socket.connect", "socket.gethostbyname"):
        _emit("network", event=event, args=[str(a) for a in args])
    elif event in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork"):
        # Never record the child's environment: it carries secrets (e.g.
        # ANTHROPIC_API_KEY). Found, then fixed 2026-11-22: the first version
        # logged Popen's env argument in full, and the key ended up in log 27.
        if event == "subprocess.Popen":
            executable, argv = (list(args) + [None, None])[:2]
            _emit("process", event=event, executable=str(executable), argv=str(argv), env="[not recorded]")
        else:
            _emit("process", event=event, args=[str(a) for a in args[:2]])


if __name__ == "__main__":
    # run as a script from tools/, so put the project root (not tools/) on the path
    sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.addaudithook(hook)
    runpy.run_module("js3.mcp_server", run_name="__main__")
