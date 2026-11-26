"""python3 make_shortlist.py [version] -> out/<version>/shortlist.json : every kept posting, every claim, auto label."""
import json
import sys
from pathlib import Path

from jsagent3.evidence import justify
from jsagent3.filter import decide, load_rules
from jsagent3.mcp_server import load_postings

v = sys.argv[1] if len(sys.argv) > 1 else "v1.1"
rules = load_rules(v)
rows = []
for p in load_postings().values():
    d = decide(p, rules)
    if d["keep"]:
        rows.append({"id": p["id"], "title": p["title"], "location": p["location"], "url": p["url"],
                     "rank": d["rank"], "reason": d["reason"], "claims": justify(p, d, rules)})
rows.sort(key=lambda r: -r["rank"])
out = Path("out") / v / "shortlist.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
for r in rows:
    print(f"== {r['id']} | {r['title']} | {r['location']} | rank {r['rank']}")
    for c in r["claims"]:
        print(f"   {c['claim'].get('skill', c['claim']['type'])} -> {c['label']} | {c['quote'][:160]}")
