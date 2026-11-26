"""Claude's judgment (CONTRACT.md section 2): a fixed JSON format and a validator that rejects anything else.

The judgment is an opinion. It is stored next to the rule's record and never replaces it.
"""

import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from string import Template

from js3.rule import description_text

LABEL = "Claude judgment — opinion, not fact"
KEYS = {"label", "verdict", "reason"}
VERDICTS = ("MATCH", "NOT_MATCH")
MODEL = "claude-opus-5-5"
SYSTEM = "You judge job postings for a coursework project. Follow the reply format exactly."
BASELINE = Path(__file__).resolve().parent.parent / "prompts" / "baseline-v1.txt"


def _no_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate key in JSON object")
    return dict(pairs)


def validate(reply):
    """Return (True, parsed) for exactly one valid judgment object, else (False, reason rejected)."""
    try:
        value = json.loads(reply.strip(), object_pairs_hook=_no_duplicate_keys)
    except (AttributeError, ValueError) as error:
        return False, "not exactly one JSON object: %s" % error
    if not isinstance(value, dict):
        return False, "not a JSON object"
    if set(value) != KEYS:
        return False, "keys must be exactly label, verdict, reason; got %s" % sorted(value)
    if value["label"] != "CLAUDE_JUDGMENT":
        return False, "label must be CLAUDE_JUDGMENT"
    if not isinstance(value["verdict"], str) or value["verdict"] not in VERDICTS:
        return False, "verdict must be MATCH or NOT_MATCH"
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        return False, "reason must be non-empty text"
    return True, value


def resume_for_prompt(resume):
    """The résumé without name, email, phone, linkedin or github (CONTRACT.md section 3)."""
    return {
        "location": resume.get("personal", {}).get("location"),
        "education": [{k: e.get(k) for k in ("degree", "institution", "end_date", "status")}
                      for e in resume.get("education", [])],
        "experience": [{k: e.get(k) for k in ("title", "company", "start_date", "end_date", "bullets")}
                       for e in resume.get("experience", [])],
        "projects": [{k: p.get(k) for k in ("name", "bullets")} for p in resume.get("projects", [])],
        "skills": {k: v for k, v in resume.get("skills", {}).items() if isinstance(v, list)},
    }


def build_prompt(posting, resume, template_path=BASELINE):
    return Template(Path(template_path).read_text(encoding="utf-8")).substitute(
        resume=json.dumps(resume_for_prompt(resume), indent=2, ensure_ascii=False),
        title=posting.get("title") or "",
        location=(posting.get("location") or {}).get("name") or "",
        description=description_text(posting.get("content")))


def ask_claude_cli(prompt, model=MODEL, timeout=300):
    """One fresh, tool-less Claude Code conversation, run in an empty folder so no project files are read."""
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(
            ["claude", "-p", "--output-format", "json", "--model", model, "--tools", "",
             "--no-session-persistence", "--setting-sources", "", "--system-prompt", SYSTEM],
            input=prompt, capture_output=True, text=True, cwd=empty, timeout=timeout)
    if done.returncode != 0:
        raise RuntimeError("claude exited %d: %s" % (done.returncode, done.stderr.strip()[:300]))
    envelope = json.loads(done.stdout)
    if envelope.get("is_error"):
        raise RuntimeError("claude reported an error: %s" % str(envelope.get("result"))[:300])
    meta = {"model_requested": model, "models_used": sorted(envelope.get("modelUsage", {})),
            "session_id": envelope.get("session_id"), "total_cost_usd": envelope.get("total_cost_usd")}
    return envelope.get("result") or "", meta


def judgment(posting, resume, ask, template_path=BASELINE):
    """Ask once and validate. A reply that fails the validator is kept as rejected, never repaired."""
    prompt = build_prompt(posting, resume, template_path)
    record = {"label": LABEL, "asked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "prompt_file": Path(template_path).name,
              "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
              "status": None, "verdict": None, "reason": None, "raw_reply": None, "rejected_because": None}
    try:
        answer = ask(prompt)
    except Exception as error:  # the run goes on; the rule verdict does not depend on Claude
        record.update(status="error", rejected_because="%s: %s" % (type(error).__name__, error))
        return record
    reply, meta = (answer, {}) if isinstance(answer, str) else answer
    ok, value = validate(reply)
    record.update(meta, raw_reply=reply)
    if ok:
        record.update(status="accepted", verdict=value["verdict"], reason=value["reason"])
    else:
        record.update(status="rejected", rejected_because=value)
    return record
