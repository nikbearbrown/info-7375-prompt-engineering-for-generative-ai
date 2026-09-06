"""Navigate and execute INFO 7375 weekly reference labs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "run", "test"])
    parser.add_argument("week", nargs="?", type=int)
    args = parser.parse_args()
    weeks = json.loads((ROOT / "course.json").read_text())["weeks"]
    if args.command == "list":
        for item in weeks:
            print(f'{item["week"]:2}: {item["title"]}')
        return
    selected = next((w for w in weeks if w["week"] == args.week), None)
    if not selected:
        parser.error("Choose a week from 1 through 15")
    folder = ROOT / selected["path"] / "code"
    command = ([sys.executable, str(folder / "main.py")] if args.command == "run"
               else [sys.executable, "-m", "unittest", "discover", "-s", str(folder / "tests"), "-v"])
    raise SystemExit(subprocess.run(command, cwd=ROOT, timeout=30).returncode)


if __name__ == "__main__":
    main()
