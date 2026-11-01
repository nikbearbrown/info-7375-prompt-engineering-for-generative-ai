"""Action-surface comparison (Chapter 3): the same judgment done three ways, on one posting.

1. chat:  writes the exact text to paste into claude.ai (a person pastes it and saves the reply by hand).
2. file:  Claude Code gets one tool, Read, in a folder holding only the posting and the résumé.
3. agent: `python3 -m agent watch` (fetches, saves the raw response, writes its own state file).
"""
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

from . import claude_judge, config, rule

OUT = config.ROOT / "action-surfaces"
BASELINE = config.ROOT / "experiment" / "prompts" / "baseline.md"
FILE_COMMAND = ["claude", "-p", "--output-format", "json", "--tools", "Read", "--allowedTools", "Read",
                "--system-prompt", claude_judge.SYSTEM, "--model", claude_judge.MODEL,
                "--no-session-persistence", "--strict-mcp-config", "--setting-sources", ""]
FILE_TAIL = ("The candidate's résumé is in the file `resume.json` and the job posting is in the file "
             "`posting.txt`, both in the current folder. Read both files before you answer.\n")


def find_job(job_id):
    """The job as it came back in the newest saved Pinterest response that has it."""
    for path in sorted(config.RAW_DIR.glob("pinterest-*.json"), reverse=True):
        for job in json.loads(path.read_text(encoding="utf-8"))["jobs"]:
            if job["id"] == job_id:
                return job, path
    raise KeyError(f"job {job_id} is not in any saved Pinterest response")


def posting_text(job):
    location = (job.get("location") or {}).get("name", "")
    return (f"Job ID: {job['id']}\nTitle: {job.get('title', '')}\nLocation: {location}\n\n"
            f"Description:\n{rule.description_text(job)}\n")


def file_prompt():
    text = BASELINE.read_text(encoding="utf-8")
    return text[:text.index("Candidate résumé (fictional):")] + FILE_TAIL


def chat_way(job, resume, out=OUT):
    """Way 1: the text a person pastes into claude.ai. The résumé part leaves out email and phone."""
    path = out / "1-chat" / f"paste-into-claude-ai-{job['id']}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(claude_judge.build_prompt(BASELINE.read_text(encoding="utf-8"), job, resume), encoding="utf-8")
    return path


def file_way(job, resume_path, run=subprocess.run, out=OUT, now=None):
    """Way 2: Claude Code reads two files with its Read tool. Everything it was given and said is saved."""
    folder = out / "2-file"
    given = folder / "given"
    given.mkdir(parents=True, exist_ok=True)
    (given / "posting.txt").write_text(posting_text(job), encoding="utf-8")
    shutil.copyfile(resume_path, given / "resume.json")
    prompt = file_prompt()
    (folder / "prompt.txt").write_text(prompt, encoding="utf-8")
    at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory() as work:
        for name in ("posting.txt", "resume.json"):
            shutil.copyfile(given / name, f"{work}/{name}")
        done = run(FILE_COMMAND, input=prompt, capture_output=True, text=True, cwd=work, timeout=300)
    envelope = json.loads(done.stdout) if done.returncode == 0 else {"is_error": True, "result": "",
                                                                     "error": (done.stderr or done.stdout)[:2000]}
    reply = envelope.get("result", "")
    record = {"kind": claude_judge.KIND, "at": at, "job_id": job["id"], "surface": "file (Claude Code, Read tool only)",
              "command": FILE_COMMAND, "models_used": list((envelope.get("modelUsage") or {}).keys()),
              "num_turns": envelope.get("num_turns"), "reply": reply, "valid": False, "error": None, "parsed": None}
    try:
        record["parsed"], record["valid"] = claude_judge.validate(reply), True
    except claude_judge.InvalidReply as e:
        record["error"] = str(e)
    return claude_judge.save(record, folder, f"reply-{job['id']}")
