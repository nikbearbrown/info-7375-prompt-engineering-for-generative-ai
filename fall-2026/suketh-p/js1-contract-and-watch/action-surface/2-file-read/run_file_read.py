"""Action surface 2: give Claude files to read. The same task as the agent's judge, for
posting 5418610008, but Claude must open the files itself with the Read tool.

    python3 action-surface/2-file-read/run_file_read.py

Copies prompt.md, resume.json and posting.json into a fresh empty folder OUTSIDE the repo
(so no CLAUDE.md or project file is in reach), runs `claude -p` there with only the Read
tool, saves the full event stream, and checks the final answer with the agent's validator.
"""

import gzip
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from jobwatch import board, judge  # noqa: E402
from jobwatch.errors import JudgeError  # noqa: E402
from jobwatch.resume import validate_resume  # noqa: E402

POSTING_ID = 5418610008
ASK = ("Read prompt.md, resume.json and posting.json in the current directory. "
       "Follow the instructions in prompt.md: resume.json is the résumé and posting.json is the posting.")


def main():
    resume = validate_resume(json.loads((ROOT / "persona/alex_morgan.json").read_text(encoding="utf-8")))
    raw = gzip.decompress((ROOT / "runs/20261028T102612Z-live/raw_response.json.gz").read_bytes())
    posting = judge.posting_input({p.id: p for p in board.parse_board(raw)}[POSTING_ID])
    files = HERE / "files-given-to-claude"
    files.mkdir(exist_ok=True)
    (files / "prompt.md").write_text(judge.load_prompt("judge_v1"), encoding="utf-8")
    (files / "resume.json").write_text(json.dumps(resume, indent=2, ensure_ascii=False), encoding="utf-8")
    (files / "posting.json").write_text(json.dumps(posting, indent=2, ensure_ascii=False), encoding="utf-8")

    command = ["claude", "-p", "--model", "claude-opus-5-5", "--tools", "Read", "--allowedTools", "Read",
               "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
               "--no-session-persistence", "--verbose", "--output-format", "stream-json"]
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory(prefix="jobwatch-file-read-") as work:
        for name in ("prompt.md", "resume.json", "posting.json"):
            shutil.copy(files / name, Path(work) / name)
        done = subprocess.run(command, input=ASK, capture_output=True, text=True, cwd=work, timeout=600,
                              env={**__import__("os").environ, "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"})
    finished = datetime.now().astimezone().isoformat(timespec="seconds")
    (HERE / "stream.jsonl").write_text(done.stdout, encoding="utf-8")

    events = [json.loads(line) for line in done.stdout.splitlines() if line.strip().startswith("{")]
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    tool_calls = [block for e in events if e.get("type") == "assistant"
                  for block in e.get("message", {}).get("content", []) if block.get("type") == "tool_use"]
    result = next((e for e in events if e.get("type") == "result"), {})
    answer = result.get("result", "")
    try:
        judge.validate_response(answer, resume, posting)
        validation = "accepted by the agent's validator"
    except JudgeError as error:
        validation = f"rejected by the agent's validator: {error}"
    summary = {
        "started_at": started, "finished_at": finished, "command": command, "user_message": ASK,
        "exit_code": done.returncode, "tools_available": init.get("tools"), "mcp_servers": init.get("mcp_servers"),
        "tool_calls": [{"name": t.get("name"), "input": t.get("input")} for t in tool_calls],
        "answer": answer, "validation": validation, "usage": result.get("usage"),
        "total_cost_usd": result.get("total_cost_usd"), "is_error": result.get("is_error"),
        "note": "Real claude -p run. Files were copied to a temporary folder outside the repo; only the Read tool was available.",
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("started_at", "exit_code", "tools_available", "tool_calls", "validation", "total_cost_usd")}, indent=2))
    print("answer:", answer[:600])


if __name__ == "__main__":
    main()
