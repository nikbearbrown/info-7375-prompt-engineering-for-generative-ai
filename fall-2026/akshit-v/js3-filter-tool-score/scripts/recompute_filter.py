"""Second method: recompute FILTER.md v1.0 for every posting from the raw saved responses.

Imports nothing from agent3. Parses HTML with html.parser (not regex), matches terms as
token sequences (not regex lookarounds), and re-types every word list from FILTER.md.
Then compares each verdict and score with out/filter/v1.0/results.json.

    python -I -B scripts/recompute_filter.py           # literal reading: only whitespace between a phrase's words
    python -I -B scripts/recompute_filter.py --loose   # loose reading: any punctuation may sit between them

The first run (2026-11-24) used the loose reading by accident and disagreed with the code on 5
postings, all because of "data-quality", "data-model" and "Data & Integration". FILTER.md v1.0
says "whole-word phrase" but not what may sit between the words. The code reads it literally.
"""
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Re-typed from FILTER.md v1.0, section 1.
DISQ = ["staff", "principal", "director", "manager", "head of", "intern", "phd", "contract", "temporary"]
ROLE = ["data engineer", "data engineering", "data platform", "data infrastructure", "analytics engineer",
        "analytics engineering", "etl", "data integration", "data pipeline"]
TOPICS = [["data pipeline", "data pipelines", "etl", "elt"],
          ["data warehouse", "data warehouses", "data warehousing", "data lake", "data lakes", "lakehouse"],
          ["data modeling", "data model", "data models"], ["orchestration"], ["streaming"],
          ["batch processing", "batch job", "batch jobs"], ["data quality"]]
SKILLS = ["python", "sql", "spark", "airflow", "kafka", "dbt", "snowflake", "aws"]
EMPLOYER = {"snowflake": "snowflake", "figma": "figma", "spotify": "spotify"}
FULLTIME = {"ashby": {"FullTime"}, "lever": {"Permanent"}}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, d):
        self.parts.append(d)

    def handle_starttag(self, tag, attrs):
        self.parts.append(" ")

    def handle_endtag(self, tag):
        self.parts.append(" ")


def html_text(s):
    t = Text()
    t.feed(unescape(s or ""))   # Greenhouse content is escaped HTML: unescape once, then parse tags
    return " ".join("".join(t.parts).split())


LOOSE = "--loose" in sys.argv


def toks(s):
    """Words, plus each punctuation mark as its own token (so 'data-quality' is not 'data quality')."""
    if LOOSE:
        return re.findall(r"[a-z0-9]+", (s or "").lower())
    return re.findall(r"[a-z0-9]+|[^a-z0-9\s]", (s or "").lower())


def has(term, tokens):
    t = toks(term)
    n = len(t)
    return any(tokens[i:i + n] == t for i in range(len(tokens) - n + 1))


def postings():
    out = {}
    for rec_path in sorted((ROOT / "out" / "runs").glob("*.json")):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        raws = {e["board"]: e["raw"] for e in rec["trace"] if e["event"] == "request" and e.get("raw")}
        for key, o in rec["boards"].items():
            if o["outcome"] != "ok":
                continue
            ats, board = key.split(":")
            data = json.loads((ROOT / raws[key]).read_text(encoding="utf-8"))
            if ats == "greenhouse":
                rows = [(j["id"], j["title"], html_text(j["content"]), None) for j in data["jobs"]]
            elif ats == "lever":
                rows = []
                for j in data:
                    lists = " ".join(x.get("text", "") + " " + html_text(x.get("content")) for x in j.get("lists") or [])
                    rows.append((j["id"], j["text"], " ".join([j.get("descriptionPlain") or "", lists,
                                                               j.get("additionalPlain") or ""]),
                                 (j.get("categories") or {}).get("commitment")))
            else:
                rows = [(j["id"], j["title"], j.get("descriptionPlain") or html_text(j.get("descriptionHtml")),
                         j.get("employmentType")) for j in data["jobs"] if j.get("isListed", True)]
            for nid, title, text, et in rows:
                out[f"{key}:{nid}"] = (ats, board, title.strip(), " ".join(text.split()), et)
    return out


def score(ats, board, title, text, et):
    if len(text) < 300:
        return "cannot_tell", None
    tt, ct = toks(title), toks(text)
    disq = any(has(w, tt) for w in DISQ) or (ats in FULLTIME and et is not None and et not in FULLTIME[ats])
    s = (4 if any(has(w, tt) for w in ROLE) else 0)
    s += min(sum(1 for g in TOPICS if any(has(t, ct) for t in g)), 4)
    s += sum(1 for k in SKILLS if k != EMPLOYER.get(board) and has(k, ct))
    return ("reject" if disq or s < 6 else "keep"), s


def main():
    # literal reading = FILTER.md v1.0; loose reading = v1.1 (rule C2, added 2026-11-25)
    version = "v1.1" if LOOSE else "v1.0"
    mine = json.loads((ROOT / "out" / "filter" / version / "results.json").read_text(encoding="utf-8"))["results"]
    ps = postings()
    diffs = []
    for pid, args in ps.items():
        v, s = score(*args)
        r = mine.get(pid)
        if r is None or r["verdict"] != v or (s is not None and r["score"] != s):
            diffs.append((pid, args[2], v, s, r and r["verdict"], r and r["score"]))
    print(f"reading: {'loose' if LOOSE else 'literal'} vs code {version}; recomputed {len(ps)} postings (code has {len(mine)}); "
          f"disagreements: {len(diffs)}")
    for d in diffs[:20]:
        print("  ", d)
    return 1 if diffs or len(ps) != len(mine) else 0


if __name__ == "__main__":
    sys.exit(main())
