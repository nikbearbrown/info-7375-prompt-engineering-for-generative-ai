"""Phase 4: the source-grounded shortlist (FILTER.md sections 2, 3 and 4).

    python -m jobwatch shortlist --dataset data/postings-<run-id>.jsonl --filter data/filter-v1.jsonl

The shortlist is every kept posting of the final filter version, in the section 2 tie order
(FILTER.md sets no top N, so none are cut). For each posting:
  - one claim per matched rule (role, location, topic, and E01 when it found a requirement),
    written from the rule and its span (RULE_CLAIMS); its quote is the matched span;
  - up to 2 claims written by the Claude judge (jobwatch/claude_judge.py, prompt
    prompts/js3_claims_v1.md), each with a quote the judge copied from the posting.
The checker pre-labels each claim (section 3): is the quote found in the posting's own text
(title, location or text, at the claim's offsets), and is its sentence boilerplate.
    no quote found              -> pre_label "insufficient (quote not found)"
    quote only in boilerplate   -> pre_label "insufficient (boilerplate)"
    otherwise                   -> pre_label "quote found, not boilerplate"
Deepak's hand label (supported, contradicted, insufficient) is final.

Section 4 rule 3, on the shortlist: a kept posting gives "I cannot tell" when a claim its keep
decision needs is labeled insufficient. The keep needs its role claim, its location claim, and
enough topic claims for 5 + 2 + topics >= T (keep_needs). A contradicted needed claim also
removes the support. `decide` applies this to hand labels when they exist, else to pre-labels
(a missing quote or boilerplate counts as insufficient).
"""
import json

from jobwatch import filter as flt
from jobwatch import sheets

COLUMNS = ("claim_id", "posting_key", "rank", "source", "claim", "field", "start", "end", "quote",
           "quote_found", "boilerplate", "pre_label", "text_path", "label", "note")
MAX_JUDGE_CLAIMS = 2


def rule_term(rules, rule_id):
    for attr in ("roles", "locations", "topics", "exclude"):
        for rid, term in getattr(rules, attr):
            if rid == rule_id:
                return term
    return rules.remote[1] if rule_id == rules.remote[0] else None


def rule_claim(m, rules, years=None):
    rid = m["rule"]
    if rid.startswith("R"):
        return f"The role is a {rule_term(rules, rid)} role."
    if rid == rules.remote[0]:
        return "The job is remote and open to candidates in the United States."
    if rid.startswith("L"):
        return f"The job is based in {rule_term(rules, rid)}."
    if rid.startswith("T"):
        return f"The work involves {rule_term(rules, rid)}."
    if rid == "E01":
        return f"The minimum required experience stated is {years} years, five or fewer."
    return None


def field_text(line, field):
    return {"title": line["title"] or "", "location": line["location"] or "", "text": line["text"]}[field]


def locate(line, quote):
    """First exact occurrence of `quote` in title, location or text: (field, start, end) or None."""
    if not quote:
        return None
    for field in ("text", "title", "location"):
        i = field_text(line, field).find(quote)
        if i >= 0:
            return field, i, i + len(quote)
    return None


def is_boilerplate(line, field, start, end):
    """True when the quote lies inside sentences that are all boilerplate (text field only)."""
    if field != "text":
        return False
    covering = [s for s in line["sentences"] if s["start"] < end and start < s["end"]]
    return bool(covering) and all(s["boilerplate"] for s in covering)


def pre_label(line, field, start, end, quote):
    found = (field is not None and start is not None and quote != ""
             and field_text(line, field)[start:end] == quote)
    if not found:
        return False, False, "insufficient (quote not found)"
    bp = is_boilerplate(line, field, start, end)
    return True, bp, "insufficient (boilerplate)" if bp else "quote found, not boilerplate"


def parse_judge(result):
    """The judge's claims, or [] with a reason, from its raw result text."""
    try:
        data = json.loads(result)
        claims = data["claims"]
        assert isinstance(claims, list)
    except (TypeError, ValueError, KeyError, AssertionError):
        return [], "judge result is not the JSON shape the prompt asks for"
    out = [c for c in claims if isinstance(c, dict) and isinstance(c.get("claim"), str) and isinstance(c.get("quote"), str)]
    return out[:MAX_JUDGE_CLAIMS], None


def claims_for(line, output, rules, rank, text_path, judge_claims):
    rows = []
    n = 0
    for m in output["matched"]:
        text = rule_claim(m, rules, output.get("years"))
        if text is None:
            continue
        n += 1
        found, bp, pl = pre_label(line, m["field"], m["start"], m["end"], m["quote"])
        rows.append({"claim_id": f"{line['key']}#{n}", "posting_key": line["key"], "rank": rank, "source": f"rule:{m['rule']}",
                     "claim": text, "field": m["field"], "start": m["start"], "end": m["end"], "quote": m["quote"],
                     "quote_found": found, "boilerplate": bp, "pre_label": pl, "text_path": text_path, "label": "", "note": ""})
    for jc in judge_claims:
        n += 1
        loc = locate(line, jc["quote"])
        field, start, end = loc if loc else (None, None, None)
        found, bp, pl = pre_label(line, field, start, end, jc["quote"])
        rows.append({"claim_id": f"{line['key']}#{n}", "posting_key": line["key"], "rank": rank, "source": "judge",
                     "claim": jc["claim"], "field": field or "", "start": "" if start is None else start,
                     "end": "" if end is None else end, "quote": jc["quote"], "quote_found": found, "boilerplate": bp,
                     "pre_label": pl, "text_path": text_path, "label": "", "note": ""})
    return rows


def keep_needs(rules):
    """How many supported topic claims the keep decision needs (role and location are always needed)."""
    return max(0, rules.threshold - rules.role_weight - rules.location_weight)


def _status(c):
    lab = (c.get("label") or "").strip()
    if lab:
        return lab
    return "insufficient" if c["pre_label"].startswith("insufficient") else "supported"


def decide(claims, rules=flt.V1):
    """Section 4 rule 3 for one shortlisted posting: ("keep", why) or ("I cannot tell", why)."""
    role = [c for c in claims if c["source"].startswith("rule:R")]
    loc = [c for c in claims if c["source"].startswith("rule:L")]
    topics = [c for c in claims if c["source"].startswith("rule:T")]
    if not any(_status(c) == "supported" for c in role):
        return "I cannot tell", "the role claim is not supported"
    if not any(_status(c) == "supported" for c in loc):
        return "I cannot tell", "the location claim is not supported"
    supported = sum(_status(c) == "supported" for c in topics)
    if supported < keep_needs(rules):
        return "I cannot tell", f"{supported} supported topic claims; the keep needs {keep_needs(rules)}"
    return "keep", f"role, location and {supported} topic claims supported"


def shortlisted(outputs):
    return flt.rank([o for o in outputs if o.get("scope") != "board" and o["decision"] == "keep"])


def write_claims(tools, path, run_id, version, rows, judge_notes):
    comments = [f"Claims for the shortlist of filter {version} on run {run_id} (FILTER.md sections 3 and 4).",
                "pre_label is the checker's (quote found in the posting text at the offsets; boilerplate or not).",
                "label: supported, contradicted or insufficient (Deepak's hand label, final). note: optional."]
    comments += judge_notes
    sheets.write_sheet(tools, path, comments, COLUMNS, rows)
