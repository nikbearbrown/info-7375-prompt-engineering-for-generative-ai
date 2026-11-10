"""The Claude judge (CONTRACT.md, Out: Claude's judgment and its fixed format; Refuses 3, 5). A judgment.

Claude answers through the Claude Code CLI on the author's claude.ai seat; there is no API key. The CLI is
locked down the way Klaxon's adapter does it (credited in SOURCES.md):

- No tools (--tools ""), no MCP servers (--strict-mcp-config with an empty list), no skills, none of this Mac's
  customizations (--safe-mode) and no user, project or local settings (--restricted), nobody asked for
  permission (dontAsk, --permission-prompts none), and no transcript kept (--no-session-persistence).
- Its first event, the CLI's own account of what it loaded, must list no tools, no MCP servers, no skills and no
  slash commands, only the CLI's known built-in plugins, the empty temporary folder this call made, the seat's login
  (apiKeySource "none") and dontAsk. That event does not list memory files (CLI 2.1.309), so the input-token count
  is checked instead: more than the characters sent explain means something else was loaded. The reply must be one
  turn with no tool use. Anything else makes the call fail: the verdict is "no valid judgment".
- It runs in a new empty temporary folder with a small environment (no API key, no API address, no proxy).
- The data goes in on stdin inside a tag made from the data's own hash. Every "@" is sent as a fullwidth one,
  because Claude Code attaches files named in "@path" mentions. Hidden characters are dropped.

Then OUR validator checks the answer against the contract's fixed format. There is no retry: a rejected
answer is saved, and the verdict is "no valid judgment". Every call is saved, whatever happened.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from . import resume as resume_mod

DEFAULT_MODEL = "claude-sonnet-5-5"
TIMEOUT_SECONDS = 180
MAX_OUTPUT = 5_000_000
POSTING_FIELDS = ("title", "location", "secondaryLocations", "workplaceType", "employmentType", "descriptionPlain")
ANSWER_KEYS = ("verdict", "justification", "resume_fields", "posting_fields", "quotes")
VERDICTS = ("relevant", "not_relevant")
MAX_JUSTIFICATION = 600
MAX_QUOTES = 3
MAX_SENTENCES = 3
# Claude Code adds about 2,000 tokens of its own to a call: measured on the 66 calls of 2026-10-30, 1,866 to 2,313
# above one token per four characters sent. A context the size of a memory file would pass this allowance.
OVERHEAD_TOKENS = 3_500
# Built-in plugins trusted by name. The first three were built into Claude Code 2.1.309 (JS1). The desktop app
# moved to 2.1.317, which adds cc-plugin-privacy; it was trusted on 2026-11-08 by my decision, after one call
# showed it loads no tools, MCP servers, skills or slash commands. What it does inside a call is not checked.
KNOWN_PLUGINS = ("cc-plugin-sec-default", "cc-plugin-agents-md", "cc-plugin-plugin-authoring", "cc-plugin-privacy")
FULLWIDTH_AT = "＠"
SEAT = "none"  # the init event's apiKeySource when the CLI uses a claude.ai login, not an API key
PERMISSION_MODE = "dontAsk"
APP_COPIES = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code"
APP_BINARY = "claude.app/Contents/MacOS/claude"

OUTPUT = ("--print", "--output-format", "stream-json", "--verbose")
LOCKDOWN = (
    "--tools", "",
    "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
    "--disable-slash-commands",
    "--safe-mode",
    "--restricted",
    "--permission-mode", PERMISSION_MODE,
    "--permission-prompts", "none",
    "--no-session-persistence",
)
PASSED_ON = ("HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE", "CLAUDE_CONFIG_DIR")
FIXED_ENV = {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "DISABLE_AUTOUPDATER": "1",
    "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
}
SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
LEFT_OUT_EVENTS = ("rate_limit_event",)  # the seat's usage state is about the account, not the call


class CallFailed(Exception):
    """The CLI call did not produce a usable reply. The verdict becomes "no valid judgment"."""


# What is sent.

def find_claude(env=os.environ, copies: Path = APP_COPIES) -> Path:
    """JOB_AGENT_CLAUDE if set, else `claude` on the PATH, else the newest copy the Claude desktop app keeps."""
    configured = env.get("JOB_AGENT_CLAUDE")
    if configured:
        return Path(configured).expanduser()
    on_path = shutil.which("claude", path=env.get("PATH"))
    if on_path:
        return Path(on_path)
    found = [p for p in Path(copies).glob(f"*/*/{APP_BINARY}") if p.is_file() and os.access(p, os.X_OK)]
    if not found:
        raise CallFailed("Claude Code was not found: set JOB_AGENT_CLAUDE to its path")

    def version(path):
        try:
            return tuple(int(part) for part in path.relative_to(copies).parts[0].split("."))
        except ValueError:
            return (-1,)

    return max(found, key=version)


def shown(text: str) -> str:
    """Text as Claude gets it: hidden characters dropped, "@" written as a fullwidth at sign."""
    kept = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch) not in ("Cc", "Cf"))
    return kept.replace("@", FULLWIDTH_AT)


def shown_value(value):
    if isinstance(value, str):
        return shown(value)
    if isinstance(value, list):
        return [shown_value(v) for v in value]
    if isinstance(value, dict):
        return {shown(str(k)): shown_value(v) for k, v in value.items()}
    return value


def build_request(job: dict, resume: dict) -> dict:
    """The data block: the posting's six fields and the résumé without contact fields, as Claude will see them."""
    data = {
        "posting": {field: shown_value(job.get(field)) for field in POSTING_FIELDS},
        "resume": shown_value(resume_mod.for_claude(resume)),
    }
    body = json.dumps(data, indent=1, ensure_ascii=False)
    tag = "data-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    user = (f"Judge the posting for this résumé. The data block is between the <{tag}> and </{tag}> lines; "
            f"each at sign in it is written as a fullwidth {FULLWIDTH_AT}.\n<{tag}>\n{body}\n</{tag}>\n")
    return {"data": data, "user": user}


def command(binary, model: str, system: str) -> list:
    return [str(binary), *OUTPUT, "--model", model, "--system-prompt", system, *LOCKDOWN]


def environment(binary, source=os.environ) -> dict:
    env = {name: source[name] for name in PASSED_ON if name in source}
    env.update(FIXED_ENV)
    env["PATH"] = f"{Path(binary).parent}{os.pathsep}{SYSTEM_PATH}"
    return env


# One call.

def run_cli(argv: list, stdin: bytes, cwd: str, env: dict, timeout: float = TIMEOUT_SECONDS) -> dict:
    """Run the CLI once and return its raw output. The whole process group is killed at the deadline."""
    started = time.monotonic()
    proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = proc.communicate(input=stdin, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        out, err = proc.communicate()
        timed_out = True
    finally:
        _kill_group(proc)
    return {"stdout": out, "stderr": err, "exit_code": proc.returncode, "timed_out": timed_out,
            "seconds": round(time.monotonic() - started, 2)}


def _kill_group(proc) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def read_reply(raw: dict, folder: str, chars_sent: int) -> dict:
    """Check the CLI's own events and return the reply text and model, or raise CallFailed with the reason."""
    if raw["timed_out"]:
        raise CallFailed(f"no reply within {TIMEOUT_SECONDS} s; Claude Code was stopped")
    if len(raw["stdout"]) > MAX_OUTPUT:
        raise CallFailed("Claude Code wrote more output than one answer needs")
    events = []
    for line in raw["stdout"].decode("utf-8", "replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and isinstance(event.get("type"), str):
            events.append(event)
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    if init is None:
        raise CallFailed("Claude Code did not say what it loaded")
    reason = _loaded(init, folder)
    if reason:
        raise CallFailed(reason)
    for event in events:
        message = event.get("message") if isinstance(event.get("message"), dict) else {}
        content = message.get("content") if isinstance(message.get("content"), list) else []
        for block in content:
            if isinstance(block, dict) and block.get("type") in ("tool_use", "server_tool_use", "mcp_tool_use",
                                                                 "tool_result", "mcp_tool_result"):
                raise CallFailed("the reply used a tool")
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if result is None:
        raise CallFailed(f"Claude Code stopped without a result (exit code {raw['exit_code']})")
    if result.get("subtype") != "success" or result.get("is_error") is not False:
        raise CallFailed(f"Claude Code reported an error ({str(result.get('subtype'))[:40]})")
    if result.get("num_turns") != 1:
        raise CallFailed(f"Claude Code took {result.get('num_turns')} turns for one answer")
    if result.get("permission_denials"):
        raise CallFailed("Claude Code was refused a permission: something tried to run")
    if raw["exit_code"] != 0:
        raise CallFailed(f"Claude Code exited with code {raw['exit_code']}")
    usage = result.get("usage")
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int):
        raise CallFailed("Claude Code did not report how many input tokens the call read")
    tokens = sum(usage.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    if tokens > chars_sent / 4 + OVERHEAD_TOKENS:
        raise CallFailed(f"the call read {tokens} input tokens, more than the {chars_sent} characters sent explain")
    text = result.get("result")
    if not isinstance(text, str):
        raise CallFailed("Claude Code's result has no text")
    models = {e["message"].get("model") for e in events if e.get("type") == "assistant" and isinstance(e.get("message"), dict)}
    if len(models) != 1 or not isinstance(next(iter(models)), str):
        raise CallFailed("the reply does not name the one model that wrote it")
    return {"text": text, "model": models.pop(), "init": init, "result": result, "events": events}


def _loaded(init: dict, folder: str):
    tools, servers, cwd = init.get("tools"), init.get("mcp_servers"), init.get("cwd")
    if not isinstance(tools, list) or not isinstance(servers, list) or not isinstance(cwd, str):
        return "Claude Code did not say which tools, MCP servers and folder it uses"
    if tools:
        return f"Claude Code loaded {len(tools)} tool(s)"
    if servers:
        return f"Claude Code loaded {len(servers)} MCP server(s)"
    for key in ("skills", "slash_commands"):
        if not isinstance(init.get(key), list):
            return f"Claude Code did not say which {key.replace('_', ' ')} it loaded"
        if init[key]:
            return f"Claude Code loaded {len(init[key])} {key.replace('_', ' ')}"
    plugins = init.get("plugins")
    if not isinstance(plugins, list):
        return "Claude Code did not say which plugins it loaded"
    unknown = [p for p in plugins if not (isinstance(p, dict) and p.get("path") == "builtin" and p.get("name") in KNOWN_PLUGINS)]
    if unknown:
        return f"Claude Code loaded {len(unknown)} plugin(s) other than its known built-in ones"
    if any(isinstance(p, str) and p.strip() for p in init.get("memory_paths") or []):
        return "Claude Code loaded memory files"
    if os.path.realpath(cwd) != os.path.realpath(folder):
        return "Claude Code is not working in the empty folder made for this call"
    if init.get("apiKeySource") != SEAT:
        return "Claude Code is not signed in with the seat's own login"
    if init.get("permissionMode") != PERMISSION_MODE:
        return f"Claude Code is not in the {PERMISSION_MODE} permission mode"
    return None


# Our validator (CONTRACT.md, Out: "The validator rejects anything else").

def validate(text: str, sent: dict) -> tuple:
    """(answer, problems): the answer object, and every reason it breaks the fixed format. Valid when no problems."""
    try:
        answer = json.loads(text, object_pairs_hook=_each_key_once)
    except (TypeError, ValueError):
        return None, ["the answer is not one JSON object with each key once"]
    if not isinstance(answer, dict):
        return None, ["the answer is not one JSON object"]
    problems = []
    keys = set(answer)
    if keys != set(ANSWER_KEYS):
        missing, extra = sorted(set(ANSWER_KEYS) - keys), sorted(keys - set(ANSWER_KEYS))
        problems.append(f"keys are wrong (missing {missing}, extra {extra})")
    if answer.get("verdict") not in VERDICTS:
        problems.append("verdict is not relevant or not_relevant")
    justification = answer.get("justification")
    if not isinstance(justification, str) or not justification.strip():
        problems.append("justification is empty")
    elif len(justification) > MAX_JUSTIFICATION:
        problems.append(f"justification is over {MAX_JUSTIFICATION} characters")
    elif sentence_count(justification) > MAX_SENTENCES:
        problems.append(f"justification has more than {MAX_SENTENCES} sentences")
    allowed = {"resume_fields": resume_mod.field_paths(sent["resume"]),
               "posting_fields": set(POSTING_FIELDS) | resume_mod.field_paths(sent["posting"])}
    for key in ("resume_fields", "posting_fields"):
        fields = answer.get(key)
        if not isinstance(fields, list) or not fields:
            problems.append(f"{key} is empty")
            continue
        unknown = [f for f in fields if not isinstance(f, str) or f not in allowed[key]]
        if unknown:
            problems.append(f"{key} names fields that were not sent: {unknown[:3]}")
    quotes = answer.get("quotes")
    if not isinstance(quotes, list) or len(quotes) > MAX_QUOTES:
        problems.append(f"quotes is not a list of at most {MAX_QUOTES}")
    else:
        texts = [_plain(t) for t in _strings(sent["posting"])]
        for quote in quotes:
            if not isinstance(quote, str) or not quote.strip() or not any(_plain(quote) in t for t in texts):
                problems.append("a quote does not appear word for word in the posting sent")
                break
    return answer, problems


def _each_key_once(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("a key appears twice")
    return dict(pairs)


# A sentence ends at ".", "!" or "?" (or one followed by a closing quote) before a space and a capital letter, a
# quote or a parenthesis, but not after an initialism such as "U.S." or after "e.g." or "i.e.".
_SENTENCE_END = re.compile(r'(?:(?<![.\s][A-Z]\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<=[.!?])|(?<=[.!?]["\u201d]))\s+(?=[A-Z"(\u201c])')


def sentence_count(text: str) -> int:
    return len([piece for piece in _SENTENCE_END.split(text.strip()) if piece.strip()])


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)


def _plain(text: str) -> str:
    """Runs of whitespace collapsed, and either at sign read as one, for comparing a quote with the posting."""
    return re.sub(r"\s+", " ", text.replace(FULLWIDTH_AT, "@")).strip()


# The judge, end to end, with its record.

def judge(job: dict, resume: dict, *, prompt_path: Path, record_dir: Path, model: str = DEFAULT_MODEL,
          runner=run_cli, binary=None, label: str = "") -> dict:
    """Claude's judgment of one posting, saved to record_dir before it is returned."""
    system = Path(prompt_path).read_text(encoding="utf-8")
    request = build_request(job, resume)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    record = {
        "posting_id": job.get("id"), "posting_title": job.get("title"), "label": label,
        "prompt": {"file": Path(prompt_path).name, "sha256": hashlib.sha256(system.encode("utf-8")).hexdigest()},
        "model_requested": model, "started_at": started, "sent": {"user": request["user"], "data": request["data"]},
    }
    verdict = {"judge": "claude", "label": "judgment", "verdict": None, "valid": False, "model": None,
               "date": started[:10], "prompt": record["prompt"]}
    try:
        binary = Path(binary) if binary else find_claude()
        with tempfile.TemporaryDirectory(prefix="job-agent-claude-") as folder:
            argv = command(binary, model, system)
            record["command"] = [_tilde(arg) for arg in
                                 command(binary, model, f"<the system prompt in prompts/{Path(prompt_path).name}>")]
            record["environment"] = sorted(environment(binary))
            raw = runner(argv, request["user"].encode("utf-8"), folder, environment(binary))
            record.update(exit_code=raw["exit_code"], seconds=raw["seconds"], timed_out=raw["timed_out"],
                          stderr_tail=_tilde(raw["stderr"].decode("utf-8", "replace")[-1500:]))
            record["events"] = _for_the_record(raw["stdout"])
            reply = read_reply(raw, folder, len(system) + len(request["user"]))
        record.update(answer_text=reply["text"], model=reply["model"],
                      claude_code=_init_summary(reply["init"]), cost_usd=reply["result"].get("total_cost_usd"))
        answer, problems = validate(reply["text"], request["data"])
        record["validation"] = {"valid": not problems, "problems": problems}
        verdict["model"] = reply["model"]
        if problems:
            verdict["reason"] = "the answer failed the validator: " + "; ".join(problems)
        else:
            verdict.update(valid=True, verdict=answer["verdict"], justification=answer["justification"],
                           resume_fields=answer["resume_fields"], posting_fields=answer["posting_fields"],
                           quotes=answer["quotes"])
    except CallFailed as exc:
        verdict["reason"] = f"the call failed: {exc}"
        record["validation"] = {"valid": False, "problems": [str(exc)]}
    except OSError as exc:
        verdict["reason"] = f"the call failed: Claude Code could not be run ({type(exc).__name__})"
        record["validation"] = {"valid": False, "problems": [verdict["reason"]]}
    record["verdict"] = {k: verdict.get(k) for k in ("verdict", "valid", "reason")}
    verdict["record"] = f"{Path(record_dir).name}/{_save(record, Path(record_dir), job.get('id') or '', label)}"
    verdict["lines"] = _lines(verdict)
    return verdict


def _tilde(text: str) -> str:
    """This Mac's home folder written as ~, so a record never names the account."""
    home = str(Path.home())
    return text.replace(home, "~") if len(home) > 1 else text


def _for_the_record(stdout: bytes) -> list:
    home = str(Path.home())
    kept = []
    for line in stdout.decode("utf-8", "replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            kept.append({"unreadable_line": line[:500]})
            continue
        if isinstance(event, dict) and event.get("type") in LEFT_OUT_EVENTS:
            continue
        kept.append(json.loads(json.dumps(event).replace(home, "~")) if len(home) > 1 else event)
    return kept


def _init_summary(init: dict) -> dict:
    return {k: init.get(k) for k in ("claude_code_version", "model", "apiKeySource", "permissionMode", "tools",
                                     "mcp_servers", "memory_paths")}


def _save(record: dict, folder: Path, posting_id: str, label: str) -> str:
    folder.mkdir(parents=True, exist_ok=True)
    stem = (label + "-" if label else "") + hashlib.sha256(posting_id.encode("utf-8")).hexdigest()[:10]
    path = folder / f"{stem}.json"
    n = 2
    while path.exists():  # never overwrite an earlier call
        path = folder / f"{stem}-{n}.json"
        n += 1
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path.name


def _lines(verdict: dict) -> list:
    if not verdict["valid"]:
        return [f"No valid judgment: {verdict.get('reason')}", f"Call saved as {verdict['record']}."]
    return [
        f"Justification: {verdict['justification']}",
        f"Résumé fields cited: {', '.join(verdict['resume_fields'])}",
        f"Posting fields cited: {', '.join(verdict['posting_fields'])}",
        "Quotes: " + ("; ".join(f'"{q}"' for q in verdict["quotes"]) or "none"),
        f"Model {verdict['model']}, {verdict['date']}, prompt {verdict['prompt']['file']} "
        f"(SHA-256 {verdict['prompt']['sha256'][:12]}); call saved as {verdict['record']}.",
    ]
