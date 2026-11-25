"""The filter (FILTER.md v1.0 section 1). Rules R1-R4 and the score; every word and number comes from the filter file
(filters/filter_vX.json), so a change to the filter is a change to one file.  Run:  python3 -m js3.filter [filter file]"""
import gzip, json, re, sys
from pathlib import Path

def load_filter(path):
    return json.loads(Path(path).read_text())

def has_phrase(text, phrase):
    """Whole word or whole phrase, case-insensitive: 'BI' does not match inside 'ability'."""
    if not text: return False
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])", text, re.I) is not None

_RANGE = re.compile(r"(?<![\d.])(\d{1,2})\s*\+?\s*(?:-|–|—|to)\s*(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", re.I)
_SINGLE = re.compile(r"(?<![\d.])(\d{1,2})\s*\+?\s*(?:plus\s+)?(?:years?|yrs?)\b", re.I)

def years_spans(text):
    """[(top_of_range, matched_text)]. A range counts by its top (FILTER.md R4)."""
    if not text: return []
    out, taken = [], []
    for m in _RANGE.finditer(text):
        out.append((int(m.group(2)), m.group(0))); taken.append(m.span())
    for m in _SINGLE.finditer(text):
        if not any(a <= m.start() < b for a, b in taken): out.append((int(m.group(1)), m.group(0)))
    return out

def years_in(text):
    return [n for n, _ in years_spans(text)]

def evaluate(posting, cfg):
    title = (posting.get("title") or "").strip(); text = (posting.get("text") or "").strip()
    d = {"id": posting.get("id"), "title": title, "filter_version": cfg["version"], "status": None, "score": 0,
         "r1": False, "r2_reject": False, "r3": False, "r4": None, "skills": [], "years_max": None, "failed": []}
    if not title or not text:
        d["status"] = "cannot_tell"; d["failed"] = ["missing " + ("title" if not title else "text")]; return d
    w = cfg["weights"]
    d["r1"] = any(has_phrase(title, x) for x in cfg["role_words"])
    d["r2_reject"] = any(has_phrase(title, x) for x in cfg["seniority_words"])
    d["skills"] = [s for s in cfg["skills"] if has_phrase(text, s)]
    d["r3"] = len(d["skills"]) >= cfg["min_skills"]
    ys = years_in(text)
    if ys: d["years_max"] = max(ys); d["r4"] = d["years_max"] <= cfg["max_years"]
    d["score"] = (w["title"] if d["r1"] else 0) + min(w["skill_cap"], w["per_skill"] * len(d["skills"])) \
                 - (w["seniority_penalty"] if d["r2_reject"] else 0) - (w["years_penalty"] if d["r4"] is False else 0)
    d["failed"] = [r for r, bad in [("R1", not d["r1"]), ("R2", d["r2_reject"]), ("R3", not d["r3"]), ("R4", d["r4"] is False)] if bad]
    d["status"] = "kept" if not d["failed"] and d["score"] >= cfg["keep_threshold"] else "rejected"
    return d

def rank(decisions):
    return sorted([d for d in decisions if d["status"] == "kept"], key=lambda d: (-d["score"], d["id"]))

def is_close_call(d, cfg):
    """FILTER.md 1.4: score 4, 5 or 6, or exactly one rule failed."""
    t = cfg["keep_threshold"]
    return d["status"] != "cannot_tell" and (t - 1 <= d["score"] <= t + 1 or len(d["failed"]) == 1)

def load_corpus(path="data/corpus.jsonl.gz"):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f: return [json.loads(l) for l in f if l.strip()]

def main(argv):
    from js3.policy import Policy
    fpath = argv[1] if len(argv) > 1 else "filters/filter_v1.0.json"
    cfg = load_filter(fpath); corpus = load_corpus()
    ds = [evaluate(p, cfg) for p in corpus]
    out = Policy(".").check_write(Path(f"out/decisions_v{cfg['version']}.jsonl"))
    out.write_text("".join(json.dumps(d) + "\n" for d in ds))
    from collections import Counter
    c = Counter(d["status"] for d in ds); fails = Counter(r for d in ds for r in d["failed"])
    print(f"filter v{cfg['version']} on {len(ds)} postings: {dict(c)}; rule failures {dict(fails)}; close calls {sum(is_close_call(d, cfg) for d in ds)}")
    print(f"wrote {out.relative_to(Path('.').resolve())}")
if __name__ == "__main__": main(sys.argv)
