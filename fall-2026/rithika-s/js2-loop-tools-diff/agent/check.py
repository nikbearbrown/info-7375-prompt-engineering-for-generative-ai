"""Checker for rule verdicts, catching the contract's two wrong versions.

check_verdicts(postings, verdicts) returns a list of problems; an empty list
means every verdict passed. It catches:
  1. misaligned labels: every term a citation says matched must appear in
     *that* posting's text (and every "not matched" term must not);
  2. empty justification: each verdict must cite at least one résumé/target
     field and at least one posting field.
"""

from agent.resume import NOT_COUNTED_GROUP, SKILL_GROUPS
from agent.rule import NOT_RELEVANT, RELEVANT, contains, prepared_fields, render

ALLOWED_FIELDS = frozenset(
    [f"skills.{g}" for g in SKILL_GROUPS]
    + ["target.excluded_terms", "target.target_title_keywords"])
POSTING_FIELDS = frozenset({"posting.title", "posting.content"})


def _check_one(posting, verdict):
    pid = posting.get("id")
    where = f"posting {pid}"
    problems = []
    if verdict.get("posting_id") != pid:
        problems.append(f"{where}: verdict is for posting_id "
                        f"{verdict.get('posting_id')!r}")
    if verdict.get("verdict") not in (RELEVANT, NOT_RELEVANT):
        problems.append(f"{where}: unknown verdict {verdict.get('verdict')!r}")

    citations = verdict.get("citations") or []
    justification = verdict.get("justification") or []
    if not any(c.get("field", "").startswith(("skills.", "target."))
               for c in citations):
        problems.append(f"{where}: justification cites no résumé/target field")
    if not any(f.startswith("posting.")
               for c in citations for f in c.get("posting_fields", [])):
        problems.append(f"{where}: justification cites no posting field")

    texts = prepared_fields(posting)
    for cite in citations:
        field, term = cite.get("field", ""), cite.get("term", "")
        if field == f"skills.{NOT_COUNTED_GROUP}" or field not in ALLOWED_FIELDS:
            problems.append(f"{where}: cites disallowed field {field!r}")
            continue
        posting_fields = cite.get("posting_fields", [])
        if not posting_fields or not set(posting_fields) <= POSTING_FIELDS:
            problems.append(f"{where}: bad posting fields {posting_fields!r}")
            continue
        for pf in posting_fields:
            found = contains(texts[pf], term)
            if cite.get("matched") and not found:
                problems.append(f"{where}: cites {field}: {term} as matched in "
                                f"{pf}, but it does not appear there")
            elif not cite.get("matched") and found:
                problems.append(f"{where}: cites {field}: {term} as not "
                                f"matched in {pf}, but it appears there")
        if render(cite) not in justification:
            problems.append(f"{where}: citation {render(cite)!r} missing "
                            f"from justification text")
    return problems


def check_verdicts(postings, verdicts):
    """Return a list of problems; empty means all verdicts are sound."""
    postings, verdicts = list(postings), list(verdicts)
    if len(postings) != len(verdicts):
        return [f"{len(postings)} postings but {len(verdicts)} verdicts"]
    problems = []
    for posting, verdict in zip(postings, verdicts):
        problems.extend(_check_one(posting, verdict))
    return problems
