"""Action-surface comparison: judge posting 8546367002 with the revision prompt three ways.

    python3 experiments/action_surface.py --mode file           # OFFLINE: show folder + command
    python3 experiments/action_surface.py --mode agent          # OFFLINE: show folder + command
    python3 experiments/action_surface.py --mode file --live    # one claude -p call, Read tool only
    python3 experiments/action_surface.py --mode agent --live   # one claude -p call, WebFetch + Write

The chat surface is not run from here: paste experiments/action_surface/chat_paste.txt
into a new Claude.ai chat yourself. In both modes below, Claude Code permissions
(--permission-mode dontAsk) refuse every tool call that the allow rules do not
name, and the reply or written record still goes through judge.validate()
against the 12:40 ET Oct 26 saved description.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import judge  # noqa: E402
import persona  # noqa: E402

POSTING_ID = 8546367002
SAVED = ROOT / "runs" / "postings" / "databricks_job_8546367002_2026-10-26T12-40-58-0400.json"
PROMPT = ROOT / "prompts" / "judge-revision.txt"
URL = f"https://boards-api.greenhouse.io/v1/boards/databricks/jobs/{POSTING_ID}"
OUT_DIR = ROOT / "runs" / "action_surface"


def priya_lines(targets):
    return judge.user_message({"title": "", "location": "", "description": ""}, targets).split("\n\n", 1)[1]


def file_setup(folder, posting, targets):
    (folder / "posting.txt").write_text(judge.user_message(posting, targets) + "\n", encoding="utf-8")
    message = "Read the file posting.txt in the current folder. It holds one posting and Priya's fields. Judge it."
    command = ["claude", "-p", message, "--model", judge.MODEL, "--tools", "Read", "--allowedTools", "Read",
               "--permission-mode", "dontAsk", "--no-session-persistence", "--output-format", "stream-json",
               "--verbose", "--system-prompt", PROMPT.read_text(encoding="utf-8")]
    return command


def agent_setup(folder, posting, targets):
    record = folder / "judge-record.json"
    message = "\n".join([
        f"Fetch the job posting at {URL} (Greenhouse JSON; the description is in its 'content' field as escaped HTML).",
        "Judge it for Priya. Write exactly your JSON object to the file judge-record.json in the current folder,",
        "then reply with the same JSON object.", "", priya_lines(targets)])
    command = ["claude", "-p", message, "--model", judge.MODEL, "--tools", "WebFetch,Write",
               "--allowedTools", "WebFetch(domain:boards-api.greenhouse.io)", f"Edit(/{record})",
               "--permission-mode", "dontAsk", "--no-session-persistence", "--output-format", "stream-json",
               "--verbose", "--system-prompt", PROMPT.read_text(encoding="utf-8")]
    return command


def tool_calls(stream):
    """Every tool_use the session attempted, and every call Claude Code refused, from stream-json."""
    calls, denials, result = [], [], None
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for block in (event.get("message") or {}).get("content") or []:
                if block.get("type") == "tool_use":
                    calls.append({"tool": block.get("name"), "input": block.get("input")})
        if event.get("type") == "result":
            result = event
            denials = event.get("permission_denials") or []
    return calls, denials, result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", required=True, choices=("file", "agent"))
    parser.add_argument("--live", action="store_true", help="actually call Claude")
    args = parser.parse_args(argv)
    _, targets = persona.load_persona()
    posting = judge.load_posting(SAVED)
    with tempfile.TemporaryDirectory(prefix=f"js1-{args.mode}-") as tmp:
        folder = Path(tmp).resolve()
        command = (file_setup if args.mode == "file" else agent_setup)(folder, posting, targets)
        shown = list(command)
        shown[2] = "<user message below>"
        shown[shown.index("--system-prompt") + 1] = "<system prompt: prompts/judge-revision.txt>"
        if not args.live:
            print(f"OFFLINE: no Claude call made. Folder {folder} would contain: "
                  f"{sorted(p.name for p in folder.iterdir()) or 'nothing'}")
            print(json.dumps(shown, indent=2))
            print("--- user message ---\n" + command[2])
            return
        called_at = datetime.now().astimezone()
        proc = subprocess.run(command, cwd=folder, env=judge.clean_env(), stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=600)
        calls, denials, result = tool_calls(proc.stdout)
        reply = (result or {}).get("result")
        written = folder / "judge-record.json"
        written_text = written.read_text(encoding="utf-8") if written.exists() else None
        checked = {name: judge.validate(text, posting["description"]) for name, text in
                   (("reply", reply), ("written_file", written_text)) if text is not None}
        record = {"surface": args.mode, "posting_id": POSTING_ID, "label": "judgment", "source": judge.SOURCE,
                  "called_at": called_at.isoformat(), "model_pinned": judge.MODEL,
                  "model_reported": sorted(((result or {}).get("modelUsage") or {}).keys()),
                  "prompt_file": "prompts/judge-revision.txt", "command": shown, "exit_code": proc.returncode,
                  "tool_calls": calls, "permission_denials": denials,
                  "files_in_folder_after": sorted(p.name for p in folder.iterdir()),
                  "raw_reply": reply, "written_file": written_text,
                  "validation": {k: {"accepted": v[0] is not None, "errors": v[1]} for k, v in checked.items()},
                  "stderr": (proc.stderr or "")[-2000:]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{args.mode}_{called_at.strftime('%Y-%m-%dT%H-%M-%S%z')}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("surface", "tool_calls", "permission_denials", "validation")}, indent=2))
    print(f"record: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
