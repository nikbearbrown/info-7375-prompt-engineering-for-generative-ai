"""The relevance filter, implementing FILTER.md v1.2 (v1.2: N >= 3 years scores -0.40; v1.0 gave 0 at N = 3).

Reads only title, location and text of each posting (never department).
No duplicates are removed before filtering (FILTER.md section 1, W4).

    python3 -m agent.filter evidence/run-20261123-185425Z            # decisions -> out/filter/
    python3 -m agent.filter --labels labels/dev.csv                  # compare with my hand labels

Every number here is hand-set in FILTER.md; see score/origins.md for where each came from.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from agent.postings import load_run
from agent.skills import match_skills

RULES_VERSION = "v1.2"
RUN = "evidence/run-20261123-185425Z"
PERSONA = "examples/persona.example.json"
THRESHOLD = 0.50

# --- Hard gates --------------------------------------------------------------
G1 = re.compile(r"\b(Senior|Sr|Staff|Principal|Lead|Manager|Director|Head|VP|Vice President|Chief|President)\b")
G2 = re.compile(r"\b(Intern|Internship)\b")

# G3: a location part is US, non-US, or unknown ("I cannot tell").
US_STATES = ("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
             "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY").split()
US_PART = re.compile(r",\s*(" + "|".join(US_STATES) + r")\b|\bUnited States\b|\bRemote US\b|\bUS-based\b|\bUSA\b")
NON_US_PART = re.compile(
    r"\b(Canada|Toronto|Vancouver|Poland|Spain|UK|United Kingdom|London|Luxembourg|Slovenia|Ljubljana|"
    r"Germany|Ireland|India|Mexico|Brazil|Australia|Singapore|Japan)\b")

# --- Score -------------------------------------------------------------------
R1 = re.compile(r"\b(Software Engineer|Software Developer|Back-?end Engineer|Front-?end Engineer|"
                r"Full ?Stack Engineer|Web Engineer|iOS Engineer|Android Engineer|Mobile Engineer|"
                r"Machine Learning Engineer)", re.I)
R3_TEXT = re.compile(r"\b(new grad|new graduate|early career|entry[- ]level)\b", re.I)
R3_TITLE = re.compile(r"\bEngineer I\b(?!I)")
# N+ years / N years / N-M years / N to M years. (?<![\d.]) keeps "1.5" from also matching as "5".
YEARS = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*\+?\s*(?:(?:-|–|—|to)\s*\d+(?:\.\d+)?\s*\+?\s*)?years?\b", re.I)
WINDOW = 60


def find_years(text: str) -> list[tuple[float, str]]:
    """(N, quote) for each years phrase with 'experience' within 60 characters."""
    out = []
    for m in YEARS.finditer(text or ""):
        near = text[max(0, m.start() - WINDOW): m.end() + WINDOW]
        if "experience" in near.lower():
            n = float(m.group(1))
            out.append((int(n) if n.is_integer() else n, m.group(0)))
    return out


def min_years(text: str):
    ys = [n for n, _ in find_years(text)]
    return min(ys) if ys else None


def location_parts(location) -> list[tuple[str, str]]:
    """[(part, 'us' | 'non-us' | 'unknown')]."""
    parts = []
    for part in (location or "").split(";"):
        part = part.strip()
        if not part:
            continue
        kind = "us" if US_PART.search(part) else "non-us" if NON_US_PART.search(part) else "unknown"
        parts.append((part, kind))
    return parts


def g3_rejects(parts: list[tuple[str, str]]) -> bool:
    """Reject only if EVERY part is outside the US (W5 is 'any part')."""
    return bool(parts) and all(kind == "non-us" for _, kind in parts)


def judge(p: dict, skills: list[str]) -> dict:
    """One decision for one posting. Never looks at other postings."""
    title, text = (p.get("title") or "").strip(), p.get("text") or ""
    d = {"uid": p.get("uid"), "board": p.get("board"), "title": title, "location": p.get("location"),
         "url": p.get("url"), "keep": False, "score": None, "gates": [], "rules": {},
         "years": None, "years_quote": None, "skills": [], "cannot_tell": [], "version": RULES_VERSION}
    if not title:
        d["gates"] = ["no title"]
        return d

    if G1.search(title):
        d["gates"].append("G1")
    if G2.search(title):
        d["gates"].append("G2")
    parts = location_parts(p.get("location"))
    kinds = {k for _, k in parts}
    if g3_rejects(parts):
        d["gates"].append("G3")
    if not parts or (kinds <= {"unknown", "non-us"} and "unknown" in kinds):
        d["cannot_tell"].append("location")
    if not text.strip():
        d["cannot_tell"].append("text")

    found = find_years(text)
    if found:
        d["years"], d["years_quote"] = min(found, key=lambda x: x[0])
    d["skills"] = match_skills(text, skills) if text else []

    r1 = 0.5 if R1.search(title) else 0
    n = d["years"]
    r2 = 0 if n is None else 0.3 if n <= 2 else -0.4   # v1.2; v1.0: 0 if 2 < n < 4
    r3 = 0.2 if (R3_TEXT.search(title) or R3_TEXT.search(text) or R3_TITLE.search(title)) else 0
    r4 = 0.1 if d["skills"] else 0
    d["rules"] = {"R1": r1, "R2": r2, "R3": r3, "R4": r4}
    d["score"] = round(r1 + r2 + r3 + r4, 2)
    if n is None and not r3 and "G1" not in d["gates"]:
        d["cannot_tell"].append("level")
    d["keep"] = not d["gates"] and d["score"] >= THRESHOLD
    return d


def filter_postings(postings: list[dict], skills: list[str]) -> list[dict]:
    """A decision for every posting, in input order. No dedupe (W4)."""
    return [judge(p, skills) for p in postings]


def rank(decisions: list[dict]) -> list[dict]:
    """Highest score first; ties broken by fewer 'cannot tell' fields, then uid."""
    return sorted(decisions, key=lambda d: (-(d["score"] or -9), len(d["cannot_tell"]), d["uid"] or ""))


def compare(decisions: list[dict], label_file: str) -> dict:
    by_uid = {d["uid"]: d for d in decisions}
    rows = list(csv.DictReader(open(label_file, encoding="utf-8")))
    cells = {"tp": [], "fp": [], "fn": [], "tn": []}
    for r in rows:
        mine, got = r["my_label"] == "keep", by_uid[r["uid"]]["keep"]
        cells[("t" if mine == got else "f") + ("p" if got else "n")].append(r["uid"])
    return cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?", default=RUN)
    ap.add_argument("--persona", default=PERSONA)
    ap.add_argument("--out", default="out/filter")
    ap.add_argument("--labels", help="a labels CSV to compare against (use dev.csv while tuning)")
    args = ap.parse_args(argv)

    skills = json.loads(Path(args.persona).read_text(encoding="utf-8"))["skills"]
    ds = filter_postings(load_run(args.run), skills)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "decisions.jsonl").open("w", encoding="utf-8") as f:
        for d in ds:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    kept = [d for d in ds if d["keep"]]
    no_title = sum(1 for d in ds if d["gates"] == ["no title"])
    print(f"{RULES_VERSION}: {len(ds)} postings, kept {len(kept)}, rejected {len(ds) - len(kept) - no_title}, "
          f"no title {no_title}  -> {out / 'decisions.jsonl'}")
    for g in ("G1", "G2", "G3"):
        print(f"  {g} fired on {sum(g in d['gates'] for d in ds)}")
    if args.labels:
        c = compare(ds, args.labels)
        tp, fp, fn, tn = (len(c[k]) for k in ("tp", "fp", "fn", "tn"))
        print(f"vs {args.labels}: tp {tp} fp {fp} fn {fn} tn {tn}"
              f"  precision {tp}/{tp + fp}  recall {tp}/{tp + fn}")
        for k in ("fp", "fn"):
            for uid in c[k]:
                d = next(x for x in ds if x["uid"] == uid)
                print(f"  {k} {uid}  {d['score']}  {d['gates'] or d['rules']}  years={d['years']}  {d['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
