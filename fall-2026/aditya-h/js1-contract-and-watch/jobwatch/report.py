"""Human-readable Markdown report. Rule verdicts are records; Claude verdicts are labeled judgments."""


def _fields(d):
    return "; ".join(f"`{k}` = \"{v}\"" for k, v in d.items())


def _claude(c):
    if c.get("status") == "not_run":
        return "_Claude judgment not run for this run._"
    label = f"**Claude judgment** ({c.get('model', '?')}, {c.get('date', '?')}) — a model's opinion, not a record"
    if c.get("status") != "valid":
        return f"{label}: **invalid** — rejected by validator: {'; '.join(c.get('errors', []))}"
    return (f"{label}: **{c['verdict']}**  \n"
            f"  résumé fields cited: {', '.join(c['resume_fields'])}  \n"
            f"  posting fields cited: {', '.join(c['posting_fields'])}  \n"
            f"  reason: {c['reason']}")


def markdown(rec):
    c = rec["counts"]
    out = [f"# Job watch — `{rec['board']}` — {rec['run_time']}", ""]
    if rec["seeded"]:
        out += [f"> **SEEDED RUN** — input is a saved earlier response ({rec['seeded_from']}), "
                "not a live fetch.", ""]
    if rec["baseline"]:
        out += ["> **Baseline run** — every posting id recorded; none reported as new.", ""]
    if rec["suspect_empty"]:
        out += ["> **Suspect response** — the board returned zero jobs although the state holds ids; "
                "the state file was not updated.", ""]
    out += [
        f"- Postings fetched: {c['fetched']}",
        f"- New since last run: {c['new']}",
        f"- Relevant by the rule (record, `{rec['rule_id']}`): {c['relevant_rule']}",
        f"- Skipped (new but not relevant by the rule): {c['skipped']}",
        f"- Relevant by Claude (judgment): {c['relevant_claude']} · invalid Claude replies: {c['invalid_claude']}"
        f" · rule/Claude disagreements: {c['disagreements']}",
        f"- Raw response: `{rec['raw_response_path']}` · State: `{rec['state_path']}`",
        "",
    ]
    for heading, want in (("Relevant by the rule", "relevant"), ("Not relevant by the rule", "not_relevant")):
        items = [e for e in rec["verdicts"] if e["rule"]["verdict"] == want]
        if not items:
            continue
        out += [f"## {heading} ({len(items)})", ""]
        for e in items:
            r = e["rule"]
            out += [
                f"### {e['title']} — id {e['posting_id']}" + ("  ⚠ judges disagree" if e["disagree"] else ""),
                f"{e['url'] or ''}",
                "",
                f"**Rule verdict (record, recomputable): {r['verdict']}** — {r['reason']}  ",
                f"  résumé fields: {_fields(r['resume_fields'])}  ",
                f"  posting fields: {_fields(r['posting_fields'])}  ",
                f"  résumé skills seen in posting body (context only): {', '.join(r['skills_in_content']) or 'none'}",
                "",
                _claude(e["claude"]),
                "",
            ]
    return "\n".join(out) + "\n"
