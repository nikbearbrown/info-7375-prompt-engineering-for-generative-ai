"""Action surface, way 2: one claude -p call told to read a file.

Run from the project folder: python3 experiment/action_surface/way2_run.py

Writes one posting + the persona without its personal block (the baseline
prompt, filled) to a file in a fresh empty temporary folder, runs claude -p
there once, and saves the timestamped reply to way2_file.txt.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
sys.path.insert(0, str(PROJECT))

from agent.claude_judge import build_prompt  # noqa: E402
from agent.resume import load_resume  # noqa: E402

POSTING_ID = 7855793003  # dev row: Software Engineer II, Test Frameworks & Tooling
RAW_PATH = PROJECT / "raw" / "klaviyo_20261031T175121.json"
OUT_PATH = HERE / "way2_file.txt"
FILE_NAME = "judge_request.txt"
PROMPT = f"Read the file {FILE_NAME} in the current folder and follow its instructions."


def main():
    jobs = {j["id"]: j for j in json.loads(RAW_PATH.read_text())["jobs"]}
    resume = load_resume(PROJECT / "persona_arjun_mehta.json")
    request = build_prompt(jobs[POSTING_ID], resume)
    command = ["claude", "-p", PROMPT, "--output-format", "json"]

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory(prefix="js1-way2-") as folder:
        (Path(folder) / FILE_NAME).write_text(request)
        proc = subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=120)

    OUT_PATH.write_text("\n".join([
        f"Way 2 run: {started}",
        f"Posting: {POSTING_ID}",
        f"Command (run in a fresh empty temporary folder): {' '.join(command[:2])} \"{PROMPT}\" {' '.join(command[3:])}",
        f"Exit code: {proc.returncode}",
        "",
        f"===== {FILE_NAME} (the only file in the folder) =====",
        request,
        "===== raw reply (stdout) =====",
        proc.stdout,
        "===== stderr =====",
        proc.stderr,
    ]))
    print(f"exit {proc.returncode}; saved {OUT_PATH.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
