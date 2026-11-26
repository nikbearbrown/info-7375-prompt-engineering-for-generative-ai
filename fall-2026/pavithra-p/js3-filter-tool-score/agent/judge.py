"""Claude as a second scorer, for one change to one object other than the filter file: the context Claude is given
(SCORE-REPORT.md section 2b). The prompt (prompts/judge-v1.txt) is the same in both runs; only the posting text differs:

* "full": title, location and the full description;
* "title": title and location only.

Each reply is saved before parsing; a reply outside the fixed shape is counted as invalid, never fixed.
"""
import json

from . import rule

CONTEXTS = ("full", "title")
VERDICTS = ("yes", "no", "cannot tell")


class InvalidVerdict(Exception):
    pass


def posting_context(job, context):
    title = (job.get("title") or "").strip()
    location = (job.get("location") or {}).get("name") or ""
    text = f"Title: {title}\nLocation: {location}"
    if context == "full":
        text += "\nDescription:\n" + " ".join(rule.description_text(job).split())
    elif context != "title":
        raise ValueError(f"unknown context {context!r}")
    return text


def build_prompt(template, job, context):
    return template.replace("{posting}", posting_context(job, context))


def parse(envelope_text):
    try:
        envelope = json.loads(envelope_text)
        reply = json.loads((envelope.get("result") or "").strip())
    except ValueError as e:
        raise InvalidVerdict(f"not the fixed JSON shape: {e}") from e
    if not isinstance(reply, dict) or set(reply) != {"verdict", "reason"} or reply["verdict"] not in VERDICTS:
        raise InvalidVerdict(f"not the fixed shape: {reply!r}")
    return reply["verdict"], reply["reason"]


def score(results, labels):
    """results: {key: verdict or None (invalid)}; labels: {key: (label, note)}. Claude's "yes" counts as keep."""
    judged = [k for k in results if labels.get(k) and labels[k][0] != "cannot tell"]
    fk = [k for k in judged if labels[k][0] == "no" and results[k] == "yes"]
    fr = [k for k in judged if labels[k][0] == "yes" and results[k] != "yes"]
    return {"judged": len(judged), "agree": len(judged) - len(fk) - len(fr), "false_keeps": fk, "false_rejects": fr,
            "yes": sum(v == "yes" for v in results.values()), "invalid": sum(v is None for v in results.values()),
            "cannot_tell": sum(v == "cannot tell" for v in results.values())}
