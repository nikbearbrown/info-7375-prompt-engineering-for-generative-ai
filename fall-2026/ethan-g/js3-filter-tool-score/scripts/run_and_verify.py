"""Run the loop, then the independent verifier, and save both outputs in the run folder.

This is my tool, not the agent: it starts two separate processes and only reads what they print.

    python3 scripts/run_and_verify.py --boards config/boards.json --no-claude
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv):
    loop = subprocess.run([sys.executable, "-m", "jsagent.loop", *argv], cwd=ROOT, capture_output=True, text=True)
    console = loop.stdout + (("\n[stderr]\n" + loop.stderr) if loop.stderr else "")
    print(console, end="")
    m = re.search(r"^run dir: (.+)$", loop.stdout, re.M)
    if not m:
        print("verifier: not run (the loop created no run folder)")
        return loop.returncode
    run_dir = (ROOT / m.group(1)).resolve()
    ver = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_run.py"), str(run_dir)], cwd=ROOT,
                         capture_output=True, text=True)
    print(ver.stdout, end="")
    with open(run_dir / "console.txt", "x") as f:
        f.write("$ python3 -m jsagent.loop " + " ".join(argv) + "\n" + console)
    with open(run_dir / "verifier.txt", "x") as f:
        f.write(f"$ python3 scripts/verify_run.py {m.group(1)}\n" + ver.stdout + ver.stderr)
    return loop.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
