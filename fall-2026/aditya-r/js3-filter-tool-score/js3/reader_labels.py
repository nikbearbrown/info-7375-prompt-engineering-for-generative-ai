"""Reader labels for the shortlist: DUTY claims, and checks of rule-labeled LEVEL claims.

Source: READER (below), written by Claude Code on 2026-11-25 after reading each kept posting.
  .venv/bin/python -m js3.reader_labels  -> shortlist/reader_labels.json, with full verbatim quotes
A quote is given as a unique prefix of one description segment and expanded to that whole segment.
A prefix that is missing or ambiguous is an error.

DUTY reading rule (FILTER.md clarification C3):
- supported: a span describing the role's own duties or requirements states the item.
- insufficient: the item appears only in company, mission or team-culture text; or as one example in an
  "X, Y, or Z" option list; or as a description of the applicant's past exploration.
"""
import json
from pathlib import Path

from .corpus import load_corpus
from .text import readable, segments

ROOT = Path(__file__).resolve().parent.parent
BY = "Claude Code (reading), 2026-11-25"
S, I, C = "supported", "insufficient", "contradicted"
NG_WINDOW = "You will graduate"
FDE_DUTY = {"T3 llm": (S, "Develop cutting-edge GenAI solutions"), "T4 agents": (S, "Experience building GenAI applications, including RAG, multi-agent"),
            "T5 ml": (S, "Experience building production-grade machine learning deployments"),
            "T6 evaluation": (S, "Expertise in deploying production-grade GenAI applications, including evaluation"),
            "T8 cloud": (I, "Experience building production-grade machine learning deployments", "AWS is one of 'AWS, Azure, or GCP'")}
PY_OPTION = {"T1 python": (I, "You have implementation skills", "Python is one example in 'Python, Java, or C++'")}
GRAD = lambda prefix: {"label": C, "prefix": prefix, "note": "Priya completed her MS in 2025-12 (persona), so this graduation window excludes her. The rule said 'supported' from the 'New Grad' title. Whether it disqualifies her is Aditya's call (his label: check the window)."}
READER = {
    "ashby:notion:85947779-6b87-466a-98bc-30a640448c28": {"DUTY": {
        "T3 llm": (S, "You'll work on cutting-edge AI-powered features"),
        "T5 ml": (I, "Expertise building and prototyping", "describes the applicant's past exploration, not the role's work"),
        "T6 evaluation": (S, "Contribute to evals and iteration loops")}},
    "ashby:notion:e32799d2-8ef8-4803-8189-c72514afa816": {"DUTY": {
        "T1 python": (I, "Working towards a proficiency", "Python is one example among TypeScript, Node.js, or Python")},
        "LEVEL": GRAD("To be eligible for this role, you need to graduate in December 2026")},
    "greenhouse:databricks:6865698002": {"DUTY": PY_OPTION, "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:6865704002": {"DUTY": {
        "T5 ml": (I, "Our mission at Databricks", "company mission statement, not the role's duties (relevance without entailment)")},
        "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:6866549002": {"DUTY": PY_OPTION, "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:6886281002": {"DUTY": PY_OPTION, "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:8133691002": {"DUTY": PY_OPTION, "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:8847747002": {"DUTY": PY_OPTION, "LEVEL": GRAD(NG_WINDOW)},
    "greenhouse:databricks:8091041002": {"DUTY": {
        "T4 agents": (S, "You will work on Databricks’ Genie Code"),
        "T5 ml": (S, "You will help world’s largest companies build and deploy massive classical machine learning")},
        "LEVEL": {"label": C, "prefix": "2-8 years of engineering experience",
                  "note": "The rule also cites E 'junior', but that sentence describes the product's users ('the most junior data scientists'), not the role. It is a false friend that scores E +3 in v1.1."}},
    "greenhouse:databricks:8546367002": {"DUTY": FDE_DUTY, "LEVEL": {"label": C, "prefix": "It is not intended for internship",
        "note": "The rule said 'supported': its early-career phrase 'new graduate' sits inside a NEGATED sentence. A span was found, so the agent did not abstain. This is the abstention rule's limit."}},
    "greenhouse:databricks:8574655002": {"DUTY": {**FDE_DUTY, "T4 agents": (S, "7+ years of experience building GenAI applications")}},
    "greenhouse:databricks:8760167002": {"DUTY": FDE_DUTY},
    "greenhouse:databricks:8878946002": {"DUTY": {
        "T3 llm": (S, "Develop LLM solutions on customer data"), "T4 agents": (S, "Experience building Generative AI applications, including RAG, agents"),
        "T5 ml": (S, "We deliver professional services engagements"),
        "T8 cloud": (I, "Experience building production-grade machine learning deployments", "AWS is one of 'AWS, Azure, or GCP'")}},
    "greenhouse:figma:5551532004": {"DUTY": {
        "T1 python": (S, "Proficiency in Python"), "T3 llm": (S, "Design, build, and productionize ML models"),
        "T5 ml": (S, "Design, build, and productionize ML models"), "T6 evaluation": (S, "Build and maintain scalable data pipelines")}},
    "greenhouse:figma:6233043004": {"DUTY": {
        "T3 llm": (S, "Design, build, and productionize AI agents"), "T4 agents": (S, "Design, build, and productionize AI agents"),
        "T6 evaluation": (I, "Hands-on experience building applications with LLMs", "evaluation frameworks is one option in an 'or' list"),
        "T8 cloud": (I, "Knowledge of AWS Bedrock", "AWS Bedrock is one of several platforms in an 'or' list")}},
}


def expand(p, prefix):
    hits = [s for s in segments(readable(p["text"])) if s.startswith(prefix)]
    if len(set(hits)) != 1:
        raise SystemExit(f"{p['key']}: prefix {prefix!r} matches {len(set(hits))} segments")
    return hits[0]


def build():
    corpus = load_corpus()
    out = {}
    for key, entry in READER.items():
        p = corpus[key]
        duty = {}
        for g, v in entry.get("DUTY", {}).items():
            label, prefix, note = (v + ("",))[:3]
            duty[g] = {"label": label, "labeled_by": BY, "note": note,
                       "evidence": [{"field": "posting.description", "quote": expand(p, prefix)}]}
        o = {"DUTY": duty}
        if "LEVEL" in entry:
            lv = entry["LEVEL"]
            o["LEVEL"] = {"label": lv["label"], "labeled_by": BY, "note": lv["note"],
                          "evidence": [{"field": "posting.description", "quote": expand(p, lv["prefix"])}]}
        out[key] = o
    path = ROOT / "shortlist" / "reader_labels.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    o = build()
    print(f"{len(o)} postings; DUTY labels {sum(len(v['DUTY']) for v in o.values())}; LEVEL reader checks {sum('LEVEL' in v for v in o.values())}")
