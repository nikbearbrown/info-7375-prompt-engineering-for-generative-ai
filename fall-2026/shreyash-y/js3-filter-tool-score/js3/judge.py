"""The Claude judge, inherited from JS1 (jsagent/claude_judge.py and jsagent/validator.py at bb193d9),
used here only for the one-change-at-a-time experiments (SCORE.md). Its verdict is a JUDGMENT and is
always labeled as one.

Each call is one fresh `claude -p` conversation from an empty temporary folder, with no settings files
(no plugins, hooks or CLAUDE.md), no built-in tools and no saved session, exactly as in JS1. Changes
from JS1, shared by every condition so they are not one of the things compared:
  - posting_id is the posting key (board:id) as a string, because Ashby and Lever ids are not
    integers; the prompt's words "as an integer" become "exactly as given, as a string" at build time
    (the prompt files themselves are JS1's, byte for byte: their sha256 is recorded with every call);
  - the validator accepts "I cannot tell" only when the prompt's own format allows it.
"""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile

from jsagent import persona as js_persona
from js3 import offer

HERE = pathlib.Path(__file__).resolve().parent.parent
KEYS = {"posting_id", "verdict", "failed_conditions", "resume_fields", "posting_fields", "justification"}
RESUME_FIELDS = {"target_roles", "experience_years", "skills", "location", "remote_ok", "exclusions"}
POSTING_FIELDS = {"id", "title", "departments", "location", "offices", "content"}
ID_LINE = '"posting_id": <the posting\'s id, as an integer>'
ID_LINE_JS3 = '"posting_id": <the posting\'s id, exactly as given, as a string>'


def load_prompt(path):
    text = (HERE / path).read_text()
    system, user = text.split("=== USER ===", 1)
    assert ID_LINE in system, path
    return system.strip().replace(ID_LINE, ID_LINE_JS3), user.strip(), hashlib.sha256(text.encode()).hexdigest()


def posting_for_model(p):
    view = {k: p[k] for k in ("title", "departments", "location", "offices", "content")}
    return {"id": p["key"], **view}


def build(prompt_path, p):
    system, user, digest = load_prompt(prompt_path)
    resume = js_persona.public_view(json.loads((HERE / "persona" / "alex_morgan.json").read_text()))
    user = (user.replace("{RESUME}", json.dumps(resume, indent=1, ensure_ascii=False))
                .replace("{POSTING}", json.dumps(posting_for_model(p), indent=1, ensure_ascii=False)))
    return system, user, digest


def validate(text, expected_id, allow_unsure):
    """JS1's validator, with a string posting_id and an optional third verdict."""
    s = (text or "").strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None, ["output is not a bare JSON object (no prose, no code fences)"]
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        return None, [f"not valid JSON: {e.msg}"]
    if not isinstance(obj, dict) or set(obj) != KEYS:
        return None, ["keys wrong"]
    errors = []
    if obj["posting_id"] != expected_id:
        errors.append(f"posting_id {obj['posting_id']!r} is not the posting asked about ({expected_id})")
    verdicts = {"Relevant", "Not Relevant"} | ({"I cannot tell"} if allow_unsure else set())
    if obj["verdict"] not in verdicts:
        errors.append(f"verdict {obj['verdict']!r} not in {sorted(verdicts)}")
    fc = obj["failed_conditions"]
    if not (isinstance(fc, list) and all(isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= 6 for n in fc)
            and len(fc) == len(set(fc))):
        errors.append("failed_conditions must be distinct integers 1-6")
    elif (obj["verdict"] == "Relevant") != (len(fc) == 0):
        errors.append("verdict must be Relevant exactly when failed_conditions is empty")
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        v = obj[key]
        if not (isinstance(v, list) and v and all(isinstance(x, str) for x in v)) or set(v) - allowed:
            errors.append(f"{key} must be a non-empty list of known field names")
    if not isinstance(obj["justification"], str) or len(obj["justification"].strip()) < 20:
        errors.append("justification must be a sentence or more")
    return (None, errors) if errors else (obj, [])


def squash(s):
    return re.sub(r"\s+", " ", s or "").strip()


def quotes_in(justification):
    return [q for q in re.findall(r'"([^"]{3,})"', justification or "") if q.lower() != "not stated"]


QUOTE_MARKS = str.maketrans({"\u201c": "'", "\u201d": "'", "\u2018": "'", "\u2019": "'", '"': "'"})


def normal(s):
    """For the second, normalized check: quote marks made alike, trailing punctuation dropped."""
    return squash(s).translate(QUOTE_MARKS).lower().rstrip(",.;:!? ")


def made_up_quotes_normalized(justification, p):
    hay = normal(" ".join([p["title"], p["location"], " ".join(p["offices"]), " ".join(p["departments"]), p["content"]]))
    return [q for q in quotes_in(justification) if normal(q) not in hay]


def made_up_quotes(justification, p):
    """WV4 on a real model: double-quoted text in the justification that is in none of the posting's fields."""
    hay = squash(" ".join([p["title"], p["location"], " ".join(p["offices"]), " ".join(p["departments"]), p["content"]])).lower()
    return [q for q in quotes_in(justification) if squash(q).lower() not in hay]


def call(system, user, model, with_tool=False, timeout=300):
    with tempfile.TemporaryDirectory(prefix="js3-judge-") as empty:
        cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--strict-mcp-config",
               "--setting-sources", "", "--system-prompt", system]
        if with_tool:
            cfg = pathlib.Path(empty) / "mcp-config.json"
            cfg.write_text(json.dumps(offer.config()))
            cmd += ["--mcp-config", str(cfg), "--allowedTools", "mcp__js3__score_posting",
                    "--output-format", "stream-json", "--verbose"]
        else:
            cmd += ["--output-format", "json"]
        proc = subprocess.run(cmd, input=user, capture_output=True, text=True, timeout=timeout, cwd=empty)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:300]}")
    if not with_tool:
        out = json.loads(proc.stdout)
        return out, 0
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    out = next(e for e in reversed(events) if e.get("type") == "result")
    tool_calls = sum(1 for e in events if e.get("type") == "assistant"
                     for c in e["message"]["content"] if c.get("type") == "tool_use")
    return out, tool_calls


def judge(condition, prompt_path, model, p, with_tool=False):
    system, user, digest = build(prompt_path, p)
    called_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    out, tool_calls = call(system, user, model, with_tool)
    text = out.get("result", "")
    allow_unsure = "I cannot tell" in system
    parsed, errors = validate(text, p["key"], allow_unsure)
    return {"judge": "Claude (judgment, not a fact)", "condition": condition, "called_at": called_at,
            "model": ",".join(sorted((out.get("modelUsage") or {}).keys())) or model,
            "prompt_file": prompt_path, "prompt_sha256": digest, "with_tool": with_tool, "tool_calls": tool_calls,
            "posting_key": p["key"], "raw_text": text, "valid": not errors, "errors": errors, "parsed": parsed,
            "made_up_quotes": made_up_quotes(parsed["justification"], p) if parsed else None,
            "session_id": out.get("session_id"), "cost_usd": out.get("total_cost_usd"),
            "duration_ms": out.get("duration_ms")}
