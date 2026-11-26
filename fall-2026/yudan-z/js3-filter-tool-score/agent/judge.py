"""Contract §7: the Claude judge. Fixed output format + a validator that rejects anything else.
Claude is called through the Claude Code CLI in print mode (`claude -p`), one fresh conversation per call."""
import json
import os
import shutil
import subprocess

from agent import rule

RESUME_FIELDS = {"target_roles", "experience_years", "education", "work_authorization", "skills", "location"}
POSTING_FIELDS = {"title", "location", "content"}
VERDICTS = {"relevant", "not_relevant"}

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


class InvalidAnswer(ValueError):
    pass


def validate_answer(text):
    """Accept exactly one JSON object in the §7 format, else raise. Never repair or guess."""
    t = (text or "").strip()
    if not (t.startswith("{") and t.endswith("}")):
        raise InvalidAnswer("not a bare JSON object (extra text around it)")
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as e:
        raise InvalidAnswer(f"not valid JSON: {e}")
    if set(obj) != {"verdict", "resume_fields", "posting_fields", "justification"}:
        raise InvalidAnswer(f"wrong keys: {sorted(obj)}")
    if obj["verdict"] not in VERDICTS:
        raise InvalidAnswer(f"verdict {obj['verdict']!r} not in {sorted(VERDICTS)}")
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        v = obj[key]
        if not (isinstance(v, list) and v):
            raise InvalidAnswer(f"{key} is empty: the justification must cite fields")
        bad = [x for x in v if x not in allowed]
        if bad:
            raise InvalidAnswer(f"{key} names unknown fields: {bad}")
    j = obj["justification"]
    if not isinstance(j, str) or not j.strip() or len(j) > 400:
        raise InvalidAnswer("justification empty or over 400 characters")
    obj["label"] = "model-judgment"
    return obj


def build_prompt(posting, resume, prompt_file="contract_v1.txt"):
    with open(os.path.join(PROMPT_DIR, prompt_file), encoding="utf-8") as f:
        template = f.read()
    return (template.replace("{{SKILLS}}", json.dumps(resume["skills"]))
                    .replace("{{TARGET_ROLES}}", json.dumps(resume["target_roles"]))
                    .replace("{{RESUME_FACTS}}", json.dumps({"experience_years": resume["experience_years"],
                                                             "education": [{k: e.get(k) for k in ("degree", "graduation", "graduation_latest") if e.get(k)} for e in resume["education"]],
                                                             "work_authorization": resume["work_authorization"]}))
                    .replace("{{TITLE}}", posting.get("title", ""))
                    .replace("{{LOCATION}}", (posting.get("location") or {}).get("name", ""))
                    .replace("{{CONTENT}}", rule.plain(posting.get("content", ""))))


def claude_cli():
    exe = shutil.which("claude")
    if exe:
        return exe
    for cand in (os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
                 os.path.expandvars(r"%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\npm\claude.cmd")):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError("Claude Code CLI not found; install it and log in (see README)")


def ask_claude(prompt):
    """One fresh conversation: `claude -p` with no tools, prompt on stdin. Returns raw text."""
    r = subprocess.run([claude_cli(), "-p", "--output-format", "text", "--disallowedTools", "Bash,Edit,Write,WebFetch,WebSearch,Read"],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=240)
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {r.stderr.strip()[:300]}")
    return r.stdout


def judge(posting, resume, prompt_file="contract_v1.txt", asker=ask_claude):
    raw = asker(build_prompt(posting, resume, prompt_file))
    try:
        out = validate_answer(raw)
        out["status"] = "valid"
    except InvalidAnswer as e:
        out = {"status": "invalid", "label": "model-judgment", "error": str(e), "verdict": None}
    out["raw"] = raw
    return out
