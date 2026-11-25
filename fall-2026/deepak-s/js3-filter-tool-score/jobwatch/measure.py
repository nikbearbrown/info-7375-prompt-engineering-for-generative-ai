"""Phase 3d: measure one candidate rule change on the audit rows only (never the held-out set).

    python -m jobwatch measure-change --change C1 --sheet audit/audit-v1.csv --dataset data/postings-<run-id>.jsonl

Evaluates v1 and v1 plus the one change (jobwatch/filter.py CANDIDATES) on exactly the postings
in the audit sheet, against Deepak's verdicts in that sheet. An error is a kept posting judged
not_relevant or a rejected posting judged relevant; an abstention is neither. Reports errors
before and after, the errors fixed, the errors created, every row whose decision changed, and,
for each new rule term, which audited titles it matches. Applies Deepak's pre-set criterion
(Gate 3b): adopt only if the change fixes at least one error and creates none.
Writes audit/changes/<change>.json and .md.
"""
import json

from jobwatch import filter as flt
from jobwatch import sheets


def is_error(decision, verdict):
    return (decision == "keep" and verdict == "not_relevant") or (decision == "reject" and verdict == "relevant")


def new_terms(change):
    base, cand = flt.V1, flt.CANDIDATES[change][1]
    out = []
    for attr in ("exclude", "roles", "topics"):
        old = set(getattr(base, attr))
        out += [(rid, term) for rid, term in getattr(cand, attr) if (rid, term) not in old]
    return out


def measure(change, rows, lines):
    desc, rules = flt.CANDIDATES[change]
    by_key = {ln["key"]: ln for ln in lines}
    out_rows, fixed, created = [], [], []
    for r in rows:
        ln = by_key[r["posting_key"]]
        a, b = flt.evaluate(ln, flt.V1), flt.evaluate(ln, rules)
        ea, eb = is_error(a["decision"], r["verdict"]), is_error(b["decision"], r["verdict"])
        rec = {"posting_key": r["posting_key"], "group": r["group"], "title": r["title"], "verdict": r["verdict"],
               "before": a["decision"], "after": b["decision"], "error_before": ea, "error_after": eb,
               "reasons_after": b["reasons"]}
        if a["decision"] != b["decision"]:
            out_rows.append(rec)
        if ea and not eb:
            fixed.append(rec)
        if eb and not ea:
            created.append(rec)
    errors_before = sum(is_error(flt.evaluate(by_key[r["posting_key"]], flt.V1)["decision"], r["verdict"]) for r in rows)
    errors_after = sum(is_error(flt.evaluate(by_key[r["posting_key"]], rules)["decision"], r["verdict"]) for r in rows)
    terms = []
    for rid, term in new_terms(change):
        spans_hit = [r["title"] for r in rows if flt.find_term(term, flt.token_spans(r["title"]))]
        terms.append({"rule": rid, "term": term, "audited_titles_matched": spans_hit})
    adopt = bool(fixed) and not created
    return {"change": change, "description": desc, "version": rules.version, "audit_rows": len(rows),
            "errors_before": errors_before, "errors_after": errors_after, "fixed": fixed, "created": created,
            "decision_changes": out_rows, "new_terms": terms,
            "criterion": "adopt only if it fixes at least one filter error on the audit rows and creates no new one (Deepak, Gate 3b)",
            "criterion_result": "adopted (Deepak's Gate 3b criterion)" if adopt else "rejected (Deepak's Gate 3b criterion)"}


def render(m):
    L = [f"# {m['change']}: {m['description']}", "",
         f"Measured on the {m['audit_rows']} rows of the audit sheet only (Deepak's verdicts), never the held-out set.", "",
         f"- Filter errors on the audit rows: {m['errors_before']}/{m['audit_rows']} with v1, {m['errors_after']}/{m['audit_rows']} with {m['version']}.",
         f"- Errors fixed: {len(m['fixed'])}; errors created: {len(m['created'])}.",
         f"- Rows whose decision changed: {len(m['decision_changes'])}.",
         f"- Criterion: {m['criterion']}. Result: {m['criterion_result']}.", "", "## Decision changes", ""]
    L += [f"- {r['group']} {r['posting_key']} \"{r['title']}\": {r['before']} -> {r['after']} (verdict {r['verdict']}; "
          f"error {r['error_before']} -> {r['error_after']}); after: {'; '.join(r['reasons_after'])}" for r in m["decision_changes"]] or ["- none"]
    L += ["", "## Audited titles each new term matches", ""]
    L += [f"- {t['rule']} \"{t['term']}\": " + ("; ".join(f"\"{x}\"" for x in t["audited_titles_matched"]) or "none")
          for t in m["new_terms"]] or ["- no new title term (this change edits a body or location rule)"]
    return "\n".join(L) + "\n"


def run(tools, change, sheet, lines):
    _, _, rows = sheets.read_sheet(tools, sheet)
    m = measure(change, rows, lines)
    tools.write_file(f"audit/changes/{change}.json", (json.dumps(m, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    tools.write_file(f"audit/changes/{change}.md", render(m).encode("utf-8"))
    return m
