"""Contract §2 Out: assemble one record per new posting. Joins strictly by posting id (wrong version W1)."""


def assemble(new_jobs, rule_by_id, claude_by_id):
    out = []
    for j in new_jobs:
        jid = j["id"]
        r = rule_by_id[jid]
        out.append({
            "posting_id": jid,
            "title": j.get("title"),
            "location": (j.get("location") or {}).get("name"),
            "url": j.get("absolute_url"),
            "rule_verdict": r["verdict"], "rule_label": r["label"], "rule_reasons": r["reasons"],
            "claude": claude_by_id.get(jid),
        })
    return out


def to_markdown(records, board, stamp, seeded=False):
    L = [f"# Run report: {board}, {stamp}{' (SEEDED)' if seeded else ''}\n", "## Executive summary\n"]
    rel = sum(1 for r in records if r["rule_verdict"] == "relevant")
    L.append(f"{len(records)} new posting(s) since the last run; the written rule (record) calls {rel} relevant. "
             "Claude's verdict is a model judgment, shown beside it, never instead of it.\n")
    if not records:
        L.append("_No new postings this run._\n")
    for r in records:
        c = r.get("claude") or {}
        L.append(f"### {r['title']} ({r['posting_id']})\n\n{r['location']} · {r['url']}\n")
        L.append(f"- **Rule verdict (record):** {r['rule_verdict']}")
        L.append(f"- **Claude verdict (model-judgment):** {c.get('verdict') or c.get('status', 'not run')}"
                 + (f": {c['justification']}" if c.get("justification") else (f" ({c['error']})" if c.get("error") else "")))
        L.append("\n| Check | Résumé field | Posting field | Result | Evidence |\n|---|---|---|---|---|")
        for x in r["rule_reasons"]:
            L.append(f"| {x['check']} | `{x['resume_field']}` | `{x['posting_field']}` | {x['result']} | {x['evidence']} |")
        L.append("")
    return "\n".join(L) + "\n"
