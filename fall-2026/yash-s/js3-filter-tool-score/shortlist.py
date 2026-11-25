"""The source-grounded shortlist: every claim in each justification, labeled against the
posting's own text (FILTER.md sections 4-7).

    python3 shortlist.py [--run runs/filter-v1.1-2026-11-18T212545Z]

For the confirmed shortlist and the review-candidate shortlist (kept separate), the
filter's justification is split into claims: one per score component, plus the claims
a reader would be tempted to draw from them. A mechanical checker labels each claim
supported, contradicted or insufficient by the rules in CHECKER_RULES below, and
records the exact excerpt and the field it came from. The columns MY_LABEL and
MY_EXPLANATION are left blank for my own check. Nothing is sent anywhere.

Writes shortlist/claims-<run>.csv (create-only, so my columns are never overwritten)
and shortlist/SHORTLIST-<run>.md (regenerated from the CSV's checker columns).
"""
import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

import job_filter as J
import postings as P

HERE = Path(__file__).resolve().parent
DEFAULT_RUN = HERE / "runs" / "filter-v1.1-2026-11-18T212545Z"
OUT_DIR = HERE / "shortlist"
# Two real postings outside the shortlist, used for the relevance-versus-entailment case
# because my own audit labels exist for them.
EXTRA = [("OpenAI", "e9bea775-7eb6-438a-ab96-27d5f941e69d", "audit row 60"),
         ("OpenAI", "ca9e0aeb-6df1-4b73-8ec0-2e9e124712f1", "audit row 40")]
AUDIT_SHEET = HERE / "audit" / "sample-filter-v1.1-2026-11-18T212545Z" / "labeling-sheet.csv"

# ---------------------------------------------------------------- the checker

HEADING_KINDS = [  # checked in this order; first match wins; compared in lower case
    ("not required", ["need not have"]),
    ("preferred", ["preferred", "nice to have", "bonus", "may also", "may have", "will also have"]),
    ("requirement", ["minimum qualifications", "qualifications", "good fit if you", "thrive in this role",
                     "thrive in this role if", "what we look for", "what we're looking for", "looking for someone",
                     "your background might look"]),
    ("responsibility", ["responsibilit", "in this role, you will", "in this role you will", "what you'll do",
                        "what you'll own", "impact you will have", "impact you'll have", "representative projects",
                        "sample projects", "about the role", "you'll be responsible"]),
    ("company or team", ["about anthropic", "about openai", "about databricks", "about the team", "about the teams",
                         "about the rl teams", "about horizons", "how we're different", "come work with us", "logistics",
                         "annual salary", "compliance", "our commitment", "pay range", "location and workplace",
                         "mission", "related roles"]),
]
EARLY_CAREER = ["early-career", "early career", "entry-level", "entry level", "new grad", "new graduate",
                "recent graduate", "0-1 years", "0–1 years", "no prior experience", "no professional experience"]
EXPERIENCED_SIGNALS = [r"\bseasoned\b", r"\bsignificant (?:\w+ ){0,2}experience", r"\bextensive (?:\w+ ){0,2}experience",
                       r"\bdeep (?:expertise|experience)", r"\btrack record\b", r"\bsenior\b", r"\d+\s*\+\s*years",
                       r"\bseveral years\b", r"\byears of (?:\w+ ){0,3}experience"]
OTHER_TEAM = re.compile(r"\b(partner|work|collaborat)\w*\s+(?:\w+\s+){0,2}with\b.{0,160}\bteams?\b", re.IGNORECASE)

CHECKER_RULES = {
    "title": "supported: the words appear in the title, which is what Rule 1 reads",
    "mention": "supported: the phrase appears word for word in the job-specific text",
    "work": ("supported only if a sentence with one of the category's phrases sits under a requirement or "
             "responsibility heading; otherwise insufficient. A mention under a company, team, preferred or "
             "unclear heading does not establish that the role does this work"),
    "skill-named": "supported: the skill appears word for word in the job-specific text",
    "skill-required": ("supported only if a sentence naming the skill sits under a requirement heading and has no "
                       "preferred word; otherwise insufficient"),
    "location": "supported if a location part is US by Rule 7; insufficient if unknown; contradicted if every part is outside the US",
    "experience": ("from Rule 8: compatible -> supported; a mandatory minimum above eight months -> contradicted; "
                   "unknown -> insufficient, and the agent says \"I cannot tell\""),
    "early-career": ("supported only by an explicit early-career statement; contradicted by a seniority exclusion or a "
                     "mandatory minimum above the cutoff; otherwise insufficient, with any experienced-candidate wording "
                     "quoted (Anthropic's standard experience sentence is not counted as such wording)"),
}


def heading_kind(heading):
    h = (heading or "").lower().replace("’", "'")
    for kind, words in HEADING_KINDS:
        if any(w in h for w in words):
            return kind
    return "other"


def where(s):
    return f"description, under '{s['heading']}'" if s["heading"] else "description (no heading)"


def find(job, phrase):
    return [s for s in job if J.has(phrase, s["text"])]


def has_preferred_word(text, rules):
    return any(J.has(w, text) for w in rules["filter"]["experience"]["preferred_words"])


def claims_for(posting, result, rules):
    """The justification for one posting, as labeled claims."""
    _, job = J.job_specific(posting, rules)
    out = []

    def add(kind, claim, label, field, excerpt, caution=""):
        out.append({"claim_kind": kind, "claim": claim, "checker_label": label, "checker_rule": CHECKER_RULES[kind],
                    "source_field": field, "source_excerpt": excerpt, "caution": caution})

    role_names = {"target": "a target", "related": "a related technical", "special_review": "a special-review"}
    if result["role"] in role_names:
        add("title", f"The title names {role_names[result['role']]} role (it contains '{result['role_match']}').",
            "supported", "title", posting["title"])

    topic_phrases = {c: ps for c, ps in rules["filter"]["topics"].items() if not c.startswith("_")}
    for cat, phrase in result["topics"].items():
        first = find(job, phrase)[0]
        add("mention", f"The job text mentions {cat} ('{phrase}').", "supported", where(first), first["text"])
        hits = [s for p in topic_phrases[cat] for s in find(job, p)]
        work = [s for s in hits if heading_kind(s["heading"]) in ("requirement", "responsibility")]
        if work:
            s = work[0]
            caution = "the supporting sentence may describe another team, not this role" if OTHER_TEAM.search(s["text"]) else ""
            add("work", f"{cat} is part of this role's own work or requirements.", "supported", where(s), s["text"], caution)
        else:
            kinds = sorted({heading_kind(s["heading"]) for s in hits})
            add("work", f"{cat} is part of this role's own work or requirements.", "insufficient", where(hits[0]),
                hits[0]["text"], f"every mention sits under a {' / '.join(kinds)} heading")

    for skill in result["skills"]:
        hits = find(job, skill)
        add("skill-named", f"The job text names {skill}, which is on Priya's résumé.", "supported", where(hits[0]), hits[0]["text"])
        req = [s for s in hits if heading_kind(s["heading"]) == "requirement" and not has_preferred_word(s["text"], rules)]
        if req:
            add("skill-required", f"The posting requires {skill}.", "supported", where(req[0]), req[0]["text"])
        else:
            kinds = sorted({heading_kind(s["heading"]) for s in hits})
            add("skill-required", f"The posting requires {skill}.", "insufficient", where(hits[0]), hits[0]["text"],
                f"named only under a {' / '.join(kinds)} heading or with a preferred word")

    loc = result["location_status"]
    us_parts = [p for p, k in result["location_parts"] if k == "us"]
    label = {"us": "supported", "unknown": "insufficient", "non_us": "contradicted"}[loc]
    add("location", "The role can be done from a US location.", label, "location",
        "; ".join(us_parts) if us_parts else (posting["location"] or "(no location)"))

    st, det = result["experience_status"], result["experience_detail"]
    if st == "compatible":
        add("experience", "Priya's eight months meet the posting's required experience.", "supported",
            "description", result["experience_reason"])
    decisive = max(det["units"], key=lambda u: u.get("min") or 0) if det["units"] else {}
    if st == "compatible":
        add("experience", "Priya's eight months meet the posting's required experience.", "supported",
            "description", result["experience_reason"])
    elif st in ("above_cutoff", "within_cutoff"):
        add("experience", "Priya's eight months meet the posting's required experience.", "contradicted",
            "description", decisive.get("sentence") or result["experience_reason"], result["experience_reason"])
    else:
        bp = rules["filter"]["experience"]["anthropic_boilerplate"]
        if det["preferred"]:
            ex = f"Preferred, not required: \"{det['preferred'][0]['sentence']}\" ({det['preferred'][0]['why']})"
        else:
            ex = next((s["text"] for s in job if bp.lower() in s["text"].lower()), "No year count in the job-specific text.")
        add("experience", "Priya's eight months meet the posting's required experience.", "insufficient",
            "description", ex, "the agent must say \"I cannot tell\" (FILTER.md section 6)")

    text = "\n".join(s["text"] for s in job)
    early = [p for p in EARLY_CAREER if J.has(p, text)]
    bp = rules["filter"]["experience"]["anthropic_boilerplate"].lower()
    if result["hard_exclusions"] and any(h.startswith("seniority") for h in result["hard_exclusions"]):
        add("early-career", "The posting is open to an early-career candidate like Priya.", "contradicted",
            "title/description", next(h for h in result["hard_exclusions"] if h.startswith("seniority")))
    elif st == "above_cutoff":
        add("early-career", "The posting is open to an early-career candidate like Priya.", "contradicted",
            "description", decisive.get("sentence") or result["experience_reason"], result["experience_reason"])
    elif early:
        s = find(job, early[0])[0]
        add("early-career", "The posting is open to an early-career candidate like Priya.", "supported", where(s), s["text"])
    else:
        signals = []
        for pat in EXPERIENCED_SIGNALS:
            s = next((x for x in job if re.search(pat, x["text"], re.IGNORECASE) and bp not in x["text"].lower()), None)
            if s and s["text"] not in [x["text"] for x in signals]:
                signals.append(s)
        ex = " | ".join(f"[{x['heading'] or 'no heading'}] {x['text']}" for x in signals[:2]) or "No early-career statement."
        add("early-career", "The posting is open to an early-career candidate like Priya.", "insufficient",
            "description", ex, "no explicit early-career statement" + ("; experienced-candidate wording quoted" if signals else ""))
    return out


# ----------------------------------------------------------------- the output

CSV_FIELDS = ["list", "rank", "board", "posting_id", "title", "score", "claim_id", "claim_kind", "claim",
              "checker_label", "checker_rule", "source_field", "source_excerpt", "caution", "MY_LABEL", "MY_EXPLANATION"]


def build(run, js2):
    results = {(r["board"], str(r["id"])): r for r in json.loads((run / "results.json").read_text(encoding="utf-8"))}
    persona, _ = P.load_persona(js2)
    rules = J.load_rules(persona=persona)
    by_key = {(p["board"], p["id"]): p for p in P.load_saved_postings(js2)[0]}
    lists = [("confirmed", J.confirmed_shortlist(list(results.values()))),
             ("review-candidate", J.review_candidates(list(results.values()), rules)),
             ("example outside the shortlist", [results[(b, i)] for b, i, _ in EXTRA])]
    rows = []
    for name, recs in lists:
        for rank, r in enumerate(recs, 1):
            k = (r["board"], str(r["id"]))
            again = J.evaluate(by_key[k], rules)
            if again["decision"] != r["decision"] or again["score"] != r["score"]:
                raise SystemExit(f"{k}: the saved result no longer reproduces; stop")
            for n, c in enumerate(claims_for(by_key[k], r, rules), 1):
                rows.append({"list": name, "rank": rank, "board": r["board"], "posting_id": r["id"], "title": r["title"],
                             "score": r["score"], "claim_id": f"{r['board'][0]}{str(r['id'])[:8]}-C{n}", **c,
                             "MY_LABEL": "", "MY_EXPLANATION": ""})
    return rows, results, rules, lists


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def report(run, rows, results, rules, lists):
    by_post = collections.OrderedDict()
    for r in rows:
        by_post.setdefault((r["list"], r["board"], r["posting_id"]), []).append(r)
    L = [f"# Source-grounded shortlist: {run.name}", "",
         "Generated by `python3 shortlist.py`. Do not edit by hand. The checker labels below are produced by code "
         "from the rules in FILTER.md section 5; my own check goes in the `MY_LABEL` and `MY_EXPLANATION` columns of "
         f"`claims-{run.name}.csv`.", "",
         f"- Confirmed shortlist: {len(lists[0][1])} postings. "
         + ("It is empty: no posting met every confirmed condition, so nothing below is a confirmed match." if not lists[0][1] else ""),
         f"- Review-candidate shortlist: the top {len(lists[1][1])} of the review queue by score, then board, then ID. "
         "Every one is **unconfirmed**.",
         "- One example outside the shortlist, for the relevance-versus-entailment case.", "",
         "## How each claim is labeled", "", "| Claim kind | Rule the checker applies |", "|---|---|"]
    L += [f"| {k} | {md_cell(v)} |" for k, v in CHECKER_RULES.items()]
    L += ["", "Heading kinds, checked in order (first match wins): "
          + "; ".join(f"**{k}**: {', '.join(repr(w) for w in ws)}" for k, ws in HEADING_KINDS) + "; anything else is **other**.", ""]
    totals = collections.Counter((r["list"], r["checker_label"]) for r in rows)
    L += ["## Label totals", "", "| List | Supported | Contradicted | Insufficient | Claims |", "|---|---:|---:|---:|---:|"]
    for name, _ in lists:
        n = sum(v for (l, _), v in totals.items() if l == name)
        if n:
            L.append(f"| {name} | {totals[(name, 'supported')]} | {totals[(name, 'contradicted')]} | "
                     f"{totals[(name, 'insufficient')]} | {n} |")

    for (lst, board, pid), cl in by_post.items():
        r = results[(board, pid)]
        L += ["", f"## {lst} #{cl[0]['rank']}: {r['title']} ({board} `{pid}`)", "",
              f"Score {r['score']} ({', '.join(f'{k} {v}' for k, v in r['points'].items())}). Decision: **{r['decision']}**"
              + (f", because {'; '.join(r['review_reasons'])}." if r["review_reasons"] else "."), f"URL: {r['url']}", "",
              "| Claim | Label | Field | Excerpt from the posting | Caution |", "|---|---|---|---|---|"]
        for c in cl:
            ex = c["source_excerpt"]
            ex = ex if len(ex) <= 260 else ex[:257] + "…"
            L.append(f"| `{c['claim_id']}` {md_cell(c['claim'])} | **{c['checker_label']}** | {md_cell(c['source_field'])} | "
                     f"{md_cell(ex)} | {md_cell(c['caution'])} |")

    L += relevance_section(rows) + abstention_section(rows, results)
    return "\n".join(L) + "\n"


def relevance_section(rows):
    L = ["", "## Relevance is not entailment", "",
         "A *mention* claim is relevance: the posting contains the words. A *work* or *required* claim is what a "
         "justification usually wants to say. The rows below are claims where the mention is supported but the "
         "stronger claim is not.", "", "| Posting | Supported mention | Not entailed | Why |", "|---|---|---|---|"]
    for r in rows:
        if r["claim_kind"] in ("work", "skill-required") and r["checker_label"] == "insufficient":
            mention = next((m for m in rows if m["posting_id"] == r["posting_id"] and m["claim_kind"] in ("mention", "skill-named")
                            and m["source_excerpt"] == r["source_excerpt"]), None)
            L.append(f"| {r['title']} (`{r['claim_id']}`) | {md_cell(mention['claim'] if mention else '')} | "
                     f"{md_cell(r['claim'])} | {md_cell(r['caution'])}: \"{md_cell(r['source_excerpt'][:180])}\" |")
    a60, a40 = audit_label(*EXTRA[0][:2]), audit_label(*EXTRA[1][:2])
    L += ["", f"**Main case (real posting, {EXTRA[0][2]}):** OpenAI `{EXTRA[0][1]}`, Security Engineer, Agent Security. "
          "The filter kept it in review with 65 points. Its only topic is one phrase, 'agentic systems', which also makes the "
          "title count as a related role. The checker labels \"The job text mentions AI applications ('agentic systems')\" "
          "**supported**: the words are there. The posting's sentence is \"Your role will involve designing and implementing "
          "robust security frameworks, policies, and controls to safeguard OpenAI's critical assets and ensure the safe "
          "deployment of agentic systems.\" That supports *securing* agentic systems, not *building* AI applications. The "
          "requirements ask for isolation techniques, kernel-level hardening and network security, and AI/ML security "
          "familiarity is listed as \"nice-to-have but valuable\".",
          "",
          "The checker also labels the stronger claim \"AI applications is part of this role's own work or requirements\" "
          "**insufficient**, but for a shallow reason: OpenAI put that sentence under the heading 'About the Team'. The label "
          "is right, but the checker's reason is not the real one. Under a different heading, the same sentence would have been "
          "marked supported.",
          "", f"My own audit label for this posting: **{a60.get('MY_VERDICT', '(not labeled)')}**: "
          f"\"{a60.get('MY_REASON', '')}\" (false friend I named: `{a60.get('FALSE_FRIEND_WORD', '')}`). "
          "Removing that one phrase drops the score from 65 to 35 and the posting is rejected (`audit-results.md`).", "",
          f"**Second case ({EXTRA[1][2]}):** OpenAI `{EXTRA[1][1]}`, Applied AI Engineer, Plugins. The title matches a target "
          "role, so the title claim is **supported** and the posting is topically relevant. But the claim \"Priya's eight months "
          "meet the posting's required experience\" is **contradicted**: \"Have 4-6 years of professional software engineering "
          f"experience…\". My audit label: **{a40.get('MY_VERDICT', '(not labeled)')}**: \"{a40.get('MY_REASON', '')}\"", "",
          "**Checker limit, shown by its own output:** a *work* claim marked supported with a caution comes from a sentence "
          "about working *with* a team (for example, the #1 candidate's \"You'll partner closely with … the central data "
          "engineering team\"). The heading says the sentence describes the role, but the team named in the sentence is the "
          "one that does the work. For that posting the claim is still true, because the title is Data Engineer. But the "
          "excerpt is not the evidence for it. The checker cannot read that difference, so a person has to. The caution is "
          "itself a pattern match and can misfire: on #5 (Recruiting Analytics Data Engineer) it fires on \"working with a "
          "team that's actively experimenting with AI\", but the same sentence says \"you'll build the technical "
          "foundation\", which is the role's own work.", ""]
    return L


def abstention_section(rows, results):
    queue = [r for r in results.values() if r["decision"] == "review"]
    unknown_q = sum(r["experience_status"] == "unknown" for r in queue)
    anth = [r for r in results.values() if r["board"] == "Anthropic"]
    anth_unknown = sum(r["experience_status"] == "unknown" for r in anth)
    top = next(r for r in rows if r["list"] == "review-candidate" and r["rank"] == 1 and r["claim_kind"] == "experience")
    L = ["## The abstention rule and a counterexample", "",
         "**Rule (FILTER.md section 6):** when the posting does not state a mandatory year count, or states one that cannot "
         "be read reliably, the agent answers \"I cannot tell\" about experience, labels the experience claim "
         "insufficient, and an otherwise promising posting (score at least 65) goes to the review queue instead of the "
         "confirmed shortlist.", "",
         f"**How often it fires:** {unknown_q} of the {len(queue)} review-queue postings are there because experience is "
         f"unknown. On Anthropic, {anth_unknown} of {len(anth)} postings have unknown experience, partly because every Anthropic "
         "posting carries the same sentence, \"Years of experience required will correlate with the internal job level "
         "requirements for the position\", which Rule 8 sets aside.", "",
         f"**Counterexample:** the #1 review candidate, {top['title']} ({top['board']} `{top['posting_id']}`, score "
         f"{results[(top['board'], top['posting_id'])]['score']}). The rule abstains, correctly: there is no mandatory year "
         f"count. But the posting says: {top['source_excerpt']}. The abstention avoids a false claim that Priya is eligible, "
         "yet the ranking still puts this posting first, above postings with no evidence against Priya's fit. "
         "\"I cannot tell\" is treated as neutral when the text actually leans one way. The rule protects against a false "
         "*yes*; it does nothing to stop a likely *no* from being ranked first.", ""]
    return L


def audit_label(board, pid):
    if not AUDIT_SHEET.exists():
        return {}
    with open(AUDIT_SHEET, encoding="utf-8", newline="") as f:
        return next((r for r in csv.DictReader(f) if r["board"] == board and r["posting_id"] == pid), {})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=str(DEFAULT_RUN))
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2))
    args = ap.parse_args(argv)
    run = Path(args.run).resolve()
    rows, results, rules, lists = build(run, args.js2)
    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / f"claims-{run.name}.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8", newline="") as f:
            old = list(csv.DictReader(f))
        same = [[o[k] for k in CSV_FIELDS[:-2]] for o in old] == [[str(r[k]) for k in CSV_FIELDS[:-2]] for r in rows]
        print(f"{csv_path.relative_to(HERE)} exists; kept as is (checker columns {'unchanged' if same else 'DIFFER - check'})")
    else:
        with open(csv_path, "x", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {csv_path.relative_to(HERE)} ({len(rows)} claims)")
    md = OUT_DIR / f"SHORTLIST-{run.name}.md"
    md.write_text(report(run, rows, results, rules, lists), encoding="utf-8")
    print(f"wrote {md.relative_to(HERE)}")
    c = collections.Counter((r["list"], r["checker_label"]) for r in rows)
    for k, v in sorted(c.items()):
        print(f"  {k[0]:32} {k[1]:13} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
