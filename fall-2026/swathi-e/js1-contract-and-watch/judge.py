"""The Claude judge from JUDGE-CONTRACT.md (baseline): a JUDGMENT, never a record.

Usage:
    python3 judge.py --fetch-posting ID         # save one posting's description (allow-listed host)
    python3 judge.py --posting RAW.json         # OFFLINE (default): show the prompt, call nothing
    python3 judge.py --posting RAW.json --live  # one fresh `claude -p` conversation

Live calls run Claude Code from a new empty folder with tools off, no session
persistence, stdin from /dev/null, no ANTHROPIC_API_KEY, and a pinned model.
Every reply goes through validate(); a rejected reply is recorded as rejected,
never repaired.
"""
import argparse
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import persona
import watch

HERE = Path(__file__).resolve().parent
MODEL = "claude-opus-5-5"
SOURCE = "Claude via Claude Code `claude -p` (not the bare model)"
CONTRACT_PATH = HERE / "JUDGE-CONTRACT.md"
BASELINE_PROMPT = HERE / "prompts" / "judge-baseline.txt"
POSTING_DIR = HERE / "runs" / "postings"
JUDGE_DIR = HERE / "runs" / "judge"

KEYS = ("verdict", "label", "experience_found", "authorization_found",
        "posting_fields_cited", "resume_fields_cited", "reason")
VERDICTS = ("relevant", "not_relevant")
SENTINELS = {"experience_found": "experience not stated", "authorization_found": "none stated"}


class _Text(HTMLParser):
    BLOCKS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "table"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKS:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def description_text(content):
    """Greenhouse sends HTML escaped twice; the judge and validator both see this text."""
    parser = _Text()
    parser.feed(html.unescape(content or ""))
    parser.close()
    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines())
    return "\n".join(line for line in lines if line)


def _words(text):
    return " ".join(text.split())


def validate(text, description):
    """Return (output, errors); output is None whenever errors is non-empty."""
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None, ["not valid JSON"]
    if not isinstance(data, dict):
        return None, ["not a JSON object"]
    errors = [f"missing key {k!r}" for k in KEYS if k not in data]
    errors += [f"extra key {k!r}" for k in data if k not in KEYS]
    if data.get("verdict") not in VERDICTS:
        errors.append(f"verdict {data.get('verdict')!r} is not 'relevant' or 'not_relevant'")
    if data.get("label") != "judgment":
        errors.append(f"label {data.get('label')!r} is not 'judgment'")
    for key in ("posting_fields_cited", "resume_fields_cited"):
        value = data.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
            errors.append(f"{key} must be a non-empty list of field names")
    for key, sentinel in SENTINELS.items():
        value = data.get(key)
        if value == sentinel:
            continue
        if not isinstance(value, str) or not _words(value):
            errors.append(f"{key} must be a quote or {sentinel!r}")
        elif _words(value) not in _words(description):
            errors.append(f"{key} quote does not appear word for word in the description")
    if "reason" in data and not isinstance(data["reason"], str):
        errors.append("reason must be a string")
    return (None if errors else data), errors


def load_posting(path):
    job = json.loads(Path(path).read_text(encoding="utf-8"))
    return {"id": job["id"], "title": job["title"], "location": (job.get("location") or {}).get("name", ""),
            "description": description_text(job.get("content")), "raw_file": watch._relative(path)}


def user_message(posting, targets):
    role, geo, visa = targets["target_role"], targets["geography"], targets["visa"]
    return "\n".join([
        "Posting fields:",
        f"title: {posting['title']}",
        f"location: {posting['location']}",
        "description:",
        posting["description"],
        "",
        "Priya's fields (fictional profile):",
        f"target roles: primary {role['primary']}; secondary {role['secondary']}",
        f"location: {geo['current_location']}; open to remote: {str(geo['open_to_remote']).lower()}",
        f"visa status: {visa['current_status']}",
    ])


def claude_command(system_prompt, message, model=MODEL):
    return ["claude", "-p", message, "--model", model, "--tools", "", "--no-session-persistence",
            "--output-format", "json", "--system-prompt", system_prompt]


def clean_env():
    """Only what claude needs to find itself and the user's login; never an API key."""
    return {key: os.environ[key] for key in ("HOME", "USER", "PATH") if key in os.environ}


def call_claude(command, runner=subprocess.run, timeout=300):
    with tempfile.TemporaryDirectory(prefix="js1-judge-") as empty:
        if any(Path(empty).iterdir()):
            raise RuntimeError("judge folder is not empty")
        return runner(command, cwd=empty, env=clean_env(), stdin=subprocess.DEVNULL,
                      capture_output=True, text=True, timeout=timeout)


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def judge_posting(posting, targets, live=False, prompt_path=BASELINE_PROMPT, runner=subprocess.run, now=None):
    system_prompt = Path(prompt_path).read_text(encoding="utf-8")
    message = user_message(posting, targets)
    record = {"posting_id": posting["id"], "title": posting["title"], "location": posting["location"],
              "raw_file": posting.get("raw_file"), "label": "judgment", "source": SOURCE,
              "judge_contract_sha256": _sha256(CONTRACT_PATH), "prompt_file": watch._relative(prompt_path),
              "prompt_sha256": hashlib.sha256(system_prompt.encode()).hexdigest(), "model_pinned": MODEL}
    command = claude_command(system_prompt, message)
    if not live:
        record.update(mode="offline", claude_called=False, status="not_run",
                      note="OFFLINE: no Claude call was made; nothing here is Claude output.",
                      command=command[:2] + ["<user message below>"] + command[3:], user_message=message)
        return record
    record.update(mode="live", claude_called=True,
                  called_at=(now or datetime.now().astimezone()).isoformat())
    proc = call_claude(command, runner)
    record.update(exit_code=proc.returncode, stderr=(proc.stderr or "")[-2000:])
    try:
        envelope = json.loads(proc.stdout)
    except (TypeError, ValueError):
        record.update(status="call_failed", errors=["Claude Code did not return its JSON envelope"],
                      raw_stdout=(proc.stdout or "")[-4000:], judge_output=None)
        return record
    models = sorted((envelope.get("modelUsage") or {}).keys())
    record.update(session_id=envelope.get("session_id"), model_reported=models,
                  model_matches_pin=models == [MODEL], raw_output=envelope.get("result"))
    if proc.returncode != 0 or envelope.get("is_error"):
        record.update(status="call_failed", errors=["Claude Code reported an error"], judge_output=None)
        return record
    output, errors = validate(envelope.get("result"), posting["description"])
    record.update(status="accepted" if output else "rejected", errors=errors, judge_output=output)
    return record


def fetch_posting(posting_id, now=None, posting_dir=POSTING_DIR):
    url = f"https://boards-api.greenhouse.io/v1/boards/{watch.BOARD}/jobs/{int(posting_id)}"
    status, body = watch.fetch(url)
    return watch.save_raw(body, now or datetime.now().astimezone(), url, status, posting_dir,
                          name=f"{watch.BOARD}_job_{int(posting_id)}")


def save_record(record, judge_dir=JUDGE_DIR):
    judge_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.fromisoformat(record["called_at"]).strftime("%Y-%m-%dT%H-%M-%S%z")
    path = judge_dir / f"{record['posting_id']}_{stamp}_{record['status']}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch-posting", type=int, metavar="ID", help="save one posting's raw detail response")
    group.add_argument("--posting", metavar="RAW.json", help="a saved posting detail response to judge")
    parser.add_argument("--live", action="store_true", help="actually call Claude (default: offline)")
    parser.add_argument("--prompt", default=str(BASELINE_PROMPT), help="system prompt file")
    args = parser.parse_args(argv)
    if args.fetch_posting:
        print(f"saved: {watch._relative(fetch_posting(args.fetch_posting))}")
        return
    _, targets = persona.load_persona()
    record = judge_posting(load_posting(args.posting), targets, live=args.live, prompt_path=args.prompt)
    if not args.live:
        print(record["note"])
        print(json.dumps({k: v for k, v in record.items() if k != "user_message"}, indent=2, ensure_ascii=False))
        print("\n--- user message that --live would send ---\n" + record["user_message"])
        return
    path = save_record(record)
    print(f"Claude verdict (JUDGMENT, not a fact) for {record['posting_id']}: status={record['status']}")
    print(json.dumps(record.get("judge_output") or {"errors": record.get("errors")}, indent=2, ensure_ascii=False))
    print(f"record: {watch._relative(path)}")


if __name__ == "__main__":
    sys.exit(main())
