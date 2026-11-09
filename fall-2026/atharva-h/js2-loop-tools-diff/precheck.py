"""Pre-submit honesty check. Run it before zipping; it fails loudly instead of letting a claim slip.

    python3 precheck.py

Fails if:
- an open work marker is left in a .md or .py file;
- the README names a run folder that has no saved trace;
- a run folder is missing its trace, summary, or report;
- the budgets in loop.py differ from GATE.md.
"""
import os
import re
import sys

import loop

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN_MARKERS = re.compile(r"\[TODO\]|\bTODO:|\bFIXME\b|\bTBD\b|\bXXX\b")
RUN_REF = re.compile(r"runs/(\d{4}-\d\d-\d\dT\d{6}Z[\w.-]*)")
SKIP_DIRS = {"runs", "state", "__pycache__", ".git"}


def files(ext):
    for base, dirs, names in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            if name.endswith(ext) and name != "precheck.py":
                yield os.path.join(base, name)


def main():
    problems = []
    for path in list(files(".md")) + list(files(".py")):
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if OPEN_MARKERS.search(line):
                    problems.append(f"open marker in {os.path.relpath(path, HERE)}:{n}: {line.strip()[:80]}")
    readme = os.path.join(HERE, "README.md")
    if os.path.exists(readme):
        with open(readme, encoding="utf-8") as f:
            for name in sorted(set(RUN_REF.findall(f.read()))):
                if not os.path.exists(os.path.join(HERE, "runs", name)):
                    problems.append(f"README names runs/{name}, which does not exist")
    runs = os.path.join(HERE, "runs")
    for name in sorted(os.listdir(runs)) if os.path.isdir(runs) else []:
        folder = os.path.join(runs, name)
        needed = ("result.json", "report.md") if name.endswith("_identity-check") else ("trace.jsonl", "run.json", "report.md")
        for item in needed:
            if not os.path.exists(os.path.join(folder, item)):
                problems.append(f"runs/{name} has no {item}")
    with open(os.path.join(HERE, "GATE.md"), encoding="utf-8") as f:
        gate = f.read()
    for key, pattern in (("boards", r"\*\*Boards:\*\* at most (\d+)"), ("requests", r"\*\*HTTP requests:\*\* at most (\d+)"),
                         ("seconds", r"\*\*Time:\*\* at most (\d+) seconds")):
        m = re.search(pattern, gate)
        if not m or int(m.group(1)) != loop.BUDGETS[key]:
            problems.append(f"budget {key}: loop.py has {loop.BUDGETS[key]}, GATE.md has {m.group(1) if m else 'nothing'}")
    for p in problems:
        print(f"FAIL {p}")
    print("precheck: " + ("OK" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
