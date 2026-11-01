"""Recompute run 2's rule verdicts by a second method, for failure condition #1.

Does not import agent.rule. It tokenizes text (split on non-alphanumerics) instead of
using the agent's regex, and reads the raw Greenhouse JSON directly.

    python -I scripts/recompute_rule.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "evidence" / "raw" / "20261031T233955Z_figma_live.json"
RUN = ROOT / "runs" / "20261031T233955Z_figma_run.json"

# Copied by hand from CONTRACT.md, not from agent/rule.py.
DQ = ["staff", "principal", "director", "manager", "head of", "intern", "phd", "contract", "temporary"]
TT = ["data engineer", "data platform", "data infrastructure", "analytics engineer", "etl", "data integration"]
SK = ["python", "sql", "spark", "airflow", "kafka", "dbt", "snowflake", "aws"]


def tokens(s):
    return re.split(r"[^a-z0-9]+", s.lower())


def has_phrase(tok, phrase):
    p = phrase.split()
    return any(tok[i:i + len(p)] == p for i in range(len(tok)))


def main():
    jobs = {j["id"]: j for j in json.loads(RAW.read_text(encoding="utf-8"))["jobs"]}
    rows = json.loads(RUN.read_text(encoding="utf-8"))["rows"]
    agree = 0
    for row in rows:
        j = jobs[row["posting"]["id"]]
        title = j["title"]
        text = re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(j["content"])))
        dq = [w for w in DQ if has_phrase(tokens(title), w)]
        tm = [t for t in TT if t in title.lower()]
        sk = [s for s in SK if s in tokens(text)]
        if dq:
            v = "not_relevant"
        elif (tm and len(sk) >= 3) or (not tm and len(sk) >= 4):
            v = "relevant"
        else:
            v = "not_relevant"
        code = row["rule"]
        same = v == code["verdict"] and (bool(dq) or sk == [s.lower() for s in code["skills_found"]])
        agree += same
        print(f"{'MATCH' if same else 'DIFF '} {j['id']} {title[:45]:45} recomputed={v:12} "
              f"code={code['verdict']:12} disq={dq} skills={'-' if dq else sk}")
    print(f"{agree}/{len(rows)} match")


if __name__ == "__main__":
    main()
