"""The Claude judge: a fixed prompt contract and a validator that rejects anything else.

A Claude verdict is a judgment, never a record. Output that fails validation is kept
as invalid and is never repaired into a verdict.
"""
import json
import os
import re
import subprocess
import tempfile

from rule import description_text

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = {"relevant", "not_relevant", "needs_human"}
OUTPUT_KEYS = {"posting_id", "verdict", "cites", "reason"}
CITE_KEYS = {"source", "path", "value"}


def rule_text(contract_path=os.path.join(HERE, "CONTRACT.md")):
    """The rule section of CONTRACT.md, verbatim, minus item 7 (scoring is not judging)."""
    with open(contract_path, encoding="utf-8") as f:
        contract = f.read()
    section = contract.split("## The rule", 1)[1].split("\n## ", 1)[0]
    return "\n".join(line for line in section.strip().splitlines() if not line.startswith("7. Scoring"))


def posting_view(posting):
    """Exactly what Claude sees of a posting; posting cites are checked against this."""
    return {
        "id": posting.get("id"),
        "title": posting.get("title"),
        "location": {"name": (posting.get("location") or {}).get("name")},
        "offices": [{"name": o.get("name"), "location": o.get("location")} for o in posting.get("offices") or []],
        "content": description_text(posting.get("content")),
    }


def build_prompt(template_path, posting, resume):
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    return (template.replace("{rule}", rule_text())
            .replace("{resume}", json.dumps(resume, indent=2, ensure_ascii=False))
            .replace("{posting}", json.dumps(posting_view(posting), indent=2, ensure_ascii=False)))


def resolve(obj, path):
    """Follow a dot path such as "targets.titles" or "offices[0].name"; raise KeyError if absent."""
    tokens = re.findall(r"\[(\d+)\]|([^.\[\]]+)", path)
    if not tokens or "".join(f"[{i}]" if i else k for i, k in tokens) != path.replace(".", ""):
        raise KeyError(path)
    for index, key in tokens:
        if index:
            if not isinstance(obj, list) or int(index) >= len(obj):
                raise KeyError(path)
            obj = obj[int(index)]
        else:
            if not isinstance(obj, dict) or key not in obj:
                raise KeyError(path)
            obj = obj[key]
    return obj


def _squash(text):
    return " ".join(str(text).lower().split())


def value_present(field, value):
    """Is the quoted value really at that field? Case and whitespace are ignored."""
    want = _squash(value)
    if not want:
        return False
    if isinstance(field, list) and all(not isinstance(x, (dict, list)) for x in field):
        candidates = [str(x) for x in field] + [", ".join(map(str, field))]
    elif isinstance(field, (dict, list)):
        candidates = [json.dumps(field, ensure_ascii=False)]
    else:
        candidates = [str(field)]
    return any(want in _squash(c) for c in candidates)


def validate(raw, posting, resume):
    """Return (verdict_dict, []) when the output meets the contract, else (None, errors)."""
    try:
        obj = json.loads(raw.strip())
    except (json.JSONDecodeError, AttributeError) as e:
        return None, [f"not a single JSON object: {e}"]
    if not isinstance(obj, dict):
        return None, ["output is not a JSON object"]
    errors = []
    if set(obj) != OUTPUT_KEYS:
        missing, extra = OUTPUT_KEYS - set(obj), set(obj) - OUTPUT_KEYS
        errors.append(f"keys must be exactly {sorted(OUTPUT_KEYS)}; missing {sorted(missing)}, extra {sorted(extra)}")
    if obj.get("posting_id") != posting.get("id") or isinstance(obj.get("posting_id"), bool):
        errors.append(f"posting_id {obj.get('posting_id')!r} does not match {posting.get('id')!r}")
    if obj.get("verdict") not in VERDICTS:
        errors.append(f"verdict {obj.get('verdict')!r} is not one of {sorted(VERDICTS)}")
    if not isinstance(obj.get("reason"), str) or not obj.get("reason", "").strip():
        errors.append("reason must be a non-empty string")
    cites = obj.get("cites")
    sources = set()
    if not isinstance(cites, list) or not cites:
        errors.append("cites must be a non-empty list")
        cites = []
    view = posting_view(posting)
    for i, cite in enumerate(cites):
        if not isinstance(cite, dict) or set(cite) != CITE_KEYS:
            errors.append(f"cites[{i}] must have exactly the keys {sorted(CITE_KEYS)}")
            continue
        target = {"resume": resume, "posting": view}.get(cite["source"])
        if target is None:
            errors.append(f"cites[{i}].source {cite['source']!r} must be 'resume' or 'posting'")
            continue
        try:
            field = resolve(target, str(cite["path"]))
        except KeyError:
            errors.append(f"cites[{i}].path {cite['path']!r} does not exist in the {cite['source']}")
            continue
        if not isinstance(cite["value"], (str, int, float)) or not value_present(field, cite["value"]):
            errors.append(f"cites[{i}].value {cite['value']!r} is not at {cite['source']}.{cite['path']}")
            continue
        sources.add(cite["source"])
    for needed in ("resume", "posting"):
        if needed not in sources:
            errors.append(f"needs at least one valid {needed} cite")
    return (None, errors) if errors else (obj, [])


def call_cli(prompt, claude_bin=None, timeout=300):
    """Ask Claude through `claude -p` with every tool disabled, from an empty directory
    so no project CLAUDE.md is loaded. Returns the raw stdout."""
    claude_bin = claude_bin or os.environ.get("CLAUDE_BIN", "claude")
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(
            [claude_bin, "-p", "--tools", "", "--no-session-persistence", "--output-format", "text"],
            input=prompt, capture_output=True, text=True, timeout=timeout, cwd=empty,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout
