"""Run the constructed meeting-recap feature on every AMI sample meeting.

Each meeting's transcript is sent to headless Claude Code (`claude -p`, the
user's subscription, no API key) with the recap system prompt from
constructed/recap-system-prompt.md (everything after the first `---` line).
Tools are disabled and the run happens in an empty working directory, so no
project CLAUDE.md, memory or files reach the model.

Leakage rule: the recap feature receives the transcript only and never
summary.txt. Only the judge for rubric clause C1 gets the AMI DECISIONS list.

Each output is saved as outputs/feature-run/<meeting>.json with the run date,
`claude --version`, the model(s) reported in the output, and SHA-256 hashes of
the prompt and transcript.

Usage (from final-project-film/):
  python3 -I case-study/run_feature.py [--claude PATH] [--only MEETING ...]
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "data" / "sample"
PROMPT_FILE = HERE / "constructed" / "recap-system-prompt.md"
OUT = HERE / "outputs" / "feature-run"


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def system_prompt():
    text = PROMPT_FILE.read_text()
    marker = "\n---\n"
    if marker not in text:
        sys.exit(f"{PROMPT_FILE}: no '---' line separating the header from the prompt")
    return text.split(marker, 1)[1].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude", default=str(Path.home() / ".local/bin/claude"))
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()

    prompt = system_prompt()
    version = subprocess.run([args.claude, "--version"], capture_output=True,
                             text=True, check=True).stdout.strip()
    meetings = sorted(p.name for p in SAMPLE.iterdir() if (p / "transcript.txt").exists())
    if args.only:
        meetings = [m for m in meetings if m in args.only]
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = [args.claude, "-p", "--output-format", "json", "--system-prompt", prompt,
           "--tools", "", "--no-session-persistence"]

    with tempfile.TemporaryDirectory() as empty:
        for m in meetings:
            # Leakage rule: only the transcript is sent; summary.txt is never read here.
            transcript = (SAMPLE / m / "transcript.txt").read_text()
            started = dt.datetime.now(dt.timezone.utc)
            proc = subprocess.run(cmd, input=transcript, capture_output=True,
                                  text=True, cwd=empty)
            if proc.returncode != 0:
                sys.exit(f"{m}: claude exited {proc.returncode}\n{proc.stderr.strip()}")
            reply = json.loads(proc.stdout)
            record = {
                "meeting": m,
                "run_started_utc": started.isoformat(timespec="seconds"),
                "claude_version": version,
                "models_reported": sorted(reply.get("modelUsage", {})),
                "is_error": reply.get("is_error"),
                "recap": reply.get("result"),
                "system_prompt_file": str(PROMPT_FILE.relative_to(HERE)),
                "system_prompt_sha256": sha256(prompt),
                "transcript_file": f"data/sample/{m}/transcript.txt",
                "transcript_sha256": sha256(transcript),
                "usage": reply.get("usage"),
                "duration_ms": reply.get("duration_ms"),
            }
            (OUT / f"{m}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
            print(f"{m}\t{record['models_reported']}\terror={record['is_error']}"
                  f"\t{len((record['recap'] or '').split())} words")


if __name__ == "__main__":
    main()
