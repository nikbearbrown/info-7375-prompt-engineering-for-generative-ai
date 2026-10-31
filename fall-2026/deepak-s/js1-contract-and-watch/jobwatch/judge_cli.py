"""The claude-cli judge backend: Amendment A14.

One `claude -p` subprocess per call, from a new empty temporary directory, with the System section
replacing the system prompt, no tools, no MCP servers, safe mode (no CLAUDE.md, hooks, plugins or
skills), the model pinned, ANTHROPIC_API_KEY removed from its environment, and a 120 s timeout.
Temperature and max_tokens cannot be set through the CLI. A failed call stops the judge: it is
never retried, and the command makes no further calls.

`run_subprocess` and `which` are module attributes so tests can replace them with fakes.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from jobwatch.evidence import utc_iso
from jobwatch.judge import _judgment, judge_text
from jobwatch.prompt import fill_user

CLI = "claude"
TIMEOUT_S = 120
VERSION_TIMEOUT_S = 20
REMOVED_ENV = ("ANTHROPIC_API_KEY",)
_USAGE_LIMIT = re.compile(r"usage limit|limit reached|hit your limit|out of (extra )?usage", re.IGNORECASE)

run_subprocess = subprocess.run
which = shutil.which


def cli_argv(system, model):
    return [CLI, "-p", "--output-format", "json", "--system-prompt", system, "--tools", "",
            "--strict-mcp-config", "--safe-mode", "--disable-slash-commands", "--no-session-persistence",
            "--model", model]


class CliJudge:
    name = "claude-cli"
    unavailable_reason = "claude_cli_not_found"

    def __init__(self):
        self.stopped = None  # {"posting_id", "reason"} once a call has failed
        self._version = None

    def available(self):
        return which(CLI) is not None

    def request(self, prompt, model, resume, posting_id, posting_doc):
        return {
            "backend": self.name,
            "argv": cli_argv(prompt.system, model),
            "stdin": fill_user(prompt, resume, posting_id, posting_doc),
            "cwd": "a new empty temporary directory",
            "env_removed": list(REMOVED_ENV),
            "timeout_s": TIMEOUT_S,
        }

    def version(self):
        if self._version is None:
            try:
                done = run_subprocess([CLI, "--version"], capture_output=True, text=True,
                                      timeout=VERSION_TIMEOUT_S, env=_env())
                self._version = done.stdout.strip() or f"unknown (exit {done.returncode})"
            except (OSError, subprocess.TimeoutExpired):
                self._version = "unknown"
        return self._version

    def call(self, prompt, model, resume, posting_id, posting_doc, out_dir, clock, stem=None):
        stem = stem or posting_id
        request = self.request(prompt, model, resume, posting_id, posting_doc)
        out_dir.write_json(f"claude/{stem}.request.json", request)
        version = self.version()
        called_at = utc_iso(clock())
        stdout, stderr, code, error = "", "", None, None
        with tempfile.TemporaryDirectory(prefix="jobwatch-judge-") as empty:
            try:
                done = run_subprocess(request["argv"], input=request["stdin"], capture_output=True, text=True,
                                      timeout=TIMEOUT_S, cwd=empty, env=_env())
                stdout, stderr, code = done.stdout or "", done.stderr or "", done.returncode
            except subprocess.TimeoutExpired as e:
                stdout, stderr, error = _text(e.stdout), _text(e.stderr), "cli_timeout"
            except OSError:
                error = "cli_exec_failed"

        envelope = _envelope(stdout)
        result = envelope.get("result") if isinstance(envelope, dict) else None
        if error is None:
            error = _error_kind(code, stdout, stderr, envelope, result)
        raw_path = out_dir.write(f"claude/{stem}.response.txt", stdout) if stdout else None
        reported = _reported_models(envelope)
        used_model = _pick_model(reported, model)
        out_dir.write_json(f"claude/{stem}.response.meta.json", {
            "backend": self.name,
            "cli_version": version,
            "model": reported,
            "session_id": envelope.get("session_id") if isinstance(envelope, dict) else None,
            "usage": envelope.get("usage") if isinstance(envelope, dict) else None,
            "exit_code": code,
            "stop_reason": envelope.get("stop_reason") if isinstance(envelope, dict) else None,
            "error": error,
            "stderr": stderr,
            "called_at": called_at,
        })
        if error:
            self.stopped = {"posting_id": posting_id, "reason": error}
            return _judgment("error", error, used_model, called_at, raw_path)
        return judge_text(result, envelope.get("stop_reason"), used_model, called_at, raw_path,
                          posting_id, resume, posting_doc)

    def saved(self, directory, stem, posting_id, resume, posting_doc, raw_path):
        """Re-validate a saved call from its files; None if no call was made."""
        claude = Path(directory) / "claude"
        meta_file = claude / f"{stem}.response.meta.json"
        if not meta_file.exists():
            return None
        meta = json.loads(meta_file.read_bytes())
        text_file = claude / f"{stem}.response.txt"
        stdout = text_file.read_bytes().decode("utf-8") if text_file.exists() else ""
        envelope = _envelope(stdout)
        used_model = _pick_model(meta.get("model") or [], _requested_model(claude / f"{stem}.request.json"))
        saved_raw_path = raw_path if text_file.exists() else None
        if meta.get("error"):
            return _judgment("error", meta["error"], used_model, meta.get("called_at"), saved_raw_path)
        return judge_text(envelope.get("result"), envelope.get("stop_reason"), used_model, meta.get("called_at"),
                          saved_raw_path, posting_id, resume, posting_doc)


def _env():
    return {k: v for k, v in os.environ.items() if k not in REMOVED_ENV}


def _text(data):
    if data is None:
        return ""
    return data.decode("utf-8", "replace") if isinstance(data, bytes) else data


def _envelope(stdout):
    try:
        envelope = json.loads(stdout)
    except ValueError:
        return {}
    return envelope if isinstance(envelope, dict) else {}


def _error_kind(code, stdout, stderr, envelope, result):
    """cli_<kind> for a failed call, or None. Only a failed or non-JSON-looking result is scanned for a limit."""
    failed = code != 0 or envelope.get("is_error") is True
    looks_like_limit = isinstance(result, str) and not result.lstrip().startswith("{") and _USAGE_LIMIT.search(result)
    if (failed and _USAGE_LIMIT.search(f"{stdout}\n{stderr}")) or looks_like_limit:
        return "cli_usage_limit"
    if code != 0:
        return "cli_nonzero_exit"
    if envelope.get("is_error") is True:
        return "cli_error_result"
    if not isinstance(result, str):
        return "cli_bad_output"
    return None


def _reported_models(envelope):
    usage = envelope.get("modelUsage") if isinstance(envelope, dict) else None
    if isinstance(usage, dict) and usage:
        return sorted(usage)
    model = envelope.get("model") if isinstance(envelope, dict) else None
    return [model] if isinstance(model, str) else []


def _pick_model(reported, requested):
    """The model the CLI reports: the only one, or the one matching the requested name."""
    if len(reported) == 1:
        return reported[0]
    matching = [m for m in reported if requested and m.startswith(requested)]
    if len(matching) == 1:
        return matching[0]
    return ",".join(reported) if reported else requested


def _requested_model(request_file):
    try:
        argv = json.loads(request_file.read_bytes())["argv"]
        return argv[argv.index("--model") + 1]
    except (OSError, ValueError, KeyError, IndexError):
        return None
