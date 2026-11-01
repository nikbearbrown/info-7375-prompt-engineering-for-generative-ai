"""Claude judge ("judgment"). CONTRACT.md Final, Out: The Claude judge (D5§2, D6-C§14, D6-C§15, D4§1, D4§3).

Python itself makes no network calls: the claude CLI runs as a subprocess, in print mode,
from a fresh empty temporary directory, with every tool disabled.

Smoke test on one constructed posting:
    python3 -m js1.claude_judge --prompt baseline --posting-file tests/fixtures/constructed_postings.json --posting-id 8000002
"""

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from js1.persona import PersonaRefused, load_persona
from js1.rule_judge import EXCLUDED_SKILL_SECTIONS, MAX_YEARS, countable_skills, sentences

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
EVIDENCE_DIR = ROOT / "evidence" / "claude"
RESUME = ROOT / "persona" / "priya-nair.resume.json"
PROFILE = ROOT / "persona" / "priya-nair.profile.json"

MODEL = "claude-sonnet-4-6"  # pinned; the CLI's full id for Sonnet 4.6
CLAUDE_CMD = [
    "claude", "-p",
    "--model", MODEL,
    "--tools", "",
    "--strict-mcp-config", "--mcp-config", '{"mcpServers": {}}',
    "--disable-slash-commands",
    "--no-session-persistence",
    "--output-format", "text",
]
TIMEOUT_SECONDS = 180
MAX_ATTEMPTS = 2  # D6-C§15: retry exactly once
OUTPUT_EXCERPT_CHARS = 2000
REQUIRED_KEYS = {"posting_id", "verdict", "skills_cited", "explanation"}
VERDICTS = {"relevant", "not relevant"}
POSTING_FIELDS = ("title", "location", "description")
FAMILIAR_FIELD = "skills.familiar_with_not_shipped"


class InvalidReply(Exception):
    pass


def candidate_fields(resume, profile):
    """Priya's fields for Claude. No contact details, and no rule-judge output (D4§1, D6-C§14)."""
    skills = {f"skills.{k}": v for k, v in resume.get("skills", {}).items()
              if k not in EXCLUDED_SKILL_SECTIONS and isinstance(v, list)}
    in_sections = {s for values in skills.values() for s in values}
    tools = {name: fields for name, fields in countable_skills(resume).items() if name not in in_sections}
    target = profile.get("target_role", {})
    return {
        "resume_skill_fields": skills,
        "resume_experience_tools": tools,
        FAMILIAR_FIELD: resume.get("skills", {}).get("familiar_with_not_shipped", []),
        "target_roles": {"profile.target_role.primary": target.get("primary"),
                         "profile.target_role.secondary": target.get("secondary")},
        "profile.needs_sponsorship": profile.get("needs_sponsorship"),
        "exclusions": {"profile.target_role.excluded": target.get("excluded")},
        "experience_cap": {"max_required_years": MAX_YEARS, "source": "CONTRACT.md D4§2, not a profile field"},
    }


def posting_fields(posting):
    return {
        "id": posting.get("id"),
        "title": posting.get("title", ""),
        "location": (posting.get("location") or {}).get("name", ""),
        "description": " ".join(sentences(posting.get("content", ""))),
    }


def citable_fields(candidate):
    fields = set(candidate["resume_skill_fields"])
    for cited in candidate["resume_experience_tools"].values():
        fields.update(cited)
    return fields


def build_prompt(prompt_text, posting, candidate):
    data = {"posting": posting_fields(posting), "candidate": candidate}
    return prompt_text.rstrip("\n") + "\n\nINPUT:\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def validate(reply, expected_id, allowed_fields):
    """Return the parsed judgment, or raise InvalidReply. Anything outside the fixed format is rejected (D5§2)."""
    try:
        data = json.loads(reply.strip())
    except (json.JSONDecodeError, ValueError) as exc:
        raise InvalidReply(f"not JSON: {exc}") from None
    if not isinstance(data, dict):
        raise InvalidReply("not a JSON object")
    if set(data) != REQUIRED_KEYS:
        missing, extra = REQUIRED_KEYS - set(data), set(data) - REQUIRED_KEYS
        raise InvalidReply(f"keys wrong: missing {sorted(missing)}, extra {sorted(extra)}")
    if type(data["posting_id"]) is not int or data["posting_id"] != expected_id:
        raise InvalidReply(f"posting_id {data['posting_id']!r} does not equal input id {expected_id!r}")
    if data["verdict"] not in VERDICTS:
        raise InvalidReply(f"invalid verdict {data['verdict']!r}")
    if not isinstance(data["skills_cited"], list):
        raise InvalidReply("skills_cited is not a list")
    for item in data["skills_cited"]:
        if not isinstance(item, dict) or set(item) != {"skill", "resume_field"}:
            raise InvalidReply(f"skills_cited entry has wrong shape: {item!r}")
        if not isinstance(item["skill"], str) or not item["skill"].strip():
            raise InvalidReply(f"skills_cited entry has no skill name: {item!r}")
        if item["resume_field"] == FAMILIAR_FIELD:
            raise InvalidReply(f"cites {FAMILIAR_FIELD}, which cannot justify a match: {item!r}")
        if item["resume_field"] not in allowed_fields:
            raise InvalidReply(f"resume_field {item['resume_field']!r} is not a field given in the input")
    explanation = data["explanation"]
    if not isinstance(explanation, str) or not explanation.strip():
        raise InvalidReply("explanation is empty")
    if not any(f in explanation.lower() for f in POSTING_FIELDS):
        raise InvalidReply(f"explanation names none of the posting fields {list(POSTING_FIELDS)}")
    return data


def run_claude(prompt):
    """One claude CLI call from a fresh empty temporary directory. Returns (returncode, stdout, stderr)."""
    with tempfile.TemporaryDirectory(prefix="js1-claude-") as cwd:
        proc = subprocess.run(CLAUDE_CMD, input=prompt, cwd=cwd, capture_output=True, text=True,
                              timeout=TIMEOUT_SECONDS)
        return proc.returncode, proc.stdout, proc.stderr


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def judge(posting, resume, profile, prompt_name="baseline", runner=run_claude,
          evidence_dir=EVIDENCE_DIR, stamp=None, prompts_dir=PROMPTS_DIR):
    stamp = stamp or _stamp()
    candidate = candidate_fields(resume, profile)
    prompt = build_prompt((Path(prompts_dir) / f"{prompt_name}.txt").read_text(encoding="utf-8"), posting, candidate)
    allowed = citable_fields(candidate)
    out_dir = Path(evidence_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{stamp}-{prompt_name}-{posting.get('id')}"
    errors = []
    result = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            code, stdout, stderr = runner(prompt)
        except (OSError, subprocess.SubprocessError) as exc:
            code, stdout, stderr = None, "", f"{type(exc).__name__}: {exc}"
        (out_dir / f"{base}-attempt{attempt}.txt").write_text(stdout, encoding="utf-8")
        try:
            if code != 0:
                raise InvalidReply(f"claude exited with {code}")
            parsed = validate(stdout, posting.get("id"), allowed)
            result = {"label": "judgment", "status": "valid", "model": MODEL, "prompt": prompt_name,
                      "attempts": attempt, **parsed}
            break
        except InvalidReply as exc:
            # Keep both streams: the CLI prints some failures, like "Not logged in", on stdout.
            errors.append({"attempt": attempt, "error": str(exc), "exit_code": code,
                           "stdout": stdout[:OUTPUT_EXCERPT_CHARS], "stderr": stderr[:OUTPUT_EXCERPT_CHARS]})
    if result is None:
        result = {"label": "judgment", "status": "invalid", "model": MODEL, "prompt": prompt_name,
                  "attempts": MAX_ATTEMPTS, "posting_id": posting.get("id"), "validation_errors": errors}
    else:
        result["validation_errors"] = errors
    (out_dir / f"{base}-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")
    return result


def judge_all(postings, resume, profile, **kwargs):
    stamp = kwargs.pop("stamp", None) or _stamp()
    return [judge(p, resume, profile, stamp=stamp, **kwargs) for p in postings]


def main(argv=None):
    parser = argparse.ArgumentParser(prog="js1.claude_judge")
    parser.add_argument("--prompt", choices=["baseline", "revised"], default="baseline")
    parser.add_argument("--posting-file", required=True, help="a saved Greenhouse-shaped JSON file")
    parser.add_argument("--posting-id", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        resume, profile = load_persona(RESUME, PROFILE)
    except PersonaRefused as exc:
        print(exc, file=sys.stderr)
        return 1
    jobs = json.loads(Path(args.posting_file).read_text(encoding="utf-8"))["jobs"]
    posting = next((j for j in jobs if j.get("id") == args.posting_id), None)
    if posting is None:
        print(f"posting {args.posting_id} not found in {args.posting_file}", file=sys.stderr)
        return 1
    result = judge(posting, resume, profile, prompt_name=args.prompt)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "valid" else 4


if __name__ == "__main__":
    sys.exit(main())
