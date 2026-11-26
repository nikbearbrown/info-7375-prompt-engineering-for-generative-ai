"""Run a Python module under audit hooks and record what it actually does, not what it says.

    python3 scripts/audited.py <audit-log.jsonl> <module> [args...]

Records every file open (with mode), socket connect, subprocess / exec, and os.system /
os.remove / os.rename event the interpreter raises (PEP 578). The log is written by this
wrapper, outside the audited code's control (it cannot remove the hook).
"""
import json
import os
import runpy
import sys

WATCH = {"open", "socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn",
         "os.remove", "os.rename", "os.rmdir", "shutil.rmtree", "urllib.Request"}


def main():
    log_path = os.path.realpath(sys.argv[1])
    module = sys.argv[2]
    sys.argv = [module] + sys.argv[3:]
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    log = open(log_path, "a", encoding="utf-8", buffering=1)

    def hook(event, args):
        if event not in WATCH:
            return
        if event == "open":
            path, mode = args[0], args[1]
            if isinstance(path, int) or (isinstance(path, str) and os.path.realpath(path) == log_path):
                return
            mode = mode if isinstance(mode, str) else ("w" if (args[2] or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT) else "r")
            log.write(json.dumps({"event": "open", "path": str(path), "mode": mode}) + "\n")
        else:
            log.write(json.dumps({"event": event, "args": repr(args)[:300]}) + "\n")

    sys.addaudithook(hook)
    runpy.run_module(module, run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
