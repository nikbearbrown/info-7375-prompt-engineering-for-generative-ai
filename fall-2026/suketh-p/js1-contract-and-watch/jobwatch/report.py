"""results.md: the same results as results.json, readable by a person."""


def _evidence(items):
    return "; ".join(f'{e["field"]}: "{e["quote"]}"' for e in items)


def _matched(matched):
    return "; ".join(f"{k}: {', '.join(v) if v else '(none)'}" for k, v in matched.items())


def render(results):
    seeded = results["mode"] == "seeded"
    label = "SEEDED: replay of a saved earlier response, not a live fetch" if seeded else "LIVE fetch"
    lines = [
        f"# Run {results['run_id']} ({label})",
        "",
        f"- Board: {results['board']} (Greenhouse), endpoint `{results['endpoint']}`",
        f"- Source: {results['source']}",
        f"- Retrieved at: {results['retrieved_at']} · raw sha256 `{results['raw_sha256']}`",
        f"- Postings in response: {results['posting_count']} · previously seen ids: {results['previously_seen_count']}",
        f"- New since last run: {len(results['new_ids'])}",
        "",
    ]
    if results["baseline"]:
        lines += ["Baseline run: every id is recorded as seen and none is reported as new.", ""]
    for p in results["postings"]:
        r, c = p["rule_verdict"], p["claude_verdict"]
        lines += [
            f"## {p['posting_id']}: {p['title']} ({p['location'] or 'no location'})",
            "",
            "| Judge | Verdict | What it is |",
            "|---|---|---|",
            f"| Rule | {r['verdict']} | record: recomputable from CONTRACT.md |",
            f"| Claude | {c['verdict']} | model judgment, not a verified fact |",
            "",
            f"Verdicts agree: {'yes' if p['verdicts_agree'] else 'NO, disagreement kept'}",
            "",
            f"**Rule record.** {r['justification']}",
            "",
            "| Condition | Passed | Matched |",
            "|---|---|---|",
        ]
        lines += [f"| {k['condition']} | {'yes' if k['passed'] else 'no'} | {_matched(k['matched'])} |"
                  for k in r["conditions"]]
        lines += [
            "",
            f"**Claude, model judgment ({c['prompt']}).** {c['justification']}",
            "",
            f"- Résumé evidence: {_evidence(c['resume_evidence'])}",
            f"- Posting evidence: {_evidence(c['posting_evidence'])}",
            f"- Reply saved verbatim: `{c['reply_file']}`",
            "",
        ]
    return "\n".join(lines) + "\n"
