"""The boot of tools/mcp_runtime_trace.py: an audit hook (PEP 578) around an MCP server that runs unchanged.

  python3 -B tools/mcp_trace_boot.py LOG -m MODULE [ARG ...]   runs MODULE as python3 -B -m MODULE [ARG ...] would
  python3 -B tools/mcp_trace_boot.py LOG PATH [ARG ...]        runs the file PATH as python3 -B PATH [ARG ...] would

LOG must not exist. It is created and opened (unbuffered) before the hook is installed, so the log's own writes
never reach the record; the hook writes one line per audit event to it. stdin, stdout and stderr are left to the
server: the boot writes nothing to stdout.

What a line keeps (an allowlist; every other event is kept as its name alone, never its arguments):
  open                         path, mode, flags (a file descriptor is matched to a path opened just before)
  file-changing events         their path arguments only (os.remove, os.rename, os.mkdir, shutil.*, ...)
  directory listings           the path only (os.listdir, os.scandir, glob, pathlib globs)
  socket.*                     family, type and protocol numbers, or the address (host, port) asked for
  http.client.connect, ...     host and port; urllib.Request: the URL's scheme and host only
  process events               the executable's file name only (subprocess.Popen, os.exec, os.posix_spawn, ...)
  import                       the module name only
os.putenv and os.unsetenv carry a variable's value, so they are kept as their names alone, like ctypes.* and the
rest. Paths are written as Python sees them; tools/mcp_runtime_trace.py replaces the repo with <repo> and the home
folder with ~ before anything is saved.

The boot imports nothing that Python's own startup has not already loaded (sys and os), so the record starts
complete: the module names present when the hook is installed are written first, runpy is imported after the hook
is on (its imports are recorded as the launcher's), and the server's imports follow. Python 3.9 and 3.12.
"""

import os
import sys

# event: the positions of its path arguments
FILE_CHANGES = {
    "os.chflags": (0,), "os.chmod": (0,), "os.chown": (0,), "os.link": (0, 1), "os.mkdir": (0,), "os.remove": (0,),
    "os.removexattr": (0,), "os.rename": (0, 1), "os.rmdir": (0,), "os.setxattr": (0,), "os.symlink": (0, 1),
    "os.truncate": (0,), "os.utime": (0,), "shutil.chown": (0,), "shutil.copyfile": (0, 1),
    "shutil.copymode": (0, 1), "shutil.copystat": (0, 1), "shutil.copytree": (0, 1), "shutil.make_archive": (0,),
    "shutil.move": (0, 1), "shutil.rmtree": (0,), "shutil.unpack_archive": (0, 1), "tempfile.mkdtemp": (0,),
    "tempfile.mkstemp": (0,), "sqlite3.connect": (0,),
}
LISTINGS = {"os.listdir": (0,), "os.scandir": (0,), "os.listxattr": (0,), "glob.glob": (0,), "glob.glob/2": (0, 2),
            "pathlib.Path.glob": (0, 1), "pathlib.Path.rglob": (0, 1)}
# event: the position of the executable (or command line) whose file name is kept; None keeps nothing
PROCESSES = {"subprocess.Popen": 0, "os.system": 0, "os.exec": 0, "os.posix_spawn": 0, "os.spawn": 1,
             "os.fork": None, "os.forkpty": None, "os.kill": None, "os.killpg": None, "os.startfile": None,
             "webbrowser.open": None, "_winapi.CreateProcess": None, "pty.spawn": None}
CONNECTS = {"http.client.connect", "ftplib.connect", "imaplib.open", "nntplib.connect", "poplib.connect",
            "smtplib.connect", "telnetlib.Telnet.open"}  # (self, host, port)
SOCKET_ADDRESS = {"socket.bind": 1, "socket.connect": 1, "socket.sendto": 1, "socket.sendmsg": 1,
                  "socket.getnameinfo": 0, "socket.gethostbyname": 0, "socket.gethostbyaddr": 0}


def quote(text: str) -> str:
    """A JSON string without the json module: ASCII only, every other character escaped."""
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch == '"' or ch == "\\":
            out.append("\\" + ch)
        elif 0x20 <= code < 0x7F:
            out.append(ch)
        elif code < 0x10000:
            out.append("\\u%04x" % code)
        else:
            code -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF)))
    out.append('"')
    return "".join(out)


def value(item) -> str:
    """str, bytes, int, bool, None and tuples or lists of them, as JSON; anything else as its type's name."""
    if item is None:
        return "null"
    if item is True or item is False:
        return "true" if item else "false"
    if isinstance(item, int):
        return str(int(item))
    if isinstance(item, str):
        return quote(item)
    if isinstance(item, bytes):
        return quote(os.fsdecode(item))
    if isinstance(item, (tuple, list)):
        return "[" + ",".join(value(i) for i in item) + "]"
    if hasattr(item, "__fspath__"):
        return value(os.fspath(item))
    return quote("<%s>" % type(item).__name__)


def path_of(item):
    if isinstance(item, (str, bytes)) or hasattr(item, "__fspath__"):
        return os.fsdecode(os.fspath(item))
    return item  # None, or a file descriptor (int)


def program(item):
    """The file name of an executable or of a command line's first word, nothing else."""
    if isinstance(item, (list, tuple)):
        item = item[0] if item else None
    if item is None:
        return None
    text = os.fsdecode(os.fspath(item)) if not isinstance(item, int) else str(item)
    words = text.split()
    return os.path.basename(words[0]) if words else ""


def make_hook(write, phase, recent):
    """The audit hook. It never raises into the audited call, and events it causes itself are not recorded."""
    busy = [False]

    def hook(event, args):
        if busy[0]:
            return
        busy[0] = True
        try:
            fields = describe(event, args, recent)
            write('{"n":%s,"p":%s%s}\n' % (quote(event), quote(phase[0]), fields))
        except Exception:
            try:
                write('{"n":%s,"p":%s,"hook_error":true}\n' % (quote(event), quote(phase[0])))
            except Exception:
                pass
        finally:
            busy[0] = False

    return hook


def describe(event, args, recent) -> str:
    if event == "import":
        return ',"m":' + value(args[0])
    if event == "open":
        path = path_of(args[0])
        via = None
        if isinstance(path, int):
            via, path = path, fd_path(path, recent)
        else:
            recent.append(path)
            del recent[:-8]
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else None
        flags = args[2] if len(args) > 2 and isinstance(args[2], int) else None
        return ',"path":%s,"mode":%s,"flags":%s%s' % (value(path), value(mode), value(flags),
                                                      "" if via is None else ',"fd":true')
    if event in FILE_CHANGES or event in LISTINGS:
        where = FILE_CHANGES.get(event) or LISTINGS.get(event)
        paths = [path_of(args[i]) if i < len(args) else None for i in where]
        return ',"paths":' + value(paths)
    if event in PROCESSES:
        at = PROCESSES[event]
        if at is None or at >= len(args):
            return ""
        item = args[at]
        if event == "subprocess.Popen" and item is None and len(args) > 1:
            item = args[1]  # no executable given: the first word of args
        return ',"program":' + value(program(item))
    if event.startswith("socket."):
        if event == "socket.__new__" and len(args) >= 4:
            return ',"family":%s,"type":%s,"proto":%s' % tuple(
                value(a if isinstance(a, int) else None) for a in args[1:4])
        if event == "socket.getaddrinfo" and len(args) >= 2:
            return ',"address":' + value([args[0], args[1]])
        at = SOCKET_ADDRESS.get(event)
        if at is not None and at < len(args):
            return ',"address":' + value(args[at])
        return ""
    if event in CONNECTS and len(args) >= 3:
        return ',"address":' + value([args[1], args[2]])
    if event == "urllib.Request" and args and isinstance(args[0], str):
        scheme, _, rest = args[0].partition("://")
        host = rest.split("/", 1)[0].split("?", 1)[0].rsplit("@", 1)[-1]
        return ',"scheme":%s,"host":%s' % (quote(scheme), quote(host))
    return ""


def fd_path(fd, recent):
    """The path of a file descriptor: the recently opened path with the same device and inode, else "<fd>"."""
    try:
        target = os.fstat(fd)
    except OSError:
        return "<fd>"
    for path in reversed(recent):
        try:
            seen = os.stat(path)
        except (OSError, TypeError, ValueError):
            continue
        if (seen.st_dev, seen.st_ino) == (target.st_dev, target.st_ino):
            return path
    return "<fd>"


def main(argv) -> int:
    if len(argv) < 2 or (argv[1] == "-m" and len(argv) < 3):
        sys.stderr.write("usage: python3 -B tools/mcp_trace_boot.py LOG (-m MODULE | PATH) [ARG ...]\n")
        return 2
    try:
        log = open(argv[0], "xb", buffering=0)
    except OSError as exc:
        sys.stderr.write("mcp_trace_boot: the log could not be created (%s)\n" % type(exc).__name__)
        return 2

    def write(line):
        log.write(line.encode("ascii"))

    module = argv[2] if argv[1] == "-m" else None
    target = module or argv[1]
    rest = argv[3:] if module else argv[2:]
    python_dirs = []  # where this Python's own files live, so the record can tell them from the server's
    for item in (sys.prefix, sys.base_prefix, sys.exec_prefix, getattr(sys, "base_exec_prefix", None),
                 os.path.dirname(os.__file__)):
        if item and item not in python_dirs:
            python_dirs.append(item)
    try:
        python_dirs += [p for p in sys.modules["site"].getsitepackages() if p not in python_dirs]
    except Exception:
        pass
    write('{"n":"_start","python":%s,"cwd":%s,"form":%s,"target":%s,"stdlib":%s,"python_dirs":%s,'
          '"pycache_prefix":%s}\n' % (
              quote(sys.version.split()[0]), value(os.getcwd()), quote("module" if module else "path"), value(target),
              value(os.path.dirname(os.__file__)), value(python_dirs), value(getattr(sys, "pycache_prefix", None))))
    write('{"n":"_modules","p":"startup","m":%s}\n' % value(sorted(sys.modules)))
    phase, recent = ["launcher"], []
    sys.addaudithook(make_hook(write, phase, recent))

    import runpy  # after the hook: its imports are recorded, as the launcher's
    if not module:
        import pkgutil  # noqa: F401  run_path's own import (Python 3.12), counted as the launcher's

    if sys.path and sys.path[0] == os.path.dirname(os.path.abspath(__file__)):
        # Python put the boot's folder first; the server's own command would have put this there instead
        sys.path[0] = os.getcwd() if module else os.path.dirname(os.path.abspath(target))
    sys.argv = [module or target] + rest
    phase[0] = "server"
    write('{"n":"_phase","p":"server"}\n')
    try:
        if module:
            runpy.run_module(module, run_name="__main__", alter_sys=True)
        else:  # an absolute path, as Python 3.9+ gives a script's __file__
            runpy.run_path(os.path.abspath(target), run_name="__main__")
    finally:
        phase[0] = "exit"
        write('{"n":"_modules","p":"server","m":%s}\n' % value(sorted(sys.modules)))
        write('{"n":"_phase","p":"exit"}\n')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
