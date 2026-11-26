"""The Claude stage of the scorer, inherited from JS1 (agent/claude_judge.py): same prompt template, same strict
output validator, one identical retry, nothing repaired. JS3 changes only where the posting text comes from
(js3.textprep with the filter file's boilerplate) and adds the experiment knobs (prompt, context, tools, model)."""
from __future__ import annotations

import json
import re

from . import claude_cli
from .textprep import posting_sentences

MAX_CONTENT = 6000                                   # inherited from JS1 CONTRACT.md
VERDICTS = ("relevant", "not_relevant")
KEYS = {"verdict", "justification", "cited_resume_fields", "cited_posting_fields"}
RESUME_FIELDS = ("target_title_keywords", "skills", "years_experience", "preferred_cities", "remote_ok",
                 "highest_degree")
POSTING_FIELDS = ("title", "location", "content")
# Siddi's JS1 LABELING.md answers, verbatim (2026-10-31): the context-change variant gives these to Claude.
PREFERENCES = ("1. What kind of role is worth his time?: Data Engineer/AIML 2. How much required experience is too "
               "much?: 2+years 3. Which locations count? Anywhere in usa 4. Do roles that require a PhD or a master's "
               "count, or internships? Masters or some internships 5. When it's unclear, which way do you lean? To skill")
TOOL_LINE = ("\nThe score_posting tool can look up this posting in the job-search agent's collection as "
             "board={board}, posting_id={id}.\n")


def requirements_text(cfg: dict, posting: dict) -> str:
    return "\n".join(posting_sentences(posting, cfg["boilerplate"]))[:MAX_CONTENT]


def fill(template: str, persona: dict, posting: dict, req_text: str, tool_line: bool = False) -> str:
    values = {"target_title_keywords": json.dumps(persona["target_title_keywords"]),
              "skills": json.dumps(persona["skills"]), "years_experience": str(persona["years_experience"]),
              "highest_degree": persona["highest_degree"], "preferred_cities": json.dumps(persona["preferred_cities"]),
              "remote_ok": json.dumps(persona["remote_ok"]), "preferences": PREFERENCES,
              "title": posting["title"], "location": posting["location"].get("name") or "", "content": req_text}
    body = template.split("---", 2)[2].lstrip("\n")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], body)
    return out + (TOOL_LINE.format(board=posting["board"], id=posting["id"]) if tool_line else "")


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate keys")
    return dict(pairs)


def validate(stdout: bytes):
    """JS1's output contract, unchanged: (answer, None) or (None, reason)."""
    result, why = claude_cli.envelope_result(stdout)
    if result is None:
        return None, why
    try:
        answer = json.loads(result, object_pairs_hook=_no_dupes)
    except ValueError:
        return None, "result is not exactly one JSON object"
    if not isinstance(answer, dict) or set(answer) != KEYS:
        return None, f"result keys are not exactly {sorted(KEYS)}"
    if answer["verdict"] not in VERDICTS:
        return None, f"verdict {answer['verdict']!r} is not relevant/not_relevant"
    j = answer["justification"]
    if not isinstance(j, str) or not 1 <= len(j) <= 400:
        return None, "justification is not a 1-400 character string"
    for key, allowed in (("cited_resume_fields", RESUME_FIELDS), ("cited_posting_fields", POSTING_FIELDS)):
        v = answer[key]
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x in allowed for x in v):
            return None, f"{key} is empty or names a field outside {list(allowed)}"
    return answer, None
