"""The source-grounded shortlist: every claim behind a kept posting, with a quote and a label.

    python3 src/shortlist.py --run-id live-20261114

For each posting the current filter keeps, the justification is split into claims. Each claim
gets the posting text it rests on and a label from a mechanical checker, following the evidence
rules in FILTER.md section 3:
  supported     the quoted sentence states the claim
  contradicted  the quoted sentence states the opposite
  insufficient  nothing quoted states it (a word appearing is not enough)
The checker's labels are a RECORD of these rules, not a judgment. Smit's own labels are kept
separately in audit/shortlist-hand-labels.json and compared by --compare.
Writes audit/shortlist.json.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
from postings import ROOT, load_run  # noqa: E402
from run_filter import load_skills  # noqa: E402

ENTRY_LEVEL = re.compile(r"\b(new grad(uate)?s?|entry[- ]level|junior|early[- ]career|recent graduates?)\b", re.I)
LEVEL_VARIES = re.compile(r"(span more than one career level|varying seniority levels?|multiple levels|"
                          r"level(ing)? (is|will be) (determined|decided))", re.I)
# e.g. / i.e. sit outside the \b group: "\be\.g\.\b" never matches "e.g.," (no word boundary after ".")
HEDGE = re.compile(r"\b(e\.g\.|i\.e\.)|\b(such as|like|is a plus|a plus|bonus|nice to have|familiar(ity)?|"
                   r"preferred|ideally)\b", re.I)
NEGATION = re.compile(r"\b(not required|no (prior )?experience (with|in) .* (needed|required))\b", re.I)


def in_or_list(sentence, skill):
    """True when the skill sits in an either/or list: 'TypeScript, Python, or Ruby'."""
    m = flt.find_whole(skill, sentence)
    if not m:
        return False
    window = sentence[max(0, m.start() - 80):m.end() + 80]
    return bool(re.search(r",\s*(or|and/or)\s+\w|\w\s+or\s+\w", window)) and "," in window


def skill_label(sentence, skill):
    if NEGATION.search(sentence):
        return "contradicted", "the sentence says it is not required"
    if HEDGE.search(sentence) or in_or_list(sentence, skill):
        return "insufficient", "named only as an example or one option, not as what the job uses"
    return "supported", "the sentence says the job uses it"


def claims_for(posting, verdict):
    title, text = posting["title"], posting["text"]
    claims = []
    role = next(e for e in verdict["evidence"] if e["check"] == "role")
    claims.append({"claim": "The job is a software engineering role.", "quote": title,
                   "checker": "supported", "why": f"title contains «{role['quote']}»"})
    level_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", text) if LEVEL_VARIES.search(s)]
    entry = ENTRY_LEVEL.search(title + "\n" + text)
    claims.append({"claim": "The job is open at an early-career level (not senior, lead, manager or intern).",
                   "quote": " / ".join([f"Title: {title}"] + level_sents) if level_sents else f"Title: {title}",
                   "checker": "supported" if entry else "insufficient",
                   "why": (f"text says «{entry.group(0)}»" if entry else
                           "no level word in the title is an absence, not a statement; "
                           + ("the text says the level is decided later" if level_sents else "the text does not state a level"))})
    loc = next(e for e in verdict["evidence"] if e["check"] == "location")
    claims.append({"claim": "The job is in the United States.", "quote": f"{loc['field']}: {loc['quote']}",
                   "checker": "supported", "why": "a US place or country code is stated"})
    status, yq, ysent = flt.years_requirement(text, flt.CURRENT["years_bound"])
    claims.append({"claim": "The job asks for fewer than 4 years of experience.",
                   "quote": ysent or "(no sentence in the posting states a number of years)",
                   "checker": {"ok": "supported", "too_many": "contradicted"}.get(status, "insufficient"),
                   "why": {"ok": f"«{yq}» is under 4", "too_many": f"«{yq}» is 4 or more"}.get(
                       status, "the posting does not say how many years")})
    for e in verdict["evidence"]:
        if e["check"] == "skill":
            label, why = skill_label(e["context"], e["quote"])
            claims.append({"claim": f"The job uses {e['quote']}.", "quote": e["context"], "checker": label, "why": why})
    for i, c in enumerate(claims, 1):
        c["claim_id"] = f"{posting['board']}:{posting['id']}#{i}"
    return claims


def build(run_id):
    postings, _, _ = load_run(run_id)
    skills = load_skills()
    kept = [(p, v) for p in postings for v in [flt.judge(p, skills)] if v["verdict"] == "keep"]
    kept.sort(key=lambda pv: -pv[1]["score"])
    out = {"run_id": run_id, "filter_version": flt.FILTER_VERSION, "shortlist": []}
    for p, v in kept:
        out["shortlist"].append({"board": p["board"], "id": p["id"], "title": p["title"], "url": p["url"],
                                 "score": v["score"], "claims": claims_for(p, v)})
    with open(os.path.join(ROOT, "audit", "shortlist.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    return out


def compare():
    with open(os.path.join(ROOT, "audit", "shortlist.json"), encoding="utf-8") as f:
        claims = {c["claim_id"]: c for s in json.load(f)["shortlist"] for c in s["claims"]}
    with open(os.path.join(ROOT, "audit", "shortlist-hand-labels.json"), encoding="utf-8") as f:
        hand = json.load(f)["labels"]
    agree = sum(claims[k]["checker"] == v for k, v in hand.items())
    print(f"checker agrees with Smit on {agree}/{len(hand)} claims")
    for k, v in hand.items():
        if claims[k]["checker"] != v:
            print(f"  {k}: checker {claims[k]['checker']}, Smit {v} | {claims[k]['claim']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="live-20261114")
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()
    if a.compare:
        return compare()
    for s in build(a.run_id)["shortlist"]:
        print(f"\n== {s['title']} ({s['board']}, score {s['score']})")
        for c in s["claims"]:
            print(f"  [{c['checker']:12}] {c['claim_id']} {c['claim']}\n      quote: {c['quote'][:200]}")


if __name__ == "__main__":
    main()
