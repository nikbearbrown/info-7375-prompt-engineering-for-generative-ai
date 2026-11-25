# Windows shim: subprocess.run(["npx", ...]) cannot find npx.cmd without a shell.
# Resolve the executable to its full path, then run the toolkit script unchanged.
import runpy, shutil, subprocess, sys
_orig = subprocess.run
def _run(cmd, *a, **k):
    if isinstance(cmd, list) and cmd and cmd[0] in ("npx", "node"):
        cmd = [shutil.which(cmd[0]) or cmd[0]] + cmd[1:]
    return _orig(cmd, *a, **k)
subprocess.run = _run
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
