"""Claude's output schema from CONTRACT.md, and the separate support check.

validate() decides only whether a judgment has the contract's shape. Whether its
quotes appear in the cited fields is support_check(), reported apart from it.
"""
import json

from agent import rules

JUDGMENT_KEYS = {"posting_id", "verdict", "citations", "label"}
CITATION_KEYS = {"resume_field", "posting_field", "quote"}
VERDICTS = {"relevant", "not_relevant"}


def resume_field_exists(resume, path):
    """True if a dotted path such as 'skills.languages' or 'experience.0.title' exists."""
    node = resume
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            return False
    return True


def validate(judgment, resume, new_ids):
    """A list of reasons the judgment breaks the schema; empty means accepted."""
    if isinstance(judgment, (str, bytes)):
        try:
            judgment = json.loads(judgment)
        except ValueError:
            return ["not valid JSON"]
    if not isinstance(judgment, dict):
        return ["not a JSON object"]

    errors = []
    if set(judgment) != JUDGMENT_KEYS:
        missing, extra = JUDGMENT_KEYS - set(judgment), set(judgment) - JUDGMENT_KEYS
        errors.append(f"keys must be exactly {sorted(JUDGMENT_KEYS)}; "
                      f"missing {sorted(missing)}, extra {sorted(extra)}")

    posting_id = judgment.get("posting_id")
    if type(posting_id) is not int:
        errors.append("posting_id must be an integer")
    elif posting_id not in new_ids:
        errors.append(f"posting_id {posting_id} is not one of this run's new ids")

    if judgment.get("verdict") not in VERDICTS:
        errors.append(f"verdict must be one of {sorted(VERDICTS)}")
    if judgment.get("label") != "judgment":
        errors.append('label must be "judgment"')

    citations = judgment.get("citations")
    if not isinstance(citations, list) or not citations:
        errors.append("citations must be a non-empty list")
        return errors
    for i, citation in enumerate(citations):
        if not isinstance(citation, dict) or set(citation) != CITATION_KEYS:
            errors.append(f"citations[{i}] must have exactly the keys {sorted(CITATION_KEYS)}")
            continue
        field = citation["resume_field"]
        if not isinstance(field, str) or not resume_field_exists(resume, field):
            errors.append(f"citations[{i}].resume_field {field!r} does not exist in the résumé")
        if citation["posting_field"] not in rules.POSTING_FIELDS:
            errors.append(f"citations[{i}].posting_field must be one of {list(rules.POSTING_FIELDS)}")
        # Amendment 2026-10-29: "" is a substring of every field, so it would always count as supported.
        if not isinstance(citation["quote"], str) or not citation["quote"].strip():
            errors.append(f"citations[{i}].quote must be a non-empty string")
    return errors


def support_check(citation, posting):
    """'supported' if the quote is a substring of the cited posting field (HTML stripped for
    content); for a rule citation with quote None, if none of its absent_terms appears."""
    try:
        text = rules.field_text(posting, citation.get("posting_field"))
    except ValueError:
        return "not supported"
    quote = citation.get("quote")
    if quote is None:
        terms = citation.get("absent_terms")
        if not terms:
            return "not supported"
        return "not supported" if any(rules.find_term(text, t) for t in terms) else "supported"
    if not isinstance(quote, str) or not quote.strip():
        return "not supported"
    return "supported" if quote in text else "not supported"
