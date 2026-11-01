"""Action surface 2: Claude Code reads the résumé and posting files itself.

Same task, same prompt rules and same posting as surface 1 (the chat paste); the only
difference is that the inputs are files Claude must open with its Read tool instead of
text pasted into the conversation. Read is the only tool it gets: no shell, no network,
no writing. The reply goes through the same validator the watch uses.

    python3 action-surfaces/file_read.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jobwatch import judge, lab, persona  # noqa: E402

POSTING_ID = "7855793003"
OUT = ROOT / "action-surfaces" / "2-file-read"
FILES_PROMPT = ("RÉSUMÉ: read the file resume.json in the current folder.\n\n"
                "POSTING: read the file posting.json in the current folder.\n")


def main() -> int:
    resume = persona.load_resume(ROOT / "data" / "supriya-sharma.resume.json")
    posting = lab.load_postings(ROOT / lab.SOURCE)[POSTING_ID]
    _, template = judge.load_prompt(ROOT / "prompts" / "revision-v2.md")
    prompt = template[:template.index("RÉSUMÉ:")] + FILES_PROMPT

    inputs = OUT / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    (inputs / "resume.json").write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (inputs / "posting.json").write_text(json.dumps(judge.posting_view(posting), indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    (OUT / "prompt.txt").write_text(prompt, encoding="utf-8")

    cmd = ["claude", "-p", "--output-format", "json", "--tools", "Read", "--allowedTools", "Read",
           "--no-session-persistence", "--setting-sources", "", "--strict-mcp-config"]
    called_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory(prefix="js1-file-read-") as work:
        for name in ("resume.json", "posting.json"):
            shutil.copy(inputs / name, work)
        done = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=300, cwd=work)
    if done.returncode != 0:
        print(f"claude exited {done.returncode}: {done.stderr.strip()[:300]}", file=sys.stderr)
        return 1
    envelope = json.loads(done.stdout)
    reply_text = envelope.get("result", "")
    _, errors = judge.validate_reply(reply_text, posting, resume)
    (OUT / "reply.txt").write_text(reply_text + "\n", encoding="utf-8")
    record = {"surface": "Claude Code file read (claude -p, Read tool only)", "posting_id": POSTING_ID,
              "called_at": called_at, "model": ",".join(sorted(envelope.get("modelUsage") or {})),
              "num_turns": envelope.get("num_turns"), "permission_denials": envelope.get("permission_denials"),
              "validator": "VALID" if not errors else errors, "command": cmd}
    (OUT / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))
    print(reply_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
