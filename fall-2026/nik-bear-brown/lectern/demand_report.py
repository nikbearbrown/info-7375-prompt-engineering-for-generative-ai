#!/usr/bin/env python3
"""demand_report.py — rank COMPANIES by whether they want this work done, not postings by fit.

    python3 demand_report.py --all-jobs <all-jobs-DATE.json> --kept <jobs-of-interest-DATE.json> --out <file.md>

Professor Bear, 2026-09-26: "don't use full-time or remote as an absolute flag to remove something.
I think if I'm good enough, they'll make a role for it." So employment type and location are CONTEXT
in this report and never a filter. A posting is not a slot to fit into — it is evidence that a company
has decided this work is worth paying for. The unit of analysis is therefore the company.

Five kinds of evidence, weakest to strongest as a signal of institutional commitment:
  SELLS      an education revenue line exists, so there is a budget
  ENABLES    it trains its own staff, so materials get made internally
  ADVOCATES  it staffs people to teach a public
  TEACHES    it hires teachers and materials-makers outright
  BUILDS     it staffs an education PRODUCT team — an org-chart fact, the hardest to fake

A company showing four or five of these has an education business, not a vacancy. That is the
company to talk to whether or not today's posting is shaped like the job you want.

Stdlib only. Ranks companies; judges no person's fit.
"""
import argparse, json, os, re
from collections import defaultdict

CATEGORY = {
    "TEACHES":   ["TEACHING", "MATERIALS"],
    "ADVOCATES": ["ADVOCACY"],
    "BUILDS":    ["EDU_PRODUCT"],
    "SELLS":     ["EDU_SALES"],
    "ENABLES":   ["SALES_ENABLEMENT", "CUSTOMER_ENABLEMENT"],
}
ORDER = ["BUILDS", "TEACHES", "ADVOCATES", "SELLS", "ENABLES"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all-jobs", required=True)
    ap.add_argument("--kept", required=True)
    ap.add_argument("--families", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "title_families.json"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    fams = json.load(open(a.families, encoding="utf-8"))["families"]
    allj = json.load(open(a.all_jobs, encoding="utf-8"))
    kept = json.load(open(a.kept, encoding="utf-8"))["records"]

    def fam(title):
        for f in fams:
            if re.search(f["pattern"], title.lower()):
                return f["name"]
        return "UNCLASSIFIED"

    rev = {f: c for c, fs in CATEGORY.items() for f in fs}
    board = {s["company"]: s["postings"] for s in allj["sources"] if s["status"] == "ok"}
    ev = defaultdict(lambda: defaultdict(list))
    for r in kept:
        c = rev.get(fam(r["title"]))
        if c:
            ev[r["company"]][c].append(r)

    rows = []
    for co, n in board.items():
        cats = [c for c in ORDER if ev[co][c]]
        total = sum(len(ev[co][c]) for c in ORDER)
        rows.append((len(cats), total, co, n, cats))
    rows.sort(key=lambda x: (-x[0], -x[1]))

    L = [f"# Which companies want this work — {allj['generated_at'][:10]}", "", "## Executive summary", "",
         "**What this is.** The 18 watched companies ranked by whether they have decided that teaching, "
         "materials-making, and advocacy are worth paying for — measured from their own open postings.", "",
         "**Why it is built this way.** Professor Bear, 2026-09-26: *\"don't use full-time or remote as an absolute "
         "flag to remove something. I think if I'm good enough, they'll make a role for it.\"* So a posting is not a "
         "slot to fit into; it is evidence about a company. **Location and employment type appear here as context "
         "and are never used to exclude anything.** The unit of analysis is the company.", "",
         "**The five kinds of evidence**, weakest to strongest as a signal of commitment:", "",
         "| | Evidence | What it proves |", "|---|---|---|",
         "| **SELLS** | education sales roles | an education revenue line exists, so there is a budget |",
         "| **ENABLES** | internal enablement roles | it already makes training materials for its own staff |",
         "| **ADVOCATES** | advocates, DevRel | it pays people to teach a public |",
         "| **TEACHES** | educators, instructors, docs and content engineers | it hires teachers outright |",
         "| **BUILDS** | an education *product* team | an org-chart fact, and the hardest of the five to fake |", "",
         "A company showing four or five has an education **business**, not a vacancy — and that is the company "
         "worth a conversation whether or not today's posting is the shape you want.", "", "---", "",
         "## The ranking", "",
         "| Company | Board | Signal roles | Kinds | BUILDS | TEACHES | ADVOCATES | SELLS | ENABLES |",
         "|---|---:|---:|---:|---|---|---|---|---|"]
    for nc, total, co, n, cats in rows:
        cells = "".join(f" {len(ev[co][c]) if ev[co][c] else '·'} |" for c in ORDER)
        L.append(f"| **{co}** | {n:,} | {total} | **{nc}/5** |{cells}")
    L += ["", "## What each company is actually hiring", ""]
    for nc, total, co, n, cats in rows:
        if not total:
            continue
        L += [f"### {co} — {nc} of 5 kinds, {total} roles of {n:,} postings", ""]
        for c in ORDER:
            for r in ev[co][c]:
                L.append(f"- **{c}** · [{r['title'].strip()}]({r['url']}) — {r['location_text'] or 'location not stated'}")
        L.append("")
    quiet = [co for nc, total, co, n, cats in rows if not total]
    if quiet:
        L += ["### No signal today", "",
              "These are still watched every run, because a company with nothing today is a company that may post "
              f"tomorrow: {', '.join(quiet)}.", ""]
    L += ["## Absent from this table is not the same as absent from the market", "",
          "Nine watched companies cannot be read by Lectern at all, and **four of them are the deepest education "
          "players on the list** — Adobe, Salesforce, GitHub, and Google. They have no row above. That is a hole in "
          "the measurement, not a finding about them, and the table would be actively misleading without this "
          "paragraph.", "",
          "**Google is the proof.** It has no public JSON feed — three endpoint shapes were tried on 2026-09-26 and "
          "all returned 404 — but its careers site is perfectly readable by a person. One search for *\"education\"* "
          "in the United States returns **20 education roles on the first page**: Google for Education product "
          "managers and engineers, *Head of Industry, Education*, *Product Marketing Manager, Google Classroom*, two "
          "*Brand Marketing Manager, AI Education* posts, *Brand Marketing Manager, Educator Social*, higher-ed sales "
          "and forward-deployed engineering. A search for *\"NotebookLM\"* returns six more, including *Senior UX "
          "Researcher, **Learning Frontiers, LearnX*** — a learning organisation invisible from outside.", "",
          "On the five-kind measure Google shows **BUILDS** and **SELLS** outright plus a dedicated AI-education "
          "marketing function, which would put it at or near the top of the table. It is missing because of an API, "
          "not because of a strategy. The manual check and its URL are recorded in `sources.json`.", "",
          "---", "", "## How to read a low number",
          "", "A small board with one teaching role (Webflow: 1 of 27) is a *stronger* signal than a huge board with "
          "two (OpenAI: 2 of 830) — except that OpenAI also **BUILDS**, which outweighs the rate. Rate and kind say "
          "different things, and neither is a ranking of how good the job would be. Nothing here is a judgment about "
          "any individual posting, and nothing was excluded for being full-time or on-site.", ""]
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {a.out} — {len(rows)} companies ranked, {sum(r[1] for r in rows)} signal roles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
