"""The Claude judge for JS3, on the JS1 claude-cli backend (jobwatch/judge_cli.py, Amendment A14).

    call(tools, system, user, model, stem, out_dir, clock) -> {"result", "error", "model", "called_at", ...}

Reuses the JS1 backend's pieces unchanged: its argv (cli_argv: no tools, no MCP servers, safe mode,
the model pinned), its environment (ANTHROPIC_API_KEY removed), its subprocess runner and timeout,
and its empty temporary working directory. JS1's CliJudge.call validates JS1's relevance schema,
so the call itself is made here. Every call saves, through tools.write_file:
  <out_dir>/<stem>.request.json   argv, the exact prompt (system and user), model, cwd note
  <out_dir>/<stem>.response.txt   the raw CLI stdout
  <out_dir>/<stem>.meta.json      CLI version, reported model, called_at (UTC), exit code, error
A failed call is recorded, never retried.
"""
import json
import tempfile
from datetime import datetime, timezone

from jobwatch import judge_cli

DEFAULT_MODEL = "claude-sonnet-5-5"  # inherited: JS1 jobwatch/judge.py DEFAULT_MODEL


def _utc(clock):
    return datetime.fromtimestamp(clock(), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fill(template, **values):
    """The prompt file's "## System" and "## User" sections, with {{NAME}} placeholders filled."""
    system = template.split("## System\n", 1)[1].split("## User\n", 1)[0].strip()
    user = template.split("## User\n", 1)[1]
    for k, v in values.items():
        user = user.replace("{{" + k + "}}", v)
    return system, user


def call(tools, system, user, model, stem, out_dir, clock):
    argv = judge_cli.cli_argv(system, model)
    request = {"backend": "claude-cli (JS1 judge_cli.cli_argv)", "argv": argv, "system": system, "stdin": user,
               "model_requested": model, "cwd": "a new empty temporary directory", "env_removed": list(judge_cli.REMOVED_ENV),
               "timeout_s": judge_cli.TIMEOUT_S}
    tools.write_file(f"{out_dir}/{stem}.request.json", (json.dumps(request, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    called_at = _utc(clock)
    stdout, stderr, code, error = "", "", None, None
    with tempfile.TemporaryDirectory(prefix="jobwatch-judge-") as empty:
        try:
            done = judge_cli.run_subprocess(argv, input=user, capture_output=True, text=True,
                                            timeout=judge_cli.TIMEOUT_S, cwd=empty, env=judge_cli._env())
            stdout, stderr, code = done.stdout or "", done.stderr or "", done.returncode
        except judge_cli.subprocess.TimeoutExpired:
            error = "cli_timeout"
        except OSError:
            error = "cli_exec_failed"
    envelope = judge_cli._envelope(stdout)
    result = envelope.get("result") if isinstance(envelope, dict) else None
    if error is None:
        error = judge_cli._error_kind(code, stdout, stderr, envelope, result)
    tools.write_file(f"{out_dir}/{stem}.response.txt", stdout.encode("utf-8"))
    reported = judge_cli._reported_models(envelope)
    meta = {"cli_version": judge_cli.CliJudge().version(), "model_requested": model, "model_reported": reported,
            "called_at_utc": called_at, "exit_code": code, "error": error, "stderr": stderr,
            "usage": envelope.get("usage") if isinstance(envelope, dict) else None}
    tools.write_file(f"{out_dir}/{stem}.meta.json", (json.dumps(meta, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    return {"result": result, "error": error, "model": judge_cli._pick_model(reported, model), "called_at": called_at}
