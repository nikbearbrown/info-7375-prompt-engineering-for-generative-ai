"""Source-grounded shortlist (FILTER.md section 2) from a saved filter run.

    python3 -m agent.shortlist evidence/filter-v1.2/decisions.jsonl   # -> shortlist/shortlist.md + .json

Each kept posting (grouped by board + title) gets five claims, each labeled
supported / contradicted / insufficient against the posting's own title,
location and text, with verbatim quotes. A filter rule firing is never used
as evidence: the claims are re-read from the text here.

  role    "This is a software engineering role."        title has a FILTER.md R1 role phrase
  years   "It asks for at most 2 years of experience."   years phrase near "experience" (N <= 2 / N >= 3),
                                                         or "No fixed minimum years"
  entry   "It is written for an entry-level engineer."   says new grad / early career / entry level /
                                                         internship experience / no fixed minimum;
                                                         contradicted by "track record" / "proven ability".
                                                         Years alone and title numerals ("Engineer I") are NOT support.
  us      "It is open to someone in the US."             location field only, never inferred
  skill   "The role uses at least one of Sam's skills."  a sentence naming the skill that is not a
                                                         nice-to-have ("is a plus", "bonus", "preferred", "not required")

Lists: any contradicted claim -> "contradicted" (shown, not ranked);
else 2+ insufficient -> "I cannot tell"; else ranked by filter score.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from agent import filter as F
from agent import skills as SK
from agent.postings import load_run

RUN = F.RUN
ENTRY = re.compile(r"\b(new grads?|new graduates?|early[- ]career|entry[- ]level|internship experience|"
                   r"No fixed minimum years)\b", re.I)
MID = re.compile(r"\b(track record|proven ability)\b", re.I)
NO_MIN = re.compile(r"No fixed minimum years", re.I)
NICE = re.compile(r"\b(is a plus|a plus\b|nice to have|bonus|preferred|not required)", re.I)
MAX_QUOTE = 240

CLAIMS = {
    "role": "This is a software engineering role.",
    "years": "It asks for at most 2 years of experience.",
    "entry": "It is written for an entry-level engineer.",
    "us": "It is open to someone in the US.",
    "skill": "The role uses at least one of Sam's skills.",
}


def sentence(text: str, start: int, end: int) -> str:
    """The sentence or line around text[start:end], as an exact slice of text."""
    nl, dot = text.rfind("\n", 0, start), text.rfind(". ", 0, start)
    s = max(nl + 1, dot + 2 if dot >= 0 else 0)
    nl, dot = text.find("\n", end), text.find(". ", end)
    cands = [i for i in (nl, dot + 1 if dot >= 0 else -1) if i >= 0]
    e = min(cands) if cands else len(text)
    q = text[s:e].strip()
    if len(q) > MAX_QUOTE:
        q = text[max(s, start - 100): min(e, end + 100)].strip()
    return q


def claim(cid: str, label: str, quotes=(), looked_for: str = "") -> dict:
    return {"id": cid, "claim": CLAIMS[cid], "label": label, "quotes": list(quotes), "looked_for": looked_for}


def _years(text: str):
    """[(N, quote)] like filter.find_years, but quoting the whole sentence."""
    out = []
    for m in F.YEARS.finditer(text):
        if "experience" in text[max(0, m.start() - F.WINDOW): m.end() + F.WINDOW].lower():
            out.append((float(m.group(1)), sentence(text, m.start(), m.end())))
    return out


def _skill_spans(text: str, skill: str):
    pats = SK.AMBIGUOUS_SKILLS.get(skill.lower()) or [SK._word(skill)]
    for pat in pats:
        for m in pat.finditer(text):
            yield sentence(text, m.start(), m.end())


def claims_for(p: dict, skills: list[str]) -> list[dict]:
    title, text, loc = p.get("title") or "", p.get("text") or "", p.get("location") or ""
    out = []

    m = F.R1.search(title)
    out.append(claim("role", "supported", [m.group(0)]) if m else
               claim("role", "insufficient", looked_for="a software engineering role phrase in the title"))

    ys = _years(text)
    nm = NO_MIN.search(text)
    if ys:
        n, q = min(ys, key=lambda x: x[0])
        out.append(claim("years", "supported" if n <= 2 else "contradicted", [q]))
    elif nm:
        out.append(claim("years", "supported", [sentence(text, nm.start(), nm.end())]))
    else:
        out.append(claim("years", "insufficient", looked_for="'N years' near 'experience', or 'no fixed minimum'"))

    em = next(((src, m) for src in (title, text) for m in [ENTRY.search(src)] if m), None)
    mm = MID.search(text)
    quotes = []
    if mm:
        quotes.append(sentence(text, mm.start(), mm.end()))
    if em:
        src, hit = em
        quotes.insert(0, sentence(src, hit.start(), hit.end()))
    if mm:
        out.append(claim("entry", "contradicted", quotes))
    elif em:
        out.append(claim("entry", "supported", quotes))
    else:
        out.append(claim("entry", "insufficient",
                         looked_for="new grad / early career / entry level / internship experience / no fixed minimum"))

    parts = F.location_parts(loc)
    us = [part for part, kind in parts if kind == "us"]
    if us:
        out.append(claim("us", "supported", [us[0]]))
    elif parts and all(kind == "non-us" for _, kind in parts):
        out.append(claim("us", "contradicted", [parts[0][0]]))
    else:
        out.append(claim("us", "insufficient", looked_for="a US place or 'Remote US' in the location field"))

    nice_only = []
    found = None
    for sk in skills:
        for q in _skill_spans(text, sk):
            if NICE.search(q):
                nice_only.append(q)
            elif found is None:
                found = q
    if found:
        out.append(claim("skill", "supported", [found]))
    else:
        out.append(claim("skill", "insufficient", nice_only[:1],
                         looked_for="one of Sam's skills in a sentence that is not a nice-to-have"))
    return out


def entry(postings: list[dict], skills: list[str], score) -> dict:
    p = postings[0]
    cs = claims_for(p, skills)
    labels = [c["label"] for c in cs]
    if "contradicted" in labels:
        lst = "contradicted"
    elif labels.count("insufficient") >= 2:
        lst = "cannot_tell"
    else:
        lst = "ranked"
    return {"uids": [x["uid"] for x in postings], "board": p["board"], "title": p["title"],
            "locations": [x.get("location") for x in postings], "urls": [x.get("url") for x in postings],
            "score": score, "claims": cs, "list": lst,
            "missing": [c["id"] for c in cs if c["label"] == "insufficient"]}


def group(decisions: list[dict]) -> list[dict]:
    groups: dict = {}
    for d in decisions:
        if d["keep"]:
            groups.setdefault((d["board"], d["title"]), {"uids": [], "score": d["score"]})["uids"].append(d["uid"])
    return list(groups.values())


def build(decisions_path: str, run: str, skills: list[str]) -> list[dict]:
    ds = F.rank([json.loads(l) for l in open(decisions_path, encoding="utf-8")])
    ps = {p["uid"]: p for p in load_run(run)}
    return [entry([ps[u] for u in g["uids"]], skills, g["score"]) for g in group(ds)]


def to_markdown(entries: list[dict], source: str) -> str:
    sections = [("ranked", "Shortlist (ranked by filter score)"),
                ("cannot_tell", "I cannot tell (2+ claims insufficient)"),
                ("contradicted", "Kept by the filter, but its own text contradicts a claim")]
    lines = [f"# Shortlist for Sam Rivera (fictional persona)\n",
             f"From `{source}`. Generated by `agent/shortlist.py`; every quote is copied from the posting "
             f"(checked by `tests/test_shortlist.py`).\n"]
    for key, head in sections:
        es = [e for e in entries if e["list"] == key]
        lines.append(f"## {head} — {len(es)}\n")
        for i, e in enumerate(es, 1):
            lines.append(f"### {i}. {e['title']} ({e['board']}, score {e['score']})")
            lines.append(f"{'; '.join(str(l) for l in e['locations'])} · `{'`, `'.join(e['uids'])}`")
            if e["missing"]:
                lines.append(f"\nMissing: {', '.join(e['missing'])}")
            lines.append("\n| Claim | Label | Evidence |\n|---|---|---|")
            for c in e["claims"]:
                ev = " / ".join(f"“{q}”" for q in c["quotes"]).replace("|", "\\|")
                if c["label"] == "insufficient":
                    ev = (ev + " — " if ev else "") + f"looked for: {c['looked_for']}"
                lines.append(f"| {c['claim']} | **{c['label']}** | {ev} |")
            lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("decisions", nargs="?", default="evidence/filter-v1.2/decisions.jsonl")
    ap.add_argument("--run", default=RUN)
    ap.add_argument("--persona", default=F.PERSONA)
    ap.add_argument("--out", default="shortlist")
    args = ap.parse_args(argv)
    skills = json.loads(Path(args.persona).read_text(encoding="utf-8"))["skills"]
    es = build(args.decisions, args.run, skills)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "shortlist.json").write_text(json.dumps(es, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "shortlist.md").write_text(to_markdown(es, args.decisions), encoding="utf-8")
    for k in ("ranked", "cannot_tell", "contradicted"):
        print(f"{k}: {sum(e['list'] == k for e in es)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
