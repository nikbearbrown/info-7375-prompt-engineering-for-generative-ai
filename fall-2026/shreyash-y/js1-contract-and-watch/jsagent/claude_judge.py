"""The second judge: Claude under a prompt contract. Its verdict is a JUDGMENT and is always
labeled as one. It runs through the Claude Code CLI (`claude -p`), one fresh conversation per
call, with every tool disabled and no session saved, from an empty temporary folder so no
project files or memory reach it. Every call's full CLI output is saved as evidence."""
import datetime
import hashlib
import json
import pathlib
import subprocess
import tempfile

from jsagent import validator

DEFAULT_MODEL = "opus"


def load_prompt(path):
    text = pathlib.Path(path).read_text()
    system, user = text.split("=== USER ===", 1)
    return system.strip(), user.strip(), hashlib.sha256(text.encode()).hexdigest()


def posting_for_model(p):
    return {k: p[k] for k in ("id", "title", "departments", "location", "offices", "content")}


def build(prompt_path, resume_view, p):
    system, user, digest = load_prompt(prompt_path)
    user = (user.replace("{RESUME}", json.dumps(resume_view, indent=1, ensure_ascii=False))
                .replace("{POSTING}", json.dumps(posting_for_model(p), indent=1, ensure_ascii=False)))
    return system, user, digest


def call_cli(system, user, model=DEFAULT_MODEL, timeout=300):
    with tempfile.TemporaryDirectory(prefix="js1-judge-") as empty:
        proc = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence",
             "--strict-mcp-config", "--setting-sources", "", "--output-format", "json",
             "--system-prompt", system],
            input=user, capture_output=True, text=True, timeout=timeout, cwd=empty)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    return json.loads(proc.stdout)


def judge(prompt_path, resume_view, p, calls_dir, tag, model=DEFAULT_MODEL):
    system, user, digest = build(prompt_path, resume_view, p)
    called_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    out = call_cli(system, user, model)
    text = out.get("result", "")
    parsed, errors = validator.validate(text, p["id"])
    models = sorted((out.get("modelUsage") or {}).keys())
    record = {
        "judge": "Claude (judgment, not a fact)",
        "called_at": called_at,
        "model": ",".join(models) or model,
        "prompt_file": str(prompt_path),
        "prompt_sha256": digest,
        "posting_id": p["id"],
        "tag": tag,
        "raw_text": text,
        "valid": not errors,
        "errors": errors,
        "parsed": parsed,
        "session_id": out.get("session_id"),
        "cost_usd": out.get("total_cost_usd"),
    }
    calls_dir = pathlib.Path(calls_dir)
    calls_dir.mkdir(parents=True, exist_ok=True)
    stamp = called_at.replace(":", "").replace("-", "").replace("+0000", "Z")
    (calls_dir / f"{stamp}-{p['id']}-{tag}.json").write_text(
        json.dumps({"record": record, "cli_output": out}, indent=2, ensure_ascii=False) + "\n")
    return record
