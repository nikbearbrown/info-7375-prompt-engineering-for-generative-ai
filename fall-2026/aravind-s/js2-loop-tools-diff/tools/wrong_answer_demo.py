"""The finished wrong answer (GATE.md), shown on a real run's saved answers.

1. Copy the agent's code into a temporary folder and plant wrong version 1a in the copy's
   providers.py: a board that answers HTTP 404 is read as zero postings. This repo is not changed.
2. Replay the saved answers of the run given through the planted copy, with fresh state, so every
   board is a first run and no Claude call is needed. A replay is labeled as one, never as live.
3. Replay the same answers through an unchanged copy, for comparison.
4. Run tools/check_run.py on both replays. It reads only the saved answers and the report.

Both replay folders, both checks' output and DEMO.md go to runs/demos/finished-wrong-answer/<run id>/.

Usage (from the repo root):  python3 tools/wrong_answer_demo.py runs/<run id> [output folder]
(the output folder is for the tool's own test; it defaults to runs/demos/finished-wrong-answer/<run id>)
Exit 0 when the planted replay ends "finished" and the check flags it while the unchanged replay
passes the check; 1 otherwise.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLANT_FILE = "job_agent/providers.py"
PLANT_OLD = '    if status != 200:\n        raise Unverified(f"the board answered HTTP {status}, not 200")\n'
PLANT_NEW = '    if status == 404:\n        return []  # PLANTED: wrong version 1a\n' + PLANT_OLD


def replay(source_run: Path, planted: bool) -> tuple:
    """(exit code, screen output, the replay's run folder copied out) for one replay in a fresh copy."""
    work = Path(tempfile.mkdtemp(prefix="job-agent-demo-"))
    try:
        for item in ("job_agent", "persona", "prompts"):
            shutil.copytree(REPO / item, work / item, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(REPO / "boards.json", work / "boards.json")
        if planted:
            text = (work / PLANT_FILE).read_text(encoding="utf-8")
            if text.count(PLANT_OLD) != 1:
                raise SystemExit("the text to plant is not found exactly once in providers.py")
            (work / PLANT_FILE).write_text(text.replace(PLANT_OLD, PLANT_NEW), encoding="utf-8")
        shutil.copytree(source_run, work / "runs" / "source" / source_run.name)
        (work / "state" / "replay").mkdir(parents=True)
        (work / "runs" / "replay").mkdir(parents=True)
        command = [sys.executable, "-m", "job_agent", "run", "--replay", f"runs/source/{source_run.name}",
                   "--state", "state/replay", "--runs", "runs/replay"]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=300,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        folders = [p for p in (work / "runs" / "replay").iterdir() if p.is_dir()]
        out = Path(tempfile.mkdtemp(prefix="job-agent-demo-out-")) / ("planted" if planted else "unchanged")
        if folders:
            shutil.copytree(folders[0], out)
        return result.returncode, result.stdout + result.stderr, out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def check(run_dir: Path) -> tuple:
    result = subprocess.run([sys.executable, str(REPO / "tools" / "check_run.py"), str(run_dir)],
                            capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) not in (1, 2) or not (Path(args[0]) / "report.json").exists():
        print("usage: python3 tools/wrong_answer_demo.py runs/<run id>   (a loop run with saved answers)")
        return 2
    source = Path(args[0]).resolve()
    target = Path(args[1]).resolve() if len(args) == 2 else REPO / "runs" / "demos" / "finished-wrong-answer" / source.name
    if target.exists():
        print(f"refused: {_shown(target)} already exists; a saved demo is never overwritten")
        return 3
    planted_code, planted_screen, planted_dir = replay(source, planted=True)
    plain_code, plain_screen, plain_dir = replay(source, planted=False)
    target.mkdir(parents=True)
    shutil.copytree(planted_dir, target / "planted-replay")
    shutil.copytree(plain_dir, target / "unchanged-replay")
    planted_check, planted_text = check(target / "planted-replay")
    plain_check, plain_text = check(target / "unchanged-replay")
    (target / "check-planted.txt").write_text(planted_text, encoding="utf-8")
    (target / "check-unchanged.txt").write_text(plain_text, encoding="utf-8")
    shown = lambda text: "\n".join("    " + line for line in text.strip().splitlines())  # noqa: E731
    made = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    (target / "DEMO.md").write_text(f"""# The finished wrong answer, on the saved answers of run {source.name}

Made by `python3 tools/wrong_answer_demo.py runs/{source.name}` at {made}. Both runs below are labeled
replays of that run's saved answers, with fresh state, not live runs. Nothing was fetched.

## 1. The planted wrong version

Wrong version 1a from GATE.md, planted in a temporary copy of the code ({PLANT_FILE}):

```diff
-{PLANT_OLD.rstrip().replace(chr(10), chr(10) + '-')}
+{PLANT_NEW.rstrip().replace(chr(10), chr(10) + '+')}
```

The planted replay's screen (exit code {planted_code}):

{shown(planted_screen)}

It ends cleanly, and it is wrong: the made-up board answered HTTP 404, and the run reports it read.

## 2. The independent check (`tools/check_run.py`, exit code {planted_check})

It reads only the saved answers and report.json, never the agent's code:

{shown(planted_text)}

## 3. The same answers through the unchanged code (exit code {plain_code})

{shown(plain_screen)}

The check on that replay (exit code {plain_check}):

{shown(plain_text)}
""", encoding="utf-8")
    print(f"saved to {_shown(target)}")
    print(f"planted replay: exit {planted_code}; check: exit {planted_check}")
    print(f"unchanged replay: exit {plain_code}; check: exit {plain_check}")
    shown_ok = planted_code == 0 and planted_check == 1 and plain_check == 0
    return 0 if shown_ok else 1


def _shown(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return path.name


if __name__ == "__main__":
    sys.exit(main())
