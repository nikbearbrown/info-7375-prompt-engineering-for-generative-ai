"""Phase 3c: facts from Deepak's audit verdicts (no judgment is made here).

    python -m jobwatch audit-stats --sheet audit/audit-v1.csv --filter data/filter-v1.jsonl
                                   --dataset data/postings-<run-id>.jsonl

Per group: verdict counts and the filter's errors against the verdicts, with denominators. An
error is a kept posting judged not_relevant, or a rejected posting judged relevant. For the
random rejects (the only randomly sampled group), the miss rate with its exact (Clopper-Pearson)
95% interval and what that implies as a count over the sampling frame. Every OVERRIDE. The
false-friend candidates: each positive match (role, location or topic rule) in an audited posting
judged not_relevant, with its span, quote and sentence.

Writes audit/audit-<version>-stats.json and audit/audit-<version>-facts.md through tools.
"""
import json

from jobwatch import sheets
from jobwatch.filter import V1, location_status
from jobwatch.stats import clopper_pearson
from jobwatch.textmatch import tokens

# FILTER.md section 0, seniority: "Intern, Staff, Senior Staff, Principal, Director, Lead, Head and
# management roles are not relevant" (management read here as the title word Manager).
SECTION0_TITLE_WORDS = ("intern", "staff", "principal", "director", "lead", "head", "manager")

GROUP_ORDER = ("close_call_reject", "close_call_keep", "random_reject", "random_keep", "near_decision")
SAMPLED = {"random_reject", "random_keep"}


def _sentence(line, start, end):
    for s in line["sentences"]:
        if s["start"] <= start and end <= s["end"]:
            return line["text"][s["start"]:s["end"]], s["boilerplate"]
    return None, None


def compute(rows, outputs, lines, comments):
    out_by = {o["key"]: o for o in outputs if o.get("key")}
    line_by = {ln["key"]: ln for ln in lines}
    groups = {}
    for r in rows:
        g = groups.setdefault(r["group"], {"n": 0, "relevant": 0, "not_relevant": 0, "errors": [], "overrides": 0,
                                           "checklist": {"answered": 0, "failed_family": 0, "failed_seniority": 0,
                                                         "failed_location": 0, "failed_experience": 0, "all_yes": 0}})
        if (r.get("check_family") or "").strip():
            ck = g["checklist"]
            sen = r.get("check_seniority_title") or r.get("check_seniority") or ""
            checks = [r.get("check_family"), sen, r.get("check_location")]
            if "check_experience" in r:
                checks.append(r.get("check_experience") or "")
            ck["answered"] += 1
            ck["failed_family"] += r.get("check_family") == "n"
            ck["failed_seniority"] += sen == "n"
            ck["failed_location"] += r.get("check_location") == "n"
            ck["failed_experience"] += r.get("check_experience") == "n"
            ck["all_yes"] += all(c == "y" for c in checks)
        o = out_by[r["posting_key"]]
        g["n"] += 1
        g[r["verdict"]] += 1
        g["overrides"] += bool(r["override_reason"].strip())
        wrong = (o["decision"] == "keep" and r["verdict"] == "not_relevant") or \
                (o["decision"] == "reject" and r["verdict"] == "relevant")
        if wrong:
            g["errors"].append({"posting_key": r["posting_key"], "title": r["title"], "location": r["location"],
                                "filter_decision": o["decision"], "filter_reasons": o["reasons"], "verdict": r["verdict"],
                                "override_reason": r["override_reason"]})
    rejects_total = sum(1 for o in outputs if o.get("scope") != "board" and o["decision"] == "reject")
    frame = None
    for c in comments:
        if c.startswith("random_reject:") and "pool " in c:
            frame = int(c.split("pool ")[1].split(";")[0].split()[0])
    rr = groups.get("random_reject")
    miss = None
    if rr:
        k, n = len(rr["errors"]), rr["n"]
        lo, hi = clopper_pearson(k, n)
        miss = {"k": k, "n": n, "rate": k / n, "ci95": [lo, hi], "frame": frame, "rejects_in_run": rejects_total,
                "count_range_in_frame": [lo * frame, hi * frame] if frame else None}
    overrides = [{"posting_key": r["posting_key"], "group": r["group"], "title": r["title"], "verdict": r["verdict"],
                  "override_reason": r["override_reason"]} for r in rows if r["override_reason"].strip()]
    candidates = []
    for r in rows:
        if r["verdict"] != "not_relevant":
            continue
        o = out_by[r["posting_key"]]
        for m in o["matched"]:
            if m["rule"][0] not in "RLT":
                continue
            ln = line_by[r["posting_key"]]
            if m["field"] == "text":
                sentence, bp = _sentence(ln, m["start"], m["end"])
            else:
                sentence, bp = ln[m["field"]], False
            candidates.append({"posting_key": r["posting_key"], "group": r["group"], "filter_decision": o["decision"],
                               "rule": m["rule"], "field": m["field"], "start": m["start"], "end": m["end"],
                               "quote": m["quote"], "sentence": sentence, "sentence_boilerplate": bp})
    consistency = []
    for r in rows:
        if r["verdict"] != "relevant" or r["override_reason"].strip() or (r.get("check_family") or "").strip():
            continue  # rows answered with the checklist are built from the section 0 checks themselves
        words = sorted(set(tokens(r["title"])) & set(SECTION0_TITLE_WORDS))
        state, _ = location_status({"location": r["location"] or None}, V1)
        if words or state != "match":
            consistency.append({"posting_key": r["posting_key"], "group": r["group"], "title": r["title"],
                                "location": r["location"], "section0_title_words": words, "location_state": state})
    return {"groups": groups, "random_reject_miss": miss, "overrides": overrides, "false_friend_candidates": candidates,
            "section0_consistency": consistency}


def render(stats, sheet, version):
    L = [f"# Audit facts for filter {version} (generated by python -m jobwatch audit-stats from {sheet})", ""]
    L += ["| Group | Audited | Judged relevant | Judged not_relevant | Filter errors | OVERRIDEs |", "|---|---|---|---|---|---|"]
    for g in GROUP_ORDER:
        if g in stats["groups"]:
            s = stats["groups"][g]
            L.append(f"| {g} | {s['n']} | {s['relevant']}/{s['n']} | {s['not_relevant']}/{s['n']} | {len(s['errors'])}/{s['n']} | {s['overrides']}/{s['n']} |")
    if any(s["checklist"]["answered"] for s in stats["groups"].values()):
        L += ["", "Checklist answers (FILTER.md section 0; the questions stop at the first n, so a later check is not asked):", "",
              "| Group | Answered with checklist | Failed job family | Failed seniority | Failed location | Failed experience | All checks y |",
              "|---|---|---|---|---|---|---|"]
        for g in GROUP_ORDER:
            if g in stats["groups"]:
                c, n = stats["groups"][g]["checklist"], stats["groups"][g]["n"]
                L.append(f"| {g} | {c['answered']}/{n} | {c['failed_family']}/{c['answered']} | {c['failed_seniority']}/{c['answered']} | "
                         f"{c['failed_location']}/{c['answered']} | {c['failed_experience']}/{c['answered']} | {c['all_yes']}/{c['answered']} |")
    m = stats["random_reject_miss"]
    if m:
        lo, hi = m["ci95"]
        L += ["", f"Random rejects: miss rate {m['k']}/{m['n']} = {m['rate']:.4f}; exact (Clopper-Pearson) 95% interval "
              f"[{lo:.4f}, {hi:.4f}] (jobwatch/stats.py)."]
        if m["count_range_in_frame"]:
            a, b = m["count_range_in_frame"]
            L.append(f"Sampling frame: {m['frame']} rejects (all v1 rejects outside the held-out set; {m['rejects_in_run']} rejects in the run). "
                     f"Interval times frame: {a:.1f} to {b:.1f} relevant postings among the frame's rejects.")
    L += ["", "## Filter errors", ""]
    for g in GROUP_ORDER:
        for e in stats["groups"].get(g, {}).get("errors", []):
            L.append(f"- {g}: {e['posting_key']} \"{e['title']}\" ({e['location']}): filter {e['filter_decision']} "
                     f"({'; '.join(e['filter_reasons'])}); verdict {e['verdict']}"
                     + (f"; OVERRIDE: {e['override_reason']}" if e["override_reason"] else ""))
    L += ["", "## OVERRIDEs", ""]
    L += [f"- {o['posting_key']} ({o['group']}) \"{o['title']}\": {o['verdict']}; reason: {o['override_reason']}" for o in stats["overrides"]] or ["- none"]
    L += ["", "## Verdicts of relevant without an OVERRIDE where a mechanical reading of FILTER.md section 0 differs", "",
          "A title word from the section 0 seniority list (intern, staff, principal, director, lead, head, manager), or a "
          "location that is not Boston, New York/NYC, Seattle or US-qualified Remote (location_state as the filter reads it). "
          "This is a check of the rule's words, not a judgment of the posting; section 0 says the text takes priority over the title. "
          "Rows answered with the checklist are not checked here.", ""]
    L += [f"- {c['posting_key']} ({c['group']}) \"{c['title']}\" ({c['location']}): title words {c['section0_title_words'] or 'none'}; "
          f"location {c['location_state']}" for c in stats["section0_consistency"]] or ["- none"]
    L += ["", "## False-friend candidates (positive matches in postings judged not_relevant)", ""]
    for c in stats["false_friend_candidates"]:
        L.append(f"- {c['posting_key']} ({c['group']}, filter {c['filter_decision']}): {c['rule']} matched "
                 f"\"{c['quote']}\" in {c['field']} [{c['start']}:{c['end']}]; sentence: \"{c['sentence']}\"")
    if not stats["false_friend_candidates"]:
        L.append("- none")
    return "\n".join(L) + "\n"


def run(tools, sheet, outputs, lines):
    comments, columns, rows = sheets.read_sheet(tools, sheet)
    empty = [r["posting_key"] for r in rows if not r["verdict"].strip()]
    if empty:
        raise ValueError(f"{sheet}: {len(empty)} rows without a verdict")
    version = outputs[0]["version"]
    stats = compute(rows, outputs, lines, comments)
    base = sheet[:-len(".csv")]
    tools.write_file(f"{base}-stats.json", (json.dumps(stats, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    tools.write_file(f"{base}-facts.md", render(stats, sheet, version).encode("utf-8"))
    return stats, f"{base}-stats.json", f"{base}-facts.md"
